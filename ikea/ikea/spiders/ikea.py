import json

import scrapy

from ..items import IkeaItem


class IkeaSpider(scrapy.Spider):
    name = 'ikea'
    items_per_page = 24
    with open('./ikea/header.json', 'r') as o:
        headers = json.loads(o.read())
        o.close()
    domain = 'https://www.ikea.com'
    skip_cat = ['New & Trending', 'Offers']
    all_cats = []
    cat_api_url = 'https://www.ikea.com/us/en/meta-data/navigation/catalog-products-slim.json'
    pd_api_url = 'https://sik.search.blue.cdtapps.com/us/en/search'


    def start_requests(self):
        yield scrapy.Request(self.cat_api_url, self.parse_categories, headers=self.headers)

    def flatten_nested_categories(self, categories):
        for sub in categories:
            if 'subs' in sub:
                self.all_cats.append({'id': sub['id'], 'name': sub['name'], 'isShelf': False})
                self.flatten_nested_categories(sub['subs'])
            else:
                self.all_cats.append({'id': sub['id'], 'name': sub['name'], 'isShelf': True})


    def errback(self, response):
        print(response.request.body)
    
    def filter_shelves(self, cat):
        return cat['isShelf'] and cat['name'] not in self.skip_cat

    def parse_categories(self, response):
        self.flatten_nested_categories(response.json())
        for cat in list(filter(self.filter_shelves, self.all_cats)):
            yield scrapy.http.JsonRequest(
                f'{self.pd_api_url}?c=listaf&v=20240110', # TODO use urlencode
                self.parse,
                errback=self.errback,
                data={
                    "searchParameters": {
                        "input": cat["id"],
                        "type":"CATEGORY"
                    },
                    "zip": "32201",
                    "isUserLoggedIn":False,
                    "optimizely":{},
                    "components":[
                        {"component":"PRIMARY_AREA","columns":4,"types":{"main":"PRODUCT","breakouts":["PLANNER","LOGIN_REMINDER","MATTRESS_WARRANTY"]},
                        "filterConfig":{"max-num-filters":5},"window":{"size":24,"offset":0},"forceFilterCalculation": True}
                    ]
                },
                headers=self.headers,
            )


    def parse_breadcrumbs(self, item):
        return item['name']

    def parse(self, response):
        response = response.json()
        breadcrumbs = response['metadata']['categoryPage']['categoryParents'] +\
            [response['metadata']['categoryPage']['categoryKey']]

        for product in response['results'][0]['items']:
            item = IkeaItem()

            if 'planner' in product:
                continue # I think it is an add

            item['name'] = product['product']['name']
            item['url'] = product['product']['pipUrl']

            for i, breadcrumb in enumerate(breadcrumbs):
                cat_name = list(filter(lambda c: c['id'] == breadcrumb, self.all_cats))
                if cat_name:
                    item[f'breadcrumb_{i + 1}'] = cat_name[0]['name']

            item['position'] = int(product['metadata'].split(';')[1])
            yield item

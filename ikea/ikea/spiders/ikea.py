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
    # cities_zip_code = {'New-York': '10001', 'Baltimore': '21201', 'Stockton': '95201', 'Glendale': '85031', 'Amarillo': '79101', 'Salem': '97301', 'Escondido': '92025', 'New Haven': '06501', 'Lafayette': '70501', 'Greeley': '80631', 'Jurupa Valley': '91752'}
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
                    "searchParameters":{
                        "input":cat['id'],
                        "type":"CATEGORY"
                    },
                    "zip":"69300","optimizely":{"sik_null_test_20241016_default":"a"},
                    "isUserLoggedIn":False,
                    "components":[
                        {
                            "component":"PRIMARY_AREA",
                            "columns":4,"types":{"main":"PRODUCT", "breakouts":["PLANNER","LOGIN_REMINDER","MATTRESS_WARRANTY"]},
                            "filterConfig":{"max-num-filters":5},
                            "sort":"RELEVANCE",
                            "window":{
                                "offset":0,
                                "size":24
                            }
                        }
                    ]
                },
                headers=self.headers,
            )


    def parse_breadcrumbs(self, item):
        return item['name']

    def parse(self, response):
        res_json = response.json()
        breadcrumbs = res_json['metadata']['categoryPage']['categoryParents'] +\
            [res_json['metadata']['categoryPage']['categoryKey']]

        for product in res_json['results'][0]['items']:
            item = IkeaItem()

            if 'planner' in product:
                continue # I think it is an add

            for i, breadcrumb in enumerate(breadcrumbs):
                cat_name = list(filter(lambda c: c['id'] == breadcrumb, self.all_cats))
                if cat_name:
                    item[f'breadcrumb_{i + 1}'] = cat_name[0]['name']

            from collections import defaultdict

            def safe_json(data=None):
                if data is None:
                    data = {}
                if isinstance(data, dict):
                    # Recursively apply the function to all dictionary values
                    return defaultdict(lambda: None, {k: safe_json(v) for k, v in data.items()})
                else:
                    return data

            item['position'] = int(product['metadata'].split(';')[1])
            product = safe_json(product['product'])
            item['id'] = product['id']
            item['name'] = product['name']
            item['url'] = product['pipUrl']
            item['type_name'] = product['typeName']
            item['online_sellable'] = product['onlineSellable']
            item['last_chance'] = product['lastChance']
            item['nb_variants'] = product['gprDescription']['numberOfVariants']
            item['variants_ids'] = [i['id'] for i in product['gprDescription']['variants'] if 'id' in product['gprDescription']['variants']]
            item['colors_hex'] = [i['hex'] for i in product['colors'] if 'hex' in product['colors']]
            item['rating'] = product['ratingValue']
            item['rating_count'] = product['ratingCount']
            item['price'] = product['salesPrice']['numeral']
            item['currency'] = product['salesPrice']['currencyCode']
            item['discount'] = product['salesPrice']['discount']
            item['is_breathtaking'] = product['salesPrice']['isBreathTaking']
            item['image_url'] = product['mainImageUrl']
            # item['home_delivery'] = product['homeDelivery']
            yield item
        if res_json['results'][0]['metadata']['end'] < res_json['results'][0]['metadata']['max']:
            body = json.loads(str(response.request.body, encoding='utf-8'))
            body['components'][0]['window']['offset'] = res_json['results'][0]['metadata']['end']
            yield scrapy.http.JsonRequest(response.url, self.parse, data=body, headers=self.headers)

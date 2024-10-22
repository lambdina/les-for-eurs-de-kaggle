import json
from copy import copy
from os import getcwd

import scrapy
from scrapy.shell import inspect_response

from ..items import IkeaItem


class IkeaSpider(scrapy.Spider):
    name = 'ikea'
    items_per_page = 24
    with open('./ikea/header.json', 'r') as o:
        headers = json.loads(o.read())
        o.close()
    domain = 'https://www.ikea.com'
    skip_cat = ['New & Trending', 'Offers']
    cat_api_url = 'https://www.ikea.com/us/en/meta-data/navigation/catalog-products-slim.json'
    pd_api_url = 'https://sik.search.blue.cdtapps.com/us/en/search'


    def start_requests(self):
        yield scrapy.Request(self.cat_api_url, self.parse_categories, headers=self.headers)

    def get_categories_rec(self, categories):
        for sub in categories:
            if sub['name'] in self.skip_cat:
                continue
            if 'subs' in sub:
                yield from self.get_categories_rec(sub['subs'])
            else:
                yield scrapy.http.JsonRequest(
                    f'{self.pd_api_url}?c=listaf&v=20240110', # TODO use urlencode
                    self.parse,
                    errback=self.errback,
                    data={
                        "searchParameters": {
                            "input": sub["id"],
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
    def errback(self, response):
        print(response.request.body)

    def parse_categories(self, response):
        yield from self.get_categories_rec(response.json())

    def parse_breadcrumbs(self, item):
        return item['name']

    def parse(self, response):
        with open(str(response.json()["metadata"]["categoryPage"]["categoryKey"]) + '.json', 'w') as fd:
            import json
            fd.write(json.dumps(response.json(), indent=4))
        for product in response.json()['results'][0]['items']:
            item = IkeaItem()
            item['name'] = product['product']['name']
            item['url'] = product['product']['pipUrl']
            item['breadcrumbs'] = list(map(self.parse_breadcrumbs, product['product']['categoryPath']))
            item['position'] = int(product['metadata'].split(';')[1])
            yield item

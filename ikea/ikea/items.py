# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IkeaItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    breadcrumb_1 = scrapy.Field()
    breadcrumb_2 = scrapy.Field()
    breadcrumb_3  = scrapy.Field()
    breadcrumb_4  = scrapy.Field()
    breadcrumb_5  = scrapy.Field()
    breadcrumb_6  = scrapy.Field()
    position = scrapy.Field()

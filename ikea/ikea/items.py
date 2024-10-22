# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IkeaItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    breadcrumbs = scrapy.Field()
    position = scrapy.Field()

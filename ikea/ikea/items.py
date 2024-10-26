# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IkeaItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    type_name = scrapy.Field()
    url = scrapy.Field()
    breadcrumb_1 = scrapy.Field()
    breadcrumb_2 = scrapy.Field()
    breadcrumb_3  = scrapy.Field()
    breadcrumb_4  = scrapy.Field()
    breadcrumb_5  = scrapy.Field()
    breadcrumb_6  = scrapy.Field()
    position = scrapy.Field()
    online_sellable = scrapy.Field()
    last_chance = scrapy.Field()
    nb_variants = scrapy.Field()
    variants_ids = scrapy.Field()
    colors_hex = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    discount = scrapy.Field()
    is_breathtaking = scrapy.Field()
    image_url = scrapy.Field()
    #home_delivery = scrapy.Field()

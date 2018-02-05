# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduNewsItem(scrapy.Item):
    # define the fields for your item here like:
    keyword = scrapy.Field()
    title = scrapy.Field()
    publish_date = scrapy.Field()
    desc = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    news_from = scrapy.Field()
    pic = scrapy.Field()
    content = scrapy.Field()
    _userid = scrapy.Field()
    _ctid = scrapy.Field()
    _primary = scrapy.Field()


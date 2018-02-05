#! python3
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import hashlib
from pymongo import MongoClient
from baidu_news.spiders import baidunews
from scrapy.exceptions import CloseSpider
from scrapy.exceptions import DropItem
from baidu_news import mongodb_conf as mongodb


class BaiduNewsPipeline(object):
    def __init__(self):
        client = MongoClient(
            mongodb.MONGODB_SERVER,
            mongodb.MONGODB_PORT
        )
        self.db = client[mongodb.MONGODB_DB]
        self.collection = self.db[mongodb.MONGODB_POST_COLLECTION+str(mongodb.USER_ID)]

    def process_item(self, item, spider):
        if spider.name == "baidunews":
            if spider.conflict_count < baidunews.CONFLICT_ARTICLES or spider.repeat != baidunews.REPEAT:
                if item['content']:
                    item['_userid'] = mongodb.USER_ID
                    item['_ctid'] = mongodb.TASK_ID
                    item['_primary'] = self.md5(item['url'])
                    if not self.collection.find_one({'_ctid': item['_ctid'], '_primary': item['_primary']}):
                        spider.reset()
                        self.collection.insert_one(dict(item))
                    else:
                        spider.increase()
                else:
                    raise DropItem('Bad Item: Missing content of news!')
            else:
                raise CloseSpider(reason="Reach conflict times")
        return item

    @staticmethod
    def md5(url):
        m = hashlib.md5()
        m.update(url.encode(encoding='utf-8'))
        return m.hexdigest()[:16]

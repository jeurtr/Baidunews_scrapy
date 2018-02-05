#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import sys
import scrapy
import logging
import datetime
from newspaper import Article
from baidu_news.items import BaiduNewsItem
from scrapy.exceptions import CloseSpider
from baidu_news import mongodb_conf as mongodb

# number of conflict articles just in time
CONFLICT_ARTICLES = 3
# regex string
# find </p>
SPLITPLABEL = "</p>"
# fine <span>
SPLITSPANLABEL = "<span"
# remove html label
REMOVEHTMLLABEL = "<[^>]*>"
# repeat flag
REPEAT = 1
# log file
logging.basicConfig(filename='baidu.log', filemode='w', level=logging.ERROR)


class BaidunewsSpider(scrapy.Spider):
    """extract news from baidu"""
    name = "baidunews"

    host_url = 'http://news.baidu.com/'
    search_url = 'http://news.baidu.com/ns?word=%s&sr=0&cl=2&rn=20&tn=news&ct=0&clk=sortbytime'
    conflict_count = 0
    repeat = 0

    def __init__(self, keyword="双创", repeat=0, user_id=0, task_id=0):
        super(BaidunewsSpider, self).__init__()
        self.conflict_count = 0
        self.keyword = keyword
        self.repeat = int(repeat)
        mongodb.USER_ID = int(user_id)
        mongodb.TASK_ID = int(task_id)
        self.split_p_label = re.compile(SPLITPLABEL)
        self.split_span_label = re.compile(SPLITSPANLABEL)
        self.remove_html_label = re.compile(REMOVEHTMLLABEL)

    def start_requests(self):
        if self.keyword == "led":
            with open('../led_keywords.txt', 'r') as f:
                keywords = f.readlines()
                for k in keywords:
                    meta = {'keyword': k.strip(' ')}
                    yield scrapy.Request(url=BaidunewsSpider.search_url % k.strip(' '), meta=meta, callback=self.parse, dont_filter=True)

        elif self.keyword == "xinyidai":
            with open('../xinyidai_keywords.txt', 'r') as f:
                keywords = f.readlines()
                for k in keywords:
                    meta = {'keyword': k.strip(' ')}
                    yield scrapy.Request(url=BaidunewsSpider.search_url % k.strip(' '), meta=meta, callback=self.parse, dont_filter=True)

        else:
            meta = {'keyword': self.keyword}
            yield scrapy.Request(BaidunewsSpider.search_url % self.keyword, meta=meta, callback=self.parse,
                                 dont_filter=True)

    def reset(self):
        self.conflict_count = 0

    def increase(self):
        self.conflict_count += 1

    def parse(self, response):
        """extract basic info of news in search result page"""
        result_list = response.xpath("//div[@id='content_left']/div[3]/div")
        meta = response.meta
        for r in result_list:
            if (self.conflict_count < CONFLICT_ARTICLES) or (self.repeat != REPEAT):
                item = BaiduNewsItem()
                item['keyword'] = meta.get('keyword')
                title = r.xpath("./h3/a//text()").extract()
                item['title'] = ''.join(title)
                raw_from_date = r.xpath(
                    ".//p[@class='c-author']/text()").extract()
                tmp_from_date = ''.join(raw_from_date)
                tmp_from_date = tmp_from_date.replace(u'\xa0\xa0', ' ')
                from_date = tmp_from_date.split(' ')
                raw_date = ''
                if len(from_date) > 2:
                    raw_date = from_date[1].replace(
                        '年', '-').replace('月', '-').replace('日', '')
                else:
                    delta = 0
                    if '分钟' in from_date[1]:
                        minutes = from_date[1].split('分钟')[0]
                        delta = datetime.timedelta(minutes=int(minutes))

                    if '小时' in from_date[1]:
                        hour = from_date[1].split('小时')[0]
                        delta = datetime.timedelta(hours=int(hour))
                    now = datetime.datetime.now()
                    try:
                        accuracy_time = now - delta
                        raw_date = accuracy_time.strftime("%Y-%m-%d")
                    except TypeError:
                        logging.error("date error in: ",
                                      response.url + " title: " + item['title'])
                item['date'] = raw_date
                item['news_from'] = from_date[0].strip().replace('..', '')
                desc_data = r.xpath("./div").extract_first()
                tmp_desc_data = self.split_p_label.split(desc_data)
                if len(tmp_desc_data) > 1:
                    tmp_desc_data = tmp_desc_data[1]
                tmp_desc_data = self.split_span_label.split(tmp_desc_data)[0]
                item['desc'] = self.remove_html_label.sub(
                    "", tmp_desc_data).strip()
                item['url'] = r.xpath("./h3/a/@href").extract()[0]
                meta = {'item': item, 'dont_retry': True}
                yield scrapy.Request(item['url'], self.parse_content, meta=meta, priority=1)
            else:
                raise CloseSpider(reason="Reach conflict times")
        next_page = response.xpath(
            "//p[@id='page']/a[last()]/@href").extract_first()
        if next_page:
            logging.info("next Page： " + BaidunewsSpider.host_url + next_page)
            yield scrapy.Request(BaidunewsSpider.host_url + next_page, self.parse, meta=meta, priority=0,
                                 dont_filter=True)
        else:
            sys.exit()

    def parse_content(self, response):
        """extract content of news by newspaper"""
        item = response.meta['item']
        is_special, content = self._handle_special_site(response)
        if not is_special:
            # 不是特殊网站
            article = Article(item['url'], language='zh')
            article.set_html(response.body)
            article.is_downloaded = True
            article.parse()
            item['pic'] = article.top_image
            item['content'] = str(article.text)
            item['publish_date'] = article.publish_date
            if publish_date:
            	item['publish_date'] = publish_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
            	item['publish_date'] = "null"
        else:
            item['pic'] = ""
            item['content'] = content
        # extract content failed
        if item['content'] == '':
            logging.error("empty content in: " + response.url)
            yield item
            # raw_content = response.xpath("//body//p/text()").extract()
            # item['content'] = ''.join(raw_content)
        item['content'] = item['content'].strip().replace(u"\xa0", "").replace(u"\u3000", "").replace("|", "")\
            .replace("用微信扫码二维码分享至好友和朋友圈", "").strip("您当前的位置 ：").strip("您所在的位置：").strip("提示：点击上方").strip(">").strip()
        yield item

    @staticmethod
    def _handle_special_site(response):
        """判断和处理newspaper无法抓取的网站"""
        # 特殊处理的网站域名, 如果还有其他需要特殊处理的网站，请把域名和正文的xpath添加在下面的字典里面：
        special_site = {
            "eastmoney": "//div[@class='left-content']//p/text()",  # 东方财富网
        }
        is_special = False
        content = ""
        xpath_str = ""
        for site in special_site.keys():
            if site in response.url:
                is_special = True
                xpath_str = special_site[site]
        if is_special:
            content = response.xpath(xpath_str).extract()
            content = "\n".join(content)
        return is_special, content

#!/bin/bash
# 
# 
# Author: 
# Created Time: 2016年11月04日 星期五 16时20分53秒

source /var/www/backend/python3/baidu/bin/activate
cd /var/www/backend/python3/baidu-shuangchuang-news/
scrapy crawl baidunews -a repeat=1  >> /tmp/baidu_news.log 2>&1

#!/bin/bash
# 
# 
# Author: 
# Created Time: 2016年12月01日 星期四 16时40分08秒

source /var/www/backend/python3/baidu/bin/activate
cd /var/www/backend/python3/baidu-shuangchuang-news/
scrapy crawl baidunews -a keyword="双创"  -a user_id=70 -a task_id=58  -a  repeat=1  >> /tmp/baidu_news.log 2>&1
scrapy crawl baidunews -a keyword="智能家居" -a user_id=137 -a task_id=65 -a  repeat=1  >> /tmp/baidu_news.log 2>&1
scrapy crawl baidunews -a keyword="海尔智能家居" -a user_id=137 -a task_id=65 -a  repeat=1  >> /tmp/baidu_news.log 2>&1
scrapy crawl baidunews -a keyword="快思聪" -a user_id=137 -a task_id=65 -a  repeat=1  >> /tmp/baidu_news.log 2>&1
scrapy crawl baidunews -a keyword="河东hdl" -a user_id=137 -a task_id=65 -a  repeat=1  >> /tmp/baidu_news.log 2>&1
scrapy crawl baidunews  -a keyword="国泰君安" -a user_id=147 -a task_id=70 -a  repeat=1  >> /tmp/baidunews.log 2>&1
scrapy crawl baidunews  -a keyword="中信证券" -a user_id=147 -a task_id=70 -a  repeat=1  >> /tmp/baidunews.log 2>&1
scrapy crawl baidunews  -a keyword="广发证券" -a user_id=147 -a task_id=70 -a  repeat=1  >> /tmp/baidunews.log 2>&1

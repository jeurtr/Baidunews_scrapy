# 百度新闻搜索爬虫

## 程序运行必要依赖及安装说明：

1. 安装mongodb 2.4.9 及以上版本
2. 如果系统只有python2.x版本， 则需要安装python3.x和python-virtualenv，如果系统默认是python3.x版本，则不需要创建虚拟环境，直接pip安装相关依赖即可
    - 2.1，在baidu_news目录（该目录下有scrapy.cfg文件）下创建空的虚拟环境，名为“python3”（`python3 -m virtualenv python3 --python=/usr/bin/python3 --no-site-packages`）
    - 2.2，进入该python3环境(`cd python3`)
    - 2.3，激活环境（`source ./bin/activate`)
3. 安装依赖：`pip3 install -r requirements.txt`

## 程序运行前操作：

- 在/baidu_news/baidu_news目录下复制配置文件`cp  mongodb_conf.py.example mongodb_conf.py`
- 开启mongodb服务
- 以root账户进入目录baidu_news(该目录下有baidu_news目录以及scrapy.cfg文件)
- 进入环境并激活环境(如果系统默认是python3.x则不需要), 运行以下命令即可爬取数据：

```sh
# 参数说明：
# keyword="双创",表示抓取shuangchuang_keywords.txt里面的关键词
# user_id和task_id为此次任务的id
# repeat为0表示全量抓取，repeat=1表示增量抓取，默认为0 
scrapy crawl baidunews -a keyword="双创" -a user_id=70 -a task_id=58 -a repeat=0  
```
 
## 各个任务的相关id：
 
| 任务         | user_id | task_id |
| :--------:   | :-----: | :----:  |
| 双创         | 70      | 58      |
| 智能家居     | 137     | 65      |
| 海尔智能家居 | 137     | 65      |
| 快思聪       | 137     | 65      |
| 河东hdl      | 137     | 65      |

## mongodb存储格式（以下数据为个人制造，仅以说明之用）：

```json
    {
        //关键词
        "keyword": "双创",
        //新闻标题
        "title": "“双创债”为创新创业企业融资 提供“快速通道”",
        //新闻简介
        "desc": "资本市场支持“双创” 主持人包兴安:今年以来,随着各项政策措施的落地生根,“双创”已成为培育新动能、壮大新经济的重要动力。资本市场在支持创新创业方面也在... ",
        //新闻链接
        "url": "http://www.p5w.net/money/zqzx/201611/t20161101_1622973.htm",
        //日期
        "date": "2016-11-01",
        //新闻来源
        "news_from": "全景网络",
        //新闻图片
        "img": "http://cz.ce.cn/xwzx/201611/01/W020161101503880892362.jpg",
        //新闻内容
        "content": "主持人包兴安：今年以来，随着各项政策措施的落地生根，“双创”已成为培育新动能、壮大新经济的重要动力。资本市场在支持创新创业方面也在发挥着越来越重要的作用，“双创”公司债的推出，一方面创新创业型企业将能获得低成本的资金，另一方面有利于引导社会闲散资金投入创新创业型企业，是金融服务实体经济的新举措。"
      
    }
```


# 百度双创新闻抓取

## 爬虫要求

- 可以抓取多组关键词
- 可以抓取搜索结果页的数据，大部分的新闻详情（部分网站的内容详情可能抓取不到）
- 根据URL去重

前期先抓取一组关键词，例如“双创”，对应的链接是: http://news.baidu.com/ns?word=%CB%AB%B4%B4&bs=%CB%AB%B4%B4&sr=0&cl=2&rn=20&tn=news&ct=0&clk=sortbytime

## 需要抓取的字段

- keyword: 搜索的关键词。例如“双创”
- title: 标题
- desc: 简介。搜索结果上的简介
- url: 新闻的最终url
- date: 日期。格式如“2016-08-08”，不能是其他格式
- from: 来源。在搜索结果页上，标题下方会有来源，例如“海南在线”
- pic: 图片。抓取图片地址即可，暂时不需要将图片下载到本地。
- content: 内容

一些程序存储数据时的附加字段，不能错，例如：

- \_userid: 用户ID
- \_ctid: 任务ID
- \_primary: 去重用的唯一键，如果使用url作为去重标准，则需要将url先计算md5字符串，取其中16个字节的字符串。

## 技术要求

- 基于python3开发
- 使用 https://github.com/codelucas/newspaper 抓取新闻内容，支持python3，该框架可以分析出一个我们需要的图片
- 数据保存到mongodb中，不能影响现有的数据


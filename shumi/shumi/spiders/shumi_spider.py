#!/usr/bin/env python
# coding=utf-8

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy import log
import time
import datetime
import re
import tornado.database

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")
# 已有数据
already_exit = []

class ShumiSpider(CrawlSpider):
    name = "shumi"
    allowed_domains = ["fund.fund123.cn"]
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)

    global db
    # 选出已有数据，用作重复判断
    select_sql = "select code from CurrencyFund"
    items = db.query(select_sql)
    for item in items:
        already_exit.append(item['code'])

    start_urls = []
    for i in range(1,6):
        url = "http://market.fund123.cn/result/index/gs-ft4-sya-syb-syc-syd-sye-syf-syg-syh-nv-ljnv-sh-fc-fm-pjh-pjz-i-ic-o-p" + str(i)
        start_urls.append(url)

    rules = (
            Rule(SgmlLinkExtractor(allow=('Index\.html',)), callback='parse_detail'),
        )


    def parse_detail(self, response):
        code = response.url.split('/')[-2]
        # 如果数据已存在
        if code in already_exit:
            return

        global db
        update_time = datetime.datetime.now()
        resource = u'数米网'
        hxs = HtmlXPathSelector(response)
        name = hxs.select('/html/body/div[4]/div/div[1]/div/div[1]/h1/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        interestTenThousand = hxs.select('/html/body/div[4]/div/div[2]/div[1]/p[2]/big/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        interestSevenDays = hxs.select('/html/body/div[4]/div/div[2]/div[2]/ul[1]/li[2]/big/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneMonth = hxs.select('/html/body/div[8]/div[2]/div[2]/div/div/div[3]/table/tbody/tr[3]/td[2]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseThreeMonth = hxs.select('/html/body/div[8]/div[2]/div[2]/div/div/div[3]/table/tbody/tr[4]/td[2]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseHalfYear = hxs.select('/html/body/div[8]/div[2]/div[2]/div/div/div[3]/table/tbody/tr[5]/td[2]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneYear = hxs.select('/html/body/div[8]/div[2]/div[2]/div/div/div[3]/table/tbody/tr[6]/td[2]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')

        sql = "insert into CurrencyFund(code,link,name,interestTenThousand,interestSevenDays,riseOneMonth,riseThreeMonth,riseHalfYear,riseOneYear,update_time,resource) values('"+code+"','"+response.url+"','"+name+"','"+interestTenThousand+"','"+interestSevenDays+"','"+riseOneMonth+"','"+riseThreeMonth+"','"+riseHalfYear+"','"+riseOneYear+"','"+str(update_time)+"','"+resource+"')"
        #print sql
        try:
            db.execute(sql)
            print u"代码: " + code + u", 名称: " + name + u" 已插入"
        except:
            print u"代码: " + code + u"插入出错"

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

class TiantianSpider(CrawlSpider):
    name = "tiantian"
    allowed_domains = ["fund.eastmoney.com", "fund.eastmoney.com"]
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)

    global db
    # 选出已有数据，用作重复判断
    select_sql = "select code from CurrencyFund"
    items = db.query(select_sql)
    for item in items:
        already_exit.append(item['code'])

    start_urls = []
    for i in range(1,13):
        url = "http://hq2data.eastmoney.com/fund/fundlist.aspx?jsName=fundListObj&fund=1&type=0&page=" + str(i) +"&dt=1371708038154"
        start_urls.append(url)

    rules = (
            Rule(SgmlLinkExtractor(allow=('\/\d{6}\.html',)), callback='parse_detail'),
        )


    def parse_detail(self, response):
        code = response.url.split('/')[-1].split('.')[0]
        # 如果数据已存在
        if code in already_exit:
            return

        global db
        update_time = datetime.datetime.now()
        resource = u'天天基金'
        hxs = HtmlXPathSelector(response)
        name = hxs.select('/html/body/div[9]/div[3]/div[1]/div[1]/div[1]/a/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        interestTenThousand = hxs.select('/html/body/div[9]/div[3]/div[1]/div[1]/div[2]/table/tr[1]/td[4]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        interestSevenDays = hxs.select('/html/body/div[9]/div[3]/div[1]/div[1]/div[2]/table/tr[2]/td[2]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneMonth = hxs.select('//*[@id="zfTab0"]/ul[3]/li[2]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseThreeMonth = hxs.select('//*[@id="zfTab0"]/ul[4]/li[2]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseHalfYear = hxs.select('//*[@id="zfTab0"]/ul[5]/li[2]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneYear = hxs.select('//*[@id="zfTab0"]/ul[6]/li[2]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')

        sql = "insert into CurrencyFund(code,link,name,interestTenThousand,interestSevenDays,riseOneMonth,riseThreeMonth,riseHalfYear,riseOneYear,update_time,resource) values('"+code+"','"+response.url+"','"+name+"','"+interestTenThousand+"','"+interestSevenDays+"','"+riseOneMonth+"','"+riseThreeMonth+"','"+riseHalfYear+"','"+riseOneYear+"','"+str(update_time)+"','"+resource+"')"
        #print sql
        try:
            db.execute(sql)
            print u"代码: " + code + u", 名称: " + name + u" 已插入"
        except:
            print u"代码: " + code + u"插入出错"

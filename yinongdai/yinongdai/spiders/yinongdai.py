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
    name = "yinongdai"
    allowed_domains = ["yinongdai.com"]
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)

    global db
    # 选出已有数据，用作重复判断
    select_sql = "select id from p2p where resource = '宜农贷'"
    items = db.query(select_sql)
    for item in items:
        already_exit.append(item['code'])
'''
    start_urls = []
    for i in range(1,6):
        url = "http://market.fund123.cn/result/index/gs-ft4-sya-syb-syc-syd-sye-syf-syg-syh-nv-ljnv-sh-fc-fm-pjh-pjz-i-ic-o-p" + str(i)
        start_urls.append(url)
'''
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
        resource = u'数米基金网'
        hxs = HtmlXPathSelector(response)
        name = hxs.select('/html/head/title/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').split('(')[0]
        company = hxs.select('//*[@class="zuhetable02 zuhetable05 zuhetable06"]/tbody/tr[6]/td[2]/a/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        company_link = hxs.select('//*[@class="zuhetable02 zuhetable05 zuhetable06"]/tbody/tr[6]/td[2]/a/@href').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        interestTenThousand = hxs.select('//big/text()').extract()[2].strip().lstrip().rstrip(',').replace(',','')
        interestSevenDays = hxs.select('//big/text()').extract()[3].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneMonth = hxs.select('//td[@class="r20 red"]/text()').extract()[4].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseThreeMonth = hxs.select('//td[@class="r20 red"]/text()').extract()[6].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseHalfYear = hxs.select('//td[@class="r20 red"]/text()').extract()[8].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneYear = hxs.select('//td[@class="r20 red"]/text()').extract()[10].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        try:
            buy_link = hxs.select('//a[@class="bug anbg"]/@href').extract()[0].replace('%','%%')
        except:
            buy_link = '-'

        sql = "insert into CurrencyFund(code,link,name,interestTenThousand,interestSevenDays,riseOneMonth,riseThreeMonth,riseHalfYear,riseOneYear,update_time,resource,company,company_link,buy_link) values('"+code+"','"+response.url+"','"+name+"','"+interestTenThousand+"','"+interestSevenDays+"','"+riseOneMonth+"','"+riseThreeMonth+"','"+riseHalfYear+"','"+riseOneYear+"','"+str(update_time)+"','"+resource+"','"+company+"','"+company_link+"','"+buy_link+"')"
        print sql
        try:
            db.execute(sql)
            print u"代码: " + code + u", 名称: " + name + u" 已插入"
        except:
            print u"代码: " + code + u"插入出错"

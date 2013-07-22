#!/usr/bin/env python
# coding=utf-8

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest, Request
from scrapy import log
import time
import datetime
import re
import tornado.database

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")
# 已有数据
already_exit = []

class ShumiSpider(BaseSpider):
    name = "haomai"
    allowed_domains = ["howbuy.com"]
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)

    global db
    # 选出已有数据，用作重复判断
    select_sql = "select code from CurrencyFund"
    items = db.query(select_sql)
    for item in items:
        already_exit.append(item['code'])

    start_urls = ['http://www.howbuy.com/fundtool/filter.htm']

    def parse(self, response):
        return [FormRequest.from_response(response,
            formdata={'category':'7','filterCondition':'category:7','filterConditionName':'基金分类:货币型'},
                    callback=self.after_login)
                ]
    def after_login(self, response):
        hxs = HtmlXPathSelector(response)
        trs = hxs.select('//*[@id="fundList"]/tr')
        for tr in trs:
            code = tr.select('td[3]/a/text()').extract()[0]
            if code in already_exit:
                continue
            else:
                yield Request("http://www.howbuy.com/fund/"+code+"/", callback = self.parse_detail)

    def parse_detail(self, response):
        code = response.url.split('/')[-2]

        # 如果数据已存在
        if code in already_exit:
            return

        global db
        update_time = datetime.datetime.now()
        resource = u'好买基金'
        hxs = HtmlXPathSelector(response)
        name = hxs.select('/html/body/div[3]/div[1]/h1/text()').extract()[0].split('(')[0]
        interestTenThousand = hxs.select('//*[@id="nTab1_Con1"]/table/tr[1]/td[1]/span/strong/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        interestSevenDays = hxs.select('//*[@id="nTab1_Con1"]/table/tr[1]/td[3]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneMonth = hxs.select('//*[@id="nTab1_Con1"]/table/tr[1]/td[6]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseThreeMonth = hxs.select('//*[@id="nTab1_Con1"]/table/tr[2]/td[1]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseHalfYear = hxs.select('//*[@id="nTab1_Con1"]/table/tr[2]/td[2]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneYear = hxs.select('//*[@id="nTab1_Con1"]/table/tr[2]/td[3]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')

        sql = "insert into CurrencyFund(code,link,name,interestTenThousand,interestSevenDays,riseOneMonth,riseThreeMonth,riseHalfYear,riseOneYear,update_time,resource) values('"+code+"','"+response.url+"','"+name+"','"+interestTenThousand+"','"+interestSevenDays+"','"+riseOneMonth+"','"+riseThreeMonth+"','"+riseHalfYear+"','"+riseOneYear+"','"+str(update_time)+"','"+resource+"')"
        #print sql
        try:
            db.execute(sql)
            print u"代码: " + code + u", 名称: " + name + u" 已插入"
        except:
            print u"代码: " + code + u"插入出错"

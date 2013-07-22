#!/usr/bin/env python
# coding=utf-8

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy import log
import re
import time
import datetime
import tornado.database

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")

class HaomaiUpdateSpider(BaseSpider):
    name = "update_haomai"
    allowed_domains = ["howbuy.com"]
    handle_httpstatus_list = [404]
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)
    start_urls = [ ]

    select_sql = "select link from CurrencyFund where resource = '好买基金'"
    items = db.query(select_sql)
    for item in items:
        start_urls.append(item['link'])

    def parse(self, response):
        global db
        code = response.url.split('/')[-2]
        if not 200 == response.status:
            sql = "delete from Currency where code = '" + code + "'"
            try:
                db.execute(sql)
            except:
                print u"数据删除出错"
            return

        hxs = HtmlXPathSelector(response)
        update_time = datetime.datetime.now()
        interestTenThousand = hxs.select('//*[@id="nTab1_Con1"]/table/tr[1]/td[1]/span/strong/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        interestSevenDays = hxs.select('//*[@id="nTab1_Con1"]/table/tr[1]/td[3]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneMonth = hxs.select('//*[@id="nTab1_Con1"]/table/tr[1]/td[6]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseThreeMonth = hxs.select('//*[@id="nTab1_Con1"]/table/tr[2]/td[1]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseHalfYear = hxs.select('//*[@id="nTab1_Con1"]/table/tr[2]/td[2]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneYear = hxs.select('//*[@id="nTab1_Con1"]/table/tr[2]/td[3]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')

        sql = "update CurrencyFund set interestTenThousand = '" + interestTenThousand + "', interestSevenDays = '" + interestSevenDays + "', riseOneMonth = '" + riseOneMonth + "', riseThreeMonth = '" + riseThreeMonth + "', riseHalfYear = '" + riseHalfYear + "', riseOneYear = '" + riseOneYear + "', update_time = '" + str(update_time) + "' where code = '" + code + "'"
        print sql
        try:
            db.execute(sql)
        except:
            print u"数据更新出错"

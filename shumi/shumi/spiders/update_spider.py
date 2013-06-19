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

class ShumiUpdateSpider(BaseSpider):
    name = "update_shumi"
    allowed_domains = ["fund.fund123.cn"]
    handle_httpstatus_list = [404]
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)
    start_urls = [ ]

    select_sql = "select link from CurrencyFund where resource = '数米网'"
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
        interestTenThousand = hxs.select('/html/body/div[6]/div/div[2]/div[1]/p[2]/big/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        interestSevenDays = hxs.select('/html/body/div[6]/div/div[2]/div[2]/ul[1]/li[2]/big/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneMonth = hxs.select('/html/body/div[8]/div[2]/div[2]/div/div/div[3]/table/tbody/tr[3]/td[2]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseThreeMonth = hxs.select('/html/body/div[8]/div[2]/div[2]/div/div/div[3]/table/tbody/tr[4]/td[2]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseHalfYear = hxs.select('/html/body/div[8]/div[2]/div[2]/div/div/div[3]/table/tbody/tr[5]/td[2]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')
        riseOneYear = hxs.select('/html/body/div[8]/div[2]/div[2]/div/div/div[3]/table/tbody/tr[6]/td[2]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').replace('%','')

        sql = "update CurrencyFund set interestTenThousand = " + interestTenThousand + ", interestSevenDays = " + interestSevenDays + ", riseOneMonth = '" + riseOneMonth + "', riseThreeMonth = '" + riseThreeMonth + "', riseHalfYear = '" + riseHalfYear + "', riseOneYear = '" + riseOneYear + "', update_time = '" + str(update_time) + "' where code = '" + code + "'"
        print sql
        try:
            db.execute(sql)
        except:
            print u"数据更新出错"

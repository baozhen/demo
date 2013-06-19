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

class PPdaiUpdateSpider(BaseSpider):
    name = "update_ppdai"
    allowed_domains = ["ppdai.com"]
    
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)
    
    start_urls = [ ]   

    sql = "select link from p2p where resource = '拍拍贷' and complete_percent < 100"
    urls = db.query(sql)

    for item in urls:
        start_urls.append(item['link'])

    def parse(self, response):
        global db
        hxs = HtmlXPathSelector(response)

        uid = response.url.split('/')[-1]
        update_time = datetime.datetime.now()

        amount = hxs.select('//*[@id="allMoney"]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        amount = re.findall('(\d+).*?', amount)[0]
        complete_percent = hxs.select('//*[@id="jdProgress"]/text()').extract()[0].strip().lstrip().rstrip(',')
        
        #如果已经满额
        if 100 == int(complete_percent):
            remain_amount = 0
            sql = "update p2p set amount = " + amount + " , used_amount = " + amount + " , remain_amount = 0 , update_time = '" + str(update_time) + "' , complete_percent = '100' where id = '" + uid + "'"
            print sql
        else:
            remain_amount = hxs.select('//*[@id="allsxMoney"]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
            remain_amount = re.findall('(\d+).*?',remain_amount)[0]
            used_amount = str(int(amount) - int(remain_amount))
            sql = "update p2p set amount = " + amount + " , used_amount = " + used_amount + " , remain_amount = " + remain_amount + " , update_time = '" + str(update_time) + "', complete_percent = '" + complete_percent + "' where id = '" + uid + "'"
            print sql

        try:
            db.execute(sql)
        except:
            print "数据更新出错"

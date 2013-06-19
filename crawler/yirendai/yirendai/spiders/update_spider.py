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

class YirendaiUpdateSpider(BaseSpider):
    name = "update_yirendai"
    allowed_domains = ["yirendai.com"]
    
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)
    
    start_urls = [ ]   

    sql = "select link from p2p where resource = '宜人贷' and complete_percent < 100"
    urls = db.query(sql)

    for item in urls:
        start_urls.append(item['link'])

    def parse(self, response):
        global db
        hxs = HtmlXPathSelector(response)

        uid = response.url.split('=')[1]
        update_time = datetime.datetime.now()

        amount = hxs.select('/html/body/div[3]/div[2]/div[1]/table/tbody/tr[3]/td/span[1]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        complete = hxs.select('//span[@class="loadingNum_text"]/text()').extract()[0].strip().lstrip().rstrip(',')
        complete_percent = re.findall('(\d+).*?', complete)[0]

        #如果已经满额
        if 100 == int(complete_percent):
            remain_amount = 0
            sql = "update p2p set amount = " + amount + " , used_amount = " + amount + " , remain_amount = 0 , update_time = '" + str(update_time) + "' , complete_percent = '100' where id = '" + uid + "'"
            print sql
        else:
            remain_amount = hxs.select('/html/body/div[3]/div[2]/div[1]/table/tbody/tr[6]/td/span[1]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
            used_amount = str(int(amount) - int(remain_amount))
            sql = "update p2p set amount = " + amount + " , used_amount = " + used_amount + " , remain_amount = " + remain_amount + " , update_time = '" + str(update_time) + "', complete_percent = '" + complete_percent + "' where id = '" + uid + "'"
            print sql

        try:
            db.execute(sql)
        except:
            print "数据更新出错"

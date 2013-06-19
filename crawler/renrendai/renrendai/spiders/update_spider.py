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

class RenrendaiUpdateSpider(BaseSpider):
    name = 'update_renrendai'
    allowed_domains = ["renrendai.com"]
    download_delay = 5
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)
        
    start_urls = [ ]   

    sql = "select link from p2p where resource = '人人贷' and complete_percent < 100"
    urls = db.query(sql)

    for item in urls:
        start_urls.append(item['link'])

    def parse(self, response):
        global db
        detail_hxs = HtmlXPathSelector(response)

        uid = response.url.split('=')[1]
        update_time = datetime.datetime.now()

        amount = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[1]/div[1]/p[1]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        amount = re.findall('(\d+).*?', amount)[0]
        #已经开始还款
        if 0 == len(detail_hxs.select('//*[@id="bid1"]').extract()):
            complete_percent = '100'
        else:
            complete_percent = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[4]/span[1]/text()').extract()[0].strip().lstrip().rstrip(',').replace('%','')
        
        #如果已经满额
        if 100 == int(complete_percent):
            remain_amount = 0
            sql = "update p2p set amount = "+amount+" , used_amount = "+amount+" , remain_amount = 0 , update_time = '" + str(update_time) + "' , complete_percent = '100' where id = '" + uid + "'"
            print sql
        else:
            remain_amount = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[4]/span[3]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
            remain_amount = re.findall('(\d+).*?', remain_amount)[0]
            used_amount = str(int(amount) - int(remain_amount))
            sql = "update p2p set amount = " + amount + " , used_amount = " + used_amount + " , remain_amount = " + remain_amount + " , update_time = '" + str(update_time) + "', complete_percent = '" + complete_percent + "' where id = '" + uid + "'"
            print sql

        try:
            db.execute(sql)
        except:
            print "数据更新出错"

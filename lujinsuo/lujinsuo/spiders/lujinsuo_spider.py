#!/usr/bin/env python
# coding=utf-8

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy import log
import re
import time
import datetime
import tornado.database
import simplejson
import json

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")

class LujinsuoSpider(BaseSpider):
    name = "lujinsuo"
    allowed_domains = ["lufax.com"]
    download_delay = 1
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)

    start_urls = [
            "http://www.lufax.com/list/service/product/listing/1?minAmount=0&maxAmount=100000000&minInstalments=1&maxInstalments=240&collectionMode=&productName=&column=&order=asc&isDefault=true&pageLimit=20&_=1370675513063"
        ]

    def parse(self, response):
        global db
        hxs = HtmlXPathSelector(response)
        json_raw = hxs.select('*').extract()[0]
        json_raw = json_raw.encode('utf8')[9:-11]
        json_dict = simplejson.loads(json_raw)
        data = json_dict['data']
        resource = u'陆金所'.encode('utf8')

        for detail in data:
            uid = str(detail['productId'])
            name =  detail['productNameDisplay'].encode('utf8')
            link = "http://www.lufax.com/list/productDetail?productId="+uid
            amount = detail['price']
            interest = detail['interestRateDisplay'] * 100
            period = detail['numberOfInstalments']
            status = detail['productStatus']
            if cmp("DONE", status):
                used_amount = '0'
                remain_amount = str(amount)
                complete_percent = '0'
                bidder_num = '0'
                deadline = datetime.datetime.now() + datetime.timedelta(days=3)
            else:
                used_amount = str(amount)
                remain_amount = '0'
                complete_percent = '100'
                bidder_num = '1'
                deadline = datetime.datetime.now()

            #是否已经存在
            test_sql = u'select * from p2p where id = "' + uid + '"'
            print len(db.query(test_sql))
            if 0 == len(db.query(test_sql)):
                sql = "insert into p2p values('"+uid+"','"+link+"','"+name+"', '', 'A', '', "+str(amount)+","+str(interest)+","+str(period)+","+used_amount+","+remain_amount+","+complete_percent+",'"+str(deadline)+"','"+str(datetime.datetime.now())+"','0',"+bidder_num+",'"+resource+"')"
                print sql
                try:
                    db.execute(sql)
                except:
                    print "插入数据出错"

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
        hxs = HtmlXPathSelector(response)
        json_raw = hxs.select('*').extract()[0]
        json_raw = json_raw.encode('utf8')[9:-11]
        #print json_raw, type(json_raw)
        json_dict = simplejson.loads(json_raw)
        #print json_dict, type(json_dict)
        data = json_dict['data']
        #print data[0]['productId'], type(data[0]['productId'])

        for detail in data:
            print detail['productId']
            print detail['productNameDisplay']


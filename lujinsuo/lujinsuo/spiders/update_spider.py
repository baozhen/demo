#!/usr/bin/env python
# coding=utf-8

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy import log
import re
import simplejson
import time
import datetime
import tornado.database

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")

class LujinsuoUpdateSpider(BaseSpider):
    name = 'update_lujinsuo'
    allowed_domains = ["lufax.com"]
    download_delay = 1
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)

    start_urls = [ ]
    
    select_sql = "select id from p2p where resource = '陆金所' and complete_percent < 100"
    uids = db.query(select_sql)

    for uid in uids:
        print type(uid), uid
        url = "http://www.lufax.com/list/service/product/" + uid['id'] + "/productDetail?_=1370761334206"
        start_urls.append(url)

    def parse(self, response):
        global db
        detail_hxs = HtmlXPathSelector(response)
        json_raw = detail_hxs.select('*').extract()[0]
        json_raw = json_raw.encode('utf8')[9:-11]
        json_dict = simplejson.loads(json_raw)

        uid = response.url.split('/')[6]

        if cmp("DONE", json_dict['productStatus']):
            sql = "update p2p set used_amount = amount, remain_amount = 0, complete_percent = 100, bidder_num = 1, update_time = '"+ str(datetime.datetime.now()) +"' where id = '" + uid + "'"
            print sql
            try:
                db.execute(sql)
            except:
                print "数据更新出错"

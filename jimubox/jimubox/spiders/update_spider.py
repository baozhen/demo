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

class JimuboxUpdateSpider(BaseSpider):
    name = 'update_jimubox'
    allowed_domains = ["jimubox.com"]
    handle_httpstatus_list = [404]
    download_delay = 2
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)
    start_urls = [ ]
    select_sql = "select link from p2p where resource = '积木盒子' and complete_percent < 100"
    uids = db.query(select_sql)

    for uid in uids:
        start_urls.append(uid['link'])

    def parse(self, response):
        global db
        uid = response.url.split('/')[-1]
        # 下载页面出错
        if not 200 == response.status:
            sql = "delete from p2p where id = '" + uid + "'"
            print sql
            try:
                db.execute(sql)
            except:
                print "数据删除出错"
            return
        hxs = HtmlXPathSelector(response)
        complete = hxs.select('/html/body/div[2]/div[1]/div[2]/div[2]/dl/dd/div/div[1]/text()').extract()
        if len(complete) == 0:
            sql = "update p2p set used_amount = amount, remain_amount = 0, complete_percent = 100, update_time = '" + str(datetime.datetime.now()) + "' where id = '" + uid + "'"
        else:
            complete_percent = complete[0].replace('%','')
            remain_amount = hxs.select('/html/body/div[2]/div[1]/div[2]/div[3]/dl/dd/text()').extract()[0].split('.')[0]
            amount = hxs.select('/html/body/div[2]/div[1]/div[1]/div[3]/div[1]/span[2]/text()').extract()[0].split('.')[0] + '0000'
            used_amount = str(float(amount) - float(remain_amount))
            sql = "update p2p set used_amount = '" + used_amount + "', remain_amount = '" + remain_amount + "', complete_percent = '" + complete_percent + "', update_time = '" + str(datetime.datetime.now()) + "' where id = '" + uid + "'"


        print sql
        try:
            db.execute(sql)
        except:
            print "数据更新出错"

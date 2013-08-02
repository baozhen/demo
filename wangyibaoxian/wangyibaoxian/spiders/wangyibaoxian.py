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

class YirendaiSpider(BaseSpider):
    name = "wangyibaoxian"
    allowed_domains = ["163.com"]
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)

    start_urls = [ 
            "http://baoxian.163.com/products/invest/",
        ]   

    def parse(self, response):
        global db
        hxs = HtmlXPathSelector(response)
        divs = hxs.select('//*[@id="productList"]/li')

        for div in divs:
            shortlink = div.select('h2/a/@href').extract()[0]
            uid = shortlink.split('/')[-1].split('.')[0]
            link = u'http://baoxian.163.com' + shortlink
            name = div.select('h2/a/b/text()').extract()[0].strip().lstrip().rstrip(',')
            interest = div.select('div[1]/span[1]/text()').extract()[0]
            print name, interest

'''
            amount = div.select('div[1]/table/tbody/tr[2]/td[1]/strong/text()').extract()[0].strip().lstrip().rstrip(',')
            period = div.select('div[1]/table/tbody/tr[4]/td[1]/strong/text()').extract()[0].strip().lstrip().rstrip(',')
            used_amount = div.select('div[1]/table/tbody/tr[3]/td[1]/strong/text()').extract()[0].strip().lstrip().rstrip(',')
            remain_amount = str(int(amount) - int(used_amount))
            complete = div.select('div[2]/div[1]/div/span/text()').extract()[0].strip().lstrip().rstrip(',')
            complete_percent = re.findall('(\d+).*?', complete)[0]
            bidder_num = div.select('div[1]/table/tbody/tr[3]/td[2]/strong/text()').extract()[0].strip().lstrip().rstrip(',')
            remain_time = div.select('div[2]/div[2]/div[2]/strong/text()').extract()[0].strip().lstrip().rstrip(',')
            deadline = calculate_time(self, remain_time)

            test_sql = "select id from p2p where id = " + uid
            if 0 == len(db.query(test_sql)):
                sql = "insert into p2p values('"+uid+"','"+link+"','"+name+"', '', 'A', '', "+amount+","+interest+","+period+","+used_amount+","+remain_amount+","+complete_percent+",'"+str(deadline)+"','"+str(datetime.datetime.now())+"','0',"+bidder_num+",'"+resource+"','"+risk+"',"+start_amount+")"
                print sql.encode('utf-8')
                try:
                    db.execute(sql)
                except:
                    print "插入数据出错".encode('utf-8')

'''

def calculate_time(self, remain_time):
    hlist = re.findall('(\d+).*?(\d+).*?(\d+).*?',remain_time)
    minutes = int(hlist[0][0]) * 60 * 24 + int(hlist[0][1]) * 60 + int(hlist[0][2])
    deadline = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    return deadline

def data_insert(self, product):
    global db
    insert = 0 #插入标志
    uid = product['uid']
    test_sql = "select count(*) from p2p where id = " + uid
    print test_sql
    if len(db.query(test_sql)) > 0:
        print "id = " + uid + "数据已存在"
        return

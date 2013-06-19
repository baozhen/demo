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

class PPdaiSpider(BaseSpider):
    name = "ppdai"
    allowed_domains = ["ppdai.com"]

    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)

    start_urls = [ 
            "http://www.ppdai.com/lend/",
        ]   

    for i in range(2, 100):
        url = "http://www.ppdai.com/lend/default.aspx?page=" + str(i) + "&"
        start_urls.append(url)

    def parse(self, response):
        global db
        hxs = HtmlXPathSelector(response)
        trs = hxs.select('//tr[@class="tr"]')

        for tr in trs:
            product = {}
            shortlink = tr.select('td[2]/div/a/@href').extract()[0]
            
            uid = shortlink.split('/')[2]
            link = u'http://www.ppdai.com' + shortlink
            print u'**********************************************'
            product['uid'] = uid
            product['link'] = link
            
            credit_level = tr.select('td[7]/a/text()').extract()[0].strip().lstrip().rstrip(',').replace('(','').replace(')','')
            if 'HR' == credit_level:
                continue

            name = tr.select('td[2]/div/a/text()').extract()[0].strip().lstrip().rstrip(',')
            print name.encode('utf-8')
            product['name'] = name
            amount = tr.select('td[4]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
            amount = re.findall('(\d+).*?', amount)[0]
            interest = tr.select('td[5]/text()').extract()[0].strip().lstrip().rstrip(',')
            interest = interest.split('.')[0]
            product['interest'] = interest
            period = tr.select('td[6]/text()').extract()[0].strip().lstrip().rstrip(',')
            product['period'] = period

            complete = tr.select('td[8]/span[2]/text()').extract()[0].strip().lstrip().rstrip(',')
            complete_percent = re.findall('(\d+).*?', complete)[0]
            product['complete_percent'] = complete_percent

            used_amount = str(int(amount) * int(complete_percent) / 100)
            remain_amount = str(int(amount) - int(used_amount))
            product['amount'] = amount
            product['remain_amount'] = remain_amount
            product['used_amount'] = used_amount

            bidder_num = tr.select('td[8]/span[3]/text()[1]').extract()[0].strip().lstrip().rstrip(',')
            bidder_num = re.findall('(\d+).*?', bidder_num)[0]
            product['bidder_num'] = bidder_num

            if len(tr.select('td[8]/span[3]/text()[2]').extract()) == 0:
                continue
            remain_time = tr.select('td[8]/span[3]/text()[2]').extract()[0].strip().lstrip().rstrip(',')
            deadline = calculate_time(self, remain_time)
            product['deadline'] = deadline
            print product
            resource = u'拍拍贷'

            test_sql = "select id from p2p where id = " + uid
            if len(db.query(test_sql)) > 0:
                #print "id = " + uid + u' 数据已存在'
                try:
                    db.execute("delete from p2p where id = " + uid)
                except:
                    print "更新已有数据出错".encode('utf-8')
            sql = "insert into p2p values('"+uid+"','"+link+"','"+name+"', '', '"+credit_level+"', '', "+amount+","+interest+","+period+","+used_amount+","+remain_amount+","+complete_percent+",'"+str(deadline)+"','" + str(datetime.datetime.now()) + "','0',"+bidder_num+",'"+resource+"')"
            print sql.encode('utf-8')
            try:
                db.execute(sql)
            except:
                print "插入数据出错".encode('utf-8')


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

#!/usr/bin/env python
# coding=utf-8


from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
import re
import time
import datetime
import tornado.database

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")

class YirendaiSpider(BaseSpider):
    name = "yirendai"
    allowed_domains = ["yirendai.com"]
    start_urls = [ 
            "http://www.yirendai.com/LenderApplyListAction/applyInfoListPage.action"
            "http://www.yirendai.com/LenderInvest/applyInfoListPage.action?pager.offset=10&isJYD=&iapproveNo=&currRate=&iapproveAmt=&productType="
        ]   

    def parse(self, response):
        global db
        hxs = HtmlXPathSelector(response)
        divs = hxs.select('//div[@class="tab_box"]')

        for div in divs:
            product = {}
            shortlink = div.select('div[1]/table/tbody/tr[1]/td[2]/a/@href').extract()[0]
            uid = shortlink.split('=')[1]
            link = u'http://www.yirendai.com' + shortlink
            print u'**********************************************'
            print uid
            print link
            product['uid'] = uid
            product['link'] = link
            name = div.select('div[1]/table/tbody/tr[1]/td[2]/a/h3/text()').extract()[0].strip().lstrip().rstrip(',')
            print name
            product['name'] = name
            amount = div.select('div[1]/table/tbody/tr[2]/td[1]/strong/text()').extract()[0].strip().lstrip().rstrip(',')
            interest = div.select('div[2]/div[1]/span/strong[1]/text()').extract()[0].strip().lstrip().rstrip(',')
            print interest
            product['interest'] = interest
            period = div.select('div[1]/table/tbody/tr[4]/td[1]/strong/text()').extract()[0].strip().lstrip().rstrip(',')
            print period
            product['period'] = period
            used_amount = div.select('div[1]/table/tbody/tr[3]/td[1]/strong/text()').extract()[0].strip().lstrip().rstrip(',')
            remain_amount = str(int(amount) - int(used_amount))
            print amount, remain_amount, used_amount
            product['amount'] = amount
            product['remain_amount'] = remain_amount
            product['used_amount'] = used_amount
            complete = div.select('div[2]/div[1]/div/span/text()').extract()[0].strip().lstrip().rstrip(',')
            complete_percent = re.findall('(\d+).*?', complete)[0]
            print complete_percent
            product['complete_percent'] = complete_percent
            bidder_num = div.select('div[1]/table/tbody/tr[3]/td[2]/strong/text()').extract()[0].strip().lstrip().rstrip(',')
            print bidder_num
            product['bidder_num'] = bidder_num
            remain_time = div.select('div[2]/div[2]/div[2]/strong/text()').extract()[0].strip().lstrip().rstrip(',')
            deadline = calculate_time(self, remain_time)
            print deadline
            product['deadline'] = deadline
            print product
            resource = u'宜人贷'

            test_sql = "select id from p2p where id = " + uid
            print test_sql
            if len(db.query(test_sql)) > 0:
                #print "id = " + uid + "数据已存在"
                pass
            else:
                sql = "insert into p2p values('"+uid+"','"+link+"','"+name+"', '', '', "+amount+","+interest+","+period+","+used_amount+","+remain_amount+","+complete_percent+",'"+str(deadline)+"','0',"+bidder_num+",'"+resource+"')"
                print sql
                try:
                    db.execute(sql)
                except:
                    print "插入出错"



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

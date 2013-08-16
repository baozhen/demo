#!/usr/bin/env python
# coding=utf-8

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy import log
import re
import time
import datetime
import tornado.database
import simplejson

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")
id_dict = []

class ZhengdaSpider(BaseSpider):
    name = "dianrong"
    allowed_domains = ["dianrong.com"]
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)
    start_urls = [
            "http://www.dianrong.com/browse/browse"
        ]
    global db
    select_sql = "select id from p2p where resource = '点融网' and complete_percent < 100"
    for item in db.query(select_sql):
        id_dict.append(item['id'])

    sql_100 = "update p2p set complete_percent = 100 where resource = '点融网' and complete_percent < 100"
    db.execute(sql_100)

    def parse(self, response):
        global db
        hxs = HtmlXPathSelector(response)
        yield Request(url='http://www.dianrong.com/browse/searchLoans', method='POST', callback=self.json_parse, body='sortBy=unfundedAmount&sortDir=asc&page=0&pageSize=10&includeFullyFunded=true', headers={'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'})

    def json_parse(self, response):
        hxs = HtmlXPathSelector(response)
        total = hxs.select('//p').extract()[0].replace('<p>','').replace('</p>','')
        json_dict = simplejson.loads(total)
        searchresult = json_dict['searchresult']
        loans = searchresult['loans']
        for loan in loans:
            if not loan['loan_status'] == 'INFUNDING':
                continue
            name = loan['title']
            amount = str(loan['loanAmt'])
            remain_amount = str(loan['loanAmtRemaining'])
            used_amount = str(int(amount) - int(remain_amount))
            uid = str(loan['loanGUID'])
            link = 'http://www.dianrong.com/browse/browse'
            interest = str(loan['loanRate'])
            period = str(loan['loanLength'])
            remain_seconds = int(loan['loanTimeRemaining'])
            deadline = calculate_time(self, remain_seconds)
            level = loan['loanGrade'][0:1]
            complete_percent = str(int(used_amount) * 100 / int(amount))
            resource = u'点融网'
            risk = u'保本'
            start_amount = '100'

            if uid in id_dict:
                update_sql = "update p2p set used_amount = " + used_amount + ", remain_amount = " + remain_amount + ", complete_percent = " + complete_percent + ", update_time = '" + str(datetime.datetime.now()) + "' where id = '" + uid + "'"
                print update_sql
                db.execute(update_sql)
            else:
                insert_sql = "insert into p2p(id, link, name, credit_level, amount, interest, period, used_amount, remain_amount, complete_percent, deadline, update_time, resource, risk, start_amount) values('"+uid+"','"+link+"','"+name+"','"+level+"', "+amount+","+interest+","+period+","+used_amount+","+remain_amount+","+complete_percent+",'"+str(deadline)+"','"+str(datetime.datetime.now())+"','"+resource+"','"+risk+"',"+start_amount+")"
                print insert_sql.encode('utf-8')
                db.execute(insert_sql)

def calculate_time(self, remain_seconds):
    deadline = datetime.datetime.now() + datetime.timedelta(milliseconds=remain_seconds)
    return deadline

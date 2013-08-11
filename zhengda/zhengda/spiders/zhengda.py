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

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")
id_dict = []

class ZhengdaSpider(BaseSpider):
    name = "zhengda"
    allowed_domains = ["onlinecredit.cn"]
    download_delay = 1

    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)

    start_urls = [
            "http://www.onlinecredit.cn/online/financial/searchLoan/loanIng?column=none&seq=none&p=none&_=1376373217562"
        ]
    global db
    select_sql = "select id from p2p where resource = '证大e贷'"
    for item in db.query(select_sql):
        id_dict.append(item['id'])

    sql_100 = "update p2p set complete_percent = 100 where resource = '证大e贷'"
    db.execute(sql_100)

    def parse(self, response):
        global db
        hxs = HtmlXPathSelector(response)
        trs = hxs.select('//tr')
        trs = trs[1:]
        for tr in trs:
            name = tr.select('td[2]/a/text()').extract()[0]
            link = tr.select('td[2]/a/@href').extract()[0]
            uid = link.split('=')[1]
            link = "http://www.onlinecredit.cn" + link 
            amount = tr.select('td[3]/text()').extract()[0].strip().lstrip().rstrip(',').replace(u'￥','').split('.')[0]
            interest = tr.select('td[4]/text()').extract()[0].strip().lstrip().rstrip(',').replace(u'%','').split('.')[0]
            period = tr.select('td[5]/text()').extract()[0].strip().lstrip().rstrip(',').replace(u'个月','')
            level = tr.select('td[7]/img/@src').extract()[0].strip().lstrip().rstrip(',')
            remain = tr.select('td[8]').extract()[0].split('</div>')[1].replace(',','')
            bidder_num = re.findall('(\d+).*?', remain)[0] 
            remain_amount = re.findall('(\d+).*?', remain)[1] 
            used_amount = str(int(amount) - int(remain_amount))
            remain_time = remain.split(u'：')[1].replace('</td>','').strip().lstrip().rstrip(',')
            deadline = calculate_time(self, remain_time)
            complete_percent = tr.select('td[8]/div/em/text()').extract()[0].replace('%','')
            resource = u'证大e贷'
            risk = u'保本保息'
            start_amount = '50'
            if uid in id_dict:
                update_sql = "update p2p set used_amount = " + used_amount + ", remain_amount = " + remain_amount + ", complete_percent = " + complete_percent + ", bidder_num = " + bidder_num + " where id = '" + uid + "'"
                print update_sql
            else:
                insert_sql = "insert into p2p(id, link, name, credit_level, amount, interest, period, used_amount, remain_amount, complete_percent, deadline, update_time, bidder_num, resource, risk, start_amount) values('"+uid+"','"+link+"','"+name+"', 'A', "+amount+","+interest+","+period+","+used_amount+","+remain_amount+","+complete_percent+",'"+str(deadline)+"','"+str(datetime.datetime.now())+"',"+bidder_num+",'"+resource+"','"+risk+"',"+start_amount+")"
                print insert_sql.encode('utf-8')
                db.execute(insert_sql)
            '''
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

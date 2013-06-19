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

class RenrendaiSpider(BaseSpider):
    name = "renrendai"
    allowed_domains = ["renrendai.com"]
    download_delay = 5

    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)

    start_urls = [
            "http://www.renrendai.com/lend/loanList.action?id=all_biao_list&pageIndex=1"
        ]
   
    for i in range(2, 20):
        url = "http://www.renrendai.com/lend/loanList.action?id=all_biao_list&pageIndex=" + str(i) + "&orderid=0&amountAsc=false&monthsAsc=false&interestAsc=false&creditAsc=false&versionAsc=false&endTimeAsc=true"
        start_urls.append(url)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        divs = hxs.select('//*[@class="center biaoli"]')

        for div in divs:
            link = "http://www.renrendai.com" + div.select('div/div[2]/div[1]/div[1]/a[1]/@href').extract()[0][2:]
            complete = div.select('div/div[2]/div[7]/div[1]/p/text()').extract()[0]
            try:
                complete_percent = int(complete.replace('%',''))
            except:
                continue
            if(complete_percent == 100):
                continue
            yield Request(link, callback = self.parse_detail)

    def parse_detail(self, response):
        global db
        detail_hxs = HtmlXPathSelector(response)
        name = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/text()').extract()[0].strip().lstrip().rstrip(',')
        link = response.url
        uid = link.split('=')[1]
        amount = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[1]/div[1]/p[1]/span/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        amount = re.findall('(\d+).*?', amount)[0]
        interest = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[1]/div[1]/p[2]/span[1]/text()').extract()[0].strip().lstrip().rstrip(',').split('.')[0]
        credit_level = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[3]/div/div[2]/div[3]/p[2]/a/img/@title').extract()[0].strip().lstrip().rstrip(',')
        period = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[1]/div[1]/p[2]/span[2]/text()').extract()[0].strip().lstrip().rstrip(',')
        period = re.findall('(\d+).*?', period)[0]
        remain_amount =  detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[4]/span[3]/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','')
        remain_amount = re.findall('(\d+).*?', remain_amount)[0]
        used_amount = str(int(amount) - int(remain_amount))
        complete_percent = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[4]/span[1]/text()').extract()[0].strip().lstrip().rstrip(',').replace('%','')
        remain_time = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[4]/div[3]/text()').extract()[0].strip().lstrip().rstrip(',')
        deadline = calculate_time(self, remain_time)
        bidder_num = detail_hxs.select('//*[@id="content"]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[4]/span[2]/text()').extract()[0].strip().lstrip().rstrip(',')
        resource = u'人人贷'
        #print name,uid, amount, credit_level, period, complete_percent, remain_time, deadline, bidder_num
        test_sql = "select id from p2p where id = " + uid
        if 0 == len(db.query(test_sql)):
            sql = "insert into p2p values('"+uid+"','"+link+"','"+name+"', '', 'A', '', "+amount+","+interest+","+period+","+used_amount+","+remain_amount+","+complete_percent+",'"+str(deadline)+"','"+str(datetime.datetime.now())+"','0',"+bidder_num+",'"+resource+"')"
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

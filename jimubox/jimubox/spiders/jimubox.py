#!/usr/bin/env python
# coding=utf-8

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy import log
import time
import datetime
import re
import tornado.database

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")
# 已有数据
already_exit = []

class JimuboxSpider(CrawlSpider):
    name = "jimubox"
    allowed_domains = ["jimubox.com"]
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)
    download_delay = 2
    global db
    # 选出已有数据，用作重复判断
    select_sql = "select id from p2p where resource = '积木盒子'"
    items = db.query(select_sql)
    for item in items:
        already_exit.append(item['id'])
    start_urls = ["http://www.jimubox.com/Project/List"]
    rules = (
            Rule(SgmlLinkExtractor(allow=(r'/Project/Index/\d+',)), callback='parse_detail'),
        )

    def parse_detail(self, response):
        link = response.url
        uid = link.split('/')[-1]
        # 如果数据已存在
        if uid in already_exit:
            return
        global db
        hxs = HtmlXPathSelector(response)
        complete = hxs.select('/html/body/div[2]/div[1]/div[2]/div[2]/dl/dd/div/div[1]/text()').extract()
        if len(complete) == 0:
            return
        complete_percent = complete[0].replace('%','')
        name = hxs.select('/html/body/div[2]/div[1]/div[1]/div[1]/h4/text()').extract()[0].strip().lstrip().rstrip(',').replace(',','').split('(')[0]
        amount = hxs.select('/html/body/div[2]/div[1]/div[1]/div[3]/div[1]/span[2]/text()').extract()[0].split('.')[0] + '0000'
        interest = hxs.select('/html/body/div[2]/div[1]/div[1]/div[3]/div[2]/span[2]/text()').extract()[0].replace('%','')
        period = hxs.select('/html/body/div[2]/div[1]/div[1]/div[3]/div[3]/span[2]/text()').extract()[0].replace(u'个月','').strip().lstrip().rstrip(',')
        remain_amount = hxs.select('/html/body/div[2]/div[1]/div[2]/div[3]/dl/dd/text()').extract()[0].split('.')[0]
        used_amount = str(float(amount) - float(remain_amount))
        remain_time = hxs.select('/html/body/div[2]/div[1]/div[2]/div[1]/dl/dd/text()').extract()[0]
        deadline = calculate_time(self, remain_time)
        bidder_num = str(len(hxs.select('/html/body/div[2]/div[3]/div/table/tbody/tr').extract()))
        update_time = datetime.datetime.now()
        resource = u'积木盒子'
        risk = u'保本保息'
        start_amount = '100'
        sql = "insert into p2p values('"+uid+"','"+link+"','"+name+"', '', 'A', '', "+amount+","+interest+","+period+","+used_amount+","+remain_amount+","+complete_percent+",'"+str(deadline)+"','"+str(datetime.datetime.now())+"','0',"+bidder_num+",'"+resource+"','"+risk+"',"+start_amount+")"
        print sql
        try:
            db.execute(sql)
            print u"代码: " + uid + u", 名称: " + name + u" 已插入"
        except:
            print u"代码: " + uid + u"插入出错"
def calculate_time(self, remain_time):
    hlist = re.findall('(\d+).*?(\d+).*?(\d+).*?',remain_time)
    minutes = int(hlist[0][0]) * 60 * 24 + int(hlist[0][1]) * 60 + int(hlist[0][2])
    deadline = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    return deadline

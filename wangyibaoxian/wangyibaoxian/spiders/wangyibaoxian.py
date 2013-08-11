#!/usr/bin/env python
# coding=utf-8

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy import log
from scrapy.http import Request
import re
import time
import datetime
import tornado.database

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")
interest_dict = {}

class YirendaiSpider(BaseSpider):
    name = "wangyibaoxian"
    allowed_domains = ["163.com"]
    log.start(logfile='/root/scrapy.log', loglevel=log.INFO, logstdout=False)
    start_urls = [ 
            "http://baoxian.163.com/products/invest/",
        ]   

    def parse(self, response):
        global db, interest_dict
        hxs = HtmlXPathSelector(response)
        total = hxs.select('//*').extract()[0]
        interest_all = re.findall('"(\d+)":{"-1":"(.*?)"',total)
        for interest in interest_all:
            interest_dict[interest[0]] = interest[1]
        divs = hxs.select('//*[@id="productList"]/li')

        for div in divs:
            shortlink = div.select('h2/a/@href').extract()[0]
            uid = shortlink.split('/')[-1].split('.')[0]
            link = u'http://baoxian.163.com' + shortlink
            name = div.select('h2/a/b/text()').extract()[0].strip().lstrip().rstrip(',')
            interest = interest_dict[uid]
            summary = div.select('h2/a/span/text()').extract()[0]
            start_amount = div.select('div[3]/span/text()[1]').extract()[0]
            start_amount = re.findall('(\d+).*?', start_amount)[0]
            limit_interest = div.select('div[3]/span/text()[3]').extract()[0]
            limit_interest = re.findall('(\d+.\d+).*?', limit_interest)[0]
            period = div.select('div[3]/span/text()[4]').extract()[0].split(u"：")[1]
            company = div.select('div[2]/label/text()').extract()[0]

            try:
                db.execute("delete from 163baoxian where id = " + uid)
            except:
                return
            sql = u"insert into 163baoxian(id, url, name, interest, summary, start_amount, limit_interest, period, company, update_time) values('"+uid+"','"+link+"','"+name+"','"+interest+"','"+summary+"','"+start_amount+"','"+limit_interest+"','"+period+"','"+company+"','"+str(datetime.datetime.now())+"')"
            print sql.encode('utf-8')
            try:
                db.execute(sql.replace('%','%%'))
            except:
                print "database insert error"

            yield Request(link, callback = self.parse_detail)

    def parse_detail(self, response):
        global db
        hxs = HtmlXPathSelector(response)
        imgs = hxs.select('//*[@class="detail_wrap pb20 t_c"]/img/@src').extract()
        if 0 == len(imgs):
            imgs = hxs.select('//*[@class="detail_wrap pb20 t_c"]/p/img/@src').extract()
        pic_urls = ""
        i = 1
        for link in imgs:
            if(len(imgs) == i):
                pic_urls = pic_urls + link
            else:
                pic_urls = pic_urls + link + "|"
                i += 1
        update_sql = u"update 163baoxian set pic_urls = '" + pic_urls + "' where id = '" + response.url.split('/')[-1].split('.')[0] + "'"
        print update_sql
        try:
            db.execute(update_sql.replace('%','%%'))
        except:
            print "database update error"

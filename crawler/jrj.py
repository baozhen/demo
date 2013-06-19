#!/usr/bin/env python
# coding=utf-8
#金融界爬虫

import urlparse
import urllib
from datetime import *
from BeautifulSoup import BeautifulSoup
import re
import json
import log
import sys 
import time
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.database
import tornado.httpserver
import tornado.autoreload

reload(sys)
sys.setdefaultencoding( "utf-8" )

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")


def data_insert(product,licailist):
    #用于记录日志
    global db
    insert = 0#插入标志，为1才插入
    startdate = product.get('sell_Org_Date')
    enddate = product.get('sell_End_Date')
    currency = product.get('entr_Curncy_Name')
    productdays = product.get('days')
    if productdays == '':
        productdays =0
    rate = product.get('prd_Max_Yld_De')
    name = product.get('prd_Sname')
    BankName = product.get('bank_Name')
    money = product.get('entr_Min_Curncy')
    if money =='':
        money = 0
    endday = product.get('end_Date')
    id1 = str(product.get('inner_Code'))
    url ='http://bankpro.jrj.com.cn/product/'+str(product.get('inner_Code'))+'/'
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)
    increasemoney = re.findall('<td class="txr">委托递增金额（元）.*?</td>\s+<td class="cur">(\d+).*?</td>',str(soup))
    try:
        start= re.findall('<td class="cur">收益起始日期</td><td>(.*?)</td>',str(soup))[0]
    except:
        start = ''
    try:
        atype= re.findall('<td class="cur">收益类型</td><td>(.*?)</td>',str(soup))[0]
    except:
        atype = ''
    try:
        amoney = re.findall('<td class="cur">起购金额递增单位</td><td>(.*?)</td>',str(soup))[0]
    except:
        amoney = 0
    try:
        area = re.findall('<td class="cur">销售地区</td><td colspan="5"><span.*?>(.*?)</span></td>',str(soup))[0]
    except:
        area = ''
    #工商银行人民币2012-12-122013-06-252012-12-062012-12-1150000
    #key = BankName+currency+start[:10]+endday+startdate+enddate+money
    key = BankName+currency+startdate+enddate+str(int(money))+str(int(productdays))
    if key not in licailist:
        print "not in"
        insert = 1
    else:
        print key,"already in!"
    try:
        sql= "insert into sohulist(ID,ProductName,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,PayDuration,Return_Rate,Start_Money,Type,Product_EndDate,create_time,Increasing_Unit,Area,source) values('"+id1+"','"+name+"','"+BankName+"','"+currency+"',"+productdays+",'"+start+"','"+startdate+"','"+enddate+"','"+productdays+"',"+rate+","+money+",'"+atype+"','"+endday+"','"+str(datetime.now())[:19]+"','"+amoney+"','"+area+"','jrj')"
    except:
        sql =''
    print 'sql=',sql
    try:
        if insert == 1:
            testlog = log.getLogging('jrj')
            db.execute(sql)
            print "insert ok!"
            testlog.critical(str(datetime.now())[:19]+'\tjrj\t'+key+'\n' )
    except:
        print "insert error"
        pass
        #截止日期为空的，暂时搞不定 print "error sql: ",sql.encode('cp936')

def main():
    html = urllib.urlopen("http://bankpro.jrj.com.cn/json/f.jspa?size=500&pn=1&t={%22xszt%22:%220%22,%22st%22:%220%22,%22xsdq%22:%22-1,-1%22,%22sort%22:%22sell_org_date%22,%22order%22:%22desc%22,%22wd%22:%22%22}").read()
    run(html)
    time.sleep(1)
    html = urllib.urlopen("http://bankpro.jrj.com.cn/json/f.jspa?size=500&pn=1&t={%22xszt%22:%221%22,%22st%22:%220%22,%22xsdq%22:%22-1,-1%22,%22sort%22:%22sell_org_date%22,%22order%22:%22desc%22,%22wd%22:%22%22}").read()
    run(html)
    time.sleep(1)

def run(html):
    global db
    #如果id是新的，则插入
    sql = u'select ID,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,Duration,Product_EndDate,Start_Money,Return_Rate from sohulist ;'
    idlist = []
    licailist = []
    for id1 in db.query(sql):
        idlist.append(id1.ID)
        tmplist = []
        tmpstr = ''
        tmpstr = tmpstr+id1.BankName
        tmpstr = tmpstr+id1.Currency
        #tmpstr = tmpstr+id1.Product_StartDate
        #tmpstr = tmpstr+id1.Product_EndDate
        tmpstr = tmpstr+id1.Sell_StartDate[:10]
        tmpstr = tmpstr+id1.Sell_EndDate[:10]
        tmpstr = tmpstr+str(int(id1.Start_Money))
        tmpstr = tmpstr+str(int(id1.Duration))
        idlist.append(id1.values())
        licailist.append(tmpstr)

    jrjsql = 'select ID from jrjlist;'
    jrjIDs = []

    for jrj in db.query(jrjsql):
        jrjIDs.append(jrj.ID)
    dic =json.loads(html.replace('var bps=','')) 
    products = dic.get('bankProductList')
    for a in products:
        id1 = str(a.get('inner_Code'))
        if id1 in jrjIDs:
            print id1,"already crawlered"
            continue
        if id1 in idlist:
            print id1+' is already in it'
            continue
        print u"insert into jrjlist(ID) values('"+id1+"');"
        db.execute(u"insert into jrjlist(ID) values('"+id1+"');")
        data_insert(a,licailist)
    #'''

if __name__ == "__main__":
    testlog = log.getLogging('jrj')
    testlog.critical(str(datetime.now())[:19]+'\tjrj\tstarted\n' )
    print str(datetime.now())[:19]+'\tjrj\tstarted\n' 
    main()


#!/usr/bin/env python
# coding=utf-8

from BeautifulSoup import BeautifulSoup
import urlparse
import urllib
import urllib2
import cookielib
from datetime import *
import re
import sys
import time
import log
import HTMLParser
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.database
import tornado.httpserver
import tornado.autoreload
reload(sys)
sys.setdefaultencoding( "utf-8" )

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")
#
def main():
    global db
    #currencyList = ["CNY","USD","HKD","EUR","JPY","KRW","GBP","AUD","TWD","AED","ALL","ANG","ARS","AWG","BBD","BDT","BGN","BHD","BIF","BMD","BND","BOB","BRL","BSD","BTN","BWP","BYR","BZD","CAD","CHF","CLP","COP","CRC","CSD","CUP","CVE","CYP","CZK","DEM","DJF","DKK","DOP","DZD","ECS","EEK","EGP","ERN","ETB","FJD","FKP","FRF","GHC","GIP","GMD","GNF","GTQ","GYD","HNL","HRK","HTG","HUF","IDR","ILS","INR","IQD","IRR","ISK","ITL","JMD","JOD","KES","KHR","KMF","KPW","KWD","KYD","KZT","LAK","LBP","LKR","LRD","LSL","LTL","LVL","LYD","MAD","MDL","MGF","MKD","MMK","MNT","MOP","MRO","MTL","MUR","MVR","MWK","MXN","MYR","MZM","NAD","NGN","NIO","NOK","NPR","NZD","OMR","PAB","PEN","PGK","PHP","PKR","PLN","PYG","QAR","ROL","RON","RUB","RWF","SAR","SBD","SCR","SDD","SDP","SEK","SGD","SHP","SIT","SKK","SLL","SOS","SRG","STD","SVC","SYP","SZL","THB","TND","TOP","TRY","TTD","TZS","UAH","UGS","UYU","VEB","VND","VUV","WST","XAF","XCD","XOF","XPF","YER","ZAR","ZMK","ZWD","ZWN","XAL","XCP","XAU","XPD","XPT","XAG"]
    currencyList = ["CNY","USD","HKD","EUR","JPY","KRW","GBP","AUD","TWD"]
    for i in range(0,len(currencyList)):
        for j in range(0,len(currencyList)):
            if i == j:
                continue
            try:
                get_html(currencyList[i],currencyList[j])
            except:
                pass
    
def get_html(fromCurrency,toCurrency):
    global db

    url = "http://huilv.911cha.com"
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31')]
    urllib2.install_opener(opener)
    req = urllib2.Request("http://huilv.911cha.com",urllib.urlencode({"from":fromCurrency,"to":toCurrency,"num":"100"}))
    req.add_header("Referer","http://huilv.911cha.com")
    resp = urllib2.urlopen(req)

    html =  resp.read()
 
    table_list  = re.findall('<table .*?>(.*?)</table>',html,re.S)[3]        
    tr_list  = re.findall('<tr>(.*?)</tr>',table_list,re.S)        
    fromCurrencyName = re.findall('<th .*?>(.*?)</th>',tr_list[0],re.S)[0] 
    huilv = re.findall('<td>(.*?)<a',tr_list[1],re.S)[0]
    toCurrencyName = re.findall('<th.*?>(.*?)</th>',tr_list[2],re.S)[0]
    money = re.findall('<td>(.*?)</td>',tr_list[2],re.S)[0]
    buy = re.findall('<td>(.*?)</td>',tr_list[3],re.S)[0] 
    sale = re.findall('<td>(.*?)</td>',tr_list[4],re.S)[0] 
    sale = sale.replace('\r','').replace('\n','')
    updateTime = re.findall('<td>(.*?)</td>',tr_list[5],re.S)[0] 
    source = u"huilv.911cha"
    insertTime = str(datetime.now())[:19] 
    sql = "select * from huilv where fromCurrency = '" + fromCurrency + "' and toCurrency = '"+ toCurrency +"';"
    logs = db.query(sql)
    if len(logs) == 0:
        sql = "insert into huilv (fromCurrency,toCurrency,fromCurrencyName,huilv,toCurrencyName,money,cash_buy,cash_sale,updateTime,insertTime,source) values ('"+fromCurrency+"','"+toCurrency+"','"+fromCurrencyName+"','"+huilv+"','"+toCurrencyName+"','"+money+"','"+buy+"','"+sale+"','"+updateTime+"','"+insertTime+"','"+source+"');"
    else:
        sql = "update `huilv` set fromCurrency = '"+fromCurrency+"', toCurrency = '"+toCurrency+"',fromCurrencyName = '"+fromCurrencyName+"',huilv = "+huilv+", toCurrencyName = '"+toCurrencyName+"', money = '"+money+"',cash_buy = '"+buy+"', cash_sale = '"+sale+"',updateTime = '"+updateTime+"', insertTime = '"+insertTime+"',source = '"+source+"');"
  
    try:
        db.execute(sql)
    except e:
        #print "error:",e
        pass
    else:
        #print "succeed"
        pass
    time.sleep(1)
   


if __name__ == "__main__":
    main()

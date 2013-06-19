# -*- coding: utf-8 -*-
import urllib     
import re
import time
import  sys,  httplib
import os
from datetime import datetime,timedelta

def yyw():
    params  = "broadcast=N&username=861519010154125&title=111&message=333&uri=222&action=send"
    print params
    headers  =  {
            "Accept":  "image/gif,  */*",
            "Connection":  "Keep-Alive",
            "host":  "106.187.89.55:7070",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:20.0) Gecko/20100101 Firefox/20.0",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Cookie":"JSESSIONID=i7jmlcfb5lm56ofqg1cukydo",
            "Accept-Encoding":"gzip, deflate",
            "Referer":"http://106.187.89.55:7070/notification.do",
            "Cache-Control":  ""
    }
    con2  =  httplib.HTTPConnection("www.licairili.com:7070")
    con2.request("POST",  "/notification.do",  params,  headers)
    r2  =  con2.getresponse()
    print r2.status
    if  r2.status  ==  200:
            print  "Success",  "\n"
            html = r2.read()
            #print html
            con2.close()
    else:
            print  "Failed",  "\n"
            con2.close()
    print "离开 悠悠商旅网"

if __name__ == '__main__':
    yyw()

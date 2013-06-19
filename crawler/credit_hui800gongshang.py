#!/usr/bin/env python
# coding=utf-8

from BeautifulSoup import BeautifulSoup
import urlparse
import urllib
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
bankname = ''
citylist = []
cityname = ''
#

def main():
    global bankname
    global citylist 
    global cityname 
    logs = open("creditecard.log",'a')
    logs.write(str(datetime.now())[:19]+" start \n")
    logs.close()
    getCity()
    print len(citylist)

    for i in range(0,len(citylist)):
        citynameStr = citylist[i][1]
        cityname = citylist[i][0]
        #if cityname in ( '北京','东莞','佛山','大连','成都','重庆','长春','长沙','福州','广州','哈尔滨','杭州','合肥','济南','昆明','兰州','南昌','南京','宁波','青岛'):
         #   print '跳过',cityname
          #  continue
        print citylist[i][0]
        banklist = getMaxpage(citynameStr)

        for j in range(0,len(banklist)):
            time.sleep(2)
            bankname = str(banklist[j][0])
            urlstr = str(banklist[j][1])
            maxpage = int(banklist[j][2])+1

            #if citynameStr=='guangzhou':
             #   if urlstr in ('jiaotongyinhang','zhongxinyinhang'):
              #      print '跳过',citynameStr
               #     continue
            for k in range(1,maxpage):
                time.sleep(2)
                if citynameStr=='guangzhou':
                    if urlstr in ('minshengyinhang'):
                        if k<8:
                            print u'跳过mingshengyinhang page=',k
                            continue

                url='http://www.hui800.com/'+citynameStr+'/bank/'+urlstr+'?page='+str(k)
                print url
                getActivity(url)


def getCity():
    global citylist 
    url='http://www.hui800.com/cities'
    html = urllib.urlopen(url).read().decode('utf-8')
    hlist = re.findall('<div class="area" id="contentB">(.*?)</div>',html,re.S)
    alist = re.findall('<span>(.*?)</span>',hlist[0],re.S)

    for a in alist:
        templist=[] 
        cityName = re.findall('<a href.*?>(.*?)</a>',a,re.S)[0]
        nameStr = re.findall('<a href="/(.*?)"',a,re.S)[0]
        templist.append(cityName)
        templist.append(nameStr)
        citylist.append(templist)
        #print 'cityName = ',cityName,'   nameStr=',nameStr
def getMaxpage(citynameStr):
    #工商银行单独写一个爬虫，因为地址太长，需要单独处理
    banklist=[
            ['工商银行','gongshangyinhang']
            ]
            
    print len(banklist)
    for i in range(0,len(banklist)):
        print banklist[i][0]
        url='http://www.hui800.com/'+citynameStr+'/bank/'+str(banklist[i][1])
        html = urllib.urlopen(url).read().decode('utf-8')
        
        try:
            hlist = re.findall('<div class="pagination">(.*?)</div>',html,re.S)
            plist = re.findall('<a href.*?>(.*?)</a>',hlist[0],re.S)[-2]
            banklist[i].append(str(plist))
            
        except:
            banklist[i].append('1')
        print banklist[i][0],'Maxpage=',banklist[i][2]
    return banklist


def getActivity(url):        
    global cityname 

    #html = urllib.urlopen(url).read().replace('%','').decode('cp936')
    html = urllib.urlopen(url).read().decode('utf-8')

    hlist = re.findall('<div class="right">(.*?)<span class="page current">',html,re.S)
    try:
        plist = re.findall('<div class=.*?>(.*?)</div>',hlist[0],re.S)
    except:
        print 'error'
        return
    print 'len pilst=',len(plist)
    for p in plist:
        activityname = re.findall('<a hre.*?>(.*?)</a>',p,re.S)[0][9:-7]
        date = re.findall('<p class="mid">(.*?)</p>',p,re.S)[0].replace('有效期：','').replace('&nbsp;','')[7:-5]
        
        startdate = ''
        enddate = ''
        if '-' in date:
            index=date.index('-')
            startdate=date[0:index]
            enddate=date[index+1:]
        else:
            startdate=u'即日起'
            enddate=date
        
        detailurl = 'http://www.hui800.com' + re.findall('<a href="(.*?)" target="',p,re.S)[0]
        address = geturl(detailurl)
        if len(address)==0:
            continue
        create_time=str(datetime.now())[:19]

        sql = u"insert into creditcard (BankName,ActivityName,StartDate,EndDate,Address,Source,Area,Create_time) values('"+bankname+"','"+activityname+"','"+startdate+"','"+enddate+"','"+address+"','惠800' ,'"+cityname+"','"+create_time+"');" 
        print sql
        try:
            db.execute(sql)
        except:
            print "error sql: "
            pass

def geturl(detailurl):
    try:
        #html = urllib.urlopen(detailurl).read().decode('utf-8')
        html = urllib.urlopen(detailurl).read()
        hlist = re.findall('<div class="mauto rowG".*?>(.*?)</div>',html,re.S)
        url = re.findall('<a href="/(.*?)"',hlist[0],re.S)[0]
        durl = u'http://www.hui800.com/' + url
        dhtml = urllib.urlopen(durl).read()

        dlist = re.findall('<body.*?>(.*?)</body>',dhtml,re.S)[0]
        address = re.findall('<a href="(.*?)"',dlist,re.S)[1]
        address = address.replace('http://www.icbc.com.cn/ICBC/','') 
        address = address.replace('http://www.icbc.com.cn/icbc/','') 

        address = urllib.unquote(address)
        address = address.replace('%2F','/')
        #print 'address changed=',name.encode('utf-8')
        '''
        print 'len of name=',len(name)
        index = name.index('?')
        print 'index=',index
        temp = name[index-1:]
        name = name[0:index-1]
        url ={} 
        url['a'] = name
        url = urllib.urlencode(url)
        #url= urllib.unquote(name)
        url = url [2:]
        url = url.replace('%2F','/')
        url = 'http://www.icbc.com.cn/icbc/' + url +temp
        print 'url=',url
        '''
    except:
        address=''

    return address






if __name__ == "__main__":
    testlog = log.getLogging('qq')
    testlog.critical(str(datetime.now())[:19]+'\tqq\tstarted\n' )
    main()

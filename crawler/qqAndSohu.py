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

#

def main():
    logs = open("crawler.log",'a')
    logs.write(str(datetime.now())[:19]+" start \n")
    logs.close()
    for i in range(1,6):
        print i
        url = 'http://stock.finance.qq.com/money/view/show.php?t=bank&c=cpdq_search_products&status%5B%5D=1&orderBy=0&desc=desc&p='+str(i)+'&name=&max_ratio_min=-1&max_ratio_max=-1&object%5B%5D='
        print url
        html = urllib.urlopen(url).read().replace('%','').decode('cp936')
        #print html
        hlist = re.findall("<tr.*?>(.*?)</tr>",html,re.S)
        #hlist  = re.findall('<tr.*>\s+<td><input.*?/></td>\s<td><a title=.*?href="javascript:parent.showProductDetail(\'(.*?)\',true);"><script>.*?</script></a></td>',html,re.S)
        #print hlist
        for h in hlist[1:]:
            n = re.findall('<td>(.*?)</td>',h)
            productid = re.findall('parent.onClickCompa.*?this,\'(.*?)\',',n[0])[0]
            detailURL='http://stock.finance.qq.com/money/view/show.php?t=bank&c=show_detail&id='+productid
            productname = re.findall('<a title="(.*?.)" href=',n[1])[0]
            #print productname
            html_parser = HTMLParser.HTMLParser()
            productname = html_parser.unescape(productname)
            #print productname
            n=n[2:]
            #print n;       
            dhtml = urllib.urlopen(detailURL).read().replace('%','').decode('cp936')
            soup = BeautifulSoup(dhtml)
            #print soup
            run(dhtml,n,productid,productname)
        #time.sleep(2)

def run(html,blist,productid,productname):
    global db
    logs = open("crawler.log",'a')
    bankdic = {
            u'上海浦东发展银行':u'浦发银行',                 
            u'中国光大银行':u'光大银行',          
            u'中国农业银行':u'农业银行',        
            u'中国工商银行':u'工商银行',        
            u'中国建设银行':u'建设银行',        
            u'中国民生银行':u'民生银行',          
            u'中国邮政储蓄银行':u'邮政储蓄银行',      
            u'中国银行':u'中国银行',            
            u'交通银行':u'交通银行',            
            u'兴业银行':u'兴业银行',              
            u'北京银行':u'北京银行',              
            u'华夏银行':u'华夏银行',              
            u'平安银行':u'平安银行',              
            u'广发银行':u'广发银行',              
            u'招商银行':u'招商银行',
            u'上海银行':u'上海银行',   
            u'中信银行':u'中信银行', 
            }
    banklist=['中国银行','建设银行','农业银行','工商银行','交通银行','招商银行','民生银行','平安银行','浦发银行','广发银行','光大银行','华夏银行','中信银行','北京银行','上海银行','兴业银行','深发展银行','邮政储蓄银行'] 
    bankname=blist[0].replace(u'股份有限公司','')
    #print productid,blist
    sell_startDate = blist[1]
    sell_endDate = blist[2][:10]
    sell_endDate = sell_endDate.replace(' ','')
    #print len(sell_endDate),'qq'
    product_endDate=blist[3]
    currency=blist[4]
    start_money=blist[7]
    print 'start_money= ',start_money
    if (start_money=='0') or (start_money==''):
        print 'money error!!!'
        return
    return_rate=blist[8]
    return_type=blist[10]
    hlist = re.findall("<li>(.*?)</li>",html,re.S)
    product_startDate=hlist[4].replace(u'收益起计：','')
    area=re.findall('<a title="(.*?)" class=',hlist[6])[0]
    
    product_type=hlist[8].replace(u'对象：','')
    duration=hlist[12].replace(u'付息周期：','')
    duration=duration.replace(u'天','')
    duration=duration.replace(u'日','')
    
    if u"月" in duration:
        d = int(re.findall('\d+',duration)[0])*30
        duration=str(d)
    elif u"年" in duration:
        d = int(re.findall('\d+',duration)[0])*360
        duration=str(d)
    if len(duration)==0:
        duration=str(0)

    #复制出来的 licailis
    sql = u'select ID,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,Duration,Product_EndDate,Start_Money,Return_Rate from sohulist ;'
    licailist = []
    for id1 in db.query(sql):
        tmplist = []
        tmpstr = ''
        tmpstr = tmpstr+id1.BankName
        tmpstr = tmpstr+id1.Currency
        #tmpstr = tmpstr+id1.Product_StartDate
        #tmpstr = tmpstr+id1.Product_EndDate
        tmpstr = tmpstr+id1.Sell_StartDate.replace(' ','')
        tmpstr = tmpstr+id1.Sell_EndDate.replace(' ','')
        tmpstr = tmpstr+str(int(id1.Start_Money))
        tmpstr = tmpstr+str(int(id1.Duration))
        licailist.append(tmpstr)

    #if bankname in bankdic:
    if len(bankname)>0:
        if bankname in bankdic:
            bankname=bankdic.get(bankname)
    
        sell_endDate = sell_endDate[:10]
        sell_endDate = sell_endDate.replace(' ','')
        key = bankname+currency+sell_startDate+sell_endDate+str(int(start_money))+str(int(duration))
        print 'key =',key
        #这里开始判断
        #======================
        #======================
        #print '啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊'
        sql1 = u'select ID from qqlist;'
        idlist = []
        for id1 in db.query(sql1):
            idlist.append(id1.ID)
        if productid in idlist:
            print 'qqlist已经存在'
            return 0
        else:
            sql = u"insert into qqlist(ID,ProductName,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,PayDuration,Return_Rate,Type,Start_Money,Area,Product_EndDate,Product_Type) values ('"+productid+"','"+productname+"','"+bankname+"','"+currency+"',"+duration+",'"+product_startDate+"','"+sell_startDate+"','"+sell_endDate+"','"+duration+"','"+return_rate+"','"+return_type+"',"+start_money+",'"+area+"','"+product_endDate+"','"+product_type+"');"
            #print sql    
            try:
                pass
                db.execute(sql)
                print 'qqlist不存在，插入qqlist'
            except:
                print "error sql@@@@@@@: "
        #sqlsohulist= u"select  * from sohulist WHERE BankName='"+bankname+"' and Start_Money="+start_money+" and  Sell_StartDate = '"+sell_startDate+"' and Sell_EndDate  = '"+sell_endDate+"'and Product_StartDate='"+product_startDate+"' and Product_EndDate='"+product_endDate+"';"
        if key not in licailist:
            sqlsohu = u"insert into sohulist(ID,ProductName,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,PayDuration,Return_Rate,Type,Start_Money,Area,Product_EndDate,Product_Type,create_time,source) values('"+productid+"','"+productname+"','"+bankname+"','"+currency+"',"+duration+",'"+product_startDate+"','"+sell_startDate+"','"+sell_endDate+"','"+duration+"','"+return_rate+"','"+return_type+"',"+start_money+",'"+area+"','"+product_endDate+"','"+product_type+"','"+str(datetime.now())[:19]+"','qq');"
            #print 'sqlsohu',sqlsohu
            sql2 = u'select ID from sohulist;'
            idlist2 = []
            for id2 in db.query(sql2):
                idlist2.append(id2.ID)
            if productid not in idlist2:
                try:
                    print 'sohu里没有'
                    db.execute(sqlsohu)
                    testlog = log.getLogging('qq')
                    testlog.critical(str(datetime.now())[:19]+'\tqq\t'+productname+'\n' )
                except:
                    print "error sql: "
            else:
                print 'sohulist idlist里已经有了'
        else:
            print 'sohu里已经有了'
    

if __name__ == "__main__":
    testlog = log.getLogging('qq')
    testlog.critical(str(datetime.now())[:19]+'\tqq\tstarted\n' )
    print str(datetime.now())[:19]+'\tsohu\tstarted\n' 
    main()

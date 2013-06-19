#!usr/bin/env python
# coding=utf-8


import urlparse
import urllib
from datetime import *
from BeautifulSoup import BeautifulSoup
import re
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

#

def main():
    global db
    logs = open("crawler.log",'a')
    logs.write(str(datetime.now())[:19]+" sohu start \n")
    logs.close()
    banklist=['中国银行','建设银行','农业银行','工商银行','交通银行','招商银行','民生银行','平安银行（原）','浦发银行','广发银行','光大银行','华夏银行','中信银行','北京银行','上海银行','兴业银行','中国邮政储蓄银行'] 
    sql = u'select ID,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,Product_EndDate,Start_Money,Return_Rate from sohulist ;'
    idlist = []
    licailist = []
    for id1 in db.query(sql):
        idlist.append(id1.ID)
        tmplist = []
        tmpstr1 = ''
        tmpstr1 = tmpstr1+id1.BankName
        tmpstr1 = tmpstr1+id1.Currency
        #tmpstr = tmpstr+id1.Product_StartDate
        #tmpstr = tmpstr+id1.Product_EndDate
        tmpstr1 = tmpstr1+id1.Sell_StartDate[:10]
        tmpstr1 = tmpstr1+id1.Sell_EndDate[:10]
        tmpstr1 = tmpstr1+str(int(id1.Start_Money))
        tmpstr1 = tmpstr1+str(int(id1.Duration))
        idlist.append(id1.values())
        licailist.append(tmpstr1)
    for i in range(1,10):
        print i
        url = 'http://db.money.sohu.com/bank/bksearch.html?yh=1&bkstatus=1&pageNO='+str(i)
        #url = 'http://db.money.sohu.com/bank/bksearch.html?yh=1&org=%B9%E3%B7%A2%D2%F8%D0%D0'
        print url
        if  i ==1:
            html = urllib.urlopen(url).read().replace('%','').decode('cp936')+ urllib.urlopen('http://db.money.sohu.com/bank/bksearch.html?yh=1&bkstatus=2').read().replace('%','').decode('cp936')
        else:
            html = urllib.urlopen(url).read().replace('%','').decode('cp936')
        hlist  = re.findall('<tr>\s+<td><a href="(.*?)" target="_blank" title=.*?>.*?</a></td>\s+<td>(.*?)</td>',html)
        sql = u'select ID from sohulist;'
        idlist = []
        insert = 1
        for id2 in db.query(sql):
            idlist.append(id2.ID)
        for h in hlist:
            #if h[1] not in banklist:
             #   print h[1],"not in banklist"
              #  continue
            #print h[1],'in banklist'
            productid = h[0].replace('.html','').split('/')[-1]
            if productid in idlist:
                print "already in",productid
                #continue
            print h[1]
            run(h[0],licailist)
        time.sleep(2)

def run(url,licailist):
    print "len of list is ",len(licailist)
    global db
    logs = open("crawler.log",'a')
    bankdic = {
            u'中国邮政储蓄银行':u'邮政储蓄银行',
            u'平安银行（原）':u'平安银行',
            }
    html = urllib.urlopen("http://db.money.sohu.com"+url).read().replace('%','').decode('cp936').replace(u'平安银行（原）','平安银行').replace(u'中国邮政储蓄银行','邮政储蓄银行')
    product_id = re.findall("view/\d+/(\d+).html",url)[0]
    print product_id,
    soup = BeautifulSoup(html)
    strs = str(soup.table).replace('\t','').replace('\r\n','').replace(' ','').replace('</p>','').replace('<p>','')
    hlist = re.findall("<td.*?>(.*?)</td>\s+<td.*?>(.*?)</td>",strs,re.S)
    #print hlist
    p = []
    sql = u'select ID from sohulist;'
    idlist = []
    idlist.append('00051509')
    insert = 1
    for id2 in db.query(sql):
        idlist.append(id2.ID)
    if product_id in idlist:
        insert = 0
        print "already in"
        
    p.append(product_id)
    for h in hlist:
        p.append(h[1])
        #sql = u"insert into qqlist(Id,Name,BankName,StartDate,EndDate,Currency,Duration,Return_Rate,StartMoney,Type) values ('"+id1+"','"+name+"','"+bankname+"','"+startdate+"','"+enddate+"','"+currency+"',"+duration+",'"+returnrate+"%%',"+startmoney+",'"+type1+"');"
    t = hlist[4][1]
    start =  datetime(int(t[:4]),int(t[5:7]),int(t[8:10]))
    duration = int(re.findall('\d+',hlist[3][1])[0])
    if p[2] in ['上海银行','农业银行','中国银行','招商银行','浦发银行','广发银行','光大银行','北京银行','建设银行','兴业银行','平安银行','交通银行','华夏银行','中信银行','江苏银行','包商银行','杭州银行','湖北银行','富滇银行','恒丰银行','青岛银行','兰州银行']:
        endday = str(start+ timedelta(duration))[:10]
    else:
        endday = str(start+ timedelta(duration-1))[:10]
        print start,str(duration),endday
    p.append(endday)
    tmpstr=u''
    
    for m in p[:4]:
        tmpstr = tmpstr+"'"+m+"',"
    temp=p[4]
    if '天' in temp:
        temp=int(filter(str.isdigit,temp))
    if '月' in p[4]:
        temp=int(filter(str.isdigit,temp))*30 
    if '年' in p[4]:
        temp=int(filter(str.isdigit,temp))*365
    duration=str(temp)
    tmpstr = tmpstr+duration+","
    #['2012-12-18', '2012-12-11', '2012-12-17', '93\xe5\xa4\xa9', '4.7', '\xe4\xbf\xa1\xe6\x89\x98\xe7\xb1\xbb']
    for m in p[5:8]:
        tmpstr = tmpstr+"'"+m+"',"
    tmpstr = tmpstr+"'"+duration+"',"
    
    tmpstr = tmpstr+""+p[9]+","
    tmpstr = tmpstr+"'"+p[10]+"',"
    if '万元' in p[11]:
        tmpstr = tmpstr+""+p[11].replace('万元','0000')+","
        moneynu= p[11].replace('万元','0000')
        if len(moneynu)> len('9999999'):
            return
    else:
        moneynu = re.findall('\d+',p[11])[0]
        if len(moneynu)> len('9999999'):
            return
        tmpstr = tmpstr+""+moneynu+","
    #工商银行人民币2012-12-122013-06-252012-12-062012-12-1150000
    #工商银行人民币2012-12-072013-04-232012-12-042012-12-061000000
    #key = p[2]+p[3]+p[5]+endday+p[6]+p[7]+moneynu
    key = p[2]+p[3]+p[6][:10]+p[7][:10]+str(int(moneynu))+str(int(duration))
    print "key",key
    if key in licailist:
        insert = 0
        print "already in"

    for m in p[12:]:
        tmpstr = tmpstr+"'"+m+"',"
    print type(tmpstr)
    sql = u"insert into sohulist values("+tmpstr[:-1].replace('\n','').replace('%','%%')+",'"+str(datetime.now())[:19]+"','sohu')"
    if insert ==1:
        print sql.encode('utf-8')
        try:
            testlog = log.getLogging('sohu')
            db.execute(sql)
            testlog.critical(str(datetime.now())[:19]+'\tsohu\t'+key+'\n' )
        except:
            print "error"
        

if __name__ == "__main__":
    testlog = log.getLogging('sohu')
    testlog.critical(str(datetime.now())[:19]+'\tsohu\tstarted\n' )
    print str(datetime.now())[:19]+'\tsohu\tstarted\n' 
    main()

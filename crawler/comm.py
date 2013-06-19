#!/usr/bin/env python
# coding=utf-8


import urlparse
import urllib
import re
import time
import sys 
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.database
import tornado.httpserver
import tornado.autoreload
from datetime import *
from BeautifulSoup import BeautifulSoup
reload(sys)
sys.setdefaultencoding( "utf-8" )

db = tornado.database.Connection("localhost:3306", "money","root","mnldfgrxr1Q")


def comm():
    global db
    print "commbank"
    sql = u'select ID,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,Product_EndDate,Start_Money,Return_Rate from sohulist ;'
    idlist = []
    licailist = []
    for id1 in db.query(sql):
        idlist.append(id1.ID)
        tmplist = []
        tmpstr = ''
        tmpstr = tmpstr+id1.BankName
        tmpstr = tmpstr+id1.Currency
        tmpstr = tmpstr+id1.Product_StartDate
        tmpstr = tmpstr+id1.Product_EndDate
        tmpstr = tmpstr+id1.Sell_StartDate
        tmpstr = tmpstr+id1.Sell_EndDate
        tmpstr = tmpstr+str(int(id1.Start_Money))
        idlist.append(id1.values())
        licailist.append(tmpstr)
    html = str(BeautifulSoup(urllib.urlopen('http://www.bankcomm.com/BankCommSite/cn/lcpd/include/products.jsp?param=%0F%0Fall%0Fbuy%0Fcode:%0FproName:').read()))
    hlist = re.findall('<tr.*?">(.*?)</tr>',html.replace("澳大利亚元","澳元"),re.S)
    for h in hlist[1:]:
        #<a href="/BankCommSite/cn/lcpd/wmbook.jsp?wmbook=2102120245" target="_blank">交银添利56天</a>
        #name = re.findall('<a href="javascript:void(0);" onclick="validate()" class="fh">点击查询</a>',h,re.S)
        if '封闭式' not in h:
            continue
        id = re.findall('wmbook.jsp\?wmbook=(\d+)"',h,re.S)[0]
        if len(id)>2:
            if id in idlist:
                print id,"already in"
                continue
        else:
            continue
        name = re.findall(' target="_blank">(.*?)</a>',h.replace('\t',''),re.S)[0]
        pname = name.replace(' ','').replace('\t','')
        b = re.findall('<td.*?>(.*?)</td>',h)
        #封闭式 2R 人民币 50,000.00 56天 4.00% 2012/11/28 2012/12/04 2012-12-05
        currency = b[2]
        money = b[3][:-3].replace(',',u'')
        duration = b[4].replace('天','')
        rate = str(float(b[5].split('-')[0].replace('%','')))
        print "rate",rate
        sell_startdate = b[6].replace('/','-')
        sell_enddate = b[7].replace('/','-')
        startdate = b[8]
        t = startdate
        start =  datetime(int(t[:4]),int(t[5:7]),int(t[8:10]))
        endday = str(start+ timedelta(int(duration)))[:10]
        key = '交通银行'+currency+str(start)[:10]+endday+sell_startdate+sell_enddate+money
        if key not in licailist:
            print 'not in'
            insert = 1
        else:
            print key,"already in !!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            insert = 0
        sql = u"insert into sohulist(ID,ProductName,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,PayDuration,Return_Rate,Type,Start_Money,Area,Product_EndDate,create_time,source) values ('"+id+"','"+pname+"','交通银行','"+currency+"',"+duration+",'"+startdate+"','"+sell_startdate+"','"+sell_enddate+" ','"+duration+"','"+rate+"','',"+money+",'','"+endday+"','"+str(datetime.now())[:19]+"','comm');"
        print sql
        try:    
            pass
            if insert == 1:
                pass
                db.execute(sql)
        except:
        #截止日期为空的，暂时搞不定
            print "error sql: ",sql.encode('cp936')



    

def hxb():
    for i in range(1,2):
        print i
        url = 'http://www.hxb.com.cn/chinese/personal/index1.jsp?cid2=24&cid3=12761537033940333'
        html = BeautifulSoup(urllib.urlopen(url).read())
        print html
    

'''
def  cmbstr(string):
    a=re.findall('<span.*?>\s*(.*?)<',string,re.S)
    print 'aaaa'
    print a
    returnstr=''
    for str in a:
        print str
        returnstr=returnstr+str
        return returnstr
'''

def  cmbstr(string):
    reh=re.compile('</?\w+[^>]*>')
    s=reh.sub('',string)
    return s

def cmb():
    url = 'http://www.cmbchina.com/cfweb/svrajax/product.ashx?op=search&type=s&pageindex=1&pagesize=100&salestatus=A&baoben=&currency=&term=&keyword=&series=01&risk=&city=&date=&orderby=begindate%20desc&t=0.27203526763814967'
    html = BeautifulSoup(urllib.urlopen(url).read())
    #print html
    idlist=re.findall('PrdCode:"(.*?)",PrdName',str(html))
    print len(idlist)
    for id in idlist:
        url='http://www.cmbchina.com/cfweb/personal/productdetail.aspx?code='+id
        print url
        detailhtml = str(BeautifulSoup(urllib.urlopen(url).read()))
        #print detailhtml    
        table=re.findall('<table.*?>\s*(.*?)</table>',detailhtml,re.S)[2]
        print table
        Currency=re.findall('<tr.*?>\s+<td.*?>理财币种.*?</td>.*?FONT-SIZE: 9pt">(.*?)</tr>',table,re.S)[0]
        Currency=cmbstr(Currency)
        print '币种',Currency
        pid=id
        print 'pid',pid
        pname=re.findall('<tr.*?>\s+<td.*?>名称.*?</td>.*?FONT-SIZE: 9pt">(.*?)</tr>',table,re.S)[0]
        print 'pname',pname
        ProductName=cmbstr(pname)
        print '产品名字',ProductName
        print '币种',Currency
        day=re.findall('<tr.*?>\s+<td.*?>理财期限.*?</td>.*?FONT-SIZE: 9pt">(.*?)</tr>',table,re.S)[0] 
        day=cmbstr(day)
        dayn=re.findall('\d\d*',day)
        if '日' in day or '天' in day:
            Duration=dayn[0]
        else:
            if '年' in day:
                if '一年' in day:
                    Duration='365'
                if '半年' in day:
                    Duration='182'
            if '月' in day:
                Duration=str(int(dayn[0])*30)
            else:
                Duration=dayn[0]
        print '周期',Duration
        print '产品类型'
        Product_Type=d[6]
        print Product_Type
        print '收益起计日'
        Product_StartDate=d[12].replace('年','-').replace('月','-').replace('日','')
        print Product_StartDate
        print '发售地区'
        Area=d[10]
        print Area
        date=d[7].split('-')
        Sell_StartDate=date[0].replace('年','-').replace('月','-').replace('日','')
        Sell_EndDate=date[1].replace('年','-').replace('月','-').replace('日','')
        print '销售起始日期'
        print '销售截止日期'
        print Sell_StartDate
        print Sell_EndDate
        print '收益率'
        Return_Rate=0.0
        print Return_Rate          
        


def ccb():
    for i in range(1,2):
        print i
        url = 'http://finance.ccb.com/Channel/3080?_tp_c5='+str(i)
        html = str(BeautifulSoup(urllib.urlopen(url).read())).replace('&nbsp;','')
        #<tr onmouseover="this.className='table_select_bg'" onmouseout="this.className=''">
        hlist = re.findall('<tr onmouseover="this.className=.*?>(.*?)</tr>',html,re.S)
        for h in hlist:
            blist= re.findall('<td.*?>(.*?)</td>',h)
            #<a href="/Info/53647880" class="blue4" target="_blank">利得盈2012年第142期人民币债券型保本理财</a>
            url,name= re.findall('<a href="(.*?)" class="blue4" target="_blank">(.*?)</a>',h)[0]
            print url,name
            for b in blist[1:]:
                print b

    

def ceb():
    for i in range(1,3):
        print i
        url = 'http://www.cebbank.com/jsp/include/newsun/product_n.jsp?_tp_p11='+str(i)+'&number=1&title=%E5%9C%A8%E5%94%AE%E7%90%86%E8%B4%A2%E4%BA%A7%E5%93%81'
        html = str(BeautifulSoup(urllib.urlopen(url).read()))
        #print html
        hlist= re.findall('<tr align="center">(.*?)</tr>',html,re.S)
        for h in hlist:
            print "-----------------------------------------------------------------------"
            pid = re.findall('<a href="(.*?)"',h)[0]
            print "pid=",pid
            url = 'http://www.cebbank.com/'+pid
            dhtml = urllib.urlopen(url).read()[1:-1].replace("%","") 
            #print "aaaaa",('*')*20
            tablelist = re.findall('<table.*?>(.*?)</table>',dhtml,re.S)[2]
            d=re.findall('<td.*?>(.*?)</td>',tablelist,re.S)
            pid=pid[6:]
            print "id=",pid
            #print 'len(D)=',len(d)
            pname=d[0]
            #print "name=",productname
            Sale_State=d[4]
            #print "state=",Sale_State
            Sell_StartDate=d[6]
            print "startDate=",Sell_StartDate
            Product_StartDate=d[8]
            print "StartDate",Product_StartDate
            Sell_EndDate=d[10]
            print "EndDate",Sell_EndDate
            Product_EndDate=d[12]
            print "Product ENd",Product_EndDate
            Currency=d[14]
            #print "Curry",Currency
            #Duration=d[18].replace('日','').replace('天','')
            day=d[18]
            dayn=re.findall('\d\d*',day)
            if '日' in day or '天' in day:
                Duration=dayn[0]
            else:
                if '年' in day:
                    if '一年' in day:
                        Duration='365'
                        print "一年"
                    if '半年' in day:
                        Duration='182'
                else:
                    if '月' in day:
                        Duration=str(int(dayn[0])*30)
                        print 'duration type =',type(Duration)
                        print day,"月"
                        print 'duration=',Duration
            Start_Money=str(float(d[22].replace(',','')))
            print 'money=',Start_Money
            Increasing_Unit=str(float(d[26].replace(',','')))
            print 'Increasing_Unit=',Increasing_Unit
            Type=d[30]
            print'Type=',Type
            PayDuration=str(d[32])
            print 'PayDuration',PayDuration
            Return_Rate=str(d[34])
            print 'Return_Rate',Return_Rate
            if '-' in Return_Rate:
                if '--' in Return_Rate:
                    pass
                else:
                    index=Return_Rate.find('-')
                    Return_Rate=Return_Rate[0:index]
                    print '@@@@@'
                    print Return_Rate
            Create_time=str(datetime.now())[:19]
            BankName=u'光大银行'            
            sqlsohulist= u"select  * from sohulist WHERE BankName='"+BankName+"' and Start_Money="+Start_Money+" and  Sell_StartDate = '"+Sell_StartDate+"' and Sell_EndDate= '"+Sell_EndDate+"' and Product_StartDate='"+Product_StartDate+"' and Product_EndDate='"+Product_EndDate+"';"
            sohuiterms=db.query(sqlsohulist)
            if len(sohuiterms)==0:
                print 'soho不存在，将要插入'
                sql1 = u'select * from sohulist;'     
                idlist = []
                for id2 in db.query(sql1):
                    idlist.append(id2.ID)
                if pid in idlist:
                    print pid+' is already in sohulist'
                else:
                    sql = u"insert into sohulist(ID,ProductName,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,PayDuration,Return_Rate,Type,Start_Money,Product_EndDate,create_time,source) values ('"+pid+"','"+pname+"','光大银行','"+Currency+"',"+Duration+",'"+Product_StartDate+"','"+Sell_StartDate+"','"+Sell_EndDate+" ','"+PayDuration+"','"+Return_Rate+"','"+Type+"',"+Start_Money+",'"+Product_EndDate+"','"+str(datetime.now())[:19]+"','ceb');"
                    print 'sql=',sql
                    try:
                        db.execute(sql)
                        pass
                    except:
                        print "error sql: ",sql.encode('cp936')
            else:
                print pid+' is already in sohulist'

def spdb():
        url='http://ebank.spdb.com.cn/net/finnaceMoreInfo.do?_viewReferer=finance%2FmoreInfo&_PagableInfor.PageSize=11&num=11&FinanceType=[Ljava.lang.String%3B%40a18540&ftype=0&ispage=1&_PagableInfor.PageNo=1' 
        html = str(BeautifulSoup(urllib.urlopen(url).read()))
        print html
        pages = re.findall('<a href="(finnaceMoreInfo.*?)">',html,re.S)
        for page in pages:
            print page

        tables= re.findall('<a href.*?>(.*?)</a>',html,re.S)
        print '表内容'
        for t in tables:
            print t
        hlist= re.findall('<tr>(.*?)</tr>',table,re.S)
        print '行内容'
        print hlist[0],'0'
        print hlist[1],'1'
        return 0
        for h in hlist[1:]:
            print "-----------------------------------------------------------------------"
            purl = re.findall('<a href="(.*?)" .*?>',h)
            if len(purl)==0:
                print '没详情数据了'
                break         
            publicnow = re.findall('<td.*?>\s+即将发行\s+</td>',h)
            if len(publicnow)==0:
                publicnow = re.findall('<div.*?>\s*正在发行\s*</div>',h)
                if len(publicnow)==0:
                    print '没有发行的产品了'
                    break
            pid=purl[0]
            print "pid=",pid
            url = 'http://ebank.spdb.com.cn'+pid
            #dhtml = urllib.urlopen(url).read().decode('cp936') 
            dhtml = str(BeautifulSoup(urllib.urlopen(url).read()))
            print url
            #print dhtml
            d=re.findall('<td.*?width="456">\s*<p.*?>(.*?)</p></td>',dhtml,re.S)
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            for i in range(0,len(d)):
                print str(i).decode('UTF-8').encode('GBK')
                print d[i].decode('UTF-8').encode('GBK')
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            pid=pid[22:32]
            print pid
            print 'dddd'
            print '产品名字'
            ProductName=d[0]
            print ProductName
            print '币种'
            Currency=d[5]
            print Currency
            print '周期'
            day=d[4]
            dayn=re.findall('\d\d*',day)
            if '日' in day or '天' in day:
                Duration=dayn[0]
            else:
                if '年' in day:
                    if '一年' in day:
                        Duration='365'
                    if '半年' in day:
                        Duration='182'
                else:
                    if '月' in day:
                        Duration=str(int(dayn[0])*30)
            print Duration
            print '产品类型'
            Product_Type=d[6]
            print Product_Type
            print '收益起计日'
            Product_StartDate=d[12].replace('年','-').replace('月','-').replace('日','')
            print Product_StartDate
            print '发售地区'
            Area=d[10]
            print Area
            date=d[7].split('-')
            Sell_StartDate=date[0].replace('年','-').replace('月','-').replace('日','')
            Sell_EndDate=date[1].replace('年','-').replace('月','-').replace('日','')
            print '销售起始日期'
            print '销售截止日期'
            print Sell_StartDate
            print Sell_EndDate
            print '收益率'
            Return_Rate=0.0
            print Return_Rate          
            try:
                Start_Money,Increasing_Unit=re.findall('(.*?)元，以(.*?)元整数倍递增',d[20])[0]
                Start_Money=str(float(Start_Money.replace(u'万','0000')))
                Increasing_Unit=str(float(Increasing_Unit.replace(u'万','0000').replace(u'千','000')))                                    
            except:
                Start_Money=re.findall('仅限(.*?)元',d[20])[0]
                Start_Money=str(float(Start_Money.replace(u'万','0000')))
                Increasing_Unit=''
            print '起始金额'
            print Start_Money
            print '递增单位'
            print  Increasing_Unit
            print '收益率说明'
            Profit_Direction=d[19]
            print Profit_Direction
            print '产品说明'
            Product_Direction=d[11]
            print Product_Direction
            print '产品管理费'
            Management_Fee=d[18]
            print Management_Fee
            print '产品结束日'
            Product_EndDate=d[13]
            Product_EndDate=Product_EndDate.replace('年','-').replace('月','-').replace('日','')
            print Product_EndDate
            Create_time=str(datetime.now())[:19]
            BankName=u'浦发银行'
            sqlsohulist= u"select  * from sohulist WHERE BankName='"+BankName+"' and Start_Money="+Start_Money+" and  Sell_StartDate = '"+Sell_StartDate+"' and Sell_EndDate= '"+Sell_EndDate+"' and Product_StartDate='"+Product_StartDate+"' and Product_EndDate='"+Product_EndDate+"';"
            print sqlsohulist
            sohuiterms=db.query(sqlsohulist)
            if len(sohuiterms)==0:
                print 'soho不存在，将要插入'
                sql1 = u'select * from sohulist;'     
                idlist = []
                for id2 in db.query(sql1):
                    idlist.append(id2.ID)
                if pid in idlist:
                    print pid+' is already in sohulist'
                else:
                    sql = u"insert into sohulist(ID,ProductName,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,Return_Rate,Type,Start_Money,Increasing_Unit,Product_EndDate,Profit_Direction,Product_Direction,Management_Fee,create_time,source) values ('"+pid+"','"+ProductName+"','浦发银行','"+Currency+"',"+Duration+",'"+Product_StartDate+"','"+Sell_StartDate+"','"+Sell_EndDate+"',"+str(Return_Rate)+",'"+Product_Type+"',"+Start_Money+",'"+Increasing_Unit+"','"+Product_EndDate+"','"+Profit_Direction+"','"+Product_Direction+"','"+Management_Fee+"','"+str(datetime.now())[:19]+"','spdb');"
                    print 'sql=',sql
                    tmp = sql.replace(u'%',u'%%')
                    print tmp
                    db.execute(tmp)
                    print '插入成功'
                    try:
                        #db.execute(sql)
                        pass
                    except:
                        print "error sql: ",sql.encode('cp936')
            else:
                print pid+' is already in sohulist'


                
                
def spdb2():
        url='http://ebank.spdb.com.cn/net/financeInner.do?ftype=0-2-3-1' 
        html = str(BeautifulSoup(urllib.urlopen(url).read()))
        table= re.findall('<table id="FinanceTypeCss2"(.*?)</table>',html,re.S)[0]
        #print '表内容'
        #print table
        hlist= re.findall('<tr>(.*?)</tr>',table,re.S)
        #print '行内容'
        #print hlist[0]
        print hlist[1]
        for h in hlist[1:]:
            print "-----------------------------------------------------------------------"
            purl = re.findall('<a href="(.*?)" .*?>',h)
            if len(purl)==0:
                print '没详情数据了'
                break         
            publicnow = re.findall('<td.*?>\s+即将发行\s+</td>',h)
            if len(publicnow)==0:
                publicnow = re.findall('<div.*?>\s*正在发行\s*</div>',h)
                if len(publicnow)==0:
                    print '没有发行的产品了'
                    break
            pid=purl[0]
            print "pid=",pid
            url = 'http://ebank.spdb.com.cn'+pid
            #dhtml = urllib.urlopen(url).read().decode('cp936') 
            dhtml = str(BeautifulSoup(urllib.urlopen(url).read()))
            print url
            #print dhtml
            d=re.findall('<td.*?width="510">\s*<p.*?>(.*?)</p></td>',dhtml,re.S)
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            for i in range(0,len(d)):
                print str(i)
                print d[i]
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            pid=pid[22:32]
            print pid
            print '产品名字'
            ProductName=d[0].split('</a>')[-1]
            print ProductName
            print '币种'
            #Currency=re.findall('<a.*?></a>.*?',d[5])[0]
            Currency=d[5].split('>')[-1]
            print Currency
            print '周期'
            day=d[4].split('>')[-1]
            dayn=re.findall('\d\d*',day)
            if '日' in day or '天' in day:
                Duration=dayn[0]
            else:
                if '年' in day:
                    if '一年' in day:
                        Duration='365'
                    if '半年' in day:
                        Duration='182'
                else:
                    if '月' in day:
                        Duration=str(int(dayn[0])*30)
            print Duration
            print '产品类型'
            Product_Type=d[6]
            print Product_Type
            print '收益起计日'
            Product_StartDate=d[12].split('>')[-1].replace('年','-').replace('月','-').replace('日','')
            print Product_StartDate
            print '发售地区'
            Area=d[10]
            print Area
            date=d[7].split('-')          
            Sell_StartDate=date[0].split('</a>')[-1].replace('年','-').replace('月','-').replace('日','')
            Sell_EndDate=date[1].split('</a>')[-1].replace('年','-').replace('月','-').replace('日','')
            print '销售起始日期'
            print '销售截止日期'
            print Sell_StartDate
            print Sell_EndDate
            Return_Rate=d[16].split('>')[-1].replace('%','')
            if '-' in Return_Rate:
                if '--' in Return_Rate:
                    pass
                else:
                    index=Return_Rate.find('-')
                    Return_Rate=float(Return_Rate[0:index])
                    print '@@@@@'
                    print Return_Rate
            print '收益率'
            Return_Rate=float(Return_Rate)
            print Return_Rate          
            money=d[17].replace(',','',1)
            money=money.split('，')
            for a in money:
                print a
            Start_Money=re.findall('(.*?)元起',money[0].split('</a>')[-1])[0]
            Increasing_Unit=re.findall('(.*?)元整数倍递增',money[1].split('</a>')[-1])[0]
            #Increasing_Unit=str(float(Increasing_Unit.replace(u'万','0000').replace(u'千','000')))                                    
            #except:
                #Start_Money=re.findall('仅限(.*?)元',d[17])[0]
                #Start_Money=str(float(Start_Money.replace(u'万','0000')))
                #Increasing_Unit=''
            print '起始金额'
            print Start_Money
            print '递增单位'
            print  Increasing_Unit
            print '收益率说明'
            Profit_Direction=d[20].split('>')[-1]
            print Profit_Direction
            print '产品管理费'
            Management_Fee=d[15].split('>')[-1]
            print Management_Fee
            print '产品结束日'
            Product_EndDate=d[13].split('>')[-1]
            Product_EndDate=Product_EndDate.replace('年','-').replace('月','-').replace('日','')
            print Product_EndDate
            Create_time=str(datetime.now())[:19]
            BankName=u'浦发银行'
            sqlsohulist= u"select  * from sohulist WHERE BankName='"+BankName+"' and Start_Money="+Start_Money+" and  Sell_StartDate = '"+Sell_StartDate+"' and Sell_EndDate= '"+Sell_EndDate+"' and Product_StartDate='"+Product_StartDate+"' and Product_EndDate='"+Product_EndDate+"';"
            print sqlsohulist
            sqlsohulist=sqlsohulist.replace('%','%%')
            sohuiterms=db.query(sqlsohulist)
            print sohuiterms
            if len(sohuiterms)==0:
                print 'soho不存在，将要插入'
                sql1 = u'select * from sohulist;'     
                idlist = []
                for id2 in db.query(sql1):
                    idlist.append(id2.ID)
                if pid in idlist:
                    print pid+' is already in sohulist'
                else:
                    sql = u"insert into sohulist(ID,ProductName,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,Return_Rate,Type,Start_Money,Increasing_Unit,Product_EndDate,Profit_Direction,Management_Fee,create_time,source) values ('"+pid+"','"+ProductName+"','浦发银行','"+Currency+"',"+Duration+",'"+Product_StartDate+"','"+Sell_StartDate+"','"+Sell_EndDate+"',"+Return_Rate+",'"+Product_Type+"',"+Start_Money+",'"+Increasing_Unit+"','"+Product_EndDate+"','"+Profit_Direction+"','"+Management_Fee+"','"+str(datetime.now())[:19]+"','spdb');"
                    print 'sql=',sql
                    tmp = sql.replace(u'%',u'%%')
                    print tmp
                    db.execute(tmp)
                    print '插入成功'
                    try:
                        #db.execute(sql)
                        pass
                    except:
                        print "error sql: ",sql.encode('cp936')
            else:
                print pid+' is already in sohulist'


def  date(string):
    tmpstr=string.split('-')
    print tmpstr
    if len(tmpstr[1])==1:
        tmpstr[1]='0'+tmpstr[1]
    if len(tmpstr[2])==1:
        tmpstr[2]='0'+tmpstr[2]
    returnstr=tmpstr[0]+'-'+tmpstr[1]+'-'+tmpstr[2]
    return returnstr


                
                
def cib():
        url='http://www.cib.com.cn/netbank/cn/Financing_Release/sale/mb22.html' 
        html = str(BeautifulSoup(urllib.urlopen(url).read()))
        table= re.findall('<table id="finTable"(.*?)</table>',html,re.S)[0]
        #print '表内容',table
        hlist= re.findall('<tr>(.*?)</tr>',table,re.S)
        #print '行内容'
        #print hlist[0]
        urllist=[]
        for h in hlist:
            print "-----------------------------------------------------------------------"
            d=re.findall('<td.*?>\s*(.*?)</td>',h,re.S)
            print '币种',d[3]
            currency=d[3]
            purl = re.findall('<a href="(.*?)".*?>',h)
            pid=purl[0]
            print "pid=",pid
            if 'www.cib.com.cn' in pid:
                url=pid
            else:
                url = 'http://www.cib.com.cn'+pid
            if url not in urllist:
                dhtml = str(BeautifulSoup(urllib.urlopen(url).read()))
                urllist.append(url)
                #print url
                #print dhtml
                prolist= re.findall('<tr>(.*?)</tr>',dhtml,re.S)
                #print prolist[0]
                #print prolist[1]
                for pro in prolist[1:]:
                    d=re.findall('<td.*?>\s*(.*?)</td>',pro,re.S)
                    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
                    for i in range(0,len(d)):
                        print str(i)
                        print d[i]
                    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
                    pid=d[1]
                    print 'pid=',pid
                    ProductName=d[0]
                    print ProductName
                    Currency=currency
                    print '币种',Currency
                    print '周期'
                    day=d[8]
                    Duration=d[8]
                    dayn=re.findall('\d\d*',day)
                    if '日' in day or '天' in day:
                        Duration=dayn[0]
                    else:
                        if '年' in day:
                            if '一年' in day:
                                Duration='365'
                            if '半年' in day:
                                Duration='182'
                        else:
                            if '月' in day:
                                Duration=str(int(dayn[0])*30)
                    print Duration
                    Product_Type=d[9]
                    print '产品类型',Product_Type
                    print '收益起计日'
                    Product_StartDate=date(d[5].strip())
                    print Product_StartDate
                    print '发售地区'
                    Area=d[4]
                    print Area
                    Sell_StartDate=date(d[2].strip())
                    Sell_EndDate=date(d[3].strip())
                    print'销售起始日期' ,Sell_StartDate
                    print'销售截止日期', Sell_EndDate 
                    print '产品结束日'
                    Product_EndDate=date(d[6].strip())
                    print Product_EndDate
                    print Currency,'美元',Currency.strip()=="美元"
                    if Currency.strip()=='美元':
                        Return_Rate=float(d[12].split('，')[0].replace('%',''))
                        print'收益率',Return_Rate
                        Start_Money,Increasing_Unit=re.findall('(\d+).*?(\d+)',d[11].replace(',','').replace('，',''))[0]
                        print '起始金额',Start_Money
                        print '递增单位',Increasing_Unit
                        print '产品管理费'
                        Management_Fee=d[13].split(',')[0].replace('%','')
                        print Management_Fee
                    else:
                        Return_Rate=float(d[11].split('，')[0].replace('%',''))
                        print '收益率',Return_Rate          
                        Start_Money=d[10].split('，')[0].replace('万','0000')
                        print d[10].split('，')[1]
                        Increasing_Unit=re.findall('\d+',d[10].split('，')[1])[0]
                        print '起始金额',Start_Money
                        print '递增单位',Increasing_Unit
                        print '产品管理费'
                        Management_Fee=d[12].split(',')[0].replace('%','')
                        print Management_Fee
                    Create_time=str(datetime.now())[:19]
                    BankName=u'兴业银行'
                    sqlsohulist= u"select  * from sohulist WHERE BankName='"+BankName+"' and Start_Money="+Start_Money+" and  Sell_StartDate = '"+Sell_StartDate+"' and Sell_EndDate= '"+Sell_EndDate+"' and Product_StartDate='"+Product_StartDate+"' and Product_EndDate='"+Product_EndDate+"';"
                    print sqlsohulist
                    sqlsohulist=sqlsohulist.replace('%','%%')
                    sohuiterms=db.query(sqlsohulist)
                    #print sohuiterms
                    if len(sohuiterms)==0:
                        print 'soho不存在，将要插入'
                        sql1 = u'select * from sohulist;'     
                        idlist = []
                        for id2 in db.query(sql1):
                            idlist.append(id2.ID)
                        if pid in idlist:
                            print pid+' is already in sohulist'
                        else:
                            sql = u"insert into sohulist(ID,ProductName,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,Return_Rate,Type,Start_Money,Increasing_Unit,Product_EndDate,Management_Fee,create_time,source) values ('"+pid+"','"+ProductName+"','兴业银行','"+Currency+"',"+Duration+",'"+Product_StartDate+"','"+Sell_StartDate+"','"+Sell_EndDate+"',"+Return_Rate+",'"+Product_Type+"',"+Start_Money+",'"+Increasing_Unit+"','"+Product_EndDate+"','"+Management_Fee+"','"+str(datetime.now())[:19]+"','cib');"
                            print 'sql=',sql
                            tmp = sql.replace(u'%',u'%%')
                            #print tmp
                            db.execute(tmp)
                            print '插入成功'
                            try:
                                #db.execute(sql)
                                pass
                            except:
                                print "error sql: ",sql.encode('cp936')
                    else:
                        print pid+' is already in sohulist'



def pingan():
    for i in range(1,3):
        print i
        url='http://bank.pingan.com/cms-tmplt/licai.do?page='+str(i)+'&pageCount=38&sellState=1&qixiang=1&fengxiandengji=1&nianhuashouyi=1&pxValue=0' 
        html = str(BeautifulSoup(urllib.urlopen(url).read()))
        #print html
        table= re.findall('<table(.*?)</table>',html,re.S)[0]
        #print '表内容',table
        hlist= re.findall('<tr>(.*?)</tr>',table,re.S)
        #print '行内容'
        #print hlist[0]
        #print hlist[1]
        for h in hlist[1:]:
            print "-----------------------------------------------------------------------"
            purl = re.findall('<a.*?href="(.*?)" .*?>',h)
            pid=purl[0]
            print "pid=",pid
            url = 'http://bank.pingan.com'+pid
            #dhtml = urllib.urlopen(url).read().decode('cp936') 
            dhtml = str(BeautifulSoup(urllib.urlopen(url).read()))
            print url
            #print dhtml
            d=re.findall('<td.*?>\s*(.*?)</td>',dhtml,re.S)
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            #for i in range(0,len(d)):
                #print str(i)
                #print d[i]
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            pid=pid[14:27]
            print "pid=",pid
            ProductName=d[0]
            print'产品名字', ProductName
            print '币种'
            Currency=d[8]
            print Currency
            Duration=d[5]
            day=d[5]
            dayn=re.findall('\d\d*',day)
            if '日' in day or '天' in day:
                Duration=dayn[0]
            else:
                if '年' in day:
                    if '一年' in day:
                        Duration='365'
                    if '半年' in day:
                        Duration='182'
                else:
                    if '月' in day:
                        Duration=str(int(dayn[0])*30)
            print  '周期',Duration
            #print '产品类型'
            #Product_Type=d[6]
            #print Product_Type
            Product_StartDate=d[6]
            print '收益起计日',Product_StartDate
            Product_EndDate=d[7]
            print '产品结束日',Product_EndDate
            Area=d[3]
            print '发行地区',Area
            date=d[4].split('——')
            print date[0]
            Sell_StartDate=date[0][0:10]
            Sell_EndDate=date[1][0:10]
            print '销售起始日期'
            print '销售截止日期'
            print Sell_StartDate
            print Sell_EndDate
            Return_Rate=d[10].split('%')[0]
            print '收益率',Return_Rate
            Start_Money=re.findall('\d+',d[9])
            print Start_Money
            Start_Money=re.findall('\d+',d[9])[0]
            Start_Money=Start_Money+'0000'
            print '起始金额',Start_Money
            Increasing_Unit=re.findall('\d+',d[9])[-1]
            print '递增单位',Increasing_Unit
            Create_time=str(datetime.now())[:19]
            BankName=u'平安银行'
            sqlsohulist= u"select  * from sohulist WHERE BankName='"+BankName+"' and Start_Money="+Start_Money+" and  Sell_StartDate = '"+Sell_StartDate+"' and Sell_EndDate= '"+Sell_EndDate+"' and Product_StartDate='"+Product_StartDate+"' and Product_EndDate='"+Product_EndDate+"';"
            #print sqlsohulist
            sohuiterms=db.query(sqlsohulist)
            if len(sohuiterms)==0:
                print 'soho不存在，将要插入'
                sql1 = u'select * from sohulist;'     
                idlist = []
                for id2 in db.query(sql1):
                    idlist.append(id2.ID)
                if pid in idlist:
                    print pid+' is already in sohulist'
                else:
                    sql = u"insert into sohulist(ID,ProductName,BankName,Currency,Duration,Product_StartDate,Sell_StartDate,Sell_EndDate,Return_Rate,Start_Money,Increasing_Unit,Product_EndDate,create_time,source) values ('"+pid+"','"+ProductName+"','"+BankName+"','"+Currency+"',"+Duration+",'"+Product_StartDate+"','"+Sell_StartDate+"','"+Sell_EndDate+"',"+Return_Rate+","+Start_Money+",'"+Increasing_Unit+"','"+Product_EndDate+"','"+str(datetime.now())[:19]+"','pingan');"
                    print 'sql=',sql
                    tmp = sql.replace(u'%',u'%%')
                    print tmp
                    db.execute(tmp)
                    print '插入成功'
                    try:
                        #db.execute(sql)
                        pass
                    except:
                        print "error sql: ",sql.encode('cp936')
            else:
                print pid+' is already in sohulist'


                
                
                
if __name__ == "__main__":
   #ceb()
   #spdb()
   #ccb()
   #cmb()
   comm()
   cib()
   #pingan()

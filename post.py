#!/usr/bin/python
#coding=utf-8

import urllib
import urllib2

def post(url, data):
    req = urllib2.Request(url)
    data = urllib.urlencode(data)
    #enable cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)
    return response.read()

def main():
    posturl = "https://api.weibo.com/oauth2/access_token"
    code = u'fbbac9097fbd4888260e8b6e1e1d7140'
    print code
    #data = {'code': u'7f657543b50a41d161fecd7cb9351542', 'client_id': u'1873335772', 'client_secret': u'3967c07ea03b1f5587c4550e5d0d3e36', 'grant_type': u'authorization_code', 'redirect_uri': u'http://www.cunzhe.com/register/college'}
    data = {'code': code, 'client_id': u'1873335772', 'client_secret': u'3967c07ea03b1f5587c4550e5d0d3e36', 'grant_type': u'authorization_code', 'redirect_uri': u'http://www.cunzhe.com/register/college'}
    print data
    print post(posturl, data)

if __name__ == '__main__':
    main()

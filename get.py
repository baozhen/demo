import urllib2
import urllib
import json

data = {}
data['uid'] = '2283732215'
data['access_token'] = '2.00ZE_YUCGN1mCC20f49afc37SEW_EB'

url_values = urllib.urlencode(data)
print url_values

url = 'https://api.weibo.com/2/users/show.json'
full_url = url + '?' + url_values

response = urllib2.urlopen(full_url)
print response
print type(response)

user_info = json.loads(response.read())
print type(user_info)
print user_info['idstr']
print user_info['name']

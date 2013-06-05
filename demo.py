#-*-coding:utf-8-*-
from autocomplete import Autocomplete
import os
import json

testfile = os.path.abspath('licai.json')
a = Autocomplete(filename=testfile,)
a.rebuild_index()
results = a.search_query(u'宝')
a = u'宝'
print a, type(a)
print results
#json_data = json.JSONEncoder().encode(results)
#print json_data, type(json_data)

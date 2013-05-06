#-*-coding:utf-8-*-
from autocomplete import Autocomplete
import os

testfile = os.path.abspath('dailyRedemptionType.json')
mapping={'id':'Id','term':'Product'}
a = Autocomplete(filename=testfile,mapping=mapping)
a.rebuild_index()
results = a.search_query(u'宝')

print results

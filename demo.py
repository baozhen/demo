#-*-coding:utf-8-*-
from autocomplete import Autocomplete
import os

testfile = os.path.abspath('licai.json')
a = Autocomplete(filename=testfile,)
a.rebuild_index()
results = a.search_query(u'宝')

print results

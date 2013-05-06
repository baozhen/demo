#coding=utf-8
import MySQLdb
import json
import itertools

conn = MySQLdb.connect(host="localhost", user="root", passwd="mnldfgrxr1Q", db="money", charset="utf8")

cursor = conn.cursor()
cursor.execute("select Id, Product from dailyRedemptionType")
column_names = [d[0] for d in cursor.description]
list = [dict(itertools.izip(column_names,row)) for row in cursor]

json_str = json.dumps(list, encoding="UTF-8", ensure_ascii=False)

print json_str, type(json_str)

f = open('dailyRedemptionType.json', 'w')
f.write(json_str.encode('utf8'))
f.close()

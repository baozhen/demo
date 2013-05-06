import time, MySQLdb

conn = MySQLdb.connect(host='localhost', user='root', passwd='mnldfgrxr1Q', db='money', charset="utf8")

cursor = conn.cursor()

n = cursor.execute("select Id, Product from dailyRedemptionType")
for row in cursor.fetchall():
    for r in row:
        print r

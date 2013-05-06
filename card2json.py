import time, MySQLdb

conn = MySQLdb.connect(host='localhost', user='root', passwd='mnldfgrxr1Q', db='money', charset="utf8")

cursor = conn.cursor()

f = open('card.json', 'w')
n = cursor.execute("select id, name from college")
for row in cursor.fetchall():
    f.write(u'{"score":"9","id":"')
    f.write(str(row[0]))
    f.write(u'","term":"')
    f.write(row[1].encode('utf8'))
    f.write(u'"}\n')

f.close()

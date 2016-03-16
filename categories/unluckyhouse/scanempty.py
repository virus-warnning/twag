#!../../../bin/python
# -.- encoding: utf-8 -.-

import httplib
import re
import sqlite3
from xml.etree.ElementTree import ElementTree

def dict_factory(cursor, row):  
    d = {}  
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d 

# 取得未處理的編號
# unluckyhouse.state=0

con = sqlite3.connect('unluckyhouse.sqlite')
con.row_factory = dict_factory

todolist = []
sql = 'SELECT id FROM unluckyhouse WHERE state=0 ORDER BY id DESC LIMIT 256'

cur = con.cursor()
cur.execute(sql)

for row in cur:
	todolist.append(row['id'])

cur.close()

print('TODO: %d ~ %d' % (todolist[0], todolist[-1]))

# 確認是不是有效文章 (長度>0)
# http://unluckyhouse.com/archive/index.php/t-%d.html
latest_id = -1
host = 'unluckyhouse.com'
uri  = '/archive/index.php/t-%d.html'
conn = httplib.HTTPConnection(host)
sql  = 'UPDATE unluckyhouse SET state=-1 WHERE id=?'

for t in todolist:
	try:
		conn.request('GET', uri % t)
		resp = conn.getresponse()
		if resp.status==200:
			clen = len(resp.read(5))
			if clen==0:
				con.execute(sql, (t, ))
				con.commit()
				print('%d is empty page' % t)
		conn.close()
	except:
		pass

con.close()

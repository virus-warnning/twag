#!../../../bin/python
# coding: utf-8

import os
import sys
import json

commons_path = os.path.realpath('../../commons')
sys.path.insert(1, commons_path)

import corp_utils
import smart_dbapi
from print_progress import print_progress

BEGIN = 0
LIMIT = 5000

rank = 0
sql  = 'SELECT id,corp,boss FROM unluckylabor WHERE lat=0 AND lng=0 AND id>=? LIMIT ?'
conn = smart_dbapi.connect('unluckylabor.sqlite')
curr = conn.execute(sql, (BEGIN, LIMIT))

changes = {}
for row in curr:
	rank = rank + 1
	msg = u'定位中 %s (%d/%d) ...' % (row['corp'], rank, LIMIT)
	print_progress(msg)
	sys.stdout.flush()

	info = corp_utils.get_corp_info(row['corp'])
	if info != False:
		changes[row['id']] = info

print('')
print(len(changes))
print('更新資料庫')
for i in changes:
	info = changes[i]
	conn.execute('UPDATE unluckylabor SET lat=?, lng=? WHERE id=?', (info['lat'], info['lng'], i))

print(info)
conn.commit()
conn.close()

print(u'完成')

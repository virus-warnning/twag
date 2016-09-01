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

BEGIN = 1001
LIMIT = 1000

rank = 0
sql  = 'SELECT id,corperation FROM unluckylabor WHERE lat=0 AND lng=0 AND id>=? LIMIT ?'
conn = smart_dbapi.connect('unluckylabor.sqlite')
curr = conn.execute(sql, (BEGIN, LIMIT))

changes = {}
for row in curr:
	rank = rank + 1
	msg = u'定位中 %s (%d/%d) ...' % (row['corperation'], rank, LIMIT)
	print_progress(msg)
	sys.stdout.flush()

	point = corp_utils.get_corp_location(row['corperation'])
	if point != False:
		changes[row['id']] = point

print('')
print('更新資料庫')
for i in changes:
	(lat, lng) = changes[i]
	conn.execute('UPDATE unluckylabor SET lat=?, lng=? WHERE id=?', (lat, lng, i))
conn.commit()

conn.close()

print(u'完成')

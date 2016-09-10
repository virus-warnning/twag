#!../../../bin/python
# coding: utf-8

import os
import sys
import json
import time

commons_path = os.path.realpath('../../commons')
sys.path.insert(1, commons_path)

import corp_utils
import smart_dbapi
from print_progress import print_progress

BEGIN = 891
LIMIT = 10

rank = 0
sql  = 'SELECT id,corp,boss FROM unluckylabor WHERE lat=0 AND lng=0 AND id>=? LIMIT ?'
conn = smart_dbapi.connect('unluckylabor.sqlite')
curr = conn.execute(sql, (BEGIN, LIMIT))

# 蒐集要修改項目
cnt = 0
changes = {}
for row in curr:
	rank = rank + 1
	info = corp_utils.get_corp_info(row['corp'])
	if info != False and info['lat'] != 0:
		changes[row['id']] = info
		cnt = cnt + 1

	msg = u'處理中 #%d %s (%d/%d) 需要更新 %d 項 ...\n' % (row['id'], row['corp'], rank, LIMIT, cnt)
	print_progress(msg)
	sys.stdout.flush()
	time.sleep(0.5)

# 更新
print('\n更新資料庫')
for i in changes:
	info = changes[i]
	conn.execute('UPDATE unluckylabor SET lat=?, lng=? WHERE id=?', (info['lat'], info['lng'], i))

conn.commit()
conn.close()

print(u'完成')

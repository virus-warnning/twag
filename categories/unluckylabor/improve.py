#!../../../bin/python
# coding: utf-8
#
# 資料庫完整性補充程式
# 違反勞基法事業名單沒有地址、經緯度欄位，有些資料沒有雇主欄位，
# 利用 RonnyWang 的查公司 API 以及 TGOS 地址定位補充這些。
#
# @author 小璋丸 <virus.warnning@gmail.com>
#

import os
import sys
import json
import time

commons_path = os.path.realpath('../../commons')
sys.path.insert(1, commons_path)

import corp_utils
import smart_dbapi
from print_progress import print_progress

BEGIN = 899
LIMIT = 1000

rank = 0
sql  = 'SELECT id,corp,boss,gov FROM unluckylabor WHERE lat=0 AND id>=? AND id<=?'
conn = smart_dbapi.connect('unluckylabor.sqlite')
curr = conn.execute(sql, (BEGIN, BEGIN+LIMIT-1))

# 蒐集要修改項目
cnt = 0
changeset = {}
for row in curr:
	info = corp_utils.get_corp_info(row['corp'], row['boss'], row['gov'])
	rank = rank + 1
	if info != False:
		if row['boss'] != '' and info['lat'] != 0:
			changeset[row['id']] = info
			cnt = cnt + 1

	msg = u'處理中 #%d %s (%d/%d) 需要更新 %d 項 ...\n' % (row['id'], row['corp'], rank, LIMIT, cnt)
	print_progress(msg)
	sys.stdout.flush()
	time.sleep(0.5)

# 更新
print('\n更新資料庫')
for id in changeset:
	info = changeset[id]
	sql  = 'UPDATE unluckylabor SET addr=?, lat=?, lng=? WHERE id=?'
	conn.execute(sql, (info['addr'], info['lat'], info['lng'], id))
	sql  = 'UPDATE unluckylabor SET boss=? WHERE id=? AND boss=\'\''
	conn.execute(sql, (info['boss'], id))

conn.commit()
conn.close()

print(u'完成')

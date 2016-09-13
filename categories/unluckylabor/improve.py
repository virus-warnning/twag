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

BEGIN = 112
END   = 112

rank = 0
sql  = 'SELECT id,corp,boss,gov FROM unluckylabor WHERE lat=0 AND id>=? AND id<=?'
conn = smart_dbapi.connect('unluckylabor.sqlite')
rows = conn.execute(sql, (BEGIN, END)).fetchall()

# 蒐集要修改項目
modified = 0
visited  = 0
total    = len(rows)

for row in rows:
	info = corp_utils.get_corp_info(row['corp'], row['boss'], row['gov'])
	if info != False:
		sql  = 'UPDATE unluckylabor SET addr=?, lat=?, lng=? WHERE id=?'
		conn.execute(sql, (info['addr'], info['lat'], info['lng'], row['id']))
		sql  = 'UPDATE unluckylabor SET boss=? WHERE id=? AND boss=\'\''
		conn.execute(sql, (info['boss'], row['id']))
		conn.commit()
		modified = modified + 1

	visited = visited + 1
	msg = '處理中 #%d %s (%d/%d) 已更新 %d 項 ...' % (row['id'], row['corp'], visited, total, modified)
	print_progress(msg)
	sys.stdout.flush()

conn.close()

print(u'完成')

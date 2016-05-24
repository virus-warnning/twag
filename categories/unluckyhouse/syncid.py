#!../../../bin/python
# coding: utf-8

import os
import re
import sys
import httplib
from xml.etree.ElementTree import ElementTree

commons_path = os.path.realpath('../../commons')
sys.path.insert(1, commons_path)

import smart_http
import smart_dbapi

# 取得台灣凶宅網的最新討論串 id
# http://unluckyhouse.com/external.php
# rss > channel > item > link (t=...)
resp = smart_http.request('unluckyhouse.com', '/external.php')
if resp != False:
	latest_url = resp.find('channel/item/link').text
	m = re.match(r".+t=(\d+).+", latest_url)
	latest_id = int(m.group(1))
else:
	latest_id = -1

# SQLite 同步台灣凶宅網的 id，資料採用預設值
if latest_id is not -1:
	con = smart_dbapi.connect('unluckyhouse.sqlite')
	cur = con.execute('SELECT max(id) sync_id FROM unluckyhouse')
	row = cur.fetchone()

	if row['sync_id'] is not None:
		sync_id = row['sync_id']
	else:
		sync_id = 0

	if sync_id<latest_id:
		print('Add entries %d ~ %d' % (sync_id+1,latest_id))
		diff = range(sync_id+1, latest_id+1)
		for i in diff:
			sql = 'INSERT INTO unluckyhouse(id) VALUES (?)'
			con.execute(sql, (i, ))
		con.commit()
	else:
		print('Already synchronized (%d)' % latest_id)

	con.close()

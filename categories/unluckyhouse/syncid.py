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

# 取得台灣凶宅網的最新討論串 id
# http://unluckyhouse.com/external.php
# rss > channel > item > link (t=...)
latest_id = -1
host = 'unluckyhouse.com'
uri  = '/external.php'
conn = httplib.HTTPConnection(host)

try:
	conn.request('GET', uri)
	resp = conn.getresponse()
	if resp.status==200:
		tree = ElementTree()
		tree.parse(resp)
		latest_url = tree.getroot().find('channel/item/link').text
		m = re.match(r".+t=(\d+).+", latest_url)
		latest_id = int(m.group(1))
	conn.close()
except:
	pass

# SQLite 同步台灣凶宅網的 id，資料採用預設值
sync_id = 0
if latest_id is not -1:
	con = sqlite3.connect('unluckyhouse.sqlite')
	con.row_factory = dict_factory
	cur = con.cursor()

	sql = 'SELECT max(id) sync_id FROM unluckyhouse'
	cur.execute(sql)
	row = cur.fetchone()
	row['sync_id']
	if row['sync_id'] is not None:
		sync_id = row['sync_id']

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

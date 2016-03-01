# -.- encoding: utf-8 -.-

# http://unluckyhouse.com/external.php
# rss > channel > item > link (t=...)
 
import httplib
import re
from xml.etree.ElementTree import ElementTree

host = 'unluckyhouse.com'
uri  = '/external.php'
conn = httplib.HTTPConnection(host)
latest_id = -1

# 取得台灣凶宅網的最新討論串 id
try:
	conn.request('GET', uri)
	resp = conn.getresponse()
	if resp.status==200:
		tree = ElementTree()
		tree.parse(resp)
		latest_url = tree.getroot().find('channel/item/link').text
		m = re.match(r".+t=(\d+).+", latest_url)
		latest_id = m.group(1)
	conn.close()
except:
	pass

# SQLite 同步台灣凶宅網的 id，資料採用預設值
if latest_id is not -1:
	print latest_id
	# TODO

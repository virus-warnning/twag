#!../../bin/python
# coding: utf-8

import os
import re
import httplib
import urllib
import smart_http
import smart_geo
import smart_dbapi

DEBUG = True
CODEPATH = os.path.dirname(os.path.abspath(__file__))

## 查詢公司統編
#  - 利用 RonnyWang 的公司名稱查詢
#  - 查詢公司名稱
#  - 取重新導向的 header location
#  - 從 location 取出 id
def get_corp_id(name):
	corp_id = False

	try:
		if type(name) is unicode:
			name = name.encode('utf-8')

		conn  = httplib.HTTPConnection('company.g0v.ronny.tw')
		query = urllib.urlencode({'q': name})
		uri   = '/index/search?%s' % query
		
		conn.request('GET', uri)
		resp  = conn.getresponse()

		if resp.status == 302:
			moveto  = resp.getheader('Location', '')
			match   = re.match('/id/(\d+)', moveto)
			if match != None:
				corp_id = match.group(1)
			else:
				if DEBUG: print('invalid request')
		else:
			if DEBUG: print('Response Code: %d' % resp.status)

		conn.close()
	except Exception as e:
		if DEBUG: print(e)

	return corp_id

# 取得公司資訊
def get_corp_info(name):
	dbfile = '%s/corp_cache.sqlite' % CODEPATH
	conn = smart_dbapi.connect(dbfile)

	sql = 'SELECT name,uid,boss,addr,lat,lng FROM corp_cache WHERE name=?'
	cur = conn.execute(sql, (name,))
	info = cur.fetchone()
	cur.close()

	if info is None:
		uid = get_corp_id(name)
		if uid == False:
			sql = 'INSERT INTO corp_cache(name,mtime) VALUES(?,DATETIME())'
			conn.execute(sql, (name,))
			conn.commit()
			info = False
		else:
			uri  = '/api/show/%s' % uid
			resp = smart_http.request('company.g0v.ronny.tw', uri)
			boss = ''
			addr = ''
			lat  = 0.0
			lng  = 0.0
			loc  = False

			if resp != False:
				if u'公司所在地' in resp['data']:
					addr = resp['data'][u'公司所在地']
					loc  = smart_geo.geocode(addr)

				# e.g. 財團法人中央通訊社
				if u'營業地址' in resp['data'][u'財政部']:
					addr = resp['data'][u'財政部'][u'營業地址']
					loc  = smart_geo.geocode(addr)

				if loc != False:
					(lat, lng) = loc

				if u'代表人姓名' in resp['data']:
					boss = resp['data'][u'代表人姓名']

			sql = 'INSERT INTO corp_cache(name,uid,boss,addr,lat,lng,mtime) VALUES(?,?,?,?,?,?,DATETIME())'
			conn.execute(sql, (name, uid, boss, addr, lat, lng))
			conn.commit()

			info = {
				'name': name,
				'uid':  uid,
				'boss': boss,
				'addr': addr,
				'lat':  lat,
				'lng':  lng
			}

	conn.close()

	return info

## 簡易測試
def main():
	print(get_corp_info(u'廣全科技股份有限公司'))

if __name__ == "__main__":
	main()

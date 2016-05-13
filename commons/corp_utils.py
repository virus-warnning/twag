# coding: utf-8

import json
import re
import httplib
import urllib
import smart_http
import smart_geo

DEBUG = False

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

## 查詢公司位置
#  - 利用 RonnyWang 的公司資料 API
#  - 取出 resp.data.公司所在地 或 resp.data.財政部.營業地址
#  - 利用 Google geocoding 服務轉換成經緯度
def get_corp_location(corp_query):
	if re.match('\d{8}', corp_query) != None:
		corp_id = corp_query
	else:
		corp_id = get_corp_id(corp_query)
		if corp_id == False:
			return False

	uri  = '/api/show/%s' % corp_id
	resp = smart_http.request('company.g0v.ronny.tw', uri)
	if resp != False:
		if u'公司所在地' in resp['data']:
			address = resp['data'][u'公司所在地']
			return smart_geo.geocode(address)

		# e.g. 財團法人中央通訊社
		if u'營業地址' in resp['data'][u'財政部']:
			address = resp['data'][u'財政部'][u'營業地址']
			return smart_geo.geocode(address)

	return False

## 簡易測試
def main():
	print(get_corp_location(u'台灣奧蜜思股份有限公司'))

if __name__ == "__main__":
	main()

#!../../bin/python
# coding: utf-8
#
# @author 小璋丸 <virus.warnning@gmail.com>
#

import geocoder

# 土炮版相依套件
import re
import math
import requests
from simplejson.scanner import JSONDecodeError

TRACE = False

cookies = False
pagekey = False
apikey  = 'USZWSgrBGpevjABqoXT3mLlUnkiR1Ruf8MWixp//eGc='

# 使用 TGOS 定位
def geocode(address):
	return tgos_by_spider(address)

# TGOS 取得圖台狀態
# 取得 pagekey 與 session 值
def tgos_get_state():
	global cookies, pagekey

	if TRACE:
		print('取得圖台狀態')

	# pagekey 取得途徑: window.sircMessage.sircPAGEKEY = '...';
	r = requests.post('http://map.tgos.nat.gov.tw/TGOSCLOUD/Web/Map/TGOSViewer_Map.aspx')
	if r.status_code == 200:
		m = re.search('window\.sircMessage\.sircPAGEKEY\s?=\s?\'([\w\+%]+)\';', r.text)
		if m != None:
			cookies = {}
			pagekey = m.group(1)
			for c in r.cookies:
				cookies[c.name] = c.value
			if TRACE:
				print('pagekey="%s"' % pagekey)
	else:
		if TRACE:
			print('無法取得 pagekey')

# TGOS 瀏覽器操作模擬
def tgos_by_spider(address):
	global cookies, pagekey

	if pagekey == False:
		tgos_get_state()

	if pagekey != False:
		# 取得 TWD 97 (EPSG 3826) 座標
		url = 'http://map.tgos.nat.gov.tw/TGOSCloud/Generic/Project/GHTGOSViewer_Map.ashx'
		params = {
			'pagekey': pagekey,
			'method': 'querymoiaddr',
			'address': address,
			'sid': cookies['ASP.NET_SessionId'],
			'useoddeven': False
		}
		headers = {
			'Origin': 'http://map.tgos.nat.gov.tw',
			'Referer': 'http://map.tgos.nat.gov.tw/TGOSCLOUD/Web/Map/TGOSViewer_Map.aspx',
			'X-Requested-With': 'XMLHttpRequest'
		}
		data = {
			'method': 'querymoiaddr',
			'address': address,
			'sid': cookies['ASP.NET_SessionId'],
			'useoddeven': False
		}
		kwargs = {
			'params':  params,
			'headers': headers,
			'cookies': cookies,
			'data': data
		}
		r = requests.post(url, **kwargs)
		if r.status_code == 200:
			'''
			這裡有可能會爆掉
			The conversion of the nvarchar value '183185187189' overflowed an int column.
			...
			The statement has been terminated.
			'''
			try:
				addinfo = r.json()['AddressList']
				if len(addinfo) > 0:
					# 轉 WGS84 座標 (僅適用台灣本島，其他地方可能誤差稍大)
					y = addinfo[0]['Y'] * 0.00000899823754
					x = 121 + (addinfo[0]['X'] - 250000) * 0.000008983152841195214 / math.cos(math.radians(y))
					return (y, x)
			except JSONDecodeError as e:
				print('無法處理地址定位 %s' % address);

	return False

# TGOS API 方法1
def tgos_by_api1(address):
	global apikey

	url  = 'http://gis.tgos.nat.gov.tw/TGLocator/TGLocator.ashx'
	data = {
		'format': 'json',
		'input': address,
		'srs': 'EPSG:4326',
		'ignoreGeometry': False,
		'pnum': 5,
		'keystr': apikey
	}

	r = requests.post(url, data=data)
	if r.status_code == 200:
		resp = r.json()
		if resp['status'] == 'OK' and resp['featureCount'] > 0:
			loc = resp['results'][0]['geometry']
			return (loc['y'], loc['x'])

	return False

# TGOS API 方法2
def tgos_by_api2(address):
	global apikey

	url = 'http://gis.tgos.nat.gov.tw/TGAddress/TGAddress.aspx'
	params = {
		'oResultDataType': 'json',
		'oAddress': address,
		'oSRS': 'EPSG:4326',
		'keystr': apikey
	}

	r = requests.get(url, params=params)
	# TODO: ...

	return False

# TGOS API 方法3
# http://tgos.nat.gov.tw/TGOS_WEB_API/Sample_Codes/TGOSQueryAddr/QueryAddrGoogleMap.aspx
def tgos_by_api2(address):
	# TODO
	return False

# TGOS API (被檔掉了，同 tgos_by_api1)
def tgos_by_geocoder(address):
	g = geocoder.tgos(address)
	#g.debug()
	if g.ok:
		return (g.lat, g.lng)
	return False

# 簡易測試
def main():
	addr = '臺北市信義區興雅里松高路１號２８樓'
	loc  = geocode(addr)
	if loc != False:
		print('(%f, %f)' % loc)
	else:
		print('定位失敗')

	addr = '雲林縣元長鄉鹿南村後建八號'
	loc  = geocode(addr)
	if loc != False:
		print('(%f, %f)' % loc)
	else:
		print('定位失敗')

	addr = '高雄市苓雅區三多一路333號'
	loc  = geocode(addr)
	if loc != False:
		print('(%f, %f)' % loc)
	else:
		print('定位失敗')

if __name__ == '__main__':
	main()

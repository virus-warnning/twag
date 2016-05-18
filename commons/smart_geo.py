#!../../bin/python
# coding: utf-8
# dependencies: requests, pyproj

import urllib
import requests
import pyproj

# 匿名處理 Geocode
def geocode(address):
	pagekey = ' XTBMqgNs I44ur5d8TLu0s/KYdkneZ0'

	# 弄個 SessionID
	qs = urllib.urlencode({
		'method': 'GetSessionID',
		'pagekey': pagekey
	})
	url = 'http://map.tgos.nat.gov.tw/TGOSCloud/Generic/Utility/UG_Handler.ashx?%s' % qs
	r = requests.post(url)
	if r.status_code == 200 and r.json()['success'] == 'true':
		sid = r.json()['id']
		cookies = {}
		for c in r.cookies:
			cookies[c.name] = c.value
	else:
		return False

	# 查詢精確位置 (TWD97)
	# 注意!! 地址參數的 key 是 addrsss 不是 address
	qs = urllib.urlencode({'pagekey': pagekey})
	url = 'http://map.tgos.nat.gov.tw/TGOSCloud/Generic/Project/GHTGOSViewer_Map.ashx?%s' % qs
	params = {
		'method': 'queryaddr',
		'addrsss': address,
		'useoddeven': 'false',
		'sid': sid
	}
	r = requests.post(url, data=params, cookies=cookies)
	if r.status_code == 200 and 'AddressList' in r.json():
		result  = r.json()['AddressList'][0]
		loc3826 = (result['X'], result['Y'])
	else:
		return False

	# TWD97 轉 WGS84
	twd97   = pyproj.Proj(init='EPSG:3826')
	loc4326 = twd97(loc3826[0], loc3826[1], inverse=True)

	return (loc4326[1], loc4326[0])

# 簡易測試
def main():
	loc = geocode('台北市中山區南京東路二段2號')
	if len(loc) == 2:
		print('(%f, %f)' % loc)
	else:
		print(loc)

if __name__ == '__main__':
	main()

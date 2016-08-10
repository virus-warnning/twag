#!../../bin/python
# coding: utf-8
#
# @author 小璋丸 <virus.warnning@gmail.com>
#

# geocoder 套件
import geocoder

# 土炮
import re
import requests
import pyproj

# 使用 TGOS 定位
def geocode(address):
	return tgos_by_spider(address)

# TGOS 瀏覽器操作模擬
def tgos_by_spider(address):
	pagekey = 'Unknown'
	cookies = {'ASP.NET_SessionId': 'Unknown'}

	# 取得 pagekey 與 session id
	# *   range: <script id='sircMessage1'>...</script>
	# * pattern: window.sircMessage.sircPAGEKEY = '...';
	r = requests.post('http://map.tgos.nat.gov.tw/TGOSCLOUD/Web/Map/TGOSViewer_Map.aspx')
	if r.status_code == 200:
		m = re.search('window\.sircMessage\.sircPAGEKEY\s?=\s?\'([\w\+%]+)\';', r.text)
		if m != None:
			pagekey = m.group(1)
			for c in r.cookies:
				cookies[c.name] = c.value

	# 取得 TWD 97 (EPSG 3826) 座標
	url = 'http://map.tgos.nat.gov.tw/TGOSCloud/Generic/Project/GHTGOSViewer_Map.ashx?pagekey=' + pagekey
	headers = {
		'Origin': 'http://map.tgos.nat.gov.tw',
		'Referer': 'http://map.tgos.nat.gov.tw/TGOSCLOUD/Web/Map/TGOSViewer_Map.aspx',
		'X-Requested-With': 'XMLHttpRequest'
	}
	data = {
		'method': 'querymoiaddr',
		'address': address,
		'useoddeven': False,
		'sid': cookies['ASP.NET_SessionId']
	}
	r = requests.post(url, headers=headers, cookies=cookies, data=data)
	if r.status_code == 200:
		addinfo = r.json()['AddressList']
		if len(addinfo) > 0:
			# TWD 97 轉 WGS 84
			epsg3826 = pyproj.Proj(init='EPSG:3826')
			coord = epsg3826(addinfo[0]['X'], addinfo[0]['Y'], inverse=True)
			return coord

	return False

# TGOS API (被檔掉了)
def tgos_by_geocoder(address):
	g = geocoder.tgos(address)
	if g.parse.get('featureCount') > 0:
		return (g.lat, g.lng)
	return False

# 簡易測試
def main():
	loc = geocode('台北市內湖區內湖路一段735號')

	if loc != False:
		print('(%f, %f)' % loc)

if __name__ == '__main__':
	main()

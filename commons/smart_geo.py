#!../../bin/python
# coding: utf-8
#
# 相依套件:
# *       requests: 進行有狀態 HTTP 連線
# *         pyproj: EPSG:3826 轉 EPSG:4326
# * beautifulsoup4: 分解 HTML 原始碼內含的 pagekey
#
# @author 小璋丸 <virus.warnning@gmail.com>
#

import urllib
import requests
import pyproj
import re
from bs4 import BeautifulSoup

# TGOS 取得門牌座標
def geocode(address):
	pagekey = False

	# 弄到 pagekey, cookies 產生合理狀態
	# *   range: <script id='sircMessage1'>...</script>
	# * pattern: window.sircMessage.sircPAGEKEY = '...';
	url = 'http://map.tgos.nat.gov.tw/TGOSCLOUD/Web/Map/TGOSViewer_Map.aspx'
	r = requests.post(url)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text, 'html.parser')
		node = soup.find('script', {'id': 'sircMessage1'})
		script = node.get_text().strip()
		m = re.search('window\.sircMessage\.sircPAGEKEY\s?=\s?\'([\w\+%]+)\';', script)
		if m != None:
			pagekey = m.group(1)
			cookies = {}
			for c in r.cookies:
				cookies[c.name] = c.value

	if pagekey == False: return False

	# 查詢精確位置 (TWD97)
	# 注意!! 地址參數的 key 是 addrsss 不是 address
	loc3826 = False
	qs = urllib.urlencode({'pagekey': pagekey})
	url = 'http://map.tgos.nat.gov.tw/TGOSCloud/Generic/Project/GHTGOSViewer_Map.ashx?%s' % qs
	params = {
		'method':     'queryaddr',
		'useoddeven': 'false',
		'addrsss':    address,
		'sid':        cookies['ASP.NET_SessionId']
	}
	r = requests.post(url, data=params, cookies=cookies)
	if r.status_code == 200 and 'AddressList' in r.json():
		result  = r.json()['AddressList'][0]
		loc3826 = (result['X'], result['Y'])

	if loc3826 == False: return False

	# TWD97 轉 WGS84, 回傳 (緯度, 經度)
	twd97   = pyproj.Proj(init='EPSG:3826')
	loc4326 = twd97(loc3826[0], loc3826[1], inverse=True)
	return (loc4326[1], loc4326[0])

# 簡易測試
def main():
	loc = geocode('台北市內湖區內湖路一段591號')
	if loc != False:
		print('(%f, %f)' % loc)

if __name__ == '__main__':
	main()

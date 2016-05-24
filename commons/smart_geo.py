#!../../bin/python
# coding: utf-8
#
# @author 小璋丸 <virus.warnning@gmail.com>
#

import geocoder

# 使用 TGOS 定位
def geocode(address):
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

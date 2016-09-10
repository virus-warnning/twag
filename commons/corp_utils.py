#!../../bin/python
# coding: utf-8

import os
import json
import sys
import smart_http
import smart_geo
import smart_dbapi

DEBUG = True
CODEPATH = os.path.dirname(os.path.abspath(__file__))

## 查詢公司資訊
# 取統編、名稱、負責人、地址、登記機關五個欄位
def get_corp_info(name, boss, gov):
	corp_info = False

	try:
		if type(name) is unicode:
			name = name.encode('utf-8')

		# http://company.g0v.ronny.tw/api/search?q=
		resp = smart_http.request('company.g0v.ronny.tw', '/api/search', {'q': name})
		if resp != False and resp['found'] > 0:
			# 計算每筆資料的相似度績分
			# 名稱 5
			# 負責人 2
			# 註冊單位 1
			# 核准設立 1
			score_list = []
			for e in resp['data']:
				score = 0

				# 名稱
				if u'商業名稱' in e and e[u'商業名稱'] == name:
					score = score + 5

				# 負責人
				#if u'負責人姓名' in e and e[u'負責人姓名'] == boss:
				#	score = score + 2

				# 註冊單位
				#if u'登記機關' in e and e[u'登記機關'] == gov:
				#	score = score + 1

				# 核准設立
				if u'現況' in e and e[u'現況'] == u'核准設立':
					score = score + 1

				uid = e[u'統一編號']
				print(u'%s %s: 積分 %d' % (uid, name, score))
				score_list.append(score)
			'''
			if resp['found'] == 1:
				corp_info = resp['data'][0] # [u'統一編號']
			else:
				# TODO: 出現同名公司，依下列順序選取一項
				# 1. 負責人姓名吻合
				# 2. 註冊單位吻合
				# 3. 核准設立
				for e in resp['data']:
					if u'公司狀況' in e and e[u'公司狀況'] == u'核准設立':
						corp_info = e # [u'統一編號']
					if u'現況' in e and e[u'現況'] == u'核准設立':
						corp_info = e # [u'統一編號']
			'''

	except Exception:
		if DEBUG:
			errln = sys.exc_info()[-1].tb_lineno
			print('第 %d 行發生錯誤' % errln)

	return corp_info

## 取得公司資訊
#
# @param name 事業名稱
# @param boss 負責人姓名
# @param gov  登記機關
#
'''
def get_corp_info(name, boss='', gov=''):
	dbfile = '%s/corp_cache.sqlite' % CODEPATH
	conn = smart_dbapi.connect(dbfile)

	sql = 'SELECT name,uid,boss,addr,lat,lng,mtime FROM corp_cache WHERE name=?'
	cur = conn.execute(sql, (name,))
	# TODO: 如果快取出現多筆，依下列順序選取一項
	# 1. 負責人姓名吻合
	# 2. 註冊單位吻合
	# 3. 其他
	info = cur.fetchone()
	cur.close()

	# TODO: 如果 lat = 0.0 七天後再試一次
	#       如果 lat > 0.0 一年後再試一次

	# 先用暴力法刪除有公司無地址項目，強迫重新查一次
	if info is not None and (info['addr'] == None or info['addr'] == ''):
		conn.execute('DELETE FROM corp_cache WHERE name=?', [name])
		conn.commit()
		info = None

	# 沒有快取資料可以用，用 API 查一下
	if info is None:
		uid = get_corp_id(name, boss, gov)
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

				print(addr)

				if addr != '' and loc == False:
					print('有地址卻定位失敗，可能是 TGOS 禁止存取: %s' % addr)
					exit(0)
			else:
				print('Ronny API return False')

			# 紀錄到快取
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
'''

## 簡易測試
def main():
	#print(get_corp_id(u'興富發建設股份有限公司'))
	print(json.dumps(get_corp_info(u'萬相企業社', '', ''),ensure_ascii=False,indent=2))
	print(json.dumps(get_corp_info(u'萬相企業社', '郭同會', '桃園縣政府'),ensure_ascii=False,indent=2))
	print(json.dumps(get_corp_info(u'萬相企業社', '洪美英', '桃園縣政府'),ensure_ascii=False,indent=2))
	#print(get_corp_id(u'去你爸股份有限公司'))
	#print(get_corp_info(u'廣全科技股份有限公司'))

if __name__ == "__main__":
	main()

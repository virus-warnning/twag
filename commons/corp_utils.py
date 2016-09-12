#!../../bin/python
# coding: utf-8

import os
import json
import time
import smart_http
import smart_geo
import smart_dbapi

DEBUG = True
CODEPATH = os.path.dirname(os.path.abspath(__file__))

_conn = None

## 不固定屬性名稱讀取
#
# @param dict 字典
# @param keys 接受的鍵值，排前面的優先採用
#
def get_attr(dict, keys):
	for k in keys:
		v = dict.get(k)
		if v is not None:
			return v
	return None

## 取得資料庫連線
#
def get_conn():
	global _conn
	if _conn is None:
		dbfile = '%s/corp_cache.sqlite' % CODEPATH
		_conn = smart_dbapi.connect(dbfile)
	return _conn

## 從快取查詢公司
#
# @param name 公司名稱
#
def list_corp_from_cache(name):
	dbfile = '%s/corp_cache.sqlite' % CODEPATH
	conn = get_conn()
	sql  = 'SELECT * FROM corp_cache WHERE name=?'
	cur  = conn.execute(sql, [name])
	corp_list = []
	for row in cur:
		corp_list.append(row)
	if len(corp_list) > 0:
		return corp_list
	return False

## 從 API 查詢公司
#
# @param name 公司名稱
#
def list_corp_from_api(name):
	resp = smart_http.request('company.g0v.ronny.tw', '/api/search', {'q': name})
	if resp != False and resp['found'] > 0:
		corp_list = []
		for e in resp['data']:
			fullname = get_attr(e, ['公司名稱', '商業名稱'])
			if fullname == name:
				corp_list.append({
					'uid':    e['統一編號'],
					'name':   name,
					'boss':   get_attr(e, ['代表人姓名', '負責人姓名']),
					'addr':   get_attr(e, ['公司所在地', '地址']),
					'regat':  e['登記機關'],
					'status': get_attr(e, ['公司狀況', '現況']),
					'lat':    0,
					'lng':    0
				})
		if len(corp_list) > 0:
			return corp_list
	return False

## 查詢公司資訊，傳回相似度最接近的一筆
#
# @param name 公司名稱
# @param boss 負責人
# @param gov  登記機關
#
def get_corp_info(name, boss='', gov=''):
	# 先從快取查公司
	corp_list = list_corp_from_cache(name)

	# 找不到再從 API 查公司
	if corp_list == False:
		corp_list = list_corp_from_api(name)
		if corp_list != False:
			# API 查到的結果寫入快取
			conn = get_conn()
			for e in corp_list:
				sql = 'INSERT INTO corp_cache(uid, name, boss, addr, regat, status, mtime) VALUES (?,?,?,?,?,?,DATETIME())'
				conn.execute(sql, (e['uid'], e['name'], e['boss'], e['addr'], e['regat'], e['status']))
			conn.commit()

	# 選取吻合度最高的公司
	if corp_list != False:
		# 計算吻合度積分
		score_list = []

		for e in corp_list:
			score = 0
			if boss != '' and e['boss'] == boss:
				score = score + 3
			if gov in e['regat']:
				score = score + 1
			if e['status'] == '核准設立':
				score = score + 1
			score_list.append(score)

		# 選取積分最高的公司
		best_score = -1
		best_index = -1
		for i in range(len(score_list)):
			if best_score < score_list[i]:
				best_score = score_list[i]
				best_index = i
		corp_info = corp_list[best_index]

		# 填滿地理座標
		if corp_info['lat'] == 0:
			loc = smart_geo.geocode(corp_info['addr'])
			if loc != False:
				corp_info['lat'] = loc[0]
				corp_info['lng'] = loc[1]
				sql = 'UPDATE corp_cache SET lat=?, lng=? WHERE uid=?'
				conn = get_conn()
				conn.execute(sql, (corp_info['lat'], corp_info['lng'], corp_info['uid']))
				conn.commit()
			time.sleep(0.5)

		return corp_info

	return False

## 簡易測試
def main():
	#print(get_corp_info('興富發建設股份有限公司','',''))
	#print(json.dumps(get_corp_info(u'萬相企業社', '', ''),ensure_ascii=False,indent=2))
	#print(get_corp_info('萬相企業社', '郭同會', '桃園縣政府'))
	#print(get_corp_info('去你爸股份有限公司'))
	#print(list_corp_from_api('廣全科技股份有限公司'))
	#print(get_corp_info('萬相企業社'))
	#print(get_corp_info('萬相企業社', '洪美英', '桃園縣政府'))
	print(get_corp_info('樺達奶茶', '', '臺北市'))
	print(get_corp_info('樺達奶茶', '', '新北市'))
	print(get_corp_info('樺達奶茶', '', '高雄市'))

if __name__ == "__main__":
	main()

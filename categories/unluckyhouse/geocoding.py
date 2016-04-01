#!../../../bin/python
# coding: utf-8

import re
import time
import smart_http
import smart_dbapi

# 匿名處理 Geocode
def geocode(address):
	params = {'address': address}
	resp   = smart_http.request('maps.googleapis.com', '/maps/api/geocode/json', params)
	if resp != False and resp['status'] == 'OK':
		loc = resp['results'][0]['geometry']['location']
		return (loc['lat'], loc['lng'])
	return False

# 檢查定位問題用
'''
print(geocode(u'彰化市彰水路33巷2之1號'))
exit(0)
'''

# 篩選可定位的凶宅
ROW_LIMIT = 100
sql = u"SELECT id,area,address FROM unluckyhouse WHERE state=1 AND INSTR(address,'X')=0 AND INSTR(address,'號')>0 ORDER BY id DESC LIMIT ?"
con = smart_dbapi.connect('unluckyhouse.sqlite')
cur = con.execute(sql, (ROW_LIMIT,))

for row in cur:
	topic_id = row['id']
	address = row['area'] + row['address']
	address = re.sub(u'\(.*\)', u'', address)
	if u'號' in address and u'X' not in address:
		loc = geocode(address)
		if loc != False:
			print(u'%d 定位完成，座標 (%f, %f)' % (topic_id, loc[0], loc[1]))
			con.execute('UPDATE unluckyhouse SET lat=?, lng=?, state=2 WHERE id=?', (loc[0], loc[1], topic_id))
			time.sleep(1) # 避免被當作 DoS 踢掉
		else:
			print(u'%d 定位失敗，可能超過今天使用額度' % topic_id)
			break

	else:
		print(u'%d 地址不完整，不進行定位' % topic_id)

con.commit()
cur.close()
con.close()
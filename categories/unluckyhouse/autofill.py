#!../../../bin/python
# coding: utf-8

import re
import smart_http
import smart_dbapi
from datetime import date, datetime, timedelta

def analyze(con, topic_id, soup):
	execnt = 0

	# 排除 "站務服務中心"、"其他" 兩個分類
	# div#navbar > a:nth-child(2)
	branch = soup.find(id="navbar").find_all('a')[1].get_text()
	if branch == u'站務服務中心' or branch == u'其他':
		sql = 'UPDATE unluckyhouse SET state=-2 WHERE id=?'
		con.execute(sql, (t,))
		con.commit()
		print(u'%d 非凶宅文章 (分類: %s)' % (topic_id, branch))
		return

	all_node = soup.find_all('div', {'class': 'posttext'})
	all_post = []
	for node in all_node:
		all_post.append(node.get_text())

	del soup

	print(u'凶宅編號: %d' % topic_id)

	# 分析死者年齡
	# - 足歲: RE 取 '\d{1,2}歲'
	# - 嬰兒: 暫不處理
	# TODO: 中文數值辨識
	pattern = re.compile(u'\d{1,2}多?歲|\d{1,2}個月')
	age_list = pattern.findall(all_post[0])
	if len(age_list) == 1:
		age = age_list[0]
		age_unit = u'Y'
		if age.endswith(u'月'):
			age_unit = u'M'
		age = (int)(re.search('\d+', age).group(0))

		# 分析死者性別 (從年齡後 5 字找)
		# - 男性: 男、翁、少年
		# - 女性: 女、婦
		i = all_post[0].find(age_list[0]) + len(age_list[0])
		s = all_post[0][i:i+5]
		m = re.search(u'女|婦|男|翁|少年', s)
		gender = 'M'
		if m is not None:
			if m.group(0) in [u'女', u'婦']:
				gender = 'F'

		print(u'人物年齡: %s%s' % (age, age_unit))
		print(u'人物性別: %s' % gender)
		sql = 'UPDATE unluckyhouse SET age=?, age_unit=?, gender=? WHERE id=?'
		con.execute(sql, (age, age_unit, gender, topic_id))
		execnt = execnt + 1
	else:
		if len(age_list)>0:
			print(u'人物年齡:'),
			for age in age_list:
				print(age),
			print('')
		else:
			print(u'人物年齡: (無)')

	# 分析死法
	# 搜尋關鍵字：
	# - 自殺類: 跳樓、燒炭、上吊 (依熱門程度排序)
	# - 意外類: 火警、火災、墜樓
	# - 他殺類: 虐童、勒死、殺害
	pattern = re.compile(u'跳樓|跳下|燒炭|上吊|自刎|火警|火災|墜樓|窒息|猝死|虐童|殺害|行凶|毒手')
	all_approach = pattern.findall(all_post[0])
	if set(all_approach) == set([u'跳樓', u'跳下', u'墜樓']):
		all_approach = [u'跳樓']
	if set(all_approach) == set([u'上吊', u'窒息']):
		all_approach = [u'上吊']
	if len(set(all_approach)) == 1:
		approach = all_approach[0]
		# 名稱正規化
		if approach in (u'殺害', u'行凶', u'毒手'):
			approach = u'凶殺'
		if approach in (u'火警'):
			approach = u'火災'
		print(u'死亡方式: %s' % approach)
		sql = 'UPDATE unluckyhouse SET approach=? WHERE id=?'
		con.execute(sql, (approach, topic_id))
		execnt = execnt + 1

		# 區別主動性
		initative = u'S'
		if approach in (u'火災', u'墜樓', u'窒息', u'猝死'):
			initative = 'A'
		if approach in (u'虐童', u'凶殺'):
			initative = 'M'
		sql = 'UPDATE unluckyhouse SET initative=? WHERE id=?'
		con.execute(sql, (initative, topic_id))
		execnt = execnt + 1
		print(u'主動性: %s' % initative)
	else:
		if len(all_approach) > 0:
			print(u'死亡方式:'),
			for a in set(all_approach):
				print(a),
			print('(需要人工處理)')
		else:
			print(u'死亡方式: (無)')

	# 分析新聞連結
	# 依新聞完整度排序取樣：
	# 水果 > 自由 > 法拍 > 聯合 > 三立 > 中時
	channels = [
		'http://www.appledaily.com.tw',
		'http://news.ltn.com.tw',
		'http://aomp.judicial.gov.tw',
		'http://www.chinatimes.com',
		'http://www.udn.com',
		'http://udn.com',
		'http://www.setn.com',
		'http://www.cna.com.tw',
		'http://www.on.cc'
	]
	pattern   = re.compile(u'http://[\w\.\?\-%/]+')
	all_link  = pattern.findall(all_post[0])
	news_link = False
	for link in all_link:
		for c in channels:
			if link.startswith(c):
				news_link = link
				break
	
	if news_link is not False:
		print(u'新聞連結: %s' % news_link)
		sql = 'UPDATE unluckyhouse SET news=? WHERE id=?'
		con.execute(sql, (news_link, topic_id))
		execnt = execnt + 1

	# 分析地址
	# RE 取 XX(縣/市) 開頭的 post
	address = False
	pattern = re.compile(u'^\w{2}(縣|市)', re.UNICODE)
	for i in range(1,len(all_post)):
		post = all_post[i]
		m = pattern.search(post)
		if m is not None:
			address = post
			break

	if address is not False:
		# 特例: 桃園市平鎮市延平路二段29號(時代廣場社區)
		for c in [u'區', u'市', u'鄉', u'鎮']:
			sp = address.find(c, 3)
			if sp > -1 and sp < 10:
				break

		if sp > -1:
			area    = address[0:sp+1]
			address = address[sp+1:]
			print(u'案發地址: %s / %s' % (area, address))

			sql = 'UPDATE unluckyhouse SET area=?, address=? WHERE id=?'
			con.execute(sql, (area, address, topic_id))
			execnt = execnt + 1
		else:
			print(u'案發地址格式有誤: %s' % address)
	else:
		print(u'案發地址: (無)')

	# 分析新聞日期
	pattern = re.compile(u'(\d+)[年/\-](\d+)[月/\-](\d+)日?')
	m = pattern.search(all_post[0])
	if m is not None:
		yy = int(m.group(1))
		mm = int(m.group(2))
		dd = int(m.group(3))
		print(u'新聞日期: %04d-%02d-%02d' % (yy,mm,dd))

		# 分析相對時間
		# 特例:
		# * 討論串 6509 - 台北市健康路今午2時許，發生1起墜樓案件
		# TODO: 中文數值辨識
		m = re.search(u'([昨今前]?)天?([凌清早]晨|[上下]?午|傍?晚間?|深夜)(\d+)[時點]', all_post[0])
		if m is not None:
			doff = 0
			if m.group(1) == u'昨':
				doff = -1
			if m.group(1) == u'前':
				doff = -2
			hh = int(m.group(3))
			if m.group(2) in (u'午', u'下午', u'傍晚', u'晚間', u'深夜'):
				if hh < 12:
					hh = hh + 12
			print(u'相對時間: %d 天 %s 時 (%s)' % (doff, hh, m.group(2)))

			# 轉換成 ISO8601 時間
			dt = datetime(yy,mm,dd) + timedelta(days=doff, hours=hh)
			dtiso = dt.isoformat(' ')
			print(u'絕對時間: %s' % dtiso)

			sql = 'UPDATE unluckyhouse SET datetime=? WHERE id=?'
			con.execute(sql, (dtiso, topic_id))
			execnt = execnt + 1

	if execnt == 6:
		sql = 'UPDATE unluckyhouse SET state=1 WHERE id=?'
		con.execute(sql, (topic_id,))
		print(u'** 資料完整，不需要人工處理 **')
	else:
		print(u'** 資料不完整 execnt=%d **' % execnt)

	con.commit()

# 取得未處理清單
# unluckyhouse.state=0
ROW_LIMIT = 3
sql = 'SELECT id FROM unluckyhouse WHERE state=0 ORDER BY id DESC LIMIT ?'
con = smart_dbapi.connect('unluckyhouse.sqlite')
cur = con.execute(sql, (ROW_LIMIT,))

todolist = []
for row in cur:
	todolist.append(row['id'])
print('分析範圍: %d ~ %d' % (todolist[0], todolist[-1]))
print('******************************')

cur.close()

# 使用 BeautifulSoup 4 分析文章
# http://unluckyhouse.com/archive/index.php/t-%d.html
host = 'unluckyhouse.com'
uri  = '/archive/index.php/t-%d.html'

for t in todolist:
	try:
		soup = smart_http.request(host, uri % t)
		if soup != False:
			analyze(con, t, soup)
		else:
			con.execute('UPDATE unluckyhouse SET state=-1 WHERE id=?', (t,))
			print('主題 %d 已刪除' % t)
	except Exception as e:
		print('分析過程發生錯誤: %s' % e)

con.commit()
con.close()

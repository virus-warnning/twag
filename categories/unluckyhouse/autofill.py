#!../../../bin/python
# coding: utf-8

import re
import smart_http
import smart_dbapi
import zhtok
from StringIO import StringIO
from datetime import date, datetime, timedelta

## 偵測死法
def detect_approach(text):
	# - 自殺類: 跳樓、燒炭、上吊 (依熱門程度排序)
	# - 意外類: 火災、CO中毒
	# - 他殺類: 凌虐、絞死、凶殺(其他)
	# - 觀察中: 心臟病發(猝死)、縱火(誤判為意外火災)
	# P.S. 墜樓有可能是自殺跳樓，也有可能是意外墜樓
	pattern = re.compile(u'跳樓|跳下|燒炭|上吊|自刎|火警|火災|火勢|1氧化碳中毒|猝死|虐童|勒痕|槍擊|殺害|行凶|毒手')
	all_approach = pattern.findall(text)

	# 同義詞正規化
	for i in range(len(all_approach)):
		a = all_approach[i]
		if   a in [u'跳下']:
			all_approach[i] = u'跳樓'
		elif a in [u'火警', u'火勢']:
			all_approach[i] = u'火災'
		elif a in [u'1氧化碳中毒']:
			all_approach[i] = u'CO中毒'
		elif a in [u'勒痕']:
			all_approach[i] = u'絞死'
		elif a in [u'槍擊']:
			all_approach[i] = u'槍殺'
		elif a in [u'虐童']:
			all_approach[i] = u'凌虐'
		elif a in [u'殺害', u'行凶', u'毒手']:
			all_approach[i] = u'凶殺'

	# 去重複化
	all_approach = list(set(all_approach))

	return all_approach

## 偵測絕對時間
def detect_datetime(text):
	ZH_TO_HOUR = {
		u'凌晨':  1, u'清晨':  4, u'早晨':  7, u'晨間':  7,
		u'早上':  9, u'上午':  9, u'中午': 12, u'午間': 12,
		u'下午': 15, u'傍晚': 18, u'晚上': 20, u'晚間': 20,
		u'夜晚': 20, u'夜間': 20, u'半夜': 22, u'深夜': 22,
		u'晨': 7, u'早': 9, u'晚': 19, u'夜': 21
	}

	hh = 0
	mm = 0

	# 搜尋概略時間
	m = re.search(u'[凌清早]晨|[上中]午|[晨午]間|早上|晚[上間]|夜[晚間]|[半深]夜|下午|傍晚', text)
	if m is not None:
		# 概略時間包含晚、夜、下午，需要 +12 時
		si = m.start(0)
		ei = m.end(0)
		round_time = m.group(0)

		# 往後找精確時間
		mi = 0
		hhoff = 0
		suffix = text[ei:ei+20]
		m = re.search(u'[約近]?(\d{1,2})[時點]', suffix)
		if m is not None:
			hh = int(m.group(1))
			if re.search(u'晚|夜|下午', round_time) is not None:
				hhoff = 12

			m  = re.search(u'(\d{1,2})分', suffix)
			if m is not None:
				mi = int(m.group(1))
		else:
			hh = ZH_TO_HOUR[round_time]

		# 往前找相對日
		ddoff  = False
		prefix = text[si-4:si]
		m = re.search(u'[前昨今明後]天|\d{1,2}天[前後]|前\d{1,2}天', prefix)
		if m is not None:
			rdate = m.group(0)
			if len(rdate) == 2:
				# TODO: 改用查表法
				if   rdate == u'前天':
					ddoff = -2
				elif rdate == u'昨天':
					ddoff = -1
				elif rdate == u'今天':
					ddoff = 0
				elif rdate == u'明天':
					ddoff = 1
				elif rdate == u'後天':
					ddoff = 2
			else:
				m = re.search(u'\d{1,2}', rdate)
				ddoff = int(m.group(0))
				if rdate.find(u'前') > -1:
					ddoff = -ddoff

		# 往前找絕對日
		dd = False
		if ddoff == False:
			m = re.search(u'(\d{1,2})日', prefix)
			if m is not None:
				dd = int(m.group(1))

		# 往前找完整日期
		# TODO: 獨立
		dates = list(re.finditer('(\d{2,4})-(\d{1,2})-(\d{1,2})', text[0:si]))
		if len(dates) > 0:
			m  = dates[-1]
			yy = int(m.group(1))
			mo = int(m.group(2))
			if dd == False:
				dd = int(m.group(3))
			if yy < 1000:
				yy = yy + 1911
			dt = datetime(yy,mo,dd) + timedelta(days=ddoff, hours=hh+hhoff, minutes=mi)
			return dt.isoformat(' ')

	# 精簡說法
	m = re.search(u'([昨今明])([晨早晚夜])', text)
	if m is not None:
		si = m.start(0)
		ei = m.end(0)
		rdate = m.group(1)
		rtime = m.group(2)

		# 往後找精確時間
		mi = 0
		hhoff = 0
		suffix = text[ei:ei+20]
		m = re.search(u'[約近]?(\d{1,2})[時點]', suffix)
		if m is not None:
			hh = int(m.group(1))
			if rtime == u'晚' or rtime == u'夜':
				hhoff = 12

			m  = re.search(u'(\d{1,2})分', suffix)
			if m is not None:
				mi = int(m.group(1))
		else:
			hh = ZH_TO_HOUR[rtime]
		
		# 轉換相對日
		if   rdate == u'昨':
			ddoff = -1
		elif rdate == u'明':
			ddoff = 1
		else:
			ddoff = 0

		# 往前找完整日期
		# TODO: 獨立
		dates = list(re.finditer('(\d{2,4})-(\d{1,2})-(\d{1,2})', text[0:si]))
		if len(dates) > 0:
			m  = dates[-1]
			yy = int(m.group(1))
			mo = int(m.group(2))
			dd = int(m.group(3))
			if yy < 1000:
				yy = yy + 1911
			dt = datetime(yy,mo,dd) + timedelta(days=ddoff, hours=hh+hhoff, minutes=mi)
			return dt.isoformat(' ')

	return False

## 偵測新聞連結
def detect_news(text):
	# 依新聞完整度排序取樣：
	# 水果 > 自由 > 法拍 > 聯合 > 三立 > 中時 > 中央社 > 東網
	channels = [
		'http://www.appledaily.com.tw',
		'http://news.ltn.com.tw',
		'http://aomp.judicial.gov.tw',
		'http://www.udn.com',
		'http://udn.com',
		'http://www.setn.com',
		'http://www.chinatimes.com',
		'http://www.cna.com.tw',
		'http://www.on.cc'
	]

	best_link = False
	max_rank  = len(channels)
	pattern   = re.compile(u'http://[\w\.\?\-%/=]+')
	all_link  = pattern.findall(text)

	for link in all_link:
		for i in range(max_rank):
			ch = channels[i]
			if link.startswith(ch):
				best_link = link
				max_rank  = i
				break
		if max_rank == 0:
			break

	return best_link

## 偵測地址
def detect_address(text):
	pat_include = re.compile(u'\w{2}[縣市][\w\-]+[路街鄰巷弄之號樓F]', re.UNICODE)
	pat_exclude = re.compile(u'跳樓')
	
	m = pat_include.search(text)
	if m is not None:
		full = m.group(0)

		# 忽略符合排除條件的內容
		# - 6907 高雄市新田路某大樓19日發生男子跳樓
		if pat_exclude.search(full) is not None:
			return False

		# 繼續往後取社區名稱 or 地點註解
		suffix = text[m.end():m.end()+10]
		m = re.search('^\s?\(.+\)', suffix)
		if m is not None:
			full = full + u' ' + m.group(0)

		# 還原部分中文數字
		# 巷、弄、號、樓、F、鄰保留阿拉伯數字，其餘還原中文字
		# - 新北市3重區3安里6張街12號
		# - 高雄市苓雅區3多1路333號
		ms = re.finditer('\d+', full)
		offset = 0
		strout = StringIO()
		for m in ms:
			num = m.group()
			if re.match(u'[鄰巷弄之號樓FX\-]', full[m.end()]) is None:
				num = zhtok.convert_chinese_numerals(num)
			
			strout.write(full[offset:m.start()])
			strout.write(num)
			offset = m.end()

		strout.write(full[offset:])
		full = strout.getvalue()
		strout.close()

		# TODO: 高雄市前鎮 / 區中華五路
		pat = re.compile(u'[鄉鎮市區]')
		m = pat.search(full, 3)
		if m is not None:
			sp      = m.start(0)+1
			area    = full[0:sp]
			address = full[sp:]
			return (area, address)

	return False

## 分析 HTML
def analyze(con, topic_id, soup):
	# 排除 "站務服務中心"、"其他" 兩個分類
	# div#navbar > a:nth-child(2)
	branch = soup.find(id="navbar").find_all('a')[1].get_text()
	if branch == u'站務服務中心' or branch == u'其他':
		sql = 'UPDATE unluckyhouse SET state=-2 WHERE id=?'
		con.execute(sql, (t,))
		con.commit()
		print(u'%d 非凶宅文章 (分類: %s)' % (topic_id, branch))
		return

	#======================
	# 判斷為有效文章，開始分析
	#======================
	missing = []

	# 標題 (可能帶有地址)
	subject = soup.find('p', {'class': 'largefont'}).get_text()

	# 所有內文
	all_node = soup.find_all('div', {'class': 'posttext'})
	all_post = []
	for node in all_node:
		text = node.get_text()
		text = zhtok.convert_arabic_numerals(text)
		text = zhtok.convert_iso_date(text)
		all_post.append(text)

	print(u'凶宅編號: %d' % topic_id)
	#print(all_post[0])

	# 分析死者年齡
	# todo:
	# - 死者余姓婦人59年次
	pattern  = re.compile(u'\d{1,2}多?歲|\d{1,2}個?月')
	age_list = pattern.findall(all_post[0])
	age_list = list(set(age_list))

	if len(age_list) == 1:
		age = age_list[0]
		age_unit = u'Y'
		if age.endswith(u'月'):
			age_unit = u'M'
		age = (int)(re.search('\d+', age).group(0))

		# 分析死者性別 (從年齡後 10 字找)
		# - 男性: 男、翁、少年
		# - 女性: 女、婦
		# - 特例: 27歲的台大陳姓女碩士生 (女字在歲後的第 6 個字元)
		i = all_post[0].find(age_list[0]) + len(age_list[0])
		s = all_post[0][i:i+10]
		m = re.search(u'女|婦|男|翁|少年', s)
		gender = 'M'
		if m is not None:
			if m.group(0) in [u'女', u'婦']:
				gender = 'F'

		print(u'人物年齡: %s%s' % (age, age_unit))
		print(u'人物性別: %s' % gender)
		sql = 'UPDATE unluckyhouse SET age=?, age_unit=?, gender=? WHERE id=?'
		con.execute(sql, (age, age_unit, gender, topic_id))
	else:
		if len(age_list)>0:
			print(u'人物年齡:'),
			for age in age_list:
				print(age),
			print('')
		else:
			print(u'人物年齡: (無)')
		missing.append(u'人物')

	# 分析死法
	all_approach = detect_approach(all_post[0])
	if len(all_approach) == 1:
		approach = all_approach[0]
		print(u'死亡方式: %s' % approach)
		sql = 'UPDATE unluckyhouse SET approach=? WHERE id=?'
		con.execute(sql, (approach, topic_id))

		# 區別主動性
		initative = u'S'
		if approach in (u'火災', u'猝死', u'CO中毒'):
			initative = 'A'
		if approach in (u'凌虐', u'絞死', u'槍殺', u'凶殺'):
			initative = 'M'
		sql = 'UPDATE unluckyhouse SET initative=? WHERE id=?'
		con.execute(sql, (initative, topic_id))
		print(u'主動性: %s' % initative)
	else:
		if len(all_approach) > 0:
			print(u'死亡方式: %s (需要人工處理)' % u' '.join(all_approach))
		else:
			print(u'死亡方式: (無)')
			missing.append(u'死亡方式')

	# 分析新聞連結 (看主文所有回應)
	news_link = detect_news(u'\n'.join(all_post))
	if news_link is not False:
		print(u'新聞連結: %s' % news_link)
		sql = 'UPDATE unluckyhouse SET news=? WHERE id=?'
		con.execute(sql, (news_link, topic_id))
	else:
		missing.append(u'新聞')

	# 分析地址 (看所有回應及標題)
	all_clues = all_post[1:]
	all_clues.append(subject)

	for clue in all_clues:
		full_address = detect_address(clue)
		if full_address != False:
			break

	if full_address is not False:
		print(u'案發地址: %s / %s' % full_address)
		(area, address) = full_address
		sql = 'UPDATE unluckyhouse SET area=?, address=? WHERE id=?'
		con.execute(sql, (area, address, topic_id))
	else:
		print(u'案發地址: (無)')
		missing.append(u'地址')

	# 分析案發時間 (只看主文)
	dt = detect_datetime(all_post[0])
	if dt != False:
		print(u'案發時間: %s' % dt)
		sql = 'UPDATE unluckyhouse SET datetime=? WHERE id=?'
		con.execute(sql, (dt, topic_id))
	else:
		missing.append(u'案發時間')

	# 最後摘要
	if len(missing) == 0:
		sql = 'UPDATE unluckyhouse SET state=1 WHERE id=?'
		con.execute(sql, (topic_id,))
		print(u'** 資料完整，不需要人工處理 **')
	else:
		print(u'** 缺少 (%s) 欄位 **' % u'、'.join(missing))

	con.commit()

# 取得未處理清單
# unluckyhouse.state=0
ROW_LIMIT    = 100
LATEST_LIMIT = 8000
BASE_LIMIT   = 5900
sql = 'SELECT id FROM unluckyhouse WHERE state=0 AND id>=? AND id<=? ORDER BY id DESC LIMIT ?'
con = smart_dbapi.connect('unluckyhouse.sqlite')
cur = con.execute(sql, (BASE_LIMIT, LATEST_LIMIT, ROW_LIMIT))

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
	# 同步最新文章時，限制編號下限
	if t < BASE_LIMIT:
		break

	try:
		soup = smart_http.request(host, uri % t)
		if soup != False:
			analyze(con, t, soup)
		else:
			con.execute('UPDATE unluckyhouse SET state=-1 WHERE id=?', (t,))
			print('主題 %d 已刪除' % t)
		del soup
	except Exception as e:
		print('分析過程發生錯誤: %s' % e)

con.commit()
con.close()

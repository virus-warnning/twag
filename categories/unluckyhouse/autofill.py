import os
import sys
import re
import io
import traceback
from datetime import date, datetime, timedelta

commons_path = os.path.realpath('../../commons')
sys.path.insert(1, commons_path)

import zhtok
import smart_http
import smart_dbapi

# 偵測 bs4 是否已安裝
try:
	from bs4 import BeautifulSoup
except ImportError:
	print('bs4 is required.')
	print('Run `pip install beautifulsoup4` to install.')
	exit()

## 偵測死法
def detect_approach(text):
	# - 自殺類: 跳樓、燒炭、上吊 (依熱門程度排序)
	# - 意外類: 火災、CO中毒
	# - 他殺類: 凌虐、絞死、凶殺(其他)
	# - 觀察中: 心臟病發(猝死)、縱火(誤判為意外火災)
	# P.S. 墜樓有可能是自殺跳樓，也有可能是意外墜樓
	pattern = re.compile('跳樓|跳下|燒炭|上吊|自刎|火警|火災|火勢|1氧化碳中毒|猝死|虐童|勒痕|槍擊|殺害|行凶|毒手')
	all_approach = pattern.findall(text)

	# 同義詞正規化
	for i in range(len(all_approach)):
		a = all_approach[i]
		if   a in ['跳下']:
			all_approach[i] = '跳樓'
		elif a in ['火警', '火勢']:
			all_approach[i] = '火災'
		elif a in ['1氧化碳中毒']:
			all_approach[i] = 'CO中毒'
		elif a in ['勒痕']:
			all_approach[i] = '絞死'
		elif a in ['槍擊']:
			all_approach[i] = '槍殺'
		elif a in ['虐童']:
			all_approach[i] = '凌虐'
		elif a in ['殺害', '行凶', '毒手']:
			all_approach[i] = '凶殺'

	# 去重複化
	all_approach = list(set(all_approach))

	return all_approach

## 偵測絕對時間
def detect_datetime(text):
	ZH_TO_HOUR = {
		'凌晨':  1, '清晨':  4, '早晨':  7, '晨間':  7,
		'早上':  9, '上午':  9, '中午': 12, '午間': 12,
		'下午': 15, '傍晚': 18, '晚上': 20, '晚間': 20,
		'夜晚': 20, '夜間': 20, '半夜': 22, '深夜': 22,
		'晨': 7, '早': 9, '晚': 19, '夜': 21
	}

	hh = 0
	mm = 0

	# 搜尋概略時間
	m = re.search('[凌清早]晨|[上中]午|[晨午]間|早上|晚[上間]|夜[晚間]|[半深]夜|下午|傍晚', text)
	if m is not None:
		# 概略時間包含晚、夜、下午，需要 +12 時
		si = m.start(0)
		ei = m.end(0)
		round_time = m.group(0)

		# 往後找精確時間
		mi = 0
		hhoff = 0
		suffix = text[ei:ei+20]
		m = re.search('[約近]?(\d{1,2})[時點]', suffix)
		if m is not None:
			hh = int(m.group(1))
			if re.search('晚|夜|下午', round_time) is not None:
				hhoff = 12

			m  = re.search('(\d{1,2})分', suffix)
			if m is not None:
				mi = int(m.group(1))
		else:
			hh = ZH_TO_HOUR[round_time]

		# 往前找相對日
		ddoff  = False
		prefix = text[si-4:si]
		m = re.search('[前昨今明後]天|\d{1,2}天[前後]|前\d{1,2}天', prefix)
		if m is not None:
			rdate = m.group(0)
			if len(rdate) == 2:
				# TODO: 改用查表法
				if   rdate == '前天':
					ddoff = -2
				elif rdate == '昨天':
					ddoff = -1
				elif rdate == '今天':
					ddoff = 0
				elif rdate == '明天':
					ddoff = 1
				elif rdate == '後天':
					ddoff = 2
			else:
				m = re.search('\d{1,2}', rdate)
				ddoff = int(m.group(0))
				if rdate.find('前') > -1:
					ddoff = -ddoff

		# 往前找絕對日
		dd = False
		if ddoff == False:
			m = re.search('(\d{1,2})日', prefix)
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
	m = re.search('([昨今明])([晨早晚夜])', text)
	if m is not None:
		si = m.start(0)
		ei = m.end(0)
		rdate = m.group(1)
		rtime = m.group(2)

		# 往後找精確時間
		mi = 0
		hhoff = 0
		suffix = text[ei:ei+20]
		m = re.search('[約近]?(\d{1,2})[時點]', suffix)
		if m is not None:
			hh = int(m.group(1))
			if rtime == '晚' or rtime == '夜':
				hhoff = 12

			m  = re.search('(\d{1,2})分', suffix)
			if m is not None:
				mi = int(m.group(1))
		else:
			hh = ZH_TO_HOUR[rtime]

		# 轉換相對日
		if   rdate == '昨':
			ddoff = -1
		elif rdate == '明':
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
	# 水果 > 自由 > 法拍 > 聯合 > 三立 > 中時 > 中央社 > 東森 > 東網
	channels = [
		'www.appledaily.com.tw',
		'news.ltn.com.tw',
		'aomp.judicial.gov.tw',
		'www.udn.com',
		'udn.com',
		'www.setn.com',
		'www.chinatimes.com',
		'www.cna.com.tw',
		'www.ettoday.net',
		'www.on.cc'
	]

	best_link = False
	max_rank  = len(channels)
	pattern   = re.compile('https?://[\w\.\?\-%/=]+')
	all_link  = pattern.findall(text)

	for link in all_link:
		for i in range(max_rank):
			ch = channels[i]
			if ch in link:
				best_link = link
				max_rank  = i
				break
		if max_rank == 0:
			break

	return best_link

## 偵測地址
def detect_address(text):
	pat_include = re.compile('\w{2}[縣市][\w\-]+[路街鄰巷弄之號樓F]', re.UNICODE)
	pat_exclude = re.compile('跳樓')

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
			full = full + ' ' + m.group(0)

		# 還原部分中文數字
		# 巷、弄、號、樓、F、鄰保留阿拉伯數字，其餘還原中文字
		# - 新北市3重區3安里6張街12號
		# - 高雄市苓雅區3多1路333號
		ms = re.finditer('\d+', full)
		offset = 0
		strout = io.StringIO()
		for m in ms:
			num = m.group()
			if re.match('[鄰巷弄之號樓FX\-]', full[m.end()]) is None:
				num = zhtok.convert_chinese_numerals(num)

			strout.write(full[offset:m.start()])
			strout.write(num)
			offset = m.end()

		strout.write(full[offset:])
		full = strout.getvalue()
		strout.close()

		# TODO: 高雄市前鎮 / 區中華五路
		pat = re.compile('[鄉鎮市區]')
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
	if branch == '站務服務中心' or branch == '其他':
		sql = 'UPDATE unluckyhouse SET state=-2 WHERE id=?'
		con.execute(sql, (topic_id,))
		con.commit()
		print('%d 非凶宅文章 (分類: %s)' % (topic_id, branch))
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

	print('凶宅編號: {}'.format(topic_id))

	# 分析死者年齡
	# todo:
	# - 死者余姓婦人59年次
	pattern  = re.compile('\d{1,2}多?歲|\d{1,2}個?月')
	age_list = pattern.findall(all_post[0])
	age_list = list(set(age_list))

	if len(age_list) == 1:
		age = age_list[0]
		age_unit = 'Y'
		if age.endswith('月'):
			age_unit = 'M'
		age = (int)(re.search('\d+', age).group(0))

		# 分析死者性別 (從年齡後 10 字找)
		# - 男性: 男、翁、少年
		# - 女性: 女、婦
		# - 特例: 27歲的台大陳姓女碩士生 (女字在歲後的第 6 個字元)
		i = all_post[0].find(age_list[0]) + len(age_list[0])
		s = all_post[0][i:i+10]
		m = re.search('女|婦|男|翁|少年', s)
		gender = 'M'
		if m is not None:
			if m.group(0) in ['女', '婦']:
				gender = 'F'

		print('人物年齡: {}{}'.format(age, age_unit))
		print('人物性別: {}'.format(gender))
		sql = 'UPDATE unluckyhouse SET age=?, age_unit=?, gender=? WHERE id=?'
		con.execute(sql, (age, age_unit, gender, topic_id))
	else:
		if len(age_list) > 0:
			print('人物年齡: {}'.format(','.join(age_list))),
		else:
			print('人物年齡: (無)')
		missing.append('人物')

	# 分析死法
	all_approach = detect_approach(all_post[0])
	if len(all_approach) == 1:
		approach = all_approach[0]
		print('死亡方式: {}'.format(approach))
		sql = 'UPDATE unluckyhouse SET approach=? WHERE id=?'
		con.execute(sql, (approach, topic_id))

		# 區別主動性
		initative = 'S'
		if approach in ('火災', '猝死', 'CO中毒'):
			initative = 'A'
		if approach in ('凌虐', '絞死', '槍殺', '凶殺'):
			initative = 'M'
		sql = 'UPDATE unluckyhouse SET initative=? WHERE id=?'
		con.execute(sql, (initative, topic_id))
		print('主動性: %s' % initative)
	else:
		if len(all_approach) > 0:
			print('死亡方式: {} (需要人工處理)'.format(','.join(all_approach)))
		else:
			print('死亡方式: (無)')
			missing.append('死亡方式')

	# 分析新聞連結 (看主文所有回應)
	news_link = detect_news('\n'.join(all_post))
	if news_link is not False:
		print('新聞連結: {}'.format(news_link))
		sql = 'UPDATE unluckyhouse SET news=? WHERE id=?'
		con.execute(sql, (news_link, topic_id))
	else:
		missing.append('新聞')

	# 分析地址 (看所有回應及標題)
	all_clues = all_post[1:]
	all_clues.append(subject)

	for clue in all_clues:
		full_address = detect_address(clue)
		if full_address != False:
			break

	if full_address is not False:
		(area, address) = full_address
		print('案發地址: {} / {}'.format(area, address))
		sql = 'UPDATE unluckyhouse SET area=?, address=? WHERE id=?'
		con.execute(sql, (area, address, topic_id))
	else:
		print('案發地址: (無)')
		missing.append('地址')

	# 分析案發時間 (只看主文)
	dt = detect_datetime(all_post[0])
	if dt != False:
		print('案發時間: {}'.format(dt))
		sql = 'UPDATE unluckyhouse SET datetime=? WHERE id=?'
		con.execute(sql, (dt, topic_id))
	else:
		missing.append('案發時間')

	# 最後摘要
	if len(missing) == 0:
		sql = 'UPDATE unluckyhouse SET state=1 WHERE id=?'
		con.execute(sql, (topic_id,))
		print('***** 資料完整，不需要人工處理 *****')
	else:
		print('***** 缺少 ({}) 欄位 *****'.format(','.join(missing)))

	con.commit()

def main():
	# 取得未處理清單
	# unluckyhouse.state=0
	ROW_LIMIT    = 100
	LATEST_LIMIT = 11399
	BASE_LIMIT   = 11300
	sql = 'SELECT id FROM unluckyhouse WHERE state=0 AND id>=? AND id<=? ORDER BY id DESC LIMIT ?'
	con = smart_dbapi.connect('unluckyhouse.sqlite')
	cur = con.execute(sql, (BASE_LIMIT, LATEST_LIMIT, ROW_LIMIT))

	todolist = []
	for row in cur:
		todolist.append(row['id'])
	print('分析範圍: {} ~ {}'.format(todolist[0], todolist[-1]))
	print('*' * 50)

	cur.close()

	# 使用 BeautifulSoup 4 分析文章
	# http://unluckyhouse.com/archive/index.php/t-%d.html
	url = 'http://unluckyhouse.com/archive/index.php/t-{}.html'

	for t in todolist:
		# 同步最新文章時，限制編號下限
		if t < BASE_LIMIT:
			break
		try:
			soup = smart_http.get(url.format(t))
			if soup != False:
				analyze(con, t, soup)
			else:
				con.execute('UPDATE unluckyhouse SET state=-1 WHERE id=?', (t,))
				print('主題 %d 已刪除' % t)
			del soup
		except Exception as e:
			print('分析文章 #{} 過程發生錯誤'.format(t))
			print('前往 URL 確認吧: {}'.format(url.format(t)))
			print('-' * 50)
			traceback.print_exc()
			print('-' * 50)
			break

	con.commit()
	con.close()

if __name__ == '__main__':
	main()

#!../../../bin/python
# coding: utf-8

import os
import re
import sys
import geojson

commons_path = os.path.realpath('../../commons')
sys.path.insert(1, commons_path)

import smart_dbapi

DEBUG = False

sql = 'SELECT * FROM unluckylabor WHERE lat>20 ORDER BY id'
if DEBUG:
	sql = sql + ' LIMIT 10'

con = smart_dbapi.connect('unluckylabor.sqlite')
cur = con.execute(sql)

features = []
for row in cur:
	# 違反法律條文格式化
	law_list = row['law'].split(';')
	law_desc = ''
	for e in law_list:
		if law_desc != '':
			law_desc = law_desc + '\n'

		m = re.match('(\d+)\-(\d+)', e)
		if m is not None:
			law_desc = law_desc + '勞動基準法第%s條第%s項' % (m.group(1), m.group(2))
		else:
			law_desc = law_desc + '勞動基準法第%s條' % e

	point = geojson.Point((row['lng'], row['lat']))
	properties = {
		'doc_id': row['doc_id'],
		'corp':   row['corp'],
		'dt_exe': row['dt_exe'],
		'law':    law_desc,
		'boss':   row['boss'],
		'addr':   row['addr'],
		'marker-color': '#b00000',
		'marker-symbol': 'danger'
	}
	features.append(geojson.Feature(geometry=point, properties=properties))

cur.close()
con.close()

fc = geojson.FeatureCollection(features)

if DEBUG:
	print(geojson.dumps(fc, indent=2, ensure_ascii=False))
else:
	print(geojson.dumps(fc))

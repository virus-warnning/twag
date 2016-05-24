#!../../../bin/python
# coding: utf-8

import os
import sys
import geojson

commons_path = os.path.realpath('../../commons')
sys.path.insert(1, commons_path)

import smart_dbapi

sql = 'SELECT * FROM unluckylabor WHERE lat>20 ORDER BY id'
con = smart_dbapi.connect('unluckylabor.sqlite')
cur = con.execute(sql)

features = []
for row in cur:
	point = geojson.Point((row['lng'], row['lat']))
	properties = {
		'id': row['exe_id'],
		'detail': row['detail'],
		'date': row['exe_date']
	}
	features.append(geojson.Feature(geometry=point, properties=properties))

cur.close()
con.close()

fc = geojson.FeatureCollection(features)
print(geojson.dumps(fc, indent=3))

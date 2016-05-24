#!../../../bin/python
# coding: utf-8

import json
import os
import sys

commons_path = os.path.realpath('../../commons')
sys.path.insert(1, commons_path)

import smart_dbapi

# 單筆資料轉 geojson 格式
def row_to_geojson(row):
	geojson = {
		'type': 'Feature',
		"geometry": {
			"type": "Point",
			"coordinates": [row["lng"], row["lat"]]
		},
		"properties": {
			"id": row["id"],
			"address": row["area"] + row["address"],
			"marker-color": "#b00000",
			"marker-symbol": "danger"
		}
	}

	# 死法
	INITATIVE_TAGS = {"A": u"意外", "S": u"自殺", "M": u"他殺"}
	approach = "%s %s" % (INITATIVE_TAGS[row["initative"]], row["approach"])
	geojson["properties"]["approach"] = approach

	# 選擇性欄位
	# - 日期 (7401)
	# - 新聞 (7016)
	for field in ["news", "datetime"]:
		if row[field] is not None and row[field] != "":
			geojson["properties"][field] = row[field]

	return geojson

sql = 'SELECT * FROM unluckyhouse WHERE state>1 ORDER BY id DESC'
con = smart_dbapi.connect('unluckyhouse.sqlite')
cur = con.execute(sql)

entries = {
	"type": "FeatureCollection",
	"features": []
}

for row in cur:
	entries["features"].append(row_to_geojson(row))

cur.close()
con.close()

print(json.dumps(entries, indent=2))

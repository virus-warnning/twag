# coding: utf-8

import re
import time
import smart_http

# 匿名處理 Geocode
def geocode(address):
	params = {'address': address}
	resp   = smart_http.request('maps.googleapis.com', '/maps/api/geocode/json', params)
	if resp != False and resp['status'] == 'OK':
		loc = resp['results'][0]['geometry']['location']
		return (loc['lat'], loc['lng'])
	return False

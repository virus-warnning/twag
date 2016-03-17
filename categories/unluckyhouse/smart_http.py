# coding: utf-8

import httplib
import urllib
import json

DEBUG = False

try:
	from bs4 import BeautifulSoup
	BS4_INSTALLED = True
except ImportError, e:
	BS4_INSTALLED = False

try:
	from lxml import etree
	LXML_INSTALLED = True
except ImportError:
	import xml.etree.ElementTree as etree
	LXML_INSTALLED = False

## 智慧型 HTTP Request
# application/json => dict
# text/xml         => lxml.etree._Element, xml.etree.ElementTree.Element
# text/html        => bs4.BeautifulSoup, str
# otherwise        => str
def request(host, uri, params=None, method='GET'):
	content = False

	try:
		conn = httplib.HTTPConnection(host)
		if type(params) is dict:
			# 避免使用 unicode 型態的字串，可能導致 urllib 跳出 Exception
			np = {}
			for k, v in params.iteritems():
				if type(k) is unicode:
					k = k.encode('utf-8')
				if type(v) is unicode:
					v = v.encode('utf-8')
				np[k] = v

			# 參數編碼後送出
			payloads = urllib.urlencode(np)
			if method == 'GET':
				conn.request(method, uri + '?' + payloads)
			else:
				conn.request(method, uri, payloads)
		else:
			conn.request(method, uri)

		resp = conn.getresponse()
		if resp.status == 200:
			content = resp.read()
			if len(content)>0:
				ctype = resp.getheader('Content-Type', 'text/plain; charset=UTF-8')
				if '/json' in ctype:
					content = json.loads(content)
				if '/xml' in ctype:
					content = etree.fromstring(content)
				if BS4_INSTALLED:
					if '/html' in ctype:
						if LXML_INSTALLED:
							content = BeautifulSoup(content, 'lxml')
						else:
							content = BeautifulSoup(content, 'html.parser')
			else:
				content = False
				if DEBUG: print('Response 200 OK but content is empty.')
		else:
			if DEBUG: print('Response Code: %d' % resp.status)

		conn.close()
	except Exception as e:
		if DEBUG: print(e)

	if DEBUG: print('%s.%s' % (type(content).__module__, type(content).__name__))

	return content

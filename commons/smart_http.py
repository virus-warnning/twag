import json
import requests
import urllib.parse
import logging.config

logger = logging.getLogger(__name__)

# 偵測 bs4 是否已安裝
try:
	from bs4 import BeautifulSoup
	BS4_INSTALLED = True
except ImportError:
	logging.warn('bs4 is not installed.')
	BS4_INSTALLED = False

# 選擇 etree
try:
	from lxml import etree
	LXML_INSTALLED = True
except ImportError:
	logging.warn('lxml is not installed.')
	import xml.etree.ElementTree as etree
	LXML_INSTALLED = False

## 智慧型 HTTP Request
# application/json => dict
# text/xml         => lxml.etree._Element, xml.etree.ElementTree.Element
# text/html        => bs4.BeautifulSoup, str
# otherwise        => str
def get(url, params=None):
	content = False

	try:
		resp = requests.get(url, params=params)
		logger.debug('HTTP Response: {}'.format(resp.status_code))
		for (k, v) in resp.headers.items():
			logger.debug('>> {}: {}'.format(k, v))

		if resp.status_code == 200:
			ctype = resp.headers['Content-Type']

			# text/*
			if ctype.startswith('text/'):
				# text/xml
				if '/xml' in ctype:
					content = etree.fromstring(resp.text)

				# text/html
				if '/html' in ctype and BS4_INSTALLED:
					if len(resp.text) > 0:
						if LXML_INSTALLED:
							content = BeautifulSoup(resp.text, 'lxml')
						else:
							content = BeautifulSoup(resp.text, 'html.parser')

				# otherwise
				if not content and len(resp.text) > 0:
					content = resp.text

			# application/json
			if ctype == 'application/json':
				content = resp.json()
		else:
			logger.error('Cannot get URL {}.'.format(url))
	except Exception as ex:
		logger.error(ex)

	return content

if __name__ == '__main__':
	resp = get('https://unluckyhouse.com/external.php')
	print(type(resp))

#!/usr/bin/python 
# coding=utf-8

import sys
import time
import urllib2
import re
import simplejson as json
import threading

g_okcoin_ltc = False
g_fxbtc_ltc = False
g_exit_flag = False

def http_get(url):
	req = urllib2.Request(url)
	res = urllib2.urlopen(req, timeout=10)
	content = res.read()
	return content

class OkCoin(threading.Thread):
	def __init__(self):
		self.url = "https://www.okcoin.com"
		self.pattern = re.compile(r'LTC : ￥<span id="bannerLtcLast">(\d+)<\/span>')

		super(OkCoin, self).__init__()
	
	def get_ltc(self):
		try:
			content = http_get(self.url)
			match = self.pattern.search(content)
			if match:
				return match.group(1)
		except:
			pass
		return False

	def run(self):
		global g_okcoin_ltc
		while not g_exit_flag:
			g_okcoin_ltc = self.get_ltc()
			#print "okcoin", price
			time.sleep(1)
		pass

class FxBtc(threading.Thread):
	def __init__(self):
		self.url = "https://data.fxbtc.com/api?op=query_ticker&symbol=ltc_cny"
		super(FxBtc, self).__init__()

	def get_ltc(self):
		try:
			content = http_get(self.url)
			ret = json.loads(content)
			return ret['ticker']['last_rate']
		except:
			pass
		return False

	def run(self):
		global g_fxbtc_ltc
		while not g_exit_flag:
			g_fxbtc_ltc = self.get_ltc()
			#print "fxbtc", price
			time.sleep(1)

def main():
	okcoin = OkCoin()
	okcoin.daemon = True
	okcoin.start()

	fxbtc = FxBtc()
	fxbtc.daemon = True
	fxbtc.start()

	while True:
		print "okcoin: ", g_okcoin_ltc, "fxbtc: ", g_fxbtc_ltc
		#sys.stdout.write("okcoin: %s, fxbtc: %s             \r" % (str(g_okcoin_ltc),str(g_fxbtc_ltc)))
		#sys.stdout.flush()
		time.sleep(1)
	okcoin.join()
	fxbtc.join()

if __name__ == '__main__':
	main()

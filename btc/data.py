#!/usr/bin/python 
# coding=utf-8

import sys
import time
import urllib2
import re
import simplejson as json
import datetime
from StringIO import StringIO
import gzip

def colored(s, c):
	cs = dict({
		'green': '\033[92m',
		'red':'\033[91m',
	})
	endc = '\033[0m'
	return '%s%s%s' % (cs[c], s, endc)

def http_get(url):
	req = urllib2.Request(url)
	req.add_header('Accept-encoding', 'gzip')
	res = urllib2.urlopen(req, timeout=20)
	content = res.read()
	if res.info().get('Content-Encoding') == 'gzip':
		buf = StringIO(content)
		f = gzip.GzipFile(fileobj=buf)
		content = f.read()
	return content

class OkCoin():
	def __init__(self):
		self._min = 1000.0
		self._max = 0.0
		pass

	def get(self, url):
		try:
			content = http_get(url)
			ret = json.loads(content)
			return ret
		except:
			pass
		return False

	def trades(self, symbol, since = None):
		if since:
			url = 'https://www.okcoin.com/api/trades.do?symbol=%s&since=%d' % (symbol, since)
		else:
			url = 'https://www.okcoin.com/api/trades.do?symbol=%s' % (symbol)
		data = self.get(url)
		return data

	def ltc(self, start, end):
		since = start
		step = 120
		while since < end:
			data = self.trades('ltc_cny', since)
			if data:
				self._print(data)
			since += step
		pass

	def realtime(self):
		since = None
		while True:
			data = self.trades('ltc_cny')
			if data:
				since = self._print(data, since)
			time.sleep(1)
		pass

	def _print(self, data, last = None, cond = True):
		for trade in data:
			if last and trade['tid'] <= last:
				continue
			t = datetime.datetime.fromtimestamp(trade['date']).strftime('%Y-%m-%d %H:%M:%S')
			price = float(trade['price'])
			if price < self._min:
				self._min = price
			elif price > self._max:
				self._max = price
			sys.stdout.write("\x1b]2;%.2f     [%.2f,%.2f]\x07" % (price, self._min, self._max))
			#if float(price) > 135:
			#	continue
			amount = trade['amount']
			content = '[%d][%s] %.2f\t%s' % (trade['tid'], t, price, amount)
			if float(amount) >= 100:
				content = colored(content, 'red')
			print content
		return trade['tid']

def main():
	#since = int(sys.argv[1])
	
	okcoin = OkCoin()

	#okcoin.ltc(since, since+10000)
	okcoin.realtime()


if __name__ == '__main__':
	main()

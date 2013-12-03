#!/usr/bin/python 
# coding=utf-8

import sys
import time
import urllib2
import re
import simplejson as json
import datetime

def colored(s, c):
	cs = dict({
		'green': '\033[92m',
		'red':'\033[91m',
	})
	endc = '\033[0m'
	return '%s%s%s' % (cs[c], s, endc)

def http_get(url):
	req = urllib2.Request(url)
	res = urllib2.urlopen(req, timeout=10)
	content = res.read()
	return content

class OkCoin():
	def __init__(self):
		pass

	def get(self, url):
		try:
			content = http_get(url)
			ret = json.loads(content)
			return ret
		except:
			pass
		return False

	def trades(self, symbol, since):
		url = 'https://www.okcoin.com/api/trades.do?symbol=%s&since=%d' % (symbol, since)
		data = self.get(url)
		return data

	def ltc(self, start, end):
		since = start
		step = 120
		while since < end:
			data = self.trades('ltc_cny', since)
			for trade in data:
				t = datetime.datetime.fromtimestamp(trade['date']).strftime('%Y-%m-%d %H:%M:%S')
				price = trade['price']
				if float(price) > 135:
					continue
				amount = trade['amount']
				content = '[%d][%s] %s\t%s' % (trade['tid'], t, price, amount)
				if float(amount) >= 100:
					content = colored(content, 'red')
				print content
			since += step
		pass


def main():
	since = int(sys.argv[1])
	
	okcoin = OkCoin()

	okcoin.ltc(since, since+10000)


if __name__ == '__main__':
	main()

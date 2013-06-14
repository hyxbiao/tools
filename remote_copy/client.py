#!/bin/env python
# coding=utf-8

__author__="xuanbiao@baidu.com"

import os
import socket
import struct
import sys

from optparse import OptionParser

class Remote:
	CMD_UNKNOWN = 0
	CMD_SEND_FILE = 1
	CMD_RECV_FILE = 2

	CONTENT_HEAD_LEN = 8

	def __init__(self, host, port):
		self.host = host
		self.port = port
		print host, port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def connect(self):
		self.sock.connect((self.host, self.port))
	
	def close(self):
		self.sock.close()
	
	def sendHead(self, cmd, file1, file2):
		head = struct.pack('III', cmd, len(file1), len(file2))
		self.sock.send(head)
		self.sock.send(file1)
		self.sock.send(file2)

	def sendFile(self, file1, file2):
		file1 = os.path.abspath(os.path.expanduser(file1))
		if not os.path.isfile(file1):
			print 'file: %s is not a file' % (file1)
			return False

		self.sendHead(Remote.CMD_SEND_FILE, file1, file2)

		content_len = os.path.getsize(file1)
		content_head = struct.pack('Q', content_len)
		self.sock.send(content_head)
		fp = open(file1, 'rb')
		while True:
			data = fp.read(1024)
			if not data:
				break
			#print data
			self.sock.send(data)
		fp.close()
		return True

	def recvFile(self, file1, file2):
		file2 = os.path.abspath(os.path.expanduser(file2))
		if os.path.isdir(file2):
			basename = os.path.basename(file1)
			outfile = os.path.join(file2, basename)
		elif os.path.isdir(os.path.dirname(file2)):
			outfile = file2
		else:
			print 'no the file or directory: %s' % (file2)
			return False

		self.sendHead(Remote.CMD_RECV_FILE, file1, file2)

		content_head = self.sock.recv(Remote.CONTENT_HEAD_LEN)
		content_len = struct.unpack("Q", content_head)
		print 'content length: %d' % (content_len)
		recv_len = 0
		fp = open(outfile, 'wb')
		while recv_len <= content_len:
			data = self.sock.recv(1024)
			if not data:
				break
			fp.write(data)
			recv_len += len(data)
		fp.close()

if __name__ == '__main__':

	usage = 'usage: %prog [option] [host1:]file1 [host2:]file2'
	parser = OptionParser(usage=usage, version='%prog 1.0')
	parser.add_option('-p', '--port', dest='port', type='int', default=8035, help='port [default: %default]')
	opt, argv = parser.parse_args()

	if len(argv) != 2:
		parser.print_help()
		sys.exit(1)

	x0, x1 = ':' in argv[0], ':' in argv[1]
	if x0 and x1:
		print 'only support one remote host'
		sys.exit(1)

	if x0:
		host, file1 = argv[0].split(':')
		file2 = argv[1]
	elif x1:
		file1 = argv[0]
		host, file2 = argv[1].split(':')
	else:
		file1 = argv[0]
		file2 = argv[1]
		#host = 'localhost'
		host = socket.gethostbyname(socket.gethostname())

	print 'host: %s, port: %d' % (host, opt.port)
	remote = Remote(host, opt.port)
	remote.connect()
	if x0:
		remote.recvFile(file1, file2)
	else:
		remote.sendFile(file1, file2)
	remote.close()


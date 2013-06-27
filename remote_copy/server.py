#!/bin/env python
# coding=utf-8

__author__="xuanbiao@baidu.com"


import os
import sys
import socket
import struct
import time

from optparse import OptionParser

HEAD_LEN = 12
CONTENT_HEAD_LEN = 8
CMD_SEND_FILE = 1
CMD_RECV_FILE = 2

if __name__ == '__main__':
	usage = 'usage: %prog [option]'
	parser = OptionParser(usage=usage, version='%prog 1.0')
	parser.add_option('-t', '--host', dest='host', default=None, help='host')
	parser.add_option('-p', '--port', dest='port', type='int', default=8035, help='port [default: %default]')
	opt, argv = parser.parse_args()

	if len(argv) > 0:
		parser.print_help()
		sys.exit(1)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	if opt.host:
		local_ip = opt.host
	else:
		local_ip = socket.gethostbyname(socket.gethostname())
	print 'host: %s, port: %d' % (local_ip, opt.port)
	sock.bind((local_ip, opt.port))

	sock.listen(5)

	while True:
		conn, addr = sock.accept()
		try:
			conn.settimeout(5)
			head = conn.recv(HEAD_LEN)
			cmd, file1_len, file2_len = struct.unpack("III", head)
			file1 = conn.recv(file1_len)
			file2 = conn.recv(file2_len)
			print 'cmd: %d, file1: %s, file2: %s' % (cmd, file1, file2)
			if cmd == CMD_SEND_FILE:
				file2 = os.path.abspath(os.path.expanduser(file2))
				if os.path.isdir(file2):
					basename = os.path.basename(file1)
					outfile = os.path.join(file2, basename)
				elif os.path.isdir(os.path.dirname(file2)):
					outfile = file2
				else:
					print 'no the file or directory: %s' % (file2)
					sys.exit(1)
				content_head = conn.recv(CONTENT_HEAD_LEN)
				content_len = struct.unpack("Q", content_head)
				print 'content length: %d' % (content_len)
				recv_len = 0
				fp = open(outfile, 'wb')
				while recv_len <= content_len:
					data = conn.recv(1024)
					if not data:
						break
					fp.write(data)
					recv_len += len(data)
				fp.close()
			elif cmd == CMD_RECV_FILE:
				file1 = os.path.abspath(os.path.expanduser(file1))
				if not os.path.isfile(file1):
					print 'file: %s is not a file' % (file1)
					sys.exit(1)
				content_len = os.path.getsize(file1)
				content_head = struct.pack('Q', content_len)
				conn.send(content_head)
				fp = open(file1, 'rb')
				while True:
					data = fp.read(1024)
					if not data:
						break
					conn.send(data)
				fp.close()
				pass
			else:
				print 'cmd: %d not support' % cmd
				sys.exit(1)
			pass
		except socket.timeout:
			print 'time out'
		except Exception, e:
			print e

		#print 'close connection sock'
		conn.close()
		break


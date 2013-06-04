#!/bin/env python
# coding=utf-8

__author__="xuanbiao@baidu.com"


import os
import socket
import struct
import time

HEAD_LEN = 8

if __name__ == '__main__':
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	sock.bind(('localhost', 8041))

	sock.listen(5)

	while True:
		conn, addr = sock.accept()
		try:
			conn.settimeout(5)
			head = conn.recv(HEAD_LEN)
			path_len, content_len = struct.unpack("ii", head)
			print 'path_len: %d, content_len: %d' % (path_len, content_len)
			dst_path = conn.recv(path_len)
			print 'dest path: %s' % dst_path
			recv_len = 0
			content = ''
			fp = open(dst_path, 'wb')
			while recv_len <= content_len:
				data = conn.recv(1024)
				if not data:
					break
				fp.write(data)
				content += data
				recv_len += len(data)
			fp.close()
			#print content
			pass
		except socket.timeout:
			print 'time out'

		conn.close()
		break

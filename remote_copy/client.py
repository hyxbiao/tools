#!/bin/env python
# coding=utf-8

__author__="xuanbiao@baidu.com"

import os
import socket
import struct
import sys

if __name__ == '__main__':

	filename = sys.argv[1]
	host, dst_path = sys.argv[2].split(':')

	basename = os.path.basename(filename)
	full_path = os.path.join(dst_path, basename)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	sock.connect((host, 8035))

	content_len = os.path.getsize(filename)
	head = struct.pack('ii', len(full_path), content_len)
	sock.send(head)
	sock.send(full_path)
	fp = open(filename, 'rb')
	while True:
		data = fp.read(1024)
		if not data:
			break
		#print data
		sock.send(data)
	fp.close()

	sock.close()

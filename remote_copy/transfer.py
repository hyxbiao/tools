#!/bin/env python
# coding=utf-8

import os
import socket
import struct
import sys

from optparse import OptionParser

class Transfer(object):
    CMD_UNKNOWN     = 0
    CMD_SEND_FILE   = 1
    CMD_RECV_FILE   = 2
    CMD_CLOSE       = 3

    TYPE_FILE       = 1
    TYPE_DIR        = 2

    HEAD_LEN        = 12
    TYPE_HEAD_LEN   = 8
    CONTENT_HEAD_LEN = 12

    def __init__(self):
        pass

    def writeHead(self, sock, cmd, file1, file2):
        head = struct.pack('III', cmd, len(file1), len(file2))
        sock.send(head)
        sock.send(file1)
        sock.send(file2)

    def get_local_file(self, local_file, relative_path):
        local_file = os.path.abspath(os.path.expanduser(local_file))
        if os.path.isdir(local_file):
            return os.path.join(local_file, relative_path)
        elif os.path.isdir(os.path.dirname(local_file)):
            return local_file
        print 'no the file or directory: %s' % (local_file)
        sys.exit(1)

    def read_file(self, conn, filename):
        local_file = os.path.abspath(os.path.expanduser(filename))
        if os.path.isdir(local_file):
            total_files = [len(files) for _, _, files in os.walk(local_file)]
            total_files = sum(total_files)
            conn.send(struct.pack('II', self.TYPE_DIR, total_files))
            for root, dirs, files in os.walk(local_file):
                for name in files:
                    filename = os.path.join(root, name)
                    dirname = os.path.dirname(local_file)
                    relative_path = filename[len(dirname) + 1:]
                    self._read_file(conn, filename, relative_path)
        elif os.path.isfile(local_file):
            conn.send(struct.pack('II', self.TYPE_FILE, 1))
            relative_path = os.path.basename(local_file)
            return self._read_file(conn, local_file, relative_path)
        else:
            print 'path: %s is not a file' % (local_file)
            sys.exit(1)

    def write_file(self, conn, filename, remote_file):
        type_head = conn.recv(self.TYPE_HEAD_LEN)
        ftype, total_files = struct.unpack("II", type_head)

        if ftype == self.TYPE_FILE:
            self._write_file(conn, filename)
        elif ftype == self.TYPE_DIR:
            for i in range(total_files):
                self._write_file(conn, filename)

    def _read_file(self, conn, filename, relative_path):
        content_len = os.path.getsize(filename)
        content_head = struct.pack('QI', content_len, len(relative_path))
        conn.send(content_head)
        conn.send(relative_path)
        with open(filename, 'rb') as fp:
            #self.transfer(fp, conn, content_len)
            while True:
                data = fp.read(1024)
                if not data:
                    break
                conn.send(data)

    def _write_file(self, conn, filename):
        content_head = conn.recv(self.CONTENT_HEAD_LEN)
        content_len, file_length = struct.unpack("QI", content_head)
        remote_relative_path = conn.recv(file_length)
        local_file = self.get_local_file(filename, remote_relative_path)
        dirname = os.path.dirname(local_file)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        print 'local file: {}, content length: {}'.format(local_file, content_len)
        with open(local_file, 'wb') as fp:
            self.transfer(conn, fp, content_len)

    def transfer(self, readfp, writefp, length):
        left = length
        while left > 0:
            read_cnt = min(left, 1024)
            data = readfp.recv(read_cnt)
            if not data:
                break
            writefp.write(data)
            left -= len(data)


class Server(Transfer):
    def __init__(self, host, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if host:
            self.host = host
        else:
            self.host = socket.gethostbyname(socket.gethostname())
        print 'host: %s, port: %d' % (self.host, self.port)
        self.sock.bind((self.host, self.port))

    def start(self):
        self.sock.listen(5)
        conn, addr = self.sock.accept()
        conn.settimeout(5)

        while True:
            try:
                head = conn.recv(self.HEAD_LEN)
                cmd, file1_len, file2_len = struct.unpack("III", head)
                client_file = conn.recv(file1_len)
                server_file = conn.recv(file2_len)
                print 'cmd: %d, client_file: %s, server_file: %s' % (cmd, client_file, server_file)
                if cmd == self.CMD_SEND_FILE:
                    self.write_file(conn, server_file, client_file)
                elif cmd == self.CMD_RECV_FILE:
                    self.read_file(conn, server_file)
                else:
                    print 'cmd: %d not support' % cmd
                    sys.exit(1)
            except socket.timeout:
                print 'time out'
            except Exception, e:
                print e
            print 'close connection sock'
            conn.close()
            break


class Client(Transfer):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        print host, port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.host, self.port))

    def close(self):
        self.sock.close()

    def sendFile(self, client_file, server_file):
        self.writeHead(self.sock, self.CMD_SEND_FILE, client_file, server_file)
        self.read_file(self.sock, client_file)

    def recvFile(self, server_file, client_file):
        self.writeHead(self.sock, self.CMD_RECV_FILE, client_file, server_file)
        try:
            self.write_file(self.sock, client_file, server_file)
        except socket.timeout:
            print 'time out'
        except Exception, e:
            print e


def run_client(opt, argv):
    if len(argv) != 2:
        parser.print_help()
        sys.exit(1)

    src_in_remote, dst_in_remote = ':' in argv[0], ':' in argv[1]
    if src_in_remote and dst_in_remote:
        print 'only support one remote host'
        sys.exit(1)

    if src_in_remote:
        host, server_file = argv[0].split(':')
        client_file = argv[1]
    elif dst_in_remote:
        client_file = argv[0]
        host, server_file = argv[1].split(':')
    else:
        client_file = argv[0]
        server_file = argv[1]
        #host = 'localhost'
        host = socket.gethostbyname(socket.gethostname())

    print 'host: %s, port: %d' % (host, opt.port)
    client = Client(host, opt.port)
    client.connect()
    if src_in_remote:
        client.recvFile(server_file, client_file)
    else:
        client.sendFile(client_file, server_file)
    client.close()

def run_server(opt, argv):
    if len(argv) > 0:
            parser.print_help()
            sys.exit(1)

    server = Server(opt.host, opt.port)
    server.start()

def main():
    usage = 'usage: %prog [option] [host1:]file1 [host2:]file2'
    parser = OptionParser(usage=usage, version='%prog 1.0')
    parser.add_option('-m', '--mode', dest='mode', default='client', help='mode: client or server [default: %default]')
    parser.add_option('-t', '--host', dest='host', default=None, help='host')
    parser.add_option('-p', '--port', dest='port', type='int', default=8035, help='port [default: %default]')
    opt, argv = parser.parse_args()

    if opt.mode == 'client':
        run_client(opt, argv)
    else:
        run_server(opt, argv)

if __name__ == '__main__':
    main()


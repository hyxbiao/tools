#!/usr/bin/env python
# coding=utf-8

import struct
import os

def debug(data):
    print ":".join(c.encode('hex') for c in data)

def macd(EMA_S, EMA_L, DEA, closeq, S=12, L=26, M=9):
    rS = S + 1
    rL = L + 1
    rM = M + 1
    rEMA_S = EMA_S + (closeq - EMA_S) * 2 / rS
    rEMA_L = EMA_L + (closeq - EMA_L) * 2 / rL
    rDIFF = rEMA_S - rEMA_L
    rDEA = DEA * 0.8 + rDIFF * 0.2
    rBAR = 2 * (rDIFF - rDEA)

    return rEMA_S, rEMA_L, rDIFF, rDEA, rBAR

def kdj(data, K, D, N=9, M1=3, M2=3):
    datalen = len(data)

    mins = 100000.0
    maxs = 0.0
    for item in data[-N:]:
        mins = min(mins, item[3])
        maxs = max(maxs, item[2])

    rRSV = 100 * (data[-1][4] - mins) / (maxs - mins)
    if datalen == 1:
        rK = rRSV
        rD = rRSV
    else:
        rK = float(M1-1)/M1 * K + 1.0/M1 * rRSV
        rD = float(M2-1)/M2 * D + 1.0/M2 * rK
    rJ = 3 * rK - 2 * rD

    return rK, rD, rJ

class BaseFormat(object):
    def __init__(self, filename):
        self.filename = filename
        self.rawdata = None

    def readRawData(self, mode = 0):
        with open(self.filename, 'rb') as f:
            #head
            type_s = struct.unpack('6c', f.read(6))
            debug(type_s)
            length = 4 + 2 + 2 + 2
            (count, start, clen, col_count)  = struct.unpack('IHHH', f.read(length))
            print count, start, clen, col_count

            #column
            col_length = col_count * 4
            cols_f = struct.unpack('%dI' % col_count, f.read(col_length))

            if mode == 1:
                #填充区域 = 2 * col_count
                tmp_length = col_count * 2
                f.read(tmp_length)

                #复合索引数据块
                idx_total_len, idx_count = struct.unpack('HH', f.read(4))
                print idx_total_len, idx_count
                idx_len = 18
                for i in xrange(10):
                    itype, isym, iunuse_count, iridx, icount = struct.unpack('B9sHIH', f.read(idx_len))
                    isym = isym.rstrip('\0')
                    print itype, isym, iunuse_count, iridx, icount
            
            #content
            f.seek(start)
            self.rawdata = f.read(long(count) * clen)
            f.close()

        return count, clen

class Finance(BaseFormat):
    def __init__(self, filename):
        super(Finance, self).__init__(filename)

    def readData(self):
        count, clen = self.readRawData(1)

        print count, clen
        
class Minute(BaseFormat):
    def __init__(self, filename):
        super(Minute, self).__init__(filename)

    def readData(self):
        count, clen = self.readRawData()
            
        data = []
        for i in xrange(0, count):
            pos = i * clen
            cols = struct.unpack('7I', self.rawdata[pos: pos+28])
            min_s = cols[0] & 0x3F
            hour_s = (cols[0] >> 6) & 0x1F
            day_s = (cols[0] >> 11) & 0x1F
            mon_s = (cols[0] >> 16) & 0xF
            year_s = ((cols[0] >> 20) & 0xFFF) + 1900

            openq = float(cols[1] & 0xFFFF) / 1000
            high = float(cols[2] & 0xFFFF) / 1000
            low = float(cols[3] & 0xFFFF) / 1000
            closeq = float(cols[4] & 0xFFFF) / 1000
            money = float(cols[5] & 0xFFFFFFF) / 1000
            volume = float(cols[6] & 0xFFFFFFF) / 100
            date = '%04d%02d%02d %02d:%02d' % (year_s, mon_s, day_s, hour_s, min_s)
            print date, openq, high, low, closeq, money, volume
            
class Day(BaseFormat):
    def __init__(self, filename):
        super(Day, self).__init__(filename)
        self.day_num = 30

    def readData(self):
        count, clen = self.readRawData()

        data = []
        start = count - self.day_num if count>=self.day_num else 0
        #start = 0
        for i in xrange(start, count):
            pos = i * clen
            cols = struct.unpack('7I', self.rawdata[pos: pos+28])
            date = cols[0]
            openq = float(cols[1] & 0xFFFF) / 1000
            high = float(cols[2] & 0xFFFF) / 1000
            low = float(cols[3] & 0xFFFF) / 1000
            closeq = float(cols[4] & 0xFFFF) / 1000
            money = float(cols[5] & 0xFFFFFFF) / 100
            volume = float(cols[6] & 0xFFFFFFF) / 10

            
            data.append([date, openq, high, low, closeq, money, volume])

            if i == start:
                EMA12 = closeq
                EMA26 = closeq
                DIFF = 0.0
                DEA = 0.0
                BAR = 0.0

                K = 50.0
                D = 50.0
            else:
                #if date != 20150524:
                #    continue
                EMA12, EMA26, DIFF, DEA, BAR = macd(EMA12, EMA26, DEA, closeq)

            
            K, D, J = kdj(data, K, D)

            print i, date, openq, high, low, closeq, money, volume
            print EMA12, EMA26, DIFF, DEA, BAR
            print K, D, J
            print '-----------------------------'
        
def main():
    #filename = '600030.day'
    #filename = '600030.min'
    filename = '股本结构.财经'
    #filename = unicode(filename , "utf-8")

    ext = os.path.splitext(filename)[1]
    if ext == '.day':
        m = Day(filename)
    elif ext == '.min':
        m = Minute(filename)
    elif ext == '.财经':
        m = Finance(unicode(filename, 'utf-8'))
    else:
        return
    m.readData()
    
if __name__ == '__main__':
    main()

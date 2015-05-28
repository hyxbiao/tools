#!/usr/bin/env python
# coding=utf-8

import struct

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

    print rK, rD, rJ
    return rK, rD, rJ

def main():
    filename = '600030.day'
    #filename = unicode(filename , "utf-8")

    with open(filename, 'rb') as f:
        head = struct.unpack('6c', f.read(6))
        debug(head)
        length = 4 + 2 + 2 + 2
        (count, start, clen, col_count)  = struct.unpack('IHHH', f.read(length))
        print count, start, clen, col_count

        col_length = col_count * 4
        cols_f = struct.unpack('%dI' % col_count, f.read(col_length))
        f.seek(start)

        rawdata = f.read(count * clen)
        f.close()

    data = []
    for i in xrange(count):
        pos = i * clen
        cols = struct.unpack('7I', rawdata[pos: pos+28])
        date = cols[0]
        openq = float(cols[1] & 0xFFFFFF) / 1000
        high = float(cols[2] & 0xFFFFFF) / 1000
        low = float(cols[3] & 0xFFFFFF) / 1000
        closeq = float(cols[4] & 0xFFFFFF) / 1000
        money = float(cols[5] & 0xFFFFFF) / 1000
        volume = float(cols[6] & 0xFFFFFF) / 1000

        data.append([date, openq, high, low, closeq, money, volume])
        print date, openq, high, low, closeq, money, volume
        if i == 0:
            EMA12 = closeq
            EMA26 = closeq
            DEA = 0.0

            K = 50.0
            D = 50.0
        else:
            EMA12, EMA26, DIFF, DEA, BAR = macd(EMA12, EMA26, DEA, closeq)
            
            print EMA12, EMA26, DIFF, DEA, BAR

        K, D, J = kdj(data, K, D)
        print '-----------------------------'

        f.close()
    print 'test'
    
if __name__ == '__main__':
    main()

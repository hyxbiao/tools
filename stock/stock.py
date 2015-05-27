# coding=utf-8

import struct

def debug(data):
    print ":".join(c.encode('hex') for c in data)
    
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

        DIFF = 0.0
        DEA = 0.0
        MACD = 0.0
        for i in xrange(count):
            cols = struct.unpack('%dI' % col_count, f.read(clen))
            date = cols[0]
            openq = float(cols[1] & 0xFFFFFF) / 1000
            high = float(cols[2] & 0xFFFFFF) / 1000
            low = float(cols[3] & 0xFFFFFF) / 1000
            closeq = float(cols[4] & 0xFFFFFF) / 1000
            money = float(cols[5] & 0xFFFFFF) / 1000
            volume = float(cols[6] & 0xFFFFFF) / 1000
            
            print date, openq, high, low, closeq, money, volume
            if i == 0:
                EMA12 = closeq
                EMA26 = closeq
            else:
                EMA12 = EMA12 + (closeq - EMA12) * 2 / 13
                EMA26 = EMA26 + (closeq - EMA26) * 2 / 27
                DIFF = EMA12 - EMA26
                DEA = DEA * 0.8 + DIFF * 0.2
                BAR = 2 * (DIFF - DEA)
                
                print EMA12, EMA26, DIFF, DEA, BAR

            print '-----------------------------'

        f.close()
    print 'test'
    
if __name__ == '__main__':
    main()

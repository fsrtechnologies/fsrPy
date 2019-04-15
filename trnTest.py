#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Marc
#
# Created:     01/10/2015
# Copyright:   (c) Marc 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from fsrStuff.umFuncs import parseDirectDat, RecordGenerator, BBBB2money
class Global(object):
    pass

def loadDirect():
    Global.offices      = parseDirectDat("e:\\ultramed\direct.dat")

def main():
    loadDirect()
    for num, off in Global.offices.iteritems():
        for obj in RecordGenerator(off, "Transaction"):
            if obj.ChartNumber == '14498.0':
                if obj.ExtChg:
                    print '{}{}.{:03d}'.format(obj.ChartNumber, obj.Date, obj.SeqNum), obj.Diag3, obj.Diag4
                else:
                    print '{}{}.{:03d}'.format(obj.ChartNumber, obj.Date, obj.SeqNum), obj.ProcCode, obj.Diag1, obj.Diag2
if __name__ == '__main__':
    main()

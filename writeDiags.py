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
import os.path
from fsrStuff.umFuncs import parseDirectDat, RecordGenerator, BBBB2money
class Global(object):
    pass

def main():
    with open(i10Name, 'r') as i10File:
        i10Lines = i10File.readlines()
        i10Lines.pop(0)
    with open(outName, 'w+b') as outFile:
        outFile.write(bytearray(b'\x00'*90))  #Plan to throw one away
        outFile.write(bytearray(b'\x00'*90))  #Well, two actually.
        for obj in RecordGenerator(office, "Diagnosis"):
            outRec = bytearray(b'\x00'*90)
            outRec[0] = outRec[-1] = b'\x01'
            outRec[5:11]  = obj.ID.ljust(6)
            outRec[12:52] = obj.Description.ljust(40)
            if obj.DotFormat:
                outRec[53] = b'\01'
                outRec[54:60] = obj.ICD.ljust(6)
            else:
                outRec[53:60] = obj.ICD.ljust(7)
            outFile.write(outRec)
        for line in i10Lines:
            outRec = bytearray(b'\x00'*90)
            outRec[0] = outRec[-1] = b'\x01'
            outRec[5:11]  = line[:6]
            outRec[12:52] = line[9:49]
            outRec[53:60] = line[54:61]
            outFile.write(outRec)

if __name__ == '__main__':
    offices = parseDirectDat("e:\\ultramed\direct.dat")
    office = offices['01']
    outName = os.path.join(os.path.expanduser("~"),"Desktop","01dia.dat")
    i10Name = os.path.join(os.path.expanduser("~"),"Desktop","KamICD10.txt")
    main()

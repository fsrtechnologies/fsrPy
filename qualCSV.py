#-------------------------------------------------------------------------------
# Name:        qualExport
# Purpose:     Export UltraMed info to CSV for DrChrono
#
# Author:      Marc
#
# Created:     11/14/2018
# Copyright:   (c) Marc 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, zipfile, csv
from datetime import datetime
from decimal import *
from fsrStuff.umFuncs import RecordGenerator, parseDirectDat
from fsrStuff.NPIFile import NPIFile

class Global(object):
    umDrive = 'E:'
    umDir = 'UltraMed'
    offNum = '04'
    docsToDo = ['18','19']
    startDate = '20171231'
    endDate = '20190101'
    chgDates = {}
    newPats  = {}
    allPats  = {}

class mmExport(object):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","qual","qual.csv")
    fieldnames = ['example']
    def __init__(self):
        self.items = []
        self.Pat = {}
        self.Appt = {}
        self.offices = parseDirectDat(os.path.join(Global.umDrive, os.sep, Global.umDir, "direct.dat"))
        self.offices = { num: off for num, off in self.offices.items() if num == Global.offNum }

    def cvtToCSV(self):
        with open(self.csvFile, 'w') as outFile:
            writer = csv.DictWriter(outFile, self.fieldnames, quoting = csv.QUOTE_ALL, lineterminator='\n')
            writer.writeheader()
            writer.writerows(self.items)

    def insPlan(self, FC, insCo):
        insPlan = ""
        if FC == "01":   return "Medicare"
        elif FC == "02": return  "Medi-Cal"
        elif FC == "03": return  "Medi-Medi"
        else:
            try:
                return self.Ins[insCo]
            except KeyError:
                return insCo

class Tran(mmExport):
    def __init__(self):
        self.MostRecentChg = ''

    def loadData(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            for obj in RecordGenerator(off, "TransactionDt"):
                countIn += 1
                if (obj.Valid):
                    #print(obj.Date, Global.startDate, Global.endDate)
                    if (obj.Date > Global.startDate) and (obj.Date < Global.endDate):
                        try:
                            if obj.Date > Global.chgDates[obj.ChartNumber]:
                                Global.chgDates[obj.ChartNumber] = obj.Date
                        except KeyError:
                                Global.chgDates[obj.ChartNumber] = obj.Date


class Demo(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","qual", "Demo.csv")
    fieldnames =   ["LastName", "FirstName", "MI",
                    "DOB", "Sex"]

    def __init__(self):
        self.LastName = ''
        self.FirstName = ''
        self.Birthdate = ''

    def loadData(self, doc='01'):
        mmExport.__init__(self)
        self.csvFile=os.path.join(os.path.expanduser("~"),"Desktop","qual", "Doc18-19.csv")
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            for obj in RecordGenerator(off, "Patient"):
                countIn += 1
                if (obj.Valid and obj.Doctor in Global.docsToDo):
                    try:
                        tmpDate = Global.chgDates[obj.ChartNumber]
                        countOut += 1
                        prettyDOB = obj.Birthdate[4:6] + '/' + obj.Birthdate[-2:] + '/' + obj.Birthdate[:4]
                        line = {"LastName": obj.LastName,
                                "FirstName": obj.FirstName,
                                "MI": obj.MI,
                                "DOB": prettyDOB,
                                "Sex": obj.Sex}
                        self.items.append(line)
                    except KeyError:
                        pass


if __name__ == '__main__':
    charges = Tran()
    charges.loadData()
    pats = Demo()
    pats.loadData()
    pats.cvtToCSV()


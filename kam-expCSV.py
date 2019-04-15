#-------------------------------------------------------------------------------
# Name:        KaminskyExport
# Purpose:     Export UltraMed info to CSV
#
# Author:      Marc
#
# Created:     17 Jan 2018
# Copyright:   (c) Marc 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, zipfile, csv
from datetime import datetime
from decimal import *
from fsrStuff import fixDate
from fsrStuff.umFuncs import RecordGenerator, parseDirectDat
from fsrStuff.NPIFile import NPIFile

class Global(object):
    umDrive = 'E:'
    umDir = 'Ultramed'
    offNum = '03'
    docsToDo = ['41']
    startDate = '20170101'
    endDate = '20171231'

class Bunch(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class mmExport(object):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","Export.csv")
    fieldnames = ['example']
    def __init__(self):
        self.items = []
        self.Ins = {}
        self.Doc = {}
        self.Proc = {}
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


class Insurance(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","kam", "Insurance.csv")
    fieldnames = ["ID", "Name", "Street", "Address1", "City", "State", "Zip", "Tel", "Contact"]
    def __init__(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            count = 0
            for obj in RecordGenerator(off, "Insurance"):
                if (obj.Valid):
                    count += 1
                    line = {"ID":obj.ID,
                            "Name":obj.Name,
                            "Street":obj.Street,
                            "Address1":obj.Address1,
                            "City":obj.City,
                            "State":obj.State,
                            "Zip":obj.Zip,
                            "Tel":obj.Tel,
                            "Contact":obj.Contact}
                    self.items.append(line)
                    if not count % 1000: print(count)

class Referral(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","kam", "Referral.csv")
    fieldnames = ["ID","Company", "LastName", "FirstName", "MI"]
    def __init__(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            count = 0
            for obj in RecordGenerator(off, "ReferralSource"):
                if (obj.Valid):
                    count += 1
                    line = {"ID":obj.ID,
                            "Company":obj.Company,
                            "LastName":obj.LastName,
                            "FirstName":obj.FirstName,
                            "MI":obj.MI}
                    self.items.append(line)
                    if not count % 1000: print(count)

class Demographics(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","kam", "Demographics.csv")
    fieldnames = ["LastName", "FirstName", "MI", "Address1", "Street", "City", "State", "Zip", "Birthdate", "Sex", "RefID","InsCompany", "InsuredID"]
    def __init__(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            for obj in RecordGenerator(off, "Insurance"):
                self.Ins[obj.ID] = obj.Name
            for obj in RecordGenerator(off, "Patient"):
                countIn += 1
                if (obj.Valid):
                    countOut += 1
                    line = {"LastName": obj.LastName,
                            "FirstName": obj.FirstName,
                            "MI": obj.MI,
                            "Address1": obj.Address1,
                            "Street": obj.Street,
                            "City": obj.City,
                            "State": obj.State,
                            "Zip": obj.Zip,
                            "Birthdate": obj.Birthdate,
                            "Sex": obj.Sex,
                            "RefID": obj.ReferredBy, 
                            "InsCompany": self.insPlan(obj.FinancialCategory, obj.PriInsCompany),
                            "InsuredID": obj.PriInsuredID}
                    self.items.append(line)
                if not countIn % 1000: print(countIn, countOut)

class Vizel(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","kam", "Vizel.csv")
    fieldnames = ["LastName", "FirstName", "MI", "DOB", "Sex"]
    def __init__(self):
        sex = {'M':'Male', 'F':'Female'}
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            pats = {}
            for obj in RecordGenerator(off, "TransactionD"):
                if obj.Valid and not obj.ExtChg and \
                        (obj.Doctor in Global.docsToDo) and (Global.startDate < obj.Date < Global.endDate):
                    pats[obj.ChartNumber] = obj.ChartNumber
            for obj in RecordGenerator(off, "Patient"):
                if (obj.Valid) and (obj.ChartNumber in pats) and (obj.FinancialCategory in ('01', '03')):
                    line = {"LastName": obj.LastName,
                            "FirstName": obj.FirstName,
                            "MI": obj.MI,
                            "DOB": fixDate(obj.Birthdate, spaces=False, slashes=True),
                            "Sex": sex[obj.Sex]}
                    self.items.append(line)


if __name__ == '__main__':

    for obj in (Vizel,):
        print("Starting " + obj.__name__ + "... ")
        thing = obj()
        thing.cvtToCSV()
        print("... finished")


#-------------------------------------------------------------------------------
# Name:        HonboExport
# Purpose:     Export UltraMed info to CSV for Cedars
#
# Author:      Marc
#
# Created:     14/05/2015
# Copyright:   (c) Marc 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, zipfile, csv
from datetime import datetime
from decimal import *
from fsrStuff.umFuncs import RecordGenerator, parseDirectDat
from fsrStuff.NPIFile import NPIFile

class Global(object):
    umDrive = 'E:'
    umDir = 'Ultramed'
    offNum = '01'
    docsToDo = ['01', '02']
    startDate = 20130101
    endDate = 20131231

class Bunch(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class mmExport(object):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","honbo","Honbo.csv")
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


class TestBed(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","honbo", "Testbed.csv")
    fieldnames = ["Pat", "Date", "Proc", "InsPlan", "InsBal", "SecBal", "PriAllow", "SecAllow", "TerAllow",
                    "PriAdj", "SecAdj", "TerAdj", "PatAdj"]
    def __init__(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            count = 0
            for obj in RecordGenerator(off, "Insurance"):
                self.Ins[obj.ID] = obj.Name
            for obj in RecordGenerator(off, "Transaction"):
                if ((obj.Valid) and (obj.KeyType == 'C') and (not obj.ExtChg) ):
                    count += 1
                    line = {"Pat": obj.ChartNumber,
                            "Date": obj.Date,
                            "Proc": obj.ProcCode,
                            "InsPlan": self.insPlan(obj.FC, obj.PriIns),
                            "InsBal": obj.InsBal,
                            "SecBal": obj.SecBal,
                            "PriAllow": obj.PriAllow,
                            "SecAllow": obj.SecAllow,
                            "TerAllow": obj.TerAllow,
                            "PriAdj": obj.PriAdj,
                            "SecAdj": obj.SecAdj,
                            "TerAdj": obj.TerAdj,
                            "PatAdj": obj.PatAdj}
                    self.items.append(line)
                    if count >= 1000: break

class Charges(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","honbo", "Charges.csv")
    fieldnames =   ["Date of Service", "Patient Number", "Physician", "Location", "Insurance Plan", "Original CPT Codes", "CPT",
                    "Modifiers", "Combined CPT (Final)", "Procedure Description", "Sum of Charges", "Sum of Payments", "Adjustments / Credits",
                    "Procedure Count", "Units / Quantity"]
    def __init__(self):
        mmExport.__init__(self)
        locDict = {11: "Office", 12: "Patient's Home", 21: "Inpatient Hospital", 22: "Outpatient Hospital",
                     81: "Independent Laboratory", 99: "Other"}
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            for obj in RecordGenerator(off, "Insurance"):
                self.Ins[obj.ID] = obj.Name
            for obj in RecordGenerator(off, "Doctor"):
                self.Doc[obj.ID] = obj.Name
            for obj in RecordGenerator(off, "Procedure"):
                self.Proc[obj.InHouseCode] = (obj.CPTCode, obj.Description1 + obj.Description2)
            for obj in RecordGenerator(off, "TransactionM"):
                countIn += 1
                if ((obj.Valid) and (obj.Doctor in Global.docsToDo) and (Global.startDate <= int(obj.Date) <= Global.endDate)):
                    countOut += 1
                    try:
                        totAdj = Decimal(obj.PriAdj) + Decimal(obj.SecAdj) + Decimal(obj.TerAdj) + Decimal(obj.PatAdj)
                        totBal = Decimal(obj.InsBal) + Decimal(obj.SecBal)
                        totPmt = Decimal(obj.Charge) - totAdj - totBal
                    except InvalidOperation:
                        print("Chart: {} Date: {} ProcCode: {}".format(obj.ChartNumber, obj.Date, obj.ProcCode))
                    line = {"Date of Service": datetime.strptime(obj.Date,'%Y%m%d').strftime('%m/%d/%Y'),
                            "Patient Number": obj.ChartNumber,
                            "Physician": self.Doc[obj.Doctor],
                            "Location": locDict[obj.Location],
                            "Insurance Plan": self.insPlan(obj.FC, obj.PriIns),
                            "Original CPT Codes": self.Proc[obj.ProcCode][0],
                            "CPT": self.Proc[obj.ProcCode][0],
                            "Modifiers": obj.Mod1 + obj.Mod2,
                            "Combined CPT (Final)": self.Proc[obj.ProcCode][0],
                            "Procedure Description": self.Proc[obj.ProcCode][1],
                            "Sum of Charges": obj.Charge,
                            "Sum of Payments": totPmt,
                            "Adjustments / Credits": totAdj,
                            "Procedure Count": 1,
                            "Units / Quantity": obj.Units}
                    self.items.append(line)
                if not countIn % 1000: print(countIn, countOut)



if __name__ == '__main__':
    fname = os.path.join(Global.umDrive, os.sep, Global.umDir, "npiMap.xml")
    Global.npiMap = NPIFile(fname)
    Global.npiMap.Load()

    for obj in (Charges, ):
        print("Starting " + obj.__name__ + "... ")
        thing = obj()
        thing.cvtToCSV()
        print("... finished")


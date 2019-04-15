#-------------------------------------------------------------------------------
# Name:        2017 MIPS #204
# Purpose:     Export UltraMed info to CSV
#
# Author:      Marc
#
# Created:     11 Feb 2018
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
    umDir = 'Ultramed'
    offNum = '02'
    docsToDo = ['45']
    startDate = '20170101'
    endDate = '20171231'

class Bunch(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class mmExport(object):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","MIPS204.csv")
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

    def insPlan(self, FC):
        insPlan = ""
        if FC in ("01", "03"): return "Yes"
        else: return  "Other"
        
    def maleFemale(self, Sex):
        if Sex == 'M': return 'Male'
        if Sex == 'F': return 'Female'
        return ''


class MIPS001(mmExport):
    print('001...')
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","MIPS", "001.csv")
    fieldnames = ["ATTENDING1_NAME","ATTENDING1_FIRST_NAME","ATTENDING1_NPI","ATTENDING1_TIN","ID_FAMILY_NAME","ID_GIVEN_NAME","ID_MIDDLE_NAME","DATE_OF_BIRTH","SEX","ID_LOCAL_PATIENT_ID","INSUR_FFS_MEDICARE","DT_VISIT_DIABETES","LAB_HEMOGLOBIN_A1C","DATETIME_LAB_DRAW","PQRS_1"]
    def __init__(self):
        mmExport.__init__(self)
        diagsIVD = ['250.00', '250.01', '250.02']
        Docs = {}
        Pats = {}
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            print('Doctor')
            for obj in RecordGenerator(off, "Doctor"):
                if obj.ID in Global.docsToDo:
                    TIN = obj.EIN
                    if TIN == "": TIN = obj.SSN
                    Docs[obj.ID] = [obj.LastName, obj.FirstName, obj.UPIN, TIN]
            print('Patients')
            count = 0
            for obj in RecordGenerator(off, "Patient"):
                count+=1
                Pats[obj.ChartNumber] = [obj.LastName, obj.FirstName, obj.MI, obj.Birthdate, self.maleFemale(obj.Sex), self.insPlan(obj.FinancialCategory)]
                if not count % 1000: print(count)
            print(count)
            print('Transactions')
            for obj in RecordGenerator(off, "TransactionD"):
                countIn += 1
                if obj.Valid and not obj.ExtChg and \
                        (obj.Doctor in Global.docsToDo) and (Global.startDate < obj.Date < Global.endDate) and \
                        ((obj.Diag1 in diagsIVD) or (obj.Diag2 in diagsIVD)):
                    countOut += 1
                    line = {"ATTENDING1_NAME": Docs[obj.Doctor][0],
                            "ATTENDING1_FIRST_NAME": Docs[obj.Doctor][1],
                            "ATTENDING1_NPI": Docs[obj.Doctor][2],
                            "ATTENDING1_TIN": Docs[obj.Doctor][3],
                            "ID_FAMILY_NAME": Pats[obj.ChartNumber][0],
                            "ID_GIVEN_NAME": Pats[obj.ChartNumber][1],
                            "ID_MIDDLE_NAME": Pats[obj.ChartNumber][2],
                            "DATE_OF_BIRTH": Pats[obj.ChartNumber][3],
                            "SEX": Pats[obj.ChartNumber][4],
                            "ID_LOCAL_PATIENT_ID": obj.ChartNumber,
                            "INSUR_FFS_MEDICARE": Pats[obj.ChartNumber][5],
                            "DT_VISIT_DIABETES": obj.Date,
                            "LAB_HEMOGLOBIN_A1C": "",
                            "DATETIME_LAB_DRAW": "",
                            "PQRS_1": ""}
                    self.items.append(line)
                if not countIn % 10000: print(countIn, countOut)
            print(countIn, countOut)
            
class MIPS204(mmExport):
    print('204...')
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","MIPS", "204.csv")
    fieldnames = ["ATTENDING1_NAME","ATTENDING1_FIRST_NAME","ATTENDING1_NPI","ATTENDING1_TIN","ID_FAMILY_NAME","ID_GIVEN_NAME","ID_MIDDLE_NAME","DATE_OF_BIRTH","SEX","ID_LOCAL_PATIENT_ID","INSUR_FFS_MEDICARE","DT_VISIT_204","ASPIRIN_FOR_IVD","PQRS_204"]
    def __init__(self):
        mmExport.__init__(self)
        diagsIVD = ['414.00', '440.9']
        Docs = {}
        patsToDo = ["0024287.0","0024497.0","0025134.0","0025251.0","0026213.0","0026343.0","0026445.0","0026521.0","0029076.0","0030271.0","0030971.0","0030973.0","0030974.0","0031009.0","0031011.0","0031077.0","0031079.0","0031258.0","0031263.0","0031287.0","0031329.0","0031355.0","0031471.0","0031528.0","0031585.0","0031616.0","0031687.0","0031689.0","0031715.0","0031737.0","0031746.0","0031876.0","0031931.0","0032197.0","0032209.0","0032214.0","0032222.0","0032264.0","0032304.0","0032305.0","0032306.0","0032340.0","0032348.0","0032355.0","0032360.0","0032361.0","0032378.0","0032379.0","0032380.0","0032382.0","0032386.0","0032395.0","0032398.0","0032401.0","0032409.0","0032410.0","0032411.0","0032413.0","0032423.0","0032426.0","0032433.0","0032439.0","0032441.0","0032443.0","0032444.0","0032445.0","0032447.0","0032448.0","0032450.0","07693.0","09611.0","11294.0"]
        Pats = {}
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            print('Doctor')
            for obj in RecordGenerator(off, "Doctor"):
                if obj.ID in Global.docsToDo:
                    TIN = obj.EIN
                    if TIN == "": TIN = obj.SSN
                    Docs[obj.ID] = [obj.LastName, obj.FirstName, obj.UPIN, TIN]
            print('Patients')
            count = 0
            for obj in RecordGenerator(off, "Patient"):
                count+=1
                Pats[obj.ChartNumber] = [obj.LastName, obj.FirstName, obj.MI, obj.Birthdate, self.maleFemale(obj.Sex), self.insPlan(obj.FinancialCategory)]
                if not count % 1000: print(count)
            print(count)
            print('Transactions')
            for obj in RecordGenerator(off, "TransactionD"):
                countIn += 1
                if obj.Valid and not obj.ExtChg and \
                        (obj.Doctor in Global.docsToDo) and (Global.startDate < obj.Date < Global.endDate) and \
                        (obj.ChartNumber in patsToDo):
                    countOut += 1
                    line = {"ATTENDING1_NAME": Docs[obj.Doctor][0],
                            "ATTENDING1_FIRST_NAME": Docs[obj.Doctor][1],
                            "ATTENDING1_NPI": Docs[obj.Doctor][2],
                            "ATTENDING1_TIN": Docs[obj.Doctor][3],
                            "ID_FAMILY_NAME": Pats[obj.ChartNumber][0],
                            "ID_GIVEN_NAME": Pats[obj.ChartNumber][1],
                            "ID_MIDDLE_NAME": Pats[obj.ChartNumber][2],
                            "DATE_OF_BIRTH": Pats[obj.ChartNumber][3],
                            "SEX": Pats[obj.ChartNumber][4],
                            "ID_LOCAL_PATIENT_ID": obj.ChartNumber,
                            "INSUR_FFS_MEDICARE": Pats[obj.ChartNumber][5],
                            "DT_VISIT_204": obj.Date,
                            "ASPIRIN_FOR_IVD": "",
                            "PQRS_204": ""}
                    self.items.append(line)
                if not countIn % 10000: print(countIn, countOut)
            print(countIn, countOut)
            
class MIPS236(mmExport):
    print('236...')
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","MIPS", "236.csv")
    fieldnames = ["ATTENDING1_NAME","ATTENDING1_FIRST_NAME","ATTENDING1_NPI","ATTENDING1_TIN","ID_FAMILY_NAME","ID_GIVEN_NAME","ID_MIDDLE_NAME","DATE_OF_BIRTH","SEX","ID_LOCAL_PATIENT_ID","INSUR_FFS_MEDICARE","DT_VISIT_236","BLOOD_PRESSURE_SYST_SIT","BLOOD_PRESSURE_DIAS_SIT","CONTROLLING_HIGH_BP","PQRS_236"]
    def __init__(self):
        mmExport.__init__(self)
        diagsIVD = ['414.00', '440.9']
        Docs = {}
        Pats = {}
        patsToDo = ["0024287.0","0024497.0","0025251.0","0026213.0","0026445.0","0029076.0","0030271.0","0030971.0","0030973.0","0030974.0","0031009.0","0031011.0","0031077.0","0031258.0","0031263.0","0031287.0","0031329.0","0031355.0","0031471.0","0031528.0","0031616.0","0031687.0","0031689.0","0031737.0","0031746.0","0031876.0","0032197.0","0032209.0","0032222.0","0032264.0","0032304.0","0032305.0","0032340.0","0032348.0","0032355.0","0032360.0","0032361.0","0032378.0","0032379.0","0032386.0","0032398.0","0032401.0","0032409.0","0032410.0","0032411.0","0032413.0","0032426.0","0032433.0","0032439.0","0032441.0","0032443.0","0032444.0","0032445.0","0032447.0","0032450.0","07693.0","09611.0","11294.0"]
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            print('Doctor')
            for obj in RecordGenerator(off, "Doctor"):
                if obj.ID in Global.docsToDo:
                    TIN = obj.EIN
                    if TIN == "": TIN = obj.SSN
                    Docs[obj.ID] = [obj.LastName, obj.FirstName, obj.UPIN, TIN]
            print('Patients')
            count = 0
            for obj in RecordGenerator(off, "Patient"):
                count+=1
                Pats[obj.ChartNumber] = [obj.LastName, obj.FirstName, obj.MI, obj.Birthdate, self.maleFemale(obj.Sex), self.insPlan(obj.FinancialCategory)]
                if not count % 1000: print(count)
            print(count)
            print('Transactions')
            for obj in RecordGenerator(off, "TransactionD"):
                countIn += 1
                if obj.Valid and not obj.ExtChg and \
                        (obj.Doctor in Global.docsToDo) and (Global.startDate < obj.Date < Global.endDate) and \
                        (obj.ChartNumber in patsToDo):
                    countOut += 1
                    line = {"ATTENDING1_NAME": Docs[obj.Doctor][0],
                            "ATTENDING1_FIRST_NAME": Docs[obj.Doctor][1],
                            "ATTENDING1_NPI": Docs[obj.Doctor][2],
                            "ATTENDING1_TIN": Docs[obj.Doctor][3],
                            "ID_FAMILY_NAME": Pats[obj.ChartNumber][0],
                            "ID_GIVEN_NAME": Pats[obj.ChartNumber][1],
                            "ID_MIDDLE_NAME": Pats[obj.ChartNumber][2],
                            "DATE_OF_BIRTH": Pats[obj.ChartNumber][3],
                            "SEX": Pats[obj.ChartNumber][4],
                            "ID_LOCAL_PATIENT_ID": obj.ChartNumber,
                            "INSUR_FFS_MEDICARE": Pats[obj.ChartNumber][5],
                            "DT_VISIT_236": obj.Date,
                            "BLOOD_PRESSURE_SYST_SIT": "",
                            "BLOOD_PRESSURE_DIAS_SIT": "",
                            "CONTROLLING_HIGH_BP": "",
                            "PQRS_236": ""}
                    self.items.append(line)
                if not countIn % 10000: print(countIn, countOut)
            print(countIn, countOut)
            
class MIPS317(mmExport):
    print('317...')
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","MIPS", "317.csv")
    fieldnames = ["ATTENDING1_NAME","ATTENDING1_FIRST_NAME","ATTENDING1_NPI","ATTENDING1_TIN","ID_FAMILY_NAME","ID_GIVEN_NAME","ID_MIDDLE_NAME","DATE_OF_BIRTH","SEX","ID_LOCAL_PATIENT_ID","INSUR_FFS_MEDICARE","DT_VISIT_317","PREV_HTN_SCREEN","PQRS_317"]
    def __init__(self):
        mmExport.__init__(self)
        diagsIVD = ['414.00', '440.9']
        Docs = {}
        Pats = {}
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            print('Doctor')
            for obj in RecordGenerator(off, "Doctor"):
                if obj.ID in Global.docsToDo:
                    TIN = obj.EIN
                    if TIN == "": TIN = obj.SSN
                    Docs[obj.ID] = [obj.LastName, obj.FirstName, obj.UPIN, TIN]
            print('Patients')
            count = 0
            for obj in RecordGenerator(off, "Patient"):
                count+=1
                Pats[obj.ChartNumber] = [obj.LastName, obj.FirstName, obj.MI, obj.Birthdate, self.maleFemale(obj.Sex), self.insPlan(obj.FinancialCategory)]
                if not count % 1000: print(count)
            print(count)
            print('Transactions')
            for obj in RecordGenerator(off, "TransactionD"):
                countIn += 1
                if obj.Valid and not obj.ExtChg and \
                        (obj.Doctor in Global.docsToDo) and (Global.startDate < obj.Date < Global.endDate) and \
                        (obj.ChartNumber in patsToDo):
                    countOut += 1
                    line = {"ATTENDING1_NAME": Docs[obj.Doctor][0],
                            "ATTENDING1_FIRST_NAME": Docs[obj.Doctor][1],
                            "ATTENDING1_NPI": Docs[obj.Doctor][2],
                            "ATTENDING1_TIN": Docs[obj.Doctor][3],
                            "ID_FAMILY_NAME": Pats[obj.ChartNumber][0],
                            "ID_GIVEN_NAME": Pats[obj.ChartNumber][1],
                            "ID_MIDDLE_NAME": Pats[obj.ChartNumber][2],
                            "DATE_OF_BIRTH": Pats[obj.ChartNumber][3],
                            "SEX": Pats[obj.ChartNumber][4],
                            "ID_LOCAL_PATIENT_ID": obj.ChartNumber,
                            "INSUR_FFS_MEDICARE": Pats[obj.ChartNumber][5],
                            "DT_VISIT_317": obj.Date,
                            "PREV_HTN_SCREEN": "",
                            "PQRS_317": ""}
                    self.items.append(line)
                if not countIn % 10000: print(countIn, countOut)
            print(countIn, countOut)
            
class MIPS326(mmExport):
    print('326...')
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","MIPS", "326.csv")
    fieldnames = ["ATTENDING1_NAME","ATTENDING1_FIRST_NAME","ATTENDING1_NPI","ATTENDING1_TIN","ID_FAMILY_NAME","ID_GIVEN_NAME","ID_MIDDLE_NAME","DATE_OF_BIRTH","SEX","ID_LOCAL_PATIENT_ID","INSUR_FFS_MEDICARE","DT_VISIT_326","ANTICOAGULANT_AFIB","PQRS_326"]
    def __init__(self):
        mmExport.__init__(self)
        diagsIVD = ['414.00', '440.9']
        Docs = {}
        Pats = {}
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            print('Doctor')
            for obj in RecordGenerator(off, "Doctor"):
                if obj.ID in Global.docsToDo:
                    TIN = obj.EIN
                    if TIN == "": TIN = obj.SSN
                    Docs[obj.ID] = [obj.LastName, obj.FirstName, obj.UPIN, TIN]
            print('Patients')
            count = 0
            for obj in RecordGenerator(off, "Patient"):
                count+=1
                Pats[obj.ChartNumber] = [obj.LastName, obj.FirstName, obj.MI, obj.Birthdate, self.maleFemale(obj.Sex), self.insPlan(obj.FinancialCategory)]
                if not count % 1000: print(count)
            print(count)
            print('Transactions')
            for obj in RecordGenerator(off, "TransactionD"):
                countIn += 1
                if obj.Valid and not obj.ExtChg and \
                        (obj.Doctor in Global.docsToDo) and (Global.startDate < obj.Date < Global.endDate) and \
                        (obj.ChartNumber in patsToDo):
                    countOut += 1
                    line = {"ATTENDING1_NAME": Docs[obj.Doctor][0],
                            "ATTENDING1_FIRST_NAME": Docs[obj.Doctor][1],
                            "ATTENDING1_NPI": Docs[obj.Doctor][2],
                            "ATTENDING1_TIN": Docs[obj.Doctor][3],
                            "ID_FAMILY_NAME": Pats[obj.ChartNumber][0],
                            "ID_GIVEN_NAME": Pats[obj.ChartNumber][1],
                            "ID_MIDDLE_NAME": Pats[obj.ChartNumber][2],
                            "DATE_OF_BIRTH": Pats[obj.ChartNumber][3],
                            "SEX": Pats[obj.ChartNumber][4],
                            "ID_LOCAL_PATIENT_ID": obj.ChartNumber,
                            "INSUR_FFS_MEDICARE": Pats[obj.ChartNumber][5],
                            "DT_VISIT_326": obj.Date,
                            "ANTICOAGULANT_AFIB": "",
                            "PQRS_326": ""}
                    self.items.append(line)
                if not countIn % 10000: print(countIn, countOut)
            print(countIn, countOut)
            
class MIPS438(mmExport):
    print('438...')
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","MIPS", "438.csv")
    fieldnames = ["ATTENDING1_NAME","ATTENDING1_FIRST_NAME","ATTENDING1_NPI","ATTENDING1_TIN","ID_FAMILY_NAME","ID_GIVEN_NAME","ID_MIDDLE_NAME","DATE_OF_BIRTH","SEX","ID_LOCAL_PATIENT_ID","INSUR_FFS_MEDICARE","DT_VISIT_438","STATIN_HIGH_RISK_CARDIO","PQRS_438"]
    def __init__(self):
        mmExport.__init__(self)
        diagsIVD = ['414.00', '440.9']
        Docs = {}
        Pats = {}
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            print('Doctor')
            for obj in RecordGenerator(off, "Doctor"):
                if obj.ID in Global.docsToDo:
                    TIN = obj.EIN
                    if TIN == "": TIN = obj.SSN
                    Docs[obj.ID] = [obj.LastName, obj.FirstName, obj.UPIN, TIN]
            print('Patients')
            count = 0
            for obj in RecordGenerator(off, "Patient"):
                count+=1
                Pats[obj.ChartNumber] = [obj.LastName, obj.FirstName, obj.MI, obj.Birthdate, self.maleFemale(obj.Sex), self.insPlan(obj.FinancialCategory)]
                if not count % 1000: print(count)
            print(count)
            print('Transactions')
            for obj in RecordGenerator(off, "TransactionD"):
                countIn += 1
                if obj.Valid and not obj.ExtChg and \
                        (obj.Doctor in Global.docsToDo) and (Global.startDate < obj.Date < Global.endDate) and \
                        (obj.ChartNumber in patsToDo):
                    countOut += 1
                    line = {"ATTENDING1_NAME": Docs[obj.Doctor][0],
                            "ATTENDING1_FIRST_NAME": Docs[obj.Doctor][1],
                            "ATTENDING1_NPI": Docs[obj.Doctor][2],
                            "ATTENDING1_TIN": Docs[obj.Doctor][3],
                            "ID_FAMILY_NAME": Pats[obj.ChartNumber][0],
                            "ID_GIVEN_NAME": Pats[obj.ChartNumber][1],
                            "ID_MIDDLE_NAME": Pats[obj.ChartNumber][2],
                            "DATE_OF_BIRTH": Pats[obj.ChartNumber][3],
                            "SEX": Pats[obj.ChartNumber][4],
                            "ID_LOCAL_PATIENT_ID": obj.ChartNumber,
                            "INSUR_FFS_MEDICARE": Pats[obj.ChartNumber][5],
                            "DT_VISIT_438": obj.Date,
                            "STATIN_HIGH_RISK_CARDIO": "",
                            "PQRS_438": ""}
                    self.items.append(line)
                if not countIn % 10000: print(countIn, countOut)
            print(countIn, countOut)
            

if __name__ == '__main__':

    for obj in (MIPS001, MIPS204, MIPS236, MIPS317, MIPS326, MIPS438 ):
        print("Starting " + obj.__name__ + "... ")
        thing = obj()
        thing.cvtToCSV()
        print("... finished")


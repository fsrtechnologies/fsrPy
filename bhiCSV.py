#-------------------------------------------------------------------------------
# Name:        BHIExport
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
    umDir = 'BHI'
    offNum = '01'
    docsToDo = ['02']
    startDate = 20130101
    endDate = 20131231
    chgDates = {}
    newPats  = {}
    allPats  = {}

class mmExport(object):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","bhi","bhi.csv")
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
            for obj in RecordGenerator(off, "TransactionM"):
                countIn += 1
                if (obj.Valid):
                    countOut += 1
                    try:
                        if obj.Date > Global.chgDates[obj.ChartNumber]:
                            Global.chgDates[obj.ChartNumber] = obj.Date
                    except KeyError:
                            Global.chgDates[obj.ChartNumber] = obj.Date


class Demo(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","bhi", "Demo.csv")
    fieldnames =   ["ChartNumber", "LastName", "FirstName", "MI",
                    "EntryDate",  "LatestChg",
                    "Address1", "Street", "City", "State", "Zip", "HomePhone",
                    "DrivLicNum", "SSN", "Birthdate", "Sex", "EmergContact",
                    "EmergPhone", "EmergRelCode", "Message1", "Message2",
                    "NrstRelName", "NrstRelStreet", "NrstRelCity", "NrstRelState",
                    "NrstRelZip", "NrstRelPhone", "NrstRelRelCode",
                    "EmpName", "EmpContact", "EmpStreet", "EmpCity", "EmpState",
                    "EmpZip", "EmpPhone", "EmpPhone2", "Doctor", "Diagnosis1",
                    "Diagnosis2", "Diagnosis3", "Diagnosis4",
                    "ReferredBy", "OtherRef1", "OtherRef2", "MaritalStatus",
                    "PriInsCompany", "PriInsuredID", "PriInsPlanName", "PriInsPolicy",
                    "SecInsCompany", "SecInsuredID", "SecInsPlanName", "SecInsPolicy",
                    "TerInsCompany", "TerInsuredID", "TerInsPlanName", "TerInsPolicy"]

    def __init__(self):
        self.LastName = ''
        self.FirstName = ''
        self.Birthdate = ''

    def loadData(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            for obj in RecordGenerator(off, "Patient"):
                countIn += 1
                if (obj.Valid and obj.Doctor in Global.docsToDo):
                    countOut += 1
                    prettyDOB = obj.Birthdate[4:6] + '/' + obj.Birthdate[-2:] + '/' + obj.Birthdate[:4]
                    try:
                        latest = Global.chgDates[obj.ChartNumber]
                    except KeyError: latest = ""
                    pat = {"first_name": obj.FirstName,
                            "last_name": obj.LastName,
                            "date_of_birth": prettyDOB}
                    Global.allPats[obj.ChartNumber] = pat
                    line = {"ChartNumber": obj.ChartNumber,
                            "LastName": obj.LastName,
                            "FirstName": obj.FirstName,
                            "MI": obj.MI,
                            "EntryDate": obj.EntryDate,
                            "LatestChg": latest,
                            "Address1": obj.Address1,
                            "Street": obj.Street,
                            "City": obj.City,
                            "State": obj.State,
                            "Zip": obj.Zip if int(obj.Zip) > 0 else '',
                            "HomePhone": obj.HomePhone,
                            "DrivLicNum": obj.DrivLicNum,
                            "SSN": obj.SSN  if int(obj.SSN) > 0 else '',
                            "Birthdate": prettyDOB,
                            "Sex": obj.Sex,
                            "EmergContact": obj.EmergContact,
                            "EmergPhone": obj.EmergPhone,
                            "EmergRelCode": obj.EmergRelCode,
                            "Message1": obj.Message1,
                            "Message2": obj.Message2,
                            "NrstRelName": obj.NrstRelName,
                            "NrstRelStreet": obj.NrstRelStreet,
                            "NrstRelCity": obj.NrstRelCity,
                            "NrstRelState": obj.NrstRelState,
                            "NrstRelZip": obj.NrstRelZip if int(obj.NrstRelZip) > 0 else '',
                            "NrstRelPhone": obj.NrstRelPhone,
                            "NrstRelRelCode": obj.NrstRelRelCode,
                            "EmpName": obj.EmpName,
                            "EmpContact": obj.EmpContact,
                            "EmpStreet": obj.EmpStreet,
                            "EmpCity": obj.EmpCity,
                            "EmpState": obj.EmpState,
                            "EmpZip": obj.EmpZip if int(obj.EmpZip) > 0 else '',
                            "EmpPhone": obj.EmpPhone,
                            "EmpPhone2": obj.EmpPhone2,
                            "Doctor": obj.Doctor,
                            "Diagnosis1": obj.Diagnosis1,
                            "Diagnosis2": obj.Diagnosis2,
                            "Diagnosis3": obj.Diagnosis3,
                            "Diagnosis4": obj.Diagnosis4,
                            "ReferredBy": obj.ReferredBy,
                            "OtherRef1": obj.OtherRef1,
                            "OtherRef2": obj.OtherRef2,
                            "MaritalStatus": obj.MaritalStatus,
                            "PriInsCompany": obj.PriInsCompany,
                            "PriInsuredID": obj.PriInsuredID if obj.PriInsuredID != '000-00-0000' else '',
                            "PriInsPlanName": obj.PriInsPlanName,
                            "PriInsPolicy": obj.PriInsPolicy,
                            "SecInsCompany": obj.SecInsCompany,
                            "SecInsuredID": obj.SecInsuredID,
                            "SecInsPlanName": obj.SecInsPlanName,
                            "SecInsPolicy": obj.SecInsPolicy,
                            "TerInsCompany": obj.TerInsCompany,
                            "TerInsuredID": obj.TerInsuredID,
                            "TerInsPlanName": obj.TerInsPlanName,
                            "TerInsPolicy": obj.TerInsPolicy}
                    self.items.append(line)
                if not countIn % 1000: print(countIn, countOut)

class Doctor(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","bhi", "Doctor.csv")
    fieldnames =   ["ID", "Name", "LastName", "FirstName", "MI", "Title",
                    "Street", "City", "State", "Zip", "Phone", "License",
                    "EIN", "SSN", "MedicareID", "UPIN",
                    "HomeStreet", "HomeCity", "HomeState", "HomeZip", "HomePhone",
                    "BirthDate"]
    def __init__(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            for obj in RecordGenerator(off, "Doctor"):
                countIn += 1
                if (obj.Valid):
                    countOut += 1
                    line = {"ID": obj.ID,
                            "Name": obj.Name,
                            "LastName": obj.LastName,
                            "FirstName": obj.FirstName,
                            "MI": obj.MI,
                            "Title": obj.Title,
                            "Street": obj.Street,
                            "City": obj.City,
                            "State": obj.State,
                            "Zip": obj.Zip if int(obj.Zip) > 0 else '',
                            "Phone": obj.Phone,
                            "License": obj.License,
                            "EIN": obj.EIN,
                            "SSN": obj.SSN,
                            "MedicareID":obj.MedicareID,
                            "UPIN": obj.UPIN,
                            "HomeStreet":obj.HomeStreet,
                            "HomeCity": obj.HomeCity,
                            "HomeState": obj.HomeState,
                            "HomeZip": obj.HomeZip,
                            "HomePhone": obj.HomePhone,
                            "BirthDate": obj.BirthDate}
                    self.items.append(line)
                if not countIn % 1000: print(countIn, countOut)

class Insurance(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","bhi", "Insurance.csv")
    fieldnames =   ["ID", "Name", "Street", "Address1", "City", "State", "Zip",
                    "Tel", "Contact"]
    def __init__(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            for obj in RecordGenerator(off, "Insurance"):
                countIn += 1
                if (obj.Valid):
                    countOut += 1
                    line = {"ID": obj.ID,
                            "Name": obj.Name,
                            "Street": obj.Street,
                            "Address1": obj.Address1,
                            "City": obj.City,
                            "State": obj.State,
                            "Zip": obj.Zip if int(obj.Zip) > 0 else '',
                            "Tel": obj.Tel,
                            "Contact": obj.Contact}
                    self.items.append(line)
                if not countIn % 1000: print(countIn, countOut)

class RefSrc(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","bhi", "RefSrc.csv")
    fieldnames =   ["ID", "Company", "Name", "Address", "Address1", "City", "State", "Zip",
                    "Phone", "LastName", "FirstName", "MI", "Fax"]
    def __init__(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            for obj in RecordGenerator(off, "ReferralSource"):
                countIn += 1
                if (obj.Valid):
                    countOut += 1
                    line = {"ID": obj.ID,
                            "Company": obj.Company,
                            "Name": obj.Name,
                            "Address": obj.Address,
                            "Address1": obj.Address1,
                            "City": obj.City,
                            "State": obj.State,
                            "Zip": obj.Zip if int(obj.Zip) > 0 else '',
                            "Phone": obj.Phone,
                            "LastName": obj.LastName,
                            "FirstName": obj.FirstName,
                            "MI": obj.MI,
                            "Fax": obj.Fax}
                    self.items.append(line)
                if not countIn % 1000: print(countIn, countOut)

class NewPat(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","bhi", "NewPat.csv")
    fieldnames =   ["NewPatNumber", "LastName", "FirstName", "MI",
                    "HomePhone", "WorkPhone", "WorkExt", "Address", "City",
                    "State", "Zip", "ReferredBy"]
    def __init__(self):
        self.LastName = ''
        self.FirstName = ''
        self.MI = ''
        self.HomePhone = ''
        self.WorkPhone = ''
        self.WorkExt = ''
        self.Address = ''
        self.City = ''
        self.State = ''
        self.Zip = ''
        self.ReferredBy = ''

    def loadData(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            for obj in RecordGenerator(off, "NewPatient"):
                countIn += 1
                if (obj.Valid and obj.LastName and obj.LastName[0].isalpha()
                    and obj.LastName[:3] not in ('AT ','DR ','DR.','G &','MJ ','NO ','OK ','ONL','PT ','rem','Rem','REM','RME','RWF','S A','SMC','smc','SX ','TGM')
                    and obj.LastName[:4] not in ('ANY ','APPT','FOR ','ISB ','MAC ','Marc','NBC ','NOT ','POLO','RED ','REEM','REF ','SAT ','VAL ','VALS')
                    and obj.LastName[:5] not in ("DON'T",'BOOK ','CLOSE','DONT ','DUMMY','FILM ','FROM ','lunch','LUNCH','MARIA','MOVE ','PARTY','PHONE','READ ','SEARS','START','TODAY')
                    and obj.LastName[:6] not in ('APPOIN','BOTOX ','CEDARS','CHECK ','CONFER','DO NOT','DUE TO','ELAINE','FRIEND','FRONT ','LASER ','MERCK ','OFFICE')
                    and obj.LastName[:7] not in ('BRENDA ','BROKER ','CLOSING','CONSULT','CONTACT','DENTIST','MEETING','MIRJANA','PATIENT','PLEASE ','SEMINAR','WEBINAR')
                    and obj.LastName[:8] not in ('COURTESY','MEMORIAL','TRAINING')
                    and obj.LastName[:9] not in ('IMPORTANT','INTERVIEW','MANAGEMEN','TELEPHONE')
                    ):
                    countOut += 1
                    line = {"NewPatNumber": obj.NewPatNumber,
                            "LastName": obj.LastName,
                            "FirstName": obj.FirstName,
                            "MI": obj.MI,
                            "HomePhone": obj.HomePhone,
                            "WorkPhone": obj.WorkPhone,
                            "WorkExt": obj.WorkExt if obj.WorkExt != '*' else '',
                            "Address": obj.Address,
                            "City": obj.City,
                            "State": obj.State,
                            "Zip": obj.Zip if int(obj.Zip) > 0 else '',
                            "ReferredBy": obj.ReferredBy}
                    Global.newPats[obj.NewPatNumber] = line
                    self.items.append(line)
                if not countIn % 1000: print(countIn, countOut)


class Appt(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","bhi", "Appt.csv")
    fieldnames = ["patient.first_name", "patient.last_name", "patient.date_of_birth",
                  "patient.chart_id", "office.name", "doctor", "scheduled_time",
                  "examination_room", "duration", "notes", "reason", "appointment_status"]
    def __init__(self):
        mmExport.__init__(self)
        for num, off in self.offices.iteritems():
            countIn = countOut = 0
            for obj in RecordGenerator(off, "Appointment"):
                countIn += 1
                if (obj.Valid and obj.SlotType == 4 and not obj.NewPatientYN and obj.DoctorNumber in Global.docsToDo):
                    try:
                        pat = Global.allPats[obj.ChartNumber]
                    except: continue
                    countOut += 1
                    line = {"patient.first_name": pat["first_name"],
                            "patient.last_name": pat["last_name"],
                            "patient.date_of_birth": pat["date_of_birth"],
                            "patient.chart_id": obj.ChartNumber,
                            "office.name": "TGM",
                            "doctor": obj.DoctorNumber,
                            "scheduled_time": obj.Date[:4] + '-' + obj.Date[4:6] + '-' + obj.Date[-2:] + ' ' + obj.MilTime + ':00',
                            "examination_room": "",
                            "duration": obj.Duration,
                            "notes": "",
                            "reason": obj.Alert,
                            "appointment_status": "Scheduled"}
                    self.items.append(line)
                if not countIn % 1000: print(countIn, countOut)


if __name__ == '__main__':
    charges = Tran()
    charges.loadData()
    pats = Demo()
    pats.loadData()
    pats.cvtToCSV()
    for obj in (Doctor, Insurance, RefSrc, Appt):
        print("Starting " + obj.__name__ + "... ")
        thing = obj()
        thing.cvtToCSV()
        print("... finished")


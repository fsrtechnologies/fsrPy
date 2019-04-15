#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Marc
#
# Created:     14/05/2015
# Copyright:   (c) Marc 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, zipfile, csv
from fsrStuff.umFuncs import RecordGenerator, parseDirectDat
from fsrStuff.NPIFile import NPIFile

class Global(object):
    umDrive = 'E:'
    umDir = 'Ultramed'
    offNum = '04'
    docsToDo = ['16', '21', '22', '23', '24', '25', '27']

class Bunch(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class mmExport(object):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "test.csv")
    fieldnames = ['example']
    def __init__(self):
        self.offices = parseDirectDat(os.path.join(Global.umDrive, os.sep, Global.umDir, "direct.dat"))
        self.offices = { num: off for num, off in self.offices.items() if num == Global.offNum }

    def cvtToCSV(self):
        with open(self.csvFile, 'w') as outFile:
            writer = csv.DictWriter(outFile, self.fieldnames, quoting = csv.QUOTE_ALL, lineterminator='\n')
            writer.writeheader()
            writer.writerows(self.items)



class Facility(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "Facility.csv")
    fieldnames =   ["ServiceFacilityName", "ServiceFacilityNPI", "ServiceFacilityTaxonomy",
                    "ServiceFacilityAddress1", "ServiceFacilityAddress2", "ServiceFacilityCity", "ServiceFacilityState", "ServiceFacilityZip",
                    "Contact", "Phone", "BillingName", "BillingTaxID", "BillingNPI", "BillingCLIA", "BillingTaxonomy",
                    "BillingAddress1", "BillingAddress2", "BillingCity", "BillingState", "BillingZip",
                    "BillingPayToAddress1", "BillingPayToAddress2", "BillingPayToCity", "BillinPayToState", "BillingPayToZip", "PlaceOfService", "Code"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        for num, off in self.offices.iteritems():
            B = Bunch()
            B.Name = 'Jim'
            for obj in RecordGenerator(off, "Misc"): # pre-load the "Billing" stuff to apply to all records in next step
                if obj.recType == 'OfficeInfo' and obj.PageNum == 1:
                    B.Name = obj.Name
                    B.TaxID = (obj.EIN if obj.EIN != '' else obj.SSN)
                    for legCode in (obj.License, obj.SSN, obj.EIN, obj.MedicareID, obj.MedicaidID, obj.BlueCrossID, obj.WorkCompID, obj.BlueShieldID, obj.OtherID1, obj.OtherID2):
                        code = Global.npiMap.lookup(legCode)
                        if code["NPI"] != '':
                            B.NPI = code["NPI"]
                    B.CLIA = obj.CLIA
                    B.Street = obj.Street
                    B.City = obj.City
                    B.State = obj.State
                    B.Zip = obj.Zip
            for obj in RecordGenerator(off, "Misc"):
                if obj.recType == 'OfficeInfo' and obj.Name != '':
                    npi = ''
                    for legCode in (obj.License, obj.SSN, obj.EIN, obj.MedicareID, obj.MedicaidID, obj.BlueCrossID, obj.WorkCompID, obj.BlueShieldID, obj.OtherID1, obj.OtherID2):
                        code = Global.npiMap.lookup(legCode)
                        if code["NPI"] != '':
                            npi = code["NPI"]
                    line = {"ServiceFacilityName": obj.Name, "ServiceFacilityNPI": (npi if npi != '' else "NPI"),
                            "ServiceFacilityAddress1": obj.Street, "ServiceFacilityCity": obj.City, "ServiceFacilityState": obj.State, "ServiceFacilityZip": obj.Zip,
                            "Phone": obj.Phone, "BillingName": B.Name, "BillingTaxID": B.TaxID, "BillingNPI": B.NPI, "BillingCLIA": B.CLIA,
                            "BillingAddress1": B.Street, "BillingCity": B.City, "BillingState": B.State, "BillingZip": B.Zip,
                            "BillingPayToAddress1": B.Street, "BillingPayToCity": B.City, "BillinPayToState": B.State, "BillingPayToZip": B.Zip}
                    self.items.append(line)



class FacilityLicenseDiagnosis(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "FacilityLicenseDiagnosis.csv")
    fieldnames = ["ICD Code", "Custom Description"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "Diagnosis"):
                line = {"ICD Code": obj.ICD, "Custom Description":obj.Description}
                self.items.append(line)



class FacilityLicensePayers(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "FacilityLicensePayers.csv")
    fieldnames =   ["PayerID", "FullName", "ShortName", "EMCID", "Class", "EnableElectronic",
                    "EnableElectronicSecondary", "BillAsProvider", "Address1", "Address2", "City", "State", "Zip",
                    "Comments", "AcceptsBenefits", "InstitutionalOrProfessionalPayer", "InsuranceType"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "Insurance"):
                line = {"PayerID": obj.ID, "FullName": obj.Name, "ShortName": obj.ID,
                        "Address1": obj.Street, "Address2": obj.Street, "City": obj.City, "State": obj.State,
                        "Zip": (obj.Zip if int(obj.Zip) > 0 else '')}
                self.items.append(line)



class FacilityLicenseReferrals(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "FacilityLicenseReferrals.csv")
    fieldnames =   ["FirstName", "MiddleName", "LastName", "DisplayName", "NPI", "Taxonomy",
                    "Address1", "Address2", "City", "State", "Zip", "Phone", "Fax", "Email", "Specialty", "Code"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "ReferralSource"):
                if obj.LastName != '':
                    if len(obj.UPIN) >0:
                        code = Global.npiMap.lookup(obj.UPIN)
                        npi = code["NPI"]
                    if npi == '' and isdigit(obj.Specialty):
                        npi = obj.Specialty  # some NPIs are stored in Specialty field
                    line = {"FirstName": obj.FirstName, "MiddleName": obj.MI, "LastName": obj.LastName, "DisplayName": obj.Name,
                            "NPI": (npi if npi != '' else "NPI"),
                            "Address1": obj.Address, "Address2": obj.Address1, "City": obj.City, "State": obj.State,
                            "Zip": (obj.Zip if int(obj.Zip) > 0 else ''),
                            "Phone": obj.Phone, "Fax": obj.Fax, "Code": obj.ID}
                    self.items.append(line)



class FacilityLicenseUsers(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "FacilityLicenseUsers.csv")
    fieldnames =   ["LoginName","Prefix","FirstName","MiddleName","LastName","Password","Suffix","Gender","SSN",
                    "DOB","HomePhone","CellPhone","WorkPhone","NPI","UPIN","DEA","DPS","Taxonomy","Address1","Address2",
                    "City","State","Zip"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "Doctor"):
                if obj.ID in Global.docsToDo:
                    npi = ''
                    for legCode in (obj.License, obj.SSN, obj.EIN, obj.MedicareID, obj.MedicaidID, obj.BlueCrossID, obj.WorkCompID, obj.BlueShieldID, obj.OtherID1, obj.OtherID2):
                        code = Global.npiMap.lookup(legCode)
                        if code["NPI"] != '':
                            npi = code["NPI"]
                    line = {"FirstName": obj.FirstName, "MiddleName": obj.MI, "LastName": obj.LastName, "SSN": obj.SSN, "DOB": (obj.BirthDate if obj.BirthDate > 0 else ''),
                            "HomePhone": obj.HomePhone, "WorkPhone": obj.Phone, "NPI": (npi if npi != '' else "NPI"), "UPIN": obj.UPIN, "DEA": obj.DEANumber,
                            "Taxonomy": obj.TaxonomyCode, "Address1": obj.Street, "City": obj.City, "State": obj.State, "Zip": obj.Zip}
                    self.items.append(line)



class FacilityOrders(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "FacilityOrders.csv")
    fieldnames =   ["CPT","FullCPTCode","CustomDescription","Category","Units","UnitQualifier","UnitPrice","Internal/External",
                    "Modifier1","Modifier2","Modifier3","Modifier4","ICD1","ICD2","ICD3","ICD4","NDC","NDCQualifier","NDCUnits",
                    "Alert","ShowOnSuperbill","ForceCPTToPatient","RelativeValue","Minutes","Keyword","UBRevCode","UBProcedure",
                    "UBCondition","Cost","OnHand","Used","ReorderPoint"]
    def __init__(self):
        mmExport.__init__(self)
        itemDict = {}
        self.items = []
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "Procedure"):
                if obj.Doctor in Global.docsToDo:
                    itemDict[obj.CPTCode] = {"CPT": obj.CPTCode, "FullCPTCode": obj.CPTCode, "CustomDescription": obj.Description1 + obj.Description2,
                            "Category": obj.Department, "Units": obj.AnesthUnits, "UnitPrice": obj.UsualCharge,
                            "Modifier1": obj.CPTModifier1, "Modifier2": obj.CPTModifier2, "ICD1": obj.DiagnosisLink,
                            "Minutes": obj.AnesthUnits, "Cost": obj.VendorCharge}
            for num, line in itemDict.iteritems():
                self.items.append(line)




class Patient(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "Patient.csv")
    fieldnames =   ["PTID", "PreFix", "FirstName", "MiddleName", "LastName","Suffix",
                    "SSN", "DOB", "HomePhone", "WorkPhone", "CellPhone", "E-Mail", "Gender",
                    "Race", "Ethnicity", "MaritalStatus", "EnableStatements", "PrimaryResource",
                    "PrimaryPhysician", "ReferringPhysician", "DefaultFacility", "DefaultLanguage",
                    "LastStatementDate", "LastSeenDate", "HIPAASigned", "ReleaseOfInformation",
                    "PreferredContactMethod", "SecondaryAccount"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "Patient"):
                if obj.Doctor in Global.docsToDo:
                    line = {"PTID": obj.ChartNumber, "FirstName": obj.FirstName, "MiddleName": obj.MI, "LastName": obj.LastName,
                            "SSN": obj.SSN, "DOB": obj.Birthdate, "HomePhone": obj.HomePhone, "WorkPhone": obj.EmpPhone,
                            "Gender": obj.Sex, "MaritalStatus": obj.MaritalStatus, "EnableStatements": ('Y' if obj.StatementCode == "Y" else 'N'),
                            "PrimaryPhysician": obj.Doctor, "ReferringPhysician": obj.ReferredBy}
                    self.items.append(line)


class PatientAddress(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "PatientAddress.csv")
    fieldnames =   ["PTID","Type","Address1","Address2","City","State","Zip"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "Patient"):
                if obj.Doctor in Global.docsToDo:
                    line = {"PTID": obj.ChartNumber, "Address1": obj.Street, "Address2": obj.Address1, "City": obj.City, "State": obj.State,
                                "Zip": (obj.Zip if int(obj.Zip) > 0 else '')}
                    self.items.append(line)



class PatientComments(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "PatientComments.csv")
    fieldnames = ["PTID", "Comment", "Date"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "Note"):
                line = {"PTID": obj.ChartNumber, "Comment": obj.Text, "Date": obj.EntryDate}
                self.items.append(line)


class PatientEmergencyContacts(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "PatientEmergencyContacts.csv")
    fieldnames = ["PTID", "Name", "Relationship", "HomePhone", "WorkPhone", "CellPhone"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "Patient"):
                if obj.Doctor in Global.docsToDo:
                    if obj.EmergContact != '':
                        line = {"PTID": obj.ChartNumber, "Name": obj.EmergContact, "Relationship": obj.EmergRelCode, "HomePhone": obj.EmergPhone}
                        self.items.append(line)



class PatientGuarantor(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "PatientGuarantor.csv")
    fieldnames = ["PTID","FirstName","MiddleName","LastName","SSN","DOB","Relationship","HomePhone","WorkPhone","Address1","Address2","City","State","Zip"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "Patient"):
                if obj.Doctor in Global.docsToDo:
                    line = {"PTID": obj.ChartNumber, "FirstName": obj.FirstName, "MiddleName": obj.MI, "LastName": obj.LastName,
                            "SSN": obj.SSN, "DOB": obj.Birthdate, "Relationship": 'Self', "HomePhone": obj.HomePhone, "WorkPhone": obj.EmpPhone,
                            "Address1": obj.Street, "Address2": obj.Address1, "City": obj.City, "State": obj.State, "Zip": (obj.Zip if int(obj.Zip) > 0 else '')}
                    self.items.append(line)



class PatientPayer(mmExport):
    csvFile=os.path.join(os.path.expanduser("~"),"Desktop","mmOut", "PatientPayer.csv")
    fieldnames = [  "PTPayerID", "PTID", "PayerID", "PayerName", "PolicyNumber", "GroupNumber",
                    "InsuranceType", "RelationshipToSubscriber", "SubscriberFirstName", "SubscriberMiddleName",
                    "SubscriberLastName", "SubscriberSuffix","SubscriberSSN", "SubscriberDOB",
                    "SubscriberGender", "SubscriberEmployer", "Copay", "Order", "CoverageStart", "CoverageEnd"]
    def __init__(self):
        mmExport.__init__(self)
        self.items = []
        self.Ins = {}
        self.Ind = {}
        self.Pat = {}
        relDict = {"0": "Self", "1": "Spouse", "2": "Child", "7": "Employee", "": "Self"}
        finDict = {"01": "Medicare", "02": "Medi-Cal", "03": "Medi-Medi", "04": "Private"}
        for num, off in self.offices.iteritems():
            for obj in RecordGenerator(off, "Insurance"):
                self.Ins[obj.ID] = obj.Name
            for obj in RecordGenerator(off, "InsuredParty"):
                self.Ind[obj.ChartNumber, obj.Rank] = (obj.LinkToChart, #0
                        obj.LastName, #1
                        obj.FirstName, #2
                        obj.MI, #3
                        obj.Street, #4
                        obj.City, #5
                        obj.State, #6
                        obj.Zip, #7
                        obj.HomePhone, #8
                        obj.Birthdate, #9
                        obj.Sex, #10
                        obj.Employer ) #11
            for obj in RecordGenerator(off, "Patient"):
                if obj.Doctor in Global.docsToDo:
                    self.Pat[obj.ChartNumber] = (obj.LastName,
                            obj.FirstName, #1
                            obj.MI, #2
                            obj.Street, #3
                            obj.City, #4
                            obj.State, #5
                            obj.Zip, #6
                            obj.HomePhone, #7
                            obj.SSN, #8
                            obj.Birthdate, #9
                            obj.Sex, #10
                            obj.FinancialCategory, #11
                            obj.EmpName, #12
                            obj.PriInsCompany, #13
                            obj.PriInsuredID, #14
                            obj.PriInsDeductible,#15
                            obj.PriInsCopay, #16
                            obj.PriInsPlanName, #17
                            obj.PriInsPolicy, #18
                            obj.PriInsuredRel, #19
                            obj.SecInsCompany, #20
                            obj.SecInsuredID, #21
                            obj.SecInsPlanName, #22
                            obj.SecInsPolicy, #23
                            obj.SecInsuredRel, #24
                            obj.TerInsCompany, #25
                            obj.TerInsuredID, #26
                            obj.TerInsPlanName, #27
                            obj.TerInsPolicy, #28
                            obj.TerInsuredRel) #29
            for chart, pat in self.Pat.iteritems():
                subsc = Bunch()
                ind = ["","","","","","","","","","","",""]
                def initSubsc(pat=pat):
                    subsc.LastName = pat[0]
                    subsc.FirstName = pat[1]
                    subsc.MI = pat[2]
                    subsc.SSN = pat[8]
                    subsc.DOB = pat[9]
                    subsc.Gender = pat[10]
                    subsc.Emp = pat[12]
                def overrideSubsc(ind=ind):
                    if ind[1]  != '': subsc.LastName = ind[1]
                    if ind[2]  != '': subsc.FirstName = ind[2]
                    if ind[3]  != '': subsc.MI = ind[3]
                    if ind[9] != '': subsc.DOB = ind[9]
                    if ind[10] != '': subsc.Gender = ind[10]
                    if ind[11] != '': subsc.Emp = ind[11]
                if pat[13] != '': #Primary insurance
                    initSubsc()
                    if (chart, '1') in self.Ind:
                        ind = self.Ind[chart, '1']
                        lnk = ind[0] # LinkToChart
                        if lnk != '':
                            initSubsc(pat=self.Pat[lnk])
                        else:
                            overrideSubsc()
                    line = {"PTID": chart, "PayerID": pat[13], "PayerName": self.Ins[pat[13]],
                            "PolicyNumber": pat[14], "GroupNumber": pat[18],
                            "InsuranceType": (finDict[pat[11]] if pat[11] in finDict else 'Other'),
                            "RelationshipToSubscriber": (relDict[pat[19]] if pat[19] in relDict else 'Other'),
                            "SubscriberFirstName": subsc.FirstName, "SubscriberMiddleName": subsc.MI,"SubscriberLastName": subsc.LastName,
                            "SubscriberSSN": subsc.SSN, "SubscriberDOB": subsc.DOB,
                            "SubscriberGender": subsc.Gender, "SubscriberEmployer": subsc.Emp, "Copay":pat[16], "Order": "Primary"}
                    self.items.append(line)
                if pat[20] != '': #Secondary insurance
                    initSubsc()
                    if (chart, '2') in self.Ind:
                        ind = self.Ind[chart, '2']
                        lnk = ind[0] # LinkToChart
                        if lnk != '':
                            initSubsc(pat=self.Pat[lnk])
                        else:
                            overrideSubsc()
                    line = {"PTID": chart, "PayerID": pat[20], "PayerName": self.Ins[pat[20]],
                            "PolicyNumber": pat[21], "GroupNumber": pat[23],
                            "InsuranceType": ('Medi-Medi' if pat[11] == '03' else ''), #not even going to try to guess any other types
                            "RelationshipToSubscriber": (relDict[pat[24]] if pat[24] in relDict else 'Other'),
                            "SubscriberFirstName": subsc.FirstName, "SubscriberMiddleName": subsc.MI,"SubscriberLastName": subsc.LastName,
                            "SubscriberSSN": subsc.SSN, "SubscriberDOB": subsc.DOB,
                            "SubscriberGender": subsc.Gender, "SubscriberEmployer": subsc.Emp, "Order": "Secondary"}
                    self.items.append(line)
                if pat[25] != '': #Tertiary insurance
                    initSubsc()
                    if (chart, '3') in self.Ind:
                        ind = self.Ind[chart, '3']
                        lnk = ind[0] # LinkToChart
                        if lnk != '':
                            initSubsc(pat=self.Pat[lnk])
                        else:
                            overrideSubsc()
                    line = {"PTID": chart, "PayerID": pat[25], "PayerName": self.Ins[pat[25]],
                            "PolicyNumber": pat[26], "GroupNumber": pat[28],
                            "RelationshipToSubscriber": (relDict[pat[29]] if pat[29] in relDict else 'Other'),
                            "SubscriberFirstName": subsc.FirstName, "SubscriberMiddleName": subsc.MI,"SubscriberLastName": subsc.LastName,
                            "SubscriberSSN": subsc.SSN, "SubscriberDOB": subsc.DOB,
                            "SubscriberGender": subsc.Gender, "SubscriberEmployer": subsc.Emp, "Order": "Tertiary"}
                    self.items.append(line)

if __name__ == '__main__':
    fname = os.path.join(Global.umDrive, os.sep, Global.umDir, "npiMap.xml")
    Global.npiMap = NPIFile(fname)
    Global.npiMap.Load()

    for obj in (Facility,
            FacilityLicenseDiagnosis,
            FacilityLicensePayers,
            FacilityLicenseReferrals,
            FacilityLicenseUsers,
            FacilityOrders,
            Patient,
            PatientAddress,
            PatientComments,
            PatientEmergencyContacts,
            PatientGuarantor,
            PatientPayer):
        print("Starting " + obj.__name__ + "... ")
        thing = obj()
        thing.cvtToCSV()
        print("... finished")


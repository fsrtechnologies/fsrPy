from __future__ import with_statement
import time, struct, string, calendar, os
try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO
import locale
locale.setlocale(locale.LC_ALL,(''))

from utils import NPI_Luhn, parseDirectDat, BBBB2date, BB2time, time2BB, day_of_week, BBBB2zip, BBBB2ssn, \
    BBBB2money, BBBB2money2, B2int, BB2Long, raw2phone, Translator

from Ailment import Ailment
from Appointment import Appointment
from CPA import CPA
from Diagnosis import Diagnosis
from Doctor import Doctor
from Group import Group
from ExtendedDiag import ExtendedDiag
from Facility import Facility
from GeneralAccounts import GeneralAccounts
from InsuredParty import InsuredParty
from Insurance import Insurance
from InsuranceType import InsuranceType
from Laboratory import Laboratory
from Message import Message
from NewPatient import NewPatient
from Note import Note
from Patient import Patient, PatMBI
from Procedure import Procedure
from ReferralSource import ReferralSource
from ScheduleMaster import ScheduleMaster
from StatementParams import StatementParams
from Transaction import Transaction, TransactionD, TransactionM, TransactionDt, DeletedTrans
from Office import Office
from TLAList import TLAList

def RecordGenerator(office=None, fileType=None):
    fTypes = {"Ailment" : Ailment,
    "Appointment" : Appointment,
    "CPA" : CPA,
    "Diagnosis" : Diagnosis,
    "Doctor" : Doctor,
    "Group" : Group,
    "ExtendedDiag" : ExtendedDiag,
    "Facility" : Facility,
    "GeneralAccounts" : GeneralAccounts,
    "InsuredParty" : InsuredParty,
    "Insurance" : Insurance,
    "InsuranceType" : InsuranceType,
    "Laboratory" : Laboratory,
    "Message" : Message,
    "NewPatient" : NewPatient,
    "Note" : Note,
    "Patient" : Patient,
    "PatMBI" : PatMBI,
    "Procedure" : Procedure,
    "ReferralSource" : ReferralSource,
    "ScheduleMaster" : ScheduleMaster,
    "StatementParams" : StatementParams,
    "Transaction" : Transaction,
    "TransactionD" : TransactionD,
    "TransactionM" : TransactionM,
    "TransactionDt": TransactionDt,
    "DeletedTrans" : DeletedTrans,}

    obj = fTypes[fileType]()
    recLen = obj.RecordLength
    with open(getattr(office, obj.TLA) + '.dat','rb') as inFile:
        tmpIn = inFile.read()
        buf = StringIO.StringIO(tmpIn)
        inRec = buf.read(recLen)    # initialize inRec and burn the header record
        while not (len(inRec) < recLen):
            inRec = buf.read(recLen)
            obj = fTypes[fileType](inRec)
            if (obj.Valid):
                yield obj
        buf.close()

def RecordGeneratorB(office=None, fileType=None, bufSize=524288):
    fTypes = {"Ailment" : Ailment,
    "Appointment" : Appointment,
    "CPA" : CPA,
    "Diagnosis" : Diagnosis,
    "Doctor" : Doctor,
    "Group" : Group,
    "ExtendedDiag" : ExtendedDiag,
    "Facility" : Facility,
    "GeneralAccounts" : GeneralAccounts,
    "InsuredParty" : InsuredParty,
    "Insurance" : Insurance,
    "InsuranceType" : InsuranceType,
    "Laboratory" : Laboratory,
    "Message" : Message,
    "NewPatient" : NewPatient,
    "Note" : Note,
    "Patient" : Patient,
    "Procedure" : Procedure,
    "ReferralSource" : ReferralSource,
    "ScheduleMaster" : ScheduleMaster,
    "StatementParams" : StatementParams,
    "Transaction" : Transaction,
    "TransactionD" : TransactionD,
    "DeletedTrans" : DeletedTrans,}

    obj = fTypes[fileType]()
    recLen = obj.RecordLength
    with open(getattr(office, obj.TLA) + '.dat','rb') as inFile:
        tmpIn = inFile.read(recLen)                 # burn the header record
        tmpIn = inFile.read(recLen*bufSize)
        while not (len(tmpIn) < recLen):
            buf = StringIO.StringIO(tmpIn)
            inRec = buf.read(recLen)
            while not (len(inRec) < recLen):
                obj = fTypes[fileType](inRec)
                if (obj.Valid):
                    yield obj
                inRec = buf.read(recLen)
            buf.close()
            tmpIn = inFile.read(recLen*bufSize)
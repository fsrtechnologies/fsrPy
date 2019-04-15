import struct
from utils import B2int, BB2Long, BBBB2date, BBBB2money

class Transaction(object):
    RecordLength = 256
    TLA = "TRN"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from transaction (TRN) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ChartNumber        = rec[5:16].split("\x00")[0].rstrip()
            self.KeyType            = rec[16]
            self.Date               = BBBB2date(rec[17:21])
            self.SeqNum             = BB2Long(rec[21:23])
            self.Diag1 = self.Diag2 = self.Diag3 = self.Diag4 = ""
            if (self.KeyType == 'C'):
                if (B2int(rec[23])==254):
                    self.ExtChg             = True
                    self.Diag3              = rec[42:49].split("\x00")[0].rstrip()
                    self.Diag4              = rec[49:56].split("\x00")[0].rstrip()
                    self.Mod3               = rec[56:58].split("\x00")[0].rstrip()
                    self.Mod4               = rec[59:61].split("\x00")[0].rstrip()
                else:
                    self.ExtChg             = False
                    self.ProcCode           = rec[58:64].split("\x00")[0].rstrip()
                    self.Mod1               = rec[64:66].split("\x00")[0].rstrip()
                    self.Mod2               = rec[67:69].split("\x00")[0].rstrip()
                    self.Diag1              = rec[74:81].split("\x00")[0].rstrip()
                    self.Diag2              = rec[81:87].split("\x00")[0].rstrip()
                    self.Doctor             = rec[88:90].split("\x00")[0].rstrip()
                    self.CPZ2               = rec[49]
                    self.FC                 = rec[50:52].split("\x00")[0].rstrip()
                    self.InsForm            = rec[55:57].split("\x00")[0].rstrip()
                    self.Units              = B2int(rec[53])
                    self.Charge             = BBBB2money(rec[70:74])
                    self.ChargeCents        = struct.unpack('L', rec[70:74])[0]
                    self.PriIns             = rec[101:108].split("\x00")[0].rstrip()
                    self.SecIns             = rec[108:115].split("\x00")[0].rstrip()
                    self.TerIns             = rec[115:122].split("\x00")[0].rstrip()
                    self.DateCode           = rec[92]
                    self.BilledOrig         = BBBB2date(rec[38:42])
                    self.BilledPri          = BBBB2date(rec[26:30])
                    self.BilledSec          = BBBB2date(rec[30:34])
                    self.BilledTer          = BBBB2date(rec[34:38])
                    self.AlteredDate        = BBBB2date(rec[169:173])
                    self.AlteredBy          = rec[173:176].split("\x00")[0].rstrip()
                    self.Ailment            = rec[231]
                    self.Location           = B2int(rec[91])
                    self.Facility           = rec[93:96].split("\x00")[0].rstrip()
                    self.Lab                = rec[97:100].split("\x00")[0].rstrip()
                    self.Tracer             = rec[31:33].split("\x00")[0].rstrip()
                    self.InsBal             = BBBB2money(rec[154:158])
                    self.SecBal             = BBBB2money(rec[158:162])
                    self.PriAllow           = BBBB2money(rec[122:126])
                    self.SecAllow           = BBBB2money(rec[126:130])
                    self.TerAllow           = BBBB2money(rec[130:134])
                    self.PriAdj             = BBBB2money(rec[134:138])
                    self.SecAdj             = BBBB2money(rec[138:142])
                    self.TerAdj             = BBBB2money(rec[142:146])
                    self.PatAdj             = BBBB2money(rec[146:150])
                    self.Expected           = BBBB2money(rec[150:154])

class TransactionM(object):
    RecordLength = 256
    TLA = "TRN"
    ID = ""
    def __init__(self, rec=False):
        """
        Extract fields from transaction (TRN) records
        Optimized for financial info (hence, M for Money.)
        Hoping to increase speed due to less overhead...
        """
        if (not rec) or (rec[5] == "\x00") or (rec[16] != "C") or (B2int(rec[23])==254): #If it's not a Charge, why bother?
            self.Valid = False
        else:
            self.Valid = True
            self.ChartNumber        = rec[5:16].split("\x00")[0].rstrip()
            self.Date               = BBBB2date(rec[17:21])
            self.ProcCode           = rec[58:64].split("\x00")[0].rstrip()
            self.Mod1               = rec[64:66].split("\x00")[0].rstrip()
            self.Mod2               = rec[67:69].split("\x00")[0].rstrip()
            self.Doctor             = rec[88:90].split("\x00")[0].rstrip()
            self.FC                 = rec[50:52].split("\x00")[0].rstrip()
            self.Units              = B2int(rec[53])
            self.Charge             = BBBB2money(rec[70:74])
            self.PriIns             = rec[101:108].split("\x00")[0].rstrip()
            self.Location           = B2int(rec[91])
            self.Facility           = rec[93:96].split("\x00")[0].rstrip()
            self.InsBal             = BBBB2money(rec[154:158])
            self.SecBal             = BBBB2money(rec[158:162])
            self.PriAdj             = BBBB2money(rec[134:138])
            self.SecAdj             = BBBB2money(rec[138:142])
            self.TerAdj             = BBBB2money(rec[142:146])
            self.PatAdj             = BBBB2money(rec[146:150])

class TransactionD(object):
    RecordLength = 256
    TLA = "TRN"
    ID = ""
    def __init__(self, rec=False):
        """
        Extract fields from transaction (TRN) records
        Optimized for ICD conversion (hence, D for Diagnosis.)
        Increased speed by 15x due to less overhead...
        """
        if (not rec) or (rec[5] == "\x00") or (rec[16] != "C"): #If it's not a Charge, why bother?
            self.Valid = False
        else:
            self.Valid = True
            self.ChartNumber        = rec[5:16].split("\x00")[0].rstrip()
            self.KeyType            = rec[16]
            self.Date               = BBBB2date(rec[17:21])
            self.SeqNum             = BB2Long(rec[21:23])
            self.Doctor             = rec[88:90].split("\x00")[0].rstrip()
            self.Diag1 = self.Diag2 = self.Diag3 = self.Diag4 = ""
            if (B2int(rec[23])==254):  # is this an extended charge record?
                self.ExtChg             = True
                self.Diag3              = rec[42:49].split("\x00")[0].rstrip()
                self.Diag4              = rec[49:56].split("\x00")[0].rstrip()
            else:
                self.ExtChg             = False
                self.ProcCode           = rec[58:64].split("\x00")[0].rstrip()
                if rec[5] == "\x00":
                    self.Diag1              = rec[73:80].split("\x00")[0].rstrip()
                    self.Diag2              = rec[80:86].split("\x00")[0].rstrip()
                else:
                    self.Diag1              = rec[74:81].split("\x00")[0].rstrip()
                    self.Diag2              = rec[81:87].split("\x00")[0].rstrip()

class TransactionDt(object):
    RecordLength = 256
    TLA = "TRN"
    ID = ""
    def __init__(self, rec=False):
        """
        Extract fields from transaction (TRN) records
        Optimized for date only (hence, M for Money.)
        Hoping to increase speed due to less overhead...
        """
        if (not rec) or (rec[5] == "\x00") or (rec[16] != "C") or (B2int(rec[23])==254): #If it's not a Charge, why bother?
            self.Valid = False
        else:
            self.Valid = True
            self.ChartNumber        = rec[5:16].split("\x00")[0].rstrip()
            self.Date               = BBBB2date(rec[17:21])

class DeletedTrans(Transaction):
    RecordLength = 256
    TLA = "trd"
    ID = ""



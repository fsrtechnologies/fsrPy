from utils import BBBB2zip, BBBB2ssn, BBBB2date, BB2Long

class Misc(object):
    RecordLength = 1024
    TLA = "RPT"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from outside facility records"""
        self.Valid = True
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
            return
        typeSel                     = rec[5:7].split("\x00")[0].rstrip()
        if typeSel == "\x15":
            self.recType            = "Submitter"
            self.Num                = ord(rec[7])
            self.SubmitterCode      = rec[9:25].split("\x00")[0].rstrip()
            self.SubmitterEntity    = rec[295]
            self.OfficeName         = rec[25:61].split("\x00")[0].rstrip()
            self.Street             = rec[61:90].split("\x00")[0].rstrip()
            self.City               = rec[90:111].split("\x00")[0].rstrip()
            self.State              = rec[112:115].split("\x00")[0].rstrip()
            self.Zip                = ('' if BBBB2zip(rec[115:119]) == '00000' else BBBB2zip(rec[115:119]))
            self.Phone              = rec[305:316].split("\x00")[0].rstrip()
            self.TestProd           = rec[119]
            self.Attention          = rec[120:149].split("\x00")[0].rstrip()
            self.Password           = rec[153:166].split("\x00")[0].rstrip()
            self.ExcDoc1            = rec[166:169].split("\x00")[0].rstrip()
            self.ExcDocSub1         = rec[169:182].split("\x00")[0].rstrip()
            self.ExcDoc2            = rec[185:188].split("\x00")[0].rstrip()
            self.ExcDocSub2         = rec[188:200].split("\x00")[0].rstrip()
            self.ExcDoc3            = rec[204:207].split("\x00")[0].rstrip()
            self.ExcDocSub3         = rec[207:220].split("\x00")[0].rstrip()
            self.ExcDoc4            = rec[223:226].split("\x00")[0].rstrip()
            self.ExcDocSub4         = rec[226:238].split("\x00")[0].rstrip()
            self.ReceiverID         = rec[242:259].split("\x00")[0].rstrip()
            self.ReceiverName       = rec[259:295].split("\x00")[0].rstrip()
            self.FirstName          = rec[316:332].split("\x00")[0].rstrip()
            self.LastName           = rec[332:348].split("\x00")[0].rstrip()
            self.MI                 = rec[348]
            self.SuppressPmt        = rec[354]
            self.LastSent           = BBBB2date(rec[349:353])




        elif typeSel == "aa":
            self.recType            = "Printer"
        elif typeSel == "ba":
            self.recType            = "Shortcut"
            self.ID                 = rec[23:24].split("\x00")[0].rstrip()
            self.City               = rec[25:39].split("\x00")[0].rstrip()
            self.State              = rec[41:43].split("\x00")[0].rstrip()
            self.Zip                = ('' if BBBB2zip(rec[44:48]) == '00000' else BBBB2zip(rec[44:48]))
            self.AreaCode           = rec[48:51].split("\x00")[0].rstrip()
        elif typeSel == "A":
            self.recType            = "OfficeInfo"
            self.PageNum            = (1 if rec[7] == '\x00' else 2 if rec[7] == '\x02' else 3 if rec[7] == '\x03' else 0)
            self.Name               = rec[31:66].split("\x00")[0].rstrip()
            self.Street             = rec[67:96].split("\x00")[0].rstrip()
            self.City               = rec[96:117].split("\x00")[0].rstrip()
            self.State              = rec[118:120].split("\x00")[0].rstrip()
            self.Zip                = BBBB2zip(rec[121:125])
            self.Phone              = rec[125:136].split("\x00")[0].rstrip()
            self.License            = rec[136:147].split("\x00")[0].rstrip()
            self.SSN                = BBBB2ssn(rec[147:151])
            self.EIN                = rec[151:161].split("\x00")[0].rstrip()
            self.MedicareID         = rec[161:173].split("\x00")[0].rstrip()
            self.MedicaidID         = rec[174:186].split("\x00")[0].rstrip()
            self.BlueCrossID        = rec[187:199].split("\x00")[0].rstrip()
            self.WorkCompID         = rec[200:212].split("\x00")[0].rstrip()
            self.BlueShieldID       = rec[213:226].split("\x00")[0].rstrip()
            self.OtherID1           = rec[226:238].split("\x00")[0].rstrip()
            self.OtherID2           = rec[239:251].split("\x00")[0].rstrip()
            self.PaymentAuth        = rec[252:278].split("\x00")[0].rstrip()
            self.CLIA               = rec[278:292].split("\x00")[0].rstrip()
            self.GroupName          = rec[359:383].split("\x00")[0].rstrip()
            self.Specialty          = rec[383:386].split("\x00")[0].rstrip()
            self.IMSNum             = rec[423:433].split("\x00")[0].rstrip()
            self.LastDayClose       = BBBB2date(rec[340:344])
            self.FiscalDate         = BB2Long(rec[347:349])
            self.Huh2               = BBBB2zip(rec[405:409])
            self.Huh3               = BBBB2zip(rec[413:417])

            self.NPI                = ''
        else:
            self.recType            = "Unknown"


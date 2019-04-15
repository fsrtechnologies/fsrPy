from utils import BBBB2ssn, BBBB2zip

class Group(object):
    RecordLength = 1024
    TLA = "RPT"
    ID = ""
    def __init__(self, rec=False, ID=False):
        """Extract fields from doctor records"""
        self.Valid = False
        if ID:
            self.ID                 = ID
        if rec:
            if (rec[5] == "A"):
                self.Valid = True
                self.Name               = rec[31:67].split("\x00")[0].rstrip()
                self.Street             = rec[67:96].split("\x00")[0].rstrip()
                self.City               = rec[96:118].split("\x00")[0].rstrip()
                self.State              = rec[118:120].split("\x00")[0].rstrip()
                self.Zip                = BBBB2zip(rec[122:126])
                self.PaymentAuth        = rec[252:278].split("\x00")[0].rstrip()
                self.SpecialtyCode      = rec[383:386].split("\x00")[0].rstrip()
                self.Phone              = rec[126:136].split("\x00")[0].rstrip()
                self.License            = rec[136:146].split("\x00")[0].rstrip()
                self.EIN                = rec[151:160].split("\x00")[0].rstrip()
                self.SSN                = BBBB2ssn(rec[147:151])
                if (self.SSN == '0'): self.SSN = ''
                self.MedicareID         = rec[161:174].split("\x00")[0].rstrip()
                self.MedicaidID         = rec[174:186].split("\x00")[0].rstrip()
                self.WorkCompID         = rec[200:212].split("\x00")[0].rstrip()
                self.BlueCrossID        = rec[188:199].split("\x00")[0].rstrip()
                self.BlueShieldID       = rec[213:225].split("\x00")[0].rstrip()
                self.OtherID1           = rec[226:238].split("\x00")[0].rstrip()
                self.OtherID2           = rec[239:251].split("\x00")[0].rstrip()
                self.IMSNumber          = rec[423:432].split("\x00")[0].rstrip()
                self.CLIANumber         = rec[278:289].split("\x00")[0].rstrip()
                self.GroupName          = rec[359:382].split("\x00")[0].rstrip()
                self.FiscalDate         = ''  # BB2time(rec[417:419])  # I'll worry about this later, maybe
                self.NPI                = ''


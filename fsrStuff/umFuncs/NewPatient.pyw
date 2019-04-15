from utils import BBBB2zip, raw2phone

class NewPatient(object):
    RecordLength = 166
    TLA = "NEW"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from new-patient (not yet seen) (NEW) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.NewPatNumber   = rec[6:15].split("\x00")[0].rstrip()
            self.LastName       = "" + rec[27:43].split("\x00")[0].rstrip()
            self.FirstName      = "" + rec[43:56].split("\x00")[0].rstrip()
            self.MI             = "" + rec[56].split("\x00")[0]
            self.HomePhone      = raw2phone(rec[57:68].split("\x00")[0].rstrip())
            self.WorkPhone      = raw2phone(rec[68:79].split("\x00")[0].rstrip())
            self.WorkExt        = rec[79:84].split("\x00")[0].rstrip()
            self.Address        = rec[84:113].split("\x00")[0].rstrip()
            self.City           = rec[113:128].split("\x00")[0].rstrip()
            self.State          = rec[129:131].split("\x00")[0].rstrip()
            self.Zip            = BBBB2zip(rec[132:136])
            self.ReferredBy     = rec[138:143].split("\x00")[0].rstrip()

from utils import BBBB2zip

class Facility(object):
    RecordLength = 198
    TLA = "FAC"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from outside facility records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ID                 = rec[5:8].split("\x00")[0].rstrip()
            self.Name               = rec[9:40].split("\x00")[0].rstrip()
            self.Street             = rec[40:69].split("\x00")[0].rstrip()
            self.City               = rec[69:90].split("\x00")[0].rstrip()
            self.State              = rec[91:93].split("\x00")[0].rstrip()
            self.Zip                = BBBB2zip(rec[94:98])
            self.Phone              = rec[98:109].split("\x00")[0].rstrip()
            self.MedicaidID         = rec[112:127].split("\x00")[0].rstrip()
            self.MedicareID         = rec[128:143].split("\x00")[0].rstrip()
            self.OtherID1           = rec[144:159].split("\x00")[0].rstrip()
            self.UsesSpecialYN      = rec[168].split("\x00")[0].rstrip()
            self.NPI                = ''


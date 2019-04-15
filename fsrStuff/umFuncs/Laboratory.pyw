from utils import BBBB2zip

class Laboratory(object):
    RecordLength = 192
    TLA = "LAB"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from laboratory (LAB) records"""
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
            self.Phone              = rec[98:109].split("\x00")[0]
            self.Contact            = rec[109:135].split("\x00")[0].rstrip()
            self.MedicareID         = rec[151:162].split("\x00")[0]
            self.NPI                = ''

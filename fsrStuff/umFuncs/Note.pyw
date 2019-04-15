from utils import BBBB2date

class Note(object):
    RecordLength = 128
    TLA = "NOT"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from F12 patient notes table (xxNOT) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ChartNumber        = rec[5:16].split("\x00")[0].rstrip()
            self.EntryDate          = BBBB2date(rec[16:20])
            self.Text               = rec[22:83].split("\x00")[0].rstrip()
            self.BlinkYN            = rec[83].split("\x00")[0]
            self.Operator           = rec[84:87].split("\x00")[0].rstrip()
            self.ActionCode         = rec[88:89].split("\x00")[0].rstrip()
            self.ActionDate         = BBBB2date(rec[91:95])

from utils import BBBB2date, BBBB2zip

class InsuredParty(object):
    RecordLength = 256
    TLA = "IND"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from insured-party (IND) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ChartNumber        = rec[5:16].split("\x00")[0].rstrip()
            self.Rank               = rec[16].split("\x00")[0]
            self.LinkToChart        = rec[18:29].split("\x00")[0].rstrip()
            self.LastName           = rec[29:45].split("\x00")[0].rstrip()
            self.FirstName          = rec[45:58].split("\x00")[0].rstrip()
            self.MI                 = rec[60].split("\x00")[0]
            self.Street             = rec[60:89].split("\x00")[0].rstrip()
            self.City               = rec[89:105].split("\x00")[0].rstrip()
            self.State              = rec[105:107].split("\x00")[0].rstrip()
            self.Zip                = BBBB2zip(rec[108:112])
            self.HomePhone          = rec[112:122].split("\x00")[0]
            self.Birthdate          = BBBB2date(rec[127:131])
            self.Sex                = rec[131].split("\x00")[0]
            self.Employer           = rec[132:160].split("\x00")[0].rstrip()


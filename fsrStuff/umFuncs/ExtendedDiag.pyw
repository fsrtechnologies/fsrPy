class ExtendedDiag(object):
    RecordLength = 94
    TLA = "EXD"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from extended-diagnosis (history) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ID = ""
            self.Description = ""

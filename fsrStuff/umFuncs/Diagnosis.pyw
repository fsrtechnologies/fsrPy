class Diagnosis(object):
    RecordLength = 90
    TLA = "DIA"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from diagnosis records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ID             = rec[5:11].split("\x00")[0].rstrip()
            self.Description    = rec[12:52].split("\x00")[0].rstrip()
            self.DotFormat      = (True if ord(rec[53]) == 1 else False)
            if self.DotFormat:
                self.ICD            = rec[54:60].split("\x00")[0].rstrip()
            else:
                self.ICD            = rec[53:60].split("\x00")[0].rstrip()

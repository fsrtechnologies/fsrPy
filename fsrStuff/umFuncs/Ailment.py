class Ailment(object):
    RecordLength = 256
    TLA = "AIL"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from ailment records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.Description = ""


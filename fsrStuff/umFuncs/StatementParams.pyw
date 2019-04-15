class StatementParams(object):
    RecordLength = 128
    TLA = "STA"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from statement parameter (STA) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ID = ""
            self.Description = ""


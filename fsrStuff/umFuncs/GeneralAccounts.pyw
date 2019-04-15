class GeneralAccounts(object):
    RecordLength = 449
    TLA = "GAA"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from GAA records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ID = ""
            self.Description = "Not yet!"


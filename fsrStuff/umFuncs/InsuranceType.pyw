class InsuranceType(object):
    RecordLength = 80
    TLA = "ITT"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from insurance-type (billing form) (ITT) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ID = ""
            self.Description = ""

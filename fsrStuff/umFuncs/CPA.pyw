class CPA(object):
    RecordLength = 512
    TLA = "CPA"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from financial category (charge-payment-adjustment type) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.Description = ""

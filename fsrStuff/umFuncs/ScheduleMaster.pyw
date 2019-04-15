class ScheduleMaster(object):
    RecordLength = 256
    TLA = "SSM"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from daily schedule master (SSM) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ID = ""
            self.Description = ""


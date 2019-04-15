class Message(object):
    RecordLength = 110
    TLA = "REC"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from systemwide messages table (REC) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ID                 = rec[5:8].split("\x00")[0].rstrip()
            self.Text               = rec[9:80].split("\x00")[0].rstrip()

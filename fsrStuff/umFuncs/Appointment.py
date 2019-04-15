from utils import B2int, BB2time, BBBB2date

class Appointment(object):
    RecordLength = 107
    TLA = "APP"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from appointment records to dictionary"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ChartNumber            = ""
            self.NewPatientYN           = False
            self.DoctorNumber           = rec[5:7]
            self.Date                   = rec[8:16]
            if   (ord(rec[22]) ==   1):
                self.SlotType           = 1 # start record
            elif (ord(rec[22]) == 255):
                self.SlotType           = 9 # end record
            elif (ord(rec[22]) ==   2):
                self.SlotType           = 2 # open slot
            elif (ord(rec[22]) ==   3):
                self.SlotType           = 3 # closed slot
            else:                                               # real appointment
                self.SlotType           = 4
                if (ord(rec[22]) == 254):                       # "new" patient
                    self.NewPatientYN   = True
                    self.ChartNumber    = rec[23:32].split("\x00")[0].rstrip()
                else:
                    self.ChartNumber    = rec[22:32].split("\x00")[0].rstrip()
                self.Procedure          = rec[33:38].split("\x00")[0].rstrip()
                self.Duration           = B2int(rec[44])
                self.Comment            = rec[46:70].split("\x00")[0].rstrip()
                self.MessageCode        = rec[73:75].split("\x00")[0].rstrip()
            self.TimeSlot               = BB2time(rec[19:21])
            self.PrettyTime             = BB2time(rec[19:21], '12')
            self.MilTime                = BB2time(rec[19:21], '24')
            self.DateCreated            = BBBB2date(rec[39:43])
            self.Alert                  = rec[46:72].split("\x00")[0].rstrip()


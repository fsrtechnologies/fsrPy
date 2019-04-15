from __future__ import with_statement
from utils import BBBB2zip

class Insurance(object):
    RecordLength = 512
    TLA = "INS"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from insurance company records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ID              = rec[5:11].split("\x00")[0].rstrip()
            self.Name            = rec[12:43].split("\x00")[0].strip().replace(',',' ')
            self.Street          = rec[43:72].split("\x00")[0].rstrip().replace(',',' ')
            self.Address1        = rec[285:314].split("\x00")[0].rstrip().replace(',',' ')
            self.City            = rec[72:94].split("\x00")[0].rstrip().replace(',',' ')
            self.State           = rec[94:97].split("\x00")[0]
            self.Zip             = BBBB2zip(rec[97:101])
            self.Tel             = rec[101:112].split("\x00")[0].rstrip()
            self.Contact         = rec[112:138].split("\x00")[0].rstrip()
            self.BillCode        = rec[139:143].split("\x00")[0].rstrip()
            #self.Profile         = rec[143]
            #self.AutoCalc1       = rec[144]
            #self.AutoCalc2       = rec[148]
            #self.AutoCalc3       = rec[378]
            #self.AutoCalc4       = rec[382]
            self.CapitationType  = rec[208].split("\x00")[0].rstrip()
            self.IMSCarrierID    = rec[209:216].split("\x00")[0].rstrip()
            self.IMSClaimOffice  = rec[348:359].split("\x00")[0].rstrip()
            self.OvrPayorID      = rec[425:442].split("\x00")[0].rstrip()
            self.OvrCarrierID    = rec[224:230].split("\x00")[0].rstrip()  # this and the override destination code might be reversed...
            self.OvrClaimOfc     = rec[230:235].split("\x00")[0].rstrip()
            self.OvrDestCode     = rec[344:347].split("\x00")[0].rstrip()  # this and the override carrier code might be reversed...
            self.MediGapOCNACode = rec[314:331].split("\x00")[0].rstrip()
            self.RendIDType      = rec[347]
            self.ProvIDType      = rec[412]
            self.ProvIDOverride  = rec[331:345].split("\x00")[0].rstrip()
            self.ReferIDType     = rec[421]
            self.ContractID      = rec[361:375].split("\x00")[0].rstrip()
            self.PaymentAuth     = rec[386:412].split("\x00")[0].rstrip()
            self.PassThruYN      = rec[359]
            self.LabelYN         = rec[420] # Print insurance company's name and address on 1500?
            self.YearFormat      = rec[424]  # 2 or 4-digit years
            self.ChampusYN       = rec[360]
            self.ContractAmtYN   = rec[377] # Accept contract amount as charge amount?
            #self.Reduction1Pct   = rec[235:240]
            #self.Reduction1Begin = rec[12:43].split("\x00")[0].rstrip()
            #self.Reduction1End   = rec[12:43].split("\x00")[0].rstrip()
            #self.Reduction2Pct   = rec[12:43].split("\x00")[0].rstrip()
            #self.Reduction2Begin = rec[12:43].split("\x00")[0].rstrip()
            #self.Reduction2End   = rec[12:43].split("\x00")[0].rstrip()
            #self.Reduction3Pct   = rec[12:43].split("\x00")[0].rstrip()
            #self.Reduction3Begin = rec[12:43].split("\x00")[0].rstrip()
            #self.Reduction3End   = rec[12:43].split("\x00")[0].rstrip()
            #self.Reduction4Pct   = rec[12:43].split("\x00")[0].rstrip()
            #self.Reduction4Begin = rec[12:43].split("\x00")[0].rstrip()
            #self.Reduction4End   = rec[12:43].split("\x00")[0].rstrip()



from utils import B2int, BBBB2money, BBBB2money2

class Procedure(object):
    RecordLength = 512
    TLA = "PRO"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from procedure (PRO) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.Doctor             = rec[5:8].split("\x00")[0].rstrip()
            self.InHouseCode        = rec[8:14].split("\x00")[0].rstrip()
            self.Description1       = rec[14:36].split("\x00")[0].rstrip()
            self.Description2       = rec[36:58].split("\x00")[0].rstrip()
            self.CPTCode            = rec[71:77].split("\x00")[0].rstrip()
            self.CPTModifier1       = rec[77:80].split("\x00")[0].rstrip()
            self.CPTModifier2       = rec[493:496].split("\x00")[0].rstrip()
            self.HCPCSCode          = rec[62:68].split("\x00")[0].rstrip()
            self.HCPCSModifier1     = rec[68:71].split("\x00")[0].rstrip()
            self.HCPCSModifier2     = rec[496:499].split("\x00")[0].rstrip()
            self.Code3Code          = rec[80:85].split("\x00")[0].rstrip()
            self.Code3Modifier      = rec[85:88].split("\x00")[0].rstrip()
            self.Code4Code          = rec[88:93].split("\x00")[0].rstrip()
            self.Code4Modifier      = rec[93:96].split("\x00")[0].rstrip()
            self.AnesthUnits        = rec[96:99].split("\x00")[0].rstrip()
            self.TypeOfService      = ord(rec[58])
            self.Department         = rec[59:62].split("\x00")[0].rstrip()
            self.UsualCharge        = BBBB2money(rec[100:104])
            self.UsualLocation      = B2int(rec[499])
           #self.UsualDuration      = struct.unpack('h',rec[104:107])[0]
            self.RemindCycle        = B2int(rec[107])
            self.ElecBillableYN     = rec[108]
            self.Comment            = rec[181:248].split("\x00")[0].rstrip()
            self.MedicareProfile    = BBBB2money(rec[109:113])
            self.MedicaidProfile    = BBBB2money(rec[113:117])
            self.Profile3           = BBBB2money(rec[117:121])
            self.Profile4           = BBBB2money(rec[121:125])
            self.Profile5           = BBBB2money(rec[125:129])
            self.RVSType            = rec[438]
            self.RVSValue           = BBBB2money2(rec[439:443])
            self.RBRVSYN            = rec[443]
            self.RBRVSValue         = BBBB2money2(rec[444:448])  # hmmm?
            self.DiagnosisLink      = rec[408:414].split("\x00")[0].rstrip()
            self.AutocalcLevel      = rec[129]
            self.ForceAssignYN      = B2int(rec[415])
            self.SpecialProcessing  = B2int(rec[421])
            self.ForceNoInsYN       = B2int(rec[448])
            self.VendorCharge       = BBBB2money(rec[416:420])
            self.RequiresUPINYN     = rec[99]
            self.Inv1Item           = rec[130:136].split("\x00")[0].rstrip()
            self.Inv1Depletion      = B2int(rec[160])
            self.Inv2Item           = rec[136:142].split("\x00")[0].rstrip()
            self.Inv2Depletion      = B2int(rec[161])
            self.Inv3Item           = rec[142:148].split("\x00")[0].rstrip()
            self.Inv3Depletion      = B2int(rec[162])
            self.Inv4Item           = rec[148:154].split("\x00")[0].rstrip()
            self.Inv4Depletion      = B2int(rec[163])
            self.Inv5Item           = rec[154:160].split("\x00")[0].rstrip()
            self.Inv5Depletion      = B2int(rec[164])


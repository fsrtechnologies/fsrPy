from utils import BBBB2date, BBBB2zip

class ReferralSource(object):
    RecordLength = 384
    TLA = "REF"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from referral source (REF) records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ID          = rec[5:9].split("\x00")[0].rstrip()
            self.Company     = rec[10:40].split("\x00")[0].rstrip()
            self.Name        = rec[41:71].split("\x00")[0].rstrip()
            self.Address     = self.Street = rec[72:100].split("\x00")[0]
            self.Address1    = self.Suite = rec[101:111].split("\x00")[0]
            self.City        = rec[112:133].split("\x00")[0]
            self.State       = rec[134:136].split("\x00")[0]
            self.Zip         = BBBB2zip(rec[137:141])
            self.Phone       = rec[141:151].split("\x00")[0]
            self.MedicaidID  = rec[152:162].split("\x00")[0]
            self.UPIN        = rec[163:173].split("\x00")[0]
            self.Specialty   = rec[174:204].split("\x00")[0]
            self.HospAffil1  = rec[205:208].split("\x00")[0]
            self.HospAffil2  = rec[209:212].split("\x00")[0]
            self.Birthday    = BBBB2date(rec[213:217])
            self.Anniversary = BBBB2date(rec[305:309])
            self.LastName    = rec[241:261].split("\x00")[0]
            self.FirstName   = rec[262:275].split("\x00")[0]
            self.MI          = rec[276]
            self.Fax         = rec[277:287].split("\x00")[0]
            self.License     = rec[288:298].split("\x00")[0]
            self.Extension   = rec[299:304].split("\x00")[0]
            self.TaxID       = rec[309:320].split("\x00")[0]
            self.MedicareID  = rec[321:333].split("\x00")[0]
            self.NPI         = ''
    def __str__(self):
        if not self.Valid:
            return "Not a valid referral source record"
        else:
            outStr = "ID:" + self.ID + " Name:" + self.Name + " Address:" + self.Address + " Street:" + self.Street + " Address1:" + self.Address1 + " Suite:" + self.Suite
            return outStr


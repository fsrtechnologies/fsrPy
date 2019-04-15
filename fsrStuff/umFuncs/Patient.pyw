import struct
from utils import B2int, BBBB2date, BBBB2ssn, BBBB2zip, raw2phone

class Patient(object):
    RecordLength = 1024
    TLA = "PAT"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from patient records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ChartNumber        = rec[5:16].split("\x00")[0].rstrip()
            self.LastName           = "" + rec[16:31].split("\x00")[0].rstrip()
            self.FirstName          = "" + rec[32:44].split("\x00")[0].rstrip()
            self.MI                 = "" + rec[45]
            self.AccountNumber      = rec[16:31].split("\x00")[0].rstrip()
            self.Address1           = rec[982:1010].split("\x00")[0].rstrip()
            self.Street             = rec[72:100].split("\x00")[0].rstrip()
            self.City               = rec[101:116].split("\x00")[0].rstrip()
            self.State              = rec[117:119].split("\x00")[0].rstrip()
            self.Zip                = BBBB2zip(rec[120:124])
            self.HomePhone          = raw2phone(rec[124:134].split("\x00")[0])
            self.DrivLicNum         = rec[135:147].split("\x00")[0].rstrip()
            self.SSN                = BBBB2ssn(rec[148:152])
            self.Birthdate          = BBBB2date(rec[152:156])
            self.Sex                = rec[156].split("\x00")[0]
            self.EmergContact       = rec[157:187].split("\x00")[0].rstrip()
            self.EmergPhone         = raw2phone(rec[188:198].split("\x00")[0])
            self.EmergRelCode       = rec[199:205].split("\x00")[0].rstrip()
            self.Message1           = rec[206:238].split("\x00")[0].rstrip()
            self.Message2           = rec[239:271].split("\x00")[0].rstrip()
            self.NrstRelName        = rec[272:302].split("\x00")[0].rstrip()
            self.NrstRelStreet      = rec[303:331].split("\x00")[0].rstrip()
            self.NrstRelCity        = rec[332:347].split("\x00")[0].rstrip()
            self.NrstRelState       = rec[348:350].split("\x00")[0].rstrip()
            self.NrstRelZip         = BBBB2zip(rec[351:355])
            self.NrstRelPhone       = raw2phone(rec[355:365].split("\x00")[0])
            self.NrstRelRelCode     = rec[366:372].split("\x00")[0].rstrip()
            self.EmpRefSrcCode      = struct.unpack('B',rec[979])[0]
            self.EmpName            = rec[373:403].split("\x00")[0].rstrip()
            self.EmpContact         = rec[947:975].split("\x00")[0].rstrip()
            self.EmpStreet          = rec[404:432].split("\x00")[0].rstrip()
            self.EmpCity            = rec[433:448].split("\x00")[0].rstrip()
            self.EmpState           = rec[455:457].split("\x00")[0].rstrip()
            self.EmpZip             = BBBB2zip(rec[458:462])
            self.EmpPhone           = raw2phone(rec[462:472].split("\x00")[0])
            self.EmpPhone2          = raw2phone(rec[473:483].split("\x00")[0])
            self.EmpPhone2Ext       = rec[484:488].split("\x00")[0].rstrip()
            self.Doctor             = rec[489:491].split("\x00")[0].rstrip()
            self.MessageCode        = rec[492:495].split("\x00")[0].rstrip()
            self.RecallCycle        = rec[496:500].split("\x00")[0].rstrip()
            self.Ailment            = B2int(rec[501])
            self.Operator           = rec[503:506].split("\x00")[0].rstrip()
            self.EntryDate          = BBBB2date(rec[507:511])
            self.ChampSpnsrGrade    = rec[515:517].split("\x00")[0].rstrip()
            self.ChampBranchOfSvc   = rec[518].split("\x00")[0]
            self.ChampDutyStatus    = struct.unpack('B',rec[520])[0]
            self.Facility           = rec[528:531].split("\x00")[0].rstrip()
            self.Pharmacy           = rec[570:573].split("\x00")[0].rstrip()
            self.Diagnosis1         = rec[574:580].split("\x00")[0].rstrip()
            self.Diagnosis2         = rec[581:587].split("\x00")[0].rstrip()
            self.Diagnosis3         = rec[588:594].split("\x00")[0].rstrip()
            self.Diagnosis4         = rec[595:601].split("\x00")[0].rstrip()
            self.ReferredBy         = rec[602:606].split("\x00")[0].rstrip()
            self.OtherRef1          = rec[607:611].split("\x00")[0].rstrip()
            self.OtherRef2          = rec[612:616].split("\x00")[0].rstrip()
            self.OtherRef3          = rec[617:621].split("\x00")[0].rstrip()
            self.InsuranceType      = rec[622:624].split("\x00")[0].rstrip()
            self.FinancialCategory  = rec[625:627].split("\x00")[0].rstrip()
            self.MaritalStatus      = rec[628].split("\x00")[0]
            self.StatementCode      = rec[629].split("\x00")[0]
            self.BillingCycle       = rec[630].split("\x00")[0]
            self.AssignmentYN       = rec[631].split("\x00")[0]
            self.FinanceChargeYN    = rec[632].split("\x00")[0]
            self.PriInsDeductible   = struct.unpack('i',rec[633:637])[0]
            self.PriInsCopay        = rec[637:643].split("\x00")[0].rstrip()
            self.PriInsCompany      = rec[644:650].split("\x00")[0].rstrip()
            self.SecInsCompany      = rec[651:657].split("\x00")[0].rstrip()
            self.TerInsCompany      = rec[658:664].split("\x00")[0].rstrip()
            self.PriInsuredID       = rec[665:685].split("\x00")[0].rstrip()
            self.SecInsuredID       = rec[686:706].split("\x00")[0].rstrip()
            self.TerInsuredID       = rec[707:727].split("\x00")[0].rstrip()
            self.PriInsPlanName     = rec[728:748].split("\x00")[0].rstrip()
            self.SecInsPlanName     = rec[749:769].split("\x00")[0].rstrip()
            self.TerInsPlanName     = rec[770:790].split("\x00")[0].rstrip()
            self.PriInsPolicy       = rec[791:806].split("\x00")[0].rstrip()
            self.SecInsPolicy       = rec[807:822].split("\x00")[0].rstrip()
            self.TerInsPolicy       = rec[823:838].split("\x00")[0].rstrip()
            self.PriInsuredRel      = rec[932].split("\x00")[0]
            self.SecInsuredRel      = rec[933].split("\x00")[0]
            self.TerInsuredRel      = rec[934].split("\x00")[0]
            self.PmtAuthType        = rec[935].split("\x00")[0].rstrip()

class PatMBI(object): #Stripped-down version for finding Medicare Beneficiary IDs in Message2 field
    RecordLength = 1024
    TLA = "PAT"
    ID = ""
    def __init__(self, rec=False):
        """Extract fields from patient records"""
        if (not rec) or (rec[5] == "\x00"):
            self.Valid = False
        else:
            self.Valid = True
            self.ChartNumber        = rec[5:16].split("\x00")[0].rstrip()
            self.SSN                = BBBB2ssn(rec[148:152])
            self.Message2           = rec[239:271].split("\x00")[0].rstrip()
            self.PriInsuredID       = rec[665:685].split("\x00")[0].rstrip()


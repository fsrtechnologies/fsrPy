class X12NM1:  #Name - could be anybody...
    def __init__(self, Last='', First='', MI='', Suffix='', IDQual='', IDNum=''):
        self.Last   = Last
        self.First  = First
        self.MI     = MI
        self.Suffix = Suffix
        self.IDQual = IDQual
        self.IDNum  = IDNum

class X12MIA:  #Inpatient adjustments - skipping this for now
    def __init__(self, CoveredDays='', PPSOutlier='', PsychDays='', DRGAmt=0.00, Remark1='', DispropAmt=0.00, 
                        MSP_PassThruAmt=0.00, PPS_Amt=0.00, PPS_FSP_DRGAmt=0.00, PPS_HSP_DRGAmt=0.00, 
                        PPS_DSH_DRGAmt=0.00, OldCapAmt=0.00, PPS_IMEAmt=0.00, PPS_OHS_DRG_Amt=0.00,
                        CostRepDayCnt='', PPS_OFS_DRGAmt=0.00, PPS_OutlierAmt=0.00, IndirTchAmt=0.00, 
                        NonPayPCAmt=0.00,Remark2='', Remark3='', Remark4='', Remark5='', PPS_ExceptAmt=0.00):
        self.CoveredDays      = CoveredDays    
        self.PPSOutlier       = PPSOutlier     
        self.PsychDays        = PsychDays      
        self.DRGAmt           = DRGAmt         
        self.Remark1          = Remark1        
        self.DispropAmt       = DispropAmt     
        self.MSP_PassThruAmt  = MSP_PassThruAmt
        self.PPS_Amt          = PPS_Amt        
        self.PPS_FSP_DRGAmt   = PPS_FSP_DRGAmt 
        self.PPS_HSP_DRGAmt   = PPS_HSP_DRGAmt 
        self.PPS_DSH_DRGAmt   = PPS_DSH_DRGAmt 
        self.OldCapAmt        = OldCapAmt      
        self.PPS_IMEAmt       = PPS_IMEAmt     
        self.PPS_OHS_DRG_Amt  = PPS_OHS_DRG_Amt
        self.CostRepDayCnt    = CostRepDayCnt  
        self.PPS_OFS_DRGAmt   = PPS_OFS_DRGAmt 
        self.PPS_OutlierAmt   = PPS_OutlierAmt 
        self.IndirTchAmt      = IndirTchAmt    
        self.NonPayPCAmt      = NonPayPCAmt    
        self.Remark2          = Remark2        
        self.Remark3          = Remark3        
        self.Remark4          = Remark4        
        self.Remark5          = Remark5        
        self.PPS_ExceptAmt    = PPS_ExceptAmt  


class X12MOA:  #Outpatient adjustments
    def __init__(self, ReimbRate='', HCPCSAmt=0.00,Remark1='', Remark2='', Remark3='', Remark4='', Remark5='', NonPayPCAmt=0.00):
        self.ReimbRate    = ReimbRate  
        self.HCPCSAmt     = HCPCSAmt   
        self.Remark1      = Remark1    
        self.Remark2      = Remark2    
        self.Remark3      = Remark3    
        self.Remark4      = Remark4    
        self.Remark5      = Remark5    
        self.NonPayPCAmt  = NonPayPCAmt


class X12REF:
    def __init__(self, IDQual='', IDNum=''):
        self.IDQual = IDQual
        self.IDNum  = IDNum 


class X12AMT:
    def __init__(self, AmtQual='', Amt=0.00):
        self.AmtQual = AmtQual
        self.Amt     = Amt    

class X12QTY:
    def __init__(self, QuantQual='', Quantity=0):
        self.QuantQual= QuantQual
        self.Quantity = Quantity 

class X12LQ:
    def __init__(self, CodeListQual='', RemarkCode=''):
        self.CodeListQual= CodeListQual
        self.RemarkCode  = RemarkCode

class X12PLB:  # FGrp.TSet.ProviderAdj...
    def __init__(self, ProvID='', date='', RsnCode1='', ID1='', Amt1=0.00, RsnCode2='', ID2='', Amt2=0.00, RsnCode3='', ID3='', Amt3=0.00, RsnCode4='', ID4='', Amt4=0.00, RsnCode5='', ID5='', Amt5=0.00, RsnCode6='', ID6='', Amt6=0.00):
        self.ProvID  = ProvID   
        self.date    = date     
        self.RsnCode1= RsnCode1 
        self.ID1     = ID1      
        self.Amt1    = Amt1     
        self.RsnCode2= RsnCode2 
        self.ID2     = ID2      
        self.Amt2    = Amt2     
        self.RsnCode3= RsnCode3 
        self.ID3     = ID3      
        self.Amt3    = Amt3     
        self.RsnCode4= RsnCode4 
        self.ID4     = ID4      
        self.Amt4    = Amt4     
        self.RsnCode5= RsnCode5 
        self.ID5     = ID5      
        self.Amt5    = Amt5     
        self.RsnCode6= RsnCode6 
        self.ID6     = ID6      
        self.Amt6    = Amt6     


class X12PER: #Contact at insurance company... not used
    def __init__(self, FuncCode='', ContactName='', Comm1Qual='', Comm1Num='', Comm2Qual='', Comm2Num='', Comm3Qual='', Comm3Num=''):    
        self.FuncCode    = FuncCode        
        self.ContactName = ContactName    
        self.Comm1Qual   = Comm1Qual      
        self.Comm1Num    = Comm1Num       
        self.Comm2Qual   = Comm2Qual      
        self.Comm2Num    = Comm2Num       
        self.Comm3Qual   = Comm3Qual
        self.Comm3Num    = Comm3Num

class Adjust:
    def __init__(self, RsnCode='', Amt=0.00, Qty=0):    
        self.RsnCode= RsnCode
        self.Amt    = Amt    
        self.Qty    = Qty    

class X12Payor:
    def __init__(self, Name='',Add1='',Add2='',CSZ='', ContactText='',ContactNum=''):
        self.Name       = Name        
        self.Add1       = Add1        
        self.Add2       = Add2        
        self.CSZ        = CSZ         
        self.ContactText= ContactText  # Medicare is using this field for "Provider is on A/R" notification...
        self.ContactNum = ContactNum   # Could be tel, fax, or email

class X12Payee:
    def __init__(self, Name='', Add1='', Add2='', CSZ='', IDType='', IDNum=''): 
        self.Name   = Name    
        self.Add1   = Add1    
        self.Add2   = Add2    
        self.CSZ    = CSZ     
        self.IDType = IDType 
        self.IDNum  = IDNum   

class Loop2110:  #Fgrp.TSet().Detail().Claim().Service loop========
    def __init__(self, AdjudProcIDQual='', AdjudProcID='', AdjudMod1='', AdjudMod2='', AdjudMod3='', AdjudMod4='', AdjudDesc='', 
                       ChgAmt=0.00, AllowedAmt=0.00, Deduct=0.00, CoIns=0.00, AdjCodes='', AdjAmt=0.00, PmtAmt=0.00, NUBCRevCode='', 
                       PaidUnits=0 , SubmProcIDQual='', SubmProcID='', SubmMod1='', SubmMod2='', SubmMod3='', SubmMod4='', SubmDesc='', 
                       SubmUnits=0, Date1='', Date2='', POS='', LineNum='', RendProv='', SvcSupQty='', RmkCodes=''):
        self.AdjudProcIDQual  = AdjudProcIDQual   # Type of code: HCPCS, etc. (usually HCPCS)
        self.AdjudProcID      = AdjudProcID       # Procedure code being adjudicated     
        self.AdjudMod1        = AdjudMod1       
        self.AdjudMod2        = AdjudMod2       
        self.AdjudMod3        = AdjudMod3       
        self.AdjudMod4        = AdjudMod4       
        self.AdjudDesc        = AdjudDesc       
        self.ChgAmt           = ChgAmt          
        self.AllowedAmt       = AllowedAmt      
        self.Deduct           = Deduct          
        self.CoIns            = CoIns           
        self.AdjCodes         = AdjCodes        
        self.AdjAmt           = AdjAmt          
        self.PmtAmt           = PmtAmt          
        self.NUBCRevCode      = NUBCRevCode    
        self.PaidUnits        = PaidUnits       
        self.SubmProcIDQual   = SubmProcIDQual    # Type of code: HCPCS, etc. (usually HCPCS)  
        self.SubmProcID       = SubmProcID        # Procedure code originally submitted (if different)     
        self.SubmMod1         = SubmMod1        
        self.SubmMod2         = SubmMod2        
        self.SubmMod3         = SubmMod3       
        self.SubmMod4         = SubmMod4       
        self.SubmDesc         = SubmDesc       
        self.SubmUnits        = SubmUnits      
        self.Date1            = Date1           
        self.Date2            = Date2           
        self.POS              = POS             
        self.LineNum          = LineNum         
        self.RendProv         = RendProv        
        self.SvcSupQty        = SvcSupQty        # May implement this later if necessary   
        self.RmkCodes         = RmkCodes         # May implement this later if necessary  

class Loop2100:   #Fgrp.TSet().Detail().Claim loop=======
    def __init__(self, PatAcct='', Status='', ChgAmt=0.00, AllowedAmt=0.00, Deduct=0.00, CoIns=0.00, AdjCodes='', AdjAmt=0.00, PmtAmt=0.00, 
                        PatResp=0.00, CFICode='', ClmCtrlNum='', Facility='', FreqType='', DRGCode='', DRGWeight='', DischFract='', 
                        Patient='', Insured='', CorrPatIns='', SvcProvider='', XoverCarrier='', CorrPriPayor='', InPatAdj='', OutPatAdj='', OtherClmID='', 
                        RendProv='', ClmDate='', ClmContact='', ClmSuppInfo='', FacilityCode='', Service=''):
        self.PatAcct      = PatAcct       
        self.Status       = Status        
        self.ChgAmt       = ChgAmt        
        self.AllowedAmt   = AllowedAmt      #Must total this from service lines
        self.Deduct       = Deduct        
        self.CoIns        = CoIns         
        self.AdjCodes     = AdjCodes      
        self.AdjAmt       = AdjAmt        
        self.PmtAmt       = PmtAmt        
        self.PatResp      = PatResp       
        self.CFICode      = CFICode       
        self.ClmCtrlNum   = ClmCtrlNum    
        self.Facility     = Facility      
        self.FreqType     = FreqType      
        self.DRGCode      = DRGCode       
        self.DRGWeight    = DRGWeight     
        self.DischFract   = DischFract    
        self.Patient      = Patient         # As X12NM1 
        self.Insured      = Insured         # As X12NM1 
        self.CorrPatIns   = CorrPatIns      # As X12NM1 
        self.SvcProvider  = SvcProvider     # As X12NM1 
        self.XoverCarrier = XoverCarrier    # As X12NM1 
        self.CorrPriPayor = CorrPriPayor    # As X12NM1 
        self.InPatAdj     = InPatAdj        # As X12MIA
        self.OutPatAdj    = OutPatAdj     
        self.OtherClmID   = OtherClmID      # As X12MIA 
        self.RendProv     = RendProv        # As X12REF 
        self.ClmDate      = ClmDate       
        self.ClmContact   = ClmContact      # As X12PER
        self.ClmSuppInfo  = ClmSuppInfo     # As X12AMT
        self.FacilityCode = FacilityCode  
        self.Service      = Service         # As Loop2110

class Loop2000:     #Fgrp.TSet().Detail loop
    def __init__(self, HdrNum='', PrvSumInfo='', PrvSupSumInfo='', Claim=''):
        self.HdrNum            = HdrNum       
        self.PrvSumInfo        = PrvSumInfo   
        self.PrvSupSumInfo     = PrvSupSumInfo
        self.Claim             = Claim           #As Loop2100     



class X12ST_SE:  #FGrp.TSet()
    def __init__(self, ST=0, SE=0, TSType='', STControlNum='', CredDeb='', PmtMethod='', ChkAmt=0.00, ChgAmt=0.00, 
                        AllowedAmt=0.00, Deduct=0.00, CoIns=0.00, AdjAmt=0.00,PmtAmt=0.00, ChkDate='', ChkNum='', 
                        ReceiverID='', ProdDate='', TSTotalSegs=0, SEControlNum='', Payor='', Payee='', Detail='', 
                        dAdj='', cMOA='', cMIA='', PLBTot=0.00, ProviderAdj=''):
        self.ST            = ST           
        self.SE            = SE           
        self.TSType        = TSType       
        self.STControlNum  = STControlNum 
        self.CredDeb       = CredDeb      
        self.PmtMethod     = PmtMethod    
        self.ChkAmt        = ChkAmt       
        self.ChgAmt        = ChgAmt       #These must be totaled from service lines
        self.AllowedAmt    = AllowedAmt   #These must be totaled from service lines
        self.Deduct        = Deduct       #These must be totaled from service lines
        self.CoIns         = CoIns        #These must be totaled from service lines
        self.AdjAmt        = AdjAmt       #These must be totaled from service lines
        self.PmtAmt        = PmtAmt       #This is the amount before provider adjustments - These must be totaled from service lines
        self.ChkDate       = ChkDate      
        self.ChkNum        = ChkNum       
        self.ReceiverID    = ReceiverID   
        self.ProdDate      = ProdDate     
        self.TSTotalSegs   = TSTotalSegs  
        self.SEControlNum  = SEControlNum 
        self.Payor         = Payor        #As X12Payor
        self.Payee         = Payee        #As X12Payee
        self.Detail        = Detail       #As Loop2000
        self.dAdj          = dAdj         #As scripting.Dictionary
        self.cMOA          = cMOA         #As Collection
        self.cMIA          = cMIA         #As Collection
        self.PLBTot        = PLBTot       
        self.ProviderAdj   = ProviderAdj  #As X12PLB

class X12FGrp:
    def __init__(self, SubmitterID='', ProdStatus='', FileDate='', FILETIME='', CtlNumber='', TSet=''):
        self.SubmitterID   = SubmitterID 
        self.ProdStatus    = ProdStatus  
        self.FileDate      = FileDate    
        self.FILETIME      = FILETIME    
        self.CtlNumber     = CtlNumber   
        self.TSet          = TSet        #As X12ST_SE


#================RAW===========================
class X12Seg:
    def __init__(self, X12Elem):
        self.X12Elem = X12Elem          # individual elements that make up each segment

class X12Loop:
    def __init__(self, sANSIType='', lBeg=0, lEnd=0):
        self.sANSIType  = sANSIType     # What kind of transaction set - 835, 837, 997, etc
        self.lBeg       = lBeg          # segment number of ST record
        self.lEnd       = lEnd          # segment number of ST record

class X12_Raw:
    def __init__(self, sElemSep='*', sSubElemSep=':', sSegTerm='~', Seg=[], STLoop=[]):
        self.sElemSep    = sElemSep     # Element separator (usually "*" - 4th byte of file)
        self.sSubElemSep = sSubElemSep  # Sub-element separator (usually ":" - 105th byte of file)
        self.sSegTerm    = sSegTerm     # Segment terminator (usually "~" - 106th byte of file)
        self.Seg         = Seg          # As X12Seg       ' Original file, divided into segments
        self.STLoop      = STLoop       # As X12Loop      ' Location/type of each transaction set in file

#================RAW===========================



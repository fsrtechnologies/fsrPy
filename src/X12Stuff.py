class PatEmail:
    def __init__(self, ID='', Email=' ', LastName=' ', FirstName=' ', MI=' '):
        self.ID        = ID
        self.Email     = Email
        self.LastName  = LastName
        self.FirstName = FirstName
        self.MI        = MI

class X12NM1:  #Name - could be anybody...
    def __init__(self, Last='', First=' ', MI=' ', Suffix=' ', IDQual=' ', IDNum=' '):
        self.Last   = Last
        self.First  = First
        self.MI     = MI
        self.Suffix = Suffix
        self.IDQual = IDQual
        self.IDNum  = IDNum

class X12MIA:  #Inpatient adjustments - skipping this for now
    def __init__(self, CoveredDays='', PPSOutlier='', PsychDays='', DRGAmt=0.00, Remark1='', DispropAmt=0.00, MSP_PassThruAmt=0.00, PPS_Amt=0.00,
                       PPS_FSP_DRGAmt=0.00, PPS_HSP_DRGAmt=0.00, PPS_DSH_DRGAmt=0.00, OldCapAmt=0.00, PPS_IMEAmt=0.00, PPS_OHS_DRG_Amt=0.00, 
                       CostRepDayCnt='', PPS_OFS_DRGAmt=0.00, PPS_OutlierAmt=0.00, IndirTchAmt=0.00, NonPayPCAmt=0.00,
                       Remark2='', Remark3='', Remark4='', Remark5='', PPS_ExceptAmt=0.00)   
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
    def __init__(IDQual='', IDNum=''):
        self.IDQual = IDQual
        self.IDNum  = IDNum 


class X12AMT:
    def __init__(AmtQual='', Amt=0.00):
        self.AmtQual = AmtQual
        self.Amt     = Amt    

class X12QTY:
    def __init__(QuantQual='', Quantity=0):
        self.QuantQual= QuantQual
        self.Quantity = Quantity 

class X12LQ:
    def __init__(CodeListQual='', RemarkCode=''):
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
                       SubmUnits=0, Date1='', Date2='', POS='', LineNum='', RendProv, SvcSupQty, RmkCodes)
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
        self.SvcSupQty()      = SvcSupQty()      # May implement this later if necessary   
        self.RmkCodes()       = RmkCodes()       # May implement this later if necessary  

class Loop2100:   #Fgrp.TSet().Detail().Claim loop=======
    def __init__(self, PatAcct='', Status='', ChgAmt=0.00, AllowedAmt=0.00, Deduct=0.00, CoIns=0.00, AdjCodes='', AdjAmt=0.00, PmtAmt=0.00, 
                        PatResp=0.00, CFICode='', ClmCtrlNum='', Facility='', FreqType='', DRGCode='', DRGWeight='', DischFract='', 
                        Patient, Insured, CorrPatIns, SvcProvider, XoverCarrier, CorrPriPayor, InPatAdj, OutPatAdj='', OtherClmID, 
                        RendProv, ClmDate='', ClmContact, ClmSuppInfo, FacilityCode='', Service):
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
    def __init__(self, HdrNum='', PrvSumInfo='', PrvSupSumInfo='', Claim)
        self.HdrNum            = HdrNum       
        self.PrvSumInfo        = PrvSumInfo   
        self.PrvSupSumInfo     = PrvSupSumInfo
        self.Claim             = Claim           #As Loop2100     



class X12ST_SE:  #FGrp.TSet()
    def __init__(self, ST= 0, SE= 0, TSType= '', STControlNum= '', CredDeb= '', PmtMethod= '', ChkAmt= 0.00, ChgAmt= 0.00, AllowedAmt= 0.00, Deduct= 0.00, CoIns= 0.00, AdjAmt= 0.00, PmtAmt= 0.00, ChkDate= '', ChkNum= '', ReceiverID= '', ProdDate= '', TSTotalSegs= 0, SEControlNum= '', Payor, Payee, Detail, dAdj, cMOA, cMIA, PLBTot= 0.00, ProviderAdj):
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
    def __init__(self, SubmitterID='', ProdStatus='', FileDate='', FILETIME='', CtlNumber='', TSet)
        self.SubmitterID   = SubmitterID 
        self.ProdStatus    = ProdStatus  
        self.FileDate      = FileDate    
        self.FILETIME      = FILETIME    
        self.CtlNumber     = CtlNumber   
        self.TSet          = TSet        #As X12ST_SE


#================RAW===========================
class X12Seg:
    def __init__(self, X12Elem):
        self.X12Elem = X12Elem  # individual elements that make up each segment

class X12Loop:
    def __init__(self, sANSIType='', lBeg=0, lEnd=0)
        self.sANSIType  = sANSIType # What kind of transaction set - 835, 837, 997, etc
        self.lBeg       = lBeg      # segment number of ST record
        self.lEnd       = lEnd      # segment number of ST record

class X12_Raw:
    def __init__(self, sElemSep='',sSubElemSep='',sSegTerm='',Seg, STLoop)
        self.sElemSep    = sElemSep     # Element separator (usually "*", but check to be sure - 4th byte of file)
        self.sSubElemSep = sSubElemSep  # Sub-element separator (usually ":", but check to be sure - 105th byte of file)
        self.sSegTerm    = sSegTerm     # Segment terminator (usually "~", but check to be sure - 106th byte of file)
        self.Seg         = Seg          # As X12Seg       ' Original file, divided into segments (records)
        self.STLoop      = STLoop       # As X12Loop      ' Location/type of each transaction set in file

#================RAW===========================

class currency(float):
    def __init__(self,amount):
        self.amount = amount
    def __str__(self):
        temp = "%.2f" % self.amount
        profile = compile(r"(\d)(\d\d\d[.,])")
        while 1:
            temp, count = subn(profile,r"\1,\2",temp)
            if not count: break
        return temp


Const sPageBreak= "<page break>" & vbCrLf

Global.lPageLength=0
Global.lPageNum=0
lLineCount=0
lGroupCodesUsed=0
Global.bFootnotesLoaded=False
dFootNotes As scripting.Dictionary




Function PageHeader(uTSet  As X12ST_SE) ='', 
    Dim sTmp='', 
    Const sColHeader= "PERF PROV  SERVICE DATE(S)    POS  U   PROC  MODS     BILLED   ALLOWED  DEDUCT     COINS ADJ CODES    ADJ AMT   PROV PD"
    if lPageNum= 1 Then
        lLineCount= 13
        PageHeader= Format$(uTSet.Payor.Name, "!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") & "                                                                            MEDICARE" & vbNewLine
        PageHeader= PageHeader & Format$(uTSet.Payor.Add1, "!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") & "                                                                          REMITTANCE" & vbNewLine
        PageHeader= PageHeader & Format$(uTSet.Payor.CSZ, "!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") & "                                                                              NOTICE" & vbNewLine
        PageHeader= PageHeader & uTSet.Payor.ContactText & "  " & uTSet.Payor.ContactNum & vbNewLine
        PageHeader= PageHeader & vbNewLine
        PageHeader= PageHeader & "      " & Format$(uTSet.Payee.Name, "!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") & "                                                       PROVIDER #: " & Format$(uTSet.Payee.IDNum, "@@@@@@@@@@@") & vbNewLine
        PageHeader= PageHeader & "      " & Format$(uTSet.Payee.Add1, "!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") & "                                                       PAGE #:             " & Format$(lPageNum, "@@@") & vbNewLine
        PageHeader= PageHeader & "      " & Format$(uTSet.Payee.Add2, "!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") & "                                                       DATE:          " & uTSet.ProdDate & vbNewLine
        PageHeader= PageHeader & "      " & Format$(uTSet.Payee.CSZ, "!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") & "                                                       CHECK/EFT #: " & Format$(uTSet.ChkNum, "@@@@@@@@@@") & vbNewLine
        PageHeader= PageHeader & vbNewLine
        PageHeader= PageHeader & vbNewLine
        PageHeader= PageHeader & vbNewLine
        PageHeader= PageHeader & sColHeader
    Else
        lLineCount= 5
        PageHeader= "  " & Format$(uTSet.Payor.Name, "!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") & "                                                                          MEDICARE" & vbNewLine
        PageHeader= PageHeader & "  PROVIDER #: " & Format$(uTSet.Payee.IDNum, "@@@@@@@@@@@") & "                                            " & Format$(uTSet.Payee.Name, "!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") & "     REMITTANCE" & vbNewLine
        PageHeader= PageHeader & "  CHECK/EFT #: " & Format$(uTSet.ChkNum, "@@@@@@@@@@") & "               " & uTSet.ProdDate & "                     PAGE #: " & Format$(lPageNum, "@@@") & "                                 NOTICE" & vbNewLine
        PageHeader= PageHeader & vbNewLine
        PageHeader= PageHeader & sColHeader
    End If



Function ClaimHeader(lClaim =0,ByRef uClm As Loop2100)                                           ='', 
    Dim sTmp                                           ='', 
    lLineCount= lLineCount + 2
    sTmp= uClm.Patient.Last & ", " & uClm.Patient.First & " " & uClm.Patient.MI
    ClaimHeader= "_______________________________________________________________________________________________________________________" & vbCrLf
    ClaimHeader= ClaimHeader & Format(lClaim, "@@@@") & " "
    ClaimHeader= ClaimHeader & Format(uClm.PatAcct, "@@@@@@@@@@") & " " & Format(sTmp, "!@@@@@@@@@@@@@@@@@@@@@@@@@")
    ClaimHeader= ClaimHeader & "HIC " & Format(uClm.Patient.IDNum, "!@@@@@@@@@@@@") & " ICN " & Format(uClm.ClmCtrlNum, "!@@@@@@@@@@@@") & " " & uClm.OutPatAdj
    ClaimHeader= ClaimHeader








Function ServiceLine(ByRef uSvc                                            As Loop2110)                                           ='', 
    lLineCount= lLineCount + 1
    ServiceLine= Format$(uSvc.RendProv.IDNum, "!@@@@@@@@@")
    ServiceLine= ServiceLine & Format(uSvc.Date1, "@@@@@@@@@@") + " " + Format(uSvc.Date2, "@@@@@@@@@@")
    ServiceLine= ServiceLine & " " & Format(uSvc.POS, "@@") & " " & Format(uSvc.PaidUnits, "@@") & "  " & Format(uSvc.AdjudProcID, "@@@@@@")
    ServiceLine= ServiceLine & " " & Format(uSvc.AdjudMod1, "@@") + " " + Format(uSvc.AdjudMod1, "@@")
    ServiceLine= ServiceLine & " " & Format$(Format$(uSvc.ChgAmt, "#,###.00"), "@@@@@@@@") & "  " & Format$(Format$(uSvc.AllowedAmt, "#,###.00"), "@@@@@@@@")
    ServiceLine= ServiceLine & " " & Format$(Format$(uSvc.Deduct, "#,###.00"), "@@@@@@@@") & "  " & Format$(Format$(uSvc.CoIns, "#,###.00"), "@@@@@@@@")
    ServiceLine= ServiceLine & Format$(uSvc.AdjCodes, "!@@@@@@@@@@@@")
    ServiceLine= ServiceLine & " " & Format$(Format$(uSvc.AdjAmt, "#,###.00"), "@@@@@@@@") & "  " & Format$(Format$(uSvc.PmtAmt, "#,###.00"), "@@@@@@@@")







Function ClaimFooter(ByRef uClm                                            As Loop2100)                                           ='', 
    lLineCount= lLineCount + 3
    ClaimFooter= "PT RESP " & Format$(Format$(uClm.PatResp, "#,###.00"), "@@@@@@@@") & "             CLAIM TOTALS         "
    ClaimFooter= ClaimFooter & " " & Format$(Format$(uClm.ChgAmt, "#,###.00"), "@@@@@@@@") & "  " & Format$(Format$(uClm.AllowedAmt, "#,###.00"), "@@@@@@@@")
    ClaimFooter= ClaimFooter & " " & Format$(Format$(uClm.Deduct, "#,###.00"), "@@@@@@@@") & "  " & Format$(Format$(uClm.CoIns, "#,###.00"), "@@@@@@@@")
    ClaimFooter= ClaimFooter & "            "
    ClaimFooter= ClaimFooter & " " & Format$(Format$(uClm.AdjAmt, "#,###.00"), "@@@@@@@@") & "  " & Format$(Format$(uClm.PmtAmt, "#,###.00"), "@@@@@@@@") & vbNewLine
    if len(uClm.XoverCarrier.Last) > 0 Then
        ClaimFooter= ClaimFooter & "CLAIM INFORMATION FORWARDED TO:  " & Format$(uClm.XoverCarrier.Last, "!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") & "                                               "
        ClaimFooter= ClaimFooter & Format$(Format$((uClm.PmtAmt - uClm.AdjAmt), "#,###.00"), "@@@@@@@@") & " NET"
    Else
        ClaimFooter= ClaimFooter & "                                                                                                               "
        ClaimFooter= ClaimFooter & Format$(Format$((uClm.PmtAmt - uClm.AdjAmt), "#,###.00"), "@@@@@@@@") & " NET"
    End If







Function ReportFooter(lClaim                                           =0, , uTSet                                            As X12ST_SE, sPosition                                           ='', )                                           ='', 
    Dim sTotals                                           ='', , sGlossary                                           ='', 
    Dim lGlsLineCnt                                           =0, , lStep                                           =0, , vVar                                            As Variant, sTmp()                                           ='', 
    if Not bFootnotesLoaded:   LoadFootnotes
    sTotals= "_______________________________________________________________________________________________________________________" & vbNewLine
    sTotals= sTotals & vbNewLine
    sTotals= sTotals & "TOTALS:      # OF       BILLED      ALLOWED     DEDUCT      COINS       TOTAL      PROV PD         PROV        CHECK " & vbNewLine
    sTotals= sTotals & "           CLAIMS        AMT          AMT        AMT         AMT       RC-AMT        AMT        ADJ AMT         AMT  " & vbNewLine
    sTotals= sTotals & "             " & Format(lClaim, "@@@@") & "    " & Format$(Format$(uTSet.ChgAmt, "#,###.00"), "@@@@@@@@@") & "    " & Format$(Format$(uTSet.AllowedAmt, "#,###.00"), "@@@@@@@@@")
    sTotals= sTotals & "  " & Format$(Format$(uTSet.Deduct, "#,###.00"), "@@@@@@@@@") & "  " & Format$(Format$(uTSet.CoIns, "#,###.00"), "@@@@@@@@@")
    sTotals= sTotals & "   " & Format$(Format$(uTSet.AdjAmt, "#,###.00"), "@@@@@@@@@") & "    " & Format$(Format$(uTSet.PmtAmt, "#,###.00"), "@@@@@@@@@")
    sTotals= sTotals & "    " & Format$(Format$(uTSet.PLBTot, "#,###.00"), "@@@@@@@@@") & "    " & Format$(Format$(uTSet.ChkAmt, "#,###.00"), "@@@@@@@@@") & vbNewLine
    sTotals= sTotals & vbNewLine
    ' Line count to this point: 6
    sGlossary= sGlossary & "GLOSSARY: Group, Reason, MOA, Remark and Adjustment codes" & vbNewLine
    lGlsLineCnt= 1
    
    if lGroupCodesUsed And 16 Then
        sGlossary= sGlossary & "PR - Patient Responsibility" & vbNewLine
        lGlsLineCnt= lGlsLineCnt + 1
    End If
    if lGroupCodesUsed And 8 Then
        sGlossary= sGlossary & "CO - Contractual Obligation" & vbNewLine
        lGlsLineCnt= lGlsLineCnt + 1
    End If
    if lGroupCodesUsed And 4 Then
        sGlossary= sGlossary & "PI - Payor Initiated" & vbNewLine
        lGlsLineCnt= lGlsLineCnt + 1
    End If
    if lGroupCodesUsed And 2 Then
        sGlossary= sGlossary & "CR - Corrections and Reversals" & vbNewLine
        lGlsLineCnt= lGlsLineCnt + 1
    End If
    if lGroupCodesUsed And 1 Then
        sGlossary= sGlossary & "OA - Other Adjustment" & vbNewLine
        lGlsLineCnt= lGlsLineCnt + 1
    End If
    
    for Each vVar In uTSet.dAdj
        if dFootNotes.Exists(vVar) Then
            sTmp()= Split(dFootNotes.Item(vVar), "*")
            sGlossary= sGlossary & Format$(vVar, "!@@@@") & "  " & sTmp(0) & vbNewLine
            lGlsLineCnt= lGlsLineCnt + 1
            if UBound(sTmp) > 1 Then
                for lStep= 1 To UBound(sTmp())
                    sGlossary= sGlossary & "      " & sTmp(lStep) & vbNewLine
                    lGlsLineCnt= lGlsLineCnt + 1
                Next
            End If
        Else
            sGlossary= sGlossary & Format$(vVar, "!@@@@") & "  No definition available." & vbNewLine
            lGlsLineCnt= lGlsLineCnt + 1
        End If
    Next
    
    if lLineCount + 6 > lPageLength Then
        ReportFooter= sPageBreak & sTotals & sGlossary
    Else
        if lLineCount + 6 + lGlsLineCnt > lPageLength Then
            ReportFooter= sTotals & sPageBreak & sGlossary
        Else
            ReportFooter= sTotals & sGlossary
        End If
    End If
    lLineCount= 0
    lPageNum= 1
    'If sPosition= "mid":   ReportFooter= ReportFooter & sPageBreak
    if sPosition= "mid":   ReportFooter= ReportFooter & "\"                          ' We'll be splitting into tabs based on this character






Sub LoadFootnotes()
    Dim iInFile                                            As Integer, iStep                                            As Integer, sFile(0 To 1)                                           ='', , sStr                                           ='', , sTmp()                                           ='', 
    On Error GoTo Error
    Set dFootNotes= New scripting.Dictionary
    iInFile= FreeFile
    sFile(0)= App.Path & "\RsnCodes.dat"
    sFile(1)= App.Path & "\MOACodes.dat"
    for iStep= 0 To UBound(sFile())
        Open sFile(iStep) for Input                                            As #iInFile
        while Not EOF(iInFile)
            Line Input #iInFile, sStr
            sTmp= Split(sStr, "~")
            if Not dFootNotes.Exists(sTmp(0)):   dFootNotes.Add sTmp(0), sTmp(1)
        Loop
        Close #iInFile
    Next
    bFootnotesLoaded= True
    Exit Sub
Error:
    sStr= "Can't load footnotes!  Make sure these files - RsnCodes.dat, MOACodes.dat and MIACodes.dat - exist in the FSRBBS folder.  Error:" & Err.Description
    MsgBox (sStr)















Function sANSI_835(ByRef Raw                                            As X12_Raw)                                           ='', 
    ' we receive an array of X12 elements,
    ' plus an array holding positions of the beginning(ST) and end(SE) of each 835 loop in the file.
On Error GoTo Error
    Dim iRsltFile                                            As Integer
    Dim lStep                                           =0, , lA                                           =0, , lB                                           =0, , lC                                           =0, , lFUtmp                                           =0, 
    Dim lLXCount                                           =0, , lCLPCount                                           =0, , lSVCCount                                           =0, , lLQCount                                           =0, , lPLBCount                                           =0, 
    Dim sStr1                                           ='', , sSubElemSep                                           ='', , sTSet                                           ='', , sFGrp                                           ='', 
    Dim sTmp()                                           ='', , sLevel                                           ='', , sFUHolder                                           ='', 
    Dim b2110                                            As Boolean, bClmDirty                                            As Boolean, bSvcDirty                                            As Boolean, bPayor                                            As Boolean
    Dim FGrp                                            As X12FGrp
    sSubElemSep= ":"
    sANSI_835= "835.tmp"
    iRsltFile= FreeFile
    Open sANSI_835 for Output                                            As #iRsltFile
    FGrp.SubmitterID= Trim$(Raw.Seg(0).X12Elem(8)) + " - "
    FGrp.ProdStatus= Raw.Seg(0).X12Elem(15)
    FGrp.FileDate= sFixYYMMDD(Raw.Seg(0).X12Elem(9))
    FGrp.FILETIME= Mid$(Raw.Seg(0).X12Elem(10), 1, 2) + ":" + Mid$(Raw.Seg(0).X12Elem(10), 3, 2)
    FGrp.CtlNumber= Raw.Seg(Raw.STLoop(0).lBeg).X12Elem(2)
    ReDim FGrp.TSet(0 To UBound(Raw.STLoop))
    lLXCount= 0
    bSvcDirty= False
    bClmDirty= False
    lPageNum= 1
    lLineCount= 0
    for lA= 0 To (UBound(Raw.STLoop))
        Set FGrp.TSet(lA).dAdj= New scripting.Dictionary
        sLevel= "Header"
        for lStep= (Raw.STLoop(lA).lBeg + 1) To (Raw.STLoop(lA).lEnd - 1)
            FGrp.TSet(lA).PLBTot= 0 ' until I have some real PLB records to play with
            With Raw.Seg(lStep)
            sFUHolder= ""
            for lFUtmp= 0 To UBound(.X12Elem())
                sFUHolder= sFUHolder & "*" & .X12Elem(lFUtmp)
            Next
            ' MsgBox sFUHolder
            Select Case .X12Elem(0)
                '=====================  Header info====================================================
                Case "BPR"
                    sLevel= "Header"
                    FGrp.TSet(lA).ChkAmt= .X12Elem(2)
                    FGrp.TSet(lA).CredDeb= .X12Elem(3)
                    FGrp.TSet(lA).PmtMethod= .X12Elem(4)
                    FGrp.TSet(lA).ChkDate= .X12Elem(6)
                        
                '============================= Detail info==================================================
                Case "LX"   ' Head of 2000 loop - "detail"
                    ' Print page header after reading header info, but before reading claims - but Level still needs to be Header, not Detail
                    if lLXCount= 0:   Print #iRsltFile, PageHeader(FGrp.TSet(lA))
                    '=================== - AnviCare's 835s have LX and CLP records in funky order=====
                    '== - copied this from CLP section to avoid crashes - version 6.1.0, 4 Sep 2006
                    if bSvcDirty Then
                        Print #iRsltFile, ServiceLine(FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount))
                        Print #iRsltFile, ClaimFooter(FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount))
                        bSvcDirty= False
                    End If
                    '=================== - end AnviCare fix===========================================
                    sLevel= "Detail"
                    lCLPCount= 0
                    lSVCCount= 0
                    lLXCount= lLXCount + 1
                    ReDim Preserve FGrp.TSet(lA).Detail(0 To lLXCount)
                
                '============================= Claim info==================================================
                Case "CLP"   ' Head of 2100 loop - "claim"
                    sLevel= "Claim"
                    if bSvcDirty Then
                        Print #iRsltFile, ServiceLine(FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount))
                        Print #iRsltFile, ClaimFooter(FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount))
                        bSvcDirty= False
                    End If
                    if lLineCount > lPageLength - 13 Then
                        lPageNum= lPageNum + 1
                        Print #iRsltFile, sPageBreak
                        Print #iRsltFile, PageHeader(FGrp.TSet(lA))
                    End If
                    bClmDirty= True ' to make sure we don't orphan the last claim
                    lSVCCount= 0
                    lCLPCount= lCLPCount + 1
                    ReDim Preserve FGrp.TSet(lA).Detail(lLXCount).Claim(0 To lCLPCount)
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).PatAcct= .X12Elem(1)
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Status= .X12Elem(2)
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).ChgAmt= curZeroChk(.X12Elem(3))
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).PmtAmt= curZeroChk(.X12Elem(4))
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).PatResp= curZeroChk(.X12Elem(5))
                    'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).CFICode= .X12Elem(6)
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).ClmCtrlNum= .X12Elem(7)
                    ' Cascade provider from TSet level - will override if different at claim level
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).RendProv.IDNum= FGrp.TSet(lA).Payee.IDNum
                    
                '=====================  Service info====================================================
                Case "SVC"   ' Head of 2110 loop - Service info
                    sLevel= "Service" ' determines behavior of CAS info
                    if lSVCCount= 0:   '  if this is the first service on this claim, print the claim header
                        Print #iRsltFile, ClaimHeader(lCLPCount, FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount))
                    else:                    '     Otherwise, print the previous service
                        Print #iRsltFile, ServiceLine(FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount))
                    End If
                    bSvcDirty= True  '  to make sure we don't orphan the last service line
                    lLQCount= 0
                    lSVCCount= lSVCCount + 1
                    ReDim Preserve FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(0 To lSVCCount)
                    sTmp= Split(.X12Elem(1), Mid$(.X12Elem(1), 3, 1)) ' According to spec, the separator SHOULD be a colon, but sometimes it's actually a greater-than...
                    'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AdjudProcIDQual= sTmp(0)
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AdjudProcID= sTmp(1)
                    if (UBound(sTmp) > 1):   FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AdjudMod1= sTmp(2) else:   FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AdjudMod1= "11"
                    if (UBound(sTmp) > 2):   FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AdjudMod2= sTmp(3) else:   FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AdjudMod2= "22"
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).ChgAmt= curZeroChk(.X12Elem(2))
                    FGrp.TSet(lA).ChgAmt= FGrp.TSet(lA).ChgAmt + curZeroChk(.X12Elem(2))
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).PmtAmt= curZeroChk(.X12Elem(3))
                    FGrp.TSet(lA).PmtAmt= FGrp.TSet(lA).PmtAmt + curZeroChk(.X12Elem(3))
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).PaidUnits= .X12Elem(5)
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).Date2= "          "
                    if (UBound(.X12Elem) > 5) Then
                        if (len(.X12Elem(6)) > 2) Then
                            sTmp= Split(.X12Elem(6), Mid$(.X12Elem(6), 3, 1)) ' According to spec, the separator SHOULD be a colon, but sometimes it's actually a greater-than...
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).SubmProcIDQual= sTmp(0)
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).SubmProcID= sTmp(1)
                            if (UBound(sTmp) > 1):   FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).SubmMod1= sTmp(2)
                            if (UBound(sTmp) > 2):   FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).SubmMod2= sTmp(3)
                            'If (UBound(sTmp) > 3):   FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).SubmMod3= sTmp(4)
                            'If (UBound(sTmp) > 4):   FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).SubmMod4= sTmp(5)
                            'If (UBound(sTmp) > 5):   FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).SubmDesc= sTmp(6)
                            'If (UBound(.X12Elem) > 6):   FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).SubmUnits= .X12Elem(7)
                        End If
                    End If
                    ' Cascade provider number from claim level - if different, will override
                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).RendProv.IDNum= FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).RendProv.IDNum
                
                Case "TRN"
                    FGrp.TSet(lA).ChkNum= .X12Elem(2)
                    ' MsgBox FGrp.TSet(lA).ChkNum
                
                Case "PLB" ' Provider-level adjustments
                    lPLBCount= lPLBCount + 1
                    ReDim Preserve FGrp.TSet(lA).ProviderAdj(0 To lPLBCount)
                    FGrp.TSet(lA).ProviderAdj(lPLBCount).ProvID= .X12Elem(1)
                    FGrp.TSet(lA).ProviderAdj(lPLBCount).date= .X12Elem(2)
                    sTmp= Split(.X12Elem(3), sSubElemSep)
                    FGrp.TSet(lA).ProviderAdj(lPLBCount).RsnCode1= sTmp(0)
                    if UBound(sTmp) > 0:   FGrp.TSet(lA).ProviderAdj(lPLBCount).ID1= sTmp(1) ' in case there were no sub-elements
                    FGrp.TSet(lA).ProviderAdj(lPLBCount).Amt1= curZeroChk(.X12Elem(4))
                    FGrp.TSet(lA).PLBTot= FGrp.TSet(lA).PLBTot + curZeroChk(.X12Elem(4))
                    if UBound(.X12Elem) > 4 Then
                        sTmp= Split(.X12Elem(5), sSubElemSep)
                        FGrp.TSet(lA).ProviderAdj(lPLBCount).RsnCode2= sTmp(0)
                        FGrp.TSet(lA).ProviderAdj(lPLBCount).ID2= sTmp(1)
                        FGrp.TSet(lA).ProviderAdj(lPLBCount).Amt2= curZeroChk(.X12Elem(6))
                        FGrp.TSet(lA).PLBTot= FGrp.TSet(lA).PLBTot + curZeroChk(.X12Elem(6))
                    End If
                    if UBound(.X12Elem) > 6 Then
                        sTmp= Split(.X12Elem(7), sSubElemSep)
                        FGrp.TSet(lA).ProviderAdj(lPLBCount).RsnCode3= sTmp(0)
                        FGrp.TSet(lA).ProviderAdj(lPLBCount).ID3= sTmp(1)
                        FGrp.TSet(lA).ProviderAdj(lPLBCount).Amt3= curZeroChk(.X12Elem(8))
                        FGrp.TSet(lA).PLBTot= FGrp.TSet(lA).PLBTot + curZeroChk(.X12Elem(8))
                    End If
                    ' In future, if more than 3 sets of provider-level adjustments are necessary, we can expand...
                
                Case "REF"
                    Select Case .X12Elem(1)
                        '============== TSet-level codes:============================================
                        Case "EV" ' Receiver ID
                        Case "F2" ' Version number
                        Case "2U" ' Payor ID (?!)
                        Case "EO"
                            FGrp.SubmitterID= .X12Elem(2)
                        Case "HI" ' Health Industry Number (HIN):
                        Case "NF" ' National Association of Insurance Commissioners (NAIC) Code
                        '======= Service ID codes:================================================
                        Case "1S" ' Ambulatory Patient Group (APG) Number
                        Case "6R" ' Provider Control Number (line number ID's, if sent in original 837 file)
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).LineNum= .X12Elem(2)
                        Case "BB" ' Authorization Number
                        Case "E9" ' Attachment Code
                        Case "G1" ' Prior Authorization Number
                        Case "G3" ' Predetermination of Benefits Identification Number
                        Case "LU" ' Location Number
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).POS= .X12Elem(2)
                        Case "RB" ' Rate code number
                        '========= Rendering provider ID codes - if service level differs from claim level======================
                        Case "1A" '  Blue Cross Provider Number
                        Case "1B" '  Blue Shield Provider Number
                        Case "1C" '  Medicare Provider Number
                            Select Case sLevel
                                Case "Header"
                                    FGrp.TSet(lA).Payee.IDNum= .X12Elem(2)
                                Case "Detail" ' shouldn't appear at detail level
                                Case "Claim"
                                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).RendProv.IDNum= .X12Elem(2)
                                Case "Service"
                                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).RendProv.IDNum= .X12Elem(2)
                            End Select
                        Case "1D" '  Medicaid Provider Number
                        Case "1G" '  Provider UPIN Number
                        Case "1H" '  CHAMPUS Identification Number
                        Case "1J" '  Facility ID Number
                        Case "HPI" ' HCFA NPI (National Provider Identifier)
                        Case "SY" '  Social Security Number
                        Case "TJ" '  Federal Taxpayer’s Identification Number
                   End Select
                    
                Case "DTM"  ' Date and time - can appear at various levels
                            ' Spec says dates should be CCYYMMDD, but currently they're just YYMMDD
                    if (Len(.X12Elem(2))= 8):   .X12Elem(2)= sFixCCYYMMDD(.X12Elem(2))
                    if (Len(.X12Elem(2))= 6):   .X12Elem(2)= sFixYYMMDD(.X12Elem(2))
                    Select Case .X12Elem(1)
                        Case "405"  ' Production date of 835 (who cares?)
                            FGrp.TSet(lA).ProdDate= .X12Elem(2)
                        Case "050"  ' Date claim was received by payer
                            'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).ClmDate= .X12Elem(2)
                        Case "472"  ' Single date of service
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).Date1= .X12Elem(2)
                        Case "150"  ' "From" date of service
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).Date1= .X12Elem(2)
                        Case "151"  ' "Through" date of service
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).Date2= .X12Elem(2)
                    End Select
                            
                Case "N1"  ' Payor or payee info
                    Select Case .X12Elem(1)
                        Case "PR"
                            bPayor= True  ' to interpret N3 and N4 lines
                            if UBound(.X12Elem) > 1:   FGrp.TSet(lA).Payor.Name= .X12Elem(2) else:   FGrp.TSet(lA).Payor.Name= "Medicare"
                            FGrp.TSet(lA).Payor.Add1= " "
                            FGrp.TSet(lA).Payor.Add2= " "
                            FGrp.TSet(lA).Payor.CSZ= " "
                        Case "PE"
                            bPayor= False ' to interpret N3 and N4 lines
                            FGrp.TSet(lA).Payee.Name= .X12Elem(2)
                            if len(FGrp.TSet(lA).Payee.Name)= 0:   FGrp.TSet(lA).Payee.Name= "No payee information provided"
                            if .X12Elem(3) <> "FI":   FGrp.TSet(lA).Payee.IDNum= .X12Elem(4)  ' if it's not the tax ID,:   use it                                            As the Payee ID
                            FGrp.TSet(lA).Payee.Add1= " "
                            FGrp.TSet(lA).Payee.Add2= " "
                            FGrp.TSet(lA).Payee.CSZ= " "
                    End Select
                    
                Case "N3"  ' Payor or payee info
                    if bPayor Then
                        FGrp.TSet(lA).Payor.Add1= .X12Elem(1)
                        if UBound(.X12Elem) > 1:   FGrp.TSet(lA).Payor.Add2= .X12Elem(2)
                    Else
                        FGrp.TSet(lA).Payee.Add1= .X12Elem(1)
                        if UBound(.X12Elem) > 1:   FGrp.TSet(lA).Payee.Add2= .X12Elem(2)
                    End If
                    
                Case "N4"  ' Payor or payee info
                    if bPayor Then
                        FGrp.TSet(lA).Payor.CSZ= .X12Elem(1) & ", " & .X12Elem(2) & " " & Format$(.X12Elem(3), "@@@@@-@@@@")
                    Else
                        FGrp.TSet(lA).Payee.CSZ= .X12Elem(1) & ", " & .X12Elem(2) & " " & Format$(.X12Elem(3), "@@@@@-@@@@")
                    End If
                    
                Case "PER"
                    FGrp.TSet(lA).Payor.ContactText= .X12Elem(2)
                    Select Case .X12Elem(3)
                        Case "TE"
                            FGrp.TSet(lA).Payor.ContactNum= Format$(.X12Elem(4), "(###)###-####")
                        Case "FX"
                            FGrp.TSet(lA).Payor.ContactNum= "FAX: " & Format$(.X12Elem(4), "(###)###-####")
                        Case "EM"
                            FGrp.TSet(lA).Payor.ContactNum= "email: " & .X12Elem(4)
                    End Select
                        
                Case "CAS"   ' Adjustment info
                    Select Case .X12Elem(1) ' Load group-code definitions for glossary...
                        Case "PR"
                            lGroupCodesUsed= lGroupCodesUsed Or 16
                        Case "CO"
                            lGroupCodesUsed= lGroupCodesUsed Or 8
                        Case "PI"
                            lGroupCodesUsed= lGroupCodesUsed Or 4
                        Case "CR"
                            lGroupCodesUsed= lGroupCodesUsed Or 2
                        Case "OA"
                            lGroupCodesUsed= lGroupCodesUsed Or 1
                    End Select
                    if sLevel= "Service":    ' Are we at the service level, or claim level?  if service level, then...
                        lB= 2
                        Do Until lB >= UBound(.X12Elem)
                            Select Case .X12Elem(lB)
                                Case "1"
                                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).Deduct= curZeroChk(.X12Elem(lB + 1))
                                    FGrp.TSet(lA).Deduct= FGrp.TSet(lA).Deduct + curZeroChk(.X12Elem(lB + 1))
                                Case "2"
                                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).CoIns= curZeroChk(.X12Elem(lB + 1))
                                    FGrp.TSet(lA).CoIns= FGrp.TSet(lA).CoIns + curZeroChk(.X12Elem(lB + 1))
                                Case Else
                                    sStr1= " " & .X12Elem(1) & .X12Elem(lB)
                                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AdjCodes= FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AdjCodes & sStr1
                                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AdjAmt= FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AdjAmt + curZeroChk(.X12Elem(lB + 1))
                                    FGrp.TSet(lA).AdjAmt= FGrp.TSet(lA).AdjAmt + curZeroChk(.X12Elem(lB + 1))
                                    if Not FGrp.TSet(lA).dAdj.Exists(.X12Elem(lB)):   FGrp.TSet(lA).dAdj.Add .X12Elem(lB), sStr1
                                    
                            End Select
                            lB= lB + 3
                        Loop
                    else:    ' otherwise we must be at the claim level, in which case...
                        lB= 2
                        Do Until lB >= UBound(.X12Elem)
                            Select Case .X12Elem(lB)
                                Case "1"
                                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Deduct= curZeroChk(.X12Elem(lB + 1))
                                    'FGrp.TSet(lA).Deduct= FGrp.TSet(lA).Deduct + curZeroChk(.X12Elem(lB + 1))
                                Case "2"
                                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).CoIns= curZeroChk(.X12Elem(lB + 1))
                                    'FGrp.TSet(lA).CoIns= FGrp.TSet(lA).CoIns + curZeroChk(.X12Elem(lB + 1))
                                Case Else
                                    sStr1= " " & .X12Elem(1) & .X12Elem(lB)
                                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).AdjCodes= FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).AdjCodes & sStr1
                                    FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).AdjAmt= FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).AdjAmt + curZeroChk(.X12Elem(lB + 1))
                                    'FGrp.TSet(lA).AdjAmt= FGrp.TSet(lA).AdjAmt + curZeroChk(.X12Elem(lB + 1))
                                    if Not FGrp.TSet(lA).dAdj.Exists(.X12Elem(lB)):   FGrp.TSet(lA).dAdj.Add .X12Elem(lB), sStr1
                            End Select
                            lB= lB + 3
                        Loop
                    End If
                
                Case "NM1"  ' Name - could be patient, insured, secondary insurance...
                    Select Case .X12Elem(1)
                        Case "QC" ' Patient name
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Patient.Last= .X12Elem(3)
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Patient.First= .X12Elem(4)
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Patient.MI= .X12Elem(5)
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Patient.Suffix= .X12Elem(7)
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Patient.IDQual= .X12Elem(8)
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Patient.IDNum= .X12Elem(9)
                        Case "TT" ' Crossover carrier name
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).XoverCarrier.Last= .X12Elem(3)
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).XoverCarrier.IDQual= .X12Elem(8)
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).XoverCarrier.IDNum= .X12Elem(9)
                        Case "IL" ' Insured's name
                            'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Insured.Last= .X12Elem(3)
                            'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Insured.First= .X12Elem(4)
                            'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Insured.MI= .X12Elem(5)
                            'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Insured.Suffix= .X12Elem(7)
                            'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Insured.IDQual= .X12Elem(8)
                            'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Insured.IDNum= .X12Elem(9)
                        Case "74" ' Corrected insured's name
                        Case "82" ' Service provider's name
                        Case "PR" ' Corrected priority payer
                    End Select
                
                Case "MIA"  ' Inpatient adjudication info
                
                Case "MOA"  ' Outpatient adjudication info
                    for lB= 3 To UBound(.X12Elem())
                        FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).OutPatAdj= FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).OutPatAdj & " " & .X12Elem(lB)
                        if Not FGrp.TSet(lA).dAdj.Exists(.X12Elem(lB)):   FGrp.TSet(lA).dAdj.Add .X12Elem(lB), .X12Elem(lB)
                    Next
            
                Case "AMT"   ' Service supplemental amount
                    Select Case .X12Elem(1)
                        Case "B6"  ' Allowed - Actual
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AllowedAmt= curZeroChk(.X12Elem(2))
                            ' Add allowed amt for this service to running total for claim and for entire 835
                            FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).AllowedAmt= FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).AllowedAmt + FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).AllowedAmt
                            FGrp.TSet(lA).AllowedAmt= FGrp.TSet(lA).AllowedAmt + curZeroChk(.X12Elem(2))
                            
                        Case "DY"  ' Per Day Limit - NOT ADVISED
                        Case "KH"  ' Deduction Amount - Late Filing Reduction
                        Case "NE"  ' Net Billed - NOT ADVISED
                        Case "T"   ' Tax
                        Case "T2"  ' Total Claim Before Taxes
                        Case "ZK"  ' Fed. Medicare or Medicaid Payment Mandate - Cat 1
                        Case "ZL"  ' Fed. Medicare or Medicaid Payment Mandate - Cat 2
                        Case "ZM"  ' Fed. Medicare or Medicaid Payment Mandate - Cat 3
                        Case "ZN"  ' Fed. Medicare or Medicaid Payment Mandate - Cat 4
                        Case "ZO"  ' Fed. Medicare or Medicaid Payment Mandate - Cat 5
                    End Select
                
                Case "QTY"   ' Service supplemental quantity - may implement later
                    Select Case .X12Elem(2)
                        Case "NE"  ' Non - Covered - Estimated
                        Case "ZK"  ' Fed. Medicare or Medicaid Payment Mandate - Cat 1
                        Case "ZL"  ' Fed. Medicare or Medicaid Payment Mandate - Cat 2
                        Case "ZM"  ' Fed. Medicare or Medicaid Payment Mandate - Cat 3
                        Case "ZN"  ' Fed. Medicare or Medicaid Payment Mandate - Cat 4
                        Case "ZO"  ' Fed. Medicare or Medicaid Payment Mandate - Cat 5
                    End Select
                
                Case "LQ"   ' Healthcare Remark Codes
                    'lLQCount= lLQCount + 1
                    'ReDim Preserve FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).RmkCodes(0 To lLQCount)
                    'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).RmkCodes(lLQCount).CodeListQual= .X12Elem(1)
                    'FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount).RmkCodes(lLQCount).RemarkCode= .X12Elem(2)
                    
            End Select
            End With
        Next
        '  Cleanup at the end of each ST-SE loop...
        if bSvcDirty Then
            Print #iRsltFile, ServiceLine(FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount).Service(lSVCCount))
            bSvcDirty= False
        End If
        if bClmDirty Then
            Print #iRsltFile, ClaimFooter(FGrp.TSet(lA).Detail(lLXCount).Claim(lCLPCount))
            bClmDirty= False
        End If
        if lA= UBound(Raw.STLoop) Then
        ' if lA= (UBound(Raw.STLoop) - 1):    ' last tab had two 835's - 2May2007
            Print #iRsltFile, ReportFooter(lCLPCount, FGrp.TSet(lA), "end")
        Else
            Print #iRsltFile, ReportFooter(lCLPCount, FGrp.TSet(lA), "mid")
        End If
        lLXCount= 0
        sLevel= "Header"
    
    Next
    Close #iRsltFile
    Exit Function
    
Error:
    sStr1= "ANSI 835 processing failed!  Error:" & Err.Description
    Print #iRsltFile, vbNewLine + sStr1
    Close #iRsltFile




Function sANSI_997(ByRef Raw                                            As X12_Raw)                                           ='', 
    'on error GoTo Error
    Dim iRsltFile                                            As Integer
    Dim lStep                                           =0, , lX                                           =0, , lY                                           =0, 
    Dim sStr1                                           ='', , sStr2                                           ='', , sStr3                                           ='', , sSubElemSep                                           ='', , sTSet                                           ='', 
    
    sANSI_997= "997.tmp"
    iRsltFile= FreeFile
    Open sANSI_997 for Output                                            As #iRsltFile
    
    sStr1= "Submitter ID: " + Trim$(Raw.Seg(0).X12Elem(8)) + " - "
    if Raw.Seg(0).X12Elem(15)= "P":   sStr1= sStr1 + "Production" else:   if Raw.Seg(0).X12Elem(15)= "T":   sStr1= sStr1 + "Test mode"
    sStr1= sStr1 + vbTab + vbTab + vbTab + vbTab + "File date: " + sFixYYMMDD(Raw.Seg(0).X12Elem(9)) + "     "
    sStr1= sStr1 + " Time: " + Mid$(Raw.Seg(0).X12Elem(10), 1, 2) + ":" + Mid$(Raw.Seg(0).X12Elem(10), 3, 2)
    Print #iRsltFile, sStr1
    
    Print #iRsltFile, vbTab + vbTab + vbTab + "997 Functional Acknowledgment - Control number " + Raw.Seg(Raw.STLoop(lY).lBeg).X12Elem(2) + vbNewLine
   
    for lY= 0 To UBound(Raw.STLoop)
        for lStep= (Raw.STLoop(lY).lBeg + 1) To (Raw.STLoop(lY).lEnd - 1)
        With Raw.Seg(lStep)
            Select Case .X12Elem(0)
                Case "AK1"
                    Print #iRsltFile, "This report covers your submission # " + .X12Elem(2) + vbNewLine
                Case "AK2"
                    sTSet= .X12Elem(2)
                    Print #iRsltFile, "Transaction set " + sTSet + vbNewLine
                Case "AK3"
                    sStr1= vbTab + "Error in segment " + .X12Elem(1) + " at count " + Raw.Seg(lStep).X12Elem(2)
                    sStr1= sStr1 + ", loop " + .X12Elem(3) + " - error is '"
                    sStr1= sStr1 + Choose(CSng(.X12Elem(4)), "Unrecognized segment ID", "Unexpected segment", "Mandatory segment missing", "Loop Occurs Over Maximum Times", "Segment Exceeds Maximum Use", "Segment Not in Defined Transaction Set", "Segment Not in Proper Sequence", "Segment Has Data Element Errors") + "'"
                    Print #iRsltFile, sStr1 + vbNewLine
                Case "AK4"
                    sStr1= vbTab + "Error at position " + .X12Elem(1) + "; "
                    if len(.X12Elem(2)) <> 0:   sStr1= sStr1 + "data element ref: " + .X12Elem(2) + "; "
                    sStr1= sStr1 + "error code: " + Choose(CSng(.X12Elem(3)), "Mandatory data element missing", "Conditional required data element missing", "Too many data elements", "Data element too short", "Data element too long", "Invalid character in data element", "Invalid code value", "Invalid Date", "Invalid Time", "Exclusion Condition Violated") + " "
                    if (UBound(.X12Elem) > 3) Then
                        sStr1= sStr1 + "What you sent: " + .X12Elem(4)
                    Else
                        sStr1= sStr1 + vbNewLine + vbTab + vbTab + "Sorry, don't have a copy of original billing data"
                    End If
                    Print #iRsltFile, sStr1 + vbNewLine
                    
                Case "AK5"
                    sStr1= .X12Elem(1)
                    Print #iRsltFile, "Status for transaction set " + sTSet + ": " + Switch(sStr1= "A", "Accepted", sStr1= "E", "Accepted, But Errors Were Noted", sStr1= "M", "Rejected, Message Authentication Code (MAC) Failed", sStr1= "R", "Rejected", sStr1= "W", "Rejected, Assurance Failed Validity Tests", sStr1= "X", "Rejected, Content After Decryption Could Not Be Analyzed") + vbNewLine
                    for lX= 2 To UBound(.X12Elem)
                        if len(.X12Elem(lX)) <> 0 Then
                            sStr1= .X12Elem(lX)
                            sStr1= Choose(CSng(sStr1), "TSet Not Supported", "TSet Trailer Missing", "TSet Control Number in Header and Trailer Do Not Match", "Number of Included Segments Does Not Match Actual Count", "One or More Segments in Error", "Missing or Invalid sTSet Identifier", "Missing or Invalid sTSet Control Number", "Authentication Key Name Unknown", "Encryption Key Name Unknown", "Requested Service (Authentication or Encrypted) Not Available", "Unknown Security Recipient", "Incorrect Message Length (Encryption Only)", "Message Authentication Code Failed", "Unknown Security Originator", "Syntax Error in Decrypted Text", "Security Not Supported", "TSet Control Number Not Unique within the Functional Group", "S3E Security End Segment Missing for S3S Security Start Segment", "S3S Security Start Segment Missing for S3E Security End Segment", "S4E Security End Segment Missing for S4S Security Start Segment", "S4S Security Start Segment Missing for S4E Security End Segment ")
                            Print #iRsltFile, "Error code(s) for this TSet: " + sStr1 + vbNewLine
                        End If
                    Next
                Case "AK9"
                    sStr1= .X12Elem(1)
                    Print #iRsltFile, "Status for entire billing file: " + Switch(sStr1= "A", "Accepted", sStr1= "E", "Accepted, But Errors Were Noted", sStr1= "M", "Rejected, Message Authentication Code (MAC) Failed", sStr1= "P", "Partially Accepted, At Least One sTSet Was Rejected", sStr1= "R", "Rejected", sStr1= "W", "Rejected, Assurance Failed Validity Tests", sStr1= "X", "Rejected, Content After Decryption Could Not Be Analyzed") + vbNewLine
                    Print #iRsltFile, "Transaction sets you sent: " + .X12Elem(2)
                    Print #iRsltFile, "Transaction sets received: " + .X12Elem(3)
                    if (UBound(.X12Elem) > 3):   Print #iRsltFile, "Transaction sets accepted: " + .X12Elem(4)
                    for lX= 5 To UBound(.X12Elem)
                        if len(.X12Elem(lX)) <> 0 Then
                            sStr1= .X12Elem(lX)
                            sStr1= sStr1 + " - " + Switch(sStr1= "1", "FGrp Not Supported", sStr1= "2", "FGrp Ver Not Supported", sStr1= "3", "FGrp Trailer Missing", sStr1= "4", "Grp Ctrl Num in the FGrp Header and Trailer Do Not Agree", sStr1= "5", "Number of Included sTSets Does Not Match Actual Count", sStr1= "6", "Grp Ctrl Num Violates Syntax", sStr1= "10", "Auth Key Name Unknown", sStr1= "11", "Encrypt Key Name Unknown", sStr1= "12", "Requested Service (Auth or Encrypt) Not Avail", sStr1= "13", "Unknown Security Recipient", sStr1= "14", "Unknown Security Originator", sStr1= "15", "Syntax Error in Decrypted Text", sStr1= "16", "Security Not Supported", sStr1= "17", "Bad Message Length (Encrypt Only)", sStr1= "18", "MAC Failed", sStr1= "23", "S3E Sec. End Seg Missing for S3S Sec. Start Seg", sStr1= "24", "S3S Sec. Start Seg Missing for S3E End Seg", sStr1= "25", "S4E Sec. End Seg Missing for S4S Sec. Start Seg", sStr1= sStr1= "26", "S4S Sec. Start Seg Missing for S4E Sec. End Seg")
                            Print #iRsltFile, "Error code(s) for this billing file: " + sStr1 + vbNewLine
                        End If
                    Next
            End Select
        End With
        Next
    Next
    Print #iRsltFile, vbNewLine + vbNewLine
    Print #iRsltFile, "  Note: Each billing file you submit may contain more than one batch of claims "
    Print #iRsltFile, "        (for example, if you bill for more than one doctor.)  Each of these batches is called "
    Print #iRsltFile, "        a 'transaction set' or 'TSet'.  This 997 report gives you the status of all transaction"
    Print #iRsltFile, "        sets in your billing file,                                            As well                                            As for the file                                            As a whole - even if your file only"
    Print #iRsltFile, "        contains one batch."
    Print #iRsltFile, vbNewLine
    Print #iRsltFile, "        Because it can contain more than one transaction set, your billing file is also called a "
    Print #iRsltFile, "        'functional group' or 'FGrp'.  if you receive any error messages that refer to FGrp, "
    Print #iRsltFile, "        this simply means the billing file."
    
        

    Close #iRsltFile
    Exit Function
Error:
    sStr1= "ANSI response file processing failed!  Error:" & Err.Description
    Print #iRsltFile, sStr1
    Close #iRsltFile


Public Function udtANSItoRaw(ByRef sANSIFile                                           ='', )                                            As X12_Raw
    Dim iStartFile                                            As Integer, lX                                           =0, , lY                                           =0, 
    Dim sStr1                                           ='', , sTmpSeg()                                           ='', , udtTmpANSIRaw                                            As X12_Raw
    iStartFile= FreeFile
    Open sANSIFile for Input                                            As #iStartFile
    With udtTmpANSIRaw
        sStr1= Input(LOF(iStartFile), #iStartFile)
        Close #iStartFile
        .sElemSep= Mid$(sStr1, 4, 1)
        .sSubElemSep= Mid$(sStr1, 105, 1)
        .sSegTerm= Mid$(sStr1, 106, 1)
        '====== Anvicare 835s come separated into lines - convenient to read, but not for processing====
        '======  stripping out newlines, version 6.1.1, 4 Sep 2006
        sStr1= Replace(sStr1, vbNewLine, "")
        '================================================================================================
        sTmpSeg= Split(RTrim$(sStr1), .sSegTerm)
        ReDim .Seg(0 To UBound(sTmpSeg) - 1)                                            As X12Seg
        for lX= 0 To UBound(.Seg)
            .Seg(lX).X12Elem= Split(sTmpSeg(lX), .sElemSep)
        Next
        lY= 0
        ReDim .STLoop(0 To UBound(.Seg) \ 3)                                            As X12Loop     ' pre-allocate much more space than we should need
        for lX= 0 To UBound(.Seg)
            Debug.Print .Seg(lX).X12Elem(0)
            if .Seg(lX).X12Elem(0)= "ST" Then
                .STLoop(lY).lBeg= lX
                .STLoop(lY).sANSIType= .Seg(lX).X12Elem(1)
            End If
            if .Seg(lX).X12Elem(0)= "SE" Then
                .STLoop(lY).lEnd= lX
                lY= lY + 1
            End If
        Next
        ReDim Preserve .STLoop(0 To lY - 1)                                            As X12Loop      ' now shrink it to proper size
    End With
    return udtTmpANSIRaw

Public Function sRawtoANSI(ByRef sInANSIRaw                                            As X12_Raw)                                           ='', 
    lX=0
    lY=0
    sTmpSeg =[]
    for lX= 0 To UBound(sInANSIRaw.Seg)
        sTmpSeg(lX)= sInANSIRaw.Seg(lX).X12Elem(0)
        for lY= 1 To UBound(sInANSIRaw.Seg(lX).X12Elem)
            sTmpSeg(lX)= sTmpSeg(lX) & sInANSIRaw.sElemSep & sInANSIRaw.Seg(lX).X12Elem(lY)
    return Join(sTmpSeg, sInANSIRaw.sSegTerm) & sInANSIRaw.sSegTerm

def sRawtoTruncANSI(sInANSIRaw):   #' Minnesota doesn't like empty fields at end of record (* just before ~) - so, truncate to last field used
    sTmpSeg= [] 
    for segment in sInANSIRaw.Seg: #figure out whether this is a list or dictionary...
        tmpSubSeg = segment
        for sub in tmpSubSeg:
        
        sTmpSeg.append(segment.X12Elem[0])
        while sInANSIRaw.Seg(lX).X12Elem(lTmp)= ""
            lTmp= lTmp - 1
        for lY= 1 To lTmp
            sTmpSeg(lX)= sTmpSeg(lX) & sInANSIRaw.sElemSep & sInANSIRaw.Seg(lX).X12Elem(lY)
    return Join(sTmpSeg, sInANSIRaw.sSegTerm) & sInANSIRaw.sSegTerm

def sANSI_Handler(sANSIFile)
    udtTmpRaw= udtANSItoRaw(sANSIFile)
    if udtTmpRaw.STLoop(0).sANSIType = "835":
        return sANSI_835(udtTmpRaw)
    elif udtTmpRaw.STLoop(0).sANSIType = "997":
        return sANSI_997(udtTmpRaw)

def curZeroChk(Str1=''):
    if (len(Str1)= 0): 
        return '0' 
    else:
        return CCur(Str1)

def iZeroChk(Str1='') As Integer
    if (len(Str1)= 0):
        return "0" 
    else:   
        return CInt(Str1)

def lZeroChk(Str1):
    if (len(Str1)= 0):
        return "0" 
    else:
        return CLng(Str1)

class fldDef(object):
    def __init__(self, x, y, val=False, inUse = True):
        """Each field has a location (on the new form), a value (we hope), 
        and a flag to determine whether to print it on the new form. """
        self.Value = val
        self.X = x
        self.Y = y
        self.inUse = inUse 
    def __str__(self):    
        return str(self.Value)

class DetailLine(object):
    def __init__(self, num, TestPrint=False):
        line1 = 40 + 2*num
        line2 = 41 + 2*num

        try:
            detailLeft = int(str(Global.cfgFile.detailLeft))
        except:
            detailLeft = 0
        try:
            detailTo = int(str(Global.cfgFile.detailTo))
        except:
            detailTo = 9
        try:
            detailPOS = int(str(Global.cfgFile.detailPOS))
        except:
            detailPOS = 19
        try:
            detailCode = int(str(Global.cfgFile.detailCode))
        except:
            detailCode = 25
        try:
            detailMods = int(str(Global.cfgFile.detailMods))
        except:
            detailMods = 32
        try:
            detailDiags = int(str(Global.cfgFile.detailDiags))
        except:
            detailDiags = 44
        try:
            detailCharge = int(str(Global.cfgFile.detailCharge))
        except:
            detailCharge = 49
        try:
            detailUnits = int(str(Global.cfgFile.detailUnits))
        except:
            detailUnits = 58
        try:
            detailEPSDT = int(str(Global.cfgFile.detailEPSDT))
        except:
            detailEPSDT = 62
        try:
            detailEMG = int(str(Global.cfgFile.detailEMG))
        except:
            detailEMG = 22
        try:
            detailID = int(str(Global.cfgFile.detailID))
        except:
            detailID = 67

        Global.cfgFile.detailLeft = unicode(detailLeft)
        Global.cfgFile.detailTo = unicode(detailTo)
        Global.cfgFile.detailPOS = unicode(detailPOS)
        Global.cfgFile.detailCode = unicode(detailCode)
        Global.cfgFile.detailMods = unicode(detailMods)
        Global.cfgFile.detailDiags = unicode(detailDiags)
        Global.cfgFile.detailCharge = unicode(detailCharge)
        Global.cfgFile.detailUnits = unicode(detailUnits)
        Global.cfgFile.detailEPSDT = unicode(detailEPSDT)
        Global.cfgFile.detailEMG = unicode(detailEMG)
        Global.cfgFile.detailID = unicode(detailID)
        Global.cfgFile.Save()

        self.From       = fldDef(detailLeft, line2)
        self.To         = fldDef(detailTo, line2)
        self.POS        = fldDef(detailPOS,line2)
        self.TOS        = fldDef(80,line2, inUse=False) # not used on new form
        self.Code       = fldDef(detailCode,line2)
        self.Mods       = fldDef(detailMods,line2)
        self.Diags      = fldDef(detailDiags,line2)
        self.Charge     = fldDef(detailCharge,line2)
        self.Units      = fldDef(detailUnits,line2)
        self.EPSDT      = fldDef(detailEPSDT,line2)
        self.EMG        = fldDef(detailEMG,line2)
        self.COB        = fldDef(80,line2, inUse=False) # not used on new form
        self.LegacyID   = fldDef(detailID,line1)
        self.LegacyQual = fldDef(detailID-2,line1)
        self.NPI        = fldDef(detailID,line2)
        self.Note       = fldDef(detailLeft, line1)
        if TestPrint:
            self.From.Value = "01 01 01"
            self.To.Value = "01 01 01"
            self.POS.Value = "11"
            self.Code.Value = "99999"
            self.Mods.Value = "01 02 03 04"
            self.Diags.Value = "1234"
            self.Charge.Value = "9999 99"
            self.Units.Value = "999"
            self.EPSDT.Value = "X"
            self.EMG.Value = "X"
            self.LegacyID.Value = "123456789"
            self.LegacyQual.Value = "XX"
            self.NPI.Value = "1234567893"
            self.Note.Value = "Note1Note2Note3Note4Note5Note6Note7Note8Note9Note0Note1Note2"
        


class Form1500(object):
    def __init__(self, TestPrint=False, leftBlock=0, midBlock=24, rightBlock=49, labelEdge=49):
        """
        1500 form fields.  New form is (just about) a superset of old form, so we can use one class for old and new.
        """
        "bodyLeftBlock", "bodyMidBlock", "bodyRightBlock", "bodyLabelEdge",

        try:
            leftBlock = int(str(Global.cfgFile.bodyLeftBlock))
        except:
            leftBlock = 0
        try:
            midBlock = int(str(Global.cfgFile.bodyMidBlock))
        except:
            midBlock = 24
        try:
            rightBlock = int(str(Global.cfgFile.bodyRightBlock))
        except:
            rightBlock = 49
        try:
            labelEdge = int(str(Global.cfgFile.bodyLabelEdge))
        except:
            labelEdge = 40
        Global.cfgFile.bodyLeftBlock = unicode(leftBlock)
        Global.cfgFile.bodyMidBlock = unicode(midBlock)
        Global.cfgFile.bodyRightBlock = unicode(rightBlock)
        Global.cfgFile.bodyLabelEdge = unicode(labelEdge)
        Global.cfgFile.Save()
        
      
        chkCol1 = midBlock + 10
        chkCol2 = rightBlock -9
        chkCol3 = rightBlock -8
        chkCol4 = rightBlock -3
        self.Box0Line1            = fldDef(labelEdge,0)
        self.Box0Line2            = fldDef(labelEdge,1)
        self.Box0Line3            = fldDef(labelEdge,2)
        self.Box0Line4            = fldDef(labelEdge,3)
        self.Box0Line5            = fldDef(labelEdge,4)
        self.Box0Line6            = fldDef(labelEdge,5)
        self.Box1McareCheck       = fldDef(leftBlock,7)
        self.Box1McaidCheck       = fldDef(leftBlock+7,7)
        self.Box1TriChampCheck    = fldDef(leftBlock+14,7)
        self.Box1ChampvaCheck     = fldDef(leftBlock+23,7)
        self.Box1GroupCheck       = fldDef(leftBlock+30,7)
        self.Box1FECACheck        = fldDef(leftBlock+38,7)
        self.Box1OtherCheck       = fldDef(chkCol3+3,7)
        self.Box1a                = fldDef(rightBlock,7)
        self.Box2                 = fldDef(leftBlock,9)
        self.Box3Birth            = fldDef(midBlock +6,9)
        self.Box3SexM             = fldDef(chkCol3,9)
        self.Box3SexF             = fldDef(chkCol4,9)
        self.Box4                 = fldDef(rightBlock,9)
        self.Box5Address          = fldDef(leftBlock,11)
        self.Box5City             = fldDef(leftBlock,13)
        self.Box5State            = fldDef(leftBlock+26,13)
        self.Box5Zip              = fldDef(leftBlock,15)
        self.Box5Tel              = fldDef(leftBlock+14,15)
        self.Box6Self             = fldDef(chkCol1-2,11)
        self.Box6Spouse           = fldDef(chkCol2-3,11)
        self.Box6Child            = fldDef(chkCol3,11)
        self.Box6Other            = fldDef(chkCol4,11)
        self.Box7Address          = fldDef(rightBlock,11)
        self.Box7City             = fldDef(rightBlock,13)
        self.Box7State            = fldDef(rightBlock+24,13)
        self.Box7Zip              = fldDef(rightBlock,15)
        self.Box7Tel              = fldDef(rightBlock+15,15)
        self.Box8Single           = fldDef(chkCol1,13)
        self.Box8Married          = fldDef(chkCol2,13)
        self.Box8Other            = fldDef(chkCol4,13)
        self.Box8Employed         = fldDef(chkCol1,15)
        self.Box8FTStudent        = fldDef(chkCol2,15)
        self.Box8PTStudent        = fldDef(chkCol4,15)
        self.Box9Name             = fldDef(leftBlock,17)
        self.Box9a                = fldDef(leftBlock,19)
        self.Box9bBirth           = fldDef(leftBlock,21)
        self.Box9bSexM            = fldDef(leftBlock+17,21)
        self.Box9bSexF            = fldDef(leftBlock+23,21)
        self.Box9c                = fldDef(leftBlock,23)
        self.Box9d                = fldDef(leftBlock,25)
        self.Box10aYes            = fldDef(chkCol1,19)
        self.Box10aNo             = fldDef(chkCol2,19)
        self.Box10bYes            = fldDef(chkCol1,21)
        self.Box10bNo             = fldDef(chkCol2,21)
        self.Box10bState          = fldDef(chkCol3+4,21)
        self.Box10cYes            = fldDef(chkCol1,23)
        self.Box10cNo             = fldDef(chkCol2,23)
        self.Box10d               = fldDef(midBlock+7,25)
        self.Box11Num             = fldDef(rightBlock,17)
        self.Box11aBirth          = fldDef(rightBlock,19)
        self.Box11aSexM           = fldDef(rightBlock+18,19)
        self.Box11aSexF           = fldDef(rightBlock+24,19)
        self.Box11b               = fldDef(rightBlock,21)
        self.Box11c               = fldDef(rightBlock,23)
        self.Box11dYes            = fldDef(rightBlock+2,25)
        self.Box11dNo             = fldDef(rightBlock+7,25)
        self.Box12Sig             = fldDef(leftBlock+8,29)
        self.Box12Date            = fldDef(chkCol1+1,29)
        self.Box13                = fldDef(rightBlock+7,29)
        self.Box14Date            = fldDef(leftBlock+1,31)
        self.Box15Date            = fldDef(chkCol1+3,31)
        self.Box16FromDate        = fldDef(rightBlock+4,31)
        self.Box16ToDate          = fldDef(rightBlock+18,31)
        self.Box17Name            = fldDef(leftBlock,33)
        self.Box17aType           = fldDef(midBlock+5,32)
        self.Box17aCode           = fldDef(chkCol1-2,32)
        self.Box17b               = fldDef(chkCol1-2,33)
        self.Box18FromDate        = fldDef(rightBlock+4,33)
        self.Box18ToDate          = fldDef(rightBlock+18,33)
        self.Box19                = fldDef(leftBlock,35)
        self.Box20Yes             = fldDef(rightBlock+2,35)
        self.Box20No              = fldDef(rightBlock+7,35)
        self.Box20Amount          = fldDef(rightBlock+15,35)
        self.Box21_1              = fldDef(leftBlock+2,37)
        self.Box21_2              = fldDef(leftBlock+2,39)
        self.Box21_3              = fldDef(midBlock+5,37)
        self.Box21_4              = fldDef(midBlock+5,39)
        self.Box22Code            = fldDef(rightBlock,37)
        self.Box22Orig            = fldDef(rightBlock+12,37)
        self.Box23                = fldDef(rightBlock,39)
        self.Box24                = {}
        for x in (1,2,3,4,5,6):
            self.Box24[x]         = DetailLine(x, TestPrint)  
        self.Box25Num             = fldDef(leftBlock,55)
        self.Box25SSN             = fldDef(leftBlock+16,55)
        self.Box25EIN             = fldDef(leftBlock+18,55)
        self.Box26                = fldDef(midBlock,55)
        self.Box27Yes             = fldDef(chkCol1+3,55)
        self.Box27No              = fldDef(chkCol3+1,55)
        self.Box28                = fldDef(rightBlock,55)
        self.Box29                = fldDef(rightBlock+13,55)
        self.Box30                = fldDef(rightBlock+19,55)
        self.Box31Sig             = fldDef(leftBlock,59)
        self.Box31Date            = fldDef(leftBlock+10,60)
        self.Box32Line1           = fldDef(midBlock,57)
        self.Box32Line2           = fldDef(midBlock,58)
        self.Box32Line3           = fldDef(midBlock,59)
        self.Box32a               = fldDef(midBlock,60)
        self.Box32b               = fldDef(chkCol1+1,60)
        self.Box33Tel             = fldDef(rightBlock+15,56)
        self.Box33Line1           = fldDef(rightBlock,57)
        self.Box33Line2           = fldDef(rightBlock,58)
        self.Box33Line3           = fldDef(rightBlock,59)
        self.Box33LegacyPIN       = fldDef(rightBlock+13,60,inUse=False)
        self.Box33LegacyGrp       = fldDef(rightBlock+13,60,inUse=False)
        self.Box33a               = fldDef(rightBlock,60)
        self.Box33b               = fldDef(rightBlock+14,60)
        self.Box33ExtraCodeType   = fldDef(leftBlock,0,inUse=False)
        self.Box33ExtraCode       = fldDef(leftBlock,0,inUse=False)
        
        if TestPrint:
            self.Box0Line1.Value = "XXXXXXXXXXXXXXXXXXXXXXXXX"
            self.Box0Line2.Value = "XXXXXXXXXXXXXXXXXXXXXXXXX"
            self.Box0Line3.Value = "XXXXXXXXXXXXXXXXXXXXXXXXX"
            self.Box0Line4.Value = "XXXXXXXXXXXXXXXXXXXXXXXXX"
            self.Box0Line5.Value = "XXXXXXXXXXXXXXXXXXXXXXXXX"
            self.Box0Line6.Value = "XXXXXXXXXXXXXXXXXXXXXXXXX"
            self.Box1McareCheck.Value = True
            self.Box1McaidCheck.Value = True
            self.Box1TriChampCheck.Value = True
            self.Box1ChampvaCheck.Value = True
            self.Box1GroupCheck.Value = True
            self.Box1FECACheck.Value = True
            self.Box1OtherCheck.Value = True
            self.Box1a.Value = "12345678901234567890"
            self.Box2.Value = "PUBLIC JOHN Q"
            self.Box3Birth.Value = "01012001"
            self.Box3SexM.Value = True
            self.Box3SexF.Value = True
            self.Box4.Value = "PUBLIC JANE X"
            self.Box5Address.Value = "123 MELODY LANE"
            self.Box5City.Value = "ANYTOWN"
            self.Box5State.Value = "CA"
            self.Box5Zip.Value = "90210"
            self.Box5Tel.Value = "310 555 1212"
            self.Box6Self.Value = True
            self.Box6Spouse.Value = True
            self.Box6Child.Value = True
            self.Box6Other.Value = True
            self.Box7Address.Value = "123 MELODY LANE"
            self.Box7City.Value = "ANYTOWN"
            self.Box7State.Value = "CA"
            self.Box7Zip.Value = "90210"
            self.Box7Tel.Value = "310 555 1212"
            self.Box8Single.Value = True
            self.Box8Married.Value = True
            self.Box8Other.Value = True
            self.Box8Employed.Value = True
            self.Box8FTStudent.Value = True
            self.Box8PTStudent.Value = True
            self.Box9Name.Value = "PRIVATE RYAN J"
            self.Box9a.Value = "98765432109876543210"
            self.Box9bBirth.Value = "01 01 2001"
            self.Box9bSexM.Value = True
            self.Box9bSexF.Value = True
            self.Box9c.Value = "EMPLOYER OR SCHOOL"
            self.Box9d.Value = "OTHER INSURANCE PLAN"
            self.Box10aYes.Value = True
            self.Box10aNo.Value = True
            self.Box10bYes.Value = True
            self.Box10bNo.Value = True
            self.Box10bState.Value = "CA"
            self.Box10cYes.Value = True
            self.Box10cNo.Value = True
            self.Box10d.Value = "RESERVED"
            self.Box11Num.Value = "24680246802468024680"
            self.Box11aBirth.Value = "01 01 2001"
            self.Box11aSexM.Value = True
            self.Box11aSexF.Value = True
            self.Box11b.Value = "EMPLOYER OR SCHOOL"
            self.Box11c.Value = "INSURANCE PLAN NAME"
            self.Box11dYes.Value = True
            self.Box11dNo.Value = True
            self.Box12Sig.Value = "SIGNATURE ON FILE"
            self.Box12Date.Value = "01 01 2001"
            self.Box13.Value = "SIGNATURE ON FILE"
            self.Box14Date.Value = "01 01 2001"
            self.Box15Date.Value = "01 01 2001"
            self.Box16FromDate.Value = "01 01 2001"
            self.Box16ToDate.Value = "01 01 2001"
            self.Box17Name.Value = "REFERRAL SOURCE"
            self.Box17aType.Value = "XX"
            self.Box17aCode.Value = "A123456"
            self.Box17b.Value = "1234567893"
            self.Box18FromDate.Value = "01 01 2001"
            self.Box18ToDate.Value = "01 01 2001"
            self.Box19.Value = "RESERVED FOR LOCAL USE"
            self.Box20Yes.Value = True
            self.Box20No.Value = True
            self.Box20Amount.Value = "99999 99"
            self.Box21_1.Value = "123 45"
            self.Box21_2.Value = "678 90"
            self.Box21_3.Value = "234 56"
            self.Box21_4.Value = "789 01"
            self.Box22Code.Value = "1234567890"
            self.Box22Orig.Value = "12345678901234567890"
            self.Box23.Value = "PRIOR AUTH NUMBER"
            self.Box25Num.Value = "951234567"
            self.Box25SSN.Value = True
            self.Box25EIN.Value = True
            self.Box26.Value = "123456789 0"
            self.Box27Yes.Value = True
            self.Box27No.Value = True
            self.Box28.Value = "   99999 99"
            self.Box29.Value = "9999 99"
            self.Box30.Value = "     999 99"
            self.Box31Sig.Value = "XXXXXXXXXXXXX"
            self.Box31Date.Value = "01 012 001"
            self.Box32Line1.Value = "XXXXXXXXXXXXXXXXXXXX"
            self.Box32Line2.Value = "XXXXXXXXXXXXXXXXXXXX"
            self.Box32Line3.Value = "XXXXXXXXXXXXXXXXXXXX"
            self.Box32a.Value = "1234567893"
            self.Box32b.Value = "A12345"
            self.Box33Tel.Value = "(310) 555 1212"
            self.Box33Line1.Value = "XXXXXXXXXXXXXXXXXXXX"
            self.Box33Line2.Value = "XXXXXXXXXXXXXXXXXXXX"
            self.Box33Line3.Value = "XXXXXXXXXXXXXXXXXXXX"
            self.Box33a.Value = "1234567893"
            self.Box33b.Value = "A12345"





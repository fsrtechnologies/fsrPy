from __future__ import with_statement
import wx, sys, os, re, string, copy
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.dialogs
from configobj import ConfigObj
from validate import Validator
from fsrStuff import fixDate
from fsrStuff.NPIFile import NPIFile
import Ft.Lib.Uri as uri
try:
    import wx.lib.inspection
except ImportError: pass
try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO

#---classes

class Global(object):
    cfgFileName = os.getcwd() + os.sep + 'fsr_1500.ini'
    tmpStr = """
    npiXMLFile = string(default="npiMap.XML")
    UCFformLength = integer(min=50, max=80, default=66)
    FIformLength = integer(min=50, max=80, default=64) 
    OutformLength = integer(min=50, max=80, default=64) 
    IncludeLegacy = boolean(default=False)
    TopLeft = int_list(min=2, max=2)
    BottomRight = int_list(min=2, max=2)
    FIHist = string_list(default=None)
    UCFHist = string_list(default=None)
    OutHist = string_list(default=None)
    LastRunUCF = boolean(default=True)
    LastRunPrinter = boolean(default=False)
    detailLeft = integer(min=0, max=80, default=0)
    detailTo = integer(min=0, max=80, default=9) 
    detailPOS = integer(min=0, max=80, default=19)
    detailCode = integer(min=0, max=80, default=25)
    detailMods = integer(min=0, max=80, default=32)
    detailDiags = integer(min=0, max=80, default=44)
    detailCharge = integer(min=0, max=80, default=49)
    detailUnits = integer(min=0, max=80, default=58)
    detailEPSDT = integer(min=0, max=80, default=62)
    detailEMG = integer(min=0, max=80, default=22) 
    detailID = integer(min=0, max=80, default=67)
    bodyLeftBlock = integer(min=0, max=80, default=0)
    bodyMidBlock = integer(min=0, max=80, default=24)
    bodyRightBlock = integer(min=0, max=80, default=49)
    bodyLabelEdge = integer(min=0, max=80, default=40)
    ConfirmSuccess = boolean(default=True)
    """
    cfgSpec = StringIO.StringIO(tmpStr)
    cfgFile = ConfigObj(cfgFileName, 
                configspec=cfgSpec, raise_errors=True, write_empty_values=True, 
                create_empty=True, indent_type='    ', list_values=True)
    vtor = Validator()


class Log(object):
    """Log output is redirected to the status bar of the containing frame."""
    def WriteText(self,text_string):
        self.write(text_string)
    def write(self,text_string):
        wx.GetApp().GetTopWindow().SetStatusText(text_string)


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

        self.From       = fldDef(Global.cfgFile['detailLeft'], line2)
        self.To         = fldDef(Global.cfgFile['detailTo'], line2)
        self.POS        = fldDef(Global.cfgFile['detailPOS']-1,line2)
        self.TOS        = fldDef(80,line2, inUse=False) # not used on new form
        self.Code       = fldDef(Global.cfgFile['detailCode'],line2)
        self.Mods       = fldDef(Global.cfgFile['detailMods'],line2)
        self.Diags      = fldDef(Global.cfgFile['detailDiags'],line2)
        self.Charge     = fldDef(Global.cfgFile['detailCharge']-1,line2)
        self.Units      = fldDef(Global.cfgFile['detailUnits'],line2)
        self.EPSDT      = fldDef(Global.cfgFile['detailEPSDT'],line2)
        self.EMG        = fldDef(Global.cfgFile['detailEMG'],line2)
        self.COB        = fldDef(80,line2, inUse=False) # not used on new form
        self.LegacyID   = fldDef(Global.cfgFile['detailID'],line1)
        self.LegacyQual = fldDef(Global.cfgFile['detailID']-3,line1)
        self.NPI        = fldDef(Global.cfgFile['detailID'],line2)
        self.Note       = fldDef(Global.cfgFile['detailLeft'], line1)
        if TestPrint:
            self.From.Value = "12 31 99"
            self.To.Value = "12 31 99"
            self.POS.Value = "11"
            self.Code.Value = "99999"
            self.Mods.Value = "01 02 03 04"
            self.Diags.Value = "1234"
            self.Charge.Value = "99999 99"
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
        Global.cfgFile['bodyLeftBlock'] = leftBlock
        Global.cfgFile['bodyMidBlock'] = midBlock
        Global.cfgFile['bodyRightBlock'] = rightBlock
        Global.cfgFile['bodyLabelEdge'] = labelEdge
        Global.cfgFile.write()
        
      
        chkCol1 = Global.cfgFile['bodyMidBlock'] + 10
        chkCol2 = Global.cfgFile['bodyRightBlock'] -9
        chkCol3 = Global.cfgFile['bodyRightBlock'] -8
        chkCol4 = Global.cfgFile['bodyRightBlock'] -3
        self.Box0Line1            = fldDef(Global.cfgFile['bodyLabelEdge'],0)
        self.Box0Line2            = fldDef(Global.cfgFile['bodyLabelEdge'],1)
        self.Box0Line3            = fldDef(Global.cfgFile['bodyLabelEdge'],2)
        self.Box0Line4            = fldDef(Global.cfgFile['bodyLabelEdge'],3)
        self.Box0Line5            = fldDef(Global.cfgFile['bodyLabelEdge'],4)
        self.Box0Line6            = fldDef(Global.cfgFile['bodyLabelEdge'],5)
        self.Box1McareCheck       = fldDef(Global.cfgFile['bodyLeftBlock'],7)
        self.Box1McaidCheck       = fldDef(Global.cfgFile['bodyLeftBlock']+7,7)
        self.Box1TriChampCheck    = fldDef(Global.cfgFile['bodyLeftBlock']+14,7)
        self.Box1ChampvaCheck     = fldDef(Global.cfgFile['bodyLeftBlock']+23,7)
        self.Box1GroupCheck       = fldDef(Global.cfgFile['bodyLeftBlock']+30,7)
        self.Box1FECACheck        = fldDef(Global.cfgFile['bodyLeftBlock']+38,7)
        self.Box1OtherCheck       = fldDef(chkCol3+3,7)
        self.Box1a                = fldDef(Global.cfgFile['bodyRightBlock'],7)
        self.Box2                 = fldDef(Global.cfgFile['bodyLeftBlock'],9)
        self.Box3Birth            = fldDef(Global.cfgFile['bodyMidBlock'] +6,9)
        self.Box3SexM             = fldDef(chkCol3,9)
        self.Box3SexF             = fldDef(chkCol4,9)
        self.Box4                 = fldDef(Global.cfgFile['bodyRightBlock'],9)
        self.Box5Address          = fldDef(Global.cfgFile['bodyLeftBlock'],11)
        self.Box5City             = fldDef(Global.cfgFile['bodyLeftBlock'],13)
        self.Box5State            = fldDef(Global.cfgFile['bodyLeftBlock']+26,13)
        self.Box5Zip              = fldDef(Global.cfgFile['bodyLeftBlock'],15)
        self.Box5Tel              = fldDef(Global.cfgFile['bodyLeftBlock']+14,15)
        self.Box6Self             = fldDef(chkCol1-2,11)
        self.Box6Spouse           = fldDef(chkCol2-3,11)
        self.Box6Child            = fldDef(chkCol3,11)
        self.Box6Other            = fldDef(chkCol4,11)
        self.Box7Address          = fldDef(Global.cfgFile['bodyRightBlock'],11)
        self.Box7City             = fldDef(Global.cfgFile['bodyRightBlock'],13)
        self.Box7State            = fldDef(Global.cfgFile['bodyRightBlock']+24,13)
        self.Box7Zip              = fldDef(Global.cfgFile['bodyRightBlock'],15)
        self.Box7Tel              = fldDef(Global.cfgFile['bodyRightBlock']+15,15)
        self.Box8Single           = fldDef(chkCol1,13)
        self.Box8Married          = fldDef(chkCol2,13)
        self.Box8Other            = fldDef(chkCol4,13)
        self.Box8Employed         = fldDef(chkCol1,15)
        self.Box8FTStudent        = fldDef(chkCol2,15)
        self.Box8PTStudent        = fldDef(chkCol4,15)
        self.Box9Name             = fldDef(Global.cfgFile['bodyLeftBlock'],17)
        self.Box9a                = fldDef(Global.cfgFile['bodyLeftBlock'],19)
        self.Box9bBirth           = fldDef(Global.cfgFile['bodyLeftBlock']+1,21)
        self.Box9bSexM            = fldDef(Global.cfgFile['bodyLeftBlock']+17,21)
        self.Box9bSexF            = fldDef(Global.cfgFile['bodyLeftBlock']+23,21)
        self.Box9c                = fldDef(Global.cfgFile['bodyLeftBlock'],23)
        self.Box9d                = fldDef(Global.cfgFile['bodyLeftBlock'],25)
        self.Box10aYes            = fldDef(chkCol1,19)
        self.Box10aNo             = fldDef(chkCol2,19)
        self.Box10bYes            = fldDef(chkCol1,21)
        self.Box10bNo             = fldDef(chkCol2,21)
        self.Box10bState          = fldDef(chkCol3+3,21)
        self.Box10cYes            = fldDef(chkCol1,23)
        self.Box10cNo             = fldDef(chkCol2,23)
        self.Box10d               = fldDef(Global.cfgFile['bodyMidBlock']+7,25)
        self.Box11Num             = fldDef(Global.cfgFile['bodyRightBlock'],17)
        self.Box11aBirth          = fldDef(Global.cfgFile['bodyRightBlock']+3,19)
        self.Box11aSexM           = fldDef(Global.cfgFile['bodyRightBlock']+18,19)
        self.Box11aSexF           = fldDef(Global.cfgFile['bodyRightBlock']+25,19)
        self.Box11b               = fldDef(Global.cfgFile['bodyRightBlock'],21)
        self.Box11c               = fldDef(Global.cfgFile['bodyRightBlock'],23)
        self.Box11dYes            = fldDef(Global.cfgFile['bodyRightBlock']+2,25)
        self.Box11dNo             = fldDef(Global.cfgFile['bodyRightBlock']+7,25)
        self.Box12Sig             = fldDef(Global.cfgFile['bodyLeftBlock']+8,29)
        self.Box12Date            = fldDef(chkCol1+1,29)
        self.Box13                = fldDef(Global.cfgFile['bodyRightBlock']+7,29)
        self.Box14Date            = fldDef(Global.cfgFile['bodyLeftBlock']+1,31)
        self.Box15Date            = fldDef(chkCol1+2,31)
        self.Box16FromDate        = fldDef(Global.cfgFile['bodyRightBlock']+4,31)
        self.Box16ToDate          = fldDef(Global.cfgFile['bodyRightBlock']+18,31)
        self.Box17Name            = fldDef(Global.cfgFile['bodyLeftBlock'],33)
        self.Box17aType           = fldDef(Global.cfgFile['bodyMidBlock']+5,32)
        self.Box17aCode           = fldDef(chkCol1-2,32)
        self.Box17b               = fldDef(chkCol1-2,33)
        self.Box18FromDate        = fldDef(Global.cfgFile['bodyRightBlock']+4,33)
        self.Box18ToDate          = fldDef(Global.cfgFile['bodyRightBlock']+18,33)
        self.Box19                = fldDef(Global.cfgFile['bodyLeftBlock'],35)
        self.Box20Yes             = fldDef(Global.cfgFile['bodyRightBlock']+2,35)
        self.Box20No              = fldDef(Global.cfgFile['bodyRightBlock']+7,35)
        self.Box20Amount          = fldDef(Global.cfgFile['bodyRightBlock']+15,35)
        self.Box21_1              = fldDef(Global.cfgFile['bodyLeftBlock']+2,37)
        self.Box21_2              = fldDef(Global.cfgFile['bodyLeftBlock']+2,39)
        self.Box21_3              = fldDef(Global.cfgFile['bodyMidBlock']+5,37)
        self.Box21_4              = fldDef(Global.cfgFile['bodyMidBlock']+5,39)
        self.Box22Code            = fldDef(Global.cfgFile['bodyRightBlock'],37)
        self.Box22Orig            = fldDef(Global.cfgFile['bodyRightBlock']+11,37)
        self.Box23                = fldDef(Global.cfgFile['bodyRightBlock'],39)
        self.Box24                = {}
        for x in (1,2,3,4,5,6):
            self.Box24[x]         = DetailLine(x, TestPrint)  
        self.Box25Num             = fldDef(Global.cfgFile['bodyLeftBlock'],55)
        self.Box25SSN             = fldDef(Global.cfgFile['bodyLeftBlock']+16,55)
        self.Box25EIN             = fldDef(Global.cfgFile['bodyLeftBlock']+18,55)
        self.Box26                = fldDef(Global.cfgFile['bodyMidBlock'],55)
        self.Box27Yes             = fldDef(chkCol1+3,55)
        self.Box27No              = fldDef(chkCol3+1,55)
        self.Box28                = fldDef(Global.cfgFile['bodyRightBlock'],55)
        self.Box29                = fldDef(Global.cfgFile['bodyRightBlock']+13,55)
        self.Box30                = fldDef(Global.cfgFile['bodyRightBlock']+19,55)
        self.Box31Sig             = fldDef(Global.cfgFile['bodyLeftBlock'],59)
        self.Box31Date            = fldDef(Global.cfgFile['bodyLeftBlock']+5,60)
        self.Box32Line1           = fldDef(Global.cfgFile['bodyMidBlock']-2,57)
        self.Box32Line2           = fldDef(Global.cfgFile['bodyMidBlock']-2,58)
        self.Box32Line3           = fldDef(Global.cfgFile['bodyMidBlock']-2,59)
        self.Box32a               = fldDef(Global.cfgFile['bodyMidBlock']-1,60)
        self.Box32b               = fldDef(chkCol1+1,60)
        self.Box33Tel             = fldDef(Global.cfgFile['bodyRightBlock']+15,56)
        self.Box33Line1           = fldDef(Global.cfgFile['bodyRightBlock'],57)
        self.Box33Line2           = fldDef(Global.cfgFile['bodyRightBlock'],58)
        self.Box33Line3           = fldDef(Global.cfgFile['bodyRightBlock'],59)
        self.Box33LegacyPIN       = fldDef(Global.cfgFile['bodyRightBlock']+13,60,inUse=False)
        self.Box33LegacyGrp       = fldDef(Global.cfgFile['bodyRightBlock']+13,60,inUse=False)
        self.Box33a               = fldDef(Global.cfgFile['bodyRightBlock']+1,60)
        self.Box33b               = fldDef(Global.cfgFile['bodyRightBlock']+14,60)
        self.Box33ExtraCodeType   = fldDef(Global.cfgFile['bodyLeftBlock'],0,inUse=False)
        self.Box33ExtraCode       = fldDef(Global.cfgFile['bodyLeftBlock'],0,inUse=False)
        
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
            self.Box3Birth.Value = "01 01 2001"
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
            self.Box28.Value = "9999999 99"
            self.Box29.Value = "9999 99"
            self.Box30.Value =  "9999999 99"
            self.Box31Sig.Value = "XXXXXXXXXXXXX"
            self.Box31Date.Value = "01 01 2001"
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

#---GUI


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, size=size, style=style)
        self.CreateStatusBar(1)
        self.log=Log()

        Global.printData = wx.PrintData()
        Global.printData.SetPaperId(wx.PAPER_LETTER)
        Global.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        Global.printData.SetOrientation(wx.PORTRAIT)
        Global.pageData = wx.PageSetupDialogData()
        print Global.cfgFile['TopLeft']
        Global.pageData.SetMarginTopLeft(tuple(Global.cfgFile['TopLeft']))
        Global.pageData.SetMarginBottomRight(tuple(Global.cfgFile['BottomRight']))

 
        pnl = wx.Panel(self)
        outerMost = wx.BoxSizer(wx.VERTICAL)
        box1 = wx.StaticBox(pnl, -1, "Source file:")
        boxOuter1 = wx.StaticBoxSizer(box1, wx.VERTICAL)

        #---Create filepickers

        fpOpt = {
            "UCF":{"Title":"Select the file containing UCF claims",   "Mask":"*.*",   "Mode":wx.OPEN},
            "FI" :{"Title":"Select the form-image file ",             "Mask":"FI*.*", "Mode":wx.OPEN},
            "Out":{"Title":"Where should we save the converted file?","Mask":"*.*",   "Mode":wx.SAVE}, }
        self.filePicker ={}
        for option, detail in fpOpt.iteritems():
            self.filePicker[option] = filebrowse.FileBrowseButtonWithHistory(pnl, -1, 
                    labelText=' ', fileMask=detail["Mask"], 
                    fileMode=detail["Mode"], dialogTitle=detail["Title"], 
                    changeCallback=lambda x, option=option: self.fpCallback(x, option))

            if Global.cfgFile.has_key(option+'Hist'):
                try:                            #is it a list, 
                    tmpList = Global.cfgFile[option + "Hist"].split(',')
                except AttributeError:          # or a single item?
                    tmpList = Global.cfgFile[option + "Hist"]

            self.filePicker[option].callCallback = False
            self.filePicker[option].SetHistory(tmpList, 0)
            self.filePicker[option].callCallback = True



        #---Source file selection
        
        self.group1_ctrls = []
        msg = '''In UltraMed, you can send 1500 forms to a file in two ways:
        -   select form UCF and print it to a file,
        -   select form FI and get a separate report printed on paper.
        The files created by the two methods are not identical, and they are created in different places.
        This program lets you work with either type, and keep separate settings for the two.
        '''
        self.radio1 = wx.RadioButton(pnl, -1, "UCF", style = wx.RB_GROUP|wx.ALIGN_LEFT)
        self.radio1.SetToolTip(wx.ToolTip(msg))
        self.radio2 = wx.RadioButton(pnl, -1, "FI", style = wx.ALIGN_LEFT)
        self.radio2.SetToolTip(wx.ToolTip(msg))


        #---Destination file selection

        msg = '''
        How many lines from the top of one form to the top of the next?
        If this is set incorrectly, the second and subsequent forms will not be converted correctly.
        UCF forms are usually 66 lines long, and FI forms are usually 64.
        If your situation is different, change this setting.
        '''
        self.sc1 = wx.SpinCtrl(pnl, id=-1, size=wx.Size(50,20))
        self.sc1.SetRange(50,80)
        self.sc1.SetValue(Global.cfgFile['UCFformLength'])
        self.sc1.SetToolTip(wx.ToolTip(msg))

        self.sc2 = wx.SpinCtrl(pnl, id=-1, size=wx.Size(50,20))
        self.sc2.SetRange(50,80)
        self.sc2.SetValue(Global.cfgFile['FIformLength'])
        self.sc2.SetToolTip(wx.ToolTip(msg))
        self.group1_ctrls.append((self.radio1, self.filePicker["UCF"], self.sc1))
        self.group1_ctrls.append((self.radio2, self.filePicker["FI"], self.sc2))
        self.Bind(wx.EVT_RADIOBUTTON, self.OnGroup1Select, self.radio1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnGroup1Select, self.radio2)

        if Global.cfgFile['LastRunUCF']:
            self.radio1.SetValue(True)
            self.filePicker["FI"].Enable(False)
            self.sc2.Enable(False)
        else:
            self.radio2.SetValue(True)
            self.filePicker["UCF"].Enable(False)
            self.sc1.Enable(False)
        
                       

        self.group2_ctrls = []
        msg = '''
        Do you want to print your converted claim forms to paper,
        or save them to a file so you can send them electronically?
        If you save to a file, be careful not to confuse the old file with the converted file!
        '''
        self.radio3 = wx.RadioButton(pnl, -1, "Printer", style = wx.RB_GROUP|wx.ALIGN_LEFT)
        self.radio3.SetToolTip(wx.ToolTip(msg))
        self.radio4 = wx.RadioButton(pnl, -1, "File", style = wx.ALIGN_LEFT)
        self.radio4.SetToolTip(wx.ToolTip(msg))
        self.Bind(wx.EVT_RADIOBUTTON, self.OnGroup2Select, self.radio3)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnGroup2Select, self.radio4)


        self.sc3 = wx.SpinCtrl(pnl, id=-1, size=wx.Size(50,20))
        self.sc3.SetRange(50,80)
        self.sc3.SetValue(Global.cfgFile['OutformLength'])
        msg = '''
        If you're sending form-image claims to a clearinghouse, how many lines per form are they expecting?
        Usually 64, but you can change it if necessary.
        '''
        self.sc3.SetToolTip(wx.ToolTip(msg))
        if Global.cfgFile['LastRunPrinter']:
            self.radio3.SetValue(True)
            self.filePicker["Out"].Enable(False)
            self.sc3.Enable(False)
        else:
            self.radio4.SetValue(True)
            self.filePicker["Out"].Enable(True)
            self.sc3.Enable(True)

        grid1 = wx.FlexGridSizer(3, 3, 0, 0)
        grid1.AddMany([ (wx.StaticText(pnl, -1, "File type: "), 0, wx.ALIGN_LEFT),
                        (wx.StaticText(pnl, -1, "Location: "), 0, wx.ALIGN_CENTER),
                        (wx.StaticText(pnl, -1, "Form length: "), 0, wx.ALIGN_RIGHT),
                        (self.radio1, 1, wx.ALIGN_LEFT|wx.ALL, 1),
                        (self.filePicker["UCF"], 1, wx.EXPAND, 1),
                        (self.sc1, 1, wx.ALIGN_RIGHT|wx.ALL, 1),
                        (self.radio2, 1, wx.ALIGN_LEFT|wx.ALL, 1),
                        (self.filePicker["FI"], 1, wx.EXPAND, 1),
                        (self.sc2, 1, wx.ALIGN_RIGHT|wx.ALL, 1) ])
        grid1.AddGrowableCol(1)

        boxOuter1.Add(grid1, 1, wx.EXPAND|wx.ALL,5)
        outerMost.Add(boxOuter1, 0, wx.EXPAND|wx.ALL,5)

        box2 = wx.StaticBox(pnl, -1, "Destination:")
        boxOuter2 = wx.StaticBoxSizer(box2, wx.VERTICAL)
        grid2 = wx.FlexGridSizer(2, 3, 0, 0)
        grid2.AddMany([ (self.radio3, 1, wx.ALIGN_LEFT|wx.ALL, 1),
                        (wx.StaticText(pnl, -1, " "), 0, wx.EXPAND),
                        (wx.StaticText(pnl, -1, "Form length: "), 0, wx.ALIGN_RIGHT),
                        (self.radio4, 1, wx.ALIGN_LEFT|wx.ALL, 1),
                        (self.filePicker["Out"], 1, wx.EXPAND, 1),
                        (self.sc3, 1, wx.ALIGN_RIGHT|wx.ALL, 1) ])
        grid2.AddGrowableCol(1)

        boxOuter2.Add(grid2, 1, wx.EXPAND|wx.ALL,5)
        outerMost.Add(boxOuter2, 0, wx.EXPAND|wx.ALL,5)

        #---Options
        Opts = [
            {"Name": "IncludeLegacy", "Label":"Keep legacy IDs?", "Tip":"Do you want to print the \"legacy\"  (pre-NPI) ID codes in fields 17a, 32b, 33b, and the top half of 24j?\nNote: Medicare does NOT want legacy codes after March 23 2008; other carriers' rules may vary."}, 
            {"Name": "ConfirmSuccess", "Label":"Show confirmation on success?", "Tip":"Do you want a message to confirm that we finished successfully?"}, 
        ]
        self.Options = {}
        for opt in Opts:
            nom, lbl, tip = opt["Name"], opt["Label"], opt["Tip"]
            self.Options[nom] = wx.CheckBox(pnl, -1, lbl, style=wx.ALIGN_LEFT, name=nom)
            self.Options[nom].SetToolTip(wx.ToolTip(tip))
            self.Options[nom].SetValue(Global.cfgFile[nom])
            self.Bind(wx.EVT_CHECKBOX, self.OnChange, self.Options[nom])
        
        box2o = wx.StaticBox(pnl, -1, "Options:")
        boxOuter2o = wx.StaticBoxSizer(box2o, wx.VERTICAL)
        grid2o = wx.FlexGridSizer(2, 1, 5, 0)
        grid2o.AddMany([self.Options["IncludeLegacy"], self.Options["ConfirmSuccess"]])
        grid2o.AddGrowableCol(1)

        boxOuter2o.Add(grid2o, 1, wx.EXPAND|wx.ALL,5)
        outerMost.Add(boxOuter2o, 0, wx.EXPAND|wx.ALL,5)

        #---Buttons
        boxOuter3 = wx.BoxSizer(wx.VERTICAL)
        #boxInner3 = wx.BoxSizer(wx.HORIZONTAL)
        boxInner3 = wx.FlexGridSizer(2, 2, 5, 0)
        Buttons = [
            {"Name": "OK",   "Tip": "Click here to load (or re-load) the configuration \nyou selected at left."},
            {"Name": "Cancel",   "Tip": "Click here to save your current settings into the \nconfiguration you selected (or typed) at left.\n -  If the configuration didn't exist yet,\n    it will be created with your current settings.\n -  If it already existed, it will be updated."},
            {"Name": "Page Setup",     "Tip": "Click here to proceed using the current settings."},
            {"Name": "Test Print", "Tip": "Click here to exit without doing anything."},
            ]
        for btn in Buttons:
            b = wx.Button(pnl, -1, label=btn["Name"], name=btn["Name"])
            b.SetToolTip(wx.ToolTip(btn["Tip"]))
            boxInner3.Add(b, 0, wx.ALL, 5)                
            self.Bind(wx.EVT_BUTTON, self.OnClick, b)

        boxOuter3.Add(boxInner3, 0, wx.ALIGN_CENTER)


        outerMost.Add(boxOuter3, 0, wx.ALIGN_CENTER)

        #---Cleanup
        pnl.SetSizer(outerMost)

    def fpCallback(self, evt, option, val=None):
        if val:
            value = val
        else:
            value = evt.GetString()
        value = evt.GetString()
        if not value:
            return
        history = self.filePicker[option].GetHistory()
        if value in history:  # if it already existed, remove it
            history.pop(history.index(value))
        history.insert(0, value)  # either way, insert it at the head of the list
        while len(history) > 10: # pop items off the end until history is x items long... 
            history.pop()
        self.filePicker[option].SetHistory(history)
        self.filePicker[option].GetHistoryControl().SetStringSelection(value)

        Global.cfgFile[option+'Hist'] = history
        Global.cfgFile.write()


    def OnChange(self, evt):
        option = evt.GetEventObject().Name
        Global.cfgFile[option] = evt.GetEventObject().GetValue()
        Global.cfgFile.write()
   
    def OnGroup1Select( self, event ):
        radio_selected = event.GetEventObject()

        for radio, ctrl, spin in self.group1_ctrls:
            if radio is radio_selected:
                ctrl.Enable(True)
                spin.Enable(True)
            else:
                ctrl.Enable(False)
                spin.Enable(False)
                
    def OnGroup2Select( self, event ):
        radio_selected = event.GetEventObject()
        if self.radio4 is radio_selected:
            self.filePicker["Out"].Enable(True)
            self.sc3.Enable(True)
        else:
            self.filePicker["Out"].Enable(False)
            self.sc3.Enable(False)
                

    def OnClick(self, event):
        btn = event.GetEventObject().Name
        if (btn == "OK"):
            if self.radio1.GetValue():
                pathStr = r'file:' + str(self.filePicker["UCF"].GetValue())
                self.inLength = self.sc1.GetValue()
                Global.cfgFile['UCFformLength'] = self.sc1.GetValue()
                Global.cfgFile['LastRunUCF'] = True
                Global.cfgFile.write()
            else:
                pathStr = r'file:' + str(self.filePicker["FI"].GetValue())
                self.inLength = self.sc2.GetValue()
                Global.cfgFile['FIformLength'] = self.sc2.GetValue()
                Global.cfgFile['LastRunUCF'] = False
                Global.cfgFile.write()
            if self.radio4.GetValue():
                self.outpathStr = r'file:' + str(self.filePicker["Out"].GetValue())
                self.outLength = self.sc3.GetValue()
                Global.cfgFile['OutformLength'] = self.sc3.GetValue()
                Global.cfgFile['LastRunPrinter'] = False
                Global.cfgFile.write()
            else:
                Global.cfgFile['LastRunPrinter'] = True
                Global.cfgFile.write()
                self.outLength = 66
            if not (os.path.exists(uri.UriToOsPath(pathStr))):
                self.log.write("Select a valid source file!")
            else:
                if ((Global.cfgFile['npiXMLFile']=="") or not (os.path.isfile(uri.UriToOsPath(Global.cfgFile['npiXMLFile'])))):
                    tmpStr = '''
                    I can't continue without an NPI mapping file. 
                    In the next dialog, show me where to find the file 
                      you created when you ran the NPI Update program.
                    (Hint: it's probably called "npiMap.XML")
                    '''
                    dlg = wx.MessageDialog(None, tmpStr,
                            "Can't open the NPI lookup file!", wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    dlg = wx.FileDialog(
                        self, message='''Looking for the NPI mapping file...''',
                        defaultDir=os.getcwd(), 
                        defaultFile="npiMap.XML",
                        wildcard="*.xml",
                        style=wx.OPEN | wx.CHANGE_DIR
                        )
                    if dlg.ShowModal() == wx.ID_OK:
                        path = dlg.GetPaths()[0]
                        self.log.WriteText('%s' % path)
                        Global.cfgFile['npiXMLFile'] = uri.OsPathToUri(path)
                        Global.cfgFile.write()
                    dlg.Destroy()
                    return
                else:
                    self.GetOnWithIt(pathStr, TestPrint=False)
            self.Close(True)
            sys.exit()
        if (btn == "Cancel"):
            self.Close(True)
            sys.exit()

        if (btn == "Page Setup"):
            psdd = wx.PageSetupDialogData(Global.printData)
            psdd.CalculatePaperSizeFromId()
            psdd.SetMarginTopLeft(Global.cfgFile['TopLeft'])
            psdd.SetMarginBottomRight(Global.cfgFile['BottomRight'])
            dlg = wx.PageSetupDialog(self, psdd)
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetPageSetupData()
                self.printData = wx.PrintData(data.GetPrintData())
                Global.cfgFile['TopLeft'] = data.GetMarginTopLeft()
                Global.cfgFile['BottomRight'] = data.GetMarginBottomRight()
                Global.cfgFile.write()
                Global.printData = self.printData
                Global.pageData.SetMarginTopLeft(self.TopLeft)
                Global.pageData.SetMarginBottomRight(self.BottomRight)
            dlg.Destroy()

        if (btn == "Test Print"):
            self.formLength = 66
            self.outLength = self.sc3.GetValue()
            if self.radio4.GetValue():
                self.outpathStr = r'file:' + str(self.filePicker["Out"].GetValue())
                self.fpCallback('Out', -1, val=self.filePicker["Out"].GetValue())
                self.outLength = self.sc3.GetValue()
                Global.cfgFile['OutformLength'] = self.sc3.GetValue()
                Global.cfgFile['LastRunPrinter'] = False
                Global.cfgFile.write()
            else:
                Global.cfgFile['LastRunPrinter'] = True
                Global.cfgFile.write()
                self.outLength = 66
            self.GetOnWithIt("", TestPrint=True)

    def ParseOld1500(self, pathStr): 
        def lblLine1():
            Global.Claims[Global.claimCount].Box0Line1.Value = inLine[37:].strip()
        def lblLine2():
            Global.Claims[Global.claimCount].Box0Line2.Value = inLine[37:].strip()
        def lblLine3():
            Global.Claims[Global.claimCount].Box0Line3.Value = inLine[37:].strip()
        def lblLine4():
            Global.Claims[Global.claimCount].Box0Line4.Value = inLine[37:].strip()
        def lblLine5():
            Global.Claims[Global.claimCount].Box0Line5.Value = inLine[37:].strip()
        def lblLine6():
            Global.Claims[Global.claimCount].Box0Line6.Value = inLine[37:].strip()
        def fld1_1a():
            if (inLine[0:7].strip()=='X'): Global.Claims[Global.claimCount].Box1McareCheck.Value = True
            if (inLine[7:14].strip()=='X'): Global.Claims[Global.claimCount].Box1McaidCheck.Value = True
            if (inLine[14:23].strip()=='X'): Global.Claims[Global.claimCount].Box1TriChampCheck.Value = True
            if (inLine[23:30].strip()=='X'): Global.Claims[Global.claimCount].Box1ChampvaCheck.Value = True
            if (inLine[30:38].strip()=='X'): Global.Claims[Global.claimCount].Box1GroupCheck.Value = True
            if (inLine[38:44].strip()=='X'): Global.Claims[Global.claimCount].Box1FECACheck.Value = True
            if (inLine[44:48].strip()=='X'): Global.Claims[Global.claimCount].Box1OtherCheck.Value = True
            Global.Claims[Global.claimCount].Box1a.Value = inLine[49:].strip()
        def fld2_4():    
            Global.Claims[Global.claimCount].Box2.Value =  inLine[:28].strip()
            Global.Claims[Global.claimCount].Box3Birth.Value = fixDate(inLine[30:40].strip())
            if (inLine[41:43].strip()=='X'): Global.Claims[Global.claimCount].Box3SexM.Value = True
            if (inLine[45:49].strip()=='X'): Global.Claims[Global.claimCount].Box3SexF.Value = True
            Global.Claims[Global.claimCount].Box4.Value = inLine[49:].strip()
        def fld5_7():    
            Global.Claims[Global.claimCount].Box5Address.Value =  inLine[:28].strip()
            if (inLine[29:35].strip()=='X'): Global.Claims[Global.claimCount].Box6Self.Value = True
            if (inLine[35:40].strip()=='X'): Global.Claims[Global.claimCount].Box6Spouse.Value = True
            if (inLine[40:44].strip()=='X'): Global.Claims[Global.claimCount].Box6Child.Value = True
            if (inLine[44:49].strip()=='X'): Global.Claims[Global.claimCount].Box6Other.Value = True
            Global.Claims[Global.claimCount].Box7Address.Value = inLine[49:].strip()
        def city_city():    
            Global.Claims[Global.claimCount].Box5City.Value =  inLine[:25].strip()
            Global.Claims[Global.claimCount].Box5State.Value =  inLine[25:30].strip()
            if (inLine[33:37].strip()=='X'): Global.Claims[Global.claimCount].Box8Single.Value = True
            if (inLine[37:42].strip()=='X'): Global.Claims[Global.claimCount].Box8Married.Value = True
            if (inLine[42:49].strip()=='X'): Global.Claims[Global.claimCount].Box8Other.Value = True
            Global.Claims[Global.claimCount].Box7City.Value =  inLine[49:72].strip()
            Global.Claims[Global.claimCount].Box7State.Value =  inLine[73:].strip()
        def zip_zip():    
            Global.Claims[Global.claimCount].Box5Zip.Value =  inLine[:14].strip()
            Global.Claims[Global.claimCount].Box5Tel.Value =  inLine[14:30].strip()
            if (inLine[33:37].strip()=='X'): Global.Claims[Global.claimCount].Box8Employed.Value = True
            if (inLine[37:42].strip()=='X'): Global.Claims[Global.claimCount].Box8FTStudent.Value = True
            if (inLine[42:49].strip()=='X'): Global.Claims[Global.claimCount].Box8PTStudent.Value = True
            Global.Claims[Global.claimCount].Box7Zip.Value =  inLine[49:61].strip()
            Global.Claims[Global.claimCount].Box7Tel.Value =  inLine[63:].strip()
        def fld9_11():    
            Global.Claims[Global.claimCount].Box9Name.Value =  inLine[:30].strip()
            Global.Claims[Global.claimCount].Box11Num.Value = inLine[49:].strip()
        def fld9a_11a():    
            Global.Claims[Global.claimCount].Box9a.Value =  inLine[:30].strip()
            if (inLine[33:37].strip()=='X'): Global.Claims[Global.claimCount].Box10aYes.Value = True
            if (inLine[37:42].strip()=='X'): Global.Claims[Global.claimCount].Box10aNo.Value = True
            Global.Claims[Global.claimCount].Box11aBirth.Value = inLine[49:65].strip()
            if (inLine[65:71].strip()=='X'): Global.Claims[Global.claimCount].Box11aSexM.Value = True
            if (inLine[71:77].strip()=='X'): Global.Claims[Global.claimCount].Box11aSexF.Value = True
        def fld9b_11b():    
            Global.Claims[Global.claimCount].Box9bBirth.Value = fixDate(inLine[:15].strip())
            if (inLine[16:20].strip()=='X'): Global.Claims[Global.claimCount].Box11aSexM.Value = True
            if (inLine[21:27].strip()=='X'): Global.Claims[Global.claimCount].Box11aSexF.Value = True
            if (inLine[33:37].strip()=='X'): Global.Claims[Global.claimCount].Box10bYes.Value = True
            if (inLine[37:42].strip()=='X'): Global.Claims[Global.claimCount].Box10bNo.Value = True
            Global.Claims[Global.claimCount].Box10bState.Value = inLine[44:48].strip()
        def fld9c_11c():    
            Global.Claims[Global.claimCount].Box9c.Value =  inLine[:30].strip()
            if (inLine[33:37].strip()=='X'): Global.Claims[Global.claimCount].Box10cYes.Value = True
            if (inLine[37:42].strip()=='X'): Global.Claims[Global.claimCount].Box10cNo.Value = True
            Global.Claims[Global.claimCount].Box11c.Value = inLine[49:].strip()
        def fld9d_11d():    
            Global.Claims[Global.claimCount].Box9d.Value = inLine[:30].strip()
            Global.Claims[Global.claimCount].Box10d.Value = inLine[30:49].strip()
            if (inLine[50:55].strip()=='X'): Global.Claims[Global.claimCount].Box11dYes.Value = True
            if (inLine[55:60].strip()=='X'): Global.Claims[Global.claimCount].Box11dNo.Value = True
        def fld12_13():    
            Global.Claims[Global.claimCount].Box12Sig.Value = inLine[:30].strip()
            Global.Claims[Global.claimCount].Box12Date.Value = fixDate(inLine[35:49].strip())
            Global.Claims[Global.claimCount].Box13.Value = inLine[49:].strip()
        def fld14_16():    
            Global.Claims[Global.claimCount].Box14Date.Value = fixDate(inLine[:15].strip())
            Global.Claims[Global.claimCount].Box15Date.Value = fixDate(inLine[35:49].strip())
            Global.Claims[Global.claimCount].Box16FromDate.Value = fixDate(inLine[50:65].strip())
            Global.Claims[Global.claimCount].Box16ToDate.Value = fixDate(inLine[65:].strip())
        def fld17_18():    
            Global.Claims[Global.claimCount].Box17Name.Value = inLine[:27].strip()
            legcode = inLine[27:49].strip()
            if len(legcode) >0: 
                Code = Global.npiMap.lookup(legcode, name=Global.Claims[Global.claimCount].Box17Name.Value, field="Box 17 ")
                if Global.cfgFile['IncludeLegacy']:
                    Global.Claims[Global.claimCount].Box17aType.Value = Code["legacyType"]
                    Global.Claims[Global.claimCount].Box17aCode.Value = Code["legacyCode"]
                Global.Claims[Global.claimCount].Box17b.Value = Code["NPI"]
            else:
                Global.Claims[Global.claimCount].Box17aType.Value = \
                Global.Claims[Global.claimCount].Box17aCode.Value = \
                Global.Claims[Global.claimCount].Box17b.Value = ""
            Global.Claims[Global.claimCount].Box18FromDate.Value = fixDate(inLine[50:65].strip())
            Global.Claims[Global.claimCount].Box18ToDate.Value = fixDate(inLine[65:].strip())
        def fld19_20():    
            Global.Claims[Global.claimCount].Box19.Value = inLine[:49].strip()
            if (inLine[50:55].strip()=='X'): Global.Claims[Global.claimCount].Box20Yes.Value = True
            if (inLine[55:60].strip()=='X'): Global.Claims[Global.claimCount].Box20No.Value = True
            Global.Claims[Global.claimCount].Box20Amount.Value = inLine[60:].strip()
        def fld21_22():    
            Global.Claims[Global.claimCount].Box21_1.Value = inLine[:10].strip()
            Global.Claims[Global.claimCount].Box21_3.Value = inLine[28:37].strip()
            Global.Claims[Global.claimCount].Box22Code.Value = inLine[49:60].strip()
            Global.Claims[Global.claimCount].Box22Orig.Value = inLine[60:].strip()
        def fld21_23():    
            Global.Claims[Global.claimCount].Box21_2.Value = inLine[:10].strip()
            Global.Claims[Global.claimCount].Box21_4.Value = inLine[28:37].strip()
            Global.Claims[Global.claimCount].Box23.Value = inLine[49:].strip()
            Global.lineNum = 0
        def fld24():
            fromTo2Digit = re.compile('\d\d\s\d\d\s\d\d\s\d\d\s\d\d\s\d\d')  # looking for a from-to date to identify top half of Box24 unit
            fromTo4Digit = re.compile('\d\d\d\d\d\d\d\d\s\d\d\d\d\d\d\d\d')  # looking for a from-to date to identify top half of Box24 unit
            if (len(inLine)>1 ): # adjust for (stupid extra blank lines) or (blank lines on last, total page)
                if fromTo2Digit.search(inLine) or fromTo4Digit.search(inLine) :   # this is the service line
                    Global.lineNum +=1
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].From.Value = fixDate(inLine[:9].strip(), forceYear=2)
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].To.Value = fixDate(inLine[9:18].strip(), forceYear=2)
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].POS.Value = inLine[18:20].strip()
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].TOS.Value = inLine[20:24].strip()
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].Code.Value = inLine[24:31].strip()
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].Mods.Value = inLine[31:41].strip()
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].Diags.Value = re.sub("\s+", "",inLine[41:50].strip())
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].Charge.Value = string.rjust(inLine[50:58].strip(), 9)
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].Units.Value = string.rjust(inLine[58:61].strip(), 3)
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].EPSDT.Value = inLine[61:64].strip()
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].EMG.Value = inLine[64:67].strip()
                    Global.Claims[Global.claimCount].Box24[Global.lineNum].COB.Value = inLine[67:70].strip()
                    if len(inLine[70:].strip()) > 1:  #Box 24K may not always be filled in
                        Code    = Global.npiMap.lookup(inLine[70:].strip(), name="rendering...", field="Box 24K ") 
                        if Global.cfgFile['IncludeLegacy']:
                            Global.Claims[Global.claimCount].Box24[Global.lineNum].LegacyID.Value = Code["legacyCode"]
                            Global.Claims[Global.claimCount].Box24[Global.lineNum].LegacyQual.Value = Code["legacyType"]
                        Global.Claims[Global.claimCount].Box24[Global.lineNum].NPI.Value = Code["NPI"]
                else:                               # this ought to be a note to go with the service line
                    if (len(inLine[:10].strip()) > 1):  # if this is the last, "total" page, skip it
                        Global.Claims[Global.claimCount].Box24[Global.lineNum].Note.Value = inLine[:66].strip()
        def fld25_30():    
            Global.Claims[Global.claimCount].Box25Num.Value =  inLine[:15].strip()
            if (inLine[16:18].strip()=='X'): Global.Claims[Global.claimCount].Box25SSN.Value = True
            if (inLine[18:20].strip()=='X'): Global.Claims[Global.claimCount].Box25EIN.Value = True
            Global.Claims[Global.claimCount].Box26.Value = inLine[22:36].strip()
            if (inLine[36:39].strip()=='X'): Global.Claims[Global.claimCount].Box27Yes.Value = True
            if (inLine[39:42].strip()=='X'): Global.Claims[Global.claimCount].Box27No.Value = True
            Global.Claims[Global.claimCount].Box28.Value = string.rjust(inLine[49:60].strip(), 11)
            Global.Claims[Global.claimCount].Box29.Value = string.rjust(inLine[60:70].strip(), 9)
            Global.Claims[Global.claimCount].Box30.Value = string.rjust(inLine[70:].strip(), 11)
        def bottom_1():    
            Global.Claims[Global.claimCount].Box33Tel.Value         = inLine[62:].strip()
        def bottom_2():    
            Global.Claims[Global.claimCount].Box32Line1.Value       = inLine[22:49].strip()
            Global.Claims[Global.claimCount].Box33Line1.Value       = inLine[49:].strip()
        def bottom_3():    
            Global.Claims[Global.claimCount].Box32Line2.Value       = inLine[22:49].strip()
            Global.Claims[Global.claimCount].Box33Line2.Value       = inLine[49:].strip()
        def bottom_4():    
            Global.Claims[Global.claimCount].Box31Sig.Value         = inLine[:22].strip()
            Global.Claims[Global.claimCount].Box32Line3.Value       = inLine[22:49].strip()
            Global.Claims[Global.claimCount].Box33Line3.Value       = inLine[49:].strip()
        def bottom_5():    
            Global.Claims[Global.claimCount].Box31Date.Value        = fixDate(inLine[:22].strip())
            #Initialize to empty first...
            Global.Claims[Global.claimCount].Box32b.Value = ""
            Global.Claims[Global.claimCount].Box32a.Value = ""
            Global.Claims[Global.claimCount].Box33b.Value = ""
            Global.Claims[Global.claimCount].Box33a.Value = ""
            
            legcode = inLine[22:49].strip()
            if len(legcode) >0: 
                Code = Global.npiMap.lookup(legcode, name=Global.Claims[Global.claimCount].Box33Line1.Value, field="Box 32")
                if Global.cfgFile['IncludeLegacy']:
                    Global.Claims[Global.claimCount].Box32b.Value   = Code["legacyCode"]
                Global.Claims[Global.claimCount].Box32a.Value       = Code["NPI"]

            #Codes in Box 33 can be filled by either group or individual - not both, we are told...
            legcode = inLine[49:65].strip()
            if len(legcode) >0: 
                Code = Global.npiMap.lookup(legcode, name=Global.Claims[Global.claimCount].Box33Line1.Value, field="Old Box 33a")
                if Global.cfgFile['IncludeLegacy']:
                    Global.Claims[Global.claimCount].Box33b.Value   = Code["legacyCode"]  
                Global.Claims[Global.claimCount].Box33a.Value       = Code["NPI"]  
            legcode = inLine[65:].strip()
            if len(legcode) >0: 
                Code = Global.npiMap.lookup(legcode, name=Global.Claims[Global.claimCount].Box33Line1.Value, field="Old Box 33b")
                #Global.Claims[Global.claimCount].Box32b.Value           = Code["legacyCode"]
                #Global.Claims[Global.claimCount].Box32a.Value           = Code["NPI"]
                if Global.cfgFile['IncludeLegacy']:
                    Global.Claims[Global.claimCount].Box33b.Value   = Code["legacyCode"]
                Global.Claims[Global.claimCount].Box33a.Value       = Code["NPI"]

            Global.Claims[Global.claimCount].Box33LegacyPIN.Value   = inLine[49:65].strip()
            Global.Claims[Global.claimCount].Box33LegacyGrp.Value   = inLine[65:].strip()
        def bottom_6():    
            Global.Claims[Global.claimCount].Box33ExtraCodeType.Value   = inLine[:35].strip()
            Global.Claims[Global.claimCount].Box33ExtraCode.Value       = inLine[35:].strip()
        def blankLine():    
            pass
        lineParse = {
            0:  lblLine1,
            1:  lblLine2,
            2:  lblLine3,
            3:  lblLine4,
            4:  lblLine5,
            5:  lblLine6,
            9:  fld1_1a,
            11: fld2_4,
            13: fld5_7,
            15: city_city,
            17: zip_zip,
            19: fld9_11,
            21: fld9a_11a,
            23: fld9b_11b,
            25: fld9c_11c,
            27: fld9d_11d,
            31: fld12_13,
            33: fld14_16,
            35: fld17_18,
            37: fld19_20,
            39: fld21_22,
            41: fld21_23,
            44: fld24,
            45: fld24,
            46: fld24,
            47: fld24,
            48: fld24,
            49: fld24,
            50: fld24,
            51: fld24,
            52: fld24,
            53: fld24,
            54: fld24,
            55: fld24,
            57: fld25_30,
            58: bottom_1,
            59: bottom_2,
            60: bottom_3,
            61: bottom_4,
            62: bottom_5,
            63: bottom_6}
        Global.lineCount = 0
        Global.claimCount = -1
        Global.Claims = {}
        Global.TotalBox = ''
        thisFile = uri.UriToOsPath(pathStr)
        table = string.maketrans("(),.:;-/","        ")
        with open(thisFile,'r+b') as inFile:
            for tmpLine in inFile.readlines():
                inLine = tmpLine.translate(table)
                claimLine = Global.lineCount % self.inLength
                if (claimLine == 0): 
                    Global.claimCount +=1
                    Global.Claims[Global.claimCount] = Form1500()
                try:
                    lineParse.get(claimLine, blankLine)()
                except Exception, inst:
                    tmpStr = "Error while trying to process line %s of claim %s \n" % (Global.lineNum+1, Global.claimCount+1)
                    tmpStr += "Original data:\n[%s]" % inLine[:-2]
                    raise Exception(tmpStr)
                Global.lineCount +=1

    def GetOnWithIt(self, pathStr, target=None, TestPrint=False):
        if TestPrint:
            Global.lineCount = 66
            Global.Claims = {}
            Global.Claims[0] = Form1500(TestPrint=True)
        else:
            Global.npiMap = NPIFile(uri.UriToOsPath(str(Global.cfgFile['npiXMLFile'])))
            Global.npiMap.Load()
            try:
                self.ParseOld1500(pathStr)
            except Exception, inst:
                tmpStr = "The following error occurred while processing the source file: \n\n %s \n\n" % inst
                tmpStr += "This usually happens if the form length for the source file is set incorrectly. \nCheck it and try again."
                dlg = wx.MessageDialog(None, tmpStr,
                            "Error during claim processing", style= wx.OK | wx.ICON_INFORMATION)
                response = dlg.ShowModal()
                dlg.Destroy()
                return
            
            if len(Global.npiMap.noMatch) > 0:
                tmpStr = ""
                for code, name in Global.npiMap.noMatch.iteritems():
                    tmpStr += ("Missing NPI for %s, legacy code: %s \n" % (name, code))
                dlg = wx.MessageDialog(None, tmpStr + "Proceed?",
                            "Some NPIs are missing.  Continue anyway?", style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                response = dlg.ShowModal()
                dlg.Destroy()
                if (response == wx.ID_NO):
                    self.Close(True)
                    sys.exit()
                if not Global.cfgFile['IncludeLegacy']:
                    tmpStr += """
                    These entities have no associated NPI, and legacy codes are disabled - 
                      so there will be no ID code at all.  Is that REALLY what you want?
                    """
                    dlg = wx.MessageDialog(None, tmpStr,
                                "Are you SURE?", style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                    response = dlg.ShowModal()
                    dlg.Destroy()
                    if (response == wx.ID_NO):
                        self.Close(True)
                        sys.exit()
                    
        details = [deet for deet in dir(Global.Claims[0].Box24[1]) if (deet.find("__"))]
        boxes = [box for box in dir(Global.Claims[0]) if not (box.find("Box"))]
        boxes.remove("Box24")
        
        lineLength = 85
        line = list(" "*lineLength)
        form = []
        for i in range(self.outLength):
            form.append(copy.copy(line))

        outForm = []

        for num, claim in Global.Claims.iteritems():
            newForm = copy.deepcopy(form)
            for carton in boxes:
                box = getattr(claim, carton)
                if box.inUse:
                    if (box.Value == True):
                        newForm[box.Y][box.X] = "X"
                    elif (box.Value == False):
                        continue
                    else:
                        for i in range(len(box.Value)):
                            newForm[box.Y][box.X + i] = box.Value[i]
            for x in (1,2,3,4,5,6):
                for field in details:
                    box = getattr(claim.Box24[x],field)
                    if box.inUse:
                        if (box.Value == True):
                            newForm[box.Y][box.X] = "X"
                        elif (box.Value == False):
                            continue
                        else:
                            for i in range(len(box.Value)):
                                newForm[box.Y][box.X + i] = box.Value[i]
            for num, line in enumerate(newForm):
                newForm[num] = "".join(line)
            outForm.append(newForm)
        if self.radio3.GetValue(): # Printing
            data = wx.PrintDialogData(Global.printData)
            data.EnablePrintToFile(True)
            data.EnablePageNumbers(True)
            data.SetMinPage(1)
            data.SetMaxPage(len(outForm))
            data.SetAllPages(True)
            dlg = wx.PrintDialog(self, data)
            if dlg.ShowModal() == wx.ID_OK:
                pdd = dlg.GetPrintDialogData()
                data = pdd.GetPrintData()
                dlg.Destroy()
                dc = wx.PrinterDC(data)
                scaleMM = dc.GetPPI()[0]/25.4
                dc.SetDeviceOriginPoint(wx.Point(Global.pageData.GetMarginTopLeft()[0]*scaleMM,Global.pageData.GetMarginTopLeft()[1]*scaleMM))
                l, w = dc.GetSize()
                dc.SetUserScale((l/lineLength),(w/self.outLength))
                font = wx.Font(1, wx.MODERN, wx.NORMAL, wx.NORMAL)
                dc.SetFont(font)
                dc.SetTextForeground(wx.BLACK)
                dc.StartDoc('FSR1500')
                for num, form in enumerate(outForm):
                    if not (pdd.GetAllPages()):
                        if (num < (pdd.GetFromPage()-1)):
                            continue
                        if (num > (pdd.GetToPage()-1)):
                            continue
                    dc.StartPage()
                    for num, line in enumerate(form): 
                        dc.DrawText(line, 0, num)
                    dc.EndPage()
                dc.EndDoc()
            else:
                dlg.Destroy()
        else: #Saving to file
            thisFile = uri.UriToOsPath(self.outpathStr)
            with open(thisFile,'w+b') as outFile:
                for num, form in enumerate(outForm):
                    for num1, line in enumerate(form): 
                        if (num1 == 3):  #Moving body of form (i.e., everything below the label) down by two lines
                            outFile.write(line + '\n\n\n')
                        elif (num1 == len(form)) or (num1 == len(form)-1) or (num1 == len(form)-2):
                            continue
                        else:
                            outFile.write(line + '\n')
                                 
        if Global.cfgFile['ConfirmSuccess']: 
            dlg = wx.MessageDialog(None, "Everything went well",
                            "Success!", style= wx.OK | wx.ICON_INFORMATION)
            response = dlg.ShowModal()
            dlg.Destroy()


        
#----------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "FSR-1500",wx.Size(550,425))
        frame.Show()
        return True


#===============================================================================================
#      Where it all begins...
#===============================================================================================
def main(argv=None):
    if argv is None:
        argv = sys.argv

    test = Global.cfgFile.validate(Global.vtor, copy=True)
    Global.cfgFile.write()
        

    Global.noMatch = {}
    Global.dataLoaded = False
    
    app = MyApp(0)    
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()

from __future__ import with_statement
from pprint import pprint
import sys, os, time, re, string, copy, traceback, wx
import wx.lib.filebrowsebutton as filebrowse
from configobj import ConfigObj
from validate import Validator
from fsrStuff.X12 import X12Thing, Carrier, X12_837
from fsrStuff.umFuncs import parseDirectDat, RecordGenerator
import urllib
import wx.lib.dialogs
try:
    from wx.gizmos import EditableListBox
except ImportError:
    from wx.adv import EditableListBox
try:
    import wx.lib.inspection
except ImportError:
    pass
try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO

class Global(object):
    """Generic container for shared variables."""
    cfgFileName = os.getcwd() + os.sep + 'fsr_x12.ini'
    tmpStr = """
    [Current]
    directDat = string(default="direct.dat")
    npiXMLFile = string(default="npiMap.XML")
    gemFile = string(default="2015_I9gem.txt")
    InHist = string_list(default=None)
    OutHist = string_list(default=None)
    Submitter = string(default=None)
    Carrier = string(default=None)
    MainSize = tuple()
    MainPos = tuple()
    SummarySize = tuple()
    SummaryPos = tuple()
    DoNPI = boolean(default=True)
    Do5010 = boolean(default=True)
    DoICD10 = boolean(default=True)
    XmitClaims = boolean(default=True)
    DLReports = boolean(default=True)
    ConfirmSuccess = boolean(default=True)
    SubSubst = boolean(default=True)
    CvtCarrier = boolean(default=True)
    KeepLicense = boolean(default=False)
    KeepInsID = boolean(default=False)
    KeepTaxID = boolean(default=True)
    KeepUxIN = boolean(default=True)
    KeepFacID = boolean(default=False)
    UseSecID = boolean(default=True)
    FixSSN = boolean(default=True)
    ProcessNTE = boolean(default=True)
    ForceTest = boolean(default=False)
    NewLines = boolean(default=True)
    DNtoDQ = boolean(default=False)
    AddTrace = boolean(default=True)
    DedupPER = boolean(default=True)
    StripCodes = boolean(default=True)
    UniqueFile = boolean(default=False)
    SubstMBI = boolean(default=True)
    SentDir = string(default="\\bbs\\sent")
    LastNameOA = boolean(default=True)
    [JobProfiles]
    [[__many__]]
    Submitter = string(default=" ")
    Carrier = string(default=" ")
    DoNPI = boolean(default=True)
    Do5010 = boolean(default=True)
    DoICD10 = boolean(default=True)
    SubSubst = boolean(default=True)
    CvtCarrier = boolean(default=True)
    KeepLicense = boolean(default=False)
    KeepInsID = boolean(default=False)
    KeepTaxID = boolean(default=True)
    KeepUxIN = boolean(default=True)
    KeepFacID = boolean(default=False)
    UseSecID = boolean(default=True)
    FixSSN = boolean(default=True)
    ProcessNTE = boolean(default=True)
    ForceTest = boolean(default=False)
    NewLines = boolean(default=True)
    DNtoDQ = boolean(default=False)
    AddTrace = boolean(default=True)
    DedupPER = boolean(default=True)
    StripCodes = boolean(default=True)
    InFile = string(default="")
    OutFile = string(default="")
    UniqueFile = boolean(default=False)
    SubstMBI = boolean(default=True)

    """
    cfgSpec = StringIO.StringIO(tmpStr)
    cfgFile = ConfigObj(cfgFileName,
                configspec=cfgSpec, raise_errors=True, write_empty_values = True,
                create_empty=True, indent_type='    ', list_values = True)
    vtor = Validator()

class Log(object):
    """Log output is redirected to the status bar of the containing frame."""
    def WriteText(self,text_string):
        self.write(text_string)
    def write(self,text_string):
        wx.GetApp().GetTopWindow().SetStatusText(text_string)

class SummaryDialog(wx.Dialog):
    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=(50,50),
            style=wx.DEFAULT_DIALOG_STYLE, text=""):
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style)

        sizer = wx.BoxSizer(wx.VERTICAL)

        text = wx.TextCtrl(self, -1, text, size=wx.Size(775,575), style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
        text.SetHelpText("Here's a brief summary of the billing file you're about to send.")
        font1 = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        text.SetFont(font1)

        sizer.Add(text, 1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        btnsizer = wx.StdDialogButtonSizer()

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)


class ModemSession(wx.Dialog):
    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=(50,50),
            style=wx.OK|wx.CAPTION|wx.RESIZE_BORDER|wx.CLOSE_BOX|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.SYSTEM_MENU, text=""):
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.apax = Apax(self, size=wx.Size(680,400), style=wx.SUNKEN_BORDER)

        sizer.Add(self.apax, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        btnsizer = wx.StdDialogButtonSizer()


        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)


#---GUI

class MyFrame(wx.Frame):
    ID_LOAD = wx.NewId()

    def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, size=size, style=style)
        self.CreateStatusBar(1)
        self.log=Log()

        pnl = wx.Panel(self)

        #---Create checkboxes

        Opts = [
            {"Name": "KeepInsID", "Label":"Insurance", "Tip":"Keep \"legacy\" insurance IDs codes(Medicare, Medicaid, BX/BS, etc.?"},
            {"Name": "KeepLicense", "Label":"License", "Tip":"Keep state license numbers?"},
            {"Name": "KeepUxIN", "Label":"UPIN/USIN", "Tip":"Keep UPIN and USIN codes?"},
            {"Name": "KeepFacID", "Label":"Facility ID", "Tip":"Keep legacy facility ID codes?"},
            {"Name": "KeepTaxID", "Label":"EIN/SSN", "Tip":"Keep tax IDs - EINs and SSNs?"},
            {"Name": "DNtoDQ", "Label":"Physical therapy?", "Tip":"Convert \"NM1*DN\" records (referring physician) to \"NM1*DQ\" (supervising physician)?\n*** This is ONLY for physical therapy billing! ***"},
            #{"Name": "FixSSN", "Label":"Fix SSNs?", "Tip":"If a doctor's SSN starts with one or more zeroes, they sometimes get dropped during billing, \nresulting in a SSN shorter than nine digits. \nDo you want me to check for short SSNs, and pad them with zeroes if I find them?"},
            #{"Name": "ProcessNTE", "Label":"Process NTEs?", "Tip":"If you enter 'NDC#' followed by the 11-digit NDC, and/or 'F2', 'GR', 'ME', 'ML', or 'UN' followed by the 10-digit quantity (7 digits to the left of the decimal point, 3 to the right) in the 'Box 19a' field of the Ailment\nrecord in UltraMed, I can process it into the proper format."},
            {"Name": "ForceTest", "Label":"Force Test?", "Tip":"Shall I set the test/production flag to Test (regardless of what it was originally?"},
            {"Name": "AddTrace", "Label":"Add Trace?", "Tip":"Shall I add a trace number so each 837 can be matched up to its reports?\n Otherwise, all files have the trace number 00001, which leads to confusion..."},
            {"Name": "DedupPER", "Label":"De-duplicate PER?", "Tip":"Loops 1000 (submitter) and 2010AA (billing provider) can't have the same contact name (per Noridian).\n If this box is checked, I'll put the first word in 1000 and the second in 2010AA."},
            {"Name": "StripCodes", "Label":"Strip spaces?", "Tip":"An extra space at the end of a single ID code will cause the entire file to be rejected.\n Shall I check all ID codes and strip off any space I find? (Might take an extra second or two.)"},
            {"Name": "NewLines", "Label":"Separate lines?", "Tip":"Shall I break the converted file into separate lines to make it easy to read?\n A few carriers may have problems with this, but generally it shouldn't affect processing."},
            #{"Name": "Do5010", "Label":"Convert 4010 claims to 5010?", "Tip":"5010 is mandatory starting in 2012..."},
            {"Name": "DoICD10", "Label":"Process diagnoses as ICD-10?", "Tip":"If dates of service are after October 1, 2015..."},
            {"Name": "DoNPI", "Label":"Perform NPI conversion?", "Tip":"ALWAYS check this if you're using UltraMed."},
            #{"Name": "XmitClaims", "Label":"Send claims?", "Tip":"Send claims after converting them?"},
            #{"Name": "DLReports", "Label":"Download reports?", "Tip":"Download reports (if available) from BBS?"},
            {"Name": "ConfirmSuccess", "Label":"Show summary?", "Tip":"If we finish successfully, do you want a brief summary of the file you're about to send? \nIf this box is unchecked, the program will quit silently when everything goes OK."},
            #{"Name": "UseSecID", "Label":"Use secondary ID?", "Tip":"Use \"secondary\" ID codes to match the rendering provider's NPI?\nIf not checked, will use EIN or SSN; if checked, will wait to find Medicare ID from next record."},
            {"Name": "SubSubst", "Label":"Replace Submitter?", "Tip":"Replace the submitter number in the billing file?"},
            {"Name": "CvtCarrier", "Label":"Convert Carrier?", "Tip":"Replace the carrier information in the billing file?"},
            {"Name": "UniqueFile", "Label":"Unique Filename?", "Tip":"Create a unique filename for each billing file?"},
            {"Name": "SubstMBI", "Label":"Insert new MBI?", "Tip":"If found, substitute new Medicare Beneficiary ID (from Message2 field)?"}, ]
        self.Options = {}
        for opt in Opts:
            nom, lbl, tip = opt["Name"], opt["Label"], opt["Tip"]
            self.Options[nom] = wx.CheckBox(pnl, -1, lbl, style=wx.ALIGN_LEFT, name=nom)
            self.Options[nom].SetToolTip(wx.ToolTip(tip))
            self.Options[nom].SetValue(Global.cfgFile['Current'][nom])
            self.Bind(wx.EVT_CHECKBOX, self.OnChange, self.Options[nom])

        #---Create filepickers

        fpOpt = {
            "In": {"Label":"Original: ", "Title":"Tell me where to find the original file", "Mode":wx.FD_OPEN},
            "Out":{"Label":"Converted:", "Title":"Tell me where to save the converted file", "Mode":wx.FD_SAVE}, }
        self.filePicker ={}
        for option, detail in fpOpt.iteritems():
            self.filePicker[option] = filebrowse.FileBrowseButtonWithHistory(pnl, -1,
                    labelText=detail["Label"], fileMask='*.*',
                    fileMode=detail["Mode"], dialogTitle=detail["Title"],
                    changeCallback=lambda x, option=option: self.fpCallback(x, option))
            if Global.cfgFile['Current'].has_key(option+'Hist'):
                try:                            #is it a single item,
                    tmpList = Global.cfgFile['Current'][option + "Hist"].split(',')
                except AttributeError:          # or a list?
                    tmpList = Global.cfgFile['Current'][option + "Hist"]
                self.filePicker[option].callCallback = False
                self.filePicker[option].SetHistory(tmpList, 0)
                self.filePicker[option].callCallback = True

        outerMost = wx.BoxSizer(wx.VERTICAL)

        #---Profiles and buttons

        boxTop = wx.BoxSizer(wx.HORIZONTAL)
        boxTopRight = wx.BoxSizer(wx.VERTICAL)

        self.elb = EditableListBox(
                    pnl, -1, "Job Profiles:", wx.DefaultPosition, wx.Size(size[0] -50, size[1]/5) )
        self.elb.SetStrings(Global.cfgFile['JobProfiles'].keys())

        self.List = self.elb.GetListCtrl()
        self.List.Bind(wx.EVT_TEXT_ENTER, self.NewProfile)
        self.List.Select(0)
        self.ListDelBtn = self.elb.GetDelButton()

        self.ListDelBtn.Bind(wx.EVT_BUTTON, self.DeleteProfile)
        #self.List.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnExcludesChange)

        Buttons = [
            {"Name": "Load",   "Tip": "Click here to load (or re-load) the configuration \nyou selected at left."},
            {"Name": "Save",   "Tip": "Click here to save your current settings into the \nconfiguration you selected (or typed) at left.\n -  If the configuration didn't exist yet,\n    it will be created with your current settings.\n -  If it already existed, it will be updated."},
            {"Name": "Go",     "Tip": "Click here to proceed using the current settings."},
            {"Name": "Cancel", "Tip": "Click here to exit without doing anything."},
            ]
        for btn in Buttons:
            b = wx.Button(pnl, -1, label=btn["Name"], name=btn["Name"])
            b.SetToolTip(wx.ToolTip(btn["Tip"]))
            boxTopRight.Add(b, 0, wx.ALIGN_CENTER|wx.ALL)
            boxTopRight.Add((5,5), 0, wx.EXPAND)
            if btn["Name"] == "Save":
                boxTopRight.Add(wx.StaticLine(pnl), 0, wx.EXPAND)
                boxTopRight.Add((2,2), 0, wx.EXPAND)

            self.Bind(wx.EVT_BUTTON, self.OnClick, b)

        #boxTopRight.Add(self.Options["Do5010"], 0, wx.ALL, 2)
        boxTopRight.Add(self.Options["DoICD10"], 0, wx.ALL, 2)
        boxTopRight.Add(self.Options["DoNPI"], 0, wx.ALL, 2)
        #boxTopRight.Add(self.Options["XmitClaims"], 0, wx.ALL, 2)
        #boxTopRight.Add(self.Options["DLReports"], 0, wx.ALL, 2)
        boxTopRight.Add(self.Options["ConfirmSuccess"], 0, wx.ALL, 2)

        boxTop.Add(self.elb, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
        boxTop.Add(boxTopRight, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, -1)
        outerMost.Add(boxTop, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 10)


        #---File locations
        box2 = wx.StaticBox(pnl, -1, "Location of billing files:")
        boxMidLeft = wx.StaticBoxSizer(box2, wx.VERTICAL)


        boxMidLeft.Add(self.filePicker["In"], 0, wx.ALIGN_LEFT|wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        boxMidLeft.Add(self.filePicker["Out"], 0, wx.ALIGN_LEFT|wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        boxMidLeft.Add(self.Options["UniqueFile"], 0, wx.ALL, 2)

        outerMost.Add(boxMidLeft, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 10)


        #---Options
        boxOptSiz = wx.BoxSizer(wx.HORIZONTAL)
        boxNPIOpt = wx.StaticBox(pnl, -1, "Preserve \"legacy\" IDs:")
        boxNPIOptSiz = wx.StaticBoxSizer(boxNPIOpt, wx.VERTICAL)
        # ===experimenting with simply assuming UseSecID is True...  we'll see...
        #boxNPIOptSiz.Add(self.Options["UseSecID"], 1, wx.ALIGN_CENTER)
        #==================================================================
        msg = '''Which "legacy" (pre-NPI) codes, if any, should I leave in the converted file?
        Please note: this only applies to codes that already existed in the original file.
        This program does NOT insert legacy codes that weren't in the original billing!'''
        boxNPIOpt.SetToolTip(wx.ToolTip(msg))
        grid3 = wx.FlexGridSizer(3, 2, 5, 5)
        grid3.Add(self.Options["KeepInsID"])
        grid3.Add(self.Options["KeepLicense"])
        grid3.Add(self.Options["KeepUxIN"])
        grid3.Add(self.Options["KeepTaxID"])
        grid3.Add(self.Options["KeepFacID"])


        boxNPIOptSiz.Add(grid3, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        boxOthOpt = wx.StaticBox(pnl, -1, "Other processing:")
        boxOthOptSiz = wx.StaticBoxSizer(boxOthOpt, wx.VERTICAL)
        grid4 = wx.FlexGridSizer(4, 2, 5, 0)
        grid4.Add(self.Options["DNtoDQ"])
        #grid4.Add(self.Options["FixSSN"])
        grid4.Add(self.Options["ForceTest"])
        grid4.Add(self.Options["AddTrace"])
        grid4.Add(self.Options["DedupPER"])
        grid4.Add(self.Options["StripCodes"])
        grid4.Add(self.Options["NewLines"])
        grid4.Add(self.Options["SubstMBI"])
        grid4.Add((0,0),1)

        boxOthOptSiz.Add(grid4, 1, wx.ALIGN_CENTER|wx.ALL, 5)


        #---Carrier stuff
        boxCarStat = wx.StaticBox(pnl, -1, "Submitter/Carrier info:")
        boxCarrier = wx.StaticBoxSizer(boxCarStat, wx.HORIZONTAL)
        gridCarrier = wx.FlexGridSizer(2, 2, 5, 0)

        #CarrierList = ['NHICNorth', 'NHICSouth', 'CignaDMERC', 'ColoradoMedicare', 'ColoradoMedicaid', 'MinnesotaMedicare', 'PalmettoGBA']
        CarrierList = Carrier.carDict.keys()

        self.txtSubNum = wx.TextCtrl(pnl,-1,Global.cfgFile['Current']['Submitter'], size=(150, -1), name="Submitter")
        self.cmbCarrier = wx.ComboBox(pnl, -1, Global.cfgFile['Current']['Carrier'], size=(160, -1),
                         choices=CarrierList, style=wx.CB_READONLY | wx.CB_SORT, name="Carrier")

        self.Bind(wx.EVT_TEXT, self.OnChange, self.txtSubNum)
        self.Bind(wx.EVT_TEXT, self.OnChange, self.cmbCarrier)
        self.Bind(wx.EVT_COMBOBOX, self.OnChange, self.cmbCarrier)

        gridCarrier.Add(self.Options["SubSubst"], 0, wx.ALIGN_LEFT|wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        gridCarrier.Add(self.Options["CvtCarrier"], 0, wx.ALIGN_LEFT|wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        gridCarrier.Add(self.txtSubNum, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        gridCarrier.Add(self.cmbCarrier, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        boxCarrier.Add(gridCarrier, 0, 0, wx.ALIGN_CENTER|wx.EXPAND)

        boxOptSiz.Add(boxNPIOptSiz, 1, wx.ALIGN_CENTER|wx.ALIGN_TOP|wx.ALL, 5)
        boxOptSiz.Add(boxOthOptSiz, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, 5)
        boxOptSiz.Add(boxCarrier, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, 10)
        outerMost.Add(boxOptSiz, 0, wx.ALIGN_RIGHT|wx.EXPAND|wx.ALL, -1)


        #---Cleanup
        pnl.SetSizer(outerMost)

    def fpCallback(self, evt, option):
        value = evt.GetString()
        if not value:
            return
        if (self.filePicker["Out"].GetValue() == self.filePicker["In"].GetValue()):
            dlg = wx.MessageDialog(None, "You're asking me to over-write the original file.  You sure about that?",
                "You have chosen... oddly.",
                style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            response = dlg.ShowModal()
            dlg.Destroy()
            if (response == wx.ID_NO):
                return()
        history = self.filePicker[option].GetHistory()
        if value in history:  # if it already existed, remove it
            history.pop(history.index(value))
        history.insert(0, value)  # either way, insert it at the head of the list
        while len(history) > 10: # pop items off the end until history is x items long...
            history.pop()
        self.filePicker[option].SetHistory(history)
        self.filePicker[option].GetHistoryControl().SetStringSelection(value)
        Global.cfgFile['Current'][option+'Hist'] = history
        Global.cfgFile.write()

    def NewProfile(self, strJob):
        #print(strJob, ' - New')
        return

    def RenameProfile(self,evt):
        tmpSel = self.List.GetFocusedItem()
        if (tmpSel == -1): tmpSel=0
        strJob = self.List.GetItemText(tmpSel)
        if strJob.strip() == "":
            return
        evt.Skip()
        #print(strJob, ' - Rename')


    def DeleteProfile(self, evt):
        tmpSel = self.List.GetFocusedItem()
        if (tmpSel == -1): tmpSel=0
        strJob = self.List.GetItemText(tmpSel)
        if strJob.strip() == "":
            return
        evt.Skip()
        #print(strJob, ' - Delete')
        try:
            del Global.cfgFile['JobProfiles'][strJob]
            Global.cfgFile.write()
        except:
            self.ErrOKOnly("I couldn't delete that profile. \nTry restarting the program.", "Error deleting selected profile")

    def LoadProfile(self, strJob):
        #print(strJob, ' - Load')
        try:
            self.txtSubNum.SetValue(Global.cfgFile['JobProfiles'][strJob]['Submitter'])
            self.cmbCarrier.SetValue(Global.cfgFile['JobProfiles'][strJob]['Carrier'])
            self.filePicker["In"].SetValue(Global.cfgFile['JobProfiles'][strJob]['InFile'])
            self.filePicker["Out"].SetValue(Global.cfgFile['JobProfiles'][strJob]['OutFile'])
            for chk in [
                    'CvtCarrier', 'KeepLicense', 'KeepInsID', 'KeepTaxID', 'KeepUxIN',
                    'KeepFacID', 'FixSSN', 'DNtoDQ', 'SubSubst', 'AddTrace', 'DedupPER',
                    'StripCodes', 'SubstMBI']:
                self.Options[chk].SetValue(Global.cfgFile['JobProfiles'][strJob][chk])
        except:
            #traceback.print_exc()
            dlg = wx.MessageDialog(None, "I couldn't load that profile. \nYou'll need to save it again, I'm afraid.",
                "Error loading selected profile",
                style=wx.OK | wx.ICON_ERROR)
            response = dlg.ShowModal()
            dlg.Destroy()

    def SaveProfile(self, strJob):
        #print(strJob, ' - Save')
        Global.cfgFile['JobProfiles'][strJob] = {}
        Global.cfgFile['JobProfiles'][strJob]['Submitter']  = self.txtSubNum.GetValue()
        Global.cfgFile['JobProfiles'][strJob]['Carrier']  = self.cmbCarrier.GetValue()
        Global.cfgFile['JobProfiles'][strJob]['InFile'] = str(self.filePicker["In"].GetValue())
        Global.cfgFile['JobProfiles'][strJob]['OutFile'] = str(self.filePicker["Out"].GetValue())
        for chk in [
                'CvtCarrier', 'KeepLicense', 'KeepInsID', 'KeepTaxID', 'KeepUxIN',
                'KeepFacID', 'DNtoDQ', 'AddTrace', 'DedupPER', 'StripCodes', 'SubstMBI']:
            Global.cfgFile['JobProfiles'][strJob][chk]  = self.Options[chk].GetValue()
        Global.cfgFile.write()

    def OnChange(self, evt):
        option = evt.GetEventObject().Name
        Global.cfgFile['Current'][option] = evt.GetEventObject().GetValue()
        Global.cfgFile.write()


    def OnClick(self, event):
        btn = event.GetEventObject().Name
        if (btn == "Cancel"):
            self.Close(True)
            #sys.exit()

        if (btn == "Go"):
            self.DoIt(str(self.filePicker["In"].GetValue()), str(self.filePicker["Out"].GetValue()))
        #== Get selected job profile name, exit if blank (last item is usually blank)
        tmpSel = self.List.GetFocusedItem()
        if (tmpSel == -1): tmpSel=0
        strJob = self.List.GetItemText(tmpSel)
        if strJob.strip() == "":
            return

        if (btn == "Load"):
            self.LoadProfile(strJob)

        if (btn == "Save"):
            self.SaveProfile(strJob)

        if (btn == "Delete"):
            self.DeleteProfile(strJob)

    def ErrOKOnly(self, inst, lbl):
        dlg = wx.MessageDialog(None, inst, lbl, style=wx.OK | wx.ICON_ERROR)
        response = dlg.ShowModal()
        dlg.Destroy()

    def CheckForFile(self, item):
        if item == 'npiXMLFile':
            tmpStr = '''
            I can't continue without an NPI mapping file.
            In the next dialog, show me where to find the file
              you created when you ran the NPI Update program.
            (Hint: it's probably called "npiMap.XML")
            '''
            cap = "Need NPI lookup file"
            dF="npiMap.XML"
            wC="*.xml"
        if item == 'directDat':
            tmpStr = '''
            I can't continue without the UltraMed direct.dat file.
            In the next dialog, show me where to find it.
            (Hint: it's probably in your UltraMed directory")
            '''
            cap = "Need direct.dat file"
            dF="direct.dat"
            wC="*.dat"
        if item == 'gemFile':
            tmpStr = '''
            I need the ICD-9 to ICD-10 GEM file.
            In the next dialog, show me where to find it.
            (Hint: it's probably in your UltraMed directory")
            '''
            cap = "Need GEM file"
            dF="2015_I9gem.txt"
            wC="*.txt"


        if ((str(Global.cfgFile['Current'][item]) =="") or not (os.path.isfile(urllib.url2pathname(str(Global.cfgFile['Current'][item]))))):
            dlg = wx.MessageDialog(None, tmpStr, cap, wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            dlg = wx.FileDialog(self, cap, defaultDir=os.getcwd(),defaultFile=dF, wildcard=wC, style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPaths()[0]
                self.log.WriteText('%s' % path)
                Global.cfgFile['Current'][item] = unicode(urllib.pathname2url(path))
                Global.cfgFile.write()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return

    def DoIt(self,inPathStr, outPathStr):
        self.log.write('About to convert %s' % inPathStr)
        if not (os.path.exists(urllib.url2pathname(inPathStr))):
            self.log.write("Select a valid source file!")
            return
        self.CheckForFile('npiXMLFile')
        self.CheckForFile('directDat')
        self.CheckForFile('gemFile')

        offices = parseDirectDat(urllib.url2pathname(str(Global.cfgFile['Current']["directDat"])))
        tmpList = offices.keys()
        tmpList.sort()
        if len(tmpList) == 1:
            offNum = offices.keys()[0]
            office = offices[offNum]
            self.log.WriteText('Processing diagnoses for office %s\n' % offNum)
        else:
            dlg = wx.SingleChoiceDialog(self, 'Select office to process', 'Select office', tmpList, wx.CHOICEDLG_STYLE)
            if dlg.ShowModal() == wx.ID_OK:
                offNum = dlg.GetStringSelection()
                office = offices[offNum]
                self.log.WriteText('Processing diagnoses for office %s\n' % offNum)
                dlg.Destroy()
            else:
                return

        try:
            thingy = X12_837(inPathStr, Global.cfgFile['Current']['npiXMLFile'])
        except Exception, inst:
            self.ErrOKOnly(traceback.format_exc(), "There was a problem during initial processing")
            return

        try:        # Don't see any reason to ever NOT do this...
            thingy.FixSSN()
        except Exception, inst:
            self.ErrOKOnly(traceback.format_exc(), "There was a problem while trying to fix SSNs")
            return


        if Global.cfgFile['Current']['Carrier'] in ("Jur. E NorCal"): # Only NorCal for now; might expand
            try:
                thingy.PatientHome2310C()
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem while adding patient home as place of service")
                return

        if Global.cfgFile['Current']['SubstMBI']:
            try:
                thingy.SubstMBI(offNum)
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem during new Medicare Beneficiary ID substitution")
                return
            if len(thingy.badMBI) > 0:
                tmpStr = ""
                for chartNum, desc in thingy.badMBI.iteritems():
                    tmpStr += chartNum + " - " + desc + "\n"
                tmpStr += "Proceed?"
                dlg = wx.MessageDialog(None, tmpStr,
                            "Some Medicare Beneficiary IDs (MBIs) are invalid.  Continue anyway?", style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                response = dlg.ShowModal()
                dlg.Destroy()
                if (response == wx.ID_NO):
                    return
            if len(thingy.noMBI) > 0:
                tmpStr = ""
                for chartNum, desc in thingy.noMBI.iteritems():
                    tmpStr += chartNum + " - " + desc + "\n"
                tmpStr += "Proceed?"
                dlg = wx.MessageDialog(None, tmpStr,
                            "Some claims have no valid Medicare Beneficiary IDs (MBIs) and will most likely be denied.  Continue anyway?", style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                response = dlg.ShowModal()
                dlg.Destroy()
                if (response == wx.ID_NO):
                    return

        if Global.cfgFile['Current']['DoICD10']:
            gemNotes = {}
            try:
                gemNotes = thingy.doICD10(office, urllib.url2pathname(str(Global.cfgFile['Current']["gemFile"])))
                self.log.WriteText('Finished processing diagnoses')
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem while trying to process ICD10s")
                return
            if len(gemNotes) > 0:
                gemNotes += "\nProceed?"
                dlg = wx.MessageDialog(None, gemNotes,
                            "Status of ICD-9 to ICD-10 mapping for this claim file", style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                response = dlg.ShowModal()
                dlg.Destroy()
                if (response == wx.ID_NO):
                    return


        if Global.cfgFile['Current']['DoNPI']:
            try:
                thingy.NPIConversion(UseSecID=Global.cfgFile['Current']['UseSecID'], KeepLicense=Global.cfgFile['Current']['KeepLicense'],
                                    KeepTaxID=Global.cfgFile['Current']['KeepTaxID'], KeepInsID=Global.cfgFile['Current']['KeepInsID'],
                                    KeepUxIN=Global.cfgFile['Current']['KeepUxIN'], KeepFacID=Global.cfgFile['Current']['KeepFacID'])
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem during NPI conversion")
                return

            if len(thingy.npiMap.noMatch) > 0:
                tmpStr = ""
                for name, desc in thingy.npiMap.noMatchX.iteritems():
                    tmpStr += desc + "\n"
                tmpStr += "Proceed?"
                dlg = wx.MessageDialog(None, tmpStr,
                            "Some NPIs are missing.  Continue anyway?", style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                response = dlg.ShowModal()
                dlg.Destroy()
                if (response == wx.ID_NO):
                    return
            if len(thingy.noLegs) > 0:
                tmpStr = ""
                for name, desc in thingy.noLegs.iteritems():
                    tmpStr += desc + "\n"
                tmpStr += "Proceed?"
                dlg = wx.MessageDialog(None, tmpStr,
                    "Some entities had no legacy codes - so no NPIs.  Continue anyway?", style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                response = dlg.ShowModal()
                dlg.Destroy()
                if (response == wx.ID_NO):
                    return


        if Global.cfgFile['Current']['SubSubst']:
            try:
                thingy.SubmitterSubst(SubNum=Global.cfgFile['Current']['Submitter'])
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem during submitter substitution")
                return


        if Global.cfgFile['Current']['CvtCarrier']:
            try:
                thingy.CarrierConversion(ShortName=Global.cfgFile['Current']['Carrier'])
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem during carrier/submitter conversion")
                return


        if Global.cfgFile['Current']['DNtoDQ']:
            try:
                thingy.DNtoDQ()
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem while converting referring physicians to supervising")
                return


        if Global.cfgFile['Current']['AddTrace']:
            try:
                thingy.addTraceNumber()
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem while adding trace number")
                return


        if Global.cfgFile['Current']['StripCodes']:
            try:
                thingy.StripCodes()
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem while stripping spaces from NM1 codes")
                return


        if Global.cfgFile['Current']['DedupPER']:
            try:
                thingy.DedupPER()
            except Exception, inst:
                dlg = wx.MessageDialog(None,
                    "Tried to de-duplicate the contact names, but there's only one name\nin the submitter file.\nThis will cause rejection by Noridian, but other carriers (Medi-Cal?) \nmay be OK with it.\n  Proceed?", "Duplicate contact name", style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                response = dlg.ShowModal()
                dlg.Destroy()
                if (response == wx.ID_NO):
                    return

        #if Global.cfgFile['Current']['Do5010']:  Always going to do this, as of 10/10/2015
        try:
            thingy.CvtTo5010()
        except Exception, inst:
            self.ErrOKOnly(traceback.format_exc(), "There was a problem while converting 4010 format to 5010.")
            return
        try:
            thingy.CheckZips()
        except Exception, inst:
            self.ErrOKOnly(traceback.format_exc(), "There was a problem while checking ZIP codes.")
            return
        if len(thingy.shortZips) > 0:
            tmpStr = ""
            for name, desc in thingy.shortZips.iteritems():
                tmpStr += desc + "\n"
            tmpStr += "Proceed with these substitutions?"
            dlg = wx.MessageDialog(None, tmpStr,
                "Some ZIP codes were not 9 digits.", style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            response = dlg.ShowModal()
            dlg.Destroy()
            if (response == wx.ID_NO):
                return

        if Global.cfgFile['Current']['ProcessNTE']:
            try:
                thingy.ProcessNTE()
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem while extracting NDCs and units from note fields and turning them into LIN and CTP records")
                return

        '''  This is on hold pending confirmation...
        if Global.cfgFile['Current']['LastNameOA']:
            try:
                thingy.LastNameOA()
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem while adding comma to end of last name")
                return
        '''

        if Global.cfgFile['Current']['ForceTest']:
            try:
                thingy.ForceTest()
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem while setting Test/Production flag to T")
                return

        try:
            thingy.tofile(outPathStr, Global.cfgFile['Current']['NewLines'])
        except Exception, inst:
            self.ErrOKOnly(traceback.format_exc(), "There was a problem while saving the converted file to outgoing location")
            return

        try:
            sentDir = Global.cfgFile['Current']['SentDir']
            if not os.path.isdir(sentDir):
                os.makedirs(sentDir)
            if not thingy.traceNum:
                thingy.traceNum = int(time.time()).__str__()
            dst_file = os.path.join(sentDir, thingy.traceNum + ".837")
            thingy.tofile(dst_file, Global.cfgFile['Current']['NewLines'])

        except Exception, inst:
            self.ErrOKOnly(traceback.format_exc(), "There was a problem while saving the converted file to archive location")
            return

        #---Invoking summary dialog
        if Global.cfgFile['Current']['ConfirmSuccess']:
            try:
                tmpStr = text=str(thingy)
            except Exception, inst:
                self.ErrOKOnly(traceback.format_exc(), "There was a problem creating the summary")
                return
            dlg = SummaryDialog(self, -1, "Summary", text=tmpStr,
                style=wx.OK|wx.CAPTION|wx.RESIZE_BORDER|wx.CLOSE_BOX|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.SYSTEM_MENU)
            font1 = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier')
            dlg.SetFont(font1)
            response = dlg.ShowModal()
            dlg.Destroy()
            if (response == wx.ID_CANCEL):
                return

        #---Modem sessions
        if Global.cfgFile["Current"]["XmitClaims"]:
            dlg = ModemSession(self, -1, "Mo")
            response = dlg.ShowModal()
            dlg.Destroy()
        '''

        if Global.cfgFile["Current"]["DLReports"]:
            dlg = ModemSession(self, -1, "Downloading reports")
            response = dlg.ShowModal()
            dlg.Destroy()
        '''
#----------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "FSR-X12: for all your ANSI EDI needs!",wx.Size(850,525))
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

    app = MyApp(0)
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()

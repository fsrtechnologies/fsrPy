from __future__ import with_statement
from time import strftime
import wx, sys, os, wx.lib.inspection
import  wx.lib.scrolledpanel as scrolled
import Ft.Lib.Uri as uri
import urllib
import pickle
import csv
#===These are mine: =====
from fsrStuff.ConfigFile import *
from fsrStuff.SortCheck import *
from fsrStuff.umFuncs import *
from win32com.shell import shell
try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO

class Global:
    """Generic container for shared variables."""
    cfgFileName = os.getcwd() + os.sep + 'fsr_labels.xml'
    cfgFile = ConfigFile(cfgFileName, "directDat")

class Log:
    """Log output is redirected to the status bar of the containing frame."""
    def __init__(self):
        with open(os.getcwd() + os.sep + 'labels.log', 'w') as logfile:
            logfile.write('Let the games begin....' + '\n')
        
    def WriteText(self,text_string):
        self.write(text_string)
    def write(self,text_string, fileOnly=False):
        with open(os.getcwd() + os.sep + 'labels.log', 'a+') as logfile:
            logfile.write(text_string + '\n')
        if not fileOnly: 
            wx.GetApp().GetTopWindow().SetStatusText(text_string)


class Selector(wx.Frame):
    def __init__(self, parent, id, title, size=(750,1250)):
        wx.Frame.__init__(self, parent, id, title, size)
        self.CreateStatusBar(1)
        self.log = Log()
        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel, -1)
        rightPanel = wx.Panel(panel, -1)

        #============================================================
        # Gettin' the data, nom nom nom
        self.loadDirect()
        self.loadDocList()
        #============================================================

        tipString = '''We'll generate records for patients with birthdays between the Start Date and the End Date. 
        (Never mind the year - only the month and day are considered.)
        (The year defaults to 2008 because it was a leap year, so you can select Feb 29.)
        To get all birthdates UP TO a certain date, leave the Start Date un-checked.
        To get all birthdates SINCE a certain date, leave the End Date un-checked.
        To get all patients, regardless of birthdate, leave both dates un-checked.'''
        self.BDayStart = wx.DatePickerCtrl(leftPanel, dt=(wx.DateTimeFromDMY(1,0,2008)), size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
        self.BDayEnd   = wx.DatePickerCtrl(leftPanel, size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
        self.BDayStart.SetRange(wx.DateTimeFromDMY(1,0,2008), wx.DateTimeFromDMY(31,11,2008))
        self.BDayEnd.SetRange(wx.DateTimeFromDMY(1,0,2008), wx.DateTimeFromDMY(31,11,2008))
        self.BDayEnd.SetToolTipString(tipString)
        self.BDayStart.SetToolTipString(tipString)


        tipString = '''We'll generate records for patients who were last seen (by the doctors you've selected at the right)
            between Start Date and End Date. 
        To get all dates of service UP TO a certain date, leave the Start Date un-checked.
        To get all dates of service SINCE a certain date, leave the End Date un-checked.
        If you leave both dates un-checked, we'll print labels whose PRIMARY doctor is one of the ones you've selected.'''
        self.dpcStart = wx.DatePickerCtrl(leftPanel, size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
        self.dpcStart.SetToolTipString(tipString)
        self.dpcEnd   = wx.DatePickerCtrl(leftPanel, size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
        self.dpcEnd.SetToolTipString(tipString)

        self.chkList = SortedCheckList(rightPanel, Global.DocList)
        self.chkList.SetToolTipString("Select providers")
        self.chkList.SetMinSize(wx.Size(250,50))
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        offGrid = wx.GridSizer(4,3,3,3)

        btnLabels   = wx.Button(leftPanel, -1, 'Generate CSV', size=(120, -1))
        self.Bind(wx.EVT_BUTTON, self.OnBtnLabels, id=btnLabels.GetId())


        tipString = '''Should we skip patients who didn't provide a real birthday, 
        and were entered as 01/01/00 or 01/01/01?'''
        self.cbOneOneOne = wx.CheckBox(leftPanel, -1, "Skip 01/01/01?", style=wx.ALIGN_LEFT)
        self.cbOneOneOne.SetToolTipString(tipString)
        self.cbOneOneOh  = wx.CheckBox(leftPanel, -1, "Skip 01/01/00?", style=wx.ALIGN_LEFT)
        self.cbOneOneOh.SetToolTipString(tipString)
        tipString = '''Sometimes the Address 1 field is used for a phone or fax number.  
        Should we skip printing Address 1 if it looks like a phone number?'''
        self.cbDropPh = wx.CheckBox(leftPanel, -1, "Skip Add.#1 if phone?", style=wx.ALIGN_LEFT)
        self.cbDropPh.SetToolTipString(tipString)
        tipString = '''Should we group the patients with obviously-undeliverable addresses into a separate file?'''
        self.cbSepBad = wx.CheckBox(leftPanel, -1, "Separate 'bad' patients?", style=wx.ALIGN_LEFT)
        self.cbSepBad.SetToolTipString(tipString)
        tipString = '''Should we print labels for all ZIP codes, or only for a range of ?'''
        self.cbIgnZip = wx.CheckBox(leftPanel, -1, "All Zip Codes?", style=wx.ALIGN_LEFT)
        self.scStartZip = wx.SpinCtrl(leftPanel, -1, "Starting Zip", (30, 50), style=wx.ALIGN_LEFT)
        self.scStartZip.SetRange(0,99999)
        self.scStartZip.SetValue(0)
        self.scEndZip = wx.SpinCtrl(leftPanel, -1, "Ending Zip", (30, 50), style=wx.ALIGN_LEFT)
        self.scEndZip.SetRange(0,99999)
        self.scEndZip.SetValue(99999)
        
        vbox2.Add((0,0),1)   # empty space at top
        vbox2.Add(wx.StaticText(leftPanel, -1, "Birthdays (MM/DD only):"))
        vbox2.Add(wx.StaticText(leftPanel, -1, "  Start date:"))
        vbox2.Add(self.BDayStart)
        vbox2.Add(wx.StaticText(leftPanel, -1, "  End date:"))
        vbox2.Add(self.BDayEnd)
        vbox2.Add(wx.StaticText(leftPanel, -1, "Invalid birthdays:"))
        vbox2.Add(self.cbOneOneOh)  
        vbox2.Add(self.cbOneOneOne)  
        vbox2.Add(wx.StaticText(leftPanel, -1, " "))
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(wx.StaticText(leftPanel, -1, "Dates of service:"))
        vbox2.Add(wx.StaticText(leftPanel, -1, "  Start date:"))
        vbox2.Add(self.dpcStart)
        vbox2.Add(wx.StaticText(leftPanel, -1, "  End date:"))
        vbox2.Add(self.dpcEnd)  
        vbox2.Add(wx.StaticText(leftPanel, -1, " "))
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(self.cbDropPh)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(self.cbSepBad)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(wx.StaticText(leftPanel, -1, " "))
        vbox2.Add(self.cbIgnZip)
        vbox2.Add(self.scStartZip)
        vbox2.Add(self.scEndZip)
        vbox2.Add(wx.StaticText(leftPanel, -1, " "))
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(btnLabels)
        vbox2.Add((0,0),1)   # empty space to keep second group off the floor

        leftPanel.SetSizer(vbox2)

        vbox.Add(wx.StaticText(rightPanel, -1, "Providers:"))
        vbox.Add(self.chkList, 1, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))

        rightPanel.SetSizer(vbox)

        hbox.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND)
        hbox.Add((3, -1))
        panel.SetSizer(hbox)
        hbox.Fit(self)
        self.SetMinSize(hbox.GetMinSize())
        
        self.Centre()
        self.Show(True)

    def OnBtnLabels(self, event):
        self.log.write('GO button has been pressed...')
        Global.Pats = []
        doChkDates = False
        wrapAround = False
        dateStart = self.dpcStart.GetValue()
        dateEnd = self.dpcEnd.GetValue()
        if (dateStart.IsValid() or dateEnd.IsValid()): #if neither date is checked, we can skip a LOT of work!
            doChkDates = True
            self.log.write("At least one date is selected - need to check service dates")
            if not Global.SvcsLoaded:
                self.log.write("Service dates not yet loaded - doing that now")
                start_time = time.time()
                self.loadLatestSvc()
                self.log.write("Loading service dates took %0.3f seconds" % (time.time() - start_time))
            else:
                self.log.write("Service dates already loaded")
            self.log.write("List of service dates contains: " + str(len(Global.Svc)) + " records")
            if not dateStart.IsValid(): dateStart = wx.DateTimeFromDMY(1,0,1) # remember that months are zero-based
            if not dateEnd.IsValid(): dateEnd = wx.DateTimeFromDMY(30,11,9999)
            if dateEnd.IsEarlierThan(dateStart):
                dateStart = self.dpcStart.SetValue(dateEnd)
            dateStart = wx.DateTime.Format(dateStart, '%Y%m%d')
            dateEnd = wx.DateTime.Format(dateEnd, '%Y%m%d')
            self.log.write("Start date: " + dateStart + " End date: " + dateEnd)

        else:
            self.log.write("No date was selected - will use primary doctor instead")

        # ===============================================================   Build list of criteria 
        self.log.write('Building list of criteria...') # patients with dates of service in desired range...')
        num = self.chkList.GetItemCount()
        criteria = {}
        for offNum, off in Global.offices.iteritems():
            criteria[offNum] = []
        for i in range(num):
            offNum = self.chkList.GetItem(i,0).GetText()
            docNum = self.chkList.GetItem(i,1).GetText()
            if self.chkList.IsChecked(i):
                if doChkDates:
                    self.log.write('Criteria: patients with dates of service in desired range...')
                    for pat, svcDates in Global.Svc[offNum][docNum].iteritems():
                        if ((svcDates[0] >= dateStart) and (svcDates[1] <= dateEnd)):
                                criteria[offNum].append(pat)
                else:
                    self.log.write('Criteria: primary doctor in patient record...')
                    criteria[offNum].append(docNum)
        # ===============================================================
        
        self.log.write('Loading patients, checking birthdays...')
        bDayStart = self.BDayStart.GetValue()
        bDayEnd   = self.BDayEnd.GetValue()
        if not bDayStart.IsValid(): bDayStart = wx.DateTimeFromDMY(1,0,2008) #using a leap year to catch any
        if not bDayEnd.IsValid(): bDayEnd = wx.DateTimeFromDMY(30,11,2008)   # Feb 29 birthdays
        if bDayEnd.IsEarlierThan(bDayStart):
            wrapAround = True
        bDayStart = wx.DateTime.Format(bDayStart, '%m%d')
        bDayEnd   = wx.DateTime.Format(bDayEnd, '%m%d')
        self.log.write("Looking for birthdays between: " + bDayStart + " and: " + bDayEnd)
        bDayStart = int(bDayStart)
        bDayEnd   = int(bDayEnd)
        for offNum, off in Global.offices.iteritems():
            for pat in RecordGenerator(off, "Patient"):
                if (pat.Birthdate[2:] == '000100') and self.cbOneOneOh.IsChecked(): continue
                if (pat.Birthdate[2:] == '010101') and self.cbOneOneOne.IsChecked(): continue
                if doChkDates:
                    if not (pat.ChartNumber in criteria[offNum]): continue
                else:
                    if not (pat.Doctor in criteria[offNum]): continue
                if wrapAround:
                    if ((101 <= int(pat.Birthdate[4:]) <= bDayEnd) or (bDayStart <= int(pat.Birthdate[4:]) <= 1231)):
                        Global.Pats.append(pat)
                else:
                    if (bDayStart <= int(pat.Birthdate[4:]) <= bDayEnd):
                        Global.Pats.append(pat)

        self.log.write('Sorting patients...')
        deco = [ (pat.LastName, pat) for i, pat in enumerate(Global.Pats) ] # create a "decorated" list with the key we want to sort by
        del Global.Pats                     # kill the original list - free up memory

        deco.sort()                         # sort the decorated list
        Global.Pats = [line for _, line in deco] # copy it to an "undecorated" list
        del deco                            # and kill the decorated copy

        self.log.write('Printing labels...')
        GoodFile = csv.writer(open(Global.d_top + os.sep + 'GoodPats.csv', 'wb'), quoting=csv.QUOTE_ALL)
        GoodFile.writerow(['First Name', 'Middle Name', 'Last Name', 'Employer', 'Office Name', 'Office Phone', 'Office Phone Ext.', 'Office Fax', 'Home Phone', 'Social Security', 'Marital Status', 'Gender', 'Date of Birth', 'Address Line 1', 'Address Line 2', 'City', 'State', 'Zip Code', 'Comments'])
        if self.cbSepBad.IsChecked():
            BadFile = csv.writer(open(Global.d_top + os.sep + 'GoodPats.csv', 'wb'), quoting=csv.QUOTE_ALL)
            GoodFile.writerow(['First Name', 'Middle Name', 'Last Name', 'Employer', 'Office Name', 'Office Phone', 'Office Phone Ext.', 'Office Fax', 'Home Phone', 'Social Security', 'Marital Status', 'Gender', 'Date of Birth', 'Address Line 1', 'Address Line 2', 'City', 'State', 'Zip Code', 'Comments'])

        total_rec_in = 0

        pri_labels_out = 0
        bad_labels_out = 0
        startZip = self.scStartZip.GetValue()
        endZip = self.scEndZip.GetValue()
        phoneTest = set(['(',')','-'])  # set of characters to test if Address1 contains a phone number
        
        for pat in Global.Pats:
            
            total_rec_in +=1
            zipChk = int(pat.Zip[:5])
            if 1 in [c in pat.Address1 for c in phoneTest]:
                if self.cbDropPh.IsChecked():
                    pat.Address1 = ''

            if self.cbIgnZip.IsChecked() or (startZip <= zipChk <= endZip): # 
                if not (pat.Zip[5:] == ''):
                    pat.Zip = pat.Zip[:5] + '-' + pat.Zip[5:]
                if ((zipChk==0) or (99950 < zipChk <= 99999) or (pat.LastName[0] in ['$','~','z','*'])) and self.cbSepBad.IsChecked():
                        BadFile.writerow([pat.FirstName, pat.MI, pat.LastName, pat.EmpName, pat.EmpContact, pat.EmpPhone2, pat.EmpPhone2Ext, pat.EmpPhone, pat.HomePhone, pat.SSN, pat.MaritalStatus, pat.Sex, pat.Birthdate, pat.Address1, pat.Street, pat.City, pat.State, pat.Zip, pat.Message1 + pat.Message2])
                else:
                    #if (pat.ChartNumber in criteria):
                    GoodFile.writerow([pat.FirstName, pat.MI, pat.LastName, pat.EmpName, pat.EmpContact, pat.EmpPhone2, pat.EmpPhone2Ext, pat.EmpPhone, pat.HomePhone, pat.SSN, pat.MaritalStatus, pat.Sex, pat.Birthdate, pat.Address1, pat.Street, pat.City, pat.State, pat.Zip, pat.Message1 + pat.Message2])

        #=======================================================================================================================================
        #   and... loop!

        
        self.log.write('Done!')

    def loadDirect(self):
        self.log.write(str(Global.cfgFile.directDat[0]))
        Global.offices      = parseDirectDat(uri.UriToOsPath(str(Global.cfgFile.directDat[0])))
        Global.DocList      = []
        Global.Svc          = {}
        Global.Pats         = []
        
    def loadDocList(self):
        header = ('Office', 'ID', 'Name')
        Global.DocList.append(header)
        for num, off in Global.offices.iteritems():
            Global.Svc[off.Num] = {}
            for doc in RecordGenerator(off, "Doctor"):
                line = (off.Num, doc.ID, doc.Name)
                Global.Svc[off.Num][doc.ID] = {}
                Global.DocList.append(line)
        
    def loadLatestSvc(self):
        self.log.write("Loading service dates")
        try:
            with open(os.getcwd() + os.sep + 'svcDates.pkl', 'rb') as svcFile:
                Global.Svc = pickle.load(svcFile)
        except:
            for num, off in Global.offices.iteritems():
                for trn in RecordGenerator(off, "Transaction"):
                    if (trn.Valid and (trn.KeyType=='C') and not (trn.ExtChg)):
                        try:
                            if trn.ChartNumber in Global.Svc[off.Num][trn.Doctor]:
                                Global.Svc[off.Num][trn.Doctor][trn.ChartNumber][0] = min(trn.Date, Global.Svc[off.Num][trn.Doctor][trn.ChartNumber][0])
                                Global.Svc[off.Num][trn.Doctor][trn.ChartNumber][1] = max(trn.Date, Global.Svc[off.Num][trn.Doctor][trn.ChartNumber][1])
                            else:
                                Global.Svc[off.Num][trn.Doctor][trn.ChartNumber] = [trn.Date, trn.Date] 
                        except KeyError:
                            continue
            with open(os.getcwd() + os.sep + 'svcDates.pkl', 'wb') as svcFile:
                pickle.dump(Global.Svc, svcFile)
        Global.SvcsLoaded = True
        #self.log.write(str(Global.Svc))
        
class MyApp(wx.App):
    def OnInit(self):
        frame = Selector(None, -1, "Patient Export to CSV by Birthday")
        frame.Show()
        return True

#===============================================================================================
#      Where it all begins...
#===============================================================================================
def main(argv=None):
    if argv is None:
        argv = sys.argv
    Global.cfgFile.Load()
    Global.d_top = shell.SHGetSpecialFolderPath(0, 0x0010)
    Global.SvcsLoaded = False

    app = MyApp(0)
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()

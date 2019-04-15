from __future__ import with_statement
from time import strftime
import wx, sys, os, wx.lib.inspection
import  wx.lib.scrolledpanel as scrolled
from configobj import ConfigObj
from validate import Validator

#import Ft.Lib.Uri as uri
import urllib
#===These are mine: =====
from fsrStuff.Labels import *
#from fsrStuff.ConfigFile import *
from fsrStuff.SortCheck import *
from fsrStuff.umFuncs import *
from win32com.shell import shell
try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO

class Global(object):
    """Generic container for shared variables."""
    cfgFileName = os.getcwd() + os.sep + 'npi_upd.ini'
    tmpStr = """
    directDat = string(default="direct.dat")
    npiXMLFile = string(default="npiMap.XML")
    """
    cfgSpec = StringIO.StringIO(tmpStr)
    cfgFile = ConfigObj(cfgFileName,
                configspec=cfgSpec, raise_errors=True, write_empty_values = True,
                create_empty=True, indent_type='    ', list_values = True)
    vtor = Validator()

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
    def __init__(self, parent, id, title, size=(750,250)):
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
        self.loadInsurance()
        #============================================================

        tipString = '''We'll print labels for patients with charges between the Start Date and the End Date.
        To get all charges UP TO a certain date, leave the Start Date un-checked.
        To get all charges SINCE a certain date, leave the End Date un-checked.
        To get all charges, EVER, leave both dates un-checked.'''
        self.dpcStart = wx.DatePickerCtrl(leftPanel, size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
        self.dpcStart.SetToolTipString(tipString)
        self.dpcEnd   = wx.DatePickerCtrl(leftPanel, size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
        self.dpcEnd.SetToolTipString(tipString)

        self.list = SortedCheckList(rightPanel, Global.Ins)
        self.list.SetToolTipString("Select insurance companies")
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        offGrid = wx.GridSizer(4,3,3,3)
        self.offChk = {}
        for num, off in Global.offices.iteritems():
            self.offChk[num] = wx.CheckBox(leftPanel, -1, num, style=wx.ALIGN_LEFT)
            self.offChk[num].SetValue(True)
            self.offChk[num].Enable(True)
            self.offChk[num].Show(True)
            offGrid.Add(self.offChk[num])
        btnSelect   = wx.Button(leftPanel, -1, 'Select All', size=(120, -1))
        btnDeSel    = wx.Button(leftPanel, -1, 'Deselect All', size=(120, -1))
        btnLabels   = wx.Button(leftPanel, -1, 'Print Labels', size=(120, -1))

        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=btnSelect.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=btnDeSel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnBtnLabels, id=btnLabels.GetId())

        self.cbIgnIns = wx.CheckBox(leftPanel, -1, "Ignore Insurance?", style=wx.ALIGN_LEFT)
        self.cbDropPh = wx.CheckBox(leftPanel, -1, "Skip Add.#1 if phone?", style=wx.ALIGN_LEFT)
        self.cbSepBad = wx.CheckBox(leftPanel, -1, "Separate 'bad' labels?", style=wx.ALIGN_LEFT)
        self.cbIgnZip = wx.CheckBox(leftPanel, -1, "All Zip Codes?", style=wx.ALIGN_LEFT)
        self.scStartZip = wx.SpinCtrl(leftPanel, -1, "Starting Zip", (30, 50), style=wx.ALIGN_LEFT)
        self.scStartZip.SetRange(0,99999)
        self.scStartZip.SetValue(0)
        self.scEndZip = wx.SpinCtrl(leftPanel, -1, "Ending Zip", (30, 50), style=wx.ALIGN_LEFT)
        self.scEndZip.SetRange(0,99999)
        self.scEndZip.SetValue(99999)

        vbox2.Add(wx.StaticText(leftPanel, -1, "Offices:"))
        vbox2.Add(offGrid)
        vbox2.Add(btnSelect, 0, wx.TOP, 5)
        vbox2.Add(btnDeSel)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(wx.StaticText(leftPanel, -1, "Dates of service:"))
        vbox2.Add(wx.StaticText(leftPanel, -1, "  Start date:"))
        vbox2.Add(self.dpcStart)
        vbox2.Add(wx.StaticText(leftPanel, -1, "  End date:"))
        vbox2.Add(self.dpcEnd)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(self.cbIgnIns)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(self.cbDropPh)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(self.cbSepBad)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(self.cbIgnZip)
        vbox2.Add(self.scStartZip)
        vbox2.Add(self.scEndZip)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(btnLabels)
        vbox2.Add((0,0),1)   # empty space to keep second group off the floor

        leftPanel.SetSizer(vbox2)

        vbox.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))

        rightPanel.SetSizer(vbox)

        hbox.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND)
        hbox.Add((3, -1))

        panel.SetSizer(hbox)

        self.Centre()
        self.Show(True)

    def OnSelectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i)

    def OnDeselectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i, False)

    def OnBtnLabels(self, event):
        self.log.write('Building list of selected insurance companies...')
        criteria = []
        Global.Pats = []
        doChkDates = False
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
            if not dateStart.IsValid(): dateStart = wx.DateTimeFromDMY(1,1,1)
            if not dateEnd.IsValid(): dateEnd = wx.DateTimeFromDMY(30,12,9999)
            if dateEnd.IsEarlierThan(dateStart):
                dateStart = self.dpcStart.SetValue(dateEnd)
            dateStart = wx.DateTime.Format(dateStart, '%Y%m%d')
            dateEnd = wx.DateTime.Format(dateEnd, '%Y%m%d')
            self.log.write("Start date: " + dateStart + " End date: " + dateEnd)
        else:
            self.log.write("No date was selected - no need to check service dates")
        num = self.list.GetItemCount()
        for i in range(num):
            if self.list.IsChecked(i):
                criteria.append(self.list.GetItemText(i))
        self.log.write('Loading patients...')
        for num, off in Global.offices.iteritems():
            for obj in RecordGenerator(off, "Patient"):
                if self.cbIgnIns.IsChecked():
                    if doChkDates:
                        if ((obj.ChartNumber in Global.Svc) and (Global.Svc[obj.ChartNumber][0] >= dateStart) and (Global.Svc[obj.ChartNumber][1] <= dateEnd)):
                            Global.Pats.append(obj)
                    else:
                        Global.Pats.append(obj)
                else:
                    if ((obj.PriInsCompany in criteria) or (obj.SecInsCompany in criteria) or (obj.TerInsCompany in criteria)):
                        if doChkDates:
                            if ((obj.ChartNumber in Global.Svc) and (Global.Svc[obj.ChartNumber][0] >= dateStart) and (Global.Svc[obj.ChartNumber][1] <= dateEnd)):
                                Global.Pats.append(obj)
                        else:
                            Global.Pats.append(obj)
        self.log.write('Sorting patients...')
        deco = [ (pat.LastName, pat) for i, pat in enumerate(Global.Pats) ] # create a "decorated" list with the key we want to sort by
        del Global.Pats                     # kill the original list - free up memory

        deco.sort()                         # sort the decorated list
        Global.Pats = [line for _, line in deco] # copy it to an "undecorated" list
        del deco                            # and kill the decorated copy

        self.log.write('Printing labels...')
        if self.cbIgnIns.IsChecked():
            PriFile = Avery5160(Global.d_top + os.sep + 'Good.pdf')
        else:
            PriFile = Avery5160(Global.d_top + os.sep + 'PriIns.pdf')
            SecFile = Avery5160(Global.d_top + os.sep + 'SecIns.pdf')
            TerFile = Avery5160(Global.d_top + os.sep + 'TerIns.pdf')
        if self.cbSepBad.IsChecked():
            BadFile = Avery5160(Global.d_top + os.sep + 'Bad.pdf')
        total_rec_in = 0

        pri_labels_out = 0
        sec_labels_out = 0
        ter_labels_out = 0
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
                        BadFile.Add(pat)
                else:
                    if self.cbIgnIns.IsChecked():
                        PriFile.Add(pat)
                    else:
                        if (pat.PriInsCompany in criteria):
                            PriFile.Add(pat)
                        elif (pat.SecInsCompany in criteria):
                            SecFile.Add(pat)
                        elif (pat.TerInsCompany in criteria):
                            TerFile.Add(pat)

        #=======================================================================================================================================
        #   and... loop!

        PriFile.Print()
        if not self.cbIgnIns.IsChecked():
            SecFile.Print()
            TerFile.Print()
        if self.cbSepBad.IsChecked():
            BadFile.Print()

        self.log.write('Done!')

    def loadDirect(self):
        self.log.write(str(Global.cfgFile["directDat"]))
        Global.offices      = parseDirectDat(urllib.url2pathname(str(Global.cfgFile["directDat"])))
        Global.Ins          = []
        Global.Svc          = {}
        Global.Pats         = []

    def loadInsurance(self):
        header = ('Code', 'Name')
        Global.Ins.append(header)
        for num, off in Global.offices.iteritems():
            for obj in RecordGenerator(off, "Insurance"):
                line = (obj.ID, obj.Name)
                Global.Ins.append(line)


    def loadLatestSvc(self):
        for num, off in Global.offices.iteritems():
            for obj in RecordGenerator(off, "Transaction"):
                if ((obj.KeyType=='C') and not (obj.ExtChg)):
                    if obj.ChartNumber in Global.Svc:
                        Global.Svc[obj.ChartNumber][0] = min(obj.Date, Global.Svc[obj.ChartNumber][0])
                        Global.Svc[obj.ChartNumber][1] = max(obj.Date, Global.Svc[obj.ChartNumber][1])
                    else:
                        Global.Svc[obj.ChartNumber] = [obj.Date, obj.Date]
        Global.SvcsLoaded = True

class MyApp(wx.App):
    def OnInit(self):
        frame = Selector(None, -1, "Patient Labels by Insurance", size=(750,250))
        frame.Show()
        return True

#===============================================================================================
#      Where it all begins...
#===============================================================================================
def main(argv=None):
    if argv is None:
        argv = sys.argv
    test = Global.cfgFile.validate(Global.vtor, copy=True)
    Global.d_top = shell.SHGetSpecialFolderPath(0, 0x0010)
    Global.SvcsLoaded = False

    app = MyApp(0)
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()

from __future__ import with_statement
from time import strftime
import wx, sys, os
import  wx.lib.scrolledpanel as scrolled
import Ft.Lib.Uri as uri
#===These are mine: =====
from fsrStuff.Labels import *
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
    pass

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
        #============================================================

        tipString = '''We'll print labels for patients first entered between the Start Date and the End Date. 
        To get all patients UP TO a certain date, leave the Start Date un-checked.
        To get all patients SINCE a certain date, leave the End Date un-checked.
        To get all patients, EVER, leave both dates un-checked.'''
        self.dpcStart = wx.DatePickerCtrl(leftPanel, size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
        self.dpcStart.SetToolTipString(tipString)
        self.dpcEnd   = wx.DatePickerCtrl(leftPanel, size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
        self.dpcEnd.SetToolTipString(tipString)

        #self.list = SortedCheckList(rightPanel, Global.Ins)
        #self.list.SetToolTipString("Select insurance companies")
        vbox2 = wx.BoxSizer(wx.VERTICAL)

        #btnSelect   = wx.Button(leftPanel, -1, 'Select All', size=(100, -1))
        #btnDeSel    = wx.Button(leftPanel, -1, 'Deselect All', size=(100, -1))
        btnLabels   = wx.Button(leftPanel, -1, 'Print Labels', size=(100, -1))


        #self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=btnSelect.GetId())
        #self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=btnDeSel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnBtnLabels, id=btnLabels.GetId())

        #vbox2.Add(btnSelect, 0, wx.TOP, 5)
        #vbox2.Add(btnDeSel)
        vbox2.Add((0,0),1)   # empty space to separate groups of buttons
        vbox2.Add(wx.StaticText(leftPanel, -1, "Start date:"))
        vbox2.Add(self.dpcStart)
        vbox2.Add(wx.StaticText(leftPanel, -1, "End date:"))
        vbox2.Add(self.dpcEnd)  
        vbox2.Add((0,0),1)   # empty space to separate groups of buttons
        vbox2.Add(btnLabels)
        vbox2.Add((0,0),1)   # empty space to keep second group off the floor

        leftPanel.SetSizer(vbox2)

        #vbox.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
        #vbox.Add((-1, 10))

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
            if not dateStart.IsValid(): dateStart = wx.DateTimeFromDMY(1,1,1)
            if not dateEnd.IsValid(): dateEnd = wx.DateTimeFromDMY(30,12,9999)
            if dateEnd.IsEarlierThan(dateStart):
                dateStart = self.dpcStart.SetValue(dateEnd)
            dateStart = wx.DateTime.Format(dateStart, '%Y%m%d')
            dateEnd = wx.DateTime.Format(dateEnd, '%Y%m%d')
            self.log.write("Start date: " + dateStart + " End date: " + dateEnd)
        else:
            self.log.write("No date was selected - no need to check service dates")
        """
        num = self.list.GetItemCount()
        for i in range(num):
            if self.list.IsChecked(i):
                criteria.append(self.list.GetItemText(i))
        """
        self.log.write('Loading patients...')
        obj = Patient()
        recLen = obj.RecordLength
        for offNum, offPath in Global.offices.iteritems():
            if (offPath.Ref == ''): 
                offPath.Ref = offPath.Default
            with open(offPath.Ref + obj.TLA + '.dat','rb') as inFile:
                inRec = inFile.read(recLen)                 # burn the header record 
                inRec = inFile.read(recLen)        
                while not (len(inRec) < recLen):
                    obj = Patient(inRec)
                    if doChkDates:
                        if (obj.Valid and 
                        (obj.EntryDate >= dateStart) and (obj.EntryDate <= dateEnd)):
                            Global.Pats.append(obj)
                    else:
                        if obj.Valid:
                            Global.Pats.append(obj)
                    inRec = inFile.read(recLen)
        self.log.write('Sorting patients...')
        deco = [ (pat.LastName, pat) for i, pat in enumerate(Global.Pats) ] # create a "decorated" list with the key we want to sort by
        del Global.Pats                     # kill the original list - free up memory

        deco.sort()                         # sort the decorated list
        Global.Pats = [line for _, line in deco] # copy it to an "undecorated" list
        del deco                            # and kill the decorated copy
        
        self.log.write('Printing labels...')
        
        PriFile = Avery5160(Global.d_top + os.sep + 'Patients.pdf')
        BadFile = Avery5160(Global.d_top + os.sep + 'Bad.pdf')
        total_rec_in = 0

        pri_labels_out = 0
        bad_labels_out = 0

        for pat in Global.Pats:
            
            total_rec_in +=1
            outstr = pat.FirstName + ' '
            if (len(pat.MI)> 1): outstr = outstr + pat.MI + ' '
            outstr = outstr + pat.LastName + '\n'
            if (len(pat.Address1)> 1): outstr = pat.Address1 + '\n'
            outstr = outstr + pat.Street + '\n' + pat.City + ', ' + pat.State + ' ' + pat.Zip
            if ((pat.Zip[:5]=='99999') or (pat.Zip[:5]=='99998') or (pat.Zip[:5]=='00000') or (pat.LastName[0] in ['$','~','z'])):
                BadFile.Add(pat)
            else:
                PriFile.Add(pat)

        #=======================================================================================================================================
        #   and... loop!

        PriFile.Print()
        BadFile.Print()
        
        self.log.write('Done!')

    def loadDirect(self):
        Global.offices      = parseDirectDat(uri.UriToOsPath(str(Global.cfgFile.directDat[0])))
        Global.Ins          = []
        Global.Svc          = {}
        Global.Pats         = []
        

class MyApp(wx.App):
    def OnInit(self):
        frame = Selector(None, -1, "Patient Labels by Entry Date", size=(750,250))
        frame.Show()
        return True

#===============================================================================================
#      Where it all begins...
#===============================================================================================
def main(argv=None):
    if argv is None:
        argv = sys.argv
    Global.cfgFileName              = os.getcwd() + os.sep + 'fsr_labels.xml'
    Global.cfgFile   = ConfigFile(Global.cfgFileName, "directDat")
    Global.cfgFile.Load()
    Global.d_top = shell.SHGetSpecialFolderPath(0, 0x0010)
    Global.SvcsLoaded = False

    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    main()

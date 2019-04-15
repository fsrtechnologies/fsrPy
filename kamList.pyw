from __future__ import with_statement
from time import strftime
import wx, sys, copy, os, os.path, wx.lib.inspection, decimal
import  wx.lib.scrolledpanel as scrolled
import wx.lib.delayedresult as delayedresult
from datetime import date
from configobj import ConfigObj
from validate import Validator
from operator import attrgetter
#from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from fsrStuff.X12.GenPDFSet import GenericPDFSettings

import urllib
import traceback
#===These are mine: =====
from fsrStuff.SortCheck import SortedCheckList
from fsrStuff.umFuncs import *
#from win32com.shell import shell
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
    def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title, size)
        self.CreateStatusBar(1)
        self.log = Log()
        self.SetMinSize(size)
        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel, -1)
        rightPanel = wx.Panel(panel, -1)

        #============================================================
        # Gettin' the data, nom nom nom
        self.loadInsurance()
        #============================================================
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        tipString = '''We'll print patients with charges between the Start Date and the End Date.
        To get all charges UP TO a certain date, leave the Start Date un-checked.
        To get all charges SINCE a certain date, leave the End Date un-checked.
        To get all charges, EVER, leave both dates un-checked.'''
        self.dpcStart = wx.DatePickerCtrl(leftPanel, size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
        self.dpcStart.SetToolTipString(tipString)
        self.dpcEnd   = wx.DatePickerCtrl(leftPanel, size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
        self.dpcEnd.SetToolTipString(tipString)

        self.chkList = SortedCheckList(rightPanel, Global.Ins)
        self.chkList.SetToolTipString("Select insurance companies")
        self.chkList.SetMinSize(wx.Size(250, 400))
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        self.loadDoctors()
        tmpHeight = (len(self.docDict) / 3) + 1
        docGrid = wx.GridSizer(tmpHeight,3,3,3)
        self.docChk = {}
        for num, doc in self.docDict.iteritems():
            self.docChk[num] = wx.CheckBox(leftPanel, -1, num, style=wx.ALIGN_LEFT)
            self.docChk[num].SetValue(True)
            self.docChk[num].Enable(True)
            self.docChk[num].Show(True)
            docGrid.Add(self.docChk[num])
        btnSelect   = wx.Button(leftPanel, -1, 'Select All', size=(120, -1))
        btnDeSel    = wx.Button(leftPanel, -1, 'Deselect All', size=(120, -1))
        self.btnPrint    = wx.Button(leftPanel, -1, 'Print Report', size=(120, -1))
        self.btnAbort    = wx.Button(leftPanel, -1, 'Abort', size=(120, -1))
        self.chkSortByIns = wx.CheckBox(leftPanel, -1, "Sort by insurance?", style=wx.ALIGN_LEFT)
        self.chkSortByIns.SetValue(True)
        self.chkSortByIns.Enable(True)
        self.chkSortByIns.Show(True)

        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=btnSelect.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=btnDeSel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnBtnPrint, id=self.btnPrint.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnBtnAbort, id=self.btnAbort.GetId())
        self.abortEvent = delayedresult.AbortEvent()


        vbox2.Add(wx.StaticText(leftPanel, -1, "Doctors:"))
        vbox2.Add(docGrid)
        vbox2.Add(btnSelect, 0, wx.TOP, 5)
        vbox2.Add(btnDeSel)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(wx.StaticText(leftPanel, -1, "Dates of service:"))
        vbox2.Add(wx.StaticText(leftPanel, -1, "  Start date:"))
        vbox2.Add(self.dpcStart)
        vbox2.Add(wx.StaticText(leftPanel, -1, "  End date:"))
        vbox2.Add(self.dpcEnd)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(self.chkSortByIns)
        vbox2.Add((0,0),1)   # empty space to separate items
        vbox2.Add(self.btnPrint)
        vbox2.Add(self.btnAbort)
        vbox2.Add((0,0),1)   # empty space to keep second group off the floor
        vbox.Layout()

        leftPanel.SetSizer(vbox2)

        vbox.Add(self.chkList, 1, wx.EXPAND | wx.TOP, 3)
        #vbox.Add((-1, 10))

        rightPanel.SetSizer(vbox)

        hbox.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND)
        #hbox.Add((3, -1))

        self.btnPrint.Enable(True)
        self.btnAbort.Enable(False)

        panel.SetSizer(hbox)
        panel.Layout()

        self.Centre()
        self.Layout()
        self.Show(True)


    def loadInsurance(self):
        self.log.write("Creating list of insurance companies")
        header = ('Code', 'Name')
        Global.Ins.append(header)
        for num, off in Global.offices.iteritems():
            for obj in RecordGenerator(off, "Insurance"):
                line = (obj.ID, obj.Name)
                Global.Ins.append(line)
        self.log.write("Insurance list loaded.")


    def OnSelectAll(self, event):
        for i in range(self.chkList.GetItemCount()):
            self.chkList.CheckItem(i)

    def OnDeselectAll(self, event):
        for i in range(self.chkList.GetItemCount()):
            self.chkList.CheckItem(i, False)

    def OnBtnAbort(self, event):
        """Abort the result computation."""
        self.log.write( "Aborting job %s" % self.jobID )
        self.btnPrint.Enable(True)
        self.btnAbort.Enable(False)
        self.abortEvent.set()

    def OnBtnPrint(self, event):
        self.btnPrint.Enable(False)
        self.btnAbort.Enable(True)
        self.abortEvent.clear()
        self.jobID = 0

        #=========================Set up date range===============
        doChkDates = False
        self.dateStart = self.dpcStart.GetValue()
        self.dateEnd = self.dpcEnd.GetValue()

        if not self.dateStart.IsValid(): self.dateStart = wx.DateTimeFromDMY(1,1,1)
        if not self.dateEnd.IsValid(): self.dateEnd = wx.DateTimeFromDMY(30,12,9999)
        if self.dateEnd.IsEarlierThan(self.dateStart):
            self.dateStart = self.dpcStart.SetValue(self.dateEnd)
        self.dateStart = wx.DateTime.Format(self.dateStart, '%Y%m%d')
        self.dateEnd = wx.DateTime.Format(self.dateEnd, '%Y%m%d')
        self.log.write("Start date: " + self.dateStart + " End date: " + self.dateEnd)
        #==========================================================

        #===================Use only checked doctors===============
        self.trimDocs = {num: doc for num, doc in self.docDict.items() if self.docChk[num].IsChecked()}
        #==========================================================


        self.log.write('Building dict of selected insurance companies...')
        self.insDict = {}

        for item in range(self.chkList.GetItemCount()): # off-by-one issue here...
            if self.chkList.IsChecked(item):
                self.chkList
                tmpNum = self.chkList.GetItemData(item) -1
                tmpKey = Global.Ins[tmpNum][0]
                tmpDat = Global.Ins[tmpNum][1]
                self.insDict[tmpKey] = tmpDat
        print(self.insDict)

        #===Start chain of delayed-result processes so user can cancel if necessary
        self.log.write('Loading procedure codes...')
        self.jobID = 1
        delayedresult.startWorker(self.jobSwitcher, self.loadProcedures,
                                  wargs=(self.jobID,self.abortEvent), jobID=self.jobID)

    def jobSwitcher(self, delayedResult):
        jobID = delayedResult.getJobID()
        result = 0
        try:
            result = delayedResult.get()
        except Exception, exc:
            print( "Result for job %s raised exception: %s" % (jobID, exc) )
            return

        """
        if result == 1:
            self.log.write('Loading doctors...')
            self.jobID = 2
            delayedresult.startWorker(self.jobSwitcher, self.loadDoctors,
                                      wargs=(self.jobID,self.abortEvent), jobID=self.jobID)
        """
        if result == 1:
            self.log.write('Loading patients...')
            self.jobID = 2
            delayedresult.startWorker(self.jobSwitcher, self.loadPatients,
                                      wargs=(self.jobID,self.abortEvent), jobID=self.jobID)
        if result == 2:
            self.log.write('Loading transactions (this is the slow part)...')
            self.jobID = 3
            delayedresult.startWorker(self.jobSwitcher, self.loadTransactions,
                                      wargs=(self.jobID,self.abortEvent), jobID=self.jobID)

        if result == 3:
            self.log.write('Writing report...')
            self.jobID = 4
            delayedresult.startWorker(self.jobSwitcher, self.toPDF,
                                      wargs=(self.jobID,self.abortEvent), jobID=self.jobID)
        if result == 4:
            self.log.write('All done.')
            self.btnPrint.Enable(True)
            self.btnAbort.Enable(False)
            self.abortEvent.clear()
            return True

    def loadProcedures(self, jobID, abortEvent):
        tmpCount = 0
        self.procDict = {}
        for num, off in Global.offices.iteritems():
            for proc in RecordGenerator(off, "Procedure"):
                if abortEvent(): return False
                self.procDict[proc.InHouseCode] = [proc.CPTCode, proc.Description1]
                tmpCount +=1
        return jobID
        self.log.write('Finished transactions')


    def loadDoctors(self):
        class rptDoctor(object):
            def __init__(self, ID='', Name=''):
                self.ID = ID
                self.Name = Name
                self.Patients = {}
                self.TranNum = 0
                self.TranTotal = 0
        self.docDict = {}
        for num, off in Global.offices.iteritems():
            for doc in RecordGenerator(off, "Doctor"):
                self.docDict[doc.ID] = rptDoctor(doc.ID, doc.Name)

    def loadPatients(self, jobID, abortEvent):
        class rptPatient(object):
            def __init__(self, ChartNumber='', Name='', InsCode='', InsName=''):
                self.ChartNumber = ChartNumber
                self.Name = Name
                self.InsCode = InsCode
                self.InsName = InsName
                self.Transactions = []
        self.patDict = {}
        for num, off in Global.offices.iteritems():
            for pat in RecordGenerator(off, "Patient"):
                if abortEvent(): return False
                if (pat.PriInsCompany in self.insDict):
                    self.patDict[pat.ChartNumber] = rptPatient(pat.ChartNumber,
                        "{0}, {1} {2}".format(pat.LastName, pat.FirstName, pat.MI),
                        pat.PriInsCompany,
                        self.insDict[pat.PriInsCompany])
        return jobID


    def loadTransactions(self, jobID, abortEvent):
        self.trnList = []
        for num, off in Global.offices.iteritems():
            for trn in RecordGenerator(off, "Transaction"):
                if abortEvent(): return False
                if trn.KeyType == 'C' and not trn.ExtChg:
                    if (trn.ChartNumber in self.patDict) and (trn.Doctor in self.trimDocs) and (self.dateStart <= trn.Date <= self.dateEnd):
                        self.patDict[trn.ChartNumber].Transactions.append([trn.Date, trn.Doctor, trn.ProcCode, trn.Charge])
        return jobID

    def toPDF(self, jobID, abortEvent):
        pdfSet = PDFSettings()
        pdfSet.addStyles()
        cW = pdfSet.cW
        lH = pdfSet.lineHeight

        fileNameBase = os.path.join(os.path.expanduser("~"), "Desktop", "KamList")
        fileName = fileNameBase + '.pdf'
        doc = SimpleDocTemplate(fileName, pagesize=letter,
                                leftMargin=pdfSet.marginSize, rightMargin=pdfSet.marginSize,
                                topMargin=pdfSet.marginSize + 5 * pdfSet.lineHeight,
                                bottomMargin=pdfSet.bottomMargin)
        doc.leftPadding = 0

        stylesheet=getSampleStyleSheet()
        codeStyle = copy.copy(stylesheet['Normal'])
        codeStyle.fontName = pdfSet.regFont
        codeStyle.fontSize = pdfSet.fontSize
        codeStyle.borderPadding = 0
        codeStyle.leading = 8

        self.log.write('Starting to create PDF')
        self.trimPats = {pat:self.patDict[pat] for pat in self.patDict if self.patDict[pat].Transactions}
        rpt = sorted(self.trimPats.values(), key=attrgetter('Name'))  #Sort by patient name regardless
        if self.chkSortByIns:
            rpt.sort(key=attrgetter('InsCode')) #Sort by insurance - patient sort will remain stable
        grandTotal = 0
        insTotal = 0
        Story = []
        curIns = ""

        for pat in rpt:
            patient = []

            if self.chkSortByIns:  # Break out a header line for insurance
                if pat.InsCode != curIns:
                    if insTotal > 0:
                        btmLine =[(None, None, None, None, "Total for {0}:".format(curIns), None, None, insTotal)]
                        tbl = Table(btmLine, colWidths=pdfSet.clmLineWidths, rowHeights=None, style=pdfSet.styles['clmLine'])
                        Story.append(tbl)
                        Story.append(Spacer(2,lH))
                        insTotal = 0
                    insLine =[(None, None, pat.InsCode, pat.InsName, None, None, None, None)]
                    tbl = Table(insLine, colWidths=pdfSet.clmLineWidths, rowHeights=None, style=pdfSet.styles['clmLine'])
                    Story.append(tbl)
                    Story.append(Spacer(1,lH))
                    curIns = pat.InsCode
            tmpLine = list(8*[None])
            tmpLine[0] = pat.Name
            tmpLine[1] = pat.ChartNumber
            if not self.chkSortByIns:  # Leave the insurance part blank for higher contrast
                tmpLine[2] = pat.InsCode
                tmpLine[3] = pat.InsName
            for trn in sorted(pat.Transactions):
                if trn[1] != '':
                    try: # This whole section SHOULD get bypassed in case of corrupt multi-million-dollar transactions...
                        grandTotal += decimal.Decimal(trn[3])
                        insTotal += decimal.Decimal(trn[3])
                        self.trimDocs[trn[1]].TranTotal += decimal.Decimal(trn[3]) #trn[1] is the Doctor
                        self.trimDocs[trn[1]].TranNum += 1
                        self.trimDocs[trn[1]].Patients[pat.ChartNumber] = pat.ChartNumber  # Can only add to dictionary once, so this is a good count.
                        tmpLine[4] = "{0}/{1}/{2}".format(trn[0][4:6], trn[0][6:8], trn[0][:4])
                        tmpLine[5] = trn[1]
                        tmpLine[6] = trn[2]
                        tmpLine[7] = trn[3]
                        patient.append(tmpLine)
                    #except decimal.InvalidOperation:
                    except Exception, exc:
                        print(trn)
                        print(traceback.format_exc())
                        pass
                tmpLine = list(8*[None])
            tbl = Table(patient, colWidths=pdfSet.clmLineWidths, rowHeights=None, style=pdfSet.styles['clmLine'])
            Story.append(tbl)
            Story.append(Spacer(1,lH))

        if self.chkSortByIns:
                btmLine =[(None, None, None, None, "Total for {0}:".format(curIns), None, None, insTotal)]
                tbl = Table(btmLine, colWidths=pdfSet.clmLineWidths, rowHeights=None, style=pdfSet.styles['clmLine'])
                Story.append(tbl)
                Story.append(Spacer(2,lH))
                insTotal = 0

        for i, docObj in self.trimDocs.iteritems():
            if len(docObj.Patients) > 0:
                btmLine =[("{0}  {1}".format(docObj.ID, docObj.Name), None, "Patients: {0}".format(len(docObj.Patients)), None, "Procedures: {0}".format(docObj.TranNum), None, "Charges:", docObj.TranTotal)]
                tbl = Table(btmLine, colWidths=pdfSet.clmLineWidths, rowHeights=None, style=pdfSet.styles['clmLine'])
                Story.append(tbl)
        Story.append(Spacer(2,lH))
        btmLine =[(None, None, None, None, "Grand total:", None, None, grandTotal)]
        tbl = Table(btmLine, colWidths=pdfSet.clmLineWidths, rowHeights=None, style=pdfSet.styles['clmLine'])
        Story.append(tbl)
        attempt = 1

        while attempt > 0:  #avoid blowing up due to duplicate filename
            try:
                open(fileName, 'wb')
                doc.build(Story, onFirstPage=pdfSet.firstPage, onLaterPages=pdfSet.laterPages)
                attempt = 0
            except IOError:
                doc.filename = fileName = '%s(%s).pdf' % (fileNameBase, attempt)
                attempt += 1
        self.btnPrint.Enable(True)
        self.btnAbort.Enable(False)
        self.abortEvent.clear()
        os.startfile(fileName)
        return jobID


class PDFSettings(GenericPDFSettings):
    def addStyles(self):
        cW = self.cW
        self.columnHeader1 = "PATIENT NAME                  CHART          INS      INS NAME                       DATE           Doc       CPT          CHARGE"
        self.columnHeader2 = "---------------------------------------------------------------------------------------------------------------------------------"
        #                    Name                          Chart          InsCode  InsName                         Date           Doc       CPT          Charge
        #                    LEFT                          LEFT           LEFT     LEFT                            LEFT           LEFT      LEFT         DEC
        self.clmLineWidths    = [30*cW, 15*cW, 9*cW, 31*cW,  16*cW, 8*cW, 7*cW, 10*cW]

        self.styles['clmLine'].add('ALIGN', (7,0), (7,-1), 'DECIMAL')


    def firstPage(self, canvas, doc):
        frame = doc.pageTemplates[0].frames[0]
        frame.leftPadding=frame.rightPadding=frame.topPadding=frame.bottomPadding=0
        canvas.saveState()
        canvas.setFont(self.regFont, self.fontSize)
        tM, lM, rM, lH = self.topMargin, self.leftMargin, self.rightMargin, self.lineHeight

        canvas.drawString(lM, tM-3 * lH, date.today().strftime("%x"))
        canvas.drawCentredString(lM + (rM - lM)/2, tM-3 * lH, "Patient charges by CPT code")
        canvas.drawRightString(rM, tM-3 * lH, "Page %s" % (doc.page))
        canvas.drawString(lM+2, tM - 4 * lH, self.columnHeader1)
        canvas.drawString(lM+2, tM - 5 * lH, self.columnHeader2)
        canvas.restoreState()

    def laterPages(self, canvas, doc):
        canvas.saveState()
        canvas.setFont(self.regFont, self.fontSize)
        tM, lM, rM, lH = self.topMargin, self.leftMargin, self.rightMargin, self.lineHeight
        canvas.drawString(lM, tM-3 * lH, date.today().strftime("%x"))
        canvas.drawCentredString(lM + (rM - lM)/2, tM-3 * lH, "Patient charges by CPT code")
        canvas.drawRightString(rM, tM-3 * lH, "Page %s" % (doc.page))
        canvas.drawString(lM+2, tM - 4 * lH, self.columnHeader1)
        canvas.drawString(lM+2, tM - 5 * lH, self.columnHeader2)
        canvas.restoreState()



class MyApp(wx.App):
    def OnInit(self):
        frame = Selector(None, -1, "Patient/Procedure list by CPT", size=(450,450))
        frame.Show()
        return True

class SplashFrame(wx.Frame):
    def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, size=size, style=style)
        self.CreateStatusBar(1)
        self.log=Log()
        self.jobID = 0

        pnl = wx.Panel(self)
        gs = wx.GridSizer(3, 3, 2, 2)  # rows, cols, vgap, hgap
        self.loadDirect()
        self.offBtn = {}
        for num in sorted(Global.offices):
            self.offBtn[num] = wx.Button(pnl, -1, num, name=num)
            self.offBtn[num].Enable(True)
            self.offBtn[num].Show(True)
            self.Bind(wx.EVT_BUTTON, self.ChosenOffice, id=self.offBtn[num].GetId())
            gs.Add(self.offBtn[num])

        pnl.SetSizer(gs)
        pnl.Layout()

        self.Centre()
        self.Layout()
        self.Show(True)

    def loadDirect(self):
        self.log.write("Loading office data from: " + str(Global.cfgFile["directDat"]))
        Global.offices      = parseDirectDat(urllib.url2pathname(str(Global.cfgFile["directDat"])))
        Global.Ins          = []
        self.log.write("Loaded office data from: " + str(Global.cfgFile["directDat"]))

    def ChosenOffice(self, event):
        btn = event.GetEventObject().Name
        Global.offices = { num: off for num, off in Global.offices.items() if num == btn }
        Global.dataLoaded = True
        self.Close(True)

class SplashApp(wx.App):
    def OnInit(self):
        splash = SplashFrame(None, -1, "Patient charges by CPT code - office selection",wx.Size(450,200))
        splash.Show()
        return True



#===============================================================================================
#      Where it all begins...
#===============================================================================================
def main(argv=None):
    if argv is None:
        argv = sys.argv
    test = Global.cfgFile.validate(Global.vtor, copy=True)
    #Global.d_top = shell.SHGetSpecialFolderPath(0, 0x0010)
    Global.d_top = os.path.join(os.path.expanduser("~"),"Desktop")
    Global.SvcsLoaded = False

    Global.dataLoaded = False
    sploosh = SplashApp(0)
    sploosh.MainLoop()
    if not Global.dataLoaded: sys.exit()

    app = MyApp(0)
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()

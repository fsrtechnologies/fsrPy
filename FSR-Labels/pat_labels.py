import time
import struct
import calendar
from umFuncs import *
import wx
import sys
from wx.lib.mixins.listctrl import ColumnSorterMixin, CheckListCtrlMixin

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
width, height = letter  #keep for later

start_time = time.time()

office = '/ccmgotv/01dat/01'

leftMargin = 0.33*inch
topMargin = 0.75*inch
lblHeight = 1*inch                  # Avery 5160 labels are 1 inch tall by 2 5/8 inches wide, 3 up, 10 rows.
lblWidth = 2.625*inch
vertFudge = 0*inch                 # Unfortunately, they don't line up nominally...
horzFudge = 0.15*inch
lblHeight = lblHeight + vertFudge
lblWidth = lblWidth + horzFudge
labelpos = [(leftMargin,(height - topMargin - 0*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 0*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 0*lblHeight)),
            (leftMargin,(height - topMargin - 1*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 1*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 1*lblHeight)),
            (leftMargin,(height - topMargin - 2*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 2*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 2*lblHeight)),
            (leftMargin,(height - topMargin - 3*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 3*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 3*lblHeight)),
            (leftMargin,(height - topMargin - 4*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 4*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 4*lblHeight)),
            (leftMargin,(height - topMargin - 5*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 5*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 5*lblHeight)),
            (leftMargin,(height - topMargin - 6*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 6*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 6*lblHeight)),
            (leftMargin,(height - topMargin - 7*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 7*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 7*lblHeight)),
            (leftMargin,(height - topMargin - 8*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 8*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 8*lblHeight)),
	    (leftMargin,(height - topMargin - 9*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 9*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 9*lblHeight))]

fontFace = 'Helvetica'
#fontFace = 'Helvetica-Bold'
#fontFace = 'Helvetica-Oblique'
#fontFace = 'Courier'
#fontFace = 'Helvetica-Oblique'
#fontFace = 'Helvetica-Oblique'
#fontFace = 'Helvetica-Oblique'
fontSize = 9

#=============================================================================================
#   Load the patient file to a list and sort it by (whatever we define below)
#=============================================================================================
patlen = 1024
infile = open(office + 'pat.dat','r+b')
logfile = open(office + 'fix_app.log','w')

pats_orig = []

infile.read(patlen)                 # burn the header record 
inrec = infile.read(patlen)         # read the rest of the PAT file into the list
while not (len(inrec) < patlen):
    pats_orig.append(inrec)
    inrec = infile.read(patlen)
infile.close()

deco = [ (line[16:31], i, line) for i, line in enumerate(pats_orig) ] # create a "decorated" list with the key we want to sort by
del pats_orig                       # kill the original list - free up memory

deco.sort()                         # sort the decorated list
pats_sorted = [line for _, _, line in deco] # copy it to an "undecorated" list
del deco                            # and kill the decorated copy

logline = 'Sorted - %0.3f seconds so far. \n' % (time.time() - start_time)
logfile.write(logline)
print '...'

#=============================================================================================
#   Now that the list is sorted...
#=============================================================================================
goodfile = canvas.Canvas(office + 'gd_lbl.pdf', pagesize=letter)
bad_file = canvas.Canvas(office + 'badlbl.pdf', pagesize=letter)
total_rec_in = 0

good_labels_out = 0
bad_labels_out = 0

for patrec in pats_sorted:
    total_rec_in +=1
    if not patrec[5:6].isalnum() : continue  # dropping garbage records
    this = patfields(patrec)
    outstr = this['pat_first'] + ' '
    if (len(this['pat_mi'])> 1): outstr = outstr + this['pat_mi'] + ' '
    outstr = outstr + this['pat_last'] + '\n'
    if (len(this['pat_addr1'])> 1): outstr = this['pat_addr1'] + '\n'
    outstr = outstr + this['pat_str'] + '\n' + this['pat_city'] + ', ' + this['pat_st'] + ' ' + this['pat_zip']
    if ((this['pat_zip'][:5]=='99999') or (this['pat_zip'][:5]=='99998') or (this['pat_zip'][:5]=='00000')):
        if (bad_labels_out % 30 == 0):
            if (bad_labels_out > 0):bad_file.showPage()
            bad_file.setFont(fontFace, fontSize)
            bad_file.setStrokeColorRGB(255,255,255)
        textobject = bad_file.beginText()
        textobject.setTextOrigin(labelpos[bad_labels_out % 30][0],labelpos[bad_labels_out % 30][1])
        textobject.textLines(outstr)
        bad_file.drawText(textobject)
        del textobject
        bad_labels_out +=1
    else:
        if (good_labels_out % 30 == 0):
            if (good_labels_out > 0):goodfile.showPage()
            goodfile.setFont(fontFace, fontSize)
            goodfile.setStrokeColorRGB(255,255,255)
        textobject = goodfile.beginText()
        textobject.setTextOrigin(labelpos[good_labels_out % 30][0],labelpos[good_labels_out % 30][1])
        textobject.textLines(outstr)
        goodfile.drawText(textobject)
        del textobject
        good_labels_out +=1

#=======================================================================================================================================
#   and... loop!

goodfile.showPage()
goodfile.save()
bad_file.showPage()
bad_file.save()
logline = 'Read %u patient records \n  wrote: \n \t %u good labels \n \t %u bad labels \n Total time %0.3f seconds. \n' % (total_rec_in, good_labels_out, bad_labels_out, (time.time() - start_time) )
logfile.write(logline)
logfile.close()
print logline

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ColumnSorterMixin):
     def __init__(self, parent, inList):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ColumnSorterMixin.__init__(self, len(inList))
        self.itemDataMap = inList


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, size=size, style=style)
        self.CreateStatusBar(1)
        self.log=Log()
 
        Global.cfgFileName  = os.getcwd() + os.sep + 'fsr_label.xml'
        Global.cfgFile      = ConfigFile(Global.cfgFileName, "directDat","TopLeft", "BottomRight")
        Global.cfgFile.Load()

        if not (os.path.exists(str(Global.cfgFileName)) and os.path.exists(uri.UriToOsPath(str(Global.cfgFile.directDat))) and os.path.exists(uri.UriToOsPath(str(Global.cfgFile.npiXMLFile)))):
            Global.cfgDone = False
            app = ConfigApp(0)
            app.MainLoop()
            if (Global.cfgDone == 2):
                dlg = wx.MessageDialog(None, "I can't go on like this!  Try again, and next time tell me what I need to know!",
                                "Abort! Abort!", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                exit()
        
        pnl = wx.Panel(self)
        boxOuter = wx.BoxSizer(wx.VERTICAL)

        Global.printData = wx.PrintData()
        Global.printData.SetPaperId(wx.PAPER_LETTER)
        Global.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        Global.printData.SetOrientation(wx.PORTRAIT)
        Global.pageData = wx.PageSetupDialogData()
        Global.pageData.SetMarginTopLeft(uniToPoint(Global.cfgFile.TopLeft))
        Global.pageData.SetMarginBottomRight(uniToPoint(Global.cfgFile.BottomRight))
        
        boxInner1 = wx.BoxSizer(wx.HORIZONTAL)
        boxInner1.Add(wx.StaticText(pnl, -1, "Source file type and location:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.log.write("Source file: %s" % uri.UriToOsPath(str(Global.cfgFile.old1500File)))
        boxOuter.Add(boxInner1, 1, wx.ALIGN_CENTER | wx.ALIGN_TOP)

        boxInner2 = wx.BoxSizer(wx.HORIZONTAL)
        grid1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        self.group1_ctrls = []
        radio1 = wx.RadioButton( pnl, -1, " UCF ", style = wx.RB_GROUP)
        radio2 = wx.RadioButton( pnl, -1, " FI    " )

        self.fp1 = filebrowse.FileBrowseButtonWithHistory(pnl, -1, size=(350, -1), 
            initialValue=uri.UriToOsPath(str(Global.cfgFile.old1500File)), 
            labelText='', fileMask='*.*', fileMode=wx.OPEN, 
            dialogTitle='Select the file containing UCF claims', changeCallback=self.fp1Callback)
        tmpStr = str(Global.cfgFile.UCFHist)[2:-2]
        tmpStr.replace(chr(27), "")
        #print tmpStr.split()
        #self.fp1.SetHistory(Global.cfgFile.UCFHist)

        self.fp2 = wx.FilePickerCtrl(pnl, message = 'Select the form-image file - generally starts with FI', 
                                wildcard = "All files (*.*)|*.*", path = uri.UriToOsPath(str(Global.cfgFile.old1500File))) 
        self.group1_ctrls.append((radio1, self.fp1))
        self.group1_ctrls.append((radio2, self.fp2))

        for radio, text in self.group1_ctrls:
            grid1.Add( radio, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            grid1.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        boxInner2.Add( grid1, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
        boxOuter.Add(boxInner2, 1, wx.ALIGN_CENTER | wx.ALIGN_TOP)

        boxInner3 = wx.BoxSizer(wx.HORIZONTAL)
        IDs = [wx.ID_OK, wx.ID_PREFERENCES, wx.ID_CANCEL]
        for ID in IDs:
            b = wx.Button(pnl, ID)
            boxInner3.Add(b, 0, wx.ALL, 5)
            self.Bind(wx.EVT_BUTTON, self.OnClick, b)
        boxOuter.Add(boxInner3, 1, wx.ALIGN_CENTER | wx.ALIGN_TOP)
        pnl.SetSizer(boxOuter)

    def fp1Callback(self, evt):
        print evt
        if not hasattr(evt, 'GetEventObject'):
            #evt.Skip()
            return
        if hasattr(self, 'fp1'):
            value = evt.GetString()
            if not value:
                return
            history = self.fp1.GetHistory()
            if value not in history:
                history.append(value)
                self.fp1.SetHistory(history)
                self.fp1.GetHistoryControl().SetStringSelection(value)
            Global.cfgFile.old1500File      = unicode(uri.OsPathToUri(value))
            print history.join()
            Global.cfgFile.UCFHist          = unicode(history)
            Global.cfgFile.Save()
            self.log.write("Source file: %s" % str(uri.OsPathToUri(value)))


    def OnClick(self, event):
        btn = event.GetId() 
        if (btn == wx.ID_OK):
            if not (os.path.exists(uri.UriToOsPath(str(Global.cfgFile.old1500File)))):
                self.log.write("Select a valid source file!")
            else:
                if not (os.path.isfile(uri.UriToOsPath(str(Global.cfgFile.npiXMLFile)))):
                    dlg = wx.MessageDialog(None, '''Click Preferences and select the file you created when you ran the NPI Update program.\n (Probably "npiMap.XML")''',
                            "Can't open the NPI lookup file!", wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                else:
                    self.GetOnWithIt()
            self.Close(True)
            exit()
        if (btn == wx.ID_PREFERENCES): 
            self.win = ConfigFrame(self, -1, "FSR1500 - Configuration screen...",wx.Size(450,300))
            self.win.Show(True)
        if (btn == wx.ID_CANCEL):
            self.Close(True)
            exit()

    def ParseOld1500(self): 
        formLen         = int(str(Global.cfgFile.formLength))
        Global.lineCount = 0
        Global.claimCount = -1
        Global.Claims   = {}
        Global.TotalBox = ''
        inFile          = uri.UriToOsPath(str(Global.cfgFile.old1500File))
        for Global.inLine in open(inFile,'r').readlines():
            claimLine   = Global.lineCount % formLen
            if (claimLine == 0): 
                Global.claimCount +=1
                Global.Claims[Global.claimCount] = Form1500()
            lineParse.get(claimLine, blankLine)()
            Global.lineCount +=1

    def GetOnWithIt(self, target=None):

#----------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "FSR-1500",wx.Size(500,250))
        frame.Show()
        return True

#===============================================================================================
#      Where it all begins...
#===============================================================================================
def main(argv=None):
    if argv is None:
        argv = sys.argv
    Global.cfgFileName              = os.getcwd() + os.sep + 'fsr_1500.xml'
    Global.dataLoaded               = False
    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    main()
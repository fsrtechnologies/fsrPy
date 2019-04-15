from __future__ import with_statement
import wx, sys, os
import Ft.Lib.Uri as uri
#===These are mine: =====
from ConfigFile import *
from SortList import *
from umFuncs import *

class Global:
    """Generic container for shared variables."""
    pass

class Log:
    """Log output is redirected to the status bar of the containing frame."""
    def WriteText(self,text_string):
        self.write(text_string)
    def write(self,text_string):
        wx.GetApp().GetTopWindow().SetStatusText(text_string)


class Selector(wx.Notebook):
#----------------------------------------------------------------------
# The guts of the main operation...
#----------------------------------------------------------------------
    def __init__(self, parent, id, log):
        wx.Notebook.__init__(self, parent, id, size=(21,21), style=wx.BK_DEFAULT)

        win = SortedList(self, Global.Ins)
        self.AddPage(win, 'Transactions')
        self.Show(True)



class myFrame(wx.Frame):
    def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, size=size, style=style)
        self.CreateStatusBar(1)
        log=Log()
        self.win = Selector(self, -1, log)

class MyApp(wx.App):
    def OnInit(self):
        #============================================================
        # Gettin' the data, nom nom nom
        self.loadDirect()
        self.loadTransaction()
        #============================================================
        f = myFrame(None, -1, "Transaction Testing",wx.Size(700,600))
        f.Show()            
        return True


    def loadDirect(self):
        Global.offices      = parseDirectDat(uri.UriToOsPath(str(Global.cfgFile.directDat[0])))
        self.header = ['ChartNumber', 'Date', 'SeqNum', 'ProcCode', 'Charge', 'InsBal','SecBal','PriAllow','SecAllow','TerAllow','PriAdj','Expected', 'SecAdj', 'TerAdj', 'AdjAmt3']
        Global.Ins          = [self.header]
        Global.Pats         = []
        
    def loadTransaction(self):
        #header = ['ChartNumber', 'Date', 'SeqNum', 'ProcCode', 'Charge', 'InsBal','SecBal','PriAllow','SecAllow','TerAllow','PriAdj','Expected', 'SecAdj', 'TerAdj', 'AdjAmt3']
        #Global.Ins.append(header)
        count = 0
        obj = Transaction()
        recLen = obj.RecordLength
        for offNum, offPath in Global.offices.iteritems():
            if (offPath.Ref == ''):
                offPath.Ref = offPath.Default
            with open(offPath.Ref + obj.TLA + '.dat','r+b') as inFile:
                inRec = inFile.read(recLen)                 # burn the header record 
                inRec = inFile.read(recLen)
                while not (len(inRec) < recLen):
                    if (count == 100): return
                    obj = Transaction(inRec)
                    if (obj.Valid and not obj.ExtChg):
                        line = []
                        for field in self.header:
                            line.append(str(getattr(obj, field)))
                        Global.Ins.append(line)
                        count +=1
                    inRec = inFile.read(recLen)



#===============================================================================================
#      Where it all begins...
#===============================================================================================
def main(argv=None):
    if argv is None:
        argv = sys.argv
    Global.cfgFileName              = os.getcwd() + os.sep + 'fsr_labels.xml'
    Global.cfgFile   = ConfigFile(Global.cfgFileName, "directDat")
    Global.cfgFile.Load()

    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    main()
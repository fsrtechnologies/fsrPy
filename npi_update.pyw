from __future__ import with_statement
import wx, string, sys, os
import logging, urllib
from configobj import ConfigObj
from validate import Validator
from fsrStuff.umFuncs import NPI_Luhn, parseDirectDat, RecordGenerator
from fsrStuff.SortList import SortedList
from fsrStuff.NPIFile import NPIFile

try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO
try:
    import wx.lib.inspection
except ImportError:
    pass


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

class Log(object):
    """Log output is redirected to the status bar of the containing frame.
    """
    def WriteText(self,text_string):
        self.write(text_string)
    def write(self,text_string):
        wx.GetApp().GetTopWindow().SetStatusText(text_string)
class NPIMapObj(object):
    def __init__(self, srcFile="", Name="", legCode="", legType="", NPI=""):
        self.srcFile    = srcFile
        self.Name       = Name 
        self.LegCode    = legCode
        self.LegType    = legType
        self.NPI        = NPI
        if not self.NPI:
            self.NPI = Global.npiList.getNPI(legType, legCode)
            
class ConfigFrame(wx.Frame):
    def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, size=size, style=style)
        self.CreateStatusBar(1)
        self.log=Log()
        
        pnl = wx.Panel(self)
        boxOuter = wx.BoxSizer(wx.VERTICAL)
        boxOuter.Add(wx.StaticText(pnl, -1, "           Needful things:"), 0, wx.ALIGN_TOP)
        
        boxInner2a = wx.BoxSizer(wx.HORIZONTAL)
        boxInner2a.Add(wx.StaticText(pnl, -1, "UltraMed data directory file:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.log.write("UltraMed data directory file: %s" % str(Global.cfgFile["npiXMLFile"]))
        boxOuter.Add(boxInner2a, 1, wx.ALIGN_CENTER | wx.ALIGN_BOTTOM)

        boxInner2b = wx.BoxSizer(wx.HORIZONTAL)
        fpDDat = wx.FilePickerCtrl(pnl, message = 'Select DIRECT.DAT in your UltraMed directory', 
                                   wildcard = 'direct*.dat', path = urllib.url2pathname(str(Global.cfgFile["directDat"]))) 
        boxInner2b.Add(fpDDat, wx.ALIGN_CENTER)
        boxOuter.Add(boxInner2b, 1, wx.ALIGN_CENTER | wx.ALIGN_TOP)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnPickDirectDat, fpDDat)

        boxInner3a = wx.BoxSizer(wx.HORIZONTAL)
        boxInner3a.Add(wx.StaticText(pnl, -1, "NPI lookup file:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.log.write("NPI db file: %s" % str(Global.cfgFile["npiXMLFile"]))
        boxOuter.Add(boxInner3a, 1, wx.ALIGN_CENTER | wx.ALIGN_BOTTOM)
        
        if (Global.cfgFile["npiXMLFile"] == ''):
            self.npiXMLFile = os.getcwd() + os.sep + 'npiMap.xml'
        else:
            self.npiXMLFile = urllib.url2pathname(str(Global.cfgFile["npiXMLFile"]))    

        boxInner3b = wx.BoxSizer(wx.HORIZONTAL)
        fpXML = wx.FilePickerCtrl(pnl, message = 'Select the file containing NPI-to-legacy code mapping', 
                                  wildcard = "XML files (*.xml)|*.xml", path = self.npiXMLFile, 
                                  style = wx.FLP_OPEN | wx.FLP_USE_TEXTCTRL)
        
        
        boxInner3b.Add(fpXML, wx.ALIGN_CENTER)
        boxOuter.Add(boxInner3b, 1, wx.ALIGN_CENTER | wx.ALIGN_TOP)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnPickNPIFile, fpXML)

        boxInner4 = wx.BoxSizer(wx.HORIZONTAL)
        IDs = [wx.ID_SAVE, wx.ID_CANCEL]
        for ID in IDs:
            b = wx.Button(pnl, ID)
            boxInner4.Add(b, 0, wx.ALL, 5)
            self.Bind(wx.EVT_BUTTON, self.OnClickCfg, b)
        boxOuter.Add(boxInner4, 1, wx.ALIGN_CENTER | wx.ALIGN_BOTTOM)
        pnl.SetSizer(boxOuter)

    def OnPickDirectDat(self, evt):
        Global.cfgFile["directDat"]  = unicode(urllib.pathname2url(evt.GetPath()))
        self.log.write("Directory file for UltraMed data: %s" % str(Global.cfgFile["directDat"]))
        
    def OnPickNPIFile(self, evt):
        Global.cfgFile["npiXMLFile"] = unicode(urllib.pathname2url(evt.GetPath()))
        self.log.write("NPI file: %s" % str(Global.cfgFile["npiXMLFile"]))
        
    def OnClickCfg(self, event):
        btn = event.GetId() 
        if (btn == wx.ID_SAVE):
            if not ((len(str(Global.cfgFile["directDat"])) > 10) and os.path.exists(urllib.url2pathname(str(Global.cfgFile["directDat"])))):
                dlg = wx.MessageDialog(self, "You didn't tell me where to find the UltraMed data.  Try again!",
                            "Naughty, naughty!", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            if not (len(str(Global.cfgFile["npiXMLFile"])) > 6): 
                dlg = wx.MessageDialog(self, "You didn't tell me where to find/save the NPI mapping.  Try again!",
                            "Naughty, naughty!", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            if (self.npiXMLFile == Global.cfgFileName): 
                dlg = wx.MessageDialog(self, "You're trying to over-write the configuration file for this program.  Choose another file!",
                            "Naughty, naughty!", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            if not os.path.exists(urllib.url2pathname(str(Global.cfgFile["npiXMLFile"]))): 
                dlg = wx.MessageDialog(self, "The NPI file you specified doesn't exist (yet).  Should I create it?",
                            "Create a new file?", wx.YES_NO | wx.ICON_QUESTION)
                response = dlg.ShowModal()
                dlg.Destroy()
                if (response == wx.ID_NO): return
                npiFile = NPIFile(urllib.url2pathname(str(Global.cfgFile["npiXMLFile"])))
                npiFile.Save()
            Global.cfgFile.write()
            Global.cfgDone = 1
        else:
            Global.cfgDone = 2
        self.Destroy()
        event.Skip()
class ConfigApp(wx.App):
    def OnInit(self):
        f = ConfigFrame(None, -1, "FSRNPI - Configuration",wx.Size(400,220))
        f.Show()            
        return True


class myNB(wx.Notebook):
#----------------------------------------------------------------------
# The guts of the main operation...
#----------------------------------------------------------------------
    def __init__(self, parent, id, log):
        wx.Notebook.__init__(self, parent, id, size=wx.DefaultSize, style=wx.BK_DEFAULT)
        self.log = log

        pageEIN = npiList(self,Global.EIN, log)
        self.AddPage(pageEIN, "EINs")
        pageLicense = npiList(self, Global.License, log)
        self.AddPage(pageLicense, "Licenses")
        pageDocs = npiList(self, Global.MedicareID,log)
        self.AddPage(pageDocs, "Medicare IDs")
        pageDocs = npiList(self, Global.MedicaidID,log)
        self.AddPage(pageDocs, "Medicaid IDs")
        pageRefs = npiList(self, Global.SSN,log)
        self.AddPage(pageRefs, "SSNs")
        pageRefs = npiList(self, Global.UPIN,log)
        self.AddPage(pageRefs, "UPINs")
        pageFacs = npiList(self, Global.BlueCrossID,log)
        self.AddPage(pageFacs, "Blue Cross IDs")
        pageFacs = npiList(self, Global.BlueShieldID,log)
        self.AddPage(pageFacs, "Blue Shield IDs")
        pageLabs = npiList(self, Global.OtherID1,log)
        self.AddPage(pageLabs, "Other1 IDs")
        pageLabs = npiList(self, Global.OtherID2,log)
        self.AddPage(pageLabs, "Other2 IDs")
        self.Show(True)
        
class npiList(SortedList):
    def __init__(self, parent, inThing, log):
        self.itemtype = unicode(inThing[0][2])
        SortedList.__init__(self, parent,inThing, log)
        self.log=log
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def OnItemActivated(self, event):       # this is where the magic happens!
        self.currentItem = event.m_itemIndex
        obj = NPIMapObj(self.GetItemText(self.currentItem),
                        self.getColumnText(self.currentItem, 1),
                        self.getColumnText(self.currentItem, 2),
                        self.itemtype,
                        self.getColumnText(self.currentItem, 3))
        print obj.srcFile, obj.Name, obj.LegCode, obj.LegType, obj.NPI

        self.log.WriteText('Updating NPI for %s: %s' % (self.itemtype, obj.LegCode))
        dlg = wx.TextEntryDialog(self, message=obj.Name, caption='Enter NPI', defaultValue=unicode(obj.NPI))

        if dlg.ShowModal() == wx.ID_OK:
            tmpStr = dlg.GetValue().strip()
            self.log.WriteText('You entered: %s\n' % tmpStr)
            if (tmpStr == ''):
                obj.NPI =''
                self.updateNPI(obj)
                self.refreshList()
                self.SortListItems()
                self.log.WriteText('Deleting NPI for %s' % obj.Name)
                self.updateDict(obj.LegCode, '')
                self.refreshList()
            elif (tmpStr.isdigit()):
                if ((len(tmpStr) == 10) or (len(tmpStr) == 15)):
                    if (NPI_Luhn(tmpStr)):
                        obj.NPI = tmpStr
                        self.updateNPI(obj)
                        self.updateDict(obj.LegCode, obj.NPI)
                        self.refreshList()
                    else: self.log.WriteText('%s is not valid - invalid checkdigit' % tmpStr)
                else: self.log.WriteText('%s is not valid - must be 10 or 15 digits long' % tmpStr)
            else: self.log.WriteText('%s is not valid - must be all-numeric' % tmpStr)
        dlg.Destroy()
        
    def updateDict(self, LegCode, NPI):
        for key, data in (self.thing).iteritems():
            if data[2] == LegCode:
                data[3] = NPI
        self.itemDataMap = self.thing
            
    def updateNPI(self, obj):
        Global.npiList.update(obj)

class myFrame(wx.Frame):
    def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, size=size, style=style)
        self.CreateStatusBar(1)
        log=Log()
        self.win = myNB(self, -1, log)

class MyApp(wx.App):
    def OnInit(self):
        f = myFrame(None, -1, "FSRNPI - NPI list update utility",wx.Size(700,600))
        f.Show()            
        return True

class SplashFrame(wx.Frame):
    def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, size=size, style=style)
        self.CreateStatusBar(1)
        self.log=Log()
        self.jobID = 0

        pnl = wx.Panel(self)
        boxOuter = wx.BoxSizer(wx.VERTICAL)
        
        boxInner1 = wx.BoxSizer(wx.HORIZONTAL)
        boxInner1.Add(wx.StaticText(pnl, -1, "Loading UltraMed data from:    %s" % str(Global.cfgFile["directDat"])), 0, wx.ALIGN_CENTER_VERTICAL)
        boxOuter.Add(boxInner1, 1, wx.ALIGN_CENTER | wx.ALIGN_TOP)

        boxInner3 = wx.BoxSizer(wx.HORIZONTAL)
        self.btnCancel = wx.Button(pnl, -1, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.handleCancel, self.btnCancel)
        self.btnCancel.Enable(True)

        boxInner3.Add(self.btnCancel, 0, wx.ALL, 5)
        boxOuter.Add(boxInner3, 1, wx.ALIGN_CENTER | wx.ALIGN_TOP)
        pnl.SetSizer(boxOuter)
        self.Show(True)
        
        self.loadDirect()
        self.loadGroups()
        self.loadDoctors()
        self.loadReferrals()
        self.loadFacilities()
        self.loadLabs()
        self.Cleanup()
        
    def Cleanup(self):
        Global.dataLoaded = True
        self.Close(True)

    def loadDirect(self):
        Global.serialID = 0
        for itemType in ['EIN', 'License', 'SSN', 'MedicareID', 'MedicaidID', 'BlueCrossID', 'BlueShieldID', 'UPIN', 'OtherID1', 'OtherID2']:
            header = ["Source", "Name", itemType, "NPI"]
            setattr(Global, itemType, [header])
        Global.offices      = parseDirectDat(urllib.url2pathname(str(Global.cfgFile["directDat"])))
        
    def loadGroups(self):
        msg = 'Loading groups...'
        magic = ['EIN', 'License', 'SSN', 'MedicareID', 'MedicaidID', 'BlueCrossID', 'BlueShieldID', 'OtherID1', 'OtherID2']
        
        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "Group"):
                Global.serialID +=1
                obj.ID=str(Global.serialID)
                if not (obj.Name == '') or (obj.GroupName == ''): #skip empty groups - e.g. pages 2 and 3 if not in use...
                    msgNow = msg + ' ' + str(obj.ID)
                    self.log.write(msgNow)
                    for typ in magic:
                        if not (getattr(obj, typ) == ''):  #i.e, e.g., "if not obj.EIN ==''"
                            srcFile = num + "OFF"
                            code = NPIMapObj(srcFile, Name=obj.Name, legCode=getattr(obj, typ).upper(), legType=unicode(typ))
                            getattr(Global, typ).append([code.srcFile, code.Name, code.LegCode, code.NPI])
            
    def loadDoctors(self):
        msg = 'Loading doctors...'
        magic = ['EIN', 'License', 'SSN', 'MedicareID', u'MedicaidID', 'BlueCrossID', 'BlueShieldID', 'UPIN', 'OtherID1', 'OtherID2']

        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "Doctor"):
                if not (len(obj.ID)<1): 
                    msgNow = msg + ' ' + str(obj.ID)
                    self.log.write(msgNow)
                    for typ in magic:
                        if not (getattr(obj, typ) == ''):  #i.e, e.g., "if not obj.EIN ==''"
                            srcFile = num + obj.TLA
                            code = NPIMapObj(srcFile, Name=obj.Name, legCode=getattr(obj, typ).upper(), legType=unicode(typ))
                            getattr(Global, typ).append([code.srcFile, code.Name, code.LegCode, code.NPI])

    def loadReferrals(self):
        msg ='Loading referral sources...'
        magic = ['License', 'MedicareID', 'MedicaidID', 'UPIN']
        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "ReferralSource"):
                if (obj.ID[0]=='P'):                    #only P(hysician) referrals have NPI numbers
                    msgNow = msg + ' ' + str(obj.ID)
                    self.log.write(msgNow)
                    for typ in magic:
                        if not (getattr(obj, typ) == ''):  #i.e, e.g., "if not obj.EIN ==''"
                            srcFile = num + obj.TLA
                            code = NPIMapObj(srcFile, Name=obj.Name, legCode=getattr(obj, typ).upper(), legType=unicode(typ))
                            getattr(Global, typ).append([code.srcFile, code.Name, code.LegCode, code.NPI])

    def loadFacilities(self):
        msg = 'Loading facilities...'
        magic = ['MedicareID', 'MedicaidID', 'OtherID1']
        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "Facility"):
                logging.info("%s %s - %s - Mcare %s - MCal %s - Other %s" % (num, obj.ID, obj.Name, obj.MedicareID, obj.MedicaidID, obj.OtherID1))
                #if not ((len(obj.ID)<1) or (len(obj.MedicareID)<3) or (len(obj.MedicaidID)<3) or (len(obj.OtherID1)<3)): 
                msgNow = msg + ' ' + str(obj.ID)
                self.log.write(msgNow)
                for typ in magic:
                    if not (getattr(obj, typ) == ''):  #i.e, e.g., "if not obj.EIN ==''"
                        srcFile = num + obj.TLA
                        code = NPIMapObj(srcFile, Name=obj.Name, legCode=getattr(obj, typ).upper(), legType=unicode(typ))
                        getattr(Global, typ).append([code.srcFile, code.Name, code.LegCode, code.NPI])

    def loadLabs(self):
        msg = 'Loading labs...'
        magic = ['MedicareID']
        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "Laboratory"):
                if not ((len(obj.ID)<1) or (len(obj.MedicareID)<3)): 
                    msgNow = msg + ' ' + str(obj.ID)
                    self.log.write(msgNow)
                    for typ in magic:
                        if not (getattr(obj, typ) == ''):  #i.e, e.g., "if not obj.EIN ==''"
                            srcFile = num + obj.TLA
                            code = NPIMapObj(srcFile, Name=obj.Name, legCode=getattr(obj, typ).upper(), legType=unicode(typ))
                            getattr(Global, typ).append([code.srcFile, code.Name, code.LegCode, code.NPI])

    def handleCancel(self, event): 
        self.Close(True)
        sys.exit()
class SplashApp(wx.App):
    def OnInit(self):
        splash = SplashFrame(None, -1, "FSRNPI - loading data, please wait...",wx.Size(450,200))
        splash.Show()
        return True

#===============================================================================================
#      Where it all begins...
#===============================================================================================
def main(argv=None):
    if argv is None:
        argv = sys.argv

    test = Global.cfgFile.validate(Global.vtor, copy=True)
    Global.cfgFile.write()
        
    logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s %(message)s',
                    filename='npi_update.log',
                    filemode='w')

    if not (os.path.exists(str(Global.cfgFileName)) and os.path.exists(urllib.url2pathname(str(Global.cfgFile["directDat"]))) and os.path.exists(urllib.url2pathname(str(Global.cfgFile["npiXMLFile"])))):
        Global.cfgDone = False
        cfg = ConfigApp(0)
        cfg.MainLoop()
        if (Global.cfgDone == 2):
            dlg = wx.MessageDialog(None, "I can't go on like this!  Try again, and next time tell me what I need to know!",
                            "Abort! Abort!", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            sys.exit()

    Global.npiList = NPIFile(urllib.url2pathname(str(Global.cfgFile["npiXMLFile"])))
    Global.npiList.Load()

    Global.dataLoaded = False
    sploosh = SplashApp(0)
    sploosh.MainLoop()
    if not Global.dataLoaded: sys.exit()
    app = MyApp(0)
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
from __future__ import with_statement
import wx, string, sys, os
import logging
from   fsrStuff.umFuncs import *
from   fsrStuff.SortList import *
from   fsrStuff.SortCheck import *
from   fsrStuff.ConfigFile import *
from   fsrStuff.NPIFile import *
import Ft.Lib.Uri as uri

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
    cfgFileName = os.getcwd() + os.sep + 'npi_upd.xml'
    cfgFile = ConfigFile(cfgFileName, "directDat","npiXMLFile")

class Log(object):
    """Log output is redirected to the status bar of the containing frame.
    """
    def WriteText(self,text_string):
        self.write(text_string)
    def write(self,text_string):
        wx.GetApp().GetTopWindow().SetStatusText(text_string)
class NPIMapObj(object):
    def __init__(self, offNum="", Name="", LegCode="", LegType="", NPI=""):
        self.offNum     = offNum
        self.Name       = Name 
        self.LegCode    = LegCode
        self.LegType    = LegType
        self.NPI        = NPI
        self.NPInum     = ""
        npiItems = Global.npiList.xml_xpath( u'//npiItem[@legacyType="%s" and legacyCode="%s"]' % (LegType,LegCode))
        if (len(npiItems) != 0): 
            self.NPI = str(npiItems[0].NPI)

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
        self.log.write("UltraMed data directory file: %s" % str(Global.cfgFile.npiXMLFile))
        boxOuter.Add(boxInner2a, 1, wx.ALIGN_CENTER | wx.ALIGN_BOTTOM)

        boxInner2b = wx.BoxSizer(wx.HORIZONTAL)
        fpDDat = wx.FilePickerCtrl(pnl, message = 'Select DIRECT.DAT in your UltraMed directory', 
                                   wildcard = 'direct*.dat', path = uri.UriToOsPath(str(Global.cfgFile.directDat))) 
        boxInner2b.Add(fpDDat, wx.ALIGN_CENTER)
        boxOuter.Add(boxInner2b, 1, wx.ALIGN_CENTER | wx.ALIGN_TOP)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnPickDirectDat, fpDDat)

        boxInner3a = wx.BoxSizer(wx.HORIZONTAL)
        boxInner3a.Add(wx.StaticText(pnl, -1, "NPI lookup file:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.log.write("NPI db file: %s" % str(Global.cfgFile.npiXMLFile))
        boxOuter.Add(boxInner3a, 1, wx.ALIGN_CENTER | wx.ALIGN_BOTTOM)
        
        if (Global.cfgFile.npiXMLFile == ''):
            self.npiXMLFile = os.getcwd() + os.sep + 'npiMap.xml'
        else:
            self.npiXMLFile = uri.UriToOsPath(str(Global.cfgFile.npiXMLFile))    

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
        Global.cfgFile.directDat       = unicode(uri.OsPathToUri(evt.GetPath()))
        self.log.write("Directory file for UltraMed data: %s" % str(Global.cfgFile.directDat))
        
    def OnPickNPIFile(self, evt):
        Global.cfgFile.npiXMLFile                = unicode(uri.OsPathToUri(evt.GetPath()))
        self.log.write("NPI file: %s" % str(Global.cfgFile.npiXMLFile))
        
    def OnClickCfg(self, event):
        btn = event.GetId() 
        if (btn == wx.ID_SAVE):
            if not ((len(str(Global.cfgFile.directDat)) > 10) and os.path.exists(uri.UriToOsPath(str(Global.cfgFile.directDat)))):
                dlg = wx.MessageDialog(self, "You didn't tell me where to find the UltraMed data.  Try again!",
                            "Naughty, naughty!", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            if not (len(str(Global.cfgFile.npiXMLFile)) > 6): 
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
            if not os.path.exists(uri.UriToOsPath(str(Global.cfgFile.npiXMLFile))): 
                dlg = wx.MessageDialog(self, "The NPI file you specified doesn't exist (yet).  Should I create it?",
                            "Create a new file?", wx.YES_NO | wx.ICON_QUESTION)
                response = dlg.ShowModal()
                dlg.Destroy()
                if (response == wx.ID_NO): return
                npiFile = NPIFile(uri.UriToOsPath(str(Global.cfgFile.npiXMLFile)))
                npiFile.Save()
            Global.cfgFile.Save()
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
        print obj.offNum, obj.Name, obj.LegCode, obj.LegType, obj.NPI

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
        npiItems = Global.npiList.xml_xpath( u'//npiItem[@legacyType="%s" and legacyCode="%s"]' % (obj.LegType, obj.LegCode))
        if (len(npiItems) == 0):            # there's no such thing, 
            if not (obj.NPI == ''):         #  so, if the NPI was blank we don't need to delete it... but if the NPI isn't blank we need to get busy
                npiItem = Global.npiList.xml_create_element(u"npiItem", attributes={u"legacyType":obj.LegType})
                npiItem.xml_append(Global.npiList.xml_create_element(u"legacyCode"))
                npiItem.legacyCode = unicode(obj.LegCode)
                npiItem.xml_append(Global.npiList.xml_create_element(u"NPI"))
                npiItem.NPI = unicode(obj.NPI)
                Global.npiList.xml_append(npiItem)
        else:                               # this entry already exists
            if (obj.NPI == ''):             #  so if NPI was blank we need to delete it...
                ix = npiItems[0].xml_index_on_parent
                Global.npiList.xml_remove_child_at(ix)
            else:                           # but if the NPI isn't blank we need to get busy
                npiItems[0].NPI = unicode(obj.NPI)
        # if nothing actually fit, 
        #     create new "npiItem" with subelements "NPI", "legacyCode" and "legacyType"
        # else
        #     set "NPI" subelement to newly-entered NPI code
        # if NPI is actually blank, then delete "npiItem" and subelements if they exist
        Global.npiList.Save()

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
        boxInner1.Add(wx.StaticText(pnl, -1, "Loading UltraMed data from:    %s" % str(Global.cfgFile.directDat)), 0, wx.ALIGN_CENTER_VERTICAL)
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
            header = ["Off#", "Name", itemType, "NPI"]
            setattr(Global, itemType, [header])
        Global.offices      = parseDirectDat(uri.UriToOsPath(str(Global.cfgFile.directDat[0])))
        
    def loadGroups(self):
        msg = 'Loading groups...'
        obj = Group()
        magic = ['EIN', 'License', 'SSN', 'MedicareID', 'MedicaidID', 'BlueCrossID', 'BlueShieldID', 'OtherID1', 'OtherID2']
        recLen = obj.RecordLength
        for offNum, offPath in Global.offices.iteritems():
            msg = msg + ' Off' + str(offNum) + '...'
            self.log.write(msg)
            if (offPath.Rpt == ''): offPath.Rpt = offPath.Default
            thisFile = offPath.Rpt + obj.TLA + '.dat'
            if (os.path.getsize(thisFile) >= 2*recLen):  # make sure there's at least one real record, not just a header
                with open(thisFile,'r+b') as inFile:
                    tmpIn = inFile.read(recLen)                 # burn the header record 
                    tmpIn = inFile.read(recLen*4096)
                    while not (len(tmpIn) < recLen):
                        buf = StringIO.StringIO(tmpIn)
                        inRec = buf.read(recLen)
                        while not (len(inRec) < recLen):
                            if (inRec[5:6].split("\x00")[0] == 'A'):  #RPT file contains lots of stuff - 'A' records are group info
                                Global.serialID +=1
                                obj = Group(rec=inRec, ID=str(Global.serialID))
                                if not (obj.Name == '') or (obj.GroupName == ''): #skip empty groups - e.g. pages 2 and 3 if not in use...
                                    msgNow = msg + ' ' + str(obj.ID)
                                    self.log.write(msgNow)
                                    for typ in magic:
                                        if not (getattr(obj, typ) == ''):  #i.e, e.g., "if not obj.EIN ==''"
                                            code = NPIMapObj(offNum, Name=obj.Name, LegCode=getattr(obj, typ).upper(), LegType=unicode(typ))
                                            getattr(Global, typ).append([code.offNum, code.Name, code.LegCode, code.NPI])
                            inRec = buf.read(recLen)
                        buf.close()
                        tmpIn = inFile.read(recLen*4096)
            
    def loadDoctors(self):
        msg = 'Loading doctors...'
        obj = Doctor()
        magic = ['EIN', 'License', 'SSN', 'MedicareID', u'MedicaidID', 'BlueCrossID', 'BlueShieldID', 'UPIN', 'OtherID1', 'OtherID2']
        recLen = obj.RecordLength
        for offNum, offPath in Global.offices.iteritems():
            msg = msg + ' Off' + str(offNum) + '...'
            self.log.write(msg)
            if (offPath.Doc == ''): offPath.Doc = offPath.Default
            thisFile = offPath.Doc + obj.TLA + '.dat'
            if (os.path.getsize(thisFile) >= 2*recLen):  # make sure there's at least one real record, not just a header
                with open(thisFile,'r+b') as inFile:
                    tmpIn = inFile.read(recLen)                 # burn the header record 
                    tmpIn = inFile.read(recLen*4096)
                    while not (len(tmpIn) < recLen):
                        buf = StringIO.StringIO(tmpIn)
                        inRec = buf.read(recLen)
                        while not (len(inRec) < recLen):
                            obj = Doctor(inRec)
                            if obj.Valid:
                                if not (len(obj.ID)<1): 
                                    msgNow = msg + ' ' + str(obj.ID)
                                    self.log.write(msgNow)
                                    for typ in magic:
                                        if not (getattr(obj, typ) == ''):  #i.e, e.g., "if not obj.EIN ==''"
                                            code = NPIMapObj(offNum, Name=obj.Name, LegCode=getattr(obj, typ).upper(), LegType=unicode(typ))
                                            getattr(Global, typ).append([code.offNum, code.Name, code.LegCode, code.NPI])
                            inRec = buf.read(recLen)
                        buf.close()
                        tmpIn = inFile.read(recLen*4096)

    def loadReferrals(self):
        msg ='Loading referral sources...'
        obj = ReferralSource()
        magic = ['License', 'MedicareID', 'MedicaidID', 'UPIN']
        recLen = obj.RecordLength
        for offNum, offPath in Global.offices.iteritems():
            msg = msg + ' Off' + str(offNum) + '...'
            self.log.write(msg)
            if (offPath.Ref == ''): offPath.Ref = offPath.Default
            thisFile = offPath.Ref + obj.TLA + '.dat'
            if (os.path.getsize(thisFile) >= 2*recLen):  # make sure there's at least one real record, not just a header
                with open(thisFile,'r+b') as inFile:
                    tmpIn = inFile.read(recLen)                 # burn the header record 
                    tmpIn = inFile.read(recLen*4096)
                    while not (len(tmpIn) < recLen):
                        buf = StringIO.StringIO(tmpIn)
                        inRec = buf.read(recLen)
                        while not (len(inRec) < recLen):
                            obj = ReferralSource(inRec)
                            if (obj.Valid and obj.ID[0]=='P'):                    #only P(hysician) referrals have NPI numbers
                                msgNow = msg + ' ' + str(obj.ID)
                                self.log.write(msgNow)
                                for typ in magic:
                                    if not (getattr(obj, typ) == ''):  #i.e, e.g., "if not obj.EIN ==''"
                                        code = NPIMapObj(offNum, Name=obj.Name, LegCode=getattr(obj, typ).upper(), LegType=unicode(typ))
                                        getattr(Global, typ).append([code.offNum, code.Name, code.LegCode, code.NPI])
                            inRec = buf.read(recLen)
                        buf.close()
                        tmpIn = inFile.read(recLen*4096)

    def loadFacilities(self):
        msg = 'Loading facilities...'
        obj = Facility()
        magic = ['MedicareID', 'MedicaidID', 'OtherID1']
        recLen = obj.RecordLength
        for offNum, offPath in Global.offices.iteritems():
            msg = msg + ' Off' + str(offNum) + '...'
            self.log.write(msg)
            if (offPath.Fac == ''): offPath.Fac = offPath.Default
            thisFile = offPath.Fac + obj.TLA + '.dat'
            if (os.path.getsize(thisFile) >= 2*recLen):  # make sure there's at least one real record, not just a header
                with open(thisFile,'r+b') as inFile:
                    tmpIn = inFile.read(recLen)                 # burn the header record 
                    tmpIn = inFile.read(recLen*4096)
                    while not (len(tmpIn) < recLen):
                        buf = StringIO.StringIO(tmpIn)
                        inRec = buf.read(recLen)
                        while not (len(inRec) < recLen):
                            obj = Facility(inRec)
                            if obj.Valid:
                                logging.info("%s %s - %s - Mcare %s - MCal %s - Other %s" % (offNum, obj.ID, obj.Name, obj.MedicareID, obj.MedicaidID, obj.OtherID1))
                                if not ((len(obj.ID)<1) or (len(obj.MedicareID)<3) or (len(obj.MedicaidID)<3) or (len(obj.OtherID1)<3)): 
                                    msgNow = msg + ' ' + str(obj.ID)
                                    self.log.write(msgNow)
                                    for typ in magic:
                                        if not (getattr(obj, typ) == ''):  #i.e, e.g., "if not obj.EIN ==''"
                                            code = NPIMapObj(offNum, Name=obj.Name, LegCode=getattr(obj, typ).upper(), LegType=unicode(typ))
                                            getattr(Global, typ).append([code.offNum, code.Name, code.LegCode, code.NPI])
                            inRec = buf.read(recLen)
                        buf.close()
                        tmpIn = inFile.read(recLen*4096)

    def loadLabs(self):
        msg = 'Loading labs...'
        obj = Laboratory()
        magic = ['MedicareID']
        recLen = obj.RecordLength
        for offNum, offPath in Global.offices.iteritems():
            msg = msg + ' Off' + str(offNum) + '...'
            self.log.write(msg)
            if (offPath.Lab == ''): offPath.Lab = offPath.Default
            thisFile = offPath.Lab + obj.TLA + '.dat'
            if (os.path.getsize(thisFile) >= 2*recLen):  # make sure there's at least one real record, not just a header
                with open(thisFile,'r+b') as inFile:
                    tmpIn = inFile.read(recLen)                 # burn the header record 
                    tmpIn = inFile.read(recLen*4096)
                    while not (len(tmpIn) < recLen):
                        buf = StringIO.StringIO(tmpIn)
                        inRec = buf.read(recLen)
                        while not (len(inRec) < recLen):
                            obj = Laboratory(inRec)
                            if (obj.Valid and not ((len(obj.ID)<1) or (len(obj.MedicareID)<3))): 
                                msgNow = msg + ' ' + str(obj.ID)
                                self.log.write(msgNow)
                                for typ in magic:
                                    if not (getattr(obj, typ) == ''):  #i.e, e.g., "if not obj.EIN ==''"
                                        code = NPIMapObj(offNum, Name=obj.Name, LegCode=getattr(obj, typ).upper(), LegType=unicode(typ))
                                        getattr(Global, typ).append([code.offNum, code.Name, code.LegCode, code.NPI])
                            inRec = buf.read(recLen)
                        buf.close()
                        tmpIn = inFile.read(recLen*4096)

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
    logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s %(message)s',
                    filename='npi_update.log',
                    filemode='w')
    Global.cfgFile.Load()

    if not (os.path.exists(str(Global.cfgFileName)) and os.path.exists(uri.UriToOsPath(str(Global.cfgFile.directDat))) and os.path.exists(uri.UriToOsPath(str(Global.cfgFile.npiXMLFile)))):
        Global.cfgDone = False
        cfg = ConfigApp(0)
        cfg.MainLoop()
        if (Global.cfgDone == 2):
            dlg = wx.MessageDialog(None, "I can't go on like this!  Try again, and next time tell me what I need to know!",
                            "Abort! Abort!", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            sys.exit()

    Global.npiList   = NPIFile(uri.UriToOsPath(str(Global.cfgFile.npiXMLFile)))
    Global.npiList.Load()

    Global.dataLoaded               = False
    sploosh = SplashApp(0)
    sploosh.MainLoop()
    if not Global.dataLoaded: sys.exit()
    app = MyApp(0)
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
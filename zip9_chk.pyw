from __future__ import with_statement
import wx, string, sys, os
import logging
from configobj import ConfigObj
from validate import Validator
from fsrStuff.umFuncs import *
from fsrStuff.SortList import *
from fsrStuff.SortCheck import *
from fsrStuff.ConfigFile import *
import urllib

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
    cfgFileName = os.getcwd() + os.sep + 'zip9_chk.ini'
    tmpStr = """
    directDat = string(default="direct.dat")
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
        boxOuter.Add(boxInner2a, 1, wx.ALIGN_CENTER | wx.ALIGN_BOTTOM)

        boxInner2b = wx.BoxSizer(wx.HORIZONTAL)
        fpDDat = wx.FilePickerCtrl(pnl, message = 'Select DIRECT.DAT in your UltraMed directory', 
                                   wildcard = 'direct*.dat', path = urllib.url2pathname(str(Global.cfgFile["directDat"]))) 
        boxInner2b.Add(fpDDat, wx.ALIGN_CENTER)
        boxOuter.Add(boxInner2b, 1, wx.ALIGN_CENTER | wx.ALIGN_TOP)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnPickDirectDat, fpDDat)

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
        
    def OnClickCfg(self, event):
        btn = event.GetId() 
        if (btn == wx.ID_SAVE):
            if not ((len(str(Global.cfgFile["directDat"])) > 10) and os.path.exists(urllib.url2pathname(str(Global.cfgFile["directDat"])))):
                dlg = wx.MessageDialog(self, "You didn't tell me where to find the UltraMed data.  Try again!",
                            "Naughty, naughty!", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            Global.cfgFile.write()
            Global.cfgDone = 1
        else:
            Global.cfgDone = 2
        self.Destroy()
        event.Skip()
class ConfigApp(wx.App):
    def OnInit(self):
        f = ConfigFrame(None, -1, "FSRZip9 - Configuration",wx.Size(400,220))
        f.Show()            
        return True


class myNB(wx.Notebook):
#----------------------------------------------------------------------
# The guts of the main operation...
#----------------------------------------------------------------------
    def __init__(self, parent, id, log):
        wx.Notebook.__init__(self, parent, id, size=wx.DefaultSize, style=wx.BK_DEFAULT)
        self.log = log

        pageGroups = zip9List(self,Global.GroupList, log)
        self.AddPage(pageGroups, "Groups")
        pageDoctors = zip9List(self,Global.DoctorList, log)
        self.AddPage(pageDoctors, "Doctors")
        pageInsurances = zip9List(self,Global.InsuranceList, log)
        self.AddPage(pageInsurances, "Insurances")
        pageFacilities = zip9List(self,Global.FacilityList, log)
        self.AddPage(pageFacilities, "Facilities")
        pageReferrals = zip9List(self,Global.ReferralList, log)
        self.AddPage(pageReferrals, "Referrals")
        pageLabs = zip9List(self,Global.LabList, log)
        self.AddPage(pageLabs, "Labs")
        self.Show(True)
        
class zip9List(SortedCheckList):
    def __init__(self, parent, inThing, log):
        self.itemtype = unicode(inThing[0][2])
        SortedCheckList.__init__(self, parent,inThing, log)
        self.log=log
        #self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

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
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileMenu.Append(103, "&Print selected items\tCtrl-P", "Print checked items")
        fileMenu.Append(104, "&Exit\tAlt-F4", "Quit this program")
        # Add menu to the menu bar
        menuBar.Append(fileMenu, "&File")
        editMenu = wx.Menu()
        editMenu.Append(201, "&Select All\tCtrl-A", "Check all boxes")
        editMenu.Append(202, "&De-select All\tCtrl-D", "Uncheck all boxes")
        editMenu.Append(203, "&Select bad zip codes\tCtrl-B", "Check boxes of items with bad zip codes")
        # Add menu to the menu bar
        menuBar.Append(editMenu, "&Edit")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.fileExit, id=104)
        self.Bind(wx.EVT_MENU, self.allSelect, id=201)
        self.Bind(wx.EVT_MENU, self.allDeselect, id=202)
        self.Bind(wx.EVT_MENU, self.badSelect, id=203)
       
        self.CreateStatusBar(1)
        log=Log()
        self.win = myNB(self, -1, log)

    def fileExit(self, event): 
        self.Close(True)
        sys.exit()

    def allSelect(self, event):
        curPage = self.win.GetCurrentPage()
        num = curPage.GetItemCount()
        for i in range(num):
            curPage.CheckItem(i)

    def allDeselect(self, event):
        curPage = self.win.GetCurrentPage()
        num = curPage.GetItemCount()
        for i in range(num):
            curPage.CheckItem(i, False)

    def badSelect(self, event):
        curPage = self.win.GetCurrentPage()
        num = curPage.GetItemCount()
        for i in range(num):
            if curPage.GetItem(i,3).GetText() == "False":
                curPage.CheckItem(i)



class MyApp(wx.App):
    def OnInit(self):
        f = myFrame(None, -1, "FSRZip9 - Zip+4 database check utility",wx.Size(700,600))
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
        
        self.Hdr = ["Office#", "ID", "Name", "Zip+4 OK?", "Phone", "Address", "Address1", "City", "State", "Zip"]
        self.loadDirect()
        self.loadGroups()
        self.loadDoctors()
        self.loadReferrals()
        self.loadFacilities()
        self.loadInsurances()
        self.loadLabs()
        self.Cleanup()
        
    def Cleanup(self):
        Global.dataLoaded = True
        self.Close(True)

    def loadDirect(self):
        Global.serialID = 0
        Global.offices = parseDirectDat(urllib.url2pathname(str(Global.cfgFile["directDat"])))
        
    def loadGroups(self):
        msg = 'Loading groups...'
        Global.GroupList = [["Office#", "ID", "Name", "Zip+4 OK?", "Phone", "Address", "City", "State", "Zip"]]
        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "Group"):
                Global.serialID +=1
                obj.ID=str(Global.serialID)
                if len(obj.Name) > 2: #skip empty groups - e.g. pages 2 and 3 if not in use...
                    msgNow = msg + ' ' + str(obj.ID)
                    self.log.write(msgNow)
                    Global.GroupList.append([str(num), "", obj.Name, str(len(obj.Zip)==9), obj.Phone, obj.Street, obj.City, obj.State, obj.Zip])
            
    def loadDoctors(self):
        msg = 'Loading doctors...'
        Global.DoctorList =  [["Office#", "ID", "Name", "Zip+4 OK?", "Phone", "Address", "City", "State", "Zip"]]

        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "Doctor"):
                if (not (len(obj.ID)<1)) and (len(obj.Name) > 2): 
                    msgNow = msg + ' ' + str(obj.ID)
                    self.log.write(msgNow)
                    Global.DoctorList.append([str(num), obj.ID, obj.Name, str(len(obj.Zip)==9), obj.Phone, obj.Street, obj.City, obj.State, obj.Zip])

    def loadReferrals(self):
        msg ='Loading referral sources...'
        Global.ReferralList =  [["Office#", "ID", "Name", "Zip+4 OK?", "Phone", "Address", "Address1", "City", "State", "Zip"]]
        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "ReferralSource"):
                if (obj.ID[0]=='P') and (len(obj.Name) > 2): 
                    msgNow = msg + ' ' + str(obj.ID)
                    self.log.write(msgNow)
                    Global.ReferralList.append([str(num), obj.ID, obj.Name, str(len(obj.Zip)==9), obj.Phone, obj.Address, obj.Address1, obj.City, obj.State, obj.Zip])

    def loadFacilities(self):
        msg = 'Loading facilities...'
        Global.FacilityList =  [["Office#", "ID", "Name", "Zip+4 OK?", "Phone", "Address", "City", "State", "Zip"]]
        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "Facility"):
                if (len(obj.Name) > 2):
                    msgNow = msg + ' ' + str(obj.ID)
                    self.log.write(msgNow)
                    Global.FacilityList.append([str(num), obj.ID, obj.Name, str(len(obj.Zip)==9), obj.Phone, obj.Street, obj.City, obj.State, obj.Zip])

    def loadInsurances(self):
        msg = 'Loading insurances...'
        Global.InsuranceList =  [["Office#", "ID", "Name", "Zip+4 OK?", "Phone", "Address", "Address1", "City", "State", "Zip"]]
        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "Insurance"):
                if (len(obj.Name) > 2):
                    msgNow = msg + ' ' + str(obj.ID)
                    self.log.write(msgNow)
                    Global.InsuranceList.append([str(num), obj.ID, obj.Name, str(len(obj.Zip)==9), obj.Tel, obj.Street, obj.Address1, obj.City, obj.State, obj.Zip])

    def loadLabs(self):
        msg = 'Loading labs...'
        Global.LabList =  [["Office#", "ID", "Name", "Zip+4 OK?", "Phone", "Address", "City", "State", "Zip"]]
        for num, off in Global.offices.iteritems():
            msg = msg + ' Off' + str(num) + '...'
            self.log.write(msg)
            for obj in RecordGenerator(off, "Laboratory"):
                if not ((len(obj.ID)<1) or (len(obj.MedicareID)<3)) and (len(obj.Name) > 2):
                    msgNow = msg + ' ' + str(obj.ID)
                    self.log.write(msgNow)
                    Global.LabList.append([str(num), obj.ID, obj.Name, str(len(obj.Zip)==9), obj.Phone, obj.Street, obj.City, obj.State, obj.Zip])
        if len(Global.LabList) ==1:
            Global.LabList.append(["None", "0", "None", "False", "N/A", "None", "None", "Zip"])

    def handleCancel(self, event): 
        self.Close(True)
        sys.exit()
class SplashApp(wx.App):
    def OnInit(self):
        splash = SplashFrame(None, -1, "FSRZip9 - loading data, please wait...",wx.Size(450,200))
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

    if not (os.path.exists(str(Global.cfgFileName)) and os.path.exists(urllib.url2pathname(str(Global.cfgFile["directDat"])))):
        Global.cfgDone = False
        cfg = ConfigApp(0)
        cfg.MainLoop()
        if (Global.cfgDone == 2):
            dlg = wx.MessageDialog(None, "I can't go on like this!  Try again, and next time tell me what I need to know!",
                            "Abort! Abort!", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            sys.exit()

    Global.dataLoaded               = False
    sploosh = SplashApp(0)
    sploosh.MainLoop()
    if not Global.dataLoaded: sys.exit()
    app = MyApp(0)
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
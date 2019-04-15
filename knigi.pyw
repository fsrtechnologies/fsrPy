import wx, sys, os, time
import wx.lib.customtreectrl as CT
import wx.lib.delayedresult as delayedresult

import urllib
from urllib2 import Request, urlopen, URLError

from BeautifulSoup import BeautifulSoup
from pprint import pprint
from pubsub import pub
import locale
try:
    import wx.lib.inspection
except ImportError: pass
        
class myTreeItemData(object):
    def __init__(self, webPath=None, localPath=None):
        self.webPath = webPath
        self.localPath = localPath
        
class Log(object):
    """Log output is redirected to the status bar of the containing frame."""
    def WriteText(self,text_string):
        self.write(text_string)
    def __call__(self,text_string):
        wx.GetApp().GetTopWindow().SetStatusText(text_string)
    def write(self,text_string):
        wx.GetApp().GetTopWindow().SetStatusText(text_string)
        
#---GUI

class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Audiobooks", size=(400,600))
        self.CreateStatusBar(1)
        self.log=Log()
        self.SafeToExit = True
        
        pnl = wx.Panel(self)
        outerMost = wx.BoxSizer(wx.VERTICAL)
        self.tree = CT.CustomTreeCtrl(pnl, 
            style= wx.SUNKEN_BORDER| CT.TR_HAS_BUTTONS | CT.TR_AUTO_CHECK_CHILD | CT.TR_AUTO_CHECK_PARENT | CT.TR_AUTO_TOGGLE_CHILD )
        self.root = self.tree.AddRoot("Authors")
        boxInner = wx.BoxSizer(wx.HORIZONTAL)

        self.btnGo = wx.Button(pnl, wx.ID_OK, "Load Authors")
        boxInner.Add(self.btnGo, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnGo, self.btnGo)
        self.btnCancel = wx.Button(pnl, wx.ID_CANCEL, "Exit")
        boxInner.Add(self.btnCancel, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.btnCancel)
        outerMost.Add(boxInner, 0, wx.ALIGN_CENTER)

        self.abortEvent = delayedresult.AbortEvent()

        #self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivated, self.tree)
     
        self.tree.Expand(self.root)
        outerMost.Add(self.tree, 10, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL)
        self.Gauge1 = wx.Gauge(pnl, -1, 50)
        outerMost.Add(self.Gauge1, 0, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL)
        self.Gauge2 = wx.Gauge(pnl, -1, 50)
        outerMost.Add(self.Gauge2, 0, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL)
        
        self.eventBox = wx.TextCtrl(pnl, -1, "", style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        outerMost.Add(self.eventBox, 2, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL)
        #---Cleanup
        pnl.SetSizer(outerMost)

    def __call__(self):
        pass
        
#---getting authors      
    def AddTreeNodes(self, parentItem=None, preWeb="", depth=0, preLocal="", abortEvent=None):
        preWeb = preWeb.encode('utf8')
        data = self.ReadFromWeb(preWeb)
        soup = BeautifulSoup(data)
        if depth==0:
            authCount = 0
            for anchor in soup.findAll('a', href=True):
                hRef = anchor['href']
                if ((hRef[:4] == u'http') or (hRef[0] == u'?') or (hRef[0] == u'/')): # if it starts with / it's the Parent dir
                    continue
                if hRef[-1] == u'/':
                    authCount += 1
            self.Gauge1.SetRange(200)
            self.Gauge2.SetRange(authCount)
            self.Gauge2.SetValue(0)

        for anchor in soup.findAll('a', href=True):          
            hRef = anchor['href']
            if ((hRef[:4] == u'http') or (hRef[0] == u'?') or (hRef[0] == u'/')): # if it starts with / it's the Parent dir
                continue
            data = myTreeItemData(preWeb+hRef, preLocal+hRef)
            newItem = self.tree.AppendItem(parentItem, anchor.next, ct_type=1, wnd=None, image=-1, selImage=-1, data=data)
            self.Gauge1.Pulse()
            if hRef[-1] == u'/' : #this is a subdirectory
                if depth==0:
                    pub.sendMessage("author", msg=anchor.next)
                    self.Gauge2.SetValue(self.Gauge2.GetValue() +1)
                if not self.abortEvent():
                    self.AddTreeNodes(parentItem=newItem, preWeb=preWeb+hRef, depth=depth+1, preLocal=preLocal+anchor.next, abortEvent=abortEvent)

    def ReadFromWeb(self, addy):
        Success, Retries = False, 0
        while not Success and not self.abortEvent():
            try:
                data = urlopen(addy).read() 
                Success = True
            except URLError, e:
                pub.sendMessage("trouble", msg=addy + "- Ooops")
                if hasattr(e, 'reason'):
                    pub.sendMessage("trouble", msg='\nWe failed to reach a server. ')
                    pub.sendMessage("trouble", msg='Reason: ' + e.reason)
                elif hasattr(e, 'code'):
                    pub.sendMessage("trouble", msg='\nThe server couldn\'t fulfill the request.')
                    pub.sendMessage("trouble", msg='Error code: ' + e.code)
                Retries +=1
                if Retries > 2: 
                    pub.sendMessage("trouble", msg='\nGiving up on' + addy)
                    return
                continue
        return data
        
#---getting books
    def DownloadBooks(self, jobID=None, abortEvent=None):
        totalBooks, curBooks = 0, 0
        for item in self.GetMeCheckedItems(self.tree, self.root):
            totalBooks +=1
        self.Gauge2.SetRange(totalBooks)
        for item in self.GetMeCheckedItems(self.tree, self.root):
            if self.abortEvent(): 
                break
            self.SafeToExit = False
            pub.sendMessage("book", msg=self.GetItemText(item))
            itemData = self.GetItemData(item)
            if not os.path.isdir(os.path.dirname(itemData.localPath)):
                try:
                    os.makedirs(os.path.dirname(itemData.localPath))
                except:
                    pub.sendMessage("trouble", "\nCouldn't create folder: "+itemData.localPath)
            try:
                urllib.urlretrieve(itemData.webPath, itemData.localPath, reporthook=self.UpdateProgress)
            except:
                pub.sendMessage("trouble", "\nCouldn't download: "+itemData.localPath, sys.exc_type, ":", sys.exc_value)
            finally:
                self.SafeToExit = True
                self.btnCancel.Enable(True)
            curBooks +=1
            self.Gauge2.SetValue(curBooks)
            if self.abortEvent(): 
                break

    def GetMeCheckedItems(self, tree, treeItem):
        if not treeItem.HasChildren():
            if treeItem.IsChecked():
                yield treeItem
        else:
            for subItem in treeItem.GetChildren():
                for item in self.GetMeCheckedItems(tree, subItem):
                    yield item
                    
    def UpdateProgress(self, blocksSoFar=None, blockSize=None, totalSize=None):
        if totalSize == -1:
            self.Gauge1.Pulse()
        else:
            self.Gauge1.SetRange(totalSize / blockSize)
            self.Gauge1.SetValue(blocksSoFar)
            
#--- tree stuff
    def GetItemText(self, item):
        if item:
            return self.tree.GetItemText(item)
        else:
            return ""
        
    def GetItemData(self, item):
        if item:
            return self.tree.GetItemPyData(item)
        else:
            return ""

#---button handlers        
    def OnGo(self, evt):
        self.btnGo.Enable(False)
        self.btnCancel.Enable(True)
        self.abortEvent.clear()
        self.btnCancel.Label = "Cancel"
        btn = evt.GetEventObject().Label
        if btn == "Load Authors":
            self.btnGo.Label = "Download"
            self.jobID = 1
            pub.sendMessage("trouble", msg="\nGetting authors...")
            delayedresult.startWorker(self._resultConsumer, self.AddTreeNodes, 
                                  wargs=(self.root, 'http://audiobooks.ulitka.com/', 0, "/Music/Audiobooks/knigi/", self.abortEvent), 
                                  jobID=self.jobID)
                               
        elif btn == "Download":
            self.jobID = 2
            pub.sendMessage("trouble", msg="\nDownloading books...")
            delayedresult.startWorker(self._resultConsumer, self.DownloadBooks, 
                                  wargs=(self.jobID, self.abortEvent), 
                                  jobID=self.jobID)
                                
    def OnCancel(self, evt):
        btn = evt.GetEventObject().Label
        if btn == "Cancel":
            self.abortEvent.set()
            if not self.SafeToExit:
                self.btnCancel.Enable(False)
            self.btnGo.Enable(True)
            self.btnCancel.Label = "Quit"
            self.Gauge1.SetRange(50)
            self.Gauge2.SetRange(50)
            self.Gauge1.SetValue(0)
            self.Gauge2.SetValue(0)

        if btn in ("Exit", "Quit"):
            while not self.SafeToExit:
                time.sleep(1)
            self.Close(True)
            sys.exit()
            
#---PubSub stuff
    def OnAuthor(self,msg):
        self.log.write("Current author:  " + msg)
        self.Update()
    def OnBook(self,msg):
        self.log.write("Current book:  " + msg)
        self.Update()
    def OnTrouble(self,msg):
        self.eventBox.ChangeValue(self.eventBox.GetValue() + msg)
        self.Update()

    def _resultConsumer(self, delayedResult):
        pub.sendMessage("trouble", msg="... completed.")
        self.tree.Expand(self.root)
        self.btnGo.Label = "Download"
        self.btnGo.Enable(True)
        self.btnCancel.Label = "Quit"
        self.Gauge1.SetRange(50)
        self.Gauge2.SetRange(50)
        self.Gauge1.SetValue(0)
        self.Gauge2.SetValue(0)

app = wx.PySimpleApp(None)
frame = TestFrame()
frame.Show()
pub.subscribe(frame, pub.ALL_TOPICS)
pub.subscribe(frame.OnTrouble, 'trouble')
pub.subscribe(frame.OnAuthor, 'author')
pub.subscribe(frame.OnBook, 'book')

#wx.lib.inspection.InspectionTool().Show()

app.MainLoop()
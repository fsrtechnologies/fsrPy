import wx, sys
from types import *
from wx.lib.mixins.listctrl import ColumnSorterMixin, CheckListCtrlMixin, ListCtrlAutoWidthMixin

class SortedCheckList(wx.ListCtrl, CheckListCtrlMixin, ColumnSorterMixin, ListCtrlAutoWidthMixin):
    '''
    Combines the CheckListCtrl and ColumnSorter mixins for the ListCtrl widget.
    Also modularizes management of columns and headers.  Unfortunately this adds some constraints:
        - If the data structure is a dictionary: 
            - it must have a numeric index
            - key 0 must correspond to the header record 
        - If the data structure is a list: 
            - the first item in the list must be the header record 
    One drawback of making column creation automatic is that column width and style are set to defaults.
    Future versions may add more control...
    '''
    def __init__(self, parent, inThing, log=None):
        self.log = log
        header = []
        if isinstance(inThing, DictType): # inThing is a dictionary
            if inThing.has_key(0):
                header = inThing[0]
                del inThing[0]
            self.thing = inThing
        elif isinstance(inThing, ListType):
            header = inThing[0]
            del inThing[0]
            self.thing  = {}
            for num, item in enumerate(inThing):
                self.thing[num+1] = item   # needs to be 1-based, not 0-based
                
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
        ColumnSorterMixin.__init__(self, len(self.thing))
        self.itemDataMap = self.thing
        Widths = []
        for colNum, colData in enumerate(header):
            self.InsertColumn(colNum, colData)
            Widths.append(len(colData))
        for key, data in self.thing.items():
            for colNum, colData in enumerate(data):
                Widths[colNum] = max(Widths[colNum], len(str(colData)), 5) # get max length for each column, at least 5
                if (colNum==0):
                    index = self.InsertStringItem(sys.maxint, data[0])
                    tmpFont = self.GetItemFont(index)
                else:
                    self.SetStringItem(index, colNum, str(colData))
            self.SetItemData(index, key)
        dc = wx.ScreenDC()
        dc.SetFont(tmpFont)
        for colNum, colWidth in enumerate(Widths):
            width, h = dc.GetTextExtent('N'*colWidth) # capital W is too wide, capital I too narrow 
            self.SetColumnWidth(colNum, width)
            
        
        # for wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        # for wxGTK
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)



    def GetListCtrl(self):
        return self

    def __OnColClick(self, evt):
        oldCol = self._col
        self._col = col = evt.GetColumn()
        self._colSortFlag[col] = int(not self._colSortFlag[col])
        self.GetListCtrl().SortItems(self.GetColumnSorter())
        self.OnSortOrderChanged()

    def OnRightClick(self, event):
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popupID4 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)

        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupID1, "Select highlighted items")
        menu.Append(self.popupID2, "Deselect highlighted items")
        menu.Append(self.popupID3, "Select all")
        menu.Append(self.popupID4, "Deselect all")

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()


    def OnPopupOne(self, event):
        index = self.GetFirstSelected()
        while index != -1:
            self.CheckItem(index)
            index = self.GetNextSelected(index)

    def OnPopupTwo(self, event):
        index = self.GetFirstSelected()
        while index != -1:
            self.CheckItem(index, False)
            index = self.GetNextSelected(index)

    def OnPopupThree(self, event):
        num = self.GetItemCount()
        for i in range(num):
            self.CheckItem(i)

    def OnPopupFour(self, event):
        num = self.GetItemCount()
        for i in range(num):
            self.CheckItem(i, False)


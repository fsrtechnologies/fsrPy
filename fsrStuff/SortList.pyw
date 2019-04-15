import wx, sys#, images
from types import *
from wx.lib.mixins.listctrl import ColumnSorterMixin, ListCtrlAutoWidthMixin


class SortedList(wx.ListCtrl, ColumnSorterMixin, ListCtrlAutoWidthMixin):
    '''
    Modularize management of columns and headers.  Unfortunately this adds some constraints:
        - If the data structure is a dictionary: 
            - it must have a numeric index
            - key 0 must correspond to the header record 
        - If the data structure is a list: 
            - the first item in the list must be the header record 
    One drawback of making column creation automatic is that column width and style are set to defaults.
    Future versions may add more control...
    '''
    def __init__(self, parent, inThing, log=None):
        wx.ListCtrl.__init__(self, parent, -1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_REPORT 
                                 | wx.BORDER_NONE
                                 | wx.WANTS_CHARS
                                 )
        ListCtrlAutoWidthMixin.__init__(self)

        self.log = log

        header = []  # we'll grab zero item from inThing and use it as header
        if isinstance(inThing, DictType): # inThing is already a dictionary
            if inThing.has_key(0):
                header = inThing[0]
                del inThing[0]
            self.thing = inThing
        elif isinstance(inThing, ListType): #inThing is a list, so make a dictionary out of it
            header = inThing[0]
            del inThing[0]
            self.thing  = {}
            for num, item in enumerate(inThing):
                self.thing[num+1] = item   # needs to be 1-based, not 0-based
                
        ColumnSorterMixin.__init__(self, len(self.thing)) # number of columns equals width of header record
        list = self.GetListCtrl()
        if not list:
            raise ValueError, "No wx.ListCtrl available"
        list.Bind(wx.EVT_LIST_COL_CLICK, self.__OnColClick, list)

        self.itemDataMap = self.thing
        self.Widths = []
        for colNum, colData in enumerate(header):
            self.InsertColumn(colNum, colData)
            self.Widths.append(len(colData))
        self.refreshList(init=True)
        dc = wx.ScreenDC()
        #dc.SetFont(self.tmpFont)
        for colNum, colWidth in enumerate(self.Widths):
            width, h = dc.GetTextExtent('N'*colWidth) # capital W is too wide, capital I too narrow 
            self.SetColumnWidth(colNum, width)
               
    def __OnColClick(self, evt):
        oldCol = self._col
        self._col = col = evt.GetColumn()
        self._colSortFlag[col] = int(not self._colSortFlag[col])
        self.GetListCtrl().SortItems(self.GetColumnSorter())
        self.OnSortOrderChanged()
    
    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def refreshList(self, init = False):
        for key, data in self.thing.items():
            for colNum, colData in enumerate(data):
                if init:  # first time only - otherwise just update existing items
                    self.Widths[colNum] = max(self.Widths[colNum], len(str(colData)), 5) # get max length for each column, at least 5
                    if (colNum==0):
                        index = self.InsertStringItem(sys.maxint, data[0])
                        self.tmpFont = self.GetItemFont(index)
                else: 
                    index = key -1
                self.SetStringItem(index, colNum, str(colData))
            self.SetItemData(index, key)


    def GetListCtrl(self):
        return self

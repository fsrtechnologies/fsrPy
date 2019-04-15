from decimal import Decimal
from pprint import pprint
import wx, sys, os
import wx.lib.filebrowsebutton as filebrowse
from configobj import ConfigObj
from validate import Validator
from ObjectListView import ObjectListView, ColumnDefn
import amara
import Ft.Lib.Uri as uri
import wx.lib.dialogs
try:
    import wx.lib.inspection
except ImportError:
    pass

try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO

class Global(object):
    """Generic container for shared variables."""
    cfgFileName = os.getcwd() + os.sep + 'sPxml.ini'
   
    tmpStr = """[Current]
    InHist = string_list(default=None)
    OutHist = string_list(default=None)
    AutoName = boolean(default=True)
    SuppressZeroBal = boolean(default=False)
    
    """
    cfgSpec = StringIO.StringIO(tmpStr)
    cfgFile = ConfigObj(cfgFileName, 
                configspec=cfgSpec, raise_errors=True, write_empty_values = True, 
                create_empty=True, indent_type='    ', list_values = True)
    vtor = Validator()
    
class Log(object):
    """Log output is redirected to the status bar of the containing frame."""
    def WriteText(self,text_string):
        self.write(text_string)
    def write(self,text_string):
        wx.GetApp().GetTopWindow().SetStatusText(text_string)

class StmtObj(object):
    def __init__(self, acctNum, patName, balAmt, balFwd, stmtXML):
        self.acctNum  = acctNum
        self.patName  = patName
        self.balAmt   = balAmt
        self.balFwd   = balFwd
        self.stmtXML  = stmtXML
        
class SummaryDialog(wx.Dialog):
    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=(50,50),
            style=wx.DEFAULT_DIALOG_STYLE, text=""):
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style)

        sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer.Add(wx.StaticText(self, -1, "\"Regular\" statements (containing detail):"))

        text = wx.TextCtrl(self, -1, text, size=wx.Size(775,500), style=wx.TE_MULTILINE|wx.TE_AUTO_SCROLL|wx.TE_DONTWRAP)
        font1 = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        text.SetFont(font1)

        sizer.Add(text, 1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)


        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)



class MyFrame(wx.Frame):
    ID_LOAD = wx.NewId()
   
    def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, size=size, style=style)
        self.CreateStatusBar(1)
        self.log=Log()
        Global.stmtList = []
 
        pnl = wx.Panel(self)
        
        #---Create checkboxes
        
        Opts = [
            {"Name": "AutoName", "Label":"Auto-name output file?", "Tip":"Do you want to automatically name the output file by adding 'gw-' to the beginning?"},
            {"Name": "SuppressZeroBal", "Label":"Suppress zero balances?", "Tip":"Do you want to skip any charges that already have zero balances?"}]
        self.Options = {}
        for opt in Opts:
            nom, lbl, tip = opt["Name"], opt["Label"], opt["Tip"]
            self.Options[nom] = wx.CheckBox(pnl, -1, lbl, style=wx.ALIGN_LEFT, name=nom)
            self.Options[nom].SetToolTip(wx.ToolTip(tip))
            self.Options[nom].SetValue(Global.cfgFile['Current'][nom])
            self.Bind(wx.EVT_CHECKBOX, self.OnChange, self.Options[nom])
        
        fpOpt = {
            "In": {"Label":"Original: ", "Title":"Tell me where to find the original file", "Mode":wx.OPEN},
            "Out":{"Label":"Converted:", "Title":"Tell me where to save the converted file", "Mode":wx.SAVE}, }
        self.filePicker ={}
        for option, detail in fpOpt.iteritems():
            self.filePicker[option] = filebrowse.FileBrowseButtonWithHistory(pnl, -1, 
                    labelText=detail["Label"], fileMask='*.*', 
                    fileMode=detail["Mode"], dialogTitle=detail["Title"], 
                    changeCallback=lambda x, option=option: self.fpCallback(x, option))
            if Global.cfgFile['Current'].has_key(option+'Hist'):
                try:                            #is it a single item, 
                    tmpList = Global.cfgFile['Current'][option + "Hist"].split(',')
                except AttributeError:          # or a list?
                    tmpList = Global.cfgFile['Current'][option + "Hist"]
                self.filePicker[option].callCallback = False
                self.filePicker[option].SetHistory(tmpList, 0)
                self.filePicker[option].callCallback = True

        outerMost = wx.BoxSizer(wx.VERTICAL)
        
        #---File locations
        box2 = wx.StaticBox(pnl, -1, "Location of statement files:")
        boxMidLeft = wx.StaticBoxSizer(box2, wx.VERTICAL)

       
        boxMidLeft.Add(self.filePicker["In"], 0, wx.ALIGN_LEFT|wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        boxMidLeft.Add(self.filePicker["Out"], 0, wx.ALIGN_LEFT|wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        boxMidLeft.Add(self.Options["AutoName"], 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 5)
        boxMidLeft.Add(self.Options["SuppressZeroBal"], 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 5)
        outerMost.Add(boxMidLeft, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 10)

        #---Buttons
        
        boxBtns = [wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.HORIZONTAL)]
        Buttons = [
            {"Name": "Load",     "Tip": "Click here to read in Prime statements from the \"Original\" file."},
            {"Name": "Save",     "Tip": "After you have selected the statements you want, click here to save them to the \"Converted\" file."},
            {"Name": "Cancel",   "Tip": "Click here to exit without doing anything."},
            {"Name": "Check All","Tip": "Click here to select all patients."},
            {"Name": "Clear All","Tip": "Click here to de-select all patients."},
            ]
        self.Button ={}
        tmpCount = 0
        for btn in Buttons:
            self.Button[btn["Name"]] = wx.Button(pnl, -1, label=btn["Name"], name=btn["Name"])
            self.Button[btn["Name"]].SetToolTip(wx.ToolTip(btn["Tip"]))
            boxBtns[tmpCount / 3].Add(self.Button[btn["Name"]], 0, wx.ALIGN_CENTER|wx.ALL)
            boxBtns[tmpCount / 3].Add((10,10), 0, wx.EXPAND)
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.Button[btn["Name"]])
            tmpCount +=1
        outerMost.Add(boxBtns[0], 0, wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, 10)
        outerMost.Add(wx.StaticLine(pnl), 0, wx.EXPAND)
        outerMost.Add(boxBtns[1], 0, wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, 5)

        #---List
        self.oLV = ObjectListView(pnl, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        
        simpleColumns = [
            ColumnDefn("Account", valueGetter="acctNum", minimumWidth= 60, maximumWidth=100),
            ColumnDefn("Name", valueGetter="patName", minimumWidth=100, maximumWidth=300, isSpaceFilling=True),
            ColumnDefn("Balance", "right", valueGetter="balAmt", minimumWidth=50, maximumWidth=100),
            ColumnDefn("BalFwd", "right", valueGetter="balFwd", minimumWidth=50, maximumWidth=100)
            ]

        def rowFormatter(listItem, stmt):
            if stmt.balFwd != 0:
                listItem.SetTextColour(wx.RED)

        self.oLV.rowFormatter = rowFormatter
        self.oLV.SetColumns(simpleColumns)
        self.oLV.CreateCheckStateColumn()
        self.oLV.SetObjects(Global.stmtList)


        outerMost.Add(self.oLV, 1, wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, 5)
               
        pnl.SetSizer(outerMost)



    def fpCallback(self, evt, option):
        value = evt.GetString()
        if not value:
            return()
        if option == "In" and Global.cfgFile['Current']['AutoName']:
            self.filePicker['Out'].SetValue(os.path.split(self.filePicker['Out'].GetValue())[0] + os.sep + "gw-" + os.path.split(self.filePicker['In'].GetValue())[1])
            
        if (self.filePicker["Out"].GetValue() == self.filePicker["In"].GetValue()):
            dlg = wx.MessageDialog(None, "You're asking me to over-write the original file.  You sure about that?", 
                "You have chosen... oddly.", 
                style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            response = dlg.ShowModal()
            dlg.Destroy()
            if (response == wx.ID_NO):
                return()
        history = self.filePicker[option].GetHistory()
        if value in history:  # if it already existed, remove it
            history.pop(history.index(value))
        history.insert(0, value)  # either way, insert it at the head of the list
        while len(history) > 10: # pop items off the end until history is x items long... 
            history.pop()
        self.filePicker[option].SetHistory(history)
        self.filePicker[option].GetHistoryControl().SetStringSelection(value)
        Global.cfgFile['Current'][option+'Hist'] = history
        Global.cfgFile.write()

    def OnChange(self, evt):
        option = evt.GetEventObject().Name
        Global.cfgFile['Current'][option] = evt.GetEventObject().GetValue()
        Global.cfgFile.write()
        if option == "SuppressZeroBal":
            self.oLV.DeleteAllItems()
            #self.oLV.Refresh()

    def OnClick(self, event):
        btn = event.GetEventObject().Name
        if (btn == "Cancel"):
            self.Close(True)
            sys.exit()
        if (btn == "Load"):
            inPathStr = r'file:' + str(self.filePicker["In"].GetValue())
            self.log.write('About to convert %s' % uri.UriToOsPath(inPathStr))
            if not (os.path.exists(uri.UriToOsPath(inPathStr))):
                self.log.write("Select a valid source file!")
                return
            else:
                Global.stmtList = self.GenStmt(inPathStr)
                self.log.write('Loaded %s statements' % len(Global.stmtList))
                self.oLV.SetObjects(Global.stmtList)
        if (btn == "Check All"):
            unchecked = [x for x in self.oLV.modelObjects if not self.oLV.IsChecked(x)]           
            for item in unchecked :
                self.oLV.Check(item)
            self.oLV.RefreshObjects(unchecked)
        if (btn == "Clear All"):
            checked = self.oLV.GetCheckedObjects()
            for item in checked:
                self.oLV.Uncheck(item)
            self.oLV.RefreshObjects(checked)


        if (btn == "Save"):
            if len(self.oLV.GetCheckedObjects()) == 0:
                self.log.write('No statements selected - Nothing to save!')
                return()

            self.Button["Cancel"].SetLabel("Exit")
            outPathStr = r'file:' + str(self.filePicker["Out"].GetValue())
            outPathStr = str(self.filePicker["Out"].GetValue())
            outDoc = amara.create_document(u"statement_batch")
            outList = [ "   Account   Name                                       Balance    BalFwd",
                        "========================================================================="]
            for item in self.oLV.GetCheckedObjects():
                outDoc.statement_batch.xml_append(item.stmtXML)
                outList.append("%s%s   %s%s%s%s%s%s" % (" "*(10-len(item.acctNum)), item.acctNum, 
                                                        item.patName, " "*(40-len(item.patName)), 
                                                        " "*(10-len(str(item.balAmt))), str(item.balAmt), 
                                                        " "*(10-len(str(item.balFwd))), str(item.balFwd)))
            outFile = open(outPathStr,'w+b')
            outDoc.xml(outFile,indent=u'yes')
            outFile.close()
            self.log.write('Saved %s statements' % len(self.oLV.GetCheckedObjects()))

            dlg = SummaryDialog(self, -1, "Summary of converted statements", 
                                text="\n".join(outList), size=wx.Size(750,500), 
                style=wx.OK|wx.CAPTION|wx.RESIZE_BORDER|wx.CLOSE_BOX|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.SYSTEM_MENU)
            font1 = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier')
            dlg.SetFont(font1)
            response = dlg.ShowModal()
            dlg.Destroy()

    def GenStmt(self,inPathStr):
        stmtList = []
        inDoc = amara.parse(inPathStr)
        outDoc = amara.create_document(u"statement_batch")

        for stmt in inDoc.statements.statement:
            preBalOnly = False
            if len(stmt.row.xml_children) == 0:
                preBalOnly = True
            outStmt = outDoc.xml_create_element(u"statement")
            outElem = outDoc.xml_create_element(u"practice_name", content=stmt.clinic.name)
            outStmt.xml_append(outElem)
            
            if preBalOnly:
                outElem = outDoc.xml_create_element(u"patient_name", content=stmt.to.name)
            else:
                outElem = outDoc.xml_create_element(u"patient_name", content=stmt.row.charge.patient)
            outStmt.xml_append(outElem)

            outElem = outDoc.xml_create_element(u"remit_to", 
                                            attributes={u"name": stmt.doctor.name, 
                                                        u"address1": stmt.clinic.address,
                                                        u"address2":u"",
                                                        u"city": stmt.clinic.city.split(",")[0].strip(),
                                                        u"state": stmt.clinic.city.split(",")[1].strip(),
                                                        u"zip": stmt.clinic.city.split(",")[2].strip()})
            outStmt.xml_append(outElem)
            
            outElem = outDoc.xml_create_element(u"make_payment_to", content=stmt.doctor.name)
            outStmt.xml_append(outElem)

            outElem = outDoc.xml_create_element(u"recipient", 
                                            attributes={u"name": stmt.to.name, 
                                                        u"address1": stmt.to.address,
                                                        u"address2": stmt.to.address2,
                                                        u"city": stmt.to.city.split(",")[0].strip(),
                                                        u"state": stmt.to.city.split(",")[1].strip()[:2],
                                                        u"zip": stmt.to.city.split(",")[1].strip()[3:]})
            outStmt.xml_append(outElem)
            
            outElem = outDoc.xml_create_element(u"accept_credit_cards", content=u"Yes")
            outStmt.xml_append(outElem)
           
            outElem = outDoc.xml_create_element(u"cards_accepted", content=u"MasterCard, Visa, American Express")
            outStmt.xml_append(outElem)
           
            outElem = outDoc.xml_create_element(u"statement_date", content=stmt.date)
            outStmt.xml_append(outElem)
           
            outElem = outDoc.xml_create_element(u"billing_numbers", content=stmt.acct.number)
            outStmt.xml_append(outElem)
            totChg = Decimal(0)
            totPay = Decimal(0)
            totAdj = Decimal(0)
            totDis = Decimal(0)
            totW_O = Decimal(0)
            dirtyChg = False
            supPress = False  # "suppress this line" - best name I could think of for now
                
            for e in stmt.row.xml_children:
                if isinstance(e, unicode): # don't try to process element separators!
                    continue
                if e.nodeName == u"charge":
                    #print('Charge!')
                    if dirtyChg:  # if a charge record is already open, close it
                        chgElem.xml_append(sbtElem)
                        chgElem.xml_append(sbbElem)
                        outStmt.xml_append(chgElem)
                    if Global.cfgFile["Current"]["SuppressZeroBal"]:
                        if e.balance == "0.00":
                            supPress = True
                            dirtyChg = False
                            continue
                    supPress = False
                    dirtyChg = True
                    
                    thisChg = Decimal(e.charge)
                    totChg += thisChg
                    chgElem = outDoc.xml_create_element(u"charge", 
                                            attributes={u"code": e.procedure, 
                                                        u"description": e.description,
                                                        u"date": e.date,
                                                        u"amount": e.charge,
                                                        u"deductible": e.deductible
                                                        })
                    if e.payment == u"0.00":
                        thisPay = Decimal(0)
                    else:
                        thisPay = -1 * Decimal(e.payment)
                    if e.adjustment == u"0.00":
                        thisAdj = Decimal(0)
                    else:
                        thisAdj = -1 * Decimal(e.adjustment)

                    sbtElem = outDoc.xml_create_element(u"subtotal", 
                                                attributes={u"paid": unicode("%0.2F" % thisPay), 
                                                            u"disallowed": unicode("%0.2F" % 0),
                                                            u"adjustment": unicode("%0.2F" % thisAdj),
                                                            u"writeoff": unicode("%0.2F" % 0)})
                    sbbElem = outDoc.xml_create_element(u"subbalance", content= e.balance)
                elif e.nodeName == u"creditpay":
                    #print('Pay!')
                    if supPress: 
                        continue
                    if e.payment == u"0.00":
                        thisPay = Decimal(0)
                    else:
                        thisPay = -1 * Decimal(e.payment)
                    totPay += thisPay

                    payElem = outDoc.xml_create_element(u"payment", 
                                                attributes={u"payer": stmt.insurance.code, 
                                                            u"date": e.date,
                                                            u"paid": unicode("%0.2F" % thisPay)})
                    chgElem.xml_append(payElem)
                elif e.nodeName == u"creditadj":
                    #print('Adjust!')
                    if supPress: 
                        continue
                    if e.adjustment == u"0.00":
                        thisAdj = Decimal(0)
                    else:
                        thisAdj = -1 * Decimal(e.adjustment)
                    totAdj += thisAdj

            if dirtyChg: # clean up last open charge record
                chgElem.xml_append(sbtElem)
                chgElem.xml_append(sbbElem)
                outStmt.xml_append(chgElem)
                dirtyChg = False

            if preBalOnly:
                outElem = outDoc.xml_create_element(u"total_charges", content=stmt.agedbalances.prebalance)
            else:
                outElem = outDoc.xml_create_element(u"total_charges", content=unicode(totChg))
            outStmt.xml_append(outElem)

            outElem = outDoc.xml_create_element(u"total_payment", 
                            attributes={u"paid": unicode("%0.2F" % totPay), 
                                        u"disallowed": unicode("%0.2F" % totDis),
                                        u"adjustment": unicode("%0.2F" % totAdj),
                                        u"writeoff": unicode("%0.2F" % totW_O)})
            outStmt.xml_append(outElem)

            outElem = outDoc.xml_create_element(u"patient_message", content=stmt.remark.text)
            outStmt.xml_append(outElem)

            outElem = outDoc.xml_create_element(u"balance_due", content=stmt.agedbalances.amountDue)
            outStmt.xml_append(outElem)
       
            stmtList.append(StmtObj(stmt.acct.number, stmt.to.name, Decimal(stmt.agedbalances.amountDue), Decimal(stmt.agedbalances.prebalance), outStmt))
        
        return(stmtList)

        
#----------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "subPrime XML - Statement format conversion",wx.Size(500,700))
        frame.Show()
        return True

#===============================================================================================
#      Where it all begins...
#===============================================================================================
def main(argv=None):
    if argv is None:
        argv = sys.argv

    test = Global.cfgFile.validate(Global.vtor, copy=True)
    Global.cfgFile.write()

    app = MyApp(0)
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
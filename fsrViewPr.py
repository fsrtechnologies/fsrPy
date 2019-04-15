from __future__ import print_function
#-------------------------------------------------------------------------------
# Name:        fsrViewPr
# Purpose:     Replacement for Aeroflot's "Viewpr.exe"
#
# Author:      Marc
#
# Created:     06/04/2016
# Copyright:   (c) Marc 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import argparse, os, io, wx
import  wx.lib.editor as editor
from    wx.html import HtmlEasyPrinting
import  wx.lib.printout as  printout

class Log(object):
    """Log output is redirected to the status bar of the containing frame."""
    def WriteText(self,text_string):
        self.write(text_string)
    def write(self,text_string):
        wx.GetApp().GetTopWindow().SetStatusText(text_string)

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
        self.faceName="Courier New"
        wx.Frame.__init__(self, parent, id, title, size=size, style=style)
        self.html_printer=MyPrinter()
        self.html_print=HtmlEasyPrinting(name="Printing", parentWindow=self)
        self.CreateStatusBar(1)
        self.log=Log()
        pnl = wx.Panel(self)
        bSaveTXT = wx.Button(pnl, -1, "Save as TXT", (50,90))
        self.Bind(wx.EVT_BUTTON, self.SaveTXT, bSaveTXT)
        bPrint = wx.Button(pnl, -1, "Print", (50,90))
        self.Bind(wx.EVT_BUTTON, self.Print, bPrint)
        self.ed = editor.Editor(pnl, -1, style=wx.SUNKEN_BORDER)

        boxBtns = wx.BoxSizer(wx.HORIZONTAL)
        boxBtns.Add(bSaveTXT, 0, wx.ALL, 5)
        boxBtns.Add(bPrint, 0, wx.ALL, 5)

        boxEd = wx.BoxSizer(wx.VERTICAL)
        boxEd.Add(self.ed, 1, wx.ALL|wx.GROW, 1)

        boxMain = wx.BoxSizer(wx.VERTICAL)
        boxMain.Add(boxBtns, 0, wx.ALL, 1)
        boxMain.Add(boxEd, 1, wx.ALL|wx.GROW, 1)
        pnl.SetSizer(boxMain)
        pnl.SetAutoLayout(True)
        self.ed.SetText(parse(args.inFile))
        self.ed.font = wx.Font(8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL, faceName=self.faceName)

    def SaveTXT(self, evt):
        wildcard = "Text file (*.txt)|*.txt|"        \
            "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Save file as text",
            defaultDir=os.path.join(os.path.expanduser("~"),"Desktop"),
            defaultFile="", wildcard=wildcard, style=wx.SAVE|wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            outFileName = dlg.GetPath()
            self.log.WriteText('Saving text to "%s"' % outFileName)
        with io.open(outFileName, 'w', encoding='utf8') as outFile:
            # Probably need error checking here, but...
            for line in self.ed.GetText():
                print(line, file=outFile)
        dlg.Destroy()

    def GetHtmlText(self,text):
        text = '<pre>' + text + '</pre>' # Preserve spacing
        html_text = text.replace('\n\n','<P>')     # Paragraphs
        html_text = text.replace('\n', '<BR>')     # Line breaks
        html_text = text.replace('\f', '<div style="page-break-before:always"> </div>')     # Form feeds
        return html_text

    def HPrint(self, evt):
        global frame
        text = "\n".join(self.ed.GetText())
        self.html_print.SetFonts(self.faceName, self.faceName, [4,6,7,8,9,10,11])
        self.html_print.SetStandardFonts(8)
        self.html_print.GetPageSetupData().SetMarginTopLeft((7,7))
        self.html_print.GetPageSetupData().SetMarginBottomRight((7,7))
        self.html_print.PrintText(self.GetHtmlText(text), )

    def Print(self, evt):
        prt = printout.PrintTable(self)
        prt.data = self.ed.GetText()
        prt.left_margin = 0.5
        prt.default_font_name = self.faceName
        prt.default_font = { "Name": prt.default_font_name, "Size": 8, "Colour": [0, 0, 0], "Attr": [0, 0, 0] }
        prt.text_font = { "Name": prt.default_font_name, "Size": 8, "Colour": [0, 0, 0], "Attr": [0, 0, 0] }
        prt.text_font_size = 8
        setfont = wx.Font(8, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False)
        setfont.SetFaceName(self.faceName)
        #prt.DC = prt.GetDC()
        #prt.DC.SetFont(setfont)


        prt.Print()


class MyPrinter(HtmlEasyPrinting):
    def __init__(self):
         global frame
         HtmlEasyPrinting.__init__(self,name="Printing", parentWindow=None)
    def PreviewText(self, text, doc_name):
         self.SetHeader(doc_name)
         HtmlEasyPrinting.PreviewText(self, text)
    def Print(self, text, doc_name):
         self.SetHeader(doc_name)
         self.PrintText(text, doc_name)

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "FSR-ViewPr",wx.Size(1050,750))
        frame.Show()
        return True



def parse(inFileName):
    with io.open(inFileName, 'r', encoding='cp866') as inFile:
        outFile = []
        for line in inFile.readlines():
            # Line endings in FINANSY output are not consistent...
            line = line.replace("\n","")
            line = line.replace("\r","")
            if hash(line) not in (0, 73526461): #skip over empty/blank lines
                outFile.append(line)
        return outFile

def main():
    app = MyApp(0)
    app.MainLoop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Process output of FINANSY into something more reasonable')
    parser.add_argument('inFile', nargs='?', default=r"C:\FFF\REPORT.PRN")
    args = parser.parse_args()
    main()

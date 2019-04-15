import os.path, copy
from X12STLoop import X12STLoop
from X12Utils import fixDateYYMMDD
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from GenPDFSet import GenericPDFSettings

#---Dictionaries
ackDict = {"A":"Accepted", "E":"Interchange accepted with errors", "R":"Interchange rejected/suspended"}
errDict = {"000":"Success",
             "001":"The Interchange Control Numbers in the header ISA 13 and trailer IEA02 do not match",
             "002":"Standard in ISA11 (Control Standards) is not supported",
             "003":"Version of the controls is not supported",
             "004":"Segment Terminator is Invalid2",
             "005":"Invalid Interchange ID Qualifier for Sender",
             "006":"Invalid Interchange Sender ID",
             "007":"Invalid Interchange ID Qualifier for Receiver",
             "008":"Invalid Interchange Receiver ID",
             "009":"Unknown Interchange Receiver ID",
             "010":"Invalid Authorization Information Qualifier value",
             "011":"Invalid Authorization Information value",
             "012":"Invalid Security Information Qualifier value",
             "013":"Invalid Security Information value",
             "014":"Invalid Interchange Date value",
             "015":"Invalid Interchange Time value",
             "016":"Invalid Interchange Standards Identifier value",
             "017":"Invalid Interchange Version ID value",
             "018":"Invalid Interchange Control Number value",
             "019":"Invalid Acknowledgment Requested value",
             "020":"Invalid Test Indicator value",
             "021":"Invalid Number of Included Groups value",
             "022":"Invalid Control Structure",
             "023":"Improper (Premature) End-of-File (Transmission)",
             "024":"Invalid Interchange Content (e.g., Invalid GS segment)",
             "025":"Duplicate Interchange Control Number",
             "026":"Invalid Data Element Separator",
             "027":"Invalid Component Element Separator"}

class PDFSettings(GenericPDFSettings):
    def firstPage(self, canvas, doc):
        frame = doc.pageTemplates[0].frames[0]
        frame.leftPadding=frame.rightPadding=frame.topPadding=frame.bottomPadding=0
        canvas.saveState()
        canvas.setFont(self.regFont, self.fontSize)
        canvas.drawString(self.leftMargin, self.topMargin, 'TA1 Technical Acknowledgment - Interchange Control Number ' + self.ICN + '   Date:' + self.rptDate + '   Time:' + self.rptTime)
        canvas.drawRightString(self.rightMargin, self.topMargin, 'Version: ' + self.verNum + ' - ' + self.testProd)

        canvas.drawCentredString(self.PAGE_WIDTH / 2, self.topMargin - 1.5 * self.lineHeight,
                        "This report covers your file with control number %s, which was received/processed on %s at %s" % (
                        self.GCN, self.subDate, self.subTime))
        if self.inFileName:
            canvas.drawString(self.leftMargin, self.bottomMargin, "Filename: %s" % (self.inFileName))
        canvas.drawRightString(self.rightMargin, self.bottomMargin, "Page %s" % doc.page)
        canvas.restoreState()
    def laterPages(self, canvas, doc):
        frame = doc.pageTemplates[0].frames[0]
        frame.leftPadding=frame.rightPadding=frame.topPadding=frame.bottomPadding=0
        canvas.saveState()
        canvas.setFont(self.regFont, self.fontSize)
        canvas.drawString(self.leftMargin, self.topMargin, 'TA1 Technical Acknowledgment - Interchange Control Number ' + self.ICN + '   Date:' + self.rptDate + '   Time:' + self.rptTime)
        canvas.drawRightString(self.rightMargin, self.topMargin, 'Version: ' + self.verNum + ' - ' + self.testProd)
        if self.inFileName:
            canvas.drawString(self.leftMargin, self.bottomMargin, "Filename: %s" % (self.inFileName))
        canvas.drawRightString(self.rightMargin, self.bottomMargin, "Page %s" % doc.page)
        canvas.restoreState()

class X12_TA1(X12STLoop):
    def __init__(self, instance, ISARec, verNum='', subElemSep=':', inFileName=None, testProd='', pdfDir=""):
        """
        Parse a TA1 transaction acknowledgment.
        """
        self.inFileName = inFileName
        self.pdfDir     = pdfDir
        self.rptDate    = fixDateYYMMDD(ISARec[9])
        self.rptTime    = ISARec[10][:2] + ':' + ISARec[10][2:]
        self.verNum     = ISARec[12]
        self.ICN        = ISARec[13]
        self.testProd   = ISARec[15]
        self.GCN        = instance[1]
        self.subDate    = fixDateYYMMDD(instance[2])
        self.subTime    = instance[3][:2] + ':' + instance[3][:2]
        self.ackText    = ackDict[instance[4]]
        self.errText    = errDict[instance[5]]

    def toPDF(self):
        pdfSet = PDFSettings()
        pdfSet.pdfDir=self.pdfDir
        pdfSet.addStyles()
        cW = pdfSet.cW

        pdfSet.GCN = self.GCN
        pdfSet.ICN = self.ICN
        pdfSet.rptDate = self.rptDate
        pdfSet.rptTime = self.rptTime
        pdfSet.subDate = self.subDate
        pdfSet.subTime = self.subTime
        pdfSet.verNum = self.verNum
        pdfSet.submittedTrans = self.submittedTrans
        pdfSet.submittedVer = self.submittedVer
        pdfSet.inFileName = self.inFileName
        pdfSet.testProd = self.testProd

        fileNameBase = pdfSet.pdfDir + os.sep + 'TA1' + self.ICN
        fileName = fileNameBase + '.pdf'

        #fileName = os.path.join(os.path.expanduser('~'), 'Desktop', 'PDFs', self.ICN + '.pdf')
        doc = SimpleDocTemplate(fileName, pagesize=letter,
                                leftMargin=pdfSet.marginSize, rightMargin=pdfSet.marginSize,
                                topMargin=pdfSet.marginSize + pdfSet.lineHeight*2,
                                bottomMargin=pdfSet.marginSize + pdfSet.lineHeight*2)
        doc.leftPadding = 0
        Story = [Spacer(1,pdfSet.lineHeight)]

        stylesheet=getSampleStyleSheet()
        codeStyle = stylesheet['Normal']
        codeStyle.fontName = pdfSet.regFont
        codeStyle.fontSize = pdfSet.fontSize
        codeStyle.borderPadding = 0
        #codeStyle.leading = 8
        Lines = []
        Lines.append(Paragraph("File status: %s" % (self.ackText), style=codeStyle))
        if self.errText != "Success":
            Lines.append(Paragraph("    Error: %s" % (self.errText), style=codeStyle))
        Story.append(KeepTogether(Lines))
        attempt = 1
        while attempt > 0:  #avoid blowing up due to duplicate filename
            try:
                open(fileName, 'wb')
                doc.build(Story, onFirstPage=pdfSet.firstPage, onLaterPages=pdfSet.laterPages)
                attempt = 0
            except IOError:
                doc.filename = fileName = '%s(%s).pdf' % (fileNameBase, attempt)
                attempt += 1
        os.startfile(fileName)

if __name__ == '__main__':
    from X12Thing import X12Thing, Not_X12
    from tempfile import gettempdir
    ediDir = r'C:\Users\Marc\Desktop\277'
    codeFile = r'C:\Dropbox\fsrPy\codeTable.db'
    outDir = gettempdir()

    for inObj in os.listdir(ediDir):
        ediFile = ediDir + os.sep + inObj
        if os.path.isdir(ediFile): continue
        try:
            thingy = X12Thing(ediFile)
        except Not_X12:
            #print "%s is not an X12 file" % ediFile
            continue
        for gsLoop in thingy.GSLoop:
            verNum = gsLoop.GSRec[8]
            for stLoop in gsLoop.STLoop:
                if stLoop.STRec[1] == '277':
                    thisX12 = X12_277(stLoop, verNum, thingy.SubElemSep, thingy.inFileName, thingy.testProd, codeFile, outDir)
                    thisX12.toPDF()


import os.path
from X12STLoop import X12STLoop
from X12Utils import fixDate
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from GenPDFSet import GenericPDFSettings

#---Dictionaries
ik304Dict = {"1": "Unrecognized segment ID",
            "2":  "Unexpected segment",
            "3":  "Required Segment Missing",
            "4":  "Loop Occurs Over Maximum Times",
            "5":  "Segment Exceeds Maximum Use",
            "6":  "Segment Not in Defined Transaction Set",
            "7":  "Segment Not in Proper Sequence",
            "8":  "Segment Has Data Element Errors",
            "I4": "Implementation 'Not Used' Segment Present",
            "I6": "Implementation Dependent Segment Missing",
            "I7": "Implementation Loop Occurs Under Min Times",
            "I8": "Implementation Seg Below Minimum Use",
            "I9": "Implementation Dependent 'Not Used' Seg Present"}
ik403Dict = {"1": "Required Data Element Missing",
            "2": "Conditional Required Data Element Missing",
            "3": "Too Many Data Elements",
            "4": "Data Element Too Short",
            "5": "Data Element Too Long",
            "6": "Invalid Character In Data Element",
            "7": "Invalid Code Value",
            "8": "Invalid Date",
            "9": "Invalid Time",
            "10": "Exclusion Condition Violated",
            "12": "Too Many Repetitions",
            "13": "Too Many Components",
            "I10": "Implementation 'Not Used' Data Element Present",
            "I11": "Implementation Too Few Repetitions",
            "I12": "Implementation Pattern Match Failure",
            "I13": "Implem. Dependent 'Not Used' Data Elmnt Present",
            "I6": "Code Value Not Used in Implementation",
            "I9": "Implementation Dependent Data Element Missing"}
ik501Dict = {"A": "Accepted",
            "E": "Accepted But Errors Were Noted",
            "M": "Rejected, Message Authentication Code(MAC) Failed",
            "R": "Rejected",
            "W": "Rejected, Assurance Failed Validity Tests",
            "X": "Rejected, Couldn't Analyze Content After Decrypt"}
ik502Dict = {"1":  "Transaction Set Not Supported",
            "2":  "Transaction Set Trailer Missing",
            "3":  "Trx Set Ctrl # in Header and Trailer Don't Match",
            "4":  "# of Included Segs Does Not Match Actual Count",
            "5":  "One or More Segments in Error",
            "6":  "Missing or Invalid Trx Set Identifier",
            "7":  "Missing or Invalid Trx Set Control Number",
            "8":  "Authentication Key Name Unknown",
            "9":  "Encryption Key Name Unknown",
            "10": "Requested Svc (Auth or Encrypt) Not Available",
            "11": "Unknown Security Recipient",
            "12": "Incorrect Message Length (Encryption Only)",
            "13": "Message Authentication Code Failed",
            "15": "Unknown Security Originator",
            "16": "Syntax Error in Decrypted Text",
            "17": "Security Not Supported",
            "18": "Transaction Set not in Functional Group",
            "19": "Invalid Trx Set Implementation Convention Ref",
            "23": "Trx Set Ctrl # Not Unique within Functional Grp",
            "24": "No S3E Security EndSeg for S3S Security StartSeg",
            "25": "No S3S Security StartSeg for S3E Security EndSeg",
            "26": "No S4E Security EndSeg for S4S Security StartSeg",
            "27": "No S4S Security StartSeg for S4E Security EndSeg",
            "I5": "No Implementation One or More Segments in Error",
            "I6": "No Implementation Convention Not Supported"}
ak901Dict = {"A": "Accepted ",
            "E": "Accepted, But Errors Were Noted.",
            "M": "Rejected, Msg Authentication Code(MAC) Failed",
            "P": "Partially Accepted, At Least 1 Trx Set Rejected",
            "R": "Rejected",
            "W": "Rejected, Assurance Failed Validity Tests",
            "X": "Rejected, Couldn't Analyze Content After Decrypt"}
loopDict = {"1000A"  : "Submitter",
            "1000B"  : "Receiver",
            "2000"   : "Billing Prov (?)",
            "2000A"  : "Billing Prov",
            "2010"   : "Billing Prov (?)",
            "2010AA" : "Billing Prov Name",
            "2010AB" : "Pay-To Address",
            "2010AC" : "Pay-To Plan",
            "2000B"  : "Subscriber",
            "2000BA" : "Subscriber Name",
            "2010BB" : "Payer",
            "2000C"  : "Patient",
            "2010CA" : "Patient Name",
            "2300"   : "Claim level",
            "2310"   : "Undefined",
            "2310A"  : "Referring Prov",
            "2310B"  : "Rendering Prov",
            "2310C"  : "Service Facility",
            "2310D"  : "Supervising Prov",
            "2310E"  : "Ambulance Pick-Up",
            "2310F"  : "Ambulance Drop-Off",
            "2320"   : "Other Insurance",
            "2330"   : "Other... something?",
            "2330A"  : "Other Subscriber",
            "2330B"  : "Other Payer",
            "2330C"  : "Other Payer Referring Prov",
            "2330D"  : "Other Payer Rendering Prov",
            "2330E"  : "Other Payer Svc Facility",
            "2330F"  : "Other Payer Supervising Prov",
            "2330G"  : "Other Payer Billing Prov",
            "2400"   : "Service Line Level",
            "2410"   : "Drug Identification",
            "2420A"  : "Rendering Prov",
            "2420B"  : "Purchased Service Prov",
            "2420C"  : "Service Facility",
            "2420D"  : "Supervising Prov",
            "2420E"  : "Ordering Prov",
            "2420F"  : "Referring Prov",
            "2420G"  : "Ambulance Pick-Up",
            "2420"   : "Ambulance Drop-Off",
            "2430"   : "Line Adjudication Info",
            "2440"   : "Form ID Code"
            }


class PDFSettings(GenericPDFSettings):
    def firstPage(self, canvas, doc):
        frame = doc.pageTemplates[0].frames[0]
        frame.leftPadding=frame.rightPadding=frame.topPadding=frame.bottomPadding=0
        canvas.saveState()
        canvas.setFont(self.regFont, self.fontSize)
        canvas.drawString(self.leftMargin, self.topMargin, '999 Functional Acknowledgment - Transaction Control Number ' + self.TCN + '   Date:' + self.fgDate)
        canvas.drawRightString(self.rightMargin, self.topMargin, 'Version: ' + self.verNum + ' - ' + self.testProd)

        canvas.drawCentredString(self.PAGE_WIDTH / 2, self.topMargin - 1.5 * self.lineHeight,
                        "This report covers the %s file with control number %s, which was version %s" % (
                        self.submittedTrans, self.GCN, self.submittedVer))
        if self.inFileName:
            canvas.drawString(self.leftMargin, self.bottomMargin, "Filename: %s" % (self.inFileName))
        canvas.drawRightString(self.rightMargin, self.bottomMargin, "Page %s" % doc.page)
        canvas.restoreState()
    def laterPages(self, canvas, doc):
        frame = doc.pageTemplates[0].frames[0]
        frame.leftPadding=frame.rightPadding=frame.topPadding=frame.bottomPadding=0
        canvas.saveState()
        canvas.setFont(self.regFont, self.fontSize)
        canvas.drawString(self.leftMargin, self.topMargin, '999 Functional Acknowledgment - Transaction Control Number ' + self.TCN + '   Date:' + self.fgDate)
        canvas.drawRightString(self.rightMargin, self.topMargin, 'Version: ' + self.verNum + ' - ' + self.testProd)
        if self.inFileName:
            canvas.drawString(self.leftMargin, self.bottomMargin, "Filename: %s" % (self.inFileName))
        canvas.drawRightString(self.rightMargin, self.bottomMargin, "Page %s" % doc.page)

        canvas.restoreState()


class X12_999(X12STLoop):
    def __init__(self, instance, verNum='', subElemSep=':', inFileName=None, testProd='', fgDate='', pdfDir=""):
        """
        Parse a 999 transaction.
        """
        self.inFileName = inFileName
        self.pdfDir     = pdfDir
        self.fgDate     = fixDate(fgDate, slashes=True)
        self.STRec      = instance.STRec
        self.TSet       = instance.TSet
        self.TCN        = self.STRec[2]
        self.verNum     = verNum
        self.testProd   = testProd
        self.errorLines = [("Loop", None, "Position", "Segment/", "Element", "Data", "Error", "Detail")]
        self.tSetstatus = ""
        for seg in self.TSet:
            errLine = [None, None, None, None, None, None, None, None]
            if (seg[0] == 'AK1'):
                pass
            elif (seg[0]=='AK2'):
                self.submittedTrans = seg[1]
                self.GCN = seg[2]
                self.submittedVer =  seg[3]
            elif (seg[0]=='IK3'):
                errLine[3] = seg[1]
                errLine[2] = seg[2]
                errLine[0] = seg[3]
                try:
                    errLine[1] = loopDict[seg[3]]
                except KeyError:
                    errLine[1] = 'Undefined'
                errLine[6] = seg[4]
                errLine[7] = ik304Dict[seg[4]]
                self.errorLines.append(errLine)
            elif (seg[0]=='CTX'): # CTX info is just confusing to the user...
                #print seg
                if seg[1] == 'SITUATIONAL TRIGGER':
                    try:
                        errLine[7] = 'SITUATIONAL TRIGGER: %s*%s*%s*%s' % (seg[2], seg[3], seg[4], seg[5])
                    except:
                        try:
                            errLine[7] = 'SITUATIONAL TRIGGER: %s*%s*%s' % (seg[2], seg[3], seg[4])
                        except:
                            try:
                                errLine[7] = 'SITUATIONAL TRIGGER: %s*%s' % (seg[2], seg[3])
                            except:
                                errLine[7] = 'SITUATIONAL TRIGGER: %s' % (seg[2])
                else:
                    tmpList = seg[1].split(subElemSep)
                    errLine[7] = 'Context: %s, reference: %s' % (tmpList[0], tmpList[1])
                self.errorLines.append(errLine)
            elif (seg[0]=='IK4'):
                errLine[4] = seg[1]
                if len(seg) > 3:
                    errLine[6] = seg[3]
                    errLine[7] = ik403Dict[seg[3]]
                if len(seg) > 4:
                    errLine[5] = seg[4]
                self.errorLines.append(errLine)
            elif (seg[0]=='IK5'):
                self.tSetstatus = ik501Dict[seg[1]]
                if len(seg) > 2:
                    self.errormsg = ik502Dict[seg[2]]
            elif (seg[0]=='AK9'):
                self.fileStatus =ak901Dict[seg[1]]
                self.tSetsRec = seg[3]
                self.tSetsAcc = seg[4]

    def toPDF(self):
        pdfSet = PDFSettings()
        pdfSet.pdfDir=self.pdfDir
        pdfSet.addStyles()
        cW = pdfSet.cW

        pdfSet.GCN = self.GCN
        pdfSet.TCN = self.TCN
        pdfSet.fgDate = self.fgDate
        pdfSet.verNum = self.verNum
        pdfSet.submittedTrans = self.submittedTrans
        pdfSet.submittedVer = self.submittedVer
        pdfSet.inFileName = self.inFileName
        pdfSet.testProd = self.testProd

        fileNameBase = pdfSet.pdfDir + os.sep + '999' + self.TCN
        fileName = fileNameBase + '.pdf'

        #fileName = os.path.join(os.path.expanduser('~'), 'Desktop', 'PDFs', self.TCN + '.pdf')
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

        if len(self.errorLines) > 1:

            errorStyle = TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'),
                                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                    ('FONT', (0,0), (-1,-1), pdfSet.regFont, pdfSet.fontSize),
                                    ("BOTTOMPADDING",(0,0),(-1,-1),pdfSet.pad),
                                    ("TOPPADDING", (0,0),(-1,-1),pdfSet.pad),
                                    ("RIGHTPADDING", (0,0),(-1,-1),pdfSet.pad),
                                    ("LEFTPADDING", (0,0),(-1,-1),pdfSet.pad),
                                    ('LINEBELOW', (0,0), (-1,0), 1, (0,0,0,1))])

            errorWidths  = [7*cW, 25*cW, 10*cW, 8*cW, 10*cW, 10*cW, 8*cW, 50*cW]

            tbl = Table(self.errorLines, colWidths=errorWidths, rowHeights=None, style=errorStyle)
            Story.append(tbl)
            Story.append(Spacer(1,pdfSet.lineHeight*3))
        Lines = []
        Lines.append(Paragraph("Transaction set status: " + self.tSetstatus, style=codeStyle))
        if self.errormsg:
            Lines.append(Paragraph("    " + self.errormsg, style=codeStyle))
        Lines.append(Spacer(1,pdfSet.lineHeight))
        Lines.append(Paragraph("File status: %s" % (self.fileStatus), style=codeStyle))
        Lines.append(Paragraph("    %s transaction set(s) received, %s accepted" % (self.tSetsRec, self.tSetsAcc), style=codeStyle))
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
    from X12Thing import X12Thing
    ediDir = r'C:\Users\Marc\Desktop\Honbo'
    outDir = r'C:\Users\Marc\Desktop\PDF'
    for inObj in os.listdir(ediDir):
        ediFile = ediDir + os.sep + inObj
        if os.path.isdir(ediFile): continue
        print ediFile
        thingy = X12Thing(ediFile)
        for gsLoop in thingy.GSLoop:
            verNum = gsLoop.GSRec[8]
            fgDate = gsLoop.GSRec[4]
            for stLoop in gsLoop.STLoop:
                if stLoop.STRec[1] == '999':
                    thisX12= X12_999(stLoop, verNum, thingy.SubElemSep, thingy.inFileName, thingy.testProd, fgDate, outDir)
                    thisX12.toPDF()


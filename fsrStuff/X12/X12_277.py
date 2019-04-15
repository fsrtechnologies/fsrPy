import os.path, copy
from X12STLoop import X12STLoop
from X12Utils import fixDate, monetize
from CodeFinder import CodeFinder
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from GenPDFSet import GenericPDFSettings

class PDFSettings(GenericPDFSettings):
    def addStyles(self):
        cW = self.cW

        #                  rendID  date1 date2 POS    units Proc  Mods  Bill  Allw   Deduc  CoIns  AdjCd  AdjAmt Paid
        #                  LEFT    LEFT  LEFT  RIGHT  RIGHT RIGHT LEFT  DEC   DEC    DEC    DEC    LEFT   DEC    DEC
        self.clmLineWidths    = [11*cW, 9*cW, 8*cW, 3*cW,  3*cW, 7*cW, 6*cW, 8*cW, 10*cW, 10*cW, 10*cW, 21*cW, 9*cW,  10*cW]
        self.styles['clmLine'].add('ALIGN', (3,0), (5,-1), 'RIGHT')
        self.styles['clmLine'].add('LEFTPADDING', (6,0), (6,-1), cW)
        self.styles['clmLine'].add('LEFTPADDING', (11,0), (11,-1), 4*cW)
        self.styles['clmLine'].add('ALIGN', (7,0), (10,-1), 'DECIMAL')
        self.styles['clmLine'].add('ALIGN', (12,0), (13,-1), 'DECIMAL')

        #                   label  patRsp  label  Bill  Allow Deduc  CoIns  blank  None   AdjAmt Paid
        #                   LEFT   DEC     LEFT   DEC   DEC   DEC    DEC    DEC    DEC    DEC    DEC

    def firstPage(self, canvas, doc):
        frame = doc.pageTemplates[0].frames[0]
        frame.leftPadding=frame.rightPadding=frame.topPadding=frame.bottomPadding=0
        canvas.saveState()
        canvas.setFont(self.regFont, self.fontSize)
        canvas.drawString(self.leftMargin, self.topMargin, '277 Claim Acknowledgment - Transaction Control Number ' + self.TCN)
        canvas.drawRightString(self.rightMargin, self.topMargin, 'Version: ' + self.verNum + ' - ' + self.testProd)

        canvas.drawCentredString(self.PAGE_WIDTH / 2, self.topMargin - 1.5 * self.lineHeight,
                                 "This report covers claim file with control number %s, submitted on %s at %s" % (self.GCN, self.subDate, self.subTime))
        if self.inFileName:
            canvas.drawString(self.leftMargin, self.bottomMargin, "Filename: " + self.inFileName)
        canvas.drawRightString(self.rightMargin, self.bottomMargin, "Page %s" % doc.page)
        canvas.restoreState()
    def laterPages(self, canvas, doc):
        frame = doc.pageTemplates[0].frames[0]
        frame.leftPadding=frame.rightPadding=frame.topPadding=frame.bottomPadding=0
        canvas.saveState()
        canvas.setFont(self.regFont, self.fontSize)
        canvas.drawString(self.leftMargin, self.topMargin, '277 Claim Acknowledgment - Transaction Control Number ' + self.TCN)
        canvas.drawRightString(self.rightMargin, self.topMargin, 'Version: ' + self.verNum + ' - ' + self.testProd)
        if self.inFileName:
            canvas.drawString(self.leftMargin, self.bottomMargin, "Filename: " + self.inFileName)
        canvas.drawRightString(self.rightMargin, self.bottomMargin, "Page %s" % doc.page)

        canvas.restoreState()

class Global(object):
    loopNum = '0000'

def getLoop(seg=[], loopNum='0000'):
    if seg[0] == 'BHT':                                         #Beginning
        return '0000'
    if seg[0] == 'HL'  and seg[3] == '20':                      #Information Source
        return '2000A'
    if seg[0] == 'NM1' and seg[1] == 'PR':                      #Payor
        return '2100A'
    if seg[0] == 'HL'  and seg[3] == '21':                      #Information Receiver
        return '2000B'
    if seg[0] == 'NM1' and seg[1] == '41':                      #Submitter
        return '2100B'
    if seg[0] == 'TRN' and loopNum in ('2100A', '2100B'):       #Loop Info Rcvr Trace ID
        return loopNum
    if seg[0] == 'HL'  and seg[3] == '19':                      #Service Provider
        return '2000C'
    if seg[0] == 'NM1' and seg[1] == '1P':                      #Provider Name
        return '2100C'
    if seg[0] == 'TRN' and loopNum in ('2100C'):                #Svc Provider Trace ID
        return '2200C'
    if seg[0] == 'HL'  and seg[3] == '22':                      #Subscriber
        return '2000D'
    if seg[0] == 'NM1' and seg[1] == 'IL':                      #Subscriber Name
        return '2100D'
    if seg[0] == 'TRN' and loopNum in ('2100D'):                #Claim Status Tracking Number
        return '2200D'
    if seg[0] == 'REF' and seg[1] == 'FJ':                      #Service Line ID
        if loopNum == '2200D':
            return '2220D'
        if loopNum == '2200E':
            return '2220E'
    if seg[0] == 'HL'  and seg[3] == '22':                      #Dependent
        return '2000E'
    if seg[0] == 'NM1' and seg[1] == 'QC':                      #Dependent Name
        return '2100E'
    if seg[0] == 'TRN' and loopNum in ('2100E'):                #Claim Status Tracking Number
        return '2200E'
    return loopNum


class ClaimLine(object):
    def __init__(self, traceNum='', patID=''):
        self.traceNum = traceNum
        self.amount= monetize('0')
        self.ctrlNum = ''
        self.date1 = ''
        self.date2 = ''

class RptUnit(object):
    def __init__(self, Name='', ID=''):
        self.Name = Name
        self.ID   = ID
        self.amtString = ''
        self.qtyString = ''
    def stcUpdate(self, action='', amount='0', statusCode=''):
        self.action = action
        self.amount = monetize(amount)
        self.statusCode = statusCode

class X12_277(X12STLoop):
    def __init__(self, instance, verNum='', subElemSep=':', inFileName=None, testProd='', codeFile=os.getcwd() + os.sep + "codeTable.db", pdfDir=""):
        """
        Parse a 277 transaction.
        """
        self.inFileName = inFileName
        self.pdfDir     = pdfDir
        self.STRec      = instance.STRec
        self.TSet       = instance.TSet
        self.TCN        = self.subDateTime = self.STRec[2] # initialize here in case BHT doesn't work out
        self.verNum     = verNum
        self.testProd   = testProd
        self.bP         = []
        bpNum           = -1
        clmNum          = -1
        clmLine         = -1
        loopNum         = '0000'
        cf = CodeFinder(dbFile=codeFile)
        stcDict = {'WQ':'Accept', 'U':'Reject'}
        qtyDict = {'90':'Acknowledged', 'AA':'Unacknowledged', 'QA':'Approved', 'QC':'Disapproved'}
        amtDict = {'YU':'Allowed amount', 'YY':'Denied amount'}
        self.catGlossary = {}
        self.codeGlossary = {}
        self.srcGlossary = {}

        for seg in self.TSet:
            loopNum = getLoop(seg, loopNum)
            #print seg, loopNum

            if seg[0] == 'BHT':
                self.subDate = fixDate(seg[4], slashes=True)
                self.subTime = seg[5][0:2] + ':' + seg[5][2:4]
                self.subDateTime = seg[4] + seg[5]

            if seg[0] == 'NM1':
                if len(seg) > 9:
                    tmpID = seg[9]
                if seg[2] == '1': #Person
                    tmpName = seg[3] + ', ' + seg[4] + ' ' + seg[5]
                else:           #Non-person entity
                    tmpName = seg[3].strip()

                if seg[1] == 'PR':
                    self.payor = RptUnit(tmpName, tmpID)
                if seg[1] == '41':
                    self.submitter = RptUnit(tmpName, tmpID)
                if seg[1] == '85':  #Billing Provider
                    bpNum +=1
                    clmNum = -1
                    self.bP.append(RptUnit(tmpName, tmpID))
                    self.bP[bpNum].claim = []
                if seg[1] == 'QC':  #Patient
                    clmNum += 1
                    clmLine = -1
                    self.bP[bpNum].claim.append(RptUnit(tmpName, tmpID))
                    self.bP[bpNum].claim[clmNum].line = []

            if seg[0] == 'TRN':
                if loopNum == '2100A':  #Payor
                    self.TCN = seg[2]
                if loopNum == '2100B':  #Submitter
                    self.GCN = seg[2]   #this should match BHT03 from 837 - hope we sent something useful there!
                if loopNum == '2000C':  #Billing provider - no useful info at this level
                    pass
                if loopNum == '2200E':  #Claim line
                    clmLine += 1
                    if clmLine > 0:
                        tmpName = None
                    else:
                        tmpName = self.bP[bpNum].claim[clmNum].Name
                    self.bP[bpNum].claim[clmNum].line.append(RptUnit(tmpName, seg[2])) #trace number becomes ID
                    self.bP[bpNum].claim[clmNum].line[clmLine].date1 = ''
                    self.bP[bpNum].claim[clmNum].line[clmLine].date2 = ''

            if seg[0] == 'DTP':
                if seg[1] == '050':
                    self.date837Rec = fixDate(seg[3], slashes=True)
                if seg[1] == '009':
                    self.date837Proc = fixDate(seg[3], slashes=True)
                if seg[1] == '472':
                    self.bP[bpNum].claim[clmNum].line[clmLine].date1 = fixDate(seg[3][0:8], forceYear=2, slashes=True)
                    if seg[2] == 'RD8':
                        self.bP[bpNum].claim[clmNum].line[clmLine].date2 = fixDate(seg[3][9:17], forceYear=2, slashes=True)


            if seg[0] == 'STC':
                #print seg, inFileName
                segOne = seg[1].split(subElemSep)
                statusCode = '   '.join(segOne)
                action = stcDict[seg[3]]
                if len(seg) > 4:
                    amount = monetize(seg[4])
                self.catGlossary[segOne[0]] = cf.lookup('CSCC',segOne[0])
                if len(segOne) > 1:
                    self.codeGlossary[segOne[1]] = cf.lookup('HCSC',segOne[1])
                if len(segOne) > 2:
                    self.srcGlossary[segOne[2]] = cf.lookup('Entity',segOne[2])

                if loopNum == '2000C':              #Billing provider
                    self.bP[bpNum].stcUpdate(action, amount, statusCode)
                if loopNum == '2100B':              #Submitter
                    self.submitter.stcUpdate(action, amount, statusCode)
                if loopNum == '2200E':              #Claim line
                    self.bP[bpNum].claim[clmNum].line[clmLine].stcUpdate(action, amount, statusCode)

            if seg[0] == 'AMT':
                if loopNum == '2000C':              #Billing provider
                    if len(self.bP[bpNum].amtString) > 1:
                        self.bP[bpNum].amtString += ',  '
                    self.bP[bpNum].amtString += '%s %s' % (amtDict[seg[1]],monetize(seg[2]))
                if loopNum == '2100B':              #Submitter
                    if len(self.submitter.amtString) > 1:
                        self.submitter.amtString += ',  '
                    self.submitter.amtString += '%s %s' % (amtDict[seg[1]],monetize(seg[2]))

            if seg[0] == 'QTY':
                if loopNum == '2000C':              #Billing provider
                    if len(self.bP[bpNum].qtyString) > 1:
                        self.bP[bpNum].qtyString += ',  '
                    self.bP[bpNum].qtyString += '%s claims %s' % (seg[2], qtyDict[seg[1]])
                if loopNum == '2100B':              #Submitter
                    if len(self.submitter.qtyString) > 1:
                        self.submitter.qtyString += ',  '
                    self.submitter.qtyString += '%s claims %s' % (seg[2], qtyDict[seg[1]])

            if seg[0] == 'REF':
                if seg[1] == '1K':
                    self.bP[bpNum].claim[clmNum].line[clmLine].ctrlNum = seg[2]


    def toPDF(self):
        pdfSet = PDFSettings()
        pdfSet.pdfDir=self.pdfDir
        pdfSet.addStyles()
        cW = pdfSet.cW

        pdfSet.GCN = self.GCN
        pdfSet.TCN = self.TCN
        pdfSet.verNum = self.verNum
        pdfSet.subDate = self.subDate
        pdfSet.subTime = self.subTime
        pdfSet.inFileName = self.inFileName
        pdfSet.testProd = self.testProd

        #fileNameBase = pdfSet.pdfDir + os.sep + '277-' + self.TCN
        fileNameBase = pdfSet.pdfDir + os.sep + '277-' + self.subDateTime
        fileName = fileNameBase + '.pdf'
        doc = SimpleDocTemplate(fileName, pagesize=letter,
                                leftMargin=pdfSet.marginSize, rightMargin=pdfSet.marginSize,
                                topMargin=pdfSet.marginSize + pdfSet.lineHeight*2,
                                bottomMargin=pdfSet.marginSize + pdfSet.lineHeight*2)
        doc.leftPadding = 0
        Story = []

        stylesheet=getSampleStyleSheet()
        style1 = stylesheet['Normal']
        style1.fontName = pdfSet.regFont
        style1.fontSize = pdfSet.fontSize
        style1.borderPadding = 0
        #codeStyle.leading = 8
        style2 = copy.copy(style1)
        style2.firstLineIndent = -15
        style2.leftIndent = 20
        style3 = copy.copy(style1)
        style3.fontName = pdfSet.boldFont
        tmpPara = "Payor: %s [%s] - Received %s, processed %s" % (self.payor.Name, self.payor.ID, self.date837Rec, self.date837Rec)
        Story.append(Paragraph(tmpPara, style1))
        Story.append(Spacer(1,pdfSet.lineHeight*.5))
        tmpPara = "Submitter: %s [%s] %s - %s" % (self.submitter.Name, self.submitter.ID, self.submitter.amount, self.submitter.action)
        Story.append(Paragraph(tmpPara, style1))
        if len(self.submitter.amtString) > 1:
            Story.append(Paragraph(self.submitter.amtString, style1))
        tmpPara = self.submitter.qtyString + '  - Status code: ' + self.submitter.statusCode
        Story.append(Paragraph(tmpPara, style1))
        Story.append(Spacer(1,pdfSet.lineHeight*.5))
        for billProv in self.bP:
            #bpSection = []
            tmpPara = "Billing Provider: %s [%s] %s - %s" % (billProv.Name, billProv.ID, billProv.amount, billProv.action)
            Story.append(Paragraph(tmpPara, style1))
            if len(billProv.amtString) > 1:
                Story.append(Paragraph(billProv.amtString, style1))
            tmpPara = billProv.qtyString + '  - Status code: ' + billProv.statusCode
            Story.append(Paragraph(tmpPara, style1))
            #bpSec.append(Spacer(1,pdfSet.lineHeight*.5))

            if len(billProv.claim) > 0:
                statWidths = [26*cW, 18*cW, 9*cW, 8*cW, 8*cW, 5*cW, 3*cW, 9*cW, 18*cW, 9*cW]
                statStyle = TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'),
                                        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                        ('FONT', (0,0), (-1,-1), pdfSet.regFont, pdfSet.fontSize),
                                        ('BOTTOMPADDING',(0,0),(-1,-1),pdfSet.pad),
                                        ('TOPPADDING', (0,0),(-1,-1),pdfSet.pad),
                                        ('RIGHTPADDING', (0,0),(-1,-1),pdfSet.pad),
                                        ('LEFTPADDING', (0,0),(-1,-1),pdfSet.pad),
                                        ('LINEBELOW', (0,1), (-1,1), 1, (0,0,0,1))])
                statStyle.add('ALIGN', (4,0), (4,-1), 'DECIMAL')
                errStyle = copy.copy(statStyle)
                errStyle.add('FONT', (0,0), (-1,-1), pdfSet.regFont, pdfSet.fontSize)
                statLines = [(None, None, None, None, None, None, None, None, 'Status codes', None),
                             ("Patient", "Claim Number", None, None, None, None, None, "Action", 'Cat. Code Source', None)]
                for clm in billProv.claim:
                    for clmLine in clm.line:
                        if clmLine.action == 'Accept':
                            statLines.append([clmLine.Name, clmLine.ID, clmLine.date1, clmLine.date2, clmLine.amount, None, None, clmLine.action, clmLine.statusCode, None])
                        else:
                            statLines.append([clmLine.Name, clmLine.ID, clmLine.date1, clmLine.date2, clmLine.amount, None, '**', clmLine.action, clmLine.statusCode, '**'])
                tbl = Table(statLines, colWidths=statWidths, rowHeights=None, style=statStyle)
                tbl.hAlign = 'LEFT'
                tbl.leftPadding = 0

                Story.append(tbl)
                Story.append(Spacer(1,pdfSet.lineHeight*2))
                #Story.append(KeepTogether(bpSection))
        glossary = []
        glossary.append(Paragraph("GLOSSARY: Code categories, status codes, and entities", style3))

        for gloss in (self.catGlossary, self.codeGlossary, self.srcGlossary):
            if len(gloss) > 0:
                for code, message in gloss.iteritems():
                    tmpPara = "%s: %s " % (code, message)
                    glossary.append(Paragraph(tmpPara, style2))
        Story.append(KeepTogether(glossary))

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


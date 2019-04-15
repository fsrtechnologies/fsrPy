import os, copy
from X12Thing import X12Thing
from X12STLoop import X12STLoop
from X12Utils import fixDate, fixPhone, fixZip, monetize, sorted_nicely
from CodeFinder import CodeFinder
#from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from GenPDFSet import GenericPDFSettings

cfiDict =  {"AM": "AUTO MEDICAL",
            "BL": "BC/BS",
            "CH": "CHAMPUS",
            "CI": "COMMERCIAL",
            "DS": "DISABILITY",
            "FI": "FEP",
            "HM": "HMO",
            "LM": "LIABILITY",
            "MA": "MEDICARE PART A",
            "MB": "MEDICARE PART B",
            "MC": "MEDICAID",
            "OF": "",
            "TV": "TITLE V",
            "VA": "VETERANS AFFAIRS",
            "WC": "WORKERS' COMP",
            "ZZ": "",
            "09": "SELF-PAY",
            "11": "",
            "12": "PPO",
            "13": "POS",
            "14": "EPO",
            "15": "INDEMNITY",
            "16": "HMO MEDICARE",
            "17": "DMO"}

casDict =  {"CO": "Contractual Obligations",
            "CR": "Correction and Reversals",
            "OA": "Other adjustments",
            "PI": "Payor Initiated Reductions",
            "PR": "Patient Responsibility"}

plbDict =  {"50": "Late Charge",
            "51": "Interest Penalty Charge",
            "72": "Authorized Return",
            "90": "Early Payment Allowance",
            "AM": "Applied to Borrower's Account",
            "AP": "Acceleration of Benefits",
            "B2": "Rebate",
            "B3": "Recovery Allowance",
            "BD": "Bad Debt Adjustment",
            "BN": "Bonus",
            "C5": "Temporary Allowance",
            "CR": "Capitation Interest",
            "CS": "Adjustment",
            "CT": "Capitation Payment",
            "CV": "Capital Passthru",
            "DM": "Direct Medical Education Passthru",
            "E3": "Withholding",
            "FB": "Forwarding Balance",
            "FC": "Fund Allocation",
            "GO": "Graduate Medical Education Passthru",
            "IP": "Incentive Premium Payment",
            "IR": "Internal Revenue Service Withholding",
            "IS": "Interim Settlement",
            "J1": "Nonreimbursable",
            "L3": "Penalty",
            "L6": "Interest Owed",
            "LE": "Levy",
            "LS": "Lump Sum",
            "OA": "Organ Acquisition Passthru",
            "OB": "Offset for Affiliated Providers",
            "PI": "Periodic Interim Payment",
            "PL": "Payment Final",
            "RA": "Retro-activity Adjustment",
            "RE": "Return on Equity",
            "SL": "Student Loan Repayment",
            "TL": "Third Party Liability",
            "WO": "Overpayment Recovery",
            "WU": "Unspecified Recovery",
            "ZZ": "Mutually Defined"}

class PDFSettings(GenericPDFSettings):
    def addStyles(self):
        cW = self.cW

        self.clmHeaderWidths = [4*cW, 2*cW, 17*cW, 25*cW, 5*cW, 13*cW, 4*cW, 19*cW, 39*cW]
        self.styles['clmHeader'].add('LINEABOVE', (0,0), (-1,-1), 1, (0,0,0,1))
        self.styles['clmHeader'].add('ALIGN', (0,0), (0,0), 'RIGHT')

        self.columnHeader = "PERF PROV  SERVICE DATE(S)  POS  U   PROC MODS      BILLED   ALLOWED    DEDUCT    COINS  ADJ CODES             ADJ AMT   PROV PD"
        self.columnLeader = "123456789A123456789B123456789C123456789D123456789E123456789F123456789G123456789H123456789I123456789J123456789K123456789L12345678"

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
        self.clmFooter1Widths = [8*cW, 10*cW,  28*cW, 9*cW, 10*cW, 10*cW, 10*cW, 11*cW, 19*cW, 10*cW,  9*cW]
        self.styles['clmFooter1'].add('LEFTPADDING', (2,0), (2,-1), 2*cW)
        self.styles['clmFooter1'].add('ALIGN', (1,0), (1,-1), 'DECIMAL')
        self.styles['clmFooter1'].add('ALIGN', (3,0), (-1,-1), 'DECIMAL')


        #                  label   xover  netPmt
        #                  LEFT    LEFT   DEC
        self.clmFooter2Widths = [33*cW, 78*cW, 2*cW, 12*cW]
        self.styles['clmFooter2'].add('FONT', (-2,-1), (-1,-1), self.boldFont, self.fontSize)
        self.styles['clmFooter2'].add('ALIGN', (3,0), (-1,-1), 'DECIMAL')


    def firstPage(self, canvas, doc):
        frame = doc.pageTemplates[0].frames[0]
        frame.leftPadding=frame.rightPadding=frame.topPadding=frame.bottomPadding=0
        canvas.saveState()
        canvas.setFont(self.regFont, self.fontSize)
        tM, lM, rM, lH = self.topMargin, self.leftMargin, self.rightMargin, self.lineHeight
        canvas.drawString(lM, tM, self.payorName)
        canvas.drawString(lM, tM - lH, self.payorAdd1)
        canvas.drawString(lM, tM - 2 * lH, self.payorCSZ)
        canvas.drawString(lM, tM - 3 * lH, self.payorBizContact)
        canvas.drawRightString(rM, tM, self.insType)
        canvas.drawRightString(rM, tM - lH, 'REMITTANCE')
        canvas.drawRightString(rM, tM - 2 * lH, 'NOTICE')
        canvas.drawRightString(rM, tM - 3 * lH, 'Version: ' + self.verNum)

        canvas.drawCentredString(lM + (rM - lM)/2, tM, self.inFileName)

        canvas.drawString(lM + 0.25 * inch, tM - 5 * lH, self.payeeName)
        canvas.drawString(lM + 0.25 * inch, tM - 6 * lH, self.payeeAdd1)
        if len(self.payeeAdd2) > 0:
            canvas.drawString(lM + 0.25 * inch, tM - 7 * lH, self.payeeAdd2)
            canvas.drawString(lM + 0.25 * inch, tM - 8 * lH, self.payeeCSZ)
        else:
            canvas.drawString(lM + 0.25 * inch, tM - 7 * lH, self.payeeCSZ)

        canvas.drawString(rM - 1.75 * inch, tM - 5 * lH, "PROVIDER #:")
        canvas.drawString(rM - 1.75 * inch, tM - 6 * lH, "PAGE #:")
        canvas.drawString(rM - 1.75 * inch, tM - 7 * lH, "DATE:")
        canvas.drawString(rM - 1.75 * inch, tM - 8 * lH, "CHECK/EFT #:")

        canvas.drawRightString(rM, tM - 5 * lH, self.payeeID)
        canvas.drawRightString(rM, tM - 6 * lH, "%s" % (doc.page))
        canvas.drawRightString(rM, tM - 7 * lH, fixDateSlashes(self.chkDate, forceYear=4))
        canvas.drawRightString(rM, tM - 8 * lH, self.chkNum)

        #canvas.drawString(leftMargin, topMargin - 10 * lineHeight, self.columnLeader)
        canvas.drawString(lM, tM - 11 * lH, self.columnHeader)
        canvas.restoreState()

    def laterPages(self, canvas, doc):
        canvas.saveState()
        canvas.setFont(self.regFont, self.fontSize)
        tM, lM, rM, lH = self.topMargin, self.leftMargin, self.rightMargin, self.lineHeight

        canvas.drawString(lM, tM, self.payorName)
        canvas.drawString(lM, tM - 2 * lH, "PROVIDER #:")
        canvas.drawString(lM, tM - 3 * lH, "CHECK/EFT #:")
        canvas.drawRightString(lM + 1.75 * inch, tM - 2 * lH, self.payeeID)
        canvas.drawRightString(lM + 1.75 * inch, tM - 3 * lH, self.chkNum)

        canvas.drawString(lM + 3 * inch, tM - 3 * lH, fixDateSlashes(self.chkDate, forceYear=4))

        canvas.drawString(lM + 4.5 * inch, tM - 2 * lH, self.payeeName)
        canvas.drawString(lM + 4.5 * inch, tM - 3 * lH, "PAGE #:   %s" % doc.page)

        canvas.drawRightString(rM, tM, self.insType)
        canvas.drawRightString(rM, tM - lH, 'REMITTANCE')
        canvas.drawRightString(rM, tM - 2 * lH, 'NOTICE')

        canvas.drawString(lM, tM - 4 * lH, self.columnHeader)
        canvas.restoreState()

def fixDateSlashes(inDate=None, spaces=True, forceYear=None, slashes=True): # Overriding to make slashes default to True
    return fixDate(inDate, spaces, forceYear, slashes)

def getLoop(seg=[], loopNum='0000'):
    if seg[0] == 'BHT':                                         #Beginning
        return '0000'
    if seg[0] == 'N1':
        if seg[1] == 'PR':                                      #Payor
            return '1000A'
        if seg[1] == 'PE':                                      #Payee
            return '1000B'
    if seg[0] == 'LX':                                          #Header number
        return '2000'
    if seg[0] == 'CLP':                                         #Claim level
        return '2100'
    if seg[0] == 'SVC':                                         #Service level
        return '2110'
    if seg[0] == 'HL'  and seg[3] == '20':                      #Information Source
        return '2000A'
    return loopNum                                              #everything in-between




class ClaimLine(object):
    def __init__(self, paidProc='', paidMod=[''], amtBilled=0.00, amtPaid=0.00, paidUnits=0,
                billedProc='', billedMod=[''], billedUnits=0):
        self.paidProc = paidProc
        self.paidMod = paidMod
        self.amtBilled = amtBilled
        self.amtPaid = amtPaid
        self.paidUnits = paidUnits
        self.billedProc = billedProc
        self.billedMod = billedMod
        self.billedUnits = billedUnits
        self.ctrlNum = ''
        self.prvID = ''
        self.date1 = ''
        self.date2 = ''
        self.POS = ''
        self.adjCodes = set()
        self.amtAllowed = monetize(0.00)
        self.amtDeduct = monetize(0.00)
        self.amtCoIns = monetize(0.00)
        self.amtAdjust = monetize(0.00)

class Claim(object):
    def __init__(self, patAcct='', clmStatus='', amtBilled=monetize(0.00), amtPaid=monetize(0.00), amtPatResp=monetize(0.00), ctrlNum=''):
        self.patAcct = patAcct
        self.clmStatus = clmStatus
        self.amtBilled = amtBilled
        self.totBilled = monetize(0.00)  #Use this as a check on arithmetic only
        self.amtPaid = amtPaid
        self.amtPatResp = amtPatResp
        self.ctrlNum = ctrlNum
        self.grpPolNum = ''
        self.contact = None
        self.clmLine = []
        self.adjCodes = set()
        self.patName = ''
        self.date1 = ''
        self.date2 = ''
        self.patID = ''
        self.rendID = ''
        self.amtAllowed = monetize(0.00)
        self.amtDeduct = monetize(0.00)
        self.amtCoIns = monetize(0.00)
        self.amtAdjust = monetize(0.00)
        self.fwdInfo = None
        self.xoverCarrier = ''
        self.medRecNum = ''

class Adjustment(object):
    def __init__(self, grpCode='', adjCode='', monAmt=0, quantity=1):
        self.grpCode  = grpCode
        self.adjCode  = adjCode
        self.monAmt   = monAmt
        self.quantity = quantity

class SubPLB(object):
    def __init__(self, rsnCode='', plbID='', monAmt=0):
        self.rsnCode = rsnCode
        self.plbID = plbID
        self.monAmt = monetize(monAmt)

class ProviderLevelAdjustment(object):
    def __init__(self, provID='', fiscDate=''):
        self.provID = provID
        self.fiscDate = fixDateSlashes(fiscDate, forceYear=2)
        self.sub = []


class X12_835(X12STLoop):
    submitterID = ''
    payorName = ''
    payorID = ''
    payor2ndID = ''
    payorAdd1 = ''
    payorAdd2 = ''
    payorCSZ = ''
    payorBizContact = ''
    payorTechContact = ''
    insType = ''
    payeeName = ''
    payeeID = ''
    payeeAdd1= ''
    payeeAdd2 = ''
    payeeCSZ = ''
    payeeProvNum = ''
    chkDate = ''
    chkNum = ''


    def __init__(self, instance, verNum='', subElemSep=':', inFileName=None, testProd='', codeFile='', pdfDir=""):
        self.STRec      = instance.STRec
        self.TSet       = instance.TSet
        self.verNum     = verNum
        entityType = ''
        self.claim = []
        self.plb = []
        self.grpGlossary = {}
        self.codeGlossary = {}
        self.adjCodes = set()
        self.totClaims = 0
        self.totBilled = monetize(0.00)
        self.totAllowed = monetize(0.00)
        self.totDeduct = monetize(0.00)
        self.totCoIns = monetize(0.00)
        self.totRCAmt = monetize(0.00)
        self.totProvPd = monetize(0.00)
        self.totProvAdj = monetize(0.00)
        self.totCheckAmt = monetize(0.00)


        claimNum = -1
        lineNum = -1
        loopNum = '0000'
        self.subElemSep = subElemSep
        self.inFileName = inFileName
        self.pdfDir     = pdfDir
        cf = CodeFinder(dbFile=codeFile)

        for seg in self.TSet:
            loopNum = getLoop(seg, loopNum)
            #print loopNum, seg
            if seg[0] == 'BPR':
                self.totCheckAmt = monetize(seg[2])
                self.chkDate = fixDateSlashes(seg[16], slashes=True)

            if seg[0] == 'TRN':
                self.chkNum = seg[2]

            if seg[0] == 'N1':
                if seg[1] == 'PR':
                    entityType = 'Payor'
                    self.payorName = seg[2]
                if seg[1] == 'PE':
                    entityType = 'Payee'
                    self.payeeName = seg[2]
                    self.payeeID = seg[4]
            if seg[0] == 'N3':
                if entityType == 'Payor':
                    self.payorAdd1 = seg[1]
                    if len(seg) > 2:
                        self.payorAdd2 = seg[2]
                if entityType == 'Payee':
                    self.payeeAdd1 = seg[1]
                    if len(seg) > 2:
                        self.payeeAdd2 = seg[2]
            if seg[0] == 'N4':
                if entityType == 'Payor':
                    self.payorCSZ = seg[1] + ', ' + seg[2] + ' ' + fixZip(seg[3])
                if entityType == 'Payee':
                    self.payeeCSZ = seg[1] + ', ' + seg[2] + ' ' + fixZip(seg[3])

            #---   REF
            if seg[0] == 'REF':
                if seg[1] == 'EV':
                    self.submitterID = seg[2]
                elif seg[1] == '2U':
                    self.payorID = seg[2]
                elif seg[1] == 'TJ':  #Payee Tax/other ID
                    self.payee2ndID = seg[2]
                elif seg[1] == 'EA':
                    self.claim[claimNum].medRecNum = seg[2]
                elif seg[1] == 'LU':
                    self.claim[claimNum].clmLine[lineNum].POS = seg[2]
                elif seg[1] == '6R':
                    self.claim[claimNum].clmLine[lineNum].ctrlNum = seg[2]
                elif seg[1] == '1L':
                    self.claim[claimNum].grpPolNum = seg[2]
                elif seg[1] == 'CE':
                    self.claim[claimNum].contractClass = seg[2]
                elif seg[1] == 'F8':
                    self.claim[claimNum].origRefNum = seg[2]
                elif seg[1] == '1W':
                    self.claim[claimNum].memberID = seg[2]
                else:
                    print loopNum, seg

            #---   Remittance Delivery Method - may implement this later...
            if seg[0] == 'RDM':
                pass
            #---   (Provider/Provider Supplemental) Summary Info (?) - may implement this later...
            if seg[0] in ('TS3', 'TS2'):
                pass

            #---   DTP
            if seg[0] == 'DTM':
                if seg[1] == '405':  #production date of 835
                    self.dateProd = seg[2]
                if seg[1] == '036':  #coverage expiration
                    self.claim[claimNum].cvgExp = 'COVERAGE EXPIRATION: %s' % fixDateSlashes(seg[2])
                if seg[1] == '050':  #claim received date
                    self.claim[claimNum].dateRec = seg[2]
                if seg[1] in ('472', '150', '232'): #472 - Single date; 150 - 'from' service date; 232 - 'from' statement date
                    if lineNum > -1:
                        self.claim[claimNum].clmLine[lineNum].date1 = seg[2]
                    else:
                        self.claim[claimNum].date1 = seg[2]
                if seg[1] in ('151', '233'):        #151 - 'Through' service date; 233 - 'through' statement date
                    if lineNum > -1:
                        self.claim[claimNum].clmLine[lineNum].date2= seg[2]
                    else:
                        self.claim[claimNum].date2 = seg[2]

            if seg[0] == 'PER':  #Contact detatils
                if seg[1] == 'CX':
                    if loopNum == '1000A': #Payor Business contact
                        self.payorBizContact = seg[2] + " " + fixPhone(seg[4])
                    if loopNum == '2100':  #Claim contact
                        self.claim[claimNum].contact = seg[2] + " " + fixPhone(seg[4])
                if seg[1] == 'BL':  #Payor Technical contact
                    try:
                        self.payorTechContact = seg[2] + " " + fixPhone(seg[4])
                    except IndexError:
                        self.payorTechContact = ""
                if seg[1] == '1C':  #Payor website
                    self.payorWebsite = seg[4]

            #---   CLP - starts a claim
            if seg[0] == 'CLP':
                claimNum += 1
                lineNum = -1
                self.insType = cfiDict[seg[6]]
                tmpBilled = monetize(seg[3])
                tmpPaid = monetize(seg[4])
                tmpPatRsp = monetize(seg[5])
                newClaim = Claim(patAcct=seg[1], clmStatus=seg[2], amtBilled=tmpBilled, amtPaid=tmpPaid, amtPatResp=tmpPatRsp, ctrlNum=seg[7])
                self.claim.append(newClaim)
                self.totBilled += tmpBilled
                self.totProvPd += tmpPaid


            #---   CAS - Adjustment, either claim- or service-level
            if seg[0] == 'CAS':
                if loopNum == '2100':  #Claim-level adjustment
                    cas = self.claim[claimNum]
                if loopNum == '2110':  #Service-level adjustment
                    cas = self.claim[claimNum].clmLine[lineNum]
                for num in (2,5,8,11,14,17):
                    if len(seg) > num:
                        tmpCode = '%s%s' % (seg[1],seg[num])
                        self.grpGlossary[seg[1]] = casDict[seg[1]]
                        self.codeGlossary[seg[num]] = cf.lookup('CARC',seg[num])
                        cas.adjCodes.add(tmpCode)
                    if len(seg) > num+1:
                        self.totRCAmt += monetize(seg[num+1])
                        if seg[1] == 'PR': #Patient Responsibility
                            if seg[num] == '1': #Deductible
                                tmpDeduct = monetize(seg[num+1])
                                self.claim[claimNum].amtDeduct += tmpDeduct
                                self.totDeduct += tmpDeduct
                                if loopNum == '2110':
                                    #if len(self.claim[claimNum].clmLine) > 0:
                                    self.claim[claimNum].clmLine[lineNum].amtDeduct += tmpDeduct

                            if seg[num] == '2': #Co-Insurance
                                tmpCoIns = monetize(seg[num+1])
                                self.claim[claimNum].amtCoIns += tmpCoIns
                                self.totCoIns += tmpCoIns
                                if loopNum == '2110':
                                    self.claim[claimNum].clmLine[lineNum].amtCoIns += tmpCoIns

                        else:              #Everything else
                            tmpAdj = monetize(seg[num+1])
                            self.totProvAdj += tmpAdj
                            self.claim[claimNum].amtAdjust += tmpAdj
                            if len(self.claim[claimNum].clmLine) > 0:
                                self.claim[claimNum].clmLine[lineNum].amtAdjust += tmpAdj

            #--- AMT - Supplemental info/amount
            if seg[0] == 'AMT':
                if loopNum == '2100': #Claim supplemental info  AU, DY, F5, I, NL, ZK, ZL, ZM, ZN, ZO
                    tmpItem = self.claim[claimNum]
                if loopNum == '2110': #Service supplemental amount  B6, KH, ZK, ZL, ZM, ZN, ZO
                    tmpItem = self.claim[claimNum].clmLine[lineNum]
                if seg[1] == 'AU': #Coverage amount
                    tmpItem.amtCovered = monetize(seg[2])
                if seg[1] == 'DY': #Daily limit
                    tmpItem.dailyLimit = monetize(seg[2])
                if seg[1] == 'F5': #Patient paid amount
                    tmpItem.amtPatPaid = monetize(seg[2])
                if seg[1] == 'I': #Interest
                    tmpItem.amtInterest = monetize(seg[2])
                if seg[1] == 'NL': #Negative Ledger Balance - ?
                    tmpItem.amtNegLdgrBal = monetize(seg[2])
                if seg[1] == 'B6': #Allowed - Actual
                    self.claim[claimNum].clmLine[lineNum].amtAllowed = monetize(seg[2])
                    self.claim[claimNum].amtAllowed += monetize(seg[2])
                    self.totAllowed += monetize(seg[2])
                if seg[1] == 'KH': #Late Filing deduction
                    tmpItem.amtDeducted = monetize(seg[2])
                if seg[1] == 'ZK': #Federal Medicare or Medicaid Payment Mandate -Category 1
                    tmpItem.fedMandate1 = monetize(seg[2])
                if seg[1] == 'ZL': #Federal Medicare or Medicaid Payment Mandate -Category 2
                    tmpItem.fedMandate2 = monetize(seg[2])
                if seg[1] == 'ZM': #Federal Medicare or Medicaid Payment Mandate -Category 3
                    tmpItem.fedMandate3 = monetize(seg[2])
                if seg[1] == 'ZN': #Federal Medicare or Medicaid Payment Mandate -Category 4
                    tmpItem.fedMandate4 = monetize(seg[2])
                if seg[1] == 'ZO': #Federal Medicare or Medicaid Payment Mandate -Category 5
                    tmpItem.fedMandate5 = monetize(seg[2])

            #---   SVC - starts a service line
            if seg[0] == 'SVC':
                segOne = seg[1].split(self.subElemSep)
                lineNum += 1
                tmpMod = []
                for num in (2,3,4,5):
                    if len(segOne) > num: tmpMod.append(segOne[num])
                if len(tmpMod) == 0:
                    tmpMod.append('')
                tmpBilled=monetize(seg[2])
                tmpPaid=monetize(seg[3])
                try:
                    newLine = ClaimLine(paidProc=segOne[1], paidMod=tmpMod, amtBilled=tmpBilled, amtPaid=tmpPaid, paidUnits = seg[5])
                except IndexError: #Cigna workaround, 24Dec2014
                    newLine = ClaimLine(paidProc=segOne[1], paidMod=tmpMod, amtBilled=tmpBilled, amtPaid=tmpPaid)
                self.claim[claimNum].clmLine.append(newLine)
                self.claim[claimNum].totBilled += tmpBilled # checking our math!
                #self.totProvPd += tmpPaid

            if seg[0] == 'NM1':
                if seg[1] == 'QC':
                    self.claim[claimNum].patName = seg[3] + ", " + seg[4]
                    if len(seg) > 8:
                        self.claim[claimNum].patID = seg[9]
                if seg[1] == '82':
                    if len(seg) > 8:
                        self.claim[claimNum].rendID = seg[9]
                if seg[1] == 'TT':
                    self.claim[claimNum].fwdInfo = "CLAIM INFORMATION FORWARDED TO: "
                    self.claim[claimNum].xoverCarrier = seg[3]

            if seg[0] == 'MIA':  #Inpatient... maybe later?
                pass
            if seg[0] == 'MOA':
                for num in (3,4,5,6,7):
                    if len(seg) > num:
                        self.codeGlossary[seg[num]] = cf.lookup('RARC',seg[num])
                        self.claim[claimNum].adjCodes.add(seg[num])

            if seg[0] == 'PLB':  #Provider Level Adjustments
                provID = seg[1]
                fiscDate = seg[2]
                tmpPLB = ProviderLevelAdjustment(provID, fiscDate)
                for num in (3,5,7,9,11,13):
                    if len(seg) > num:
                        rsnCode = seg[num].split(subElemSep)[0]
                        self.codeGlossary[rsnCode] = plbDict[rsnCode]
                        plbID = ''
                        try:
                            plbID = seg[num].split(subElemSep)[1]
                        except IndexError:
                            pass
                        monAmt = seg[num+1]
                        tmpPLB.sub.append(SubPLB(rsnCode, plbID, monAmt))
                        self.totProvAdj += monetize(monAmt)
                self.plb.append(tmpPLB)

            if seg[0] == 'LQ':  #Health Care Remark Codes
                self.claim[claimNum].clmLine[lineNum].adjCodes.add(seg[2])
                if seg[1] == 'HE': #Claim Payment Remark Codes
                    self.codeGlossary[seg[2]] = cf.lookup('RARC',seg[2])
                if seg[1] == 'RX': #NCPDP codes: I don't have those
                    self.codeGlossary[seg[2]] = "This code comes from the NCPDP code table, which I don't yet have."



    def toPDF(self):
        pdfSet = PDFSettings()
        pdfSet.pdfDir=self.pdfDir
        pdfSet.verNum=self.verNum
        pdfSet.addStyles()
        cW = pdfSet.cW
        lH = pdfSet.lineHeight
        pdfSet.payorName = self.payorName
        pdfSet.payorAdd1 = self.payorAdd1
        pdfSet.payorCSZ = self.payorCSZ
        pdfSet.payorBizContact = self.payorBizContact
        pdfSet.payorTechContact = self.payorTechContact

        pdfSet.payeeID = self.payeeID
        pdfSet.payeeName = self.payeeName
        pdfSet.payeeAdd1 = self.payeeAdd1
        pdfSet.payeeAdd2 = self.payeeAdd2
        pdfSet.payeeCSZ = self.payeeCSZ

        pdfSet.insType = self.insType
        pdfSet.chkNum = self.chkNum
        pdfSet.chkDate = self.chkDate
        pdfSet.inFileName = self.inFileName

        fileNameBase = pdfSet.pdfDir + os.sep + '835' + self.chkNum
        fileName = fileNameBase + '.pdf'
        doc = SimpleDocTemplate(fileName, pagesize=letter,
                                leftMargin=pdfSet.marginSize, rightMargin=pdfSet.marginSize,
                                topMargin=pdfSet.marginSize + 4 * pdfSet.lineHeight,
                                bottomMargin=pdfSet.bottomMargin)

        doc.leftPadding = 0
        Story = []
        Story.append(Spacer(1, lH*7))

        stylesheet=getSampleStyleSheet()
        codeStyle = copy.copy(stylesheet['Normal'])
        codeStyle.fontName = pdfSet.regFont
        codeStyle.fontSize = pdfSet.fontSize
        codeStyle.borderPadding = 0
        codeStyle.leading = 8

        style1 = copy.copy(stylesheet['Normal'])
        style1.fontName = pdfSet.regFont
        style1.fontSize = pdfSet.fontSize
        style1.borderPadding = 0
        #codeStyle.leading = 8
        style2 = copy.copy(style1)
        style2.firstLineIndent = -15
        style2.leftIndent = 20
        style3 = copy.copy(style1)
        style3.fontName = pdfSet.boldFont

        for num, clm in enumerate(self.claim):
            #--- ClaimHeader
            if self.insType.split(' ')[0] == 'MEDICARE':
                idString = 'HIC'
            else:
                idString = 'ID#'
            Claim = []
            codes = Paragraph(" ".join(clm.adjCodes), style=codeStyle)
            hdrData = [(str(num+1), None, clm.patAcct, clm.patName, idString, clm.patID, 'ICN', clm.ctrlNum, codes)]
            tbl = Table(hdrData, colWidths=pdfSet.clmHeaderWidths, rowHeights=None, style=pdfSet.styles['clmHeader'])
            tbl.hAlign = 'LEFT'
            tbl.leftPadding = 0
            Claim.append(tbl)
            #--- ClaimLines
            lineData = []
            if len(clm.clmLine) == 0:
                tmpLine = list(14*[None])
                tmpLine[1]  = fixDateSlashes(clm.date1, forceYear = 2)
                tmpLine[2]  = fixDateSlashes(clm.date2, forceYear = 2)
                tmpLine[5]  = '-----'
                lineData.append(tmpLine)
            for svc in clm.clmLine:
                tmpLine = list(14*[None])
                tmpLine[0]  = clm.rendID
                tmpLine[1]  = fixDateSlashes(svc.date1, forceYear = 2)
                tmpLine[2]  = fixDateSlashes(svc.date2, forceYear = 2)
                tmpLine[3]  = svc.POS
                tmpLine[4]  = svc.paidUnits
                tmpLine[5]  = svc.paidProc
                #svc.paidMod = ['11', '22']
                tmpLine[6]  = Paragraph(" ".join(svc.paidMod), style=codeStyle)
                tmpLine[7]  = svc.amtBilled
                tmpLine[8]  = svc.amtAllowed
                tmpLine[9]  = svc.amtDeduct
                tmpLine[10] = svc.amtCoIns
                tmpLine[11] = Paragraph(" ".join(svc.adjCodes), style=codeStyle)
                tmpLine[12] = svc.amtAdjust
                tmpLine[13] = svc.amtPaid
                lineData.append(tmpLine)
            try:
                tbl = Table(lineData, colWidths=pdfSet.clmLineWidths, rowHeights=None, style=pdfSet.styles['clmLine'])
            except:
                print '!'
            tbl.hAlign = 'LEFT'
            tbl.leftPadding = 0
            Claim.append(tbl)
            #--- ClaimFooter1
            ftr1Data = [('PT RESP', clm.amtPatResp, '   CLAIM TOTALS', clm.amtBilled, clm.amtAllowed, clm.amtDeduct, clm.amtCoIns, None, clm.amtAdjust, clm.amtPaid)]
            tbl = Table(ftr1Data, colWidths=pdfSet.clmFooter1Widths, rowHeights=None, style=pdfSet.styles['clmFooter1'])
            tbl.hAlign = 'LEFT'
            tbl.leftPadding = 0
            Claim.append(tbl)
            #--- ClaimFooter2
            if clm.contact:
                if clm.fwdInfo:
                    ftr2Data = [(clm.contact, None, None, None)]
                    ftr2Data.append([clm.fwdInfo, clm.xoverCarrier, 'NET', clm.amtPaid])
                else:
                    ftr2Data = [(clm.contact, None, 'NET', clm.amtPaid)]
            else:
                ftr2Data = [(clm.fwdInfo, clm.xoverCarrier, 'NET', clm.amtPaid)]
            tbl = Table(ftr2Data, colWidths=pdfSet.clmFooter2Widths, rowHeights=None, style=pdfSet.styles['clmFooter2'])
            tbl.hAlign = 'LEFT'
            tbl.leftPadding = 0
            Claim.append(tbl)
            Story.append(KeepTogether(Claim))
            Story.append(Spacer(1,lH))

        #PLB section
        if len(self.plb) > 0:
            # Re-use rptFooter stuff - why not?
            pdfSet.rptFooterWidths = [13*cW, 10*cW, 6*cW, 31*cW, 12*cW, 5*cW,    4*cW, 31*cW, 12*cW, 2*cW]
            pdfSet.styles['rptFooter'].add('FONT', (0,0), (-1,-1), pdfSet.regFont, pdfSet.fontSize)
            pdfSet.styles['rptFooter'].add('ALIGN', (0,0), (-1, -1), 'RIGHT')
            tmpSec = []
            tmpSec.append(Paragraph("Provider-level Adjustments:", style3))
            lineData = [("Provider", "Date", "Code", "Financial Control#  /  Account", "Amount", "",    "Code", "Financial Control#  /  Account", "Amount")]
            for adj in self.plb:
                tmpLine = list(10*[None])
                tmpLine[0] = adj.provID
                tmpLine[1] = adj.fiscDate
                count = 0
                for sub in adj.sub:
                    count +=1
                    if count % 2 == 1: #odd items go on the left, with a newline if necessary; provID and date only on first line
                        if count > 1:
                            lineData.append(tmpLine)
                            tmpLine = list(10*[None])
                        tmpLine[2] = sub.rsnCode
                        tmpLine[3] = sub.plbID
                        tmpLine[4] = sub.monAmt
                    else:              #even items go on the right
                        tmpLine[6] = sub.rsnCode
                        tmpLine[7] = sub.plbID
                        tmpLine[8] = sub.monAmt
                lineData.append(tmpLine) #write out the last line
            tmpSec.append(Table(lineData, colWidths=pdfSet.rptFooterWidths, rowHeights=None, style=pdfSet.styles['rptFooter']))
            Story.append(KeepTogether(tmpSec))
            Story.append(Spacer(1,2*lH))

        #--- ReportFooter
        pdfSet.rptFooterWidths = [13*cW, 13*cW, 14*cW, 14*cW, 13*cW, 14*cW, 14*cW, 13*cW, 13*cW]
        pdfSet.styles['rptFooter'].add('FONT', (0,2), (-1,-1), pdfSet.boldFont, pdfSet.fontSize)
        pdfSet.styles['rptFooter'].add('ALIGN', (0,0), (-1, -1), 'RIGHT')
        pdfSet.styles['rptFooter'].add('ALIGN', (1,2), (-1,-1), 'DECIMAL')

        rptFooter = []
        tmpLine = [("TOTALS:     # OF", "BILLED", "ALLOWED", "DEDUCT", "COINS", "TOTAL", "PROV PD", "PROV", "CHECK"),
                   (        "CLAIMS", "AMT",     "AMT",      "AMT",    "AMT", "RC-AMT", "AMT",   "ADJ AMT", "AMT"),
                   (len(self.claim), self.totBilled, self.totAllowed, self.totDeduct, self.totCoIns,
                    self.totRCAmt, self.totProvPd, self.totProvAdj, self.totCheckAmt)]
        rptFooter.append(Table(tmpLine, colWidths=pdfSet.rptFooterWidths, rowHeights=None, style=pdfSet.styles['rptFooter']))
        Story.append(KeepTogether(rptFooter))
        Story.append(Spacer(1,2*lH))


        #--- Glossary
        tmpSec = []
        tmpSec.append(Paragraph("GLOSSARY: Group, Reason, MOA, Remark and Adjustment codes", style3))

        for gloss in (self.grpGlossary, self.codeGlossary):
            if len(gloss) > 0:
                for key in sorted_nicely(gloss.iterkeys()):
                    tmpPara = "%s: %s " % (key, gloss[key])
                    tmpSec.append(Paragraph(tmpPara, style2))
        Story.append(KeepTogether(tmpSec))


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
    from X12Thing import Not_X12
    from tempfile import gettempdir
    ediDir = r'C:\Users\Marc\Desktop\now'
    codeFile = r'C:\Dropbox\fsrPy\codeTable.db'
    outDir = r'C:\Users\Marc\Desktop'

    for inObj in os.listdir(ediDir):
        ediFile = ediDir + os.sep + inObj
        if os.path.isdir(ediFile): continue
        try:
            print(ediFile)
            thingy = X12Thing(ediFile)
        except Not_X12:
            print("%s is not an X12 file" % ediFile)
            continue
        for gsLoop in thingy.GSLoop:
            verNum = gsLoop.GSRec[8]
            print(verNum)
            for stLoop in gsLoop.STLoop:
                print(stLoop.STRec[1])
                if stLoop.STRec[1] == '835':
                    thisX12= X12_835(stLoop, verNum, thingy.SubElemSep, thingy.inFileName, thingy.testProd, codeFile, outDir)
                    thisX12.toPDF()

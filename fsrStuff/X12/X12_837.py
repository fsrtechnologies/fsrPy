from X12Thing import X12Thing, X12Error
from Carrier import Carrier
import urllib, copy, time, os
try:
    import MBIFinder
except ImportError:
    from .. import MBIFinder
try:
    from fsrStuff.NPIFile import NPIFile
except ImportError:
    from NPIFile import NPIFile
try:
    from fsrStuff.umFuncs import RecordGenerator, RecordGeneratorB, parseDirectDat
except ImportError:
    from umFuncs import RecordGenerator, RecordGeneratorB, parseDirectDat


class Global(object):
    hLevel = ''
    ins = ''
    loopNum = '0000'

def dictList(inDict):
    for v, k in inDict.iteritems():
        print '{}: {}'.format(v, k)
    print '==============================\n'

def getLoop(seg=[], loopNum='0000'):
    if seg[0] == 'BHT':                                     #Beginning
        Global.hLevel = ''
        Global.ins = ''
        return '0000'
    if seg[0] == 'NM1' and seg[1] == '41': return '1000A'       #Submitter
    if seg[0] == 'NM1' and seg[1] == '40': return '1000B'       #Receiver
    if seg[0] == 'HL'  and seg[3] == '20':                      #Billing Provider
        Global.hLevel = 'Billing'
        return '2000A'
    if seg[0] == 'NM1' and seg[1] == '85':                      #Billing Provider Name
        if Global.ins == 'Other':  return '2330G'
        else: return '2010AA'
    if seg[0] == 'NM1' and seg[1] == '87': return '2010AB'      #Pay-to Address
    if seg[0] == 'NM1' and seg[1] == 'PE': return '2010AC'      #Pay-to Plan
    if seg[0] == 'HL'  and seg[3] == '22':                      #Subscriber Level
        Global.hLevel  = 'Subscriber'
        Global.ins     = 'Receiver'
        return '2000B'
    if seg[0] == 'NM1' and seg[1] == 'IL':                      # Subscriber Name
        if Global.ins == 'Other':  return '2330A'
        else: return '2010BA'
    if seg[0] == 'NM1' and seg[1] == 'PR':                      # Payor
        if Global.ins == 'Other':  return '2330B'
        else: return '2010BB'
    if seg[0] == 'CLM':                                         #Claim level
        Global.hLevel  = 'Claim'
        return '2300'
    if seg[0] == 'HL'  and seg[3] == '23':                      # Patient Level
        Global.hLevel  = 'Patient'
        Global.ins     = 'Receiver'
        return '2000C'
    if seg[0] == 'NM1' and seg[1] == 'QC': return '2010CA'      #Patient Name
    if seg[0] == 'NM1' and seg[1] in ('DN', 'P3'):              #Referring
        if Global.ins == 'Other':    return '2330C'
        if Global.hLevel == 'SvcLn': return '2420F'
        else: return '2310A'
    if seg[0] == 'NM1' and seg[1] == '82':                      #Rendering Provider
        if Global.ins == 'Other':    return '2330D'
        if Global.hLevel == 'SvcLn': return '2420A'
        else: return '2310B'
    if seg[0] == 'NM1' and seg[1] in ('FA', 'LI', 'TL', '77'):  #Service Facility Location
        if Global.ins == 'Other':    return '2330E'
        if Global.hLevel == 'SvcLn': return '2420C'
        else: return '2310C'
    if seg[0] == 'NM1' and seg[1] == 'DQ':                      #Supervising Provider
        if Global.ins == 'Other':  return '2330F'
        if Global.hLevel == 'SvcLn': return '2420D'
        else: return '2310D'
    if seg[0] == 'NM1' and seg[1] == 'PW':                      #Ambulance Pick-Up
        if Global.hLevel == 'SvcLn': return '2420G'
        return '2310E'
    if seg[0] == 'NM1' and seg[1] == '45':                      #Ambulance Drop-Off
        if Global.hLevel == 'SvcLn': return '2420H'
        return '2310F'
    if seg[0] == 'SBR' and Global.hLevel == 'Claim':            #Other Subscriber
        Global.ins = 'Other'
        return '2320'
    if seg[0] == 'LX':                                          #Service Line Number
        Global.hLevel = 'SvcLn'
        return '2400'
    if seg[0] == 'NM1' and seg[1] == 'QB': return '2310F'       #Purchased Service Provider
    if seg[0] == 'LIN': return '2410'                           #Drug Identification
    if seg[0] == 'NM1' and seg[1] == 'DK': return '2420E'       #Ordering Provider
    if seg[0] == 'SVD': return '2430'                           #Line Adjudication Info
    if seg[0] == 'LQ':  return '2440'                           #Form Identification

    return loopNum                                              #if nothing else matched



class X12_837(X12Thing):
    def loopPrint(self, fileName='dump837'):
        """
        Dumps the 837 to text; prints the loop number (e.g. 2330) and position (aka line number minus wrapper) in the left margin
        """
        segTerm = self.SegTerm + "\n"
        outList = [self.ElemSep.join(self.ISARec)]
        for index, loop1 in enumerate(self.GSLoop):
            outList.append("   " + self.ElemSep.join(loop1.GSRec))
            for i2, loop2 in enumerate(loop1.STLoop):
                loopNum = ''
                outList.append("      " + self.ElemSep.join(loop2.STRec))
                for i3, seg in enumerate(loop2.TSet):
                    loopNum = getLoop(seg, loopNum)
                    outRec = '{:>7} {:>7} {}'.format(i3+3, loopNum, self.ElemSep.join(seg))
                    outList.append(outRec)
                outList.append("      " + self.ElemSep.join(loop2.SERec))
            outList.append("   " + self.ElemSep.join(loop1.GERec))
        outList.append(self.ElemSep.join(self.IEARec))
        outList = segTerm.join(outList)
        if (outList[-1] != segTerm):  # make sure IEA record ends with a tilde
            outList = outList + segTerm
        with open(fileName, 'w+b') as outFile:
            outFile.write(outList)


    def FixSSN(self):
        """
        When the rendering provider's SSN starts with zero(s), UltraMed truncates it.
        This restores the leading zeroes.
        """
        for loop1 in self.GSLoop:
            for loop2 in loop1.STLoop:
                for index, seg in enumerate(loop2.TSet):
                    if (seg[0] == 'NM1') and (seg[1]=='85') and (seg[8]=='34'):
                        loop2.TSet[index][9] = seg[9].zfill(9)


    def SubstMBI(self, offNum = '01', location = os.getcwd()):
        """
        New Medicare Beneficiary ID can't be stored in (legacy) UltraMed's Medicare ID field, so we're storing it
            in the Message 2 field.
        """
        with MBIFinder.MBIFinder(offNum, location) as mf:
            self.noMBI = {}
            mf.loadTable()  # load MBIs from UltraMed to db, collect dict of bad MBIs
            self.badMBI = mf.badMBI
            for index, loop1 in enumerate(self.GSLoop):
                for i2, loop2 in enumerate(loop1.STLoop):
                    newTSet = []  # We'll be changing things a bit, so make a new list and write stuff to it
                    bNeedMBI = False
                    insuredNM1 = []
                    holdLines = []
                    for i3, seg in enumerate(loop2.TSet):
                        if not bNeedMBI:
                            if seg[0] == 'NM1' and seg[1] == 'IL' and seg[9] == '000000000A':
                                bNeedMBI = True
                                insuredNM1 = seg
                            else:
                                newTSet.append(seg)
                        else: # if we DO need a new MBI
                            if seg[0] == 'CLM':
                                MBI = mf.lookup(seg[1])
                                if MBI:
                                    insuredNM1[9] = MBI
                                else:
                                    self.noMBI[seg[1]] = insuredNM1[9]
                                newTSet.append(insuredNM1)
                                insuredNM1 = []
                                newTSet.append(holdLines)
                                holdLines = []
                                newTSet.append(seg)
                                bNeedMBI = False
                            else:
                                holdLines.append(seg)

    def PatientHome2310C(self):
        """
        When services are rendered in patient's home (POS code 12), need to create 2310C loop and copy patient's address there.
        Grab subscriber's address; supercede with patient's if appropriate
        """
        for index, loop1 in enumerate(self.GSLoop):
            for i2, loop2 in enumerate(loop1.STLoop):
                newTSet = []  # We'll be changing things a bit, so make a new list and write stuff to it
                bWriteNM1 = False
                loopNum = ''
                segNM1 = []
                segN3 = []
                segN4 = []
                for i3, seg in enumerate(loop2.TSet):
                    bCopy = True
                    loopNum = getLoop(seg, loopNum)
                    if (loopNum in ['2010BA', '2010CA'] ): # patient comes after subscriber, so should automatically supersede
                        if seg[0] == 'NM1':
                            segNM1 = ['NM1', '77', '2', seg[3]]
                        if seg[0] == 'N3':
                            segN3 = seg
                        if seg[0] == 'N4':
                            segN4 = seg
                    if (seg[0] == 'CLM'):
                        if seg[5][:2] == '12':
                            bWriteNM1 = True
                        else:
                            bWriteNM1 = False
                    if (loopNum in ['2310D', '2310E', '2310F', '2320', '2330A',
                        '2330B', '2330C', '2330D', '2330E', '2330F',
                        '2330G', '2400'] ) and bWriteNM1:  # anywhere below rendering and above service detail lines
                        newTSet.append(segNM1)
                        newTSet.append(segN3)
                        newTSet.append(segN4)
                        bWriteNM1 = False
                    newTSet.append(seg)
                loop1.STLoop[i2].TSet = newTSet # Replace the original TSet with our modified one


    def NPIConversion(self, UseSecID=False, KeepLicense=False, KeepInsID=False, KeepTaxID=True, KeepUxIN=False, KeepFacID=False, Cvt5010=True):
        """
        Look for legacy provider ID codes and replace/supplement them with equivalent NPI numbers.
        In some cases this involves adding extra REF records, which may belong higher or lower in the file hierarchy
        than the existing legacy codes.

        Under the 5010 rules, Billing Providers and Pay-To Plans require a REF with the tax ID; all other additional
        identifiers must be dropped.

        Also
        """
        if Cvt5010:  #5010 rule overrides all others
            KeepLicense=False
            KeepInsID=False
            KeepTaxID=False
            KeepUxIN=False
            KeepFacID=False

        self.npiMap = NPIFile(urllib.url2pathname(str(self.npiMapFile)))
        self.npiMap.Load()
        try: pass
        except:
            raise X12Error('Error loading NPI map')

        #Create sets outside of loop to avoid recursion overhead
        IdentifierSet   = set(['N2', 'N3', 'N4', 'PRV'])  #these segments follow/amplify an NM1 segment
        REFtestSet      = set(['0B', '1A', '1B', '1C', '1D', '1G', '1H', '1J', 'B3', 'BQ', 'EI', 'FH', 'G2', 'G5', 'LU', 'N5', 'SY', 'U3', 'X5'])
        NM1testSet      = set(['77', '82', '85', '87', 'DK', 'DN', 'DQ', 'FA', 'LI', 'TL', 'P3'])  # any of these values in NM1[01] triggers an NPI substitution in NM1[09]
        # Legacy types to keep or not keep:
        LicenseSet      = set(['0B'])  # made this a set for consistency's sake
        TaxIDSet        = set(['EI', 'SY'])
        InsIDSet        = set(['1A', '1B', '1C', '1D', '1H', 'B3', 'BQ', 'G2', 'X5'])
        UxINSet         = set(['1G', 'U3'])
        FacIDSet        = set(['1J', 'FH', 'G5', 'LU'])
        # NM1 types that need EIN/TIN in REF under 5010 rules
        Tax5010Set      = set(['85','PE']) #PE is 'Pay-to Plan' - ignoring for now
        '''
        # -  This seems to be superseded - apparently Medi-Cal _does_ want referral source NPIs now
        if (self.ISARec[8] == "610442         "):   # ignore DN records for Medi-Cal
            NM1testSet      = set(['77', '82', '85', '87', 'DQ', 'FA', 'LI', 'TL', 'P3'])
        '''
        for loop1 in self.GSLoop:
            for i2, loop2 in enumerate(loop1.STLoop):
                newTSet = []  # We'll be changing things a bit, so make a new list and write stuff to it
                needREF = False
                needNPI = 0
                needTax = False
                noLegacy = False  # Signifies an NM1 record for which I can't find a legacy code to use for NPI lookup
                tmpREF  = ['REF', '', '']
                for seg in loop2.TSet:
                    if (seg[0] in IdentifierSet):  #i.e., if it's N2/N3/N4 or PRV
                        newTSet.append(seg)
                    elif (seg[0] == 'REF'):
                        if needREF:
                            if ((seg[1] == tmpREF[1]) and (seg[2] == tmpREF[2])):  # If this REF record is already the same as the new
                                needREF = False                                    # REF record we were preparing - then don't bother
                                tmpREF = ['REF', '', '']
                        if (needNPI > 0):
                            if (seg[1] in REFtestSet):
                                tmpChk = self.npiMap.lookup(seg[2], name=newTSet[needNPI][3], nm1Type=newTSet[needNPI][1])["NPI"]
                                if tmpChk:  # did NPI lookup succeed?
                                    while (len(newTSet[needNPI]) < 10): # make sure that NM1 record is long enough to hold NPI
                                        newTSet[needNPI].append('')
                                    newTSet[needNPI][8]  = 'XX'
                                    newTSet[needNPI][9]  =copy.copy(tmpChk)
                                    noLegacy = False

                        #  To implement NPI-only policy, we need to drop the REF records that contain legacy codes -
                        if (not (seg[1] in REFtestSet)): newTSet.append(seg) #if REF01 is anything but one of the legacy codes, add it and move on
                        elif ((seg[1] in TaxIDSet) and (Cvt5010 and needTax)): newTSet.append(seg) #if we're doing 5010, and this is the Billing Provider, keep tax ID
                        elif ((seg[1] in LicenseSet) and KeepLicense): newTSet.append(seg)
                        elif ((seg[1] in TaxIDSet) and KeepTaxID): newTSet.append(seg)
                        elif ((seg[1] in InsIDSet) and KeepInsID): newTSet.append(seg)
                        elif ((seg[1] in FacIDSet) and KeepFacID): newTSet.append(seg)
                        elif ((seg[1] in UxINSet) and KeepUxIN): newTSet.append(seg)

                    else:  # treating NM1 as a special case of 'else'
                        #  When we come to where we'd normally insert a newly created REF -
                        #    IF (we're keeping legacy codes), then append it; either way, clean up for next time.
                        if needREF:
                            if ((tmpREF[1] in TaxIDSet) and (Cvt5010 and needTax)): newTSet.append(tmpREF)
                            elif ((tmpREF[1] in LicenseSet) and KeepLicense): newTSet.append(tmpREF)
                            elif ((tmpREF[1] in TaxIDSet) and KeepTaxID): newTSet.append(tmpREF)
                            elif ((tmpREF[1] in InsIDSet) and KeepInsID): newTSet.append(tmpREF)
                            elif ((tmpREF[1] in FacIDSet) and KeepFacID): newTSet.append(tmpREF)
                            elif ((tmpREF[1] in UxINSet) and KeepUxIN): newTSet.append(tmpREF)

                            needREF = False
                            tmpREF = ['REF', '', '']
                        if (seg[0] == 'NM1'):
                            if seg[1] in Tax5010Set:
                                needTax = True
                            else:
                                needTax = False
                            """
                            try:
                                if seg[8] == 'XX':  # if there's already an NPI, move along
                                    continue
                            except: pass  # don't blow up if this line is too short
                            """
                            if noLegacy:
                                if len(noLegacy) > 4:
                                    tmpName = noLegacy[3] + ", " + noLegacy[4]
                                else:
                                    tmpName = noLegacy[3]
                                self.noLegs[noLegacy[1] + tmpName] = self.npiMap.nm1Types[noLegacy[1]] + ": " + tmpName
                                noLegacy = False
                            if (seg[1] in NM1testSet):
                                if (len(seg) > 9):  # if there was already an ID number associated with this record,
                                    tmpREF[1]   = seg[8]   # then this record will have segments 8 and 9 -
                                    tmpREF[2]   = seg[9]   # grab old ID from there and move it to new REF record we're creating
                                    tmpSeg = copy.copy(seg)
                                    tmpChk = self.npiMap.lookup(seg[9], name=seg[3], nm1Type=seg[1])["NPI"]  # we already have the legacy code and type, so we only need the NPI portion

                                    seg[8] = seg[9]  = ''  # if segment 9 is empty but 8 isn't, ENTIRE FILE gets deleted. Don't do that!
                                    if (seg[1] == '82') and UseSecID:  # this is a rendering  record - if "Use Secondary ID", save the EIN/SSN but wait to match NPI against ind. Medicare ID
                                        noLegacy = tmpSeg  # just in case there isn't any secondary ID to use - I doubt it...
                                        needNPI = len(newTSet) # length just before append == index of NM1 record that needs an NPI
                                    else:
                                        if tmpChk:  # did NPI lookup succeed?
                                            seg[8] = 'XX'
                                            seg[9] = copy.copy(tmpChk)
                                    needREF = True
                                    if   (tmpREF[1] == '24'):  #EIN
                                        tmpREF[1] = 'EI'
                                    elif (tmpREF[1] == '34'):  #SSN
                                        tmpREF[1] = 'SY'
                                    elif (tmpREF[1] == 'XX'):  #Already an NPI, don't need a new REF record - this will probably never happen
                                        needREF = False
                                else: # segments 8 and 9 don't exist, and we don't have a legacy code to work with yet
                                    noLegacy = copy.copy(seg)
                                    needNPI  = len(newTSet) # length just before append == index of NM1 record that needs an NPI
                        newTSet.append(seg)
                loop1.STLoop[i2].TSet = newTSet  # replace original TSet with our modified one

    def ProcessNTE(self):
        """
        Look for 'NDC#', 'F2', 'GR', 'ME', 'ML, 'UN' in NTE record (would be entered in 'Box19a' area of Ailment record in UltraMed)
        This will be at the Claim level (loop 2300), but needs to be turned into LIN record at Transaction level (loop 2410)
        If there's anything else in the NTE, leave it in place; if not, delete the NTE record (i.e, don't copy it to newTSet.)
        """
        for index, loop1 in enumerate(self.GSLoop):
            for i2, loop2 in enumerate(loop1.STLoop):
                newTSet = []  # We'll be changing things a bit, so make a new list and write stuff to it
                bWriteLIN = False
                bWriteCTP = False
                loopNum = ''
                for i3, seg in enumerate(loop2.TSet):
                    bCopy = True
                    loopNum = getLoop(seg, loopNum)
                    if (seg[0] == 'NTE'):
                        tmpList = seg[2].split(' ')
                        newNTE = []
                        for tmpStr in tmpList:
                            if (tmpStr[:3] == 'NDC'):
                                segLIN = ['LIN', '', 'N4', tmpStr[3:]]
                                bWriteLIN = True
                            elif (tmpStr[:2] in ['F2', 'GR', 'ME', 'ML', 'UN']) and (len(tmpStr) > 11) and (tmpStr[2:12].isdigit()):
                                segCTP = ['CTP', '', '', '', tmpStr[2:12], tmpStr[:2]]
                                bWriteCTP = True
                            elif (len(tmpStr) > 0):  #in case of an odd number of spaces, skip it
                                newNTE.append(tmpStr)
                        if len(newNTE) > 1:
                            seg[2] = ' '.join(newNTE)
                        else: bCopy = False
                    if bWriteLIN:
                        if (seg[0] == 'LX') and (int(seg[1]) > 1): # next transaction, same claim - we want to write the NDC on that one, too, so don't un-set
                            newTSet.append(segLIN)
                        if (seg[0] == 'HL') or (int(loopNum[:4]) > 2410): #HL starts a new claim; LIN needs to be before loop numbers in the 2420 range
                            newTSet.append(segLIN)
                            bWriteLIN = False
                    if bWriteCTP:
                        if (seg[0] == 'LX') and (int(seg[1]) > 1): # next transaction, same claim - we want to write the NDC on that one, too, so don't un-set
                            newTSet.append(segCTP)
                        if (seg[0] == 'HL') or (int(loopNum[:4]) > 2410): #HL starts a new claim; LIN needs to be before loop numbers in the 2420 range
                            newTSet.append(segCTP)
                            bWriteCTP = False
                    if bCopy:
                        newTSet.append(seg)
                if bWriteLIN:  # if we hit the end and still need to write LIN record
                    newTSet.append(segLIN)
                if bWriteCTP:  # if we hit the end and still need to write CTP record
                    newTSet.append(segCTP)
                loop1.STLoop[i2].TSet = newTSet # Replace the original TSet with our re-arranged one


    def SubmitterSubst(self, SubNum='000000000'):
        """
        Perform updates for various carriers...
        - Place the carrier code and submitter number in the appropriate fields (in case they're not already...)
        - Cigna DMERC junk
        """
        self.ISARec[6] = SubNum.ljust(15)
        for index, loop1 in enumerate(self.GSLoop):
            self.GSLoop[index].GSRec[2] = SubNum
            for loop2 in loop1.STLoop:
                for i3, seg in enumerate(loop2.TSet):
                    if (seg[0] == 'NM1'):
                        if  (seg[1]=='41'): # 1000A Submitter
                            loop2.TSet[i3][9] = SubNum

    def CarrierConversion(self, ShortName = "Jur. E SoCal"):
        """
        Perform updates for various carriers...
        - Place the carrier code, name, and interchange ID qualifier in the appropriate fields (in case they're not already...)
        - Cigna DMERC junk
        """

        CarrierName = Carrier.carDict[ShortName]["LongName"]
        CarrierCode = Carrier.carDict[ShortName]["PayorID"]
        CarrierIQ = Carrier.carDict[ShortName]["IQ"]
        CarrierDME = Carrier.carDict[ShortName]["DME"]

        self.ISARec[5] = CarrierIQ
        self.ISARec[7] = CarrierIQ
        self.ISARec[8] = CarrierCode.ljust(15)

        for index, loop1 in enumerate(self.GSLoop):
            self.GSLoop[index].GSRec[3] = CarrierCode
            for i2, loop2 in enumerate(loop1.STLoop):
                newTSet = []  # We'll be changing things a bit, so make a new list and write stuff to it
                loopNum = ''
                for i3, seg in enumerate(loop2.TSet):
                    loopNum = getLoop(seg, loopNum)
                    bCopy = True
                    bWriteOrdering = False
                    if (seg[0] == 'NM1'):
                        if  (seg[1]=='40'):  # 1000B Receiver
                            loop2.TSet[i3][3] = CarrierName
                            loop2.TSet[i3][9] = CarrierCode
                        elif  (seg[1]=='85'): # 2010AA Billing Provider
                            """ # Appears not to be required anymore - 24Dec2008
                            if CarrierDME:
                                loop2.TSet[i3][8] = '24'  #EIN
                            """
                        elif  (seg[1]=='DN'): # 2310A Referring Provider
                            if CarrierDME:
                                self.DME = True
                                loop2.TSet[i3][1] = 'DK' # Ordering Provider
                                SegNM1DK = seg  # Hold on to this for later
                                bCopy = False
                        elif  (seg[1]=='PR'): # Payer - but which kind?
                            if loopNum == '2010BB': # Payer - but not Other payer
                                while (len(loop2.TSet[i3])<10):  # field 9 may not exist yet - remember we start at 0
                                    loop2.TSet[i3].append('')
                                #if (loop2.TSet[i3][3] == 'MEDICARE') or (CarrierName == 'CignaDMERC') or (CarrierName == 'ColoradoMedicare') or (CarrierName == 'ColoradoMedicaid') or (CarrierName == 'MinnesotaMedicare'): # careful - might be secondary insurance!
                                loop2.TSet[i3][9] = CarrierCode
                    if CarrierDME:
                        if (seg[0] == 'REF'):
                            if  (seg[1]=='1G'):  # Billing Provider ID
                                SegREF1G = seg     # Hold on to this for later
                                bCopy = False
                            if  (seg[1]=='6R'): # Line Item Control Number - e.g. inventory number
                                bWriteOrdering = True
                        if bCopy:
                            newTSet.append(seg)
                        if bWriteOrdering:  # Write the ordering and billing info, after the line item control number
                            newTSet.append(SegNM1DK)
                            try:
                                newTSet.append(SegREF1G)  # if we're not keeping legacy codes, this won't exist...
                            except: pass
                if CarrierDME:
                    loop1.STLoop[i2].TSet = newTSet # Replace the original TSet with our re-arranged one

    def DNtoDQ(self):
        """
        Converts referring provider (DN) to supervising provider (DQ) - required for physical therapy.
        """
        self.PT = True
        for loop1 in self.GSLoop:
            for loop2 in loop1.STLoop:
                for index, seg in enumerate(loop2.TSet):
                    if (seg[0] == 'NM1') and (seg[1]=='DN'):
                        loop2.TSet[index][1] = 'DQ'

    def addTraceNumber(self):
        """
        ST02 and BHT03 can be used for tracking, but are wasted by default...
        Python's time.time() resolves to milliseconds, so I multiply by 100
        """
        traceNum = int(time.time())*1000
        for loop1 in self.GSLoop:
            for loop2 in loop1.STLoop:
                loop2.STRec[2] = self.traceNum = hex(traceNum)[-10:-1].upper()
                for index, seg in enumerate(loop2.TSet):
                    if (seg[0] == 'BHT'):
                        loop2.TSet[index][3] = hex(traceNum)[-10:-1].upper()
                        traceNum += 1

    def doICD10(self, office, gemFile=''):
        """
        Process diagnoses in 837 file as ICD10 instead of ICD9.
            UltraMed is only passing through first 5 characters of code, so we have to
                look inside TRN file to find intended code, and look it up in DIA.
            UltraMed is also sometimes passing empty diagnosis codes, so we have to rebuild
                the HI lines (with lists of diagnoses) and
                the SV1 lines (with pointers to diagnoses in HI lines)
            - Load DIA file to a dictionary. (Note whether codes are 9 or 10, based on "ICD format?" - if Y then 9; if N then 10)
            - Read billing file and build dictionary of claim:HI, SV1, diags[empty]
            - Read TRN file and get in-house DIA codes for each claim in dictionary
            - Rebuild HI line and SV1 line(s) based on diag fields from TRN file - ignore blanks/bad pointers in billing file
            - Look up DIA codes in DIA dict;
                #if diagnosis is ICD9,
                #    look it up in GEMS file
                sub them in to claim line.
        """
        gemNotes = {}
        gemDir = {}
        with open(gemFile, 'r') as gF:
            for line in gF.readlines():
                tmpList = line.split()
                gemDir[tmpList[0]] = [ tmpList[1], tmpList[2] ] #I9 GEM format is: ICD-9  ICD-10  Notes

        diagDir = {} #
        for obj in RecordGenerator(office, "Diagnosis"):
            diagDir[obj.ID] = {'ICD': obj.ICD, '10': not obj.DotFormat}

        procDict = {} # Lookup of procedure codes to help find service lines with trucated LICNs (more than 1000 transactions per patient)
        for obj in RecordGenerator(office, "Procedure"):
            tmpCode = obj.HCPCSCode if (len(obj.HCPCSCode) > 1) else obj.CPTCode
            procDict[obj.InHouseCode] = tmpCode
        diagClms = {} #Key to this will include procedure
        diagExts = {} #Key to this will NOT - to catch diagnoses from extended charge records
        lstLICN = [] #List of UM's (truncated) LICNs
        HI = 0
        hiLines = {}
        sv1Lines = {}
        #----  Build dict of claim numbers: HI lines (where diagnoses go), SV1 lines (where indexes go)
        for index, loop1 in enumerate(self.GSLoop):
            for i2, loop2 in enumerate(loop1.STLoop):
                for i3, seg in enumerate(loop2.TSet):
                    if seg[0] == 'HI':
                        HI = i3
                        hiLines[HI] = []
                    if seg[0] == 'SV1':
                        SV1 = i3
                        sv1Lines[SV1] = []
                        procCode = seg[1].split(self.SubElemSep)[1]
                    if seg[0] == 'REF' and seg[1] == '6R': #note the lines we'll need to fix later
                        tmpStr = seg[2].strip()
                        diagClms[tmpStr + procCode] = {"HI":HI,"SV1":SV1,"diags":["","","",""],"RecNum":tmpStr}
                        lstLICN.append(tmpStr)
        print lstLICN

        for obj in RecordGenerator(office, "TransactionD"): # Crawl transaction file to grab associated diagnosis (in-house) codes
            tmpStr = '{:03d}'.format(obj.SeqNum)[:3]
            testKey = '{}{}.{}'.format(obj.ChartNumber, obj.Date, tmpStr)
            if testKey in lstLICN:
                if obj.ExtChg: # UltraMed originally only had two diags per claim; 3 and 4 are in extended charge record
                    extKey = '{}{}.{}'.format(obj.ChartNumber, obj.Date, obj.SeqNum)
                    diag3 = obj.Diag3 if len(obj.Diag3) > 0 else ""
                    diag4 = obj.Diag4 if len(obj.Diag4) > 0 else ""
                    diagExts[extKey] = [diag3, diag4]

                else:
                    newKey = testKey + procDict[obj.ProcCode]
                    if newKey in diagClms.keys():
                        diagClms[newKey]["RecNum"] = '{}{}.{}'.format(obj.ChartNumber, obj.Date, obj.SeqNum)
                        diagClms[newKey]["diags"][0] = obj.Diag1 if len(obj.Diag1) > 0 else ""
                        diagClms[newKey]["diags"][1] = obj.Diag2 if len(obj.Diag2) > 0 else ""
        for clmID, clmLine in diagClms.iteritems():
            testKey = clmLine["RecNum"]
            if testKey in diagExts.keys():
                diagClms[clmID]["diags"][2] = diagExts[testKey][0]
                diagClms[clmID]["diags"][3] = diagExts[testKey][1]

        for claimID, claim in diagClms.iteritems():
            hiLine = claim["HI"] # grab the HI line number to use as key
            print "hiLine", hiLine
            sv1Line = claim["SV1"]
            for n in (3,2,1,0): # getting rid of blanks (what if all blank?  We'd have bigger problems then)
                if (claim["diags"][n] == ""): claim["diags"].pop(n)

            for num, diag in enumerate(claim["diags"]): # remember that num counts from 0, but SV1 and HI indexes count from 1
                print "num:", num, "diag:", diag
                try:
                    if diagDir[diag]['10']: #Check in-house code against DIA dir; if it's already an ICD-10...
                        ICD10 = diagDir[diag]['ICD'] # ... just use the ICD from UltraMed
                    else:
                        tmpICD = diagDir[diag]['ICD'] # Otherwise, get ICD entry from DIA dir...
                        try:
                            ICD10, gemNote = gemDir[tmpICD][0], gemDir[tmpICD][1] #... and look it up in GEM table
                            if gemNote == '00000':
                                #tmpNote = 'ICD-9 code {} maps exactly to ICD-10 code {}'.format(tmpICD, ICD10)
                                tmpNote = ["Exact", tmpICD, ICD10]
                            elif gemNote[0] == '1':
                                #tmpNote = 'ICD-9 code {} is an approximate match to ICD-10 code {}'.format(tmpICD, ICD10)
                                tmpNote = ["Approx", tmpICD, ICD10]
                            elif gemNote[1] == '1':
                                #tmpNote = 'ICD-9 code {} cannot be mapped to ICD-10 at all.  Passing through as-is - likely rejection.'.format(tmpICD)
                                tmpNote = ["Invalid", tmpICD, ICD10]
                                ICD10 = tmpICD
                            gemNotes[diag] = tmpNote
                        except KeyError:  # if this code didn't exist in GEM table, something is odd
                            #gemNotes[diag] = 'No record found in GEM file for code {}. Passing through as-is - likely rejection.'.format(tmpICD)
                            gemNotes[diag] = ["NoMatch", tmpICD, ""]
                            ICD10 = tmpICD
                except: # Why/how would a diagnosis from the billing file not be in the DIA table? Maybe you're doing the wrong office...?
                    #gemNotes[diag] = 'No entry found in office {} DIA table for code {}. Wrong office, maybe?'.format(office, diag)
                    gemNotes[diag] = ["NoDIA", tmpICD, ""]
                    ICD10 = diag
                print gemNotes
                ICD10 = ICD10.translate(None, " .") #strip out spaces, periods - shouldn't be there, but humans are fallible
                if ICD10 not in hiLines[hiLine]:
                    hiLines[hiLine].append(ICD10)
                sv1Lines[sv1Line].append( str(hiLines[hiLine].index(ICD10)+1) ) # remember, SV1 indexes count from 1

        for index, loop1 in enumerate(self.GSLoop):
            for i2, loop2 in enumerate(loop1.STLoop):
                for i3, seg in enumerate(loop2.TSet):
                    if seg[0] == 'HI':
                        if i3 in hiLines.keys():
                            #print i3, hiLines[i3], "seg:", seg
                            tmpSeg = seg
                            try:
                                seg = seg[:2] # remove all but initial diag
                                print "1"
                                print hiLines
                                seg[1] = self.SubElemSep.join(['ABK', hiLines[i3][0]])
                                print "2"
                                if len(hiLines[i3]) > 1:
                                    seg.append( self.SubElemSep.join(['ABF', hiLines[i3][1]]) )
                                    print "3"
                                if len(hiLines[i3]) > 2:
                                    seg.append( self.SubElemSep.join(['ABF', hiLines[i3][2]]) )
                                    print "4"
                                if len(hiLines[i3]) > 3:
                                    seg.append( self.SubElemSep.join(['ABF', hiLines[i3][3]]) )
                                    print "5"
                            except IndexError:
                                print "WTF? Original seg:", tmpSeg, " - i3:", i3, " - hiLines[i3]", hiLines[i3], " - seg:", seg
                        else: print i3, "not found in hiLines.keys"
                    loop2.TSet[i3] = seg
                    if seg[0] == 'SV1':
                        if i3 in sv1Lines.keys():
                            seg[7] = self.SubElemSep.join(sv1Lines[i3])
                            if len(seg[7]) < 1: seg[7] = "1" # Desperate, last-resort hack
                        else: print i3, "not found in sv1Lines.keys"
                    loop2.TSet[i3] = seg
        tmpStr = "                Your code     ICD-9       ICD-10\n"
        for key, response in {"Exact":"Exact matches\n", "Approx":"Approximate matches\n",
                                "Invalid":"ICD-9 can't be matched to any ICD-10\n",
                                "NoMatch":"No match found in GEM file - maybe not ICD-9\n?",
                                "NoDIA":"Couldn't match UltraMed - maybe wrong office?\n"}.iteritems():
            tmpDir = {diag: notes for diag, notes in gemNotes.iteritems() if notes[0] == key}
            if len(tmpDir) > 1:
                tmpStr += response
                for diag, notes in tmpDir.iteritems():
                    tmpStr += "                {:8}      {:8}     {}\n".format(diag, notes[1], notes[2])

        return tmpStr


    def CvtTo5010(self, repSep="^", verNum="005010X222A1", AssignNewICN=True):
        """
        Convert version 4010 file to version 5010.
            repSep: repetition separator (new in 5010, replaces "Interchange Control Standards ID", which was always 'U')
            verNum: new version number, currently 00501X222A1 for professional claims - previously 00410X098A1
            AssignNewICN: ISA13 (ICN, aka File ID) needs to be unique within last 12 months.

            New things in 5010:
                REF 6R (Line Item Control Number) must be unique - never paid any attention before
                GS05 (Time) was: HHMMSSDD; now HHMM
                ST03 segment has been added - contains version number
                Transmission Type ID record (starts with REF|87) has been deleted
                NM1 records add segment 12, Last Name - no action at this time
                N3 records, per Medi-Cal: if blank, do not send.
                N4 records add segment 07, Country Subdivision - no action at this time
                CLM records: segment 05/2 goes from 'not used' to required, must contain 'B'
                CLM records: segment 10 can only contain 'P'
                OI records: segment 4 should be blank; segment 6 reduced to I or Y
                Pay-To Provider (2000A) changed to Billing: PRV01 was: PT, BI; now BI only
                Subscriber (2000B) and Other Subscriber (2320) - only send SBR05 for MSP, and only (12, 13, 14, 15, 16, 41, 42, 43, 47)
                Subscriber (2000B) and Other Subscriber (2320) - SBR09 should not be sent at all
                Subscriber Name (2010BA) and Other Subscriber Name(2330A) - ID Code Qualifier - NM108 was: MI, ZZ; now II, MI
                Patient (2010CA) - ID Qualifier and Code - NM108, NM109 no longer used
                Crossover Indicator in loop 2300 (starts with REF|F5) has been deleted
                Other Insurance Subscriber Demographics (DMG record in loop 2320) has been deleted
                Other Insurance - "If 2320.SBR03 is present, 2320.SBR04 must not be present" (actually, removing SBR03) - 14 Oct 2013
                Service Location (2310C, 2420C) - NM101 was: 77, FA, LI, TL; now 77 only
                Rendering Provider (2310B, 2420A) - Reference ID Qualifier was: ZZ; now PXC
                Service (2400) ID Qualifier  - SV101 was: HC, IV, ZZ; now ER, HC, IV, WK (ER replaces ZZ)

        """
        time.clock()
        self.ISARec[11] = repSep
        self.ISARec[12] = "00501"
        if AssignNewICN:
            self.ISARec[13] = str(int(time.time()) % 999999999)
        for index, gsLoop in enumerate(self.GSLoop):
            self.GSLoop[index].GSRec[5] = self.GSLoop[index].GSRec[5][:4] #4010 accepted HHMMSSDD; 5010 only HHMM
            self.GSLoop[index].GSRec[8] = verNum
            for stLoop in gsLoop.STLoop:
                #5010 adds ST03
                if len(stLoop.STRec) < 4:
                    stLoop.STRec.append(verNum)
                else:
                    stLoop.STRec[3] = verNum
                # remove Transmission Type ID record (starts with REF|87)
                # and also "MANDATORY MEDICARE (SECTION 4081) CROSSOVER INDICATOR" (REF|F5)
                stLoop.TSet[:] = [seg for seg in stLoop.TSet if not ((seg[0] == 'REF') and (seg[1] in ('87', 'F5')))]
                loopNum = ''
                for seg in stLoop.TSet:
                    loopNum = getLoop(seg, loopNum)
                    if (seg[0] == 'REF' and seg[1] == '6R'):  #Line Item Control Number
                        if len(seg[2]) > 0:
                            padLen = 29 - len(seg[2])
                            # edit 19Sep2013 - LICNs were coming out longer than the 30-character max
                            seg[2] = '%s.%s' % (seg[2].strip(), str(time.clock())[:padLen])
                        else:  # if no LICN, use the time to make sure it's unique
                            seg[2] = str(time.clock())
                    if (seg[0] == 'CLM'): # 2300.CLM05-2 must be "B"; CLM10 must be "P"
                        tmpList = seg[5].split(self.SubElemSep)
                        tmpList[1] = 'B'
                        seg[5] = self.SubElemSep.join(tmpList)
                        seg[10] = 'P'
                    if (seg[0] == 'SBR'):
                        seg[5] = '' # except for MSP - add logic later
                        if loopNum == '2320':  # if Other insurance,
                            if seg[9] == 'MB': seg[9] = 'ZZ'    #SBR09 must NOT be 'MB'
                            if seg[4] != ''  : seg[3] = ''      #14 Oct 2013

                    if (seg[0] == 'DMG'):  #DMG for Other Insurance Sbscriber
                        if loopNum == '2320':
                            seg[0] = 'DELETE'
                    if (seg[0] == 'OI'):
                        seg[4] = ''
                        seg[6] = 'Y'
                    if (seg[0] == 'PRV') and (seg[1] == 'PT'):  #2000A
                        seg[1] = 'BI'
                    if (seg[0] == 'NM1') and (seg[1] in ('FA', 'LI', 'TL')): #2310C and 2420C
                        seg[1] = '77'
                    if (seg[0] == 'PRV') and (seg[1] == 'PE'):  #2310B and 2420A
                        seg[2] = 'PXC'
                    if (seg[0] == 'NM1') and (seg[1] == 'IL'):  #2010BA and 2330A
                        if seg[2] == 'ZZ': seg[2] = 'II'
                    if (seg[0] == 'NM1') and (seg[1] == 'QC'):  #2010CA
                        while (len(seg) > 8): del seg[-1:]
                    if (seg[0] =='N3') and (seg[1] == ''):      #Remove empty N3 segments
                        if (len(seg) == 2) or (len(seg) == 3 and seg[2] == ''):
                            seg[0] = 'DELETE'
                    if (seg[0] == 'SV1'):                       #2400
                        if (seg[1] == 'ZZ'): seg[1] = 'ER'
                        while seg[-1] == '':  #Trim trailing unused segments
                            del seg[-1]
                        #stLoop.TSet[i3] = seg
                stLoop.TSet[:] = [seg for seg in stLoop.TSet if not (seg[0] == 'DELETE')]

    def DedupPER(self):
        """
        Per Noridian's edit, '2010AA.PER02 must not = 1000A.PER02'...
        So - assume that the (UltraMed) submitter record contains 'JAMES JIM'; we'll put JAMES in 1000A and JIM in 2010AA.
        """
        for index, gsLoop in enumerate(self.GSLoop):
            for stLoop in gsLoop.STLoop:
                loopNum = ''
                for seg in stLoop.TSet:
                    loopNum = getLoop(seg, loopNum)
                    if (seg[0] == 'PER' and seg[1] == 'IC'):  #Contact information - but whose?
                        if loopNum == '1000A': #Submitter
                            seg[2] = seg[2].split()[0]
                        if loopNum == '2010AA': #Billing provider
                            seg[2] = seg[2].split()[1]


    def StripCodes(self):
        """
        An extra space at the end of an ID code will result in the entire file being rejected.  Who even knew this was A Thing?
        """
        for index, gsLoop in enumerate(self.GSLoop):
            for stLoop in gsLoop.STLoop:
                for seg in stLoop.TSet:
                    if (seg[0] == 'NM1' and len(seg) > 9):  #let's not have an IndexError, shall we?
                        seg[9] = seg[9].strip()


    def CheckZips(self, fixZips=True):
        gapFiller = '9998'  # I would've thought '0000', but this seems to be CMS's preference
        tmpName = tmpNM1Type = tmpAddress = tmpCSZ = newZip = ''
        badZip = False
        for gsLoop in self.GSLoop:
            for stLoop in gsLoop.STLoop:
                for seg in stLoop.TSet:
                    if (seg[0] == 'NM1'):
                        tmpNM1Type = seg[1]
                        try:
                            tmpName = seg[4] + ' ' + seg[3]
                        except IndexError:
                            tmpName = seg[3]
                    if (seg[0] == 'N3'):
                        tmpAddress = seg[1]
                    if (seg[0] == 'N4'):
                        tmpCSZ = seg[1] + ', ' + seg[2] + ' ' + seg[3]
                        if not (len(seg[3]) == 9):  # might as well check for too-long zips, while we're at it
                            if (len(seg[3]) == 5): #if it's not 9 digits, it should be 5... but who knows?
                                if fixZips: newZip = seg[3] = seg[3] + gapFiller  #e.g. 913169998
                            else:
                                badZip = True
                                if fixZips: newZip = seg[3] = seg[3].ljust(9,'0')
                            if (tmpNM1Type in ('85','77')) or badZip:  # is this a Billing Provider, a Service Location, or just a malformed ZIP?
                                self.shortZips[tmpName] = tmpName + '\n' + tmpAddress + '   ' + tmpCSZ + '\n - changed to: ' + newZip + '\n'
                            tmpName = tmpNM1Type = tmpAddress = tmpCSZ = newZip = '' # reset
                            badZip = False

    def ForceTest(self):
        self.ISARec[15] = "T"

    def LastNameOA(self):
        """
        If a patient has a double-barreled last name, Office Ally requires a comma at the end
        (otherwise only first part gets sent on to Medicare).
        Punctuation is not normally allowed in X12 files, so we should only do this if claims are to be sent via Office Ally...
        NOTE: this may not actually be necessary; I'm leaving this code here for now but commenting out caller in fsr_x12.
        """
        self.PT = True
        for loop1 in self.GSLoop:
            for loop2 in loop1.STLoop:
                for index, seg in enumerate(loop2.TSet):
                    if (seg[0] == 'NM1'):
                        if (seg[1] in ['IL', 'QC']):
                            loop2.TSet[index][3] = seg[3] + ','

    def __str__(self):
        """
        Parses an 837 file and prints a quick summary so biller can review before sending.
        """
        self.outLines = [] # lines of report
        self.LineNum  = -1
        self.billingLine = 0
        self.patientLine = 0
        self.billingTotal = 0.00
        self.patientTotal = 0.00
        self.claimTotal = 0
        def addLine(text, position=0):
            tmpLine = ' '*110
            tmpLine = tmpLine[:position] + text + tmpLine[(position+len(text)):]
            self.outLines.append(tmpLine)
            self.LineNum +=1
        def amendLine(text, line = self.LineNum, position=1):
            tmpLine = self.outLines[line]
            tmpLine = tmpLine[:position] + text + tmpLine[(position+len(text)):]
            self.outLines[line] = tmpLine

        for loop1 in self.GSLoop:
            addLine('Submission number: %s                                                             Date: %s' % (loop1.GSRec[6], loop1.GSRec[4]))
            for loop2 in loop1.STLoop:
                for seg in loop2.TSet:
                    if (seg[0] == 'NM1'):
                        if (seg[1]=='41'):
                            addLine('Submitter: %s  %s' % (seg[9], seg[3]))
                            self.submitterLine = self.LineNum
                            addLine('-'*110)
                        if (seg[1]=='40'):
                            amendLine(' Receiver: %s %s' % (seg[9], seg[3]), line=self.submitterLine, position=56)
                        if (seg[1]=='85'):
                            if self.billingLine > 0: # if this is not the first billing provider
                                addLine(('Total - $%.2f' % self.billingTotal), position = 25)
                            tmpNPI = (seg[9] if (len(seg) > 9 and len(seg[9]) > 2) else "N/A")
                            addLine('Billing Provider: %s  -  NPI: %s' % (seg[3], tmpNPI))
                            self.billingLine = self.LineNum
                            self.billingTotal = 0.00
                            addLine(' Patient')
                            amendLine(' Rendering    - NPI', position = 33)
                            amendLine(' Referring    - NPI', position = 60)
                            if self.DME:
                                amendLine(' Ordering     - NPI', position = 60)
                            if self.PT:
                                amendLine(' Supervising  - NPI', position = 60)
                            amendLine(' Facility  - NPI', position = 87)
                        if (seg[1]=='IL'):  #actually, this is the insured - but for now, I'll treat it as the patient...
                            if self.patientLine > 0: # if this is not the first patient
                                amendLine(('$%.2f' % self.patientTotal).rjust(10), line=self.patientLine, position = 20)
                            addLine('%s, %s' % (seg[3], seg[4]), position = 1)
                            self.patientLine = self.LineNum
                            self.patientTotal = 0.00
                        if (seg[1]=='82'): # rendering
                            tmpNPI = (seg[9] if (len(seg) > 9 and len(seg[9]) > 2) else "N/A       ")
                            amendLine(' %s, %s' % (seg[3], seg[4]), line=self.patientLine, position = 33)
                            amendLine(' - %s' % tmpNPI, line=self.patientLine, position = 46)
                        if (seg[1]=='DK'): # ordering
                            tmpNPI = (seg[9] if (len(seg) > 9 and len(seg[9]) > 2) else "N/A       ")
                            amendLine(' %s, %s' % (seg[3], seg[4]), line=self.patientLine, position = 60)
                            amendLine(' - %s' % tmpNPI, line=self.patientLine, position = 73)
                        if (seg[1]=='DN'): # referring
                            tmpNPI = (seg[9] if (len(seg) > 9 and len(seg[9]) > 2) else "N/A       ")
                            amendLine(' %s, %s' % (seg[3], seg[4]), line=self.patientLine, position = 60)
                            amendLine(' - %s' % tmpNPI, line=self.patientLine, position = 73)
                        if (seg[1]=='DQ'): # supervising
                            tmpNPI = (seg[9] if (len(seg) > 9 and len(seg[9]) > 2) else "N/A       ")
                            amendLine(' %s, %s' % (seg[3], seg[4]), line=self.patientLine, position = 60)
                            amendLine(' - %s' % tmpNPI, line=self.patientLine, position = 73)
                        if (seg[1]=='FA'): # facility
                            tmpNPI = (seg[9] if (len(seg) > 9 and len(seg[9]) > 2) else "N/A       ")
                            amendLine(' %s' % seg[3][:15], line=self.patientLine, position = 87)
                            amendLine('- %s' % tmpNPI, line=self.patientLine, position = 98)
                    elif (seg[0]=='CLM'):
                        self.patientTotal += float(seg[2])
                        self.billingTotal += float(seg[2])
                        self.claimTotal += 1

                amendLine(('$%.2f' % self.patientTotal).rjust(10), line=self.patientLine, position = 20) # last patient
                addLine('                    ==========')
                addLine('          Total - ')
                amendLine(('$%.2f' % self.billingTotal).rjust(10), position = 20) # last billing line will be left hanging
                amendLine(('Claims: %s' % self.claimTotal), line=self.billingLine, position = 80) # last billing line will be left hanging
        outString = "\n".join(self.outLines)
        del self.LineNum
        del self.billingLine
        del self.billingTotal
        del self.patientLine
        del self.patientTotal
        del self.claimTotal
        del self.outLines
        return outString

if __name__ == '__main__':
    #thingy = X12_837('E:\\ultramed\\mcare04.837', 'E:\\ultramed\\npiMap.xml')
    thingy = X12_837(r'C:\Users\Marc\Desktop\new.837', 'E:\\ultramed\\npiMap.xml')
    #thingy = X12_837(r'C:\Users\Marc\Desktop\norm.837', 'E:\\ultramed\\npiMap.xml')
    thingy.FixSSN()
    thingy.SubstMBI('03', 'E:\\Dropbox\\fsrPy')
    thingy.loopPrint(r'C:\Users\Marc\Desktop\preLoopDump.txt')
    thingy.PatientHome2310C()
    thingy.loopPrint(r'C:\Users\Marc\Desktop\postLoopDump.txt')
    thingy.NPIConversion(UseSecID=True, KeepLicense=False, KeepTaxID=True, KeepInsID=False, KeepUxIN=False, KeepFacID=False)
    thingy.SubmitterSubst(SubNum='EHY')
    thingy.CarrierConversion(ShortName='Jur. E SoCal')
    thingy.DNtoDQ()
    thingy.ProcessNTE()
    thingy.addTraceNumber()
    thingy.DedupPER()
    thingy.StripCodes()
    offices = parseDirectDat(urllib.url2pathname('E:\\ultramed\\direct.dat'))
    gemNotes = thingy.doICD10(offices['03'], r'E:\ultramed\2015_I9gem.txt')
    print gemNotes
    thingy.CvtTo5010()
    thingy.CheckZips()
    #thingy.ForceTest()
    thingy.tofile(r'C:\Users\Marc\Desktop\out.edi')
    #thingy.loopPrint(r'C:\Users\Marc\Desktop\postLoopDump.txt')

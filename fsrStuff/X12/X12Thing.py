from __future__ import with_statement
import os.path
import codecs
from X12GSLoop import X12GSLoop


class X12Error(Exception):
    pass
class Not_X12(X12Error):
    pass

class X12Thing(object):
    """
    X12Things contain:
        .inFileName    - Name of original file being processed (either billing or response)
        .ElemSep       - Element separator (usually "*")
        .SubElemSep    - Sub-element separator (usually ":")
        .SegTerm       - Segment terminator (usually "~")
        .expand         - Controls printing - set this to True if you want to print each segment on its own line
        .ISARec         - Header from original file
        .IEARec         - Footer, calculated on-demand
        .GSLoop[]       - List of GS/GE loops.  Most carriers want only one per file, but we better plan ahead.
                          (Update: in 5010, only one GS/GE is allowed.  Don't think it requires a change, though.)
        OR!!!!
        .TA1Rec         - If this is a TA1 file (set TA1 to true), contains status and (maybe) error codes
        .testProd       - Usage Indicator: either "T" or "P"
    They may also contain:
        .npiMap         - Dictionary of legacy-to-NPI-code mappings
        .noLegs         - Dictionary of entities for which no legacy code exists (e.g. facilities with no license, referral sources with no UPIN)
        .shortZips      - Dictionary of entities that don't have 9-digit zip codes
    """
    TA1 = False
    PT = False
    DME = False
    def __init__(self, inFileName="", npiMapFile=""):
        """
        Copy the first (ISA) record for posterity, delete first and last, the rest goes in the list.
        """
        self.noLegs  = {}
        self.shortZips = {}
        self.npiMapFile = npiMapFile
        self.inFileName = os.path.basename(inFileName)
        try:
            with open(inFileName, 'r+b') as inFile:
                inString = inFile.read()
        except Exception, inst:
            raise X12Error("There was an error opening your file - %s\n%s - %s" % (inFileName, Exception, inst))
        if inString[0:3] == codecs.BOM_UTF8:
            inString = inString[3:]
        if inString[:3] != 'ISA':
            raise Not_X12("Your file - %s - does not appear to be an X12 file." % (inFileName))
        try:
            inString        = inString.replace('\n', '')
            inString        = inString.replace('\r', '')
            self.ElemSep    = inString[3]      # Element separator (usually "*")
            self.SubElemSep = inString[104]    # Sub-element separator (usually ":")
            self.SegTerm    = inString[105]    # Segment terminator (usually "~")
            inString        = inString.strip()
            tmpSegs         = inString.split(self.SegTerm)
        except Exception, inst:
            raise X12Error("There was an error splitting your file %s into records for processing.\nIt may be an empty file, corrupted, or just not a valid billing file." % inFileName)
        while (len(tmpSegs[-1])==0):
            del tmpSegs[-1]
        for index, seg in enumerate(tmpSegs):
            tmpSegs[index] = tmpSegs[index].split(self.ElemSep)
        self.ISARec     = tmpSegs.pop(0)
        if self.ISARec[15] == 'T':
            self.testProd   = 'Test'
        elif self.ISARec[15] == 'P':
            self.testProd   = 'Production'
        else:
            self.testProd   = 'Unknown Status'
        # Split elements into list of sub-elements if warranted:
        '''
        for index, seg in enumerate(tmpSegs):
            for num, elem in enumerate(seg):
                if self.SubElemSep in elem:
                    seg[num] = seg[num].split(self.SubElemSep)
        '''
        if (tmpSegs[-1][0] == 'IEA'):
            del tmpSegs[-1]    # Strip off original IEA record - we'll create our own
        self.GSLoop    = []
        for index, seg in enumerate(tmpSegs):
            try:
                if (seg[0] == 'GS'):
                    tmpLoop = []
                    tmpLoop.append(seg)
                elif (seg[0] == 'GE'):
                    tmpLoop.append(seg)
                    self.GSLoop.append(X12GSLoop(tmpLoop))
                    del(tmpLoop)
                elif (seg[0] == 'TA1'):
                    self.TA1 = True
                    self.TA1Rec = seg
                    continue
                else:
                    tmpLoop.append(seg)
            except Exception, inst:
                print index, seg
                raise X12Error("I ran into an unforeseen problem while trying to process: %s, %s\n The error message was: %s" % (index, seg, inst))
    def __getattr__(self, name):
        if (name=='IEARec'):
            """
            Field 1 is the number of GS/GE loops, field 2 matches field 13 of the ISA record.
            """
            return ['IEA', str(len(self.GSLoop)), self.ISARec[13]]

    def tofile(self, fileName, newLines=True):
        """
        Create a new list of records
        - these are the former lists of elements, joined together by the element separator (*):
            ISARec
                GSRec
                    STRec
                        actual stuff
                    SERec() -|
                GERec()------|- these are calculated
            IEARec()---------|
        Now the records become one big string, joined by the segment terminator (~)
            and make sure there's a terminator at the very end.
        Then, of course, we write it out to a file.  Finis!
        """
        segTerm = self.SegTerm
        if newLines: segTerm += "\n"
        outList = [self.ElemSep.join(self.ISARec)]
        if self.TA1:
            outList.append(self.ElemSep.join(self.TA1Rec))
        else:
            for loop1 in self.GSLoop:
                outList.append(self.ElemSep.join(loop1.GSRec))
                for loop2 in loop1.STLoop:
                    outList.append(self.ElemSep.join(loop2.STRec))
                    for rec in loop2.TSet:
                        outList.append(self.ElemSep.join(rec))
                    outList.append(self.ElemSep.join(loop2.SERec))
                outList.append(self.ElemSep.join(loop1.GERec))
        outList.append(self.ElemSep.join(self.IEARec))
        outList = segTerm.join(outList)
        if (outList[-1] != segTerm):  # make sure IEA record ends with a tilde
            outList = outList + segTerm
        with open(fileName, 'w+b') as outFile:
            outFile.write(outList)



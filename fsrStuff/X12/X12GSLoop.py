import time
from X12STLoop import X12STLoop

class X12GSLoop(object):
    """
    GSLoops contain:
        .GSRec - header from original file
        .GERec - footer, calculated on-demand
        .STLoop - list of transaction sets
    """
    def __init__(self, inList, AssignNewGCN=True):
        """
        Copy the first (GS) record for posterity, delete first and last, the rest goes in the list.
        GS[6] (1-9 digits, numeric) contains the Group Control Number (this field and GE[2] must match).
          UltraMed never changes this field, so transmission reports are hard to match up with claim files.
          If AssignNewGCN is true, create a new GCN by the following algorithm: int(time.time()) % 999999999
             system time (seconds elapsed since the epoch) converted to integer, 
             modulo 999,999,999 (to assure it will always be between 1 and 9 digits)
             convert to string
          This should assure a unique serial number every second; there may be duplicates every 31.7 years.
        If this were a security requirement, more care would be needed - but then we'd be allowed more than 9 digits, right?
        """
        self.GSRec = inList[0]
        if AssignNewGCN:
            self.GSRec[6] = str(int(time.time()) % 999999999)
        del inList[0]
        del inList[-1]
        self.STLoop = []
        for seg in inList:
            if (seg[0] == 'ST'):
                tmpLoop = []
                tmpLoop.append(seg)
            elif (seg[0] == 'SE'):
                tmpLoop.append(seg)
                self.STLoop.append(X12STLoop(tmpLoop))
                del tmpLoop
            else:
                tmpLoop.append(seg)
    def __getattr__(self, name):
        if (name=='GERec'):
            """
            Field 1 is the number of ST/SE loops, field 2 matches field 6 of the GS record. 
            """
            return ['GE',str(len(self.STLoop)), self.GSRec[6]]



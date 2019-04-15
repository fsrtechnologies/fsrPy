class X12STLoop(object):
    """
    STLoops contain: 
        .STRec - header from original file
        .SERec - footer, calculated on-demand
        .TSet  - list of segments
    """
    def __init__(self, inList):
        """
        Copy the first (ST) record for posterity, delete first and last, the rest goes in the list.
        """
        self.STRec      = inList[0]
        #self.SERec      = inList[-1]
        del inList[0]
        del inList[-1]
        self.TSet       = inList
    def __getattr__(self, name):
        if (name=='SERec'):
            """
            Field 1 is the number of segments in this loop (must include ST and SE records, so add 2 to total)
            Field 2 matches field 2 of the ST record.
            """
            return ['SE',str(len(self.TSet) +2), self.STRec[2]]  # '+2' - this total must include ST and SE segments


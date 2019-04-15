from TLAList import TLAList
class Office(object):
    """UltraMed office - file locations"""
    Default=""
    
    def __init__(self, offNum=""):
        self.Num = offNum
        for TLA in TLAList:
            setattr(self, TLA, "")
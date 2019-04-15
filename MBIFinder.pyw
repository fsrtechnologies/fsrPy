from __future__ import with_statement
import datetime, urllib, urllib2, os, textwrap, shelve, string
from fsrStuff.umFuncs import parseDirectDat, RecordGenerator
from configobj import ConfigObj


class MBIFinder(object):
    """New Medicare Beneficiary IDs are stored in the Message 2 field.  Read them into a local db for quick access,
            and substitute them into the billing file.
    Call in the following format:
        with MBIFinder(office = '01', location = os.getcwd()) as mf:
            do stuff
    Methods:
        loadTable() - reads ChartNumber/ID pairs into local db
        lookup(chartNum) - looks up given chart number, returns MBI OR False
    """
    def __init__(self, offNum = '01', location = os.getcwd()):
        """Create database engine, configure and start session"""
        config = ConfigObj(location + os.sep + 'fsr_x12.ini')
        offices = parseDirectDat(urllib.url2pathname(str(config['Current']["directDat"])))
        if offNum in offices:
            self.dbFile = location + os.sep + offNum + "MBI.db"
            self.office = offices[offNum]
            self.db = shelve.open(self.dbFile)
        else:
            print("Can't find that office!")

    def __enter__(self):
        return self

    def __exit__(self, eType, value, traceback):
        """Close the database file"""
        self.db.close()

    def lookup(self, chartNum):
        """Look up chart number in table; return MBI or False if not found)"""
        try:
            MBI = self.db[chartNum]
            return MBI
        except KeyError:
            return False

    def loadTable(self):
        C = ['1','2','3','4','5','6','7','8','9']
        A = ['A','C','D','E','F','G','H','J','K','M','N','P','Q','R','T','U','V','W','X','Y']
        N = ['0','1','2','3','4','5','6','7','8','9']
        AN = A+N
        self.badMBI = {}
        self.db = shelve.open(self.dbFile)
        for obj in RecordGenerator(self.office, "PatMBI"):
            if obj.PriInsuredID.upper() == '000-00-0000-A':
                tmpStr = obj.Message2.translate(None, string.punctuation).upper()
                try:
                    assert (len(tmpStr))==11, 'MBI must be 11 digits long'
                    assert (tmpStr[0] in C),  '1st char must be a digit 1-9'
                    assert (tmpStr[1] in A),  '2nd char must be alpha (but not S, L, O, I, B, or Z)'
                    assert (tmpStr[2] in AN), '3rd char must be alphanumeric (but not S, L, O, I, B, or Z)'
                    assert (tmpStr[3] in N),  '4th char must be numeric'
                    assert (tmpStr[4] in A),  '5th char must be alpha (but not S, L, O, I, B, or Z)'
                    assert (tmpStr[5] in AN), '6th char must be alphanumeric (but not S, L, O, I, B, or Z)'
                    assert (tmpStr[6] in N),  '7th char must be numeric'
                    assert (tmpStr[7] in A),  '8th char must be alpha (but not S, L, O, I, B, or Z)'
                    assert (tmpStr[8] in A),  '9th char must be alpha (but not S, L, O, I, B, or Z)'
                    assert (tmpStr[9] in N),  '10th char must be numeric'
                    assert (tmpStr[10] in N), '11th char must be numeric'
                except AssertionError as err:
                    self.badMBI[obj.ChartNumber] = tmpStr + " - " + err.args[0]
                self.db[obj.ChartNumber.translate(None, string.punctuation)] = tmpStr
                # Remove the period from ChartNumber and the hyphens from the MBI
        #self.db.close()

if __name__ == '__main__':
    with MBIFinder(offNum="04") as mf:
        mf.loadTable()
        if len(mf.badMBI) > 0:
            print mf.badMBI
    with MBIFinder(offNum="04") as mf:
        print mf.db
        MBI = mf.lookup('130140')
        print MBI

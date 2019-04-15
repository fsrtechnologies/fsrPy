#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Marc
#
# Created:     14/05/2015
# Copyright:   (c) Marc 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, zipfile, csv

class mcrCodes(object):
    def __init__(self, codeFileName=os.getcwd() + os.sep + "MedicareRemitEasyPrint43.zip"):
        if zipfile.is_zipfile(codeFileName):
            piz = zipfile.ZipFile(codeFileName)
            for item in piz.infolist():
                if item.filename[-3:] == "ini":
                    inFile = piz.read(item.filename)
                    tmpCodes = inFile.splitlines()
        else:
            with open(codeFileName,'r') as inFile:
                tmpCodes = inFile.readlines()
        self.releaseDate = tmpCodes.pop(0)
        self.version = tmpCodes.pop(0)
        self.codes = []
        tmpCode = {"code":tmpCodes.pop(0)[1:-1]}
        for index, line in enumerate(tmpCodes):
            if line[0]=='[':
                self.codes.append(tmpCode)
                tmpCode = {"code":line[1:-1]}
            else:
                if line.split('=')[0] == 'Message':    tmpCode["message"] = line.split('=')[1]
                if line.split('=')[0] == 'EffDate':    tmpCode["eff_date"] = line.split('=')[1]
                if line.split('=')[0] == 'DeactDate':  tmpCode["deact_date"] = line.split('=')[1]
                if line.split('=')[0] == 'Modified':   tmpCode["mod_date"] = line.split('=')[1]
                if line.split('=')[0] == 'Note':       tmpCode["notes"] = line.split('=')[1]
                if line.split('=')[0] == 'Scenario':   pass

        self.codes.append(tmpCode) # clean up last line

    def cvtToCSV(self, csvFile=os.path.join(os.path.expanduser("~"),"Desktop","codes.csv")):
        """
        Export codes to CSV file for further processing on way to import to SQLite db
        """
        with open(csvFile, 'w') as outFile:
            fieldnames = ['codetype', 'code', 'message', 'eff_date', 'deact_date', 'mod_date', 'notes']
            writer = csv.DictWriter(outFile, fieldnames, quoting = csv.QUOTE_ALL, lineterminator='\n')
            writer.writeheader()
            writer.writerows(self.codes)



if __name__ == '__main__':
    codes = mcrCodes(os.path.join(os.path.expanduser("~"),"Desktop","MedicareRemitEasyPrint43.zip"))
    codes.cvtToCSV()

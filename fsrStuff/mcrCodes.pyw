from __future__ import with_statement
import os, zipfile, textwrap
from configobj import ConfigObj

class mcrCodes(object):
    """
    Provides dictionary of Medicare reason codes.
    Methods:
        __init__ - create dictionary
        lookup - return formatted explanation for given code
    Attributes:
        codes - dictionary of codes, explanations, and valid dates
        releaseDate - date working version of Codes.ini was released

    """
    def __init__(self, codeFileName=os.getcwd() + os.sep + "MedicareRemitEasyPrint43.zip"):
        """
        If codeFileName is a zip file, it will be searched for a 'Codes.ini' file;
        if not, codeFileName will be accessed directly.
        ConfigObj interprets internal quotes, so we replace apostrophes with backquotes before passing file to ConfigObj.
        """
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
        for index, line in enumerate(tmpCodes):
            tmpCodes[index] = line.replace("\'", "`")
        self.codes = ConfigObj(tmpCodes, raise_errors=True, list_values=False)
        print("Ingestion complete")

    def lookup(self, inStr=None, width=70, para=True):
        """
        Return a text-wrapped paragraph or list of lines containing explanation text for the code passed in inStr.
            inStr - code to be looked up
            width - line length to wrap to
            para - if True, return paragraph; if False, return list of lines
        """
        wrp = textwrap.TextWrapper(width=width, initial_indent=inStr+" - ", subsequent_indent="  ")
        try:
            outStr = self.codes[inStr]["Message"].replace("`", "'") # change backquotes back to apostrophes
        except KeyError:
            outStr = "Sorry, no explanatory text is available for this code.  Make sure your code file is up-to-date."
        if para:
            return wrp.fill(outStr)
        else:
            return wrp.wrap(outStr)

    def cvtToCSV(self, outFile=os.getcwd() + os.sep + "codes.csv"):
        """
        Export codes to CSV file for further processing on way to import to SQLite db
        """
        print self.codes.items

if __name__ == '__main__':
    with mcrCodes(os.path.join(os.path.expanduser("~"),"Desktop","MedicareRemitEasyPrint43.zip")) as codes:
        codes.cvtToCSV

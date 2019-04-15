from __future__ import print_function
import datetime, urllib, urllib2, os, textwrap
from lxml import etree
from lxml.cssselect import CSSSelector
from sqlalchemy import Table, Column, Integer, Text, Date, MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Session = sessionmaker()
Base = declarative_base()

class ResponseCode(Base):
    """Base type for the X12 healthcare response code table.
    id - primary key; internal use only
    codetype - abbreviation (CARC for 'claim adjustment reason code', RARC, etc.)
    code - usually one or two charcters
    message - the user-visible definition of the code, to be printed on ERAs etc.
    eff_date - when did/will the code become active
    deact_date - when did/will the code become obsolete
    mod_date - when was the code last modified
    notes - implementation notes for this code - generally meaningless to users
    """
    __tablename__ = 'codeTable'
    id = Column(Integer, primary_key=True)
    codetype = Column(Text)
    code = Column(Text)
    message = Column(Text)
    eff_date = Column(Date)
    deact_date = Column(Date)
    mod_date = Column(Date)
    notes = Column(Text)

    def __init__(self, codeType, Code, Message, EffDate, DeactDate='', ModDate='', Notes=''):
        self.codetype = codeType
        self.code = Code
        self.message = Message
        self.eff_date = EffDate
        self.deact_date = DeactDate
        self.mod_date = ModDate
        self.notes = Notes
        

class CodeFinder(object):
    """Helper class for interacting with the response code table
    Call in the following format:
        with CodeFinder(engineType = 'sqlite:', dbFile = os.getcwd() + os.sep + 'codeTable.db') as cf:
            do stuff
    Methods:
        loadTable() - initializes response-code database, downloads latest defs
        lookup(codeType, Code, wordwrapLen=80) - looks up given type/code pair, returns wordwrapped message
    """
    def __init__(self, engineType = 'sqlite:', dbFile = os.getcwd() + os.sep + 'codeTable.db'):
        """Create database engine, configure and start session"""
        self.engine = create_engine(engineType + urllib.pathname2url(dbFile))
        Session.configure(bind=self.engine)
        self.session = Session()
 
    def __enter__(self):
        return self

    def lookup(self, codeType, Code, wordwrapLen=80):
        """Look up codeType/Code pair in table; return wordwrapped Message string (or failure message)"""
        query = self.session.query(ResponseCode).\
            filter(ResponseCode.codetype == codeType).\
            filter(ResponseCode.code == Code).\
            order_by(ResponseCode.eff_date)
        if query.first() is None:
            Message = "No description found for " + codeType + " code '" + Code + "' - are new code-table updates available?"
        else:
            Message = query.first().message
        Message = textwrap.fill(Message, wordwrapLen)
        return (Message)

    def __exit__(self, type, value, traceback):
        """Close the database session"""
        self.session.close()

    def loadTable(self):
        """Initialize table, download latest definitions"""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        tblsel =  CSSSelector('tr.prod_set')
        codesel = CSSSelector('td.code')
        descsel = CSSSelector('td.description')
        datesel = CSSSelector('span.dates')
        notesel = CSSSelector('span')
        tmpDtTm = datetime.datetime(1,1,1)

        urlBase = 'http://www.wpc-edi.com/reference/codelists/healthcare/'

        codeTables = [
            {'Name': 'CARC', 'URL': 'claim-adjustment-reason-codes/'},
            {'Name': 'RARC', 'URL': 'remittance-advice-remark-codes/'},
            {'Name': 'CSCC', 'URL': 'claim-status-category-codes/'},
            {'Name': 'HCSC', 'URL': 'claim-status-codes/'},
            {'Name': 'HSTC', 'URL': 'health-care-service-type-codes/'},
            {'Name': 'HSDRC', 'URL': 'health-care-services-decision-reason-codes/'},
            {'Name': 'HPCC', 'URL': 'provider-characteristics-codes/'},
            {'Name': 'BPAEC', 'URL': 'insurance-business-process-application-error-codes/'}
            ]

        
        for cdTbl in codeTables:
            codeType = cdTbl['Name']
            print(codeType,'... ', sep="", end="")
            url = urlBase + cdTbl['URL']
            page = urllib2.urlopen(url)

            pagecontents = page.read()
            pagecontents = pagecontents.decode('utf-8')
            pagecontents = pagecontents.encode('ascii', 'ignore')
            tree = etree.fromstring(pagecontents, etree.HTMLParser(encoding='utf-8',recover=True))

            etree.strip_tags(tree, 'br')

            for row in tblsel(tree):
                startDate = stopDate = modDate = None
                rawDates = datesel(row[1])[0].text.split(' | ')
                notes = ''
                for span in notesel(row):
                    if span.text[:6] == 'Notes:':
                        notes = span.text[6:]
                code = codesel(row[0])[0].text
                desctmp = descsel(row[1])[0]

                if desctmp.text == None:
                    desc = desctmp[0].text + desctmp[0].tail
                else:
                    desc = desctmp.text
                for dateStr in rawDates:
                    datePart = dateStr.split(' ')
                    if datePart[0] == 'Start:':
                        startDate = tmpDtTm.strptime(datePart[1], "%m/%d/%Y")
                    if datePart[0] == 'Stop:':
                        stopDate = tmpDtTm.strptime(datePart[1], "%m/%d/%Y")
                    if datePart[0] == 'Last':
                        modDate = tmpDtTm.strptime(datePart[2], "%m/%d/%Y")
                tmpCode = ResponseCode(codeType, code, desc, startDate, stopDate, modDate, notes)
                self.session.add(tmpCode)
                #print(code, desc[:40], 'Start', startDate, 'Stop', stopDate, 'Mod', modDate, 'Notes', notes)
        self.session.commit()
        print('Done!')
                        

if __name__ == '__main__':
    with CodeFinder() as cf:
        #cf.loadTable()
        codes = [('CARC','59'),('HPCC','12'),('FAKE','99')]
        for codeType, Code in codes:
            Message = cf.lookup(codeType, Code)
            print(Code, '-', Message)


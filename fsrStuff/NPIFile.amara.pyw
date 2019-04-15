import os, amara

class NPIError(Exception):
    pass

class NPIFileError(NPIError):
    pass

class NPINoMatch(NPIError):
    pass

class NPIFile(object):
    """
    Skeleton for NPI map to be serialized to XML via Amara
    """
    codeType =  {'MedicareID':'1C',
                 'MedicaidID':'1D', 
                 'BlueCrossID':'1A', 
                 'BlueShieldID':'1B', 
                 'EIN':'EI', 
                 'SSN':'SY', 
                 'UPIN':'1G', 
                 'License':'0B', 
                 'OtherID1':'ZZ', 
                 'OtherID2':'ZY'}
    """
    Possible values for OtherID1 and OtherID2:
    1H     CHAMPUS Identification Number
    1J     Facility ID Number
    B3     Preferred Provider Organization Number
    BQ     Health Maintenance Organization Code Number
    FH     Clinic Number
    G2     Provider Commercial Number
    G5     Provider Site Number
    LU     Location Number
    U3     Unique Supplier Identification Number (USIN)
    X5     State Industrial Accident Provider Number
    """
    nm1Types =  {'77': 'Service Location', 
                 '82': 'Rendering Provider',
                 '85': 'Billing Provider',
                 '87': 'Pay-To Provider',
                 'DK': 'Ordering Provider',
                 'DN': 'Referring Provider',
                 'DQ': 'Supervising Provider',
                 'FA': 'Facility',
                 'LI': 'Independent Lab',
                 'TL': 'Testing Lab',
                 'P3': 'Primary Care Provider',
                 '00': ''}
    
    def __init__(self, fileName, *args):
        self.xDoc = amara.create_document(u'npiList')
        for myAttr in args:
            self.xDoc.npiList.xml_append(self.xDoc.npiList.xml_create_element(unicode(myAttr)))
        self.fileName = fileName
        self.noMatch = {}
        self.noMatchX = {} #new, eXtended version
        
    def __getattr__(self, name):
        if ((name == 'xDoc') or (name == 'fileName') or (name == 'codeType') or (name == 'noMatch') or (name == 'noMatchX') or (name == 'nm1Types')):
            value = object.__getattribute__(self,name)
        else:
            try:
                exec('value = self.xDoc.npiList.' + name)
            except:
                print 'Ooopsie!'
                value   = ""
                raise
        return value
    def __setattr__(self, name, value):
        if ((name == 'xDoc') or (name == 'fileName') or (name == 'codeType') or (name == 'noMatch') or (name == 'noMatchX') or (name == 'nm1Types')):
            object.__setattr__(self, name, value)
        else:
            cmd = '''self.xDoc.npiList.''' + name + ''' = unicode("''' + value + '''")'''
            try:
                exec(cmd)
            except:  # I'm thinking of disabling this so elements can't be created on the fly
                self.xDoc.npiList.xml_append(self.xDoc.npiList.xml_create_element(unicode(name)))
                exec(cmd)
    def Load(self):
        errtext = "I can't open the NPI lookup file!  Click Preferences and select the file you created when you ran the NPI Update program (probably npiMap.XML)"
        if os.path.isfile(self.fileName):
            try:
                inFile = open(self.fileName,'r+b')
                rules = [amara.binderytools.ws_strip_element_rule(u'/*')]
                self.xDoc = amara.parse(inFile, rules=rules)
            except:
                raise NPIFileError(errtext)
        else:
            raise NPIFileError(errtext)
            print 'wtf?   ', self.fileName
            exit()
        
    def Save(self):
        outFile = open(self.fileName,'w+b')
        self.xDoc.xml(outFile,indent=u'yes')
        outFile.close()

    def xml(self):
        return self.xDoc.xml(indent=u'yes')

    def lookup(self, legCode, name="", nm1Type="00", field=""):
        """
        Given a legacy code, return a dictionary with three members:
        legacyCode
        legacyType
        NPI
        Match - Boolean
        If nm1Type (from ANSI 837) is provided, use it to qualify missing entities (provider, referral, etc.)
        If field (from 1500 form) is provided, use it to qualify missing entities (provider, referral, etc.)
        If name is provided, use it to identify missing codes in user message
        """
        #print "Lookup: ", nm1Type, name, legCode, field
        code = {"legacyCode":str(legCode), "legacyType":"", "NPI":"", "Match":True}
        for item in self.xDoc.xml_xpath(u'//npiItem'):
            if (item.legacyCode        == legCode):
                code["legacyType"]      = self.codeType[str(item.legacyType)]
                code["NPI"]             = str(item.NPI)
        if (code["NPI"] == ''):  # using a dict to hold misses, as it's the simplest way to avoid dupes
            tmpStr = legCode
            if legCode == '': tmpStr = "<none>"
            code["Match"] = False
            self.noMatch[legCode] = self.nm1Types[nm1Type] + field + ' ' + name # X12 conversions will pass nm1Type, 1500 uses fields - we can cover both
            self.noMatchX[nm1Type + field + name] = ("%s %s - Legacy code: %s " % (self.nm1Types[nm1Type], name, tmpStr))
            legCode # X12 conversions will pass nm1Type, 1500 uses fields - we can cover both
        #print code, nm1Type, name
        return code
    
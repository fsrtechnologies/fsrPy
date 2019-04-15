from __future__ import with_statement
import lxml.etree as etree
class NPIError(Exception):
    pass

class NPIFileError(NPIError):
    pass

class NPINoMatch(NPIError):
    pass

class NPIFile(object):
    """
    Skeleton for NPI map to be serialized to XML
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

    def __init__(self, fileName=""):
        self.xDoc = etree.Element(u'npiList')
        self.eTree = etree.ElementTree(self.xDoc)
        self.fileName = fileName
        self.noMatch = {}
        self.noMatchX = {} #eXtended version

    def Load(self):
        errtext = "I can't open the NPI lookup file!  Click Preferences and select the file you created when you ran the NPI Update program (probably npiMap.XML)"
        try:
            with open(self.fileName, "r") as inFile:
                parser = etree.XMLParser(remove_blank_text=True)
                self.eTree = etree.parse(inFile, parser)
                self.xDoc = self.eTree.getroot()
        except:
            raise NPIFileError(errtext)
        print "Loaded %s" % self.fileName

    def Save(self):
        with open(self.fileName,'w+b') as outFile:
            self.eTree.write(outFile, method="xml", encoding="UTF-8", xml_declaration=True, pretty_print=True)

    def lookup(self, legCode, name="", nm1Type="00", field=""):
        """
        Given a legacy code, return a dictionary with four members:
        legacyCode
        legacyType
        NPI
        Match - Boolean
        If nm1Type (from ANSI 837) is provided, use it to qualify missing entities (provider, referral, etc.)
        If field (from 1500 form) is provided, use it to qualify missing entities (provider, referral, etc.)
        If name is provided, use it to identify missing codes in user message
        """
        #print "Lookup: ", nm1Type, name, legCode, field
        code = {"legacyCode":str(legCode), "legacyType":None, "NPI":None, "Match":True}
        for tmpItem in self.xDoc.findall(u'.//npiItem'):
            # UltraMed adds 'HSP' prefix to some location Medicare numbers - number on form may be different from database
            if ((legCode == tmpItem[0].text) or (legCode == 'HSP' + tmpItem[0].text)):
                code["legacyType"]      = self.codeType[tmpItem.get("legacyType")]
                code["NPI"]             = tmpItem[1].text
        if (code["NPI"] == None):  # using a dict to hold misses, as it's the simplest way to avoid dupes
            tmpStr = legCode
            if legCode == '': tmpStr = "<none>"
            code["Match"] = False
            self.noMatch[legCode] = self.nm1Types[nm1Type] + field + ' ' + name # X12 conversions will pass nm1Type, 1500 uses fields - we can cover both
            self.noMatchX[nm1Type + field + name] = ("%s %s - Legacy code: %s " % (self.nm1Types[nm1Type], name, tmpStr))
            legCode # X12 conversions will pass nm1Type, 1500 uses fields - we can cover both
        return code

    def getNPI(self, legType, legCode):
        npiItems = self.xDoc.xpath('.//npiItem[@legacyType="%s" and legacyCode="%s"]' % (legType,legCode))
        if (len(npiItems) != 0):
            return npiItems[0].findtext("NPI")
        else:
            return ""

    def update(self, obj):
        npiItems = self.xDoc.xpath( u'//npiItem[@legacyType="%s" and legacyCode="%s"]' % (obj.LegType, obj.LegCode))
        print(obj.LegType, obj.LegCode, len(npiItems))
        print npiItems
        if (len(npiItems) == 0):            # if there's no entry for this legacy type and code
            if not (obj.NPI == ''):         #   - and the user has entered an NPI, create a new entry
                npiItem = etree.SubElement(self.xDoc, "npiItem", legacyType=obj.LegType)
                legCode = etree.SubElement(npiItem, "legacyCode")
                legCode.text = obj.LegCode
                npi_NPI = etree.SubElement(npiItem, "NPI")
                npi_NPI.text = obj.NPI
        else:                               # if this entry already exists
            if (obj.NPI == ''):             #   - and the user has removed the NPI, we need to delete it...
                for elem in npiItems:
                    elem.getparent().remove(elem)
            else:                           #   - and the user has changed the NPI, we need to update the existing entry
                for elem in npiItems:
                    for child in elem:
                        if child.tag == 'NPI': child.text = unicode(obj.NPI)
        self.Save()



if __name__ == '__main__':
    #import urllib

    mapThing = NPIFile(r'C:\ULTRAMED\npiMap.xml')
    mapThing.Load()
    print mapThing.getNPI('License', 'A54670')



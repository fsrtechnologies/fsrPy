import string, os

class ConfigFile(object):
    """Skeleton for config info to be serialized to XML via Amara"""
    def __init__(self, fileName, *args):
        self.xDoc = amara.create_document(u'config')
        for myAttr in args:
            self.xDoc.config.xml_append(self.xDoc.config.xml_create_element(unicode(myAttr)))
        self.fileName = fileName
    def __getattr__(self, name):
        try:
            value = ""            
            exec('value = self.xDoc.config.' + name)
            if (value == 'True'): value = True
            if (value == 'False'): value = False
        except:
            print 'Ooops!'
            raise
        return value
    def __setattr__(self, name, value):
        #print "set name: ", name, " value: ", value
        if ((name == 'xDoc') or (name == 'fileName')):
            object.__setattr__(self, name, value)
        else:
            if (value == True): value = 'True'
            if (value == False): value = 'False'
            try:
                exec('''self.xDoc.config.''' + name + ''' = unicode("''' + value + '''")''')
            except:  # I'm thinking of disabling this so elements can't be created on the fly
                self.xDoc.config.xml_append(self.xDoc.config.xml_create_element(unicode(name)))
                exec('''self.xDoc.config.''' + name + ''' = unicode("''' + value + '''")''')
    def Load(self):
        if os.path.exists(self.fileName):
            inFile = open(self.fileName,'r+b')
            rules = [amara.binderytools.ws_strip_element_rule(u'/*')]
            tmpxDoc = amara.parse(inFile, rules=rules)
            for elem in tmpxDoc.config.xml_child_elements:
                if elem in self.xDoc.config.xml_child_elements:
                    exec('self.xDoc.config.' + elem + ' = unicode(str(tmpxDoc.config.' + elem + '))')
               
    def Save(self):
        outFile = open(self.fileName,'w+b')
        self.xDoc.xml(outFile,indent=u'yes')
        outFile.close()

    def xml(self):
        return self.xDoc.xml(indent=u'yes')

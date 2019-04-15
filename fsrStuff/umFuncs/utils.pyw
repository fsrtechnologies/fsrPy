import calendar, locale, os, string, struct
from TLAList import TLAList
def NPI_Luhn(testStr): 
    """
    Verify NPI numbers using Luhn checkdigit algorithm.  
    NPI numbers are 10 digits long, but are compatible with standard 15-digit IDs
    on health identification cards.  NPIs, and only NPIs, will start with "1" or "2".
    If the NPI is 10 digits, the checkdigit is calculated as if the prefix 
    '80840' (health, United States) were present - so we add 24 to the sum.
    """
    sum = 0
    alt = False
    if (len(testStr) == 10): 
        if testStr[0] == '1' or testStr[0] == '2': # it's a 10-digit NPI - assume "80840" in front.
            sum = 24    

    for digit in reversed(testStr):
        tmpInt = int(digit)
        if(alt):
            tmpInt *= 2
            if (tmpInt > 9): tmpInt -= 9 # equivalent to adding the value of digits
        sum += tmpInt
        alt = not alt
    return (sum % 10 == 0)
    
def parseDirectDat(directFile):
    from Office import Office
    Offices = {}
    for line in open(directFile,'r').readlines():
        offNum = line[:2]
        item = line.split('=')[0].rstrip()[2:].upper()
        itmpath = line.split('=')[1].rstrip()
        if (os.path.isabs(itmpath)): 
            Path = itmpath
        else: 
            Path = os.path.join(os.path.dirname(directFile),itmpath)
        if (item == 'DEFAULT'): 
            Offices[offNum] = Office(offNum)
            Offices[offNum].Default = Path + offNum  # exceptions will have office number appended already...
            for tla in TLAList:
                setattr(Offices[offNum], tla, Path+offNum+tla)
            continue
        elif (item in TLAList): 
            setattr(Offices[offNum], item, Path+tla)
            continue
    return Offices



def date2BBBB(YYYYMMDD): # datecode is simply YYYYMMDD converted to a 4-byte int
    """Convert a date in YYYYMMDD format to UltraMed format."""
    return struct.pack('i',int(YYYYMMDD))

def BBBB2date(BBBB,sep=""):      # datecode is simply YYYYMMDD converted to a 4-byte int
    """Convert an UltraMed date to YYYYMMDD format."""
    str_tmp = str(struct.unpack('i',BBBB)[0])
    if (len(str_tmp) == 8): str_tmp = '%s%s%s%s%s' % (str_tmp[:4],sep,str_tmp[4:6],sep,str_tmp[6:]) 
    return str_tmp

def BB2time(BB, format=False): # decimal time is stored as a 2-byte short 
    """Convert UltraMed's 2-byte time to decimal
    Parameters: 
        12      for HH:MM AM/PM
        24      for HH:MM
        [none]  for HHMM"""
    if (format == '12'):
        tmpTime = struct.unpack('h',BB)[0]                 # creates a tuple - I just want the value
        tmpHr = tmpTime // 100
        tmpMin = tmpTime % 100
        tmpAP = "AM"
        if (tmpHr > 11): tmpAP = "PM"
        if (tmpHr > 12): tmpHr -= 12
        return '%02d:%02d %s' % (tmpHr, tmpMin, tmpAP)            
    elif (format == '24'):
        tmpTime = struct.unpack('h',BB)[0]                 # creates a tuple - I just want the value
        return '%02d:%02d' % ((tmpTime // 100), (tmpTime % 100))            
    else:
        return struct.unpack('h',BB)[0]                 # creates a tuple - I just want the value

def time2BB(deci): # timecode is simply decimal time converted to a 2-byte short
    """Convert decimal time (e.g. 2345 for 11:45PM) to UltraMed's 2-byte format"""
    return struct.pack('h',int(deci))

def day_of_week(YYYYMMDD): # Python's calendar starts with Monday - I need Sunday
    """Wraps the calendar.weekday function for convenience - shift the day numbers and convert from string"""
    return (calendar.weekday(int(YYYYMMDD[:4]), int(YYYYMMDD[4:6]), int(YYYYMMDD[6:]))+ 1) % 7

def BBBB2zip(BBBB,sep=False): # zipcode is stored as a 4-byte int
    """Convert UltraMed's 4-byte zipcode to decimal 
    By default, 9-digit zipcodes will not be separated - if desired,pass separator as second parameter"""
    tmp_str =str(struct.unpack('i',BBBB)[0])        # creates a tuple - I just want the value
    if (len(tmp_str)<5):tmp_str = tmp_str.zfill(5)
    if ((len(tmp_str)>5) and (len(tmp_str)<9)):tmp_str = tmp_str.zfill(9)
    if (len(tmp_str)>5): 
        if sep: tmp_str = '%s%s%s' % (tmp_str[:5], sep, tmp_str[5:]) # if parameter was supplied, use it as separator
    return tmp_str

def BBBB2ssn(BBBB, sep=False): # SSN is stored as a 4-byte int
    """Convert UltraMed's 4-byte SSN to decimal
    By default, digits will not be separated - if desired,pass separator as second parameter"""
    tmp_str = str(struct.unpack('i',BBBB)[0])        # creates a tuple - I just want the value
    if sep: tmp_str = '%s%s%s%s%s' % (tmp_str[:3], sep, tmp_str[3:5], sep, tmp_str[5:])
    return tmp_str

def BBBB2money(BBBB): # Charges in transactions are stored as 2-byte unsigned shorts
    """Convert UltraMed's 2-byte charges, etc. to monetary values"""
    return locale.format('%.2f', (struct.unpack('L',BBBB)[0] / 100.00), True) # struct.unpack returns a tuple - I just want the value
    
#def BBBB2money(BBBB): # Monetary values are stored as 4-byte ints
    #"""Convert UltraMed's 4-byte prices, etc. to monetary values"""
    #tmp_str = str(struct.unpack('i',BBBB)[0])        # creates a tuple - I just want the value
    #if (len(tmp_str) > 2): tmp_str = '%s.%s' % (tmp_str[:-2], tmp_str[-2:])
    #return tmp_str
    
def BBBB2money2(BBBB): # Monetary values are stored as 4-byte ints, but RVS and RBRVS use 3 decimal places
    """Convert UltraMed's RVS and RBRVS values, etc. to monetary values"""
    tmp_str = str(struct.unpack('i',BBBB)[0])        # creates a tuple - I just want the value
    if (len(tmp_str) > 2): tmp_str = '%s.%s' % (tmp_str[:-3], tmp_str[-3:-1])
    return tmp_str

def B2int(B):
    return struct.unpack('B',B)[0]

def BB2Long(BB):
    return struct.unpack('H',BB)[0]

def raw2phone(raw):
    """Format a 10-digit phone number"""
    tmp_str = ""
    if (len(raw) > 1):
        tmp_str = '(%s) %s-%s' % (raw[:3], raw[3:6], raw[6:])
    return tmp_str
class Translator(object):
    """Wraps up the string.translate() function to keep us sane...
    1) Keeping only a given set of characters.
        >>> trans = Translator(keep=string.digits)
        >>> trans('Chris Perkins : 224-7992')
        '2247992'
    2) Deleting a given set of characters.
        >>> trans = Translator(delete=string.digits)
        >>> trans('Chris Perkins : 224-7992')
        'Chris Perkins : -'
    3) Replacing a set of characters with a single character.
        >>> trans = Translator(string.digits, '#')
        >>> trans('Chris Perkins : 224-7992')
        'Chris Perkins : ###-####'
    Posted to ASPN Python Cookbook by Chris Perkins - thanks!
    """
    allchars = string.maketrans('','')
    def __init__(self, frm='', to='', delete='', keep=None):
        if len(to) == 1:
            to = to * len(frm)
        self.trans = string.maketrans(frm, to)
        if keep is None:
            self.delete = delete
        else:
            self.delete = self.allchars.translate(self.allchars, keep.translate(self.allchars, delete))
    def __call__(self, s):
        return s.translate(self.trans, self.delete)

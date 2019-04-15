import string
from decimal import Decimal
import re

def sorted_nicely( l ): #Thank you @MarkByers from StackOverflow!
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def fixZip(inStr):
    if len(inStr) == 9:
        return "%s-%s" % (inStr[:5], inStr[5:])
    else:
        return inStr

def fixPhone(inStr):
    if len(inStr) == 10:
        return "(%s) %s-%s" % (inStr[:3], inStr[3:6], inStr[6:])
    else:
        return inStr


def monetize(inStr):
    try:
        return Decimal(inStr).quantize(Decimal('.01'))
    except:
        return 0.00

def fixDate(inDate=None, spaces=True, forceYear=None, slashes=False):
    """
    Receive a date string of unknown format, return it in the form requested.
    Make certain assumptions:
        if inDate contains no spaces -
            if it's 8 digits long -
                if first two digits are greater than 12, it's CCYYMMDD
                if first two digits are 12 or less, it's MMDDCCYY
            if it's 6 digits, it's MMDDYY
        else (if inDate has spaces) -
            if it's broken into more or less than three pieces, just send it back unchanged
            if the first piece is four digits, it's CCYY MM DD
            else it's MM DD YY
    Return format:
        if spaces==True, send back MM DD YY (or MM DD CCYY)
        if forceYear==None, leave the year as it is
        if forceYear==2, send year as YY, even if we received CCYY
        if forceYear==4, send year as CCYY, even if we received YY - use 50 as breakpoint (48=2048, 49=2049, 50=1950, 51=1951)
    """
    Sep = ''
    if spaces:
        Sep = ' '
    if slashes:
        Sep = '/'
    if inDate.isdigit():  #if there are no spaces in the original date
        if len(inDate) == 8:  # e.g. '20090213'
            if int(inDate[:2]) > 12:
                newList = [inDate[4:6], inDate[6:], inDate[:4] ]
            else:
                newList = [inDate[:2], inDate[2:4], inDate[4:] ]
        else:                 # e.g. '021309'
            newList = [inDate[:2], inDate[2:4], inDate[4:] ]
    else: # if there ARE spaces
        tmpList = inDate.split()
        if len(tmpList) == 3:
            if len(tmpList[0]) == 4:
                newList = [tmpList[1], tmpList[2], tmpList[0] ]
            else:
                newList = [tmpList[0], tmpList[1], tmpList[2] ]
        else:
            return inDate  # it's not one piece, it's not three pieces - send it back unchanged
    if forceYear == 2:
        newList[2] = newList[2][-2:] # just the last two digits, even if it was only two digits
    elif forceYear == 4:
        if len(newList[2]) != 4: #if it's not 4 digits, it's probably 2 - but why assume?
            YY = newList[2][-2:]
            if int(YY) >= 50:
                newList[2] = '20' + YY
            else:
                newList[2] = '19' + YY

    return string.join(newList, Sep)

def fixDateYYMMDD(inDate=None, spaces=True, forceYear=None, slashes=True):
    """
    Receive a date string of format YYMMDD, return it in the form requested.
    Return format:
        if spaces==True, send back MM DD YY (or MM DD CCYY)
        if forceYear==None, leave the year as it is
        if forceYear==2, send year as YY, even if we received CCYY
        if forceYear==4, send year as CCYY, even if we received YY - use 50 as breakpoint (48=2048, 49=2049, 50=1950, 51=1951)
    """
    Sep = ''
    if spaces:
        Sep = ' '
    if slashes:
        Sep = '/'
    newList = [inDate[2:4], inDate[4:], inDate[:2] ]
    if forceYear == 2:
        newList[2] = newList[2][-2:] # just the last two digits, even if it was only two digits
    elif forceYear == 4:
        if len(newList[2]) != 4: #if it's not 4 digits, it's probably 2 - but why assume?
            YY = newList[2][-2:]
            if int(YY) >= 50:
                newList[2] = '20' + YY
            else:
                newList[2] = '19' + YY

    return string.join(newList, Sep)


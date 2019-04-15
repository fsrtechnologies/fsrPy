#!/usr/bin/python
import os, os.path, sys, time
import logging
from win32com.client import Dispatch
from RTFdirs import * 

class Global(object):
    prov = {
        'EHRICH':   'F3EB789F-3C81-454F-845B-BAD78B0BEC6B',
        'KIM':      'BC3DFBD5-0077-4D87-A959-66B63B32727C',
        'PERRY':    '3E308D6D-85F8-44CD-B031-7E0ECD75A9EC',
        'SIMON':    '997B2DC9-1A2A-4665-B284-DC763273A8C0',
        'WONG':     '709EFD10-5419-4710-9CDB-688FDEF2785F',
        'WORK':     'FC58DDE8-4B1E-46AC-8B7D-16CE9F5CCF50'}
        
    # the only extra description that ever comes up is "Echo", 
    #    but I put it in a dict just in case I found more
    desc = {
        'ECHO':     ('Echo','Echo'),
        'STRESS':   ('Stress Test','Stress Test'),
        'CDS':      ('Vascular', 'Carotid Duplex Scan'),
        'LETTER':   ('Correspondence', 'Letter'),
        }

    locID = {
        "CCMG":     ("9D971E61-2B5A-4504-9016-7FD863790EE2", "Cardiology Consultants Medical Group of the Valley"),
        "TMC":      ("9293680B-6AE0-4002-ABAB-59718CD3B0F5", "Tarzana Medical Center"),
        "MPMC":     ("1462492F-1172-4B40-B5B2-C953792004DC", "Motion Picture Medical Center"),
        "CWHMC":    ("C3B7D5F0-6918-4E08-BE82-F3A23E7988A5", "Columbia West Hills Medical Center"),
        "CSMC":     ("5A55865D-7AAB-45EA-A39D-703B84B15E2F", "Cedars Sinai Medical Center"),
        "SJMC":     ("FB00EAF7-1F44-4597-BF4D-2E597E085C53", "St Joseph Medical Center"),
        "BHHC":     ("7851B1F6-00CE-4A9E-8075-4FD0176C4EB8", "Bob Hope Health Center"),
        "JSHC":     ("5B414D52-D71E-4FC4-8D6C-CE2F89EF31CD", "Jack Skirball Health Center"),
        "SCHC":     ("259549B6-F7E2-4ED4-B615-EBDBDF8A283C", "Santa Clarita Health Center"),
        "TLHC":     ("59E98380-22AB-4D31-B60C-447E0CEE164E", "Toluca Lake Health Center"),
        "WHC":      ("2E0FAE05-7D6B-4702-98FA-51262A4D7D81", "Westside Health Center"),
        "EH":       ("D9DBEF87-9108-4FAF-BD79-03CD8FDA4A30", "Encino Hospital"),
        }

    totalFiles = 0
    skippedFiles = 0
    failedFiles = 0
    
def getTimeStamp():
    stampFile = os.path.abspath(targetDir + os.sep + "stamp")
    os.chdir(targetDir)
    stampTime = time.localtime(0)
    if os.path.isfile(stampFile):
        try:
            inFile=open(stampFile,'r+b') 
            try:
                tmpDate = time.strptime(inFile.readline().strip(), "%a %m/%d/%Y")
            except:
                tmpDate = time.localtime(0)
            try:
                tmpTime = time.strptime(inFile.readline().strip(), "%H:%M %p")
            except:
                tmpTime = time.localtime(0)
            stampTime = (tmpDate[0], tmpDate[1], tmpDate[2], tmpTime[3], tmpTime[4], tmpTime[5], 0, 0, -1)
            inFile.close()
        except:
            stampTime = time.localtime(0)
            pass

    stampTime = time.mktime(stampTime)
    return stampTime

    
def doConversion(oldPath):
    oldName = os.path.basename(oldPath).upper()
    (oldBaseName, oldExt)=os.path.splitext(oldName)
    if not (oldExt=='.DOC'): # skip anything that's not a Word doc
        Global.skippedFiles +=1
        return
    # there are lots of daily roster files - we don't want them
    # also lots of orphaned temporary documents...
    if oldBaseName.startswith(('ROSTER', '\~'),0):
        Global.skippedFiles +=1
        return
    nameParts = oldBaseName.split('-')
    # No MRN to be had from "Last,First-Date-Doc.doc" or 
    #   "Last,First--Date-Doc.doc"
    if  ((len(nameParts) < 4) or (len(nameParts[1]) == 0)): 
        logging.error("%s - no MRN" % oldPath)
        Global.failedFiles +=1
        return
        
    newParts = {}
    try:
        # filename has date in standard position
        tmpDate = time.strptime(nameParts[2].strip(), "%d%B%Y")
    except ValueError:
        try:
            # "Last,First-Date-Doc-Echo.doc"
            tmpDate = time.strptime(nameParts[1].strip(), "%d%B%Y")
            logging.error("%s - no MRN" % oldPath)
            Global.failedFiles +=1
            return
        except ValueError:
            try:
                # "Last,First-MRN-Echo-Date-Doc.doc" or "Last,First-MRN-Doc-Date.doc" 
                # or some other bizarre combo - but we can work with it
                tmpDate = time.strptime(nameParts[3].strip(), "%d%B%Y")
            except ValueError:
                logging.error("%s - no date" % oldPath)
                Global.failedFiles +=1
                return
    newParts['date'] = time.strftime("%m/%d/%Y", tmpDate)

    # save time by cleaning these up just once
    tmpStr1 = nameParts[-1].strip()
    try:
        tmpStr2 = nameParts[-2].strip()
    except:
        tmpStr2 = ""
    try:
        tmpStr3 = nameParts[-3].strip()
    except:
        tmpStr3 = ""
    try:
        tmpStr4 = nameParts[-4].strip()
    except:
        tmpStr4 = ""
    try:
        tmpStr5 = nameParts[-5].strip()
    except:
        tmpStr5 = ""
    # Files may be "Last,First-MRN-Date-Doc.doc" (most common) OR
    #  may have an extra description, like so:
    #    "Last,First-MRN-Date-Echo-Doc.doc" OR
    #    "Last,First-MRN-Date-Doc-Echo.doc" 

    if tmpStr1 in Global.prov:
        newParts['prov'] = Global.prov[tmpStr1]
    elif tmpStr2 in Global.prov:
        newParts['prov'] = Global.prov[tmpStr2]
    elif tmpStr3 in Global.prov:
        newParts['prov'] = Global.prov[tmpStr3]
    elif tmpStr4 in Global.prov:
        newParts['prov'] = Global.prov[tmpStr4]
    elif tmpStr5 in Global.prov:
        newParts['prov'] = Global.prov[tmpStr5]
    else: 
        logging.error("%s - no provider" % oldPath)
        Global.failedFiles +=1
        return

    if tmpStr1 in Global.desc:
        newParts['cat'] = Global.desc[tmpStr1][0]
        newParts['desc'] = Global.desc[tmpStr1][1]
    elif tmpStr2 in Global.desc:
        newParts['cat'] = Global.desc[tmpStr2][0]
        newParts['desc'] = Global.desc[tmpStr2][1]
    elif tmpStr3 in Global.desc:
        newParts['cat'] = Global.desc[tmpStr3][0]
        newParts['desc'] = Global.desc[tmpStr3][1]
    elif tmpStr4 in Global.desc:
        newParts['cat'] = Global.desc[tmpStr4][0]
        newParts['desc'] = Global.desc[tmpStr4][1]
    elif tmpStr5 in Global.desc:
        newParts['cat'] = Global.desc[tmpStr5][0]
        newParts['desc'] = Global.desc[tmpStr5][1]
    else: 
        newParts['cat'] = 'Consultation'
        newParts['desc'] = 'Consultation'
    

    if tmpStr1 in Global.locID:
        newParts['loc'] = Global.locID[tmpStr1][0]
    elif tmpStr2 in Global.locID:
        newParts['loc'] = Global.locID[tmpStr2][0]
    elif tmpStr3 in Global.locID:
        newParts['loc'] = Global.locID[tmpStr3][0]
    elif tmpStr4 in Global.locID:
        newParts['loc'] = Global.locID[tmpStr4][0]
    elif tmpStr5 in Global.locID:
        newParts['loc'] = Global.locID[tmpStr5][0]
    else: 
        newParts['loc'] = Global.locID["CCMG"][0]


    # lots and lots of files with no MRN but x's as placeholders like this:     
    #    "Last,First-xxx-Date-Doc.doc"  or
    #    "Last,First-____-Date-Doc.doc"
    if (nameParts[1][1] == 'X') or (nameParts[1][1] == 'X'): 
        logging.error("%s - no MRN" % oldPath)
        Global.failedFiles +=1
        return
    else:
        newParts['MRN'] = nameParts[1].strip()
    try:
        doc = Global.wrd.Documents.Open(os.path.abspath(oldPath))
    except Exception, exc:
        logging.error("opening %s -- %s" % (oldPath, exc))
        Global.failedFiles +=1
    try:
        Global.wrd.Run("RTF", newParts['MRN'], 
                        newParts['date'], 
                        newParts['prov'], 
                        newParts['cat'], 
                        newParts['loc'], 
                        newParts['desc'], 
                        targetDir)
    except Exception, exc:
        logging.error("error while converting %s -- %s" % (oldPath, exc))
        Global.failedFiles +=1


# the guts...

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s %(message)s',
                    filename='RTF.log',
                    filemode='w')
logging.info("Start time: %s" % time.clock())
timeStamp = getTimeStamp()
logging.info("Converting files newer than: %s" % timeStamp)
Global.wrd = Dispatch('Word.Application')
Global.wrd.Visible = 1
for startDir in startDirs:
    logging.info("Processing folder: %s" % startDir)
    folders = [startDir]
    while len(folders)>0:
        fld = folders.pop()
        for name in os.listdir(fld):
            fullpath = os.path.join(fld,name)
            if os.path.isfile(fullpath):
                tmpName = os.path.basename(fullpath).upper()
                (tmpBaseName, tmpExt)=os.path.splitext(tmpName)
                if not (tmpExt=='.DOC'): 
                    continue
                elif (tmpBaseName.startswith('ROSTER') or tmpBaseName.startswith('~')):
                    continue
                elif os.path.getmtime(fullpath) > timeStamp:
                    Global.totalFiles +=1
                    doConversion(fullpath)
            elif os.path.isdir(fullpath):
                folders.append(fullpath)
                
    logging.info("Finished with folder: %s - time elapsed %.4f seconds" % (startDir, time.clock()))
Global.wrd.Quit()
logging.info("All done! Total files: %s  Skipped (rosters, etc.): %s  Failed: %s - total processing time %.4f seconds" % (Global.totalFiles, Global.skippedFiles, Global.failedFiles, time.clock()))



#!/usr/bin/python
import os, os.path, sys, time, datetime, shutil
from RTFdirs import * 


class Global(object):
    pass

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
print stampTime
for startDir in startDirs:
    folders = [startDir]
    while len(folders)>0:
        fld = folders.pop()
        for name in os.listdir(fld):
            fullpath = os.path.join(fld,name)
            if os.path.isfile(fullpath):
                tmpName = os.path.basename(fullpath).upper()
                (tmpBaseName, tmpExt)=os.path.splitext(tmpName)
                if not (tmpExt=='.RTF'): 
                    continue
                elif (tmpBaseName.startswith('ROSTER') or tmpBaseName.startswith('~')):
                    continue
                elif os.path.getmtime(fullpath) > stampTime:
                    shutil.copy2(fullpath, targetDir)
            elif os.path.isdir(fullpath):
                folders.append(fullpath)

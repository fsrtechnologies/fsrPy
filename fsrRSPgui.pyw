from __future__ import print_function
import os, time, shutil, io, zipfile
from fsrStuff.X12 import X12_277, X12_835, X12_999, X12_TA1
from fsrStuff.X12.X12Thing import X12Thing, Not_X12
from configobj import ConfigObj
from validate import Validator
try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO

cfgFileName = os.getcwd() + os.sep + 'fsrRSP.ini'
# Upd 9Dec2013 for Nourparvar: copy 835 file to specified destination folder
# Upd 9Mar2015 for Nourparvar: copy 999 file to specified destination folder also
tmpStr = """
ediDirs = string_list(default=None)
outBase = string(default=r"C:\X12PDF")
oldBase = string(default="old")
base835 = string(default="old")
"""
print(cfgFileName)
cfgSpec = StringIO.StringIO(tmpStr)
cfgFile = ConfigObj(cfgFileName,
            configspec=cfgSpec, raise_errors=True, write_empty_values=True,
            create_empty=True, indent_type='    ', list_values=True)
vtor = Validator()
lineNum = 0
test = cfgFile.validate(vtor, copy=True)
cfgFile.write()

codeFile = os.path.abspath("codeTable.db")
for ediDir in cfgFile['ediDirs']:
    print(ediDir)
    ediOld = ediDir + os.sep + cfgFile['oldBase']
    if not os.path.isdir(ediOld):
        os.makedirs(ediOld)
    edi835 = ediDir + os.sep + cfgFile['base835']
    if not os.path.isdir(edi835):
        os.makedirs(edi835)

    for inObj in os.listdir(ediDir):
        #first pass, extract any zip files to current dir and move them to Old
        inFile = ediDir + os.sep + inObj
        print(inFile)
        if zipfile.is_zipfile(inFile):
            print(inFile + 'is a zipfile')
            with zipfile.ZipFile(inFile, 'r') as zf:
                zf.extractall(path=ediDir)
            basename = os.path.basename(inObj)
            dst_file = os.path.join(ediOld, basename)
            try:
                os.rename(inFile, dst_file)
            except:  # if time stamp is same as existing file, skip it
                print('Failed to move ' + inFile + 'to ' + dst_file)
                continue

    for inObj in os.listdir(ediDir):
        #second pass, deal with response files as normal
        ediFile = ediDir + os.sep + inObj
        if os.path.isdir(ediFile):
            continue
        timeStruct = time.gmtime(os.path.getmtime(ediFile))
        outDir = "%s%s%04d%s%02d%s%02d" % (cfgFile['outBase'], os.sep,
                timeStruct.tm_year, os.sep, timeStruct.tm_mon, os.sep,
                timeStruct.tm_mday)
        if not os.path.isdir(outDir):
            os.makedirs(outDir)

        basename = os.path.basename(inObj)
        head, tail = os.path.splitext(basename)
        dst_file = os.path.join(ediOld, basename)

        print("Processing %s ..." % ediFile)
        try:
            thingy = X12Thing(ediFile)
        except Not_X12:
            if tail == ".TRNACK":
                with open(ediFile, 'r') as f:
                    for line in f.readlines():
                        if line[:10] == "Time Stamp":
                            dst_file = "TrnAck" + line[-15:-1] + ".txt"
                dst_file = os.path.join(ediOld, dst_file)
                try:
                    os.rename(ediFile, dst_file)
                except:  # if time stamp is same as existing file, skip it
                    continue
                os.startfile(dst_file)
            else:
                print("%s is not an X12 file" % ediFile)
                continue
        if thingy.TA1:
            thisX12 = X12_TA1(thingy.TA1Rec, thingy.ISARec, pdfDir=outDir)
            thisX12.toPDF()
        else:
            for gsLoop in thingy.GSLoop:
                verNum = gsLoop.GSRec[8]
                fgDate = gsLoop.GSRec[4]
                for stLoop in gsLoop.STLoop:
                    if stLoop.STRec[1] == '277':
                        thisX12 = X12_277(stLoop, verNum, thingy.SubElemSep,
                        thingy.inFileName, thingy.testProd, codeFile, outDir)
                    elif stLoop.STRec[1] == '835':
                        thisX12 = X12_835(stLoop, verNum, thingy.SubElemSep,
                        thingy.inFileName, thingy.testProd, codeFile, outDir)
                        # for Nourparvar: do we want a separate copy or not?
                        if cfgFile['base835'] != cfgFile['oldBase']:
                            shutil.copy(ediFile, os.path.join(edi835, basename))
                    elif stLoop.STRec[1] == '999':
                        thisX12 = X12_999(stLoop, verNum, thingy.SubElemSep,
                        thingy.inFileName, thingy.testProd, fgDate, outDir)
                        # for Nourparvar: do we want a separate copy or not?
                        if cfgFile['base835'] != cfgFile['oldBase']:
                            shutil.copy(ediFile, os.path.join(edi835, basename))
                    else:
                        print(stLoop.STRec)
                    try:
                        thisX12.toPDF()
                    except NameError:
                        print("Error processing %s as an X12 file" % ediFile)
        count = 0
        while os.path.exists(dst_file):
            count += 1
            dst_file = os.path.join(ediOld, '%s-%03d%s' % (head, count, tail))
        os.rename(ediFile, dst_file)

import time
import struct
import calendar
import re
from um_funcs import *

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
width, height = letter  #keep for later

start_time = time.time()

office = '/kaminsky/01dat/01'

leftMargin = 0.3*inch
topMargin = 0.4*inch
lblHeight = 1*inch
lblWidth = 2.625*inch
labelpos = [(leftMargin,(height - topMargin - 0*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 0*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 0*lblHeight)),
            (leftMargin,(height - topMargin - 1*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 1*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 1*lblHeight)),
            (leftMargin,(height - topMargin - 2*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 2*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 2*lblHeight)),
            (leftMargin,(height - topMargin - 3*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 3*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 3*lblHeight)),
            (leftMargin,(height - topMargin - 4*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 4*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 4*lblHeight)),
            (leftMargin,(height - topMargin - 5*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 5*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 5*lblHeight)),
            (leftMargin,(height - topMargin - 6*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 6*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 6*lblHeight)),
            (leftMargin,(height - topMargin - 7*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 7*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 7*lblHeight)),
            (leftMargin,(height - topMargin - 8*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 8*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 8*lblHeight)),
	    (leftMargin,(height - topMargin - 9*lblHeight)),((leftMargin + lblWidth),(height - topMargin - 9*lblHeight)),((leftMargin + 2*lblWidth),(height - topMargin - 9*lblHeight))]

fontFace = 'Helvetica'
fontSize = 9
#=============================================================================================
#   Load the patient file to a list and sort it by (whatever we define below)
#=============================================================================================
reflen = 384
infile = open(office + 'ref.dat','r+b')
logfile = open(office + 'fix_app.log','w')

refs_orig = []

infile.read(reflen)                 # burn the header record 
inrec = infile.read(reflen)         # read the rest of the PAT file into the list
while not (len(inrec) < reflen):
    refs_orig.append(inrec)
    inrec = infile.read(reflen)
infile.close()

deco = [ (line[5:9], i, line) for i, line in enumerate(refs_orig) ] # create a "decorated" list with the key we want to sort by
del refs_orig                       # kill the original list - free up memory

deco.sort()                         # sort the decorated list
refs_sorted = [line for _, _, line in deco] # copy it to an "undecorated" list
del deco                            # and kill the decorated copy

logline = 'Sorted - %0.3f seconds so far. \n' % (time.time() - start_time)
logfile.write(logline)
print logline

#=============================================================================================
#   Now that the list is sorted...
#=============================================================================================
docsfile =  canvas.Canvas(office + 'doclbl.pdf', pagesize=letter)
attyfile = canvas.Canvas(office + 'attlbl.pdf', pagesize=letter)
empsfile = canvas.Canvas(office + 'emplbl.pdf', pagesize=letter)
othrfile = canvas.Canvas(office + 'othlbl.pdf', pagesize=letter)
total_rec_in = 0

docs_out = 0
atty_out = 0
emps_out = 0
othr_out = 0

for refrec in refs_sorted:
    total_rec_in +=1
    if not refrec[5:6].isalnum() : continue  # dropping garbage records
    this = reffields(refrec)
    outstr = ''
    if (len(this['company'])> 1): outstr = this['company'] + '\n'
    if (len(this['name'])> 1): outstr = outstr + this['name'] + '\n'
    outstr = outstr + this['street']
    if (len(this['suite'])> 1): outstr = outstr + ' ' + this['suite']
    outstr = outstr + '\n' + this['city'] + ', ' + this['state'] + ' ' + this['zip']

    if (this['ref_id'][0] == 'P'):
        if (docs_out % 30 == 0):
            if (docs_out > 0):docsfile.showPage()
            docsfile.setFont(fontFace, fontSize)
            docsfile.setStrokeColorRGB(255,255,255)
        textobject = docsfile.beginText()
        textobject.setTextOrigin(labelpos[docs_out % 30][0],labelpos[docs_out % 30][1])
        textobject.textLines(outstr)
        docsfile.drawText(textobject)
        del textobject
        docs_out += 1
        continue

    if (this['ref_id'][0] == 'A'):
        if (atty_out % 30 == 0):
            if (atty_out > 0):attyfile.showPage()
            attyfile.setFont(fontFace, fontSize)
            attyfile.setStrokeColorRGB(255,255,255)
        textobject = attyfile.beginText()
        textobject.setTextOrigin(labelpos[atty_out % 30][0],labelpos[atty_out % 30][1])
        textobject.textLines(outstr)
        attyfile.drawText(textobject)
        del textobject
        atty_out +=1
        continue

    if (this['ref_id'][0] == 'E'):
        if (emps_out % 30 == 0):
            if (emps_out > 0):empsfile.showPage()
            empsfile.setFont(fontFace, fontSize)
            empsfile.setStrokeColorRGB(255,255,255)
        textobject = empsfile.beginText()
        textobject.setTextOrigin(labelpos[emps_out % 30][0],labelpos[emps_out % 30][1])
        textobject.textLines(outstr)
        empsfile.drawText(textobject)
        del textobject
        emps_out += 1
        continue
        
    if (othr_out % 30 == 0):
        othrfile.showPage()
        othrfile.setFont(ourFont, 10)
        othrfile.setStrokeColorRGB(255,255,255)
    textobject = othrfile.beginText()
    textobject.setTextOrigin(labelpos[othr_out % 30][0],labelpos[othr_out % 30][1])
    textobject.textLines(outstr)
    othrfile.drawText(textobject)

    othr_out +=1
#=======================================================================================================================================
#   and... loop!

docsfile.showPage()
docsfile.save()
attyfile.showPage()
attyfile.save()
empsfile.showPage()
empsfile.save()
othrfile.showPage()
othrfile.save()

logline = 'Read %u records from REF file \n  Wrote: \n \t %u doctor labels \n \t %u attorney labels \n \t %u employer labels  \n \t %u "other" labels \nTotal time %0.3f seconds. \n' % (total_rec_in, docs_out, atty_out, emps_out, othr_out, (time.time() - start_time) )
logfile.write(logline)
logfile.close()
print logline

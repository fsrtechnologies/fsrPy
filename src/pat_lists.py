import time
import struct
import calendar
from um_funcs import *
start_time = time.time()

office = '/bhiars/01dat/01'
#office = '/ultrahld/01dat/01'
#office = "u:/ultramed/01dat/01"

#=============================================================================================
#   Load the patient file to a list and sort it by (whatever we define below)
#=============================================================================================
patlen = 1024
infile = open(office + 'pat.dat','r+b')
logfile = open(office + 'fix_app.log','w')

pats_orig = []

infile.read(patlen)                 # burn the header record 
inrec = infile.read(patlen)         # read the rest of the PAT file into the list
while not (len(inrec) < patlen):
    pats_orig.append(inrec)
    inrec = infile.read(patlen)
infile.close()

deco = [ (line[5:16], i, line) for i, line in enumerate(pats_orig) ] # create a "decorated" list with the key we want to sort by
del pats_orig                       # kill the original list - free up memory

deco.sort()                         # sort the decorated list
pats_sorted = [line for _, _, line in deco] # copy it to an "undecorated" list
del deco                            # and kill the decorated copy

logline = 'Sorted - %0.3f seconds so far. \n' % (time.time() - start_time)
logfile.write(logline)
print logline

#=============================================================================================
#   Now that the list is sorted...
#=============================================================================================
#outfile = open(office + 'patnew.dat','w+b')
tstfile = open(office + 'pattst.csv','w+b')
total_rec_in = 0
total_rec_out = 0

tstfile.write('"pat_last","pat_first","pat_mi","pat_acct","pat_chart","pat_addr1","pat_str","pat_city","pat_st","pat_zip","pat_phone","msg_1","msg_2" \n')      #  new PAT header

for patrec in pats_sorted:
    total_rec_in +=1
    if not patrec[5:6].isalnum() : continue  # dropping garbage records
    total_rec_out +=1
    this = patfields(patrec)
    outstr = '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"' % (this['pat_last'], this['pat_first'], this['pat_mi'], this['pat_acct'], this['pat_chart'], this['pat_addr1'], this['pat_str'], this['pat_city'], this['pat_st'], this['pat_zip'], this['pat_phone'], this['msg_1'], this['msg_2']) + "\n"
    tstfile.write(outstr)
#=======================================================================================================================================
#   and... loop!

#outfile.close()
logline = 'Read %u records from old PAT file \n wrote %u records to new PAT file \n Total time %0.3f seconds. \n' % (total_rec_in, total_rec_out, (time.time() - start_time) )
logfile.write(logline)
logfile.close()
print logline

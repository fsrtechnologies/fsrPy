#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Marc
#
# Created:     17/09/2015
# Copyright:   (c) Marc 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os.path

def main():
    shortFile = os.path.join(os.path.expanduser("~"),"Desktop","ICD10short.txt")
    midFile = os.path.join(os.path.expanduser("~"),"Desktop","ICD10mid.txt")
    outFile = os.path.join(os.path.expanduser("~"),"Desktop","ICD10out.txt")
    """
    with open(midFile, 'w') as Out:
        with open(inFile, 'r') as In:
            for line in In.readlines():
                tmp = line.split('|')
                if len(tmp[0]) == 7: tmp[0] += ' '
                if len(tmp[0]) == 6: tmp[0] += '  '
                if len(tmp[0]) == 5: tmp[0] += '   '
                if len(tmp[0]) == 4: tmp[0] += '    '
                if len(tmp[0]) == 3: tmp[0] += '     '
                if len(tmp[0]) == 2: tmp[0] += '      '
                Out.write('|'.join(tmp))
    """
    with open(midFile, 'r') as In:
        tmp = In.readlines()
        tmp.sort(key = len)
    with open(midFile, 'w') as Mid:
        with open(shortFile, 'a') as Short:
            for line in tmp:
                if len(line) > 50:
                    Mid.write(line)
                else:
                    Short.write(line)
if __name__ == '__main__':
    main()

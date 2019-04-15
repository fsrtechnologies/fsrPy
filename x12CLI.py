from fsrStuff.X12 import X12_837

'''
Created on Sep 20, 2012

@author: Marc
'''

if __name__ == '__main__':
    inFile = r'C:\NextGenFiles\mcare'
    inFile = r'C:\Users\Marc\Desktop\HPy\837'
    outFile = r'C:\NextGenFiles\mcare'
    outFile = r'C:\Users\Marc\Desktop\pdfs'
    thingy = X12_837(inFile)
    thingy.addTraceNumber()
    thingy.tofile(outFile)
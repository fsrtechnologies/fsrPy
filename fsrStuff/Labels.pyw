from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch

from umFuncs import *

class Avery5160(object):
    def __init__(self, outFile):
        self.width, self.height = letter  #keep for later
        self.List = []
        self.outFile = outFile
        self.leftMargin = 0.33*inch
        self.topMargin = 0.75*inch
        self.lblHeight = 1*inch  # Avery 5160 labels are 1 inch tall by 2 5/8 inches wide, 3 up, 10 rows.
        self.lblWidth = 2.625*inch
        self.vertFudge = 0*inch  # Unfortunately, they don't line up nominally...
        self.horzFudge = 0.15*inch
        self.lblHeight = self.lblHeight + self.vertFudge
        self.lblWidth = self.lblWidth + self.horzFudge
        self.labelpos = [(self.leftMargin,(self.height - self.topMargin - 0*self.lblHeight)),((self.leftMargin + self.lblWidth),(self.height - self.topMargin - 0*self.lblHeight)),((self.leftMargin + 2*self.lblWidth),(self.height - self.topMargin - 0*self.lblHeight)),
                    (self.leftMargin,(self.height - self.topMargin - 1*self.lblHeight)),((self.leftMargin + self.lblWidth),(self.height - self.topMargin - 1*self.lblHeight)),((self.leftMargin + 2*self.lblWidth),(self.height - self.topMargin - 1*self.lblHeight)),
                    (self.leftMargin,(self.height - self.topMargin - 2*self.lblHeight)),((self.leftMargin + self.lblWidth),(self.height - self.topMargin - 2*self.lblHeight)),((self.leftMargin + 2*self.lblWidth),(self.height - self.topMargin - 2*self.lblHeight)),
                    (self.leftMargin,(self.height - self.topMargin - 3*self.lblHeight)),((self.leftMargin + self.lblWidth),(self.height - self.topMargin - 3*self.lblHeight)),((self.leftMargin + 2*self.lblWidth),(self.height - self.topMargin - 3*self.lblHeight)),
                    (self.leftMargin,(self.height - self.topMargin - 4*self.lblHeight)),((self.leftMargin + self.lblWidth),(self.height - self.topMargin - 4*self.lblHeight)),((self.leftMargin + 2*self.lblWidth),(self.height - self.topMargin - 4*self.lblHeight)),
                    (self.leftMargin,(self.height - self.topMargin - 5*self.lblHeight)),((self.leftMargin + self.lblWidth),(self.height - self.topMargin - 5*self.lblHeight)),((self.leftMargin + 2*self.lblWidth),(self.height - self.topMargin - 5*self.lblHeight)),
                    (self.leftMargin,(self.height - self.topMargin - 6*self.lblHeight)),((self.leftMargin + self.lblWidth),(self.height - self.topMargin - 6*self.lblHeight)),((self.leftMargin + 2*self.lblWidth),(self.height - self.topMargin - 6*self.lblHeight)),
                    (self.leftMargin,(self.height - self.topMargin - 7*self.lblHeight)),((self.leftMargin + self.lblWidth),(self.height - self.topMargin - 7*self.lblHeight)),((self.leftMargin + 2*self.lblWidth),(self.height - self.topMargin - 7*self.lblHeight)),
                    (self.leftMargin,(self.height - self.topMargin - 8*self.lblHeight)),((self.leftMargin + self.lblWidth),(self.height - self.topMargin - 8*self.lblHeight)),((self.leftMargin + 2*self.lblWidth),(self.height - self.topMargin - 8*self.lblHeight)),
                    (self.leftMargin,(self.height - self.topMargin - 9*self.lblHeight)),((self.leftMargin + self.lblWidth),(self.height - self.topMargin - 9*self.lblHeight)),((self.leftMargin + 2*self.lblWidth),(self.height - self.topMargin - 9*self.lblHeight))]

        self.fontFace = 'Helvetica'
        self.fontSize = 9

    def Add(self, inObj):
        self.List.append(inObj)
        
    def Print(self):
        pdfFile = canvas.Canvas(self.outFile, pagesize=letter)
        total_rec_in = 0

        labels_out = 0

        for item in self.List:
            total_rec_in +=1
            if isinstance(item, Patient):
                outStr = item.FirstName + ' '
                if (len(item.MI)> 1): outStr = outStr + item.MI + ' '
                outStr = outStr + item.LastName + '\n'
            else:
                outStr = item.Name + '\n'
            if (len(item.Address1)> 1):
                #print ">> " + item.Address1
                outStr = outStr + item.Address1 + '\n'
            outStr = outStr + item.Street + '\n' + item.City + ', ' + item.State + ' ' + item.Zip
            if (hasattr(item, 'Extra')):
                #print ">> " + item.Address1
                outStr = outStr + '\n' + item.Extra 
            if (labels_out % 30 == 0):
                if (labels_out > 0):pdfFile.showPage()
                pdfFile.setFont(self.fontFace, self.fontSize)
                pdfFile.setStrokeColorRGB(255,255,255)
            textobject = pdfFile.beginText()
            textobject.setTextOrigin(self.labelpos[labels_out % 30][0],self.labelpos[labels_out % 30][1])
            textobject.textLines(outStr)
            pdfFile.drawText(textobject)
            del textobject
            labels_out +=1

        pdfFile.showPage()
        pdfFile.save()

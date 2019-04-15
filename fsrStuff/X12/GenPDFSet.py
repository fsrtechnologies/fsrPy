import os, sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import TableStyle
from tempfile import gettempdir

#---Constants
class GenericPDFSettings(object):
    PAGE_HEIGHT=letter[1]
    PAGE_WIDTH=letter[0]
    marginSize = 0.35 * inch
    lineHeight = inch / 7
    
    leftMargin = marginSize
    bottomMargin = marginSize
    rightMargin = PAGE_WIDTH - marginSize
    topMargin = PAGE_HEIGHT - marginSize + 0.1 * inch
    pad = 0

    fontDict =     {'Anonymous Pro': ('Anonymous_Pro.ttf', 'Anonymous_Pro_B.ttf', 8),
                    'BPMono': ('BPMono.ttf', 'BPMonoBold.ttf', 7.3),
                    'Cousine': ('Cousine-Regular-Latin.ttf', 'Cousine-Bold-Latin.ttf', 7.3),
                    'DejaVu Sans': ('DejaVuSansMono.ttf', 'DejaVuSansMono-Bold.ttf', 7.3),
                    'Lekton': ('Lekton-Regular.ttf', 'Lekton-Bold.ttf', 8.7),
                    'Liberation Mono': ('LiberationMono-Regular.ttf', 'LiberationMono-Bold.ttf', 7.3),
                    'Luxi-Mono': ('luximr.ttf', 'luximb.ttf', 7.3),
                    'Ubuntu Mono': ('UbuntuMono-R.ttf', 'UbuntuMono-B.ttf', 8.7),                
                    'Vera Sans Mono': ('VeraMono.ttf', 'VeraMono-Bold.ttf', 7.3),
                    }
            
    def __init__(self, regFont='Anonymous Pro', pdfDir=gettempdir()):
        self.pdfDir = pdfDir
        for root, dirs, files in os.walk(os.getcwd()):  #to find Fonts directory regardless of how we're invoked
            if 'BPmono.ttf' in files:
                fontDir = root 
        
        self.regFont = regFont
        self.boldFont = regFont + ' Bold'

        self.fontSize = self.fontDict[regFont][2]
        fileNameReg = fontDir + os.sep + self.fontDict[regFont][0]
        fileNameBold = fontDir + os.sep + self.fontDict[regFont][1]
        pdfmetrics.registerFont(TTFont(self.regFont, fileNameReg))
        pdfmetrics.registerFont(TTFont(self.boldFont, fileNameBold))

        tmpCanv = canvas.Canvas('tmp.pdf')
        # cW - because 'charWidth' is too damn long
        self.cW = tmpCanv.stringWidth('W', fontName=regFont, fontSize=self.fontSize)
        del tmpCanv
        #---Table styles and widths
        self.styles = {}
        for tmpStyle in ['codes', 'clmHeader', 'clmLine', 'clmFooter1', 'clmFooter2', 'rptFooter']:
            self.styles[tmpStyle] = TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'),
                                                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                                ('FONT', (0,0), (-1,-1), regFont, self.fontSize),
                                                ("BOTTOMPADDING",(0,0),(-1,-1),self.pad),
                                                ("TOPPADDING", (0,0),(-1,-1),self.pad),
                                                ("RIGHTPADDING", (0,0),(-1,-1),self.pad),
                                                ("LEFTPADDING", (0,0),(-1,-1),self.pad)])
    def addStyles(self):
        pass

    def firstPage(self, canvas, doc):
        pass
    def laterPages(self, canvas, doc):
        pass
   

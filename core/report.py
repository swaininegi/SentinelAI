from fpdf import FPDF
from datetime import datetime
import tempfile
from .risk import recommendations

def make_pdf(title, scan_type, input_text, score, level, explanation):
    pdf=FPDF(); pdf.add_page(); pdf.set_auto_page_break(True,15)
    pdf.set_font('Helvetica','B',20); pdf.cell(0,12,'SentinelAI Security Report',ln=True,align='C')
    pdf.set_font('Helvetica','',11); pdf.cell(0,8,datetime.now().strftime('%d %b %Y, %H:%M:%S'),ln=True,align='C')
    pdf.ln(8); pdf.set_font('Helvetica','B',14); pdf.cell(0,8,title,ln=True)
    pdf.set_font('Helvetica','',12)
    for k,v in [('Scan Type',scan_type),('Risk Score',str(score)+'/100'),('Threat Level',level)]: pdf.cell(0,8,f'{k}: {v}',ln=True)
    pdf.ln(5); pdf.multi_cell(0,7,'Input: '+str(input_text)[:900])
    pdf.ln(3); pdf.multi_cell(0,7,'AI Explanation: '+str(explanation))
    pdf.ln(3); pdf.set_font('Helvetica','B',12); pdf.cell(0,8,'Recommendations',ln=True); pdf.set_font('Helvetica','',12)
    for r in recommendations(score): pdf.multi_cell(0,7,'- '+r)
    path=tempfile.NamedTemporaryFile(delete=False,suffix='.pdf').name; pdf.output(path)
    return path

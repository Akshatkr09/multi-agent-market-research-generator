"""ReportLab PDF compiler for market research reports."""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from xml.sax.saxutils import escape
import re
class NumberedCanvas(canvas.Canvas):
    def __init__(self,*a,**k): super().__init__(*a,**k); self._states=[]
    def showPage(self): self._states.append(dict(self.__dict__)); self._startPage()
    def save(self):
        total=len(self._states)
        for state in self._states:
            self.__dict__.update(state); self.saveState(); self.setFont("Helvetica",8); self.setFillColor(colors.grey); self.drawString(18*mm,10*mm,"Market Research Report"); self.drawRightString(A4[0]-18*mm,10*mm,f"Page {self._pageNumber} of {total}"); self.restoreState(); canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
def compile_market_report(title,report_text,metrics_markdown="",output_path="output/market_report.pdf",query=None):
    if not str(title).strip(): raise ValueError("Report title must not be empty.")
    if not str(report_text).strip() and not str(metrics_markdown).strip(): raise ValueError("Provide report text or a metrics table.")
    path=Path(output_path); path.parent.mkdir(parents=True,exist_ok=True); styles=getSampleStyleSheet(); story=[Paragraph(escape(title),styles["Title"]),Paragraph("Market research analysis",styles["Normal"]),Spacer(1,8*mm)]
    for line in (report_text+"\n"+metrics_markdown).splitlines():
        line=line.strip()
        if not line: continue
        if line.startswith("#"): story.append(Paragraph(escape(line.lstrip("# ")),styles["Heading1"]))
        elif line.startswith("|"):
            cells=[escape(x.strip()) for x in line.strip("|").split("|")]
            if all(set(x)<=set(":- ") for x in cells): continue
            story.append(Paragraph(" | ".join(cells),styles["BodyText"]))
        else: story.append(Paragraph(escape(line),styles["BodyText"]))
        story.append(Spacer(1,3*mm))
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=20*mm,bottomMargin=20*mm,title=title,author="Market Research Generator")
    doc.build(story,canvasmaker=NumberedCanvas); return str(path.resolve())
generate_pdf_report=compile_market_report

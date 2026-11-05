"""Render the editable manuscript to an A4 PDF and report its body word count."""
from pathlib import Path
import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / 'output' / 'pdf'
source = (folder / 'BIOF3001_manuscript_draft.md').read_text(encoding='utf-8')
body = source.split('## 1. Introduction', 1)[1].split('## References', 1)[0]
count = len(re.sub(r'(?m)^#+.*$', '', body).split())
assert 1000 <= count <= 1500, count

styles = {
    'title': ParagraphStyle('Title', fontName='Times-Bold', fontSize=17, leading=21, spaceAfter=12),
    'meta': ParagraphStyle('Meta', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#555555'), spaceAfter=16),
    'h1': ParagraphStyle('Heading', fontName='Times-Bold', fontSize=13, leading=17, spaceBefore=12, spaceAfter=7, keepWithNext=True),
    'h2': ParagraphStyle('Subheading', fontName='Times-Bold', fontSize=11.5, leading=15, spaceBefore=8, spaceAfter=5, keepWithNext=True),
    'body': ParagraphStyle('Body', fontName='Times-Roman', fontSize=11, leading=15, alignment=TA_JUSTIFY, spaceAfter=8, allowWidows=0, allowOrphans=0),
    'equation': ParagraphStyle('Equation', fontName='Times-Italic', fontSize=10.5, leading=14, leftIndent=15, rightIndent=15, spaceBefore=3, spaceAfter=10),
    'ref': ParagraphStyle('Reference', fontName='Times-Roman', fontSize=9.5, leading=12.5, leftIndent=23, firstLineIndent=-23, spaceAfter=8, splitLongWords=True),
}


def markup(text):
    parts = re.split(r'(https?://\S+)', text)
    output = []
    for part in parts:
        if part.startswith('http'):
            label = part.replace('https://doi.org/', 'doi: ')
            if 'openaccess.thecvf.com' in part:
                label = 'CVPR Open Access'
            elif 'utdallas.edu' in part:
                label = 'Author-posted chapter (UT Dallas)'
            output.append(f'<link href="{html.escape(part, quote=True)}" color="#254b70">{html.escape(label)}</link>')
        else:
            output.append(html.escape(part))
    return ''.join(output)


story = []
for block in source.strip().split('\n\n'):
    if block.startswith('# '):
        story.append(Paragraph(markup(block[2:]), styles['title']))
        story.append(Paragraph(f'BIOF3001 | Individual manuscript draft | Introduction and Methods: {count:,} words (references excluded)', styles['meta']))
    elif block == '## References':
        story.append(PageBreak())
        story.append(Paragraph('References', styles['h1']))
    elif block.startswith('## '):
        story.append(Paragraph(markup(block[3:]), styles['h1']))
    elif block.startswith('### '):
        story.append(Paragraph(markup(block[4:]), styles['h2']))
    elif block.startswith('> '):
        story.append(Paragraph(markup(block[2:]), styles['equation']))
    else:
        style = styles['ref'] if re.match(r'^\[\d+\]', block) else styles['body']
        story.append(Paragraph(markup(block), style))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#cccccc'))
    canvas.line(51, 43, A4[0]-51, 43)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(51, 30, 'BIOF3001 | Landmark-based statistical spine reconstruction')
    canvas.drawRightString(A4[0]-51, 30, str(doc.page))
    canvas.restoreState()


target = folder / 'BIOF3001_manuscript_draft.pdf'
doc = SimpleDocTemplate(str(target), pagesize=A4, leftMargin=51, rightMargin=51,
                        topMargin=47, bottomMargin=57,
                        title='Predicting T1-L3 Spine Shape from Fifteen Landmarks',
                        author='', subject='BIOF3001 individual manuscript draft')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f'Body words: {count}; PDF: {target}')

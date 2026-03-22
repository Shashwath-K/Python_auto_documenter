from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.pdf_converter.analyzers.document_model import StructuredDocument
from app.pdf_converter.enums.templates import PDFTemplate

def generate_docx(document: StructuredDocument, template: PDFTemplate, output_path: str):
    doc = Document()
    
    # Title
    if document.title:
        title = doc.add_heading(document.title, 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Simple Style mapping
    font_name = 'Arial'
    if template == PDFTemplate.CLASSIC:
        font_name = 'Times New Roman'
    elif template == PDFTemplate.MINIMAL:
        font_name = 'Courier New'
        
    style = doc.styles['Normal']
    style.font.name = font_name
    style.font.size = Pt(11)
    
    for block in document.blocks:
        if block.type.startswith('h'):
            level = int(block.type[1])
            # Word only supports 1-9
            level = min(level, 9)
            doc.add_heading(block.content, level=level)
            
        elif block.type == 'bullet':
            doc.add_paragraph(block.content, style='List Bullet')
            
        elif block.type == 'code':
            # Split content into lines for basic highlighting
            lines = block.content.split('\n')
            for line in lines:
                if not line.strip() and len(lines) > 1:
                    continue
                p = doc.add_paragraph()
                p.style = 'No Spacing'
                p.paragraph_format.left_indent = Pt(24)
                
                run = p.add_run(line)
                run.font.name = 'Courier New'
                run.font.size = Pt(10)
                
                # Detect comments
                if line.strip().startswith('#') or line.strip().startswith('//') or line.strip().startswith('"""') or line.strip().startswith("'''"):
                    run.font.color.rgb = RGBColor(34, 139, 34) # Forest Green
                else:
                    run.font.color.rgb = RGBColor(50, 50, 50) # Dark Gray for code
            
        elif block.type == 'quote':
            p = doc.add_paragraph(block.content)
            p.style = 'Quote'
            
        else:
            doc.add_paragraph(block.content)
            
    doc.save(output_path)

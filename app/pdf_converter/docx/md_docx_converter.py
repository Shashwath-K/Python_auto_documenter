import logging
import re
import io
import os
import base64
from markdown_it import MarkdownIt
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

from app.pdf_converter.enums.templates import PDFTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MDToDocxConverter:
    def __init__(self, template_choice: PDFTemplate):
        self.md = MarkdownIt("commonmark", {"breaks": True, "html": True}).enable("table")
        self.doc = Document()
        self.template = template_choice
        self._setup_styles()

    def _setup_styles(self):
        # Configure base font
        font_name = 'Arial'
        if self.template == PDFTemplate.CLASSIC:
            font_name = 'Times New Roman'
        elif self.template == PDFTemplate.MINIMAL:
            font_name = 'Courier New'
            
        style = self.doc.styles['Normal']
        style.font.name = font_name
        style.font.size = Pt(11)

    def convert(self, text: str, output_path: str):
        tokens = self.md.parse(text)
        self._process_tokens(tokens)
        self.doc.save(output_path)

    # ------------------------------------------------------------------ #
    #  Output block helpers                                                #
    # ------------------------------------------------------------------ #

    # Removed _preprocess_output_blocks as it breaks ordering. 
    # Logic moved to _process_tokens.

    def _emit_output_block_docx(self, content: str):
        """Renders an output block into the DOCX document."""
        # Italic, grey label paragraph
        label_para = self.doc.add_paragraph()
        label_run = label_para.add_run('Output Block')
        label_run.italic = True
        label_run.font.color.rgb = RGBColor(150, 150, 150)
        label_run.font.size = Pt(9)
        
        # Create a single cell table to serve as a bordered box
        table = self.doc.add_table(rows=1, cols=1)
        table.style = 'Table Grid'
        cell = table.cell(0, 0)
        
        # Ensure the cell is clean for our content
        if len(cell.paragraphs) > 0:
            cell.paragraphs[0].text = ''

        lines = content.split('\n')
        text_lines = []
        for line in lines:
            img_match = re.match(
                r'!\[.*?\]\(data:image/(png|jpeg);base64,(.+?)\)$', line.strip()
            )
            if img_match:
                # Flush accumulated text
                if text_lines:
                    self._add_output_text_docx('\n'.join(text_lines), cell=cell)
                    text_lines = []
                # Embed image
                b64_data = img_match.group(2).strip()
                try:
                    img_bytes = base64.b64decode(b64_data)
                    img_io = io.BytesIO(img_bytes)
                    
                    # Add paragraph into the cell for image
                    img_p = cell.add_paragraph()
                    img_p.add_run().add_picture(img_io, width=Inches(5.0))
                except Exception as e:
                    logger.warning(f"Could not embed DOCX output image: {e}")
                    cell.add_paragraph('[Image could not be rendered]')
            else:
                text_lines.append(line)

        if text_lines:
            self._add_output_text_docx('\n'.join(text_lines), cell=cell)

    def _add_output_text_docx(self, text: str, cell=None):
        """Adds a shaded code-style paragraph for output text."""
        if not text.strip():
            return
            
        if cell is not None:
            # If the initial paragraph in the cell is completely empty, reuse it
            if len(cell.paragraphs) == 1 and cell.paragraphs[0].text == '':
                p = cell.paragraphs[0]
                p.text = text.strip()
            else:
                p = cell.add_paragraph(text.strip())
        else:
            p = self.doc.add_paragraph(text.strip())
            
        p.style = 'No Spacing'
        p.paragraph_format.left_indent = Pt(18)
        for run in p.runs:
            run.font.name = 'Courier New'
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(80, 80, 80)

    def _process_tokens(self, tokens):
        i = 0
        while i < len(tokens):
            token = tokens[i]
            type_ = token.type
            
            if type_ == 'heading_open':
                level = int(token.tag[1])
                content = tokens[i+1].content
                # Word headings are 1-9.
                self.doc.add_heading(content, level=min(level, 9))
                i += 3
                continue
                
            elif type_ == 'paragraph_open':
                if tokens[i+1].type == 'inline':
                    # We need to handle inline formatting (bold/italic)
                    self._add_formatted_paragraph(tokens[i+1])
                i += 3
                continue
            
            elif type_ == 'bullet_list_open':
                consumed = self._handle_list(tokens, i, ordered=False)
                i += consumed
                continue
                
            elif type_ == 'ordered_list_open':
                consumed = self._handle_list(tokens, i, ordered=True)
                i += consumed
                continue

            elif type_ == 'table_open':
                consumed = self._handle_table(tokens, i)
                i += consumed
                continue

            elif type_ == 'html_block':
                content = token.content.strip()
                if '<!-- output_block_start' in content:
                    match = re.search(r'<!-- output_block_start\n?(.*?)\n?output_block_end -->', token.content, re.DOTALL)
                    if match:
                        self._emit_output_block_docx(match.group(1).strip())
                i += 1
                continue
                
            elif type_ == 'fence' or type_ == 'code_block':
                # Split content into lines for basic highlighting
                lines = token.content.split('\n')
                for line in lines:
                    if not line.strip():
                        continue
                    p = self.doc.add_paragraph()
                    p.style = 'No Spacing'
                    p.paragraph_format.left_indent = Pt(24)
                    
                    run = p.add_run(line)
                    run.font.name = 'Courier New'
                    run.font.size = Pt(10)
                    
                    # Detect comments (simple heuristic)
                    if line.strip().startswith('#') or line.strip().startswith('//') or line.strip().startswith('"""') or line.strip().startswith("'''"):
                        run.font.color.rgb = RGBColor(34, 139, 34) # Forest Green
                    else:
                        run.font.color.rgb = RGBColor(50, 50, 50) # Dark Gray for code
                i += 1
                continue
                
            i += 1

    def _add_formatted_paragraph(self, inline_token, style=None):
        if style:
            p = self.doc.add_paragraph(style=style)
        else:
            p = self.doc.add_paragraph()
            
        self._render_inline_to_paragraph(p, inline_token)

    def _render_inline_to_paragraph(self, paragraph, inline_token):
        if not inline_token.children:
            paragraph.add_run(inline_token.content)
            return

        # Simple state machine for bold/italic/code
        is_bold = False
        is_italic = False
        is_code = False
        
        for child in inline_token.children:
            if child.type == 'text':
                run = paragraph.add_run(child.content)
                run.bold = is_bold
                run.italic = is_italic
                if is_code:
                    run.font.name = 'Courier New'
                    run.font.color.rgb = RGBColor(200, 50, 50)
            
            elif child.type == 'softbreak':
                paragraph.add_run(" ")
            elif child.type == 'strong_open':
                is_bold = True
            elif child.type == 'strong_close':
                is_bold = False
            elif child.type == 'em_open':
                is_italic = True
            elif child.type == 'em_close':
                is_italic = False
            elif child.type == 'code_inline':
                run = paragraph.add_run(child.content)
                run.font.name = 'Courier New'
                # Highlight or distinct color
                run.font.color.rgb = RGBColor(100, 100, 100)
            elif child.type == 'image':
                src = child.attrs.get('src', '') if child.attrs else ''
                self._try_embed_image_inline_docx(src, child.content)

    def _try_embed_image_inline_docx(self, src: str, alt_text: str):
        """Embeds an image (data URI or file path) into the DOCX document."""
        try:
            if src.startswith('data:image/'):
                _, b64_data = src.split(',', 1)
                img_bytes = base64.b64decode(b64_data.strip())
                img_io = io.BytesIO(img_bytes)
                self.doc.add_picture(img_io, width=Inches(5.5))
            elif src and os.path.isfile(src):
                self.doc.add_picture(src, width=Inches(5.5))
            else:
                self.doc.add_paragraph(f'[Image: {alt_text}]')
        except Exception as e:
            logger.warning(f"Could not embed inline image: {e}")
            self.doc.add_paragraph(f'[Image: {alt_text}]')

    def _handle_list(self, tokens, start_index, ordered=False):
        # python-docx list support is tricky for nesting.
        # We rely on 'List Bullet' and 'List Number' styles.
        close_type = 'ordered_list_close' if ordered else 'bullet_list_close'
        style_name = 'List Number' if ordered else 'List Bullet'
        
        i = start_index + 1
        while i < len(tokens):
            token = tokens[i]
            if token.type == close_type:
                break
            
            if token.type == 'list_item_open':
                # Content inside
                j = i + 1
                while j < len(tokens) and tokens[j].type != 'list_item_close':
                    if tokens[j].type == 'inline':
                        # Add paragraph with list style
                        self._add_formatted_paragraph(tokens[j], style=style_name)
                    # Recurse for nested lists? 
                    # python-docx doesn't handle indentation level automatically with just style name usually
                    # but simple flat lists work.
                    if tokens[j].type in ['bullet_list_open', 'ordered_list_open']:
                         # Recurse
                         consumed = self._handle_list(tokens, j, ordered=('ordered' in tokens[j].type))
                         j += consumed - 1 # Adjust because loop increments
                    j += 1
                i = j
            i += 1
        return (i - start_index) + 1

    def _handle_table(self, tokens, start_index):
        # Gather data
        rows_data = []
        current_row = []
        i = start_index + 1
        
        while i < len(tokens):
            if tokens[i].type == 'table_close':
                break
            if tokens[i].type == 'tr_close':
                rows_data.append(current_row)
                current_row = []
            if tokens[i].type == 'inline' and tokens[i-1].type in ['th_open', 'td_open']:
                current_row.append(tokens[i].content) # Simplified text content for cells
            elif tokens[i].type in ['th_open', 'td_open'] and tokens[i+1].type != 'inline':
                # Empty cell
                current_row.append("")
            i += 1
            
        if rows_data:
            table = self.doc.add_table(rows=len(rows_data), cols=len(rows_data[0]))
            table.style = 'Table Grid'
            for r_idx, row_content in enumerate(rows_data):
                row_cells = table.rows[r_idx].cells
                for c_idx, text in enumerate(row_content):
                    row_cells[c_idx].text = text
                    
        return (i - start_index) + 1

def convert_md_to_docx(text: str, output_path: str, template: PDFTemplate):
    converter = MDToDocxConverter(template)
    converter.convert(text, output_path)

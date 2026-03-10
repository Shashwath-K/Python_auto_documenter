import os
import tempfile
import gradio as gr

from app.pdf_converter.validators.file_validator import validate_file
from app.pdf_converter.parsers.txt_parser import parse_txt
from app.pdf_converter.parsers.md_parser import parse_md
from app.pdf_converter.parsers.docx_parser import parse_docx
from app.pdf_converter.parsers.bin_parser import parse_bin
from app.pdf_converter.parsers.csv_parser import parse_csv
from app.pdf_converter.parsers.html_parser import parse_html
from app.pdf_converter.parsers.ipynb_parser import parse_ipynb

from app.pdf_converter.analyzers.content_analyzer import normalize_content
from app.pdf_converter.analyzers.markdown_analyzer import analyze_markdown
from app.pdf_converter.analyzers.plaintext_analyzer import analyze_plaintext
from app.pdf_converter.analyzers.structure_scanner import scan_structure, bulletize_text

from app.pdf_converter.pdf.md_complete_conversion import convert_md_complete
from app.pdf_converter.pdf.pdf_generator import generate_pdf
from app.pdf_converter.docx.docx_generator import generate_docx
from app.pdf_converter.docx.md_docx_converter import convert_md_to_docx

from app.pdf_converter.enums.templates import PDFTemplate
from app.pdf_converter.enums.file_types import SupportedFileType
from app.pdf_converter.exceptions.custom_exceptions import FileValidationError, ParsingError

def convert_file(file, template_choice, use_filename_as_heading, output_format="PDF", auto_structure=False, bulletize=False):
    try:
        file_type = validate_file(file)

        # --- MARKDOWN / IPYNB HANDLING ---
        if file_type == SupportedFileType.MD or file_type == SupportedFileType.IPYNB:
            if file_type == SupportedFileType.IPYNB:
                 text_content = parse_ipynb(file)
            else:
                 text_content = parse_md(file)
            
            # Apply heading ONLY if requested
            if use_filename_as_heading and not text_content.lstrip().startswith("#"):
                filename = os.path.basename(file.name)
                title = os.path.splitext(filename)[0].replace("_", " ").title()
                text_content = f"# {title}\n\n{text_content}"

            # Prepare Output Filename
            original_name = os.path.splitext(os.path.basename(file.name))[0]
            temp_dir = tempfile.mkdtemp()
            
            if output_format == "DOCX":
                output_path = os.path.join(temp_dir, f"{original_name}.docx")
                convert_md_to_docx(text_content, output_path, PDFTemplate(template_choice))
                return output_path
            else:
                output_path = os.path.join(temp_dir, f"{original_name}.pdf")
                convert_md_complete(text_content, output_path, PDFTemplate(template_choice))
                return output_path

        # --- OTHER FORMATS ---
        if file_type == SupportedFileType.TXT:
            content = parse_txt(file)
            
            if bulletize:
                 document = bulletize_text(content, file.name)
            elif auto_structure:
                 document = scan_structure(content, file.name)
            else:
                 document = analyze_plaintext(content, file.name)
                 
        elif file_type == SupportedFileType.DOCX:
            content = parse_docx(file)
            document = analyze_plaintext(content, file.name)
        elif file_type == SupportedFileType.CSV:
            content = parse_csv(file)
            document = analyze_plaintext(content, file.name)
        elif file_type == SupportedFileType.HTML:
            content = parse_html(file)
            document = analyze_plaintext(content, file.name)
        else:
            content = parse_bin(file)
            document = analyze_plaintext(content, file.name)
        
        # Remove title from StructuredDocument if toggle is OFF
        if not use_filename_as_heading:
            document.title = ""
        
        # Prepare Output Filename for other formats
        original_name = os.path.splitext(os.path.basename(file.name))[0]
        temp_dir = tempfile.mkdtemp()

        if output_format == "DOCX":
             output_path = os.path.join(temp_dir, f"{original_name}.docx")
             generate_docx(document, PDFTemplate(template_choice), output_path)
             return output_path
        else:
            output_path = os.path.join(temp_dir, f"{original_name}.pdf")
            generate_pdf(
                document=document,
                template=PDFTemplate(template_choice),
                output_path=output_path
            )
            return output_path

    except (FileValidationError, ParsingError) as e:
        raise gr.Error(str(e))

def update_txt_visibility(file):
    if file is None:
        return gr.update(visible=False), gr.update(visible=False)
    
    filename = file.name if hasattr(file, 'name') else ""
    if filename.lower().endswith('.txt'):
        return gr.update(visible=True), gr.update(visible=True)
    
    return gr.update(visible=False), gr.update(visible=False)

def create_demo():
    # Modernizing with custom CSS for centering and card-layouts
    custom_css = """
        .container { max-width: 1000px; margin: auto; padding-top: 2rem; }
        .header-text { text-align: center; margin-bottom: 2rem; }
        .footer-text { text-align: center; margin-top: 3rem; padding: 2rem; opacity: 0.7; }
        .gr-button-primary { background: #2563eb !important; }
    """

    theme = gr.themes.Soft(
        primary_hue="blue",
        neutral_hue="slate",
        spacing_size="md",
        radius_size="lg",
    )

    with gr.Blocks(theme=theme, css=custom_css, title="Semantic File Converter") as app:
        with gr.Column(elem_classes="container"):
            # --- Header ---
            gr.Markdown(
                """
                <div class="header-text">
                    <h1>Semantic File Converter</h1>
                    <p>Professional document conversion with structural intelligence.</p>
                    <small>Supports Markdown, Jupyter, Word, Text, HTML, and CSV</small>
                </div>
                """
            )

            # --- Main Interface ---
            with gr.Row(variant="panel"):
                # Left: Upload
                with gr.Column(scale=1, min_width=320):
                    file_input = gr.File(
                        label="Upload Document", 
                        file_count="single", 
                        height=250
                    )
                
                # Right: Configuration
                with gr.Column(scale=1, min_width=320):
                    gr.Markdown("### Configuration")
                    
                    with gr.Group():
                        template_dropdown = gr.Dropdown(
                            choices=[t.value for t in PDFTemplate],
                            label="Document Template",
                            value=PDFTemplate.CLASSIC.value,
                            interactive=True
                        )
                        output_format = gr.Radio(
                            choices=["PDF", "DOCX"],
                            label="Output Format",
                            value="PDF",
                            interactive=True
                        )

                    with gr.Accordion("Advanced Settings", open=False):
                        use_heading = gr.Checkbox(
                            label="Use Filename as Document Title",
                            value=True,
                            info="Automatically generates a header from the source filename."
                        )
                        
                        auto_structure = gr.Checkbox(
                            label="Automatic Structure Detection", 
                            value=False, 
                            visible=False,
                            info="Applies to TXT files: Detects headings and lists."
                        )
                        bulletize = gr.Checkbox(
                            label="Convert Paragraphs to Bullets", 
                            value=False, 
                            visible=False,
                            info="Applies to TXT files: Formats all text as a list."
                        )

            # --- Action & Output ---
            with gr.Row():
                with gr.Column():
                    convert_btn = gr.Button("Process and Convert", variant="primary", size="lg")
                    output_file = gr.File(label="Download Processed Document", interactive=False)

            # --- Footer ---
            gr.Markdown(
                """
                <div class="footer-text">
                    <hr>
                    <p>Powered by Gradio, ReportLab, and Python</p>
                    <p><a href="https://github.com/Shashwath-K/Python_based_smart_pdf_converter" target="_blank">View Source on GitHub</a></p>
                </div>
                """,
                elem_classes="footer-text"
            )

        # --- Event Listeners ---
        file_input.change(
            fn=update_txt_visibility,
            inputs=file_input,
            outputs=[auto_structure, bulletize]
        )

        convert_btn.click(
            fn=convert_file,
            inputs=[
                file_input, 
                template_dropdown, 
                use_heading, 
                output_format, 
                auto_structure, 
                bulletize
            ],
            outputs=output_file
        )

    return app
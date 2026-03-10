from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Preformatted,
    Table,
    TableStyle
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import lightgrey
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from app.pdf_converter.templates.pdf_templates import PDF_TEMPLATES
from app.pdf_converter.enums.templates import PDFTemplate
from app.pdf_converter.analyzers.document_model import StructuredDocument


# -------------------------------------------------
# Page Border Utility
# -------------------------------------------------
def draw_page_border(c: canvas.Canvas, doc, border_width: int = 1):
    width, height = A4
    margin = doc.leftMargin

    c.setLineWidth(border_width)
    c.rect(
        margin - 10,
        margin - 10,
        width - 2 * (margin - 10),
        height - 2 * (margin - 10)
    )


# -------------------------------------------------
# PDF Generator
# -------------------------------------------------
def generate_pdf(
    document: StructuredDocument,
    template: PDFTemplate,
    output_path: str
):
    cfg = PDF_TEMPLATES[template]

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=cfg["page"]["margin"],
        rightMargin=cfg["page"]["margin"],
        topMargin=cfg["page"]["margin"],
        bottomMargin=cfg["page"]["margin"]
    )

    story = []

    # -------------------------------------------------
    # Title
    # -------------------------------------------------
    if document.title:
        title_style = ParagraphStyle(
            name="Title",
            fontName=cfg["title_style"]["font"],
            fontSize=cfg["title_style"]["size"],
            alignment=TA_CENTER,
            spaceAfter=cfg["title_style"]["space_after"]
        )
        story.append(Paragraph(document.title, title_style))

    # -------------------------------------------------
    # Base Body Style
    # -------------------------------------------------
    body_cfg = cfg["body_style"]

    body_style = ParagraphStyle(
        name="Body",
        fontName=body_cfg["font"],
        fontSize=body_cfg["size"],
        leading=body_cfg["leading"],
        alignment=TA_JUSTIFY,
        spaceBefore=6,
        spaceAfter=14  # Increased from 10
    )

    # -------------------------------------------------
    # Heading Styles
    # -------------------------------------------------
    h_styles = {
        "h1": ParagraphStyle(
            "H1", fontSize=16, spaceBefore=18, spaceAfter=14
        ),
        "h2": ParagraphStyle(
            "H2", fontSize=14, spaceBefore=16, spaceAfter=12
        ),
        "h3": ParagraphStyle(
            "H3", fontSize=12, spaceBefore=14, spaceAfter=10
        ),
    }

    # -------------------------------------------------
    # Bullet Style (Indented / Hanging)
    # -------------------------------------------------
    bullet_style = ParagraphStyle(
        name="Bullet",
        fontName=body_cfg["font"],
        fontSize=body_cfg["size"],
        leading=body_cfg["leading"],
        leftIndent=24,
        bulletIndent=12,
        spaceBefore=4,
        spaceAfter=10  # Increased from 6
    )

    # -------------------------------------------------
    # Document Blocks Rendering
    # -------------------------------------------------
    for block in document.blocks:

        if block.type in h_styles:
            story.append(Paragraph(block.content, h_styles[block.type]))

        elif block.type == "paragraph":
            story.append(Paragraph(block.content, body_style))

        elif block.type == "bullet":
            story.append(
                Paragraph(
                    block.content,
                    bullet_style,
                    bulletText="•"
                )
            )

        elif block.type == "quote":
            quote_para = Paragraph(
                block.content,
                ParagraphStyle(
                    name="QuoteText",
                    fontName=body_cfg["font"],
                    fontSize=body_cfg["size"],
                    leading=body_cfg["leading"],
                    italic=True,
                    textColor=colors.darkgrey
                )
            )

            quote_table = Table(
                [[quote_para]],
                colWidths=[doc.width - 40]
            )

            quote_table.setStyle(
                TableStyle([
                    ("BOX", (0, 0), (-1, -1), 1, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ])
            )

            story.append(Spacer(1, 10))
            story.append(quote_table)
            story.append(Spacer(1, 14))

        elif block.type == "code":
            story.append(
                Preformatted(
                    block.content,
                    style=ParagraphStyle(
                        name="Code",
                        fontName="Courier",
                        fontSize=9,
                        leading=12,
                        backColor=lightgrey,
                        leftIndent=12,
                        rightIndent=12,
                        spaceBefore=12,
                        spaceAfter=12
                    )
                )
            )

    # -------------------------------------------------
    # Page Decoration Hook
    # -------------------------------------------------
    def on_page(c, d):
        if cfg["page"].get("border"):
            draw_page_border(
                c,
                d,
                cfg["page"].get("border_width", 1)
            )

    doc.build(
        story,
        onFirstPage=on_page,
        onLaterPages=on_page
    )

from app.pdf_converter.enums.templates import PDFTemplate

PDF_TEMPLATES = {
    PDFTemplate.CLASSIC: {
        "title_style": {
            "font": "Times-Bold",
            "size": 18,
            "alignment": "CENTER",
            "space_after": 20
        },
        "body_style": {
            "font": "Times-Roman",
            "size": 11,
            "leading": 13,
            "alignment": "JUSTIFY",
            "space_after": 12
        },
        "page": {
            "margin": 60,
            "border": True,
            "border_width": 1
        }
    },

    PDFTemplate.MODERN: {
        "title_style": {
            "font": "Helvetica-Bold",
            "size": 20,
            "alignment": "CENTER",
            "space_after": 24
        },
        "body_style": {
            "font": "Helvetica",
            "size": 12,
            "leading": 14,
            "alignment": "JUSTIFY",
            "space_after": 14
        },
        "page": {
            "margin": 50,
            "border": True,
            "border_width": 1.5
        }
    },

    PDFTemplate.MINIMAL: {
        "title_style": {
            "font": "Courier-Bold",
            "size": 16,
            "alignment": "LEFT",
            "space_after": 16
        },
        "body_style": {
            "font": "Courier",
            "size": 10,
            "leading": 12,
            "alignment": "LEFT",
            "space_after": 10
        },
        "page": {
            "margin": 40,
            "border": False
        }
    }
}

import re
import os
from app.pdf_converter.analyzers.document_model import StructuredDocument, DocBlock

def scan_structure(content: str, file_path: str) -> StructuredDocument:
    filename = os.path.basename(file_path)
    title = os.path.splitext(filename)[0].replace("_", " ").title()
    blocks = []
    
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        
        if not stripped:
            i += 1
            continue
            
        # Feature 1: Heuristic Heading Detection
        # Condition A: All Caps, Short, not a list item
        is_all_caps = stripped.isupper() and len(stripped) < 60 and not stripped.startswith(("-", "*", "1."))
        # Condition B: Ends with a colon and is short (e.g. "Introduction:")
        is_label = stripped.endswith(":") and len(stripped) < 40
        # Condition C: Underlined with --- or === (Markdown style)
        is_underlined = False
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            if next_line and (set(next_line) <= set("-") or set(next_line) <= set("=")) and len(next_line) >= 3:
                is_underlined = True

        if is_all_caps or is_label or is_underlined:
            blocks.append(DocBlock("h2", stripped)) # Default to H2 for detected headings
            if is_underlined:
                i += 1 # Skip the underline
            i += 1
            continue
            
        # Feature 2: List Detection
        # Detects lines starting with -, *, or 1.
        if re.match(r"^(\s*[-*]|\s*\d+\.)\s+", line):
            # Clean the marker slightly? Or keep as is? 
            # PDF generator handles 'bullet' type, but expects content without marker for bullet points usually?
            # Actually our existing md parser strips markers. Let's strip standard bullets.
            if line.lstrip().startswith(("- ", "* ")):
                content = line.lstrip()[2:].strip()
                blocks.append(DocBlock("bullet", content))
            else:
                # Numbered list or other - treat as paragraph or let it be?
                # For now, let's treat numbered lists as paragraphs unless we add a 'ordered_list' block type.
                # PDF generator currently supports 'bullet' (unordered).
                # Let's keep numbered list as paragraph to preserve the number.
                blocks.append(DocBlock("paragraph", stripped))
            i += 1
            continue
            
        # Default: Paragraph
        blocks.append(DocBlock("paragraph", stripped))
        i += 1
        
    return StructuredDocument(title=title, blocks=blocks)

def bulletize_text(content: str, file_path: str) -> StructuredDocument:
    """
    Converts every non-empty paragraph into a bullet point.
    """
    filename = os.path.basename(file_path)
    title = os.path.splitext(filename)[0].replace("_", " ").title()
    blocks = []
    
    # Split by double newlines to find "paragraphs" or just lines?
    # User said "scan the entire txt file", usually implies paragraphs.
    # But usually txt files might be single-line paragraphs.
    # Let's treat every non-empty line as a bullet for "Bulletize" mode.
    
    for line in content.splitlines():
        if line.strip():
            blocks.append(DocBlock("bullet", line.strip()))
            
    return StructuredDocument(title=title, blocks=blocks)

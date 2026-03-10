import os
import re
from app.pdf_converter.analyzers.document_model import StructuredDocument, DocBlock


def convert_inline_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


def analyze_markdown(content: str, file_path: str) -> StructuredDocument:
    lines = content.splitlines()
    blocks = []

    title = None
    in_code_block = False
    code_buffer = []
    structure_buffer = []

    for line in lines:
        stripped = line.rstrip()

        # ---------- FENCED CODE BLOCK ----------
        if stripped.strip().startswith("```"):
            if in_code_block:
                blocks.append(DocBlock("code", "\n".join(code_buffer)))
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        # ---------- BULLETS ----------
        if stripped.lstrip().startswith(("- ", "* ", "+ ")):
            marker = stripped.lstrip().split(" ")[0]  # Get the marker
            content_start = stripped.find(marker) + len(marker) + 1
            blocks.append(
                DocBlock("bullet", convert_inline_markdown(stripped[content_start:]))
            )
            continue

        # ---------- PROJECT TREE / STRUCTURE ----------
        if re.match(r"^[\s│├└─]+", line) and not stripped.strip().startswith(("#", ">")):
            # Only treat as structure if it contains tree characters OR looks like a tree
            # And isn't a bullet (already handled) or heading/quote
            # But the regex matches leading spaces. We need to be careful.
            # If it's just spaces, it might be a paragraph indent.
            # Only treat as structure if it has tree chars.
            if any(char in line for char in "│├└─"):
                structure_buffer.append(line)
                continue
            # If it's just spaces and passed bullet check, it's likely a paragraph
            pass

        # ---------- BLOCKQUOTE ----------
        if stripped.startswith(">"):
            blocks.append(
                DocBlock("quote", convert_inline_markdown(stripped[1:].strip()))
            )
            continue

        # ---------- PARAGRAPH ----------
        if stripped:
            blocks.append(
                DocBlock("paragraph", convert_inline_markdown(stripped))
            )

    if structure_buffer:
        blocks.append(DocBlock("code", "\n".join(structure_buffer)))

    if not title:
        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0].replace("_", " ").title()

    return StructuredDocument(title=title, blocks=blocks)

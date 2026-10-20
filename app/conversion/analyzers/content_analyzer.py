import re
import os

def has_heading(content: str) -> bool:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return False

    first_line = lines[0]

    if first_line.startswith("#"):
        return True

    if re.match(r"^[A-Z\s]{5,}$", first_line):
        return True

    return False


def normalize_content(content: str, file_path: str, include_filename_heading: bool = True) -> str:
    if has_heading(content):
        return content

    if not include_filename_heading:
        return content

    # Extract clean filename only
    filename = os.path.basename(file_path)
    title = os.path.splitext(filename)[0]
    title = title.replace("_", " ").replace("-", " ").title()

    return f"{title}\n\n{content}"

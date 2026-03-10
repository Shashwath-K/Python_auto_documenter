import csv
from app.pdf_converter.exceptions.custom_exceptions import ParsingError

def parse_csv(file):
    """
    Parses a CSV file and converts it to a text-based format.
    """
    try:
        content = []
        # file.name is the path to the temp file created by Gradio
        with open(file.name, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                # Join columns with a comma and space for readability
                content.append(", ".join(row))
        
        return "\n".join(content)
    except Exception as e:
        raise ParsingError(f"Failed to parse CSV: {str(e)}")

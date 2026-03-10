from bs4 import BeautifulSoup
from app.pdf_converter.exceptions.custom_exceptions import ParsingError

def parse_html(file):
    """
    Parses an HTML file and extracts the text content.
    """
    try:
        with open(file.name, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            # get_text(separator='\n') ensures that text blocks are separated by newlines
            return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        raise ParsingError(f"Failed to parse HTML: {str(e)}")

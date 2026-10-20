from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatter import Formatter
from pygments.token import Token

class ReportLabFormatter(Formatter):
    """
    Format tokens as ReportLab XML tags for use in XPreformatted or Paragraph.
    Supported tags: <font color="...">, <b>, <i>.
    """
    def __init__(self, **options):
        Formatter.__init__(self, **options)
        
        # Simple style mapping (default)
        self.colors = {
            Token.Keyword: "#B8680E",      # Orange 
            Token.Name.Builtin: "#000080",
            Token.Literal.String: "#008000", # Green
            Token.Comment: "#404040",     # Dark Gray 
            Token.Operator: "#000000",
            Token.Name.Function: "#0000FF", # Blue
            Token.Name.Class: "#0000FF",
            Token.Number: "#000000",
            Token.Text: "#000000"
        }

    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            # Escape XML entities
            value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            # Preserve Indentation while allowing wrap
            # Replace tabs with 4 nbsp
            value = value.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
            # Replace double spaces with nbsp+space to preserve width but allow break
            value = value.replace("  ", "&nbsp; ")
            
            # Find best matching color
            color = self.colors.get(ttype)
            if not color:
                # Fallback to parent type
                color = self.colors.get(ttype.parent)
            
            if color:
                # Special handling for bold/italic if needed (Pygments tokens allow check)
                is_bold = ttype in Token.Keyword
                
                # Wrap
                if is_bold:
                    value = f"<b>{value}</b>"
                    
                outfile.write(f'<font color="{color}">{value}</font>')
            else:
                outfile.write(value)

def highlight_code(code: str, language: str = None) -> str:
    try:
        if language:
            lexer = get_lexer_by_name(language, stripall=True)
        else:
            lexer = guess_lexer(code)
    except:
        lexer = get_lexer_by_name("text", stripall=True)

    formatter = ReportLabFormatter()
    return highlight(code, lexer, formatter)

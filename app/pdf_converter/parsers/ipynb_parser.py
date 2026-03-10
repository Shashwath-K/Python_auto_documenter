import json
import os
import base64

def parse_ipynb(file) -> str:
    """
    Parses an .ipynb file and converts it into a Markdown string representation.
    Includes markdown cells, code cells, output text, and embedded images.
    """
    try:
        # Read file content
        if hasattr(file, 'read'):
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
        else:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()

        nb = json.loads(content)
        
        md_output = []
        
        # Extract Cells
        cells = nb.get('cells', [])
        for cell in cells:
            cell_type = cell.get('cell_type')
            source = "".join(cell.get('source', []))
            
            if cell_type == 'markdown':
                if source.strip():
                    md_output.append(source)
                    md_output.append("\n")
                
            elif cell_type == 'code':
                if source.strip():
                    # Wrap input code in python code fence
                    md_output.append(f"```python\n{source}\n```")
                    md_output.append("\n")
                
                # --- Process Outputs ---
                outputs = cell.get('outputs', [])
                if outputs:
                    output_parts = []
                    for output in outputs:
                        output_type = output.get('output_type', '')
                        
                        # Stream output (print statements)
                        if output_type == 'stream':
                            text = "".join(output.get('text', []))
                            if text.strip():
                                output_parts.append(text.strip())
                        
                        # Display data or execute result
                        elif output_type in ('display_data', 'execute_result'):
                            data = output.get('data', {})
                            
                            # Prefer image output
                            if 'image/png' in data:
                                img_b64 = data['image/png']
                                if isinstance(img_b64, list):
                                    img_b64 = "".join(img_b64)
                                # Store as a data URI for downstream embedding
                                output_parts.append(f"![Output Image](data:image/png;base64,{img_b64.strip()})")
                            elif 'image/jpeg' in data:
                                img_b64 = data['image/jpeg']
                                if isinstance(img_b64, list):
                                    img_b64 = "".join(img_b64)
                                output_parts.append(f"![Output Image](data:image/jpeg;base64,{img_b64.strip()})")
                            elif 'image/svg+xml' in data:
                                # SVG is text-based; skip embedding for now, show note
                                output_parts.append("*(SVG image output — not rendered in PDF)*")
                            elif 'text/plain' in data:
                                text = "".join(data['text/plain'])
                                if text.strip():
                                    output_parts.append(text.strip())
                        
                        # Error output
                        elif output_type == 'error':
                            ename = output.get('ename', 'Error')
                            evalue = output.get('evalue', '')
                            output_parts.append(f"{ename}: {evalue}")
                    
                    if output_parts:
                        # Combine all output parts into the output block
                        combined = "\n\n".join(output_parts)
                        # Wrap in a special marker that downstream converters recognise
                        md_output.append(f"<!-- output_block_start\n{combined}\noutput_block_end -->")
                        md_output.append("\n")
                        
        return "\n".join(md_output)

    except Exception as e:
        raise ValueError(f"Failed to parse IPYNB: {str(e)}")

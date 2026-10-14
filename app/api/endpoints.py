from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.llm_service import generate_docstring, explain_code, generate_ai_summary
from app.services.rpa_service import type_docstring
from app.services.parser_service import extract_functions_and_classes
from app.services.sidebar_service import extract_concepts, analyze_similarity
from app.services.text_preprocessing import preprocessor
from datetime import datetime
import subprocess
import tempfile
import os

router = APIRouter()

# In-memory history for the dashboard view
history: List[Dict] = []

class GenerationRequest(BaseModel):
    code_snippet: str

class GenerationResponse(BaseModel):
    status: str
    message: str
    docstring: str = ""

@router.post("/generate-doc", response_model=GenerationResponse)
async def api_generate_doc(req: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Receives code snippet, creates docstring using LLM, and triggers RPA typing in the background.
    """
    try:
        # Generate docstring
        docstring = await generate_docstring(req.code_snippet)
        
        # Record history
        history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "code": (req.code_snippet[:150] + "...") if len(req.code_snippet) > 150 else req.code_snippet,
            "docstring": (docstring[:150] + "...") if len(docstring) > 150 else docstring
        })
        
        # We process typing in the background so the endpoint returns immediately
        background_tasks.add_task(type_docstring, docstring)
        
        return GenerationResponse(status="success", message="Ghost-typing initiated", docstring=docstring)
    except Exception as e:
        return GenerationResponse(status="error", message=str(e))

class ExtractRequest(BaseModel):
    code: str
    language: str = "python"
    doc_level: str = "maximum"

@router.post("/extract-symbols")
async def api_extract_symbols(req: ExtractRequest):
    """
    Parses code and returns items needing documentation.
    For Python, uses AST to find specific functions/classes.
    For other languages (C++, JS, IPYNB), treating the entire block as one item
    to let the LLM handle the commenting directly.
    """
    if req.language.lower() == "python":
        items = extract_functions_and_classes(req.code, req.doc_level)
    elif req.language.lower() == "ipynb":
        import json
        items = []
        try:
            notebook = json.loads(req.code)
            for i, cell in enumerate(notebook.get("cells", [])):
                if cell.get("cell_type") == "code":
                    # Convert source array/string to string
                    source = cell.get("source", "")
                    if isinstance(source, list):
                        source = "".join(source)
                    
                    if source.strip():
                        items.append({
                            "name": f"Notebook Cell {i}",
                            "type": "CodeCell",
                            "start_line": 1,
                            "insert_line": 1,
                            "indentation": "",
                            "snippet": source,
                            "is_inline": False,
                            "full_replace": True,
                            "is_ipynb_cell": True,
                            "is_markdown_cell": False,
                            "cell_index": i
                        })
        except Exception as e:
            print(f"Failed to parse ipynb JSON: {e}")
            items = []
    else:
        # For non-python scripts, we pass the entire code block to the LLM
        items = [{
            "name": f"{req.language.upper()} File",
            "type": "RawBlock",
            "start_line": 1,
            "insert_line": 1,
            "indentation": "",
            "snippet": req.code,
            "is_inline": False,
            "full_replace": True # flag to tell frontend to replace everything
        }]
    return {"items": items}

class GenerateCommentRequest(BaseModel):
    code_snippet: str
    indentation: str
    is_inline: bool = False
    language: str = "python"
    doc_level: str = "maximum"
    full_replace: bool = False
    is_markdown_cell: bool = False
    clean_with_nltk: bool = False

class GenerateCommentResponse(BaseModel):
    docstring: str

@router.post("/generate-comment", response_model=GenerateCommentResponse)
async def api_generate_comment(req: GenerateCommentRequest):
    """
    Generates a docstring for a specific code chunk and formats it with indentation.
    If full_replace is True, returns the generated commented code in its entirety.
    """
    try:
        raw_docstring = await generate_docstring(
            req.code_snippet, 
            is_inline=req.is_inline, 
            language=req.language.lower(), 
            doc_level=req.doc_level,
            is_markdown_cell=req.is_markdown_cell
        )
        
        if req.clean_with_nltk and not req.full_replace:
            # Clean and normalize generated docstring using NLTK cleaner
            raw_docstring = preprocessor.clean_text(raw_docstring, remove_urls=False, remove_special=False, to_lower=False)
        
        # If the LLM returned the fully commented code block (for non-Python)
        if hasattr(req, 'full_replace') and getattr(req, 'full_replace', False):
            # For this scenario, raw_docstring IS the new code block
            formatted_docstring = raw_docstring
            
        else:
            # Python AST snippet logic
            lines = raw_docstring.split('\n')
            indented_lines = [req.indentation + line if line.strip() else "" for line in lines]
            
            if req.is_inline:
                # Format as a single-line python comment
                comment_text = indented_lines[0].strip()
                formatted_docstring = f'{req.indentation}# {comment_text}\n'
            else:
                formatted_docstring = f'{req.indentation}"""\n' + '\n'.join(indented_lines) + f'\n{req.indentation}"""\n'
        
        # Record history for preview
        history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "code": (req.code_snippet[:150] + "...") if len(req.code_snippet) > 150 else req.code_snippet,
            "docstring": (formatted_docstring[:150] + "...") if len(formatted_docstring) > 150 else formatted_docstring
        })
        
        return GenerateCommentResponse(docstring=formatted_docstring)
    except Exception as e:
        return GenerateCommentResponse(docstring=f"{req.indentation}\"\"\"\n{req.indentation}Error generating docstring: {str(e)}\n{req.indentation}\"\"\"\n")

class RunRequest(BaseModel):
    code: str

class RunResponse(BaseModel):
    output: str
    error: str

@router.post("/run-code", response_model=RunResponse)
async def api_run_code(req: RunRequest):
    """
    Executes the provided python code in a temporary file and captures stdout/stderr.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(req.code)
        temp_file = f.name
        
    try:
        result = subprocess.run(['python', temp_file], capture_output=True, text=True, timeout=10)
        return RunResponse(output=result.stdout, error=result.stderr)
    except subprocess.TimeoutExpired:
        return RunResponse(output="", error="Execution timed out (10s limit).")
    except Exception as e:
        return RunResponse(output="", error=str(e))
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

class ExplainRequest(BaseModel):
    code: str
    user_input: Optional[str] = None

class ExplainResponse(BaseModel):
    explanation: str

@router.post("/explain-code", response_model=ExplainResponse)
async def api_explain_code(req: ExplainRequest):
    """
    Explains a chunk of code via the LLM context menu feature.
    """
    try:
        explanation = await explain_code(req.code, req.user_input)
        return ExplainResponse(explanation=explanation)
    except Exception as e:
        return ExplainResponse(explanation=f"Error generating explanation: {str(e)}")

class AnalysisRequest(BaseModel):
    code: str

@router.post("/analyze-concepts", response_model=Dict[str, Any])
async def api_analyze_concepts(req: AnalysisRequest):
    """
    Extracts high-level programming concepts from the code snippet using the LLM heuristic engine.
    """
    if not req.code.strip():
        return {"concepts": []}
    
    concepts = await extract_concepts(req.code)
    return {"concepts": concepts}

@router.post("/analyze-similarity", response_model=Dict[str, Any])
async def api_analyze_similarity(req: AnalysisRequest):
    """
    Determines open-source heuristic similarity using the LLM heuristic engine.
    """
    if not req.code.strip():
        return {"score": 0, "source": "Unknown"}
    
    result = await analyze_similarity(req.code)
    return result

# --- REPO MODE ENDPOINTS ---
from fastapi import UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse
from app.services.git_service import (
    init_job, get_job_status, process_repo_background, 
    get_repo_diff, commit_and_zip_repo
)
import os

@router.post("/repo/upload")
async def api_repo_upload(doc_level: str = Form("medium"), file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Receives a .zip repository, initializes a job, and starts background extraction & processing.
    """
    if not file.filename.endswith(".zip"):
        return JSONResponse(status_code=400, content={"error": "Only .zip repositories are supported."})
        
    session_id = init_job()
    
    # Save the zip temporarily
    temp_dir = os.path.join("temp_repos", session_id)
    os.makedirs(temp_dir, exist_ok=True)
    zip_path = os.path.join(temp_dir, file.filename)
    
    with open(zip_path, "wb") as buffer:
        buffer.write(await file.read())
        
    extract_path = os.path.join(temp_dir, "extracted")
    
    background_tasks.add_task(process_repo_background, session_id, zip_path, extract_path, doc_level)
    
    return {"session_id": session_id}

@router.get("/repo/status/{session_id}")
async def api_repo_status(session_id: str):
    """
    Polling endpoint for UI to check background progress.
    """
    return get_job_status(session_id)

@router.get("/repo/diff/{session_id}")
async def api_repo_diff(session_id: str):
    """
    Returns the git diff created by the LLM generated comments.
    """
    diff_text = get_repo_diff(session_id)
    return {"diff": diff_text}

class CommitRequest(BaseModel):
    message: str

@router.post("/repo/commit/{session_id}")
async def api_repo_commit(session_id: str, req: CommitRequest, background_tasks: BackgroundTasks):
    """
    Commits changes using the given message, zips the modified repo, and returns it.
    Cleans up the temp folder afterwards.
    """
    status = get_job_status(session_id)
    if status.get("status") not in ["completed", "failed"]:
        return JSONResponse(status_code=400, content={"error": "Job is not ready for commit."})
        
    temp_dir = os.path.join("temp_repos", session_id)
    output_zip_path = os.path.join(temp_dir, "documented_repo.zip")
    
    try:
        commit_and_zip_repo(session_id, req.message, output_zip_path)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
        
    # Check if a zip was created
    if not os.path.exists(output_zip_path):
        return JSONResponse(status_code=500, content={"error": "Failed to create output zip."})
        
    # Schedule cleanup after download
    import shutil
    background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)
    
    return FileResponse(
        output_zip_path, 
        media_type='application/zip', 
        filename="documented_repo.zip"
    )

# --- NATIVE DOCUMENT GENERATION ENDPOINT ---
from app.pdf_converter.enums.templates import PDFTemplate
from app.pdf_converter.pdf.md_complete_conversion import convert_md_complete
from app.pdf_converter.docx.md_docx_converter import convert_md_to_docx

class GenerateDocumentRequest(BaseModel):
    code: str
    format: str = "PDF" 
    filename: str = "document"
    template: str = "Classic"
    language: str = "python"

@router.post("/generate-document")
async def api_generate_document(req: GenerateDocumentRequest, background_tasks: BackgroundTasks):
    """
    Takes the raw code/markdown from the editor or repository and converts it to a PDF or DOCX natively.
    """
    language = req.language.lower()
    title = req.filename.replace("_", " ").title()

    if language == "ipynb" or req.filename.endswith(".ipynb"):
        import io
        from app.pdf_converter.parsers.ipynb_parser import parse_ipynb
        try:
            text_content = parse_ipynb(io.StringIO(req.code))
        except Exception:
            text_content = f"```json\n{req.code}\n```"
        text_content = f"# {title}\n\n{text_content}"
    elif language == "markdown":
        text_content = req.code
        if not text_content.lstrip().startswith("#"):
            text_content = f"# {title}\n\n{text_content}"
    else:
        # Wrap raw code in a markdown fence for proper styling/syntax highlighting
        text_content = f"# {title}\n\n```{language}\n{req.code}\n```"

    temp_dir = tempfile.mkdtemp()
    
    try:
        # Match template string to enum, fallback to CLASSIC
        try:
            selected_template = PDFTemplate(req.template)
        except ValueError:
            selected_template = PDFTemplate.CLASSIC

        if req.format.upper() == "DOCX":
            output_path = os.path.join(temp_dir, f"{req.filename}.docx")
            convert_md_to_docx(text_content, output_path, selected_template)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            download_name = f"{req.filename}.docx"
        else:
            output_path = os.path.join(temp_dir, f"{req.filename}.pdf")
            convert_md_complete(text_content, output_path, selected_template)
            media_type = "application/pdf"
            download_name = f"{req.filename}.pdf"
            
        # Clean up temp directory after response
        import shutil
        background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)

        return FileResponse(
            output_path,
            media_type=media_type,
            filename=download_name
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Document generation failed: {str(e)}"})

# --- AI SUMMARY ENDPOINT ---
class AISummaryRequest(BaseModel):
    code: str
    language: str = "python"
    filename: str = "program"
    format: str = "PDF"
    template: str = "Classic"
    apply_nlp_preprocessing: bool = False

@router.post("/generate-ai-summary")
async def api_generate_ai_summary(req: AISummaryRequest, background_tasks: BackgroundTasks):
    """
    Generates a comprehensive AI Summary report for the uploaded code file.
    Optionally enriches the report with NLTK-based text preprocessing and lexical metrics.
    """
    try:
        import shutil

        title = req.filename.replace("_", " ").replace("-", " ").title()

        # Call LLM for the analysis-only summary
        ai_section_md = await generate_ai_summary(req.code, req.language, req.filename)

        # Prepend NLTK Lexical Preprocessing section if requested
        if req.apply_nlp_preprocessing:
            nlp_res = preprocessor.preprocess_code_comments(req.code)
            keywords_str = ", ".join([f"**{k['word']}** ({k['count']})" for k in nlp_res['keywords'][:8]]) if nlp_res['keywords'] else "None extracted"
            tokens_sample = ", ".join(nlp_res['tokens'][:15]) if nlp_res['tokens'] else "N/A"
            nlp_section = f"""## 🔬 NLTK Text Preprocessing & Lexical Analysis
──────────────────────────────────────────────────────────────

A structured natural language preprocessing pass was applied to source comments and documentation tokens using NLTK (Punkt Tokenizer, Stopword Filtering, and WordNet Lemmatization).

| Preprocessing Metric | Measurement |
|---|---|
| **Raw Token Count** | {nlp_res['original_token_count']} |
| **Filtered Token Count** | {nlp_res['processed_token_count']} |
| **Stopwords Removed** | {nlp_res['stopwords_removed']} |
| **Unique Vocabulary Count** | {nlp_res['unique_token_count']} |
| **Lexical Diversity (Type-Token Ratio)** | {nlp_res['lexical_diversity']} |

### 🏷️ Extracted Domain Keywords
{keywords_str}

### 🧩 Normalized Tokens (Preview)
`{tokens_sample}`

---

"""
            full_markdown = f"# AI Summary Report: {title}\n\n{nlp_section}{ai_section_md}"
        else:
            full_markdown = f"# AI Summary Report: {title}\n\n{ai_section_md}"

        temp_dir = tempfile.mkdtemp()

        try:
            selected_template = PDFTemplate(req.template)
        except ValueError:
            selected_template = PDFTemplate.CLASSIC

        if req.format.upper() == "DOCX":
            output_path = os.path.join(temp_dir, f"{req.filename}_ai_summary.docx")
            convert_md_to_docx(full_markdown, output_path, selected_template)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            download_name = f"{req.filename}_ai_summary.docx"
        else:
            output_path = os.path.join(temp_dir, f"{req.filename}_ai_summary.pdf")
            convert_md_complete(full_markdown, output_path, selected_template)
            media_type = "application/pdf"
            download_name = f"{req.filename}_ai_summary.pdf"

        background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)

        return FileResponse(
            output_path,
            media_type=media_type,
            filename=download_name
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"AI Summary generation failed: {str(e)}"})

# --- NLTK PREPROCESSING DEDICATED ENDPOINTS ---
class NLPPreprocessRequest(BaseModel):
    text: str
    to_lower: bool = True
    remove_punctuation: bool = True
    remove_stopwords: bool = True
    stemming: bool = False
    lemmatization: bool = True
    extract_keywords_count: int = 8
    is_code: bool = False

class NLPPreprocessResponse(BaseModel):
    original_text: str
    processed_text: str
    sentence_count: int = 0
    original_token_count: int = 0
    processed_token_count: int = 0
    unique_token_count: int = 0
    stopwords_removed: int = 0
    lexical_diversity: float = 0.0
    tokens: List[str] = []
    keywords: List[Dict[str, Any]] = []

@router.post("/nlp/preprocess", response_model=NLPPreprocessResponse)
async def api_nlp_preprocess(req: NLPPreprocessRequest):
    """
    Applies NLTK-based text preprocessing (tokenization, stopword removal, stemming/lemmatization, keyword extraction).
    """
    try:
        if req.is_code:
            res = preprocessor.preprocess_code_comments(req.text)
        else:
            res = preprocessor.process(
                text=req.text,
                to_lower=req.to_lower,
                remove_punctuation=req.remove_punctuation,
                remove_stopwords=req.remove_stopwords,
                stemming=req.stemming,
                lemmatization=req.lemmatization,
                extract_keywords_count=req.extract_keywords_count
            )
        return NLPPreprocessResponse(**res)
    except Exception as e:
        return NLPPreprocessResponse(
            original_text=req.text,
            processed_text="",
            tokens=[],
            keywords=[{"word": f"Error: {str(e)}", "count": 1}]
        )

@router.get("/nlp/options")
async def api_nlp_options():
    """
    Returns available NLP preprocessing capabilities and configuration options.
    """
    return {
        "status": "online",
        "library": "NLTK",
        "tokenizers": ["NLTK Word Tokenizer", "NLTK Sentence Tokenizer", "Regex Fallback"],
        "stemmers": ["Porter Stemmer"],
        "lemmatizers": ["WordNet Lemmatizer"],
        "filters": ["Stopword Removal (English)", "Punctuation Stripping", "Case Normalization"],
        "metrics": ["Lexical Diversity (Type-Token Ratio)", "Token Frequency Distribution", "Keyword Extraction"]
    }

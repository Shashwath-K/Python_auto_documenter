import logging
import asyncio
from ollama import AsyncClient
from app.core.config import settings

logger = logging.getLogger(__name__)

async def generate_docstring(code_snippet: str, is_inline: bool = False, language: str = "python", doc_level: str = "maximum", is_markdown_cell: bool = False) -> str:
    """
    Calls the LLM to generate a comment or docstring for the provided code.
    Adjusts behavior based on the target programming language and doc_level (min/med/max).
    """
    
    # Configure Doc Level Instructions for Docstrings
    if doc_level == "minimum":
        level_instruction = "Low density (approx 30%). Focus strictly on a high-level summary of the class or function."
    elif doc_level == "medium":
        level_instruction = "Medium density (approx 50%). Provide a detailed explanation of the logic, covering main flow and parameters."
    else: # maximum
        level_instruction = "High density (100%). Provide a highly detailed step-by-step explanation of every single line of internal logic."

    # Language Specific Overrides
    if language != "python":
        if is_markdown_cell or language == "md":
            prompt = f"""
            You are an expert technical writer. I will provide you with a raw snippet of Markdown text.
            Your task is to review the text and return it EXACTLY in the following custom format:
            
            [Preview]
            (Write a very brief 1-2 sentence summary of what this markdown text is about to give the user a preview)
            
            [Code (Raw)]
            (Return the EXACT original markdown text here, completely unmodified)
            
            CRITICAL:
            1. DO NOT wrap the response in markdown blocks like ```md.
            2. ONLY return the two sections exactly as described above.
            
            Text to review:
            {code_snippet}
            """
        else:
            if doc_level == "minimum":
                density = "Low density (approx 30%). Add a high-level block comment at the top, and ONLY comment class/function definitions."
            elif doc_level == "medium":
                density = "Medium density (approx 50%). Add comments for functions, classes, and complex logic blocks or variable assignments."
            else:
                density = "High density (100%). Add short comments to almost every significant line to explain what it does step-by-step."
                
            # For non-python, we send the FULL block and expect the FULL block back properly commented
            prompt = f"""
        You are an expert developer. I will provide you with a raw snippet of {language.upper()} code.
        Your task is to return the exact same code, but with comments added according to the requested density.
        
        Density Requested: {density}
        
        CRITICAL:
        1. Use the correct comment syntax for {language.upper()} (e.g. `//` or `/*` for JS/C++, `#` for Bash/R, etc).
        2. Respond ONLY with the newly commented code. Do not wrap it in markdown blockticks like ```js.
        3. DO NOT CHANGE A SINGLE LINE OF THE ORIGINAL CODE LOGIC. DO NOT ADD NEW CODE BLOCKS, DO NOT DELETE CODE. ONLY ADD COMMENTS.
        4. IF A LINE OR SNIPPET ALREADY HAS A COMMENT, DO NOT MODIFY IT OR ADD AN ADDITIONAL COMMENT. KEEP PRE-EXISTING COMMENTS EXACTLY AS THEY ARE.
        
        Code to comment:
        {code_snippet}
        """
    else:
        # Standard Python injection logic (snippet-based via AST)
        if is_inline:
            prompt = f"""
            You are an expert Python developer. I will provide you with a Python snippet (usually a variable assignment or conditional block).
            Your task is to write a SINGLE, concise inline comment explaining WHY this code exists or its high-level purpose.
            
            CRITICAL: 
            1. DO NOT simply repeat what the code says. Explain its intent.
            2. Respond ONLY with the comment text itself. DO NOT OUTPUT ANY ORIGINAL CODE WHATSOEVER.
            3. Keep it short.
            4. DO NOT wrap the response in markdown code blocks.
            5. DO NOT include the `#` character in your response, just the raw text.
            6. IF THIS SNIPPET ALREADY CONTAINS A COMMENT, DO NOT MODIFY IT OR RETURN A NEW ONE. JUST RETURN THE EXISTING TEXT OR AN EMPTY STRING.
            7. UNDER NO CIRCUMSTANCES SHOULD YOU RETURN THE PROVIDED CODE. YOU MUST ONLY GENERATE THE COMMENT TEXT.
            
            Here is the code:
            {code_snippet}
            """
        else:
            prompt = f"""
            You are an expert Python developer. I will provide you with a Python function, class, or script.
            Your task is to write a PEP 257 compliant docstring for it.
            
            Context Level: {level_instruction}
            
            CRITICAL: 
            1. DO NOT regurgitate the code. Evaluate its intent based on the Context Level.
            2. Respond ONLY with the docstring text itself. DO NOT OUTPUT ANY ORIGINAL CODE WHATSOEVER.
            3. DO NOT wrap the response in markdown code blocks (e.g., ```python).
            4. DO NOT include the \"\"\" quotes at the beginning or end of your response, just the inner text.
            5. IF THIS CLASS/FUNCTION ALREADY HAS A DOCSTRING, DO NOT MODIFY IT. RETURN IT EXACTLY AS IS.
            6. NEVER REWRITE, MODIFY, OR OUTPUT THE PROVIDED CODE. ONLY WRITE THE DOCSTRING TEXT.
            
            Here is the code:
            {code_snippet}
            """
    
    if settings.LLM_PROVIDER == "ollama":
        try:
            client = AsyncClient()
            response = await asyncio.wait_for(
                client.chat(model=settings.OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}]),
                timeout=60.0
            )
            docstring = response['message']['content'].strip()
            
            # Clean up potential markdown formatting
            if docstring.startswith("```"):
                lines = docstring.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                docstring = '\n'.join(lines).strip()
            
            # Clean up quotes if the model disobeys
            if docstring.startswith('"""') and docstring.endswith('"""'):
                docstring = docstring[3:-3].strip()
            
            return docstring
            
        except asyncio.TimeoutError:
            logger.error("Ollama timeout during docstring generation")
            return "Error: Generation timed out."
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return f"Error generating docstring: {e}"
    else:
        return "This is a dummy PEP 257 compliant docstring generated because Ollama is not available or configured."

async def explain_code(code_snippet: str, user_query: str = None) -> str:
    """
    Calls the LLM to explain the provided code snippet.
    Optionally incorporates a user_query to focus the explanation.
    """
    if user_query:
        prompt = f"""
        You are an expert Python developer and teacher.
        Explain the following code snippet. The user specifically asked: "{user_query}"
        
        Keep your explanation clear, concise, and formatted in markdown.
        Do not write overly long essays.
        
        Code:
        ```python
        {code_snippet}
        ```
        """
    else:
        prompt = f"""
        You are an expert Python developer and teacher.
        Explain the purpose and functionality of the following code snippet concisely.
        
        Keep your explanation clear, concise, and formatted in markdown.
        Do not write overly long essays.
        
        Code:
        ```python
        {code_snippet}
        ```
        """
        
    if settings.LLM_PROVIDER == "ollama":
        try:
            client = AsyncClient()
            response = await asyncio.wait_for(
                client.chat(model=settings.OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}]),
                timeout=60.0
            )
            return response['message']['content'].strip()
        except asyncio.TimeoutError:
            logger.error("Ollama timeout during code explanation")
            return "Error: Generation timed out."
        except Exception as e:
            logger.error(f"Error calling Ollama for explanation: {e}")
            return f"Error generating explanation: {e}"
    else:
        return "This is a dummy explanation generated because Ollama is not available."

async def generate_ai_summary(code: str, language: str = "python", filename: str = "program") -> str:
    """
    Calls the LLM to generate a richly formatted, in-depth AI Summary analysis document.
    Targets minimum 2 pages of detailed content.
    Returns a well-structured markdown string with headings, tables, and bullet lists.
    """
    lang_upper = language.upper()

    prompt = f"""
    You are a world-class senior software engineer and technical educator writing a DETAILED,
    PROFESSIONAL analysis report that will be published as a PDF.

    I will give you the contents of a {lang_upper} file named '{filename}'.

    ══════════════════════════════════════════════════════════════
    CRITICAL LENGTH REQUIREMENT
    ══════════════════════════════════════════════════════════════
    This report MUST be at least 2 full pages when rendered as a PDF.
    Every section must be thorough and detailed. SHORT or BRIEF responses are UNACCEPTABLE.
    Think of the depth of a detailed technical blog post or a university assignment report.
    ══════════════════════════════════════════════════════════════

    Use clear markdown headings, **bold** labels, well-formatted tables, and professional prose.
    Follow this EXACT structure:

    ──────────────────────────────────────────────────────────────
    ## 🧠 Program Description
    ──────────────────────────────────────────────────────────────

    Write a MINIMUM of 4 detailed paragraphs covering ALL of the following:
    - **Overview**: What is the purpose of this program? What problem does it solve?
    - **Methodology**: Describe the step-by-step algorithm or workflow in detail.
    - **Inputs & Outputs**: What data does it take in, what does it produce?
    - **Key Techniques**: What statistical, mathematical, or CS concepts are applied?
    - **Design Choices**: Why was this approach chosen? What are its trade-offs?

    ---

    ## ⏱️ Time & Space Complexity
    ──────────────────────────────────────────────────────────────

    > **MANDATORY — do not skip any function, loop, cell, or algorithm block.**

    Provide a row for EVERY significant operation in the file (each notebook cell, each function,
    each major loop, each data transformation). Be pedantic — more rows is better.

    | Function / Block | Time Complexity | Space Complexity | Explanation |
    |---|---|---|---|
    | (every function, loop, algorithm, or notebook cell goes here) | O(...) | O(...) | explain WHY this complexity |

    After the table, write **3–5 sentences** analysing the overall complexity profile:
    - What is the dominant time/space cost?
    - Is this program computationally feasible for large datasets?
    - What would happen if the input size doubled or tripled?

    ---

    ## 📦 Dependencies & Libraries Used
    ──────────────────────────────────────────────────────────────

    | Library / Module | Version Notes | Purpose in This File | Key APIs / Functions Used |
    |---|---|---|---|
    | (every import, even standard library) | (if version matters) | (specific role in THIS file) | (exact function names used) |

    After the table, write **2–3 sentences** about the ecosystem these dependencies belong to
    and any notable compatibility or version considerations.

    ---

    ## 🔷 Programming Patterns & Paradigms
    ──────────────────────────────────────────────────────────────

    For each pattern or paradigm, use a **bold label** followed by 2–3 sentences of explanation
    that specifically reference how it appears in THIS file:

    - **Paradigm/Pattern Name**: Detailed explanation referencing specific parts of the code.

    Cover at least: coding paradigm (OOP/functional/procedural), data handling patterns,
    error handling strategy, modularity, and any design patterns present.

    ---

    ## 🚀 Potential Projects
    ──────────────────────────────────────────────────────────────

    List **7–10 distinct, creative, real-world project ideas** that build on this code.
    For each project, provide:
    - **Project Name** — a catchy title
    - **Description**: 2–3 sentences explaining what it does and how it extends the concepts here.
    - **Technologies**: list key tools/libraries needed.
    - **Difficulty**: Beginner / Intermediate / Advanced

    ---

    ## 📚 Your Next Learning Track
    ──────────────────────────────────────────────────────────────

    Create a **detailed progressive learning roadmap** with at least **8 steps**.
    Start from exactly what THIS file demonstrates and progress to expert-level mastery.

    For each step, write:
    **Step N — [Topic Name]**
    - **What to learn**: Specific concepts, functions, or techniques.
    - **Why this step**: How it directly follows from what was seen in this file.
    - **Resources to try**: 1–2 specific suggestions (library docs, theorem name, etc.)

    ---

    ## ⚡ Potential Optimisations
    ──────────────────────────────────────────────────────────────

    List at least **6 concrete, file-specific** optimisations. For each:

    **Optimisation N: [Short Title]**
    - **Current approach**: What the code does now.
    - **Suggested change**: The specific improvement.
    - **Expected benefit**: Quantify if possible (e.g. "reduces memory by ~50% for large datasets").
    - **Trade-off**: Any downside to this change.

    ---

    ## ⚠️ Edge Cases & Pitfalls
    ──────────────────────────────────────────────────────────────

    List at least **6 specific edge cases or failure modes** that exist in or are directly
    relevant to THIS code. For each:

    **Case N: [Short Title]**
    - **Scenario**: Describe the exact condition.
    - **Impact**: What breaks or goes wrong?
    - **Mitigation**: How to guard against it.

    ---

    ## 📊 Code Quality Assessment
    ──────────────────────────────────────────────────────────────

    Provide a professional code review summary covering:

    | Dimension | Rating (1–10) | Comments |
    |---|---|---|
    | Readability | X/10 | (specific comments) |
    | Modularity | X/10 | (specific comments) |
    | Error Handling | X/10 | (specific comments) |
    | Performance | X/10 | (specific comments) |
    | Documentation | X/10 | (specific comments) |
    | Best Practices | X/10 | (specific comments) |

    After the table, write a **3–4 sentence overall assessment** summarising the code quality.

    ══════════════════════════════════════════════════════════════
    ABSOLUTE RULES — VIOLATION IS NOT ACCEPTABLE:
    1. Start your response IMMEDIATELY with ## 🧠 Program Description — ZERO preamble.
    2. Do NOT reproduce the source code anywhere in the response.
    3. ALL tables MUST have a header row AND a separator row (|---|---|).
    4. Use **bold** for ALL labels, headings, and key terms.
    5. Use horizontal rules (---) between EVERY section.
    6. MINIMUM length: write enough to fill at least 2 printed A4 pages.
    7. Be SPECIFIC — reference actual variable names, function names, and logic from the file.
    8. Generic, vague, or short responses are a FAILURE. Every claim must be specific to THIS file.
    ══════════════════════════════════════════════════════════════

    File contents:
    {code}
    """

    if settings.LLM_PROVIDER == "ollama":
        try:
            client = AsyncClient()
            response = await asyncio.wait_for(
                client.chat(model=settings.OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}]),
                timeout=300.0
            )
            return response['message']['content'].strip()
        except asyncio.TimeoutError:
            logger.error("Ollama timeout during AI summary generation")
            return "## ⚠️ Error\n\n> Failed to generate AI summary: Request timed out (300s limit)."
        except Exception as e:
            logger.error(f"Error calling Ollama for AI summary: {e}")
            return f"## ⚠️ Error\n\n> Failed to generate AI summary: {e}"
    else:
        return "## 🧠 Program Description\n\nOllama is not configured. This is a placeholder summary."

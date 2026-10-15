from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.endpoints import router as api_router
from app.api.endpoints import history
from app.core.config import settings
import os

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api")

# Ensure templates and static directories exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Mount project images directory if present
ROOT_DIR = os.path.dirname(BASE_DIR)
images_dir = os.path.join(ROOT_DIR, "images")
if os.path.exists(images_dir):
    app.mount("/images", StaticFiles(directory=images_dir), name="images")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/")
async def landing(request: Request):
    """
    Renders the landing page.
    """
    return templates.TemplateResponse(
        request=request, 
        name="landing.html", 
        context={"request": request}
    )

@app.get("/upload-mode")
async def upload_mode(request: Request):
    """
    Renders the file upload tool, passing reversed history (latest first).
    """
    return templates.TemplateResponse(
        request=request, 
        name="upload_mode.html", 
        context={
            "request": request,
            "history": list(reversed(history))
        }
    )

@app.get("/live-mode")
async def live_mode(request: Request):
    """
    Renders the live generation editor tool.
    """
    return templates.TemplateResponse(
        request=request, 
        name="live_mode.html", 
        context={
            "request": request,
            "history": list(reversed(history))
        }
    )

@app.get("/repo-mode")
async def repo_mode(request: Request):
    """
    Renders the Repository Upload & Processing tool.
    """
    return templates.TemplateResponse(
        request=request, 
        name="repo_mode.html", 
        context={"request": request}
    )

@app.get("/documentation")
@app.get("/docs-guide")
async def documentation_page(request: Request):
    """
    Renders the comprehensive documentation, architecture, and developer guide.
    """
    doc_sections = [
        {"id": "quick-start", "title": "Quick Start Guide", "badge": "Essential"},
        {"id": "architecture", "title": "Architecture & Data Flow", "badge": "Core"},
        {"id": "nlp-pipeline", "title": "NLTK Preprocessing Pipeline", "badge": "NLP"},
        {"id": "live-mode-guide", "title": "Live Mode & Ghost Typing", "badge": "RPA"},
        {"id": "file-convert-guide", "title": "File & Jupyter Conversion", "badge": "Format"},
        {"id": "repo-scan-guide", "title": "Repository Batch Scanner", "badge": "Git"},
        {"id": "ai-summaries-guide", "title": "Native PDF & DOCX AI Reports", "badge": "Export"},
        {"id": "api-reference", "title": "REST API Reference", "badge": "v1.0"},
        {"id": "troubleshooting", "title": "Configuration & Ollama", "badge": "Setup"}
    ]
    return templates.TemplateResponse(
        request=request,
        name="documentation.html",
        context={
            "request": request,
            "sections": doc_sections,
            "project_name": settings.PROJECT_NAME,
            "model_name": settings.OLLAMA_MODEL
        }
    )

if __name__ == "__main__":
    import uvicorn
    # Make sure to run this file from the project root!
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=False)

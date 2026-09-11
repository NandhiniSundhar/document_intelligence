import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.api.routes.documents import router as documents_router
from app.core.database import init_db

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Document Intelligence API",
    version="1.0.0",
    description="Financial document extraction, validation and persistence API."
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(documents_router, prefix="/api/v1")

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/documents/{document_name}", response_class=HTMLResponse)
def document_result(request: Request, document_name: str):
    return templates.TemplateResponse(
        "document_result.html",
        {"request": request, "document_name": document_name}
    )

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
import sys

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from api import services, categories, import_export, preview, bookmarks, auth
from core.config import settings
from core.auth import get_current_user, verify_token
from fastapi import Depends

app = FastAPI(
    title="Homepage Configuration Tool",
    description="Web-based configuration tool for Homepage dashboard",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "frontend" / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Mount images directory for custom icons
images_path = Path("/app/public/images")
if images_path.exists():
    app.mount("/images", StaticFiles(directory=str(images_path)), name="images")

# Include routers
# Auth router (no authentication required)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Protected routers (authentication required)
app.include_router(services.router, prefix="/api/services", tags=["services"], dependencies=[Depends(get_current_user)])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"], dependencies=[Depends(get_current_user)])
app.include_router(import_export.router, prefix="/api/config", tags=["config"], dependencies=[Depends(get_current_user)])
app.include_router(preview.router, prefix="/api/preview", tags=["preview"], dependencies=[Depends(get_current_user)])
app.include_router(bookmarks.router, prefix="/api/bookmarks", tags=["bookmarks"], dependencies=[Depends(get_current_user)])

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page (authentication will be checked by frontend)"""
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve the login page (no authentication required)"""
    html_path = Path(__file__).parent.parent / "frontend" / "login.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Homepage Config Tool"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
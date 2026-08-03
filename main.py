"""
MURPHY — Main Application Entry Point

Run with:
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__, __app_name__
from app.core.config import get_settings

# ── Initialise settings ─────────────────────────────────
settings = get_settings()

# ── Create FastAPI application ──────────────────────────
app = FastAPI(
    title=__app_name__,
    description=(
        "An intelligent AI-powered assistant that helps developers "
        "understand, navigate, and analyze software projects using "
        "Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG)."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ─────────────────────────────────────
# Allow Streamlit frontend (and dev tools) to communicate with the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Root / Health Check ─────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "application": __app_name__,
        "version": __version__,
        "status": "running",
        "environment": settings.app_env,
    }


# ── Startup Event ──────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    """Run once when the application starts."""
    print(f"\n🧠 {__app_name__} v{__version__} is starting up...")
    print(f"   Environment : {settings.app_env}")
    print(f"   Debug       : {settings.debug}")
    print(f"   Embedding   : {settings.embedding_provider}")
    print(f"   Vectorstore : {settings.vectorstore_path}")
    print()


# ── CLI entry point ────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

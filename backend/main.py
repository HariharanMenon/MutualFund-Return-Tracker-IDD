"""
main.py — FastAPI application entry point.

Responsibilities (spec product-structure.md §Backend Key Files):
  - Initialise FastAPI app instance
  - Configure CORS (open to all origins — spec §15)
  - Register request-logging middleware
  - Mount /api router (POST /api/upload)
  - Health check endpoint (GET /health) for Render keep-alive pings
  - Serve React SPA static files from /frontend/dist (production only)

Start command (Procfile / Render):
  uvicorn main:app --host 0.0.0.0 --port $PORT

Local development:
  uvicorn main:app --reload --port 8000
"""

import os
import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import FileResponse, Response

from app.api import api_router
from app.utils.logger import get_logger
from config import API_PREFIX, CORS_ALLOW_HEADERS, CORS_ALLOW_METHODS, CORS_ALLOW_ORIGINS

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="MF XIRR Tracker API",
    description=(
        "Stateless API for uploading mutual fund Excel statements, "
        "calculating XIRR, and returning structured transaction data."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — open to all origins (spec §15: no sensitive data, no auth)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=False,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    logger.info("%s %s", request.method, request.url.path)
    response: Response = await call_next(request)
    logger.info("→ %d", response.status_code)
    return response

# ---------------------------------------------------------------------------
# API routes — mounted at /api
# ---------------------------------------------------------------------------

app.include_router(api_router, prefix=API_PREFIX)

# ---------------------------------------------------------------------------
# Health check — Render free tier pings this to detect liveness
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"], summary="Health check")
async def health() -> dict:
    return {"status": "ok"}

# ---------------------------------------------------------------------------
# Serve React SPA static files (production only)
# The frontend/dist directory is created by `npm run build`.
# In local development, Vite's dev server (port 5173) is used instead.
# ---------------------------------------------------------------------------

_FRONTEND_DIST = pathlib.Path(__file__).parent.parent / "frontend" / "dist"

if _FRONTEND_DIST.is_dir():
    # Serve all static assets (JS, CSS, images)
    app.mount(
        "/assets",
        StaticFiles(directory=str(_FRONTEND_DIST / "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        """Fall-through route — serves index.html for all non-API paths (React router)."""
        index = _FRONTEND_DIST / "index.html"
        return FileResponse(str(index))

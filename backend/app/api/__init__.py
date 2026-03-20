# app/api/__init__.py
from fastapi import APIRouter
from app.api.routes.upload import router as upload_router

api_router = APIRouter()
api_router.include_router(upload_router, prefix="", tags=["upload"])

__all__ = ["api_router"]

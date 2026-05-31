"""
error.py — Pydantic model for structured error payloads.

Used in UploadResponse.error and returned directly in HTTP error responses.
Matches the spec API contract (§4 API Endpoint):

  {
    "success": false,
    "error": {
      "message": "File validation failed",
      "details": "Row 5: Invalid date format ..."
    }
  }
"""

from typing import Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Structured error payload embedded in failed UploadResponse objects."""

    message: str = Field(
        ...,
        description="Short, human-readable error category",
        examples=["File validation failed"],
    )
    details: Optional[str] = Field(
        default=None,
        description="Specific error description with row numbers where applicable",
        examples=["Row 5: Invalid date format 'xyz' (expected DD-MMM-YYYY, e.g., 15-Jan-2020)"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "File validation failed",
                "details": "Row 5: Invalid date format 'xyz' (expected DD-MMM-YYYY, e.g., 15-Jan-2020)",
            }
        }
    }

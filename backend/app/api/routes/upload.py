"""
upload.py — POST /api/upload endpoint.

Orchestration order (spec §3 Steps 3–5):
  1. Read raw bytes from the uploaded file
  2. File-size guard (10 MB — spec §9)
  3. file_parser.parse_excel()        → raw row dicts
  4. validator.validate()             → typed validated row dicts
  5. transaction_processor.process()  → list[Transaction]
  6. xirr_calculator.calculate()      → (xirr_pct, SummaryMetrics)
  7. Return UploadResponse(success=True, ...)

Error handling:
  FileProcessingError  → HTTP 400
  FileValidationError  → HTTP 400
  XirrCalculationError → HTTP 500
  Unexpected exception → HTTP 500 (generic)
"""

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.exceptions.calculation_error import XirrCalculationError
from app.exceptions.file_error import FileProcessingError
from app.exceptions.validation_error import FileValidationError
from app.models.error import ErrorDetail
from app.models.response import UploadResponse
from app.services import file_parser, transaction_processor, validator, xirr_calculator
from app.utils.logger import get_logger
from config import MAX_FILE_SIZE

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload mutual fund Excel statement",
    description=(
        "Accepts a single .xlsx file containing mutual fund transaction history "
        "for one fund. Validates, calculates XIRR, and returns transaction data "
        "with summary metrics."
    ),
    responses={
        200: {"description": "File processed successfully"},
        400: {"description": "File validation error or processing error"},
        413: {"description": "File exceeds 10 MB limit"},
        500: {"description": "XIRR calculation failed"},
    },
)
async def upload_file(
    file: UploadFile = File(..., description="Excel (.xlsx) mutual fund statement"),
) -> JSONResponse:
    """Process an uploaded mutual fund statement and return XIRR + metrics."""

    logger.info("Received upload: filename='%s', content_type='%s'", file.filename, file.content_type)

    # ------------------------------------------------------------------ #
    # Step 1: Read file bytes                                              #
    # ------------------------------------------------------------------ #
    try:
        content: bytes = await file.read()
    except Exception as exc:
        logger.error("Failed to read uploaded file: %s", exc)
        return _error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="File upload failed",
            details="Could not read the uploaded file. Please try again.",
        )

    # ------------------------------------------------------------------ #
    # Step 2: File-size guard (spec §9 — 10 MB)                           #
    # ------------------------------------------------------------------ #
    if len(content) > MAX_FILE_SIZE:
        logger.warning("File too large: %d bytes (max %d)", len(content), MAX_FILE_SIZE)
        return _error_response(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            message="File too large",
            details="File size exceeds 10 MB limit",
        )

    # ------------------------------------------------------------------ #
    # Step 3: Parse Excel                                                  #
    # ------------------------------------------------------------------ #
    try:
        raw_rows = file_parser.parse_excel(content)
    except FileProcessingError as exc:
        logger.warning("File processing error: %s | %s", exc.message, exc.details)
        return _error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=exc.message,
            details=exc.details,
        )

    # ------------------------------------------------------------------ #
    # Step 4: Validate                                                     #
    # ------------------------------------------------------------------ #
    try:
        validated_rows = validator.validate(raw_rows)
    except FileValidationError as exc:
        logger.warning("Validation error: %s | %s", exc.message, exc.details)
        return _error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=exc.message,
            details=exc.details,
        )

    # ------------------------------------------------------------------ #
    # Step 5: Build Transaction objects                                    #
    # ------------------------------------------------------------------ #
    transactions = transaction_processor.process(validated_rows)

    # ------------------------------------------------------------------ #
    # Step 6: Calculate XIRR + summary metrics                            #
    # ------------------------------------------------------------------ #
    try:
        xirr_pct, summary_metrics = xirr_calculator.calculate(validated_rows)
    except XirrCalculationError as exc:
        logger.error("XIRR calculation failed: %s | %s", exc.message, exc.details)
        return _error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=exc.message,
            details=exc.details,
        )

    # ------------------------------------------------------------------ #
    # Step 7: Return success response                                      #
    # ------------------------------------------------------------------ #
    logger.info(
        "Upload successful — %d transactions | XIRR: %.2f%%",
        len(transactions),
        xirr_pct,
    )

    response = UploadResponse(
        success=True,
        xirr=xirr_pct,
        summaryMetrics=summary_metrics,
        transactions=transactions,
        error=None,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(),
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _error_response(status_code: int, message: str, details: str) -> JSONResponse:
    """Build a standardised error JSONResponse matching the spec API contract."""
    body = UploadResponse(
        success=False,
        error=ErrorDetail(message=message, details=details),
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
    )

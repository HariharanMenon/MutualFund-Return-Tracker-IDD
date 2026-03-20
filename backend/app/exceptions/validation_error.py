"""
validation_error.py — Custom exception for file/data validation failures.
Raised by validator.py; caught in the API route and returned as HTTP 400.
"""


class FileValidationError(Exception):
    """Raised when uploaded file fails validation (column, row, or file-level)."""

    def __init__(self, message: str, details: str = "") -> None:
        self.message = message
        self.details = details
        super().__init__(message)

    def __repr__(self) -> str:
        return f"FileValidationError(message={self.message!r}, details={self.details!r})"

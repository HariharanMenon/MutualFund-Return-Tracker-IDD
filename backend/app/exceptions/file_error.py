"""
file_error.py — Custom exception for file-level processing failures.
Raised by file_parser.py; caught in the API route and returned as HTTP 400.
"""


class FileProcessingError(Exception):
    """Raised when the uploaded file cannot be read or parsed (corrupted, wrong format, etc.)."""

    def __init__(self, message: str, details: str = "") -> None:
        self.message = message
        self.details = details
        super().__init__(message)

    def __repr__(self) -> str:
        return f"FileProcessingError(message={self.message!r}, details={self.details!r})"

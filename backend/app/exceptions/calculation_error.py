"""
calculation_error.py — Custom exception for XIRR convergence / calculation failures.
Raised by xirr_calculator.py; caught in the API route and returned as HTTP 500.
"""


class XirrCalculationError(Exception):
    """Raised when XIRR calculation fails to converge or encounters invalid cash flows."""

    def __init__(self, message: str, details: str = "") -> None:
        self.message = message
        self.details = details
        super().__init__(message)

    def __repr__(self) -> str:
        return f"XirrCalculationError(message={self.message!r}, details={self.details!r})"

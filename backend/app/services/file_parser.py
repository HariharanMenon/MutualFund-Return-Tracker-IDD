"""
file_parser.py — Excel file parsing service.

Responsibilities:
- Open .xlsx bytes with openpyxl (data_only=True, read_only=True)
- Extract the FIRST worksheet only (additional sheets ignored — spec §3)
- Normalise column headers: lowercase + strip whitespace
- Return list of row dicts with normalised keys and raw cell values
- Skip rows where ALL cells are empty/None
- Raise FileProcessingError on any file-level failure
"""

import io
from typing import Any

import openpyxl
from openpyxl.utils.exceptions import InvalidFileException

from app.exceptions.file_error import FileProcessingError
from app.utils.constants import ErrorMessages
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _is_cell_empty(value: Any) -> bool:
    """Return True when a cell value is None or a blank/whitespace string."""
    return value is None or (isinstance(value, str) and value.strip() == "")


def parse_excel(file_content: bytes) -> list[dict[str, Any]]:
    """Parse the first worksheet of an xlsx file into a list of row dicts.

    Parameters
    ----------
    file_content:
        Raw bytes of the uploaded ``.xlsx`` file.

    Returns
    -------
    list[dict[str, Any]]
        One dict per non-empty data row.  Keys are normalised column header
        strings (lowercase, stripped); values are raw cell values as returned
        by openpyxl (may be ``str``, ``int``, ``float``, ``datetime``, or
        ``None``).  The header row itself is **not** included in the list.

    Raises
    ------
    FileProcessingError
        If the file cannot be opened, contains no worksheets, or the first
        worksheet has no header row.
    """
    try:
        wb = openpyxl.load_workbook(
            io.BytesIO(file_content),
            read_only=True,
            data_only=True,
        )
    except (InvalidFileException, Exception) as exc:
        logger.warning("Failed to open Excel workbook: %s", exc)
        raise FileProcessingError(
            message=ErrorMessages.FILE_CANNOT_BE_READ,
            details=str(exc),
        )

    if not wb.worksheets:
        raise FileProcessingError(
            message=ErrorMessages.FILE_CANNOT_BE_READ,
            details="The workbook contains no worksheets.",
        )

    ws = wb.worksheets[0]  # first sheet only — spec §3
    logger.info("Parsing worksheet: '%s'", ws.title)

    all_rows = list(ws.iter_rows(values_only=True))

    try:
        wb.close()
    except Exception:
        pass  # read_only workbooks sometimes error on close; safe to ignore

    if not all_rows:
        raise FileProcessingError(
            message=ErrorMessages.EMPTY_FILE,
            details="The first worksheet contains no rows.",
        )

    # --- Normalise header row ---
    raw_headers: tuple = all_rows[0]
    headers: list[str] = [
        str(cell).strip().lower() if not _is_cell_empty(cell) else ""
        for cell in raw_headers
    ]

    # --- Build row dicts, skipping fully empty rows ---
    result: list[dict[str, Any]] = []
    for row_tuple in all_rows[1:]:
        row_dict: dict[str, Any] = {}
        for header, cell_val in zip(headers, row_tuple):
            if header:  # ignore columns with empty/missing headers
                row_dict[header] = cell_val

        # Skip rows where ALL present-column cells are empty
        if all(_is_cell_empty(v) for v in row_dict.values()):
            continue

        result.append(row_dict)

    logger.info("Extracted %d data rows from first worksheet", len(result))
    return result

// constants.js — Frontend-side constants.
// Backend equivalents live in backend/config.py.

/** Base URL for all API calls. Falls back to same-origin (empty string) in production
 *  where the FastAPI server also serves the built frontend. */
export const API_URL = import.meta.env.VITE_API_URL || '';

/** Maximum allowed upload size in bytes — must match backend MAX_FILE_SIZE (10 MB). */
export const MAX_FILE_SIZE = 10 * 1024 * 1024;

/** Human-readable size limit shown in the UI. */
export const FILE_SIZE_LIMIT_LABEL = '10 MB';

/** Accepted file extension (lowercase). */
export const ACCEPTED_FILE_EXTENSION = '.xlsx';

/** MIME type for .xlsx files. */
export const ACCEPTED_MIME_TYPE =
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

/** Filename of the sample transaction template served from frontend/public/.
 *  Used by UploadArea to set the download attribute on the template link. */
export const TEMPLATE_FILE_NAME = 'MFTransaction_Template.xlsx';

/** URL path of the sample transaction template — served as a Vite static asset.
 *  Used by UploadArea as the href on the template download link. */
export const TEMPLATE_DOWNLOAD_URL = '/MFTransaction_Template.xlsx';

/** Column labels used in the transaction grid header row. */
export const COLUMN_LABELS = {
  date: 'Date',
  transactionType: 'Transaction Type',
  amount: 'Amount (₹)',
  units: 'Units',
  price: 'Price (₹)',
  unitBalance: 'Unit Balance',
};

/** Application display name. */
export const APP_NAME = 'Mutual Fund XIRR Tracker';
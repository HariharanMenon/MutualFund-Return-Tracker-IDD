// api.js — HTTP client for the MutualFund XIRR backend.

import logger from '../utils/logger.js';
import { API_URL } from '../utils/constants.js';

/**
 * Uploads an .xlsx file to POST /api/upload and returns the parsed response.
 *
 * @param {File} file  The Excel file selected by the user
 * @returns {Promise<Object>}  UploadResponse payload from the backend
 * @throws {Error}  .message is always a user-facing string safe to display
 */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const url = `${API_URL}/api/upload`;
  logger.info('Uploading file to', url);

  let response;
  try {
    response = await fetch(url, {
      method: 'POST',
      body: formData,
      // Content-Type is intentionally omitted — the browser sets it
      // automatically with the correct multipart boundary.
    });
  } catch (networkError) {
    logger.error('Network error during upload:', networkError);
    throw new Error(
      'Unable to reach the server. Please check your connection and try again.'
    );
  }

  // Attempt JSON parse regardless of status (error responses also use JSON)
  let data = null;
  try {
    data = await response.json();
  } catch {
    // Non-JSON body (e.g., proxy 502) — fall through to generic message
  }

  if (!response.ok) {
    const message =
      data?.error?.message ||
      data?.detail ||
      `Unexpected server error (HTTP ${response.status}). Please try again.`;
    logger.warn('Upload failed:', response.status, message);
    const err = new Error(message);
    err.status = response.status;
    err.detail = data?.error?.detail ?? null;
    throw err;
  }

  logger.info('Upload successful');
  return data;
}

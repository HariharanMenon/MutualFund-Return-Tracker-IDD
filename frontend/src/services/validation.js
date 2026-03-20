// validation.js — Frontend-side file validation before upload.
// These checks mirror the backend limits but give instant user feedback.

import { MAX_FILE_SIZE, ACCEPTED_MIME_TYPE, ACCEPTED_FILE_EXTENSION } from '../utils/constants.js';

/**
 * Returns true if the file is within the allowed size limit.
 * @param {File} file
 * @returns {boolean}
 */
export function isValidFileSize(file) {
  return file.size <= MAX_FILE_SIZE;
}

/**
 * Returns true if the file is an .xlsx file.
 * Checks both MIME type and file extension for cross-browser reliability.
 * @param {File} file
 * @returns {boolean}
 */
export function isValidFileType(file) {
  const nameMatches = (file.name || '').toLowerCase().endsWith(ACCEPTED_FILE_EXTENSION);
  const mimeMatches = file.type === ACCEPTED_MIME_TYPE;
  // Accept if either check passes — some browsers omit MIME for xlsx
  return nameMatches || mimeMatches;
}

// helpers.js — Shared, stateless utility functions.

/**
 * Returns true if value is null, undefined, or empty string.
 * @param {*} value
 * @returns {boolean}
 */
export function isEmpty(value) {
  return value === null || value === undefined || value === '';
}

/**
 * Clamps a number between min and max (inclusive).
 * @param {number} value
 * @param {number} min
 * @param {number} max
 * @returns {number}
 */
export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

/**
 * Returns true if the value is a finite number (not NaN, not ±Infinity).
 * @param {*} value
 * @returns {boolean}
 */
export function isFiniteNumber(value) {
  return typeof value === 'number' && isFinite(value);
}

/**
 * Converts bytes to a human-readable string (e.g., "4.2 MB").
 * @param {number} bytes
 * @returns {string}
 */
export function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

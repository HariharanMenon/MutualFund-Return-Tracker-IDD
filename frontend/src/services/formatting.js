// formatting.js — Display formatters for all data types in the result view.

/** Sentinel returned by formatters when a value is null/undefined. */
const EMPTY = '—';

/**
 * Formats a number as Indian-locale currency (₹ with Indian grouping).
 * Example: 1500000 → "₹15,00,000.00"
 * @param {number|null} amount
 * @returns {string}
 */
export function formatCurrency(amount) {
  if (amount == null) return EMPTY;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

/**
 * Returns the date string as-is (backend already returns DD-MMM-YYYY).
 * Returns EMPTY sentinel for null/undefined/empty input.
 * @param {string|null} dateStr  DD-MMM-YYYY from backend
 * @returns {string}
 */
export function formatDate(dateStr) {
  if (!dateStr) return EMPTY;
  return dateStr;
}

/**
 * Formats as a percentage with 2dp.
 * Example: 14.9608 → "14.96%"
 * Note: the backend returns xirr as a 14.96.
 * @param {number|null} value  Fractional XIRR (e.g. 14.9678)
 * @returns {string}
 */
export function formatPercentage(value) {
  if (value == null) return EMPTY;
  return `${(Number(value)).toFixed(2)}%`;
}

/**
 * Formats a unit count to 3 decimal places.
 * Example: 123.456789 → "123.457"
 * @param {number|null} value
 * @returns {string}
 */
export function formatUnits(value) {
  if (value == null) return EMPTY;
  return Number(value).toFixed(3);
}

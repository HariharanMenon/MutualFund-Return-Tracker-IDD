// useXirrCalculation.js — XIRR results state management.
// Extracts xirr, transactions, and summaryMetrics from upload response.

import { useMemo } from 'react';

/**
 * useXirrCalculation — Manages XIRR calculation results.
 *
 * This is a simple extraction hook — it derives XIRR, transactions, and
 * summary metrics from the API response data returned by an upload.
 *
 * Takes the data object from useFileUpload().data and extracts:
 *   - xirr {number}              Annualized return as decimal (e.g., 0.1254 for 12.54%)
 *   - transactions {Array}       List of transaction objects
 *   - summaryMetrics {Object}    { totalInvested, finalProceeds, profitLoss }
 *
 * Returns an object with:
 *   - xirr {number|null}
 *   - transactions {Array}       Empty array if no data
 *   - summaryMetrics {Object|null}
 *
 * This hook is primarily useful for:
 *   - Reading XIRR and results in a structured way
 *   - Memoizing calculations (though here it's just extraction)
 *   - Future enhancement: filtering, sorting, aggregation across uploads
 *
 * Example:
 *   const { xirr, transactions, summaryMetrics } = useXirrCalculation(uploadData);
 */
export default function useXirrCalculation(data) {
  // Memoize extraction so downstream consumers don't re-render unnecessarily
  const extracted = useMemo(() => {
    if (!data) {
      return {
        xirr: null,
        transactions: [],
        summaryMetrics: null,
      };
    }

    return {
      xirr: data.xirr ?? null,                       // May be 0, which is falsy but valid
      transactions: data.transactions ?? [],         // Empty array if not present
      summaryMetrics: data.summaryMetrics ?? null,   // Null if not present
    };
  }, [data]);

  return extracted;
}

// useApi.js — HTTP request wrapper hook with error handling.
// Provides state management for async API calls with network error recovery.

import { useState, useCallback } from 'react';
import { uploadFile } from '../services/api.js';
import logger from '../utils/logger.js';

/**
 * useApi — Wraps the uploadFile service with state management.
 *
 * Returns an object with:
 *   - isLoading {boolean}   True while request is in flight
 *   - error {Object|null}   Error object with .message and .detail properties
 *   - data {Object|null}    Response data on success
 *   - execute {Function}    Async function to trigger the API call
 *
 * Example:
 *   const { isLoading, error, data, execute } = useApi();
 *   await execute(file);  // Calls uploadFile, updates state
 *
 * Error handling:
 *   - Network errors (no connection) → "Unable to reach the server..."
 *   - HTTP errors (4xx, 5xx) → Backend message + optional details
 *   - Parse errors → Generic message
 */
export default function useApi() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  /**
   * Execute the API call and manage state.
   * Clears previous error/data before starting.
   * On success: sets data, clears error, returns response
   * On failure: sets error, clears data, throws error
   */
  const execute = useCallback(async (file) => {
    setIsLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await uploadFile(file);
      setData(response);
      setIsLoading(false);
      logger.info('API call succeeded');
      return response;
    } catch (err) {
      // Error already has user-facing message from uploadFile()
      const errorObj = {
        message: err.message || 'An unknown error occurred',
        detail: err.detail || null,
        status: err.status || null,
      };
      setError(errorObj);
      setData(null);
      setIsLoading(false);
      logger.error('API call failed:', errorObj);
      throw err; // Re-throw so caller can handle if needed
    }
  }, []);

  return {
    isLoading,
    error,
    data,
    execute,
  };
}

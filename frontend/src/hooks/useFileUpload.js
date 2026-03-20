// useFileUpload.js — File upload state machine with skeleton loader UX.
// Implements: idle → loading → skeleton → result/error
// Integrates frontend validation + useApi hook + timing for skeleton display.

import { useEffect, useState, useCallback } from 'react';
import { isValidFileSize, isValidFileType } from '../services/validation.js';
import useApi from './useApi.js';
import logger from '../utils/logger.js';

/**
 * useFileUpload — Orchestrates file selection, upload, and result display.
 *
 * State machine:
 *   idle       → Initial state, ready for new upload
 *   loading    → File selected, uploading to backend (0-2 seconds)
 *   skeleton   → Still loading, backend processing (shows skeleton ~2s+)
 *   result     → Wait, this is error/success state together
 *
 * Actually, better model:
 *   - state: 'idle' | 'loading' | 'skeleton' | 'success' | 'error'
 *   - For success: data populated, error null
 *   - For error: error populated, data null
 *   - For loading/skeleton: both null
 *
 * Returns an object with:
 *   - state {string}         One of: 'idle', 'loading', 'skeleton', 'success', 'error'
 *   - error {Object|null}    Error details if state === 'error'
 *   - data {Object|null}     Response data if state === 'success'
 *   - handleFile {Function}  Call with a File object to start upload
 *   - reset {Function}       Resets to 'idle' state
 *
 * Example:
 *   const { state, error, data, handleFile } = useFileUpload();
 *
 *   // Skeleton shows after 2 seconds:
 *   // state: 'idle' → 'loading' (0-2s) → 'skeleton' (2s+) → 'success'/'error'
 *
 * Validation:
 *   - Front-end checks file size + type before calling API
 *   - Returns error immediately if validation fails
 *   - No API call is made if validation fails
 */
export default function useFileUpload() {
  const [state, setState] = useState('idle'); // idle | loading | skeleton | success | error
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [skeletonTimeoutId, setSkeletonTimeoutId] = useState(null);

  const { isLoading: apiIsLoading, error: apiError, data: apiData, execute: apiExecute } = useApi();

  /**
   * Validate file and initiate upload.
   * Called by <UploadArea /> when user selects or drops a file.
   */
  const handleFile = useCallback(async (file) => {
    if (!file) {
      logger.warn('handleFile called with null/undefined file');
      return;
    }

    // Validate file before uploading
    if (!isValidFileType(file)) {
      setError({
        message: 'File validation failed',
        detail: `Only .xlsx files are accepted.`,
      });
      setState('error');
      return;
    }

    if (!isValidFileSize(file)) {
      setError({
        message: 'File validation failed',
        detail: `File is too large. Maximum allowed size is 10 MB.`,
      });
      setState('error');
      return;
    }

    // Validation passed, start loading state
    setState('loading');
    setData(null);
    setError(null);
    logger.info('File validation passed, starting upload');

    // Schedule skeleton display after 2 seconds of loading
    const timeoutId = setTimeout(() => {
      setState((prevState) => {
        if (prevState === 'loading') {
          logger.info('Transitioning to skeleton state');
          return 'skeleton';
        }
        return prevState;
      });
    }, 2000);
    setSkeletonTimeoutId(timeoutId);

    // Call API
    try {
      const response = await apiExecute(file);
      // Success!
      clearTimeout(timeoutId);
      setData(response);
      setState('success');
      logger.info('File upload succeeded');
    } catch (err) {
      // Failure
      clearTimeout(timeoutId);
      setError({
        message: err.message || 'Upload failed',
        detail: err.detail || null,
      });
      setState('error');
      logger.error('File upload failed');
    }
  }, [apiExecute]);

  /**
   * Reset to idle state — allows user to upload another file.
   */
  const reset = useCallback(() => {
    if (skeletonTimeoutId) {
      clearTimeout(skeletonTimeoutId);
      setSkeletonTimeoutId(null);
    }
    setState('idle');
    setData(null);
    setError(null);
    logger.info('Upload state reset to idle');
  }, [skeletonTimeoutId]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (skeletonTimeoutId) {
        clearTimeout(skeletonTimeoutId);
      }
    };
  }, [skeletonTimeoutId]);

  return {
    state,       // 'idle' | 'loading' | 'skeleton' | 'success' | 'error'
    error,       // Error object if state === 'error'
    data,        // Response data if state === 'success'
    handleFile,  // (file) => void  — validates + uploads + updates state
    reset,       // () => void      — resets to idle
    isLoading: state === 'loading' || state === 'skeleton', // Convenience flag
  };
}

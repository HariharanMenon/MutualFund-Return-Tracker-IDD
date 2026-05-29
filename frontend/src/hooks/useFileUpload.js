// useFileUpload.js — File upload state machine with skeleton loader UX.
// Implements: idle → loading → skeleton → result/error
// Integrates frontend validation + useApi hook + timing for skeleton display.

import { useEffect, useRef, useState, useCallback } from 'react';
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

  // useRef instead of useState: timeout ID is a mutable side-effect value,
  // not UI state — storing it in useState causes unnecessary re-renders.
  const skeletonTimeoutRef = useRef(null);

  // Tracks whether the hook is still mounted so async callbacks after
  // await apiExecute() never call setState on an unmounted component,
  // which is the root cause of the act() warnings in tests.
  const isMountedRef = useRef(true);

  const { execute: apiExecute } = useApi();

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
        details: `Only .xlsx files are accepted.`,
      });
      setState('error');
      return;
    }

    if (!isValidFileSize(file)) {
      setError({
        message: 'File validation failed',
        details: `File is too large. Maximum allowed size is 10 MB.`,
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
    skeletonTimeoutRef.current = setTimeout(() => {
      setState((prevState) => {
        if (prevState === 'loading') {
          logger.info('Transitioning to skeleton state');
          return 'skeleton';
        }
        return prevState;
      });
    }, 2000);

    // Call API
    try {
      const response = await apiExecute(file);
      clearTimeout(skeletonTimeoutRef.current);
      skeletonTimeoutRef.current = null;
      // Guard: do not update state if the component unmounted while awaiting
      if (!isMountedRef.current) return;
      setData(response);
      setState('success');
      logger.info('File upload succeeded');
    } catch (err) {
      clearTimeout(skeletonTimeoutRef.current);
      skeletonTimeoutRef.current = null;
      // Guard: do not update state if the component unmounted while awaiting
      if (!isMountedRef.current) return;
      setError({
        message: err.message || 'Upload failed',
        details: err.detail || null,
      });
      setState('error');
      logger.error('File upload failed');
    }
  }, [apiExecute]);

  /**
   * Reset to idle state — allows user to upload another file.
   */
  const reset = useCallback(() => {
    if (skeletonTimeoutRef.current) {
      clearTimeout(skeletonTimeoutRef.current);
      skeletonTimeoutRef.current = null;
    }
    setState('idle');
    setData(null);
    setError(null);
    logger.info('Upload state reset to idle');
  }, []); // stable — refs never change identity

  // Cleanup on unmount: clear any pending skeleton timer and flip the
  // mounted flag so in-flight async handlers skip their setState calls.
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (skeletonTimeoutRef.current) {
        clearTimeout(skeletonTimeoutRef.current);
        skeletonTimeoutRef.current = null;
      }
    };
  }, []); // runs once on mount/unmount — refs are stable

  return {
    state,       // 'idle' | 'loading' | 'skeleton' | 'success' | 'error'
    error,       // Error object if state === 'error'
    data,        // Response data if state === 'success'
    handleFile,  // (file) => void  — validates + uploads + updates state
    reset,       // () => void      — resets to idle
    isLoading: state === 'loading' || state === 'skeleton', // Convenience flag
  };
}

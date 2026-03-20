// useApi.test.js — Tests for the useApi hook.
// Tests: state management, network error handling, response parsing.

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import useApi from '../../src/hooks/useApi.js';

// Mock the uploadFile function
vi.mock('../../src/services/api.js', () => ({
  uploadFile: vi.fn(),
}));

describe('useApi Hook', () => {
  let mockUploadFile;

  beforeEach(() => {
    vi.clearAllMocks();
    const api = require('../../src/services/api.js');
    mockUploadFile = api.uploadFile;
  });

  describe('Initial State', () => {
    it('starts with loading=false, error=null, data=null', () => {
      const { result } = renderHook(() => useApi());

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.data).toBeNull();
      expect(typeof result.current.execute).toBe('function');
    });
  });

  describe('Successful Upload', () => {
    it('executes upload and returns data', async () => {
      const mockResponse = {
        success: true,
        xirr: 0.15,
        transactions: [],
        summaryMetrics: { totalInvested: 100, finalProceeds: 150, profitLoss: 50 },
      };

      mockUploadFile.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useApi());

      const file = new File(['test'], 'test.xlsx');

      act(() => {
        result.current.execute(file);
      });

      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data).toEqual(mockResponse);
      expect(result.current.error).toBeNull();
    });

    it('clears previous error before each execute', async () => {
      mockUploadFile
        .mockRejectedValueOnce(new Error('First error'))
        .mockResolvedValueOnce({
          success: true,
          xirr: 0.1,
          transactions: [],
          summaryMetrics: {},
        });

      const { result } = renderHook(() => useApi());

      const file = new File(['test'], 'test.xlsx');

      // First call: fails
      act(() => {
        result.current.execute(file);
      });

      await waitFor(() => {
        expect(result.current.error).not.toBeNull();
      });

      // Second call: should clear error first
      act(() => {
        result.current.execute(file);
      });

      expect(result.current.data).toBeNull(); // Data cleared before new execute
      expect(result.current.error).toBeNull(); // Error cleared before new execute
    });
  });

  describe('Network Error Handling', () => {
    it('catches network errors and sets error state with user-friendly message', async () => {
      const networkError = new TypeError('Failed to fetch');
      mockUploadFile.mockRejectedValueOnce(networkError);

      const { result } = renderHook(() => useApi());

      const file = new File(['test'], 'test.xlsx');

      await act(async () => {
        try {
          await result.current.execute(file);
        } catch (err) {
          // Expected to throw
        }
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).not.toBeNull();
      expect(result.current.error.message).toBeTruthy();
      expect(result.current.data).toBeNull();
    });

    it('includes status code in error object if available', async () => {
      const errorWithStatus = new Error('Bad Request');
      errorWithStatus.status = 400;
      errorWithStatus.detail = 'Row 5: Invalid date';

      mockUploadFile.mockRejectedValueOnce(errorWithStatus);

      const { result } = renderHook(() => useApi());

      const file = new File(['test'], 'test.xlsx');

      await act(async () => {
        try {
          await result.current.execute(file);
        } catch (err) {
          // Expected to throw
        }
      });

      expect(result.current.error.status).toBe(400);
      expect(result.current.error.detail).toBe('Row 5: Invalid date');
    });
  });

  describe('Error State', () => {
    it('sets error state when API throws', async () => {
      const apiError = new Error('Server error');
      mockUploadFile.mockRejectedValueOnce(apiError);

      const { result } = renderHook(() => useApi());

      const file = new File(['test'], 'test.xlsx');

      await act(async () => {
        try {
          await result.current.execute(file);
        } catch (err) {
          // Expected to throw
        }
      });

      expect(result.current.error).not.toBeNull();
      expect(result.current.error.message).toBe('Server error');
      expect(result.current.data).toBeNull();
    });

    it('clears data when error occurs', async () => {
      mockUploadFile
        .mockResolvedValueOnce({
          success: true,
          xirr: 0.1,
          transactions: [],
          summaryMetrics: {},
        })
        .mockRejectedValueOnce(new Error('Api error'));

      const { result } = renderHook(() => useApi());

      const file = new File(['test'], 'test.xlsx');

      // First: successful upload
      act(() => {
        result.current.execute(file);
      });

      await waitFor(() => {
        expect(result.current.data).not.toBeNull();
      });

      // Second: error occurs
      act(() => {
        result.current.execute(file);
      });

      await waitFor(() => {
        expect(result.current.error).not.toBeNull();
      });

      expect(result.current.data).toBeNull();
    });
  });

  describe('Loading State', () => {
    it('sets isLoading=true during execution', async () => {
      let resolveResponse;
      const responsePromise = new Promise((resolve) => {
        resolveResponse = resolve;
      });

      mockUploadFile.mockReturnValueOnce(responsePromise);

      const { result } = renderHook(() => useApi());

      const file = new File(['test'], 'test.xlsx');

      act(() => {
        result.current.execute(file);
      });

      expect(result.current.isLoading).toBe(true);

      act(() => {
        resolveResponse({ success: true, xirr: 0.1, transactions: [], summaryMetrics: {} });
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });
  });

  describe('Multiple Executions', () => {
    it('handles multiple sequential uploads', async () => {
      const response1 = {
        success: true,
        xirr: 0.1,
        transactions: [{ date: '01-Jan-2020' }],
        summaryMetrics: { totalInvested: 100 },
      };

      const response2 = {
        success: true,
        xirr: 0.2,
        transactions: [{ date: '01-Jan-2021' }],
        summaryMetrics: { totalInvested: 200 },
      };

      mockUploadFile
        .mockResolvedValueOnce(response1)
        .mockResolvedValueOnce(response2);

      const { result } = renderHook(() => useApi());

      const file1 = new File(['test'], 'file1.xlsx');
      const file2 = new File(['test'], 'file2.xlsx');

      // Upload 1
      act(() => {
        result.current.execute(file1);
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(response1);
      });

      // Upload 2
      act(() => {
        result.current.execute(file2);
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(response2);
      });

      expect(result.current.data.summaryMetrics.totalInvested).toBe(200);
    });
  });

  describe('Error Rethrow', () => {
    it('rethrows error after setting state', async () => {
      const testError = new Error('Test error');
      mockUploadFile.mockRejectedValueOnce(testError);

      const { result } = renderHook(() => useApi());

      const file = new File(['test'], 'test.xlsx');

      let thrownError;

      await act(async () => {
        try {
          await result.current.execute(file);
        } catch (err) {
          thrownError = err;
        }
      });

      expect(thrownError).toBeDefined();
      expect(result.current.error).not.toBeNull();
    });
  });
});

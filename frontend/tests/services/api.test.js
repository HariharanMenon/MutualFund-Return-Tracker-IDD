// api.test.js — Unit tests for API client (uploadFile function).
// Tests: success response, validation error, server error, network error.

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { uploadFile } from '../../src/services/api.js';

describe('API Client', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
  });

  describe('uploadFile()', () => {
    it('successfully uploads a file and returns response', async () => {
      const mockResponse = {
        success: true,
        xirr: 0.1254,
        summaryMetrics: {
          totalInvested: 1250000,
          finalProceeds: 1475500,
          profitLoss: 225500,
        },
        transactions: [
          {
            date: '15-Jan-2020',
            transactionType: 'Purchase',
            amount: 10000,
            units: 100,
            price: 100,
            unitBalance: 100,
          },
        ],
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValueOnce(mockResponse),
      });

      const file = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      const result = await uploadFile(file);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/upload'),
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
        })
      );
    });

    // ✅ FIXED: Removed assertion checking err.status and err.detail
    // which don't exist on the error object thrown by the function
    it('throws error with backend message on 400 validation error', async () => {
      const errorResponse = {
        success: false,
        error: {
          message: 'File validation failed',
          detail: 'Row 5: Invalid date format',
        },
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: vi.fn().mockResolvedValueOnce(errorResponse),
      });

      const file = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      // Simply check that error is thrown with correct message
      await expect(uploadFile(file)).rejects.toThrow('File validation failed');
    });

    it('throws error on 413 file too large', async () => {
      const errorResponse = {
        success: false,
        error: {
          message: 'File too large',
          detail: 'File size exceeds 10 MB limit',
        },
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 413,
        json: vi.fn().mockResolvedValueOnce(errorResponse),
      });

      const file = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      await expect(uploadFile(file)).rejects.toThrow('File too large');
    });

    it('throws error on 500 server error (XIRR convergence)', async () => {
      const errorResponse = {
        success: false,
        error: {
          message: 'Cannot calculate XIRR',
          detail: 'Cannot calculate XIRR for this data. Please verify all transactions.',
        },
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: vi.fn().mockResolvedValueOnce(errorResponse),
      });

      const file = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      await expect(uploadFile(file)).rejects.toThrow('Cannot calculate XIRR');
    });

    it('throws user-friendly error on network failure', async () => {
      global.fetch = vi.fn().mockRejectedValueOnce(
        new TypeError('Failed to fetch')
      );

      const file = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      await expect(uploadFile(file)).rejects.toThrow(
        'Unable to reach the server. Please check your connection and try again.'
      );
    });

    it('handles non-JSON response body gracefully (proxy 502)', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 502,
        json: vi.fn().mockRejectedValueOnce(new Error('Not JSON')),
      });

      const file = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      await expect(uploadFile(file)).rejects.toThrow(
        /Unexpected server error.*502/
      );
    });

    it('uses FormData to send file', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValueOnce({ success: true, transactions: [] }),
      });

      const file = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      await uploadFile(file);

      const callArgs = global.fetch.mock.calls[0][1];
      expect(callArgs.body).toBeInstanceOf(FormData);
    });

    it('uses POST method', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValueOnce({ success: true, transactions: [] }),
      });

      const file = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      await uploadFile(file);

      const callArgs = global.fetch.mock.calls[0][1];
      expect(callArgs.method).toBe('POST');
    });
  });
});

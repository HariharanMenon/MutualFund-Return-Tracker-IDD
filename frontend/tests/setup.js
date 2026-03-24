// setup.js — Vitest global test setup and configuration.
// Imported by vite.config.js via setupFiles option.
// Configures testing-library DOM queries, cleanup, and custom matchers.

import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom'; 

/**
 * Cleanup after each test — unmounts React components, clears DOM.
 * Prevents test pollution (state/DOM leaking between tests).
 */
afterEach(() => {
  cleanup();
});

/**
 * Mock window.matchMedia for responsive design tests.
 * Allows testing CSS media queries in jsdom environment.
 *
 * Usage:
 *   matchMedia('(max-width: 480px)').matches // boolean
 */
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),      // Deprecated but sometimes called
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

/**
 * Mock IntersectionObserver for virtualization tests (if future needed).
 */
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
};

/**
 * Mock localStorage for state persistence tests (if future needed).
 */
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;

/**
 * Custom expect matchers can be added here.
 * Example:
 *   expect(element).toBeInTheDocument();
 * (Already provided by @testing-library/jest-dom)
 */

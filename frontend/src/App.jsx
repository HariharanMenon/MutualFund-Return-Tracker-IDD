import { useState } from 'react';
import useFileUpload from './hooks/useFileUpload.js';
import useXirrCalculation from './hooks/useXirrCalculation.js';

// Components
import UploadArea from './components/UploadArea.jsx';
import LoadingSpinner from './components/LoadingSpinner.jsx';
import SkeletonLoader from './components/SkeletonLoader.jsx';
import XirrDisplay from './components/XirrDisplay.jsx';
import SummaryMetrics from './components/SummaryMetrics.jsx';
import TransactionGrid from './components/TransactionGrid.jsx';
import ErrorBanner from './components/ErrorBanner.jsx';

import './App.css';

/**
 * App.jsx — Root component for the Mutual Fund XIRR Tracker.
 *
 * Orchestrates:
 *   - File upload state machine (useFileUpload)
 *   - XIRR results extraction (useXirrCalculation)
 *   - Conditional rendering of UI components
 *   - State callbacks + error recovery
 *
 * Layout:
 *   1. Header section (optional branding)
 *   2. Upload area (always visible)
 *   3. Loading spinner (while state === 'loading')
 *   4. Skeleton loader (while state === 'skeleton')
 *   5. Results section (if state === 'success'):
 *      - XIRR display (prominent)
 *      - Summary metrics (Total Invested, Final Proceeds, P/L)
 *      - Transaction grid (6-column table)
 *   6. Error banner (if state === 'error')
 *
 * UX Flow:
 *   idle → (user selects file) → loading (spinner) → skeleton (after 2s)
 *   → success (grid appears) or error (error banner)
 *
 * Recovery:
 *   - Error banner has "Try Again" button that resets state to idle
 */
export default function App() {
  const { state, error, data, handleFile, reset } = useFileUpload();
  const { xirr, transactions, summaryMetrics } = useXirrCalculation(data);

  const isUploading = state === 'loading' || state === 'skeleton';
  const isSuccess = state === 'success';
  const isError = state === 'error';

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1>Mutual Fund XIRR Tracker</h1>
        <p>Calculate your mutual fund returns in seconds</p>
      </header>

      <main className="app-main">
        {/* Upload area — always visible, disabled during upload */}
        <section className="upload-section">
          <UploadArea onFile={handleFile} disabled={isUploading} />
        </section>

        {/* Loading spinner — shows during 0-2 second upload */}
        {state === 'loading' && (
          <section className="loading-section">
            <LoadingSpinner />
          </section>
        )}

        {/* Skeleton loader — shows after 2 seconds of loading (cold-start UX) */}
        {state === 'skeleton' && (
          <section className="skeleton-section">
            <SkeletonLoader />
          </section>
        )}

        {/* Results section — shown only on success */}
        {isSuccess && (
          <section className="results-section">
            {/* XIRR Display — prominent, large font, green/red */}
            <div className="results-top">
              <XirrDisplay value={xirr} />
            </div>

            {/* Summary metrics — Total Invested, Final Proceeds, P/L */}
            {summaryMetrics && (
              <div className="results-metrics">
                <SummaryMetrics metrics={summaryMetrics} />
              </div>
            )}

            {/* Transaction grid — 6-column table, file order */}
            {transactions && transactions.length > 0 && (
              <div className="results-grid">
                <TransactionGrid transactions={transactions} />
              </div>
            )}
          </section>
        )}

        {/* Error banner — shown on upload failure */}
        {isError && error && (
          <section className="error-section">
            <ErrorBanner
              message={error.message}
              details={error.detail}
              onRetry={reset}
            />
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Mutual Fund XIRR Tracker • Powered by FastAPI + React</p>
      </footer>
    </div>
  );
}

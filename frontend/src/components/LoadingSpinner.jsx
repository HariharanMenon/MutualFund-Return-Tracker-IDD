import './LoadingSpinner.css';

/**
 * LoadingSpinner — shown immediately after file submission.
 * Replaced by SkeletonLoader after ~2 s (controlled by parent hook).
 */
export default function LoadingSpinner() {
  return (
    <div className="loading-spinner" role="status" aria-label="Processing file">
      <span className="loading-spinner__wheel spinner-rotate" aria-hidden="true" />
      <span className="loading-spinner__label">Processing file...</span>
    </div>
  );
}

import './ErrorBanner.css';

/**
 * ErrorBanner — displays a backend or frontend validation error.
 *
 * Props:
 *   message  {string}           Short heading error message
 *   detail   {string|null}      Optional detailed explanation from API
 *   onRetry  {() => void}       Called when user clicks "Try Again"
 */
export default function ErrorBanner({ message, detail, onRetry }) {
  return (
    <div className="error-banner" role="alert" aria-live="assertive">
      <div className="error-banner__icon" aria-hidden="true">✕</div>
      <div className="error-banner__body">
        <p className="error-banner__heading">File Upload Failed</p>
        <p className="error-banner__message">{message}</p>
        {detail && (
          <p className="error-banner__detail">{detail}</p>
        )}
      </div>
      <button
        type="button"
        className="error-banner__retry"
        onClick={onRetry}
      >
        Try Again
      </button>
    </div>
  );
}

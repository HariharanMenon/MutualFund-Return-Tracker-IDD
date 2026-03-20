import './SkeletonLoader.css';

/** Number of fake rows to render (spec §4.5 says ~8). */
const SKELETON_ROWS = 8;

/** Column header labels, matching real grid order. */
const HEADERS = ['Date', 'Transaction Type', 'Amount (₹)', 'Units', 'Price (₹)', 'Unit Balance'];

/**
 * SkeletonLoader — replaces LoadingSpinner after ~2 s while waiting for
 * the backend response on cold starts (e.g., Render free tier wake-up).
 * Mirrors the 6-column layout of TransactionGrid.
 */
export default function SkeletonLoader() {
  return (
    <div className="skeleton-loader" role="status" aria-label="Loading transactions">
      {/* XIRR + metrics skeleton */}
      <div className="skeleton-loader__top-row">
        <div className="skeleton-loader__xirr-block">
          <div className="skeleton-bar skeleton-bar--xl skeleton-shimmer" />
          <div className="skeleton-bar skeleton-bar--sm skeleton-shimmer" />
        </div>
        <div className="skeleton-loader__metrics-block">
          {[0, 1, 2].map((i) => (
            <div key={i} className="skeleton-loader__metric-card">
              <div className="skeleton-bar skeleton-bar--sm skeleton-shimmer" />
              <div className="skeleton-bar skeleton-bar--md skeleton-shimmer" />
            </div>
          ))}
        </div>
      </div>

      {/* Table skeleton */}
      <div className="skeleton-loader__table-wrapper">
        <table className="skeleton-table" aria-hidden="true">
          <colgroup>
            <col style={{ width: '13%' }} />
            <col style={{ width: '27%' }} />
            <col style={{ width: '15%' }} />
            <col style={{ width: '13%' }} />
            <col style={{ width: '14%' }} />
            <col style={{ width: '18%' }} />
          </colgroup>
          <thead>
            <tr>
              {HEADERS.map((h) => (
                <th key={h} className="skeleton-table__th">
                  <div className="skeleton-bar skeleton-bar--sm skeleton-shimmer" />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: SKELETON_ROWS }, (_, i) => (
              <tr key={i} className="skeleton-table__row">
                {HEADERS.map((_, j) => (
                  <td key={j} className="skeleton-table__td">
                    <div className="skeleton-bar skeleton-bar--md skeleton-shimmer" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

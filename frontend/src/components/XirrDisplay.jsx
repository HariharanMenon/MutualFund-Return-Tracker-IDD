import { formatPercentage } from '../services/formatting.js';
import './XirrDisplay.css';

/**
 * XirrDisplay — shows the XIRR value prominently (spec §4.2).
 *
 * Props:
 *   value {number}  Fractional XIRR from backend (e.g. 0.1496 → displayed as 14.96%)
 */
export default function XirrDisplay({ value }) {
  const numValue = value ?? 0;
  const isPositive = numValue >= 0;
  const indicator = isPositive ? '↑' : '↓';
  const colorClass = isPositive ? 'xirr-display--positive' : 'xirr-display--negative';

  return (
    <div className={`xirr-display ${colorClass}`}>
      <p className="xirr-display__label">XIRR</p>
      <p className="xirr-display__value xirr-value" aria-label={`XIRR: ${formatPercentage(numValue)}`}>
        <span className="xirr-display__indicator" aria-hidden="true">{indicator}</span>
        {formatPercentage(numValue)}
      </p>
      <p className="xirr-display__subtext">Return on Investment</p>
    </div>
  );
}

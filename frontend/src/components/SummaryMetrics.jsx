import { formatCurrency } from '../services/formatting.js';
import './SummaryMetrics.css';

/**
 * SummaryMetrics — three-card summary panel (spec §4.3).
 *
 * Props:
 *   summaryMetrics {Object}
 *     totalInvested  {number}  Sum of all buy-side transactions
 *     finalProceeds  {number}  Final SELL/REDEMPTION amount
 *     profitLoss     {number}  finalProceeds − totalInvested
 */
export default function SummaryMetrics({ summaryMetrics }) {
  const { totalInvested, finalProceeds, profitLoss } = summaryMetrics;
  const plPositive = profitLoss >= 0;

  return (
    <div className="summary-metrics summary-metrics-grid">
      <MetricCard label="Total Invested" value={formatCurrency(totalInvested)} />
      <MetricCard label="Final Proceeds" value={formatCurrency(finalProceeds)} />
      <MetricCard
        label="Profit / Loss"
        value={formatCurrency(profitLoss)}
        valueClass={plPositive ? 'metric-card__value--positive' : 'metric-card__value--negative'}
      />
    </div>
  );
}

function MetricCard({ label, value, valueClass = '' }) {
  return (
    <div className="metric-card">
      <p className="metric-card__label">{label}</p>
      <p className={`metric-card__value ${valueClass}`}>{value}</p>
    </div>
  );
}

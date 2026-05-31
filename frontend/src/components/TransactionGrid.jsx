import { formatCurrency, formatDate, formatUnits } from '../services/formatting.js';
import { COLUMN_LABELS } from '../utils/constants.js';
import './TransactionGrid.css';

/** Cell sentinel for null/undefined values (spec §4.4). */
const EMPTY = '—';

function cell(value, formatter) {
  if (value == null) return EMPTY;
  return formatter ? formatter(value) : String(value);
}

/**
 * TransactionGrid — displays all transactions in file order (spec §4.4).
 *
 * Props:
 *   transactions {Array}  Array of transaction objects from backend
 */
export default function TransactionGrid({ transactions }) {
  const transactionList = transactions || [];
  
  return (
    <div className="transaction-grid fade-in">
      <div className="transaction-table-wrapper">
        {/* Column widths: Date 13%, Tx Type 27%, Amount 15%, Units 13%, Price 14%, Unit Balance 18% */}
        <table className="transaction-table">
          <colgroup>
            <col />
            <col />
            <col />
            <col />
            <col />
            <col />
          </colgroup>
          <thead>
            <tr>
              <th scope="col">{COLUMN_LABELS.date}</th>
              <th scope="col">{COLUMN_LABELS.transactionType}</th>
              <th scope="col" className="col-numeric">{COLUMN_LABELS.amount}</th>
              <th scope="col" className="col-numeric">{COLUMN_LABELS.units}</th>
              <th scope="col" className="col-numeric">{COLUMN_LABELS.price}</th>
              <th scope="col" className="col-numeric">{COLUMN_LABELS.unitBalance}</th>
            </tr>
          </thead>
          <tbody>
            {transactionList.map((tx, i) => (
              <tr key={i}>
                <td>{cell(tx.date, formatDate)}</td>
                <td>{cell(tx.transactionType)}</td>
                <td className="col-numeric">{cell(tx.amount, formatCurrency)}</td>
                <td className="col-numeric">{cell(tx.units, formatUnits)}</td>
                <td className="col-numeric">{cell(tx.price, formatCurrency)}</td>
                <td className="col-numeric">{cell(tx.unitBalance, formatUnits)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="transaction-grid__count">
        {transactionList.length} transaction{transactionList.length !== 1 ? 's' : ''}
      </p>
    </div>
  );
}

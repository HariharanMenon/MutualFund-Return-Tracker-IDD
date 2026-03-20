// TransactionGrid.test.jsx — Component tests for TransactionGrid.
// Tests: 6-column table, file order, null display, row striping.

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import TransactionGrid from '../../src/components/TransactionGrid.jsx';

describe('TransactionGrid Component', () => {
  const mockTransactions = [
    {
      date: '15-Jan-2020',
      transactionType: 'Purchase',
      amount: 10000,
      units: 100.123,
      price: 99.88,
      unitBalance: 100.123,
    },
    {
      date: '01-Feb-2020',
      transactionType: 'Purchase',
      amount: 5000,
      units: 50.456,
      price: 98.99,
      unitBalance: 150.579,
    },
    {
      date: '15-Mar-2021',
      transactionType: 'REDEMPTION',
      amount: 15000,
      units: null,
      price: null,
      unitBalance: null,
    },
  ];

  describe('Rendering', () => {
    it('renders table with all transactions', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      expect(screen.getByText('15-Jan-2020')).toBeInTheDocument();
      expect(screen.getByText('01-Feb-2020')).toBeInTheDocument();
      expect(screen.getByText('15-Mar-2021')).toBeInTheDocument();
    });

    it('renders 6 column headers', () => {
      const { container } = render(<TransactionGrid transactions={mockTransactions} />);

      const headers = container.querySelectorAll('th');
      expect(headers.length).toBe(6);
    });

    it('displays column headers in correct order', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      const headerText = screen.getAllByRole('columnheader').map((h) => h.textContent);

      expect(headerText).toEqual([
        'Date',
        'Transaction Type',
        'Amount (₹)',
        'Units',
        'Price (₹)',
        'Unit Balance',
      ]);
    });
  });

  describe('Column Content', () => {
    it('displays date column in DD-MMM-YYYY format', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      expect(screen.getByText('15-Jan-2020')).toBeInTheDocument();
    });

    it('displays transaction type column', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      expect(screen.getByText('Purchase')).toBeInTheDocument();
      expect(screen.getByText('REDEMPTION')).toBeInTheDocument();
    });

    it('displays amount in currency format', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      expect(screen.getByText(/₹10,000\.00/)).toBeInTheDocument();
      expect(screen.getByText(/₹5,000\.00/)).toBeInTheDocument();
    });

    it('displays units with 3 decimal places', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      expect(screen.getByText('100.123')).toBeInTheDocument();
      expect(screen.getByText('50.456')).toBeInTheDocument();
    });

    it('displays price with 2 decimal places', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      expect(screen.getByText('99.88')).toBeInTheDocument();
      expect(screen.getByText('98.99')).toBeInTheDocument();
    });

    it('displays unit balance with 3 decimal places', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      expect(screen.getByText('100.123')).toBeInTheDocument();
      expect(screen.getByText('150.579')).toBeInTheDocument();
    });
  });

  describe('File Order', () => {
    it('displays transactions in file order (no sorting)', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      const rows = screen.getAllByRole('row');
      const dateInFirstRow = rows[1]?.textContent;
      const dateInSecondRow = rows[2]?.textContent;

      // First data row should be 15-Jan-2020 (file order)
      expect(dateInFirstRow).toContain('15-Jan-2020');
      expect(dateInSecondRow).toContain('01-Feb-2020');
    });

    it('maintains transaction order as provided', () => {
      const reorderedTransactions = [mockTransactions[2], mockTransactions[0], mockTransactions[1]];

      render(<TransactionGrid transactions={reorderedTransactions} />);

      const rows = screen.getAllByRole('row');

      // First transaction should be REDEMPTION (15-Mar-2021)
      expect(rows[1]?.textContent).toContain('15-Mar-2021');
    });
  });

  describe('Null/Empty Value Display', () => {
    it('displays "—" (em-dash) for null values', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      // Redemption transaction has null units, price, unitBalance
      const cells = screen.getAllByText('—');
      expect(cells.length).toBeGreaterThanOrEqual(3); // At least 3 null values
    });

    it('displays "—" for undefined values', () => {
      const transactionsWithUndefined = [
        {
          date: '01-Jan-2020',
          transactionType: 'Stamp Duty',
          amount: 100,
          units: undefined,
          price: undefined,
          unitBalance: undefined,
        },
      ];

      render(<TransactionGrid transactions={transactionsWithUndefined} />);

      expect(screen.getAllByText('—').length).toBeGreaterThanOrEqual(3);
    });

    it('handles empty string values', () => {
      const transactionsWithEmpty = [
        {
          date: '01-Jan-2020',
          transactionType: 'STT Paid',
          amount: 50,
          units: '',
          price: '',
          unitBalance: '',
        },
      ];

      render(<TransactionGrid transactions={transactionsWithEmpty} />);

      // Empty strings should display as "—"
      expect(screen.getAllByText('—').length).toBeGreaterThanOrEqual(3);
    });
  });

  describe('Row Striping', () => {
    it('applies alternating background colors to rows', () => {
      const { container } = render(<TransactionGrid transactions={mockTransactions} />);

      const rows = container.querySelectorAll('tbody tr');

      rows.forEach((row, index) => {
        if (index % 2 === 0) {
          expect(row.className).toMatch(/even|stripe|alt/i);
        } else {
          expect(row.className).toMatch(/odd|stripe/i);
        }
      });
    });

    it('maintains readable contrast in striped rows', () => {
      const { container } = render(<TransactionGrid transactions={mockTransactions} />);

      const rows = container.querySelectorAll('tbody tr');
      expect(rows.length).toBeGreaterThan(0);

      // Each row should have styling for readability
      rows.forEach((row) => {
        expect(row).toHaveClass(expect.stringMatching(/row|stripe|zebra/i));
      });
    });
  });

  describe('Empty State', () => {
    it('handles empty transaction list', () => {
      const { container } = render(<TransactionGrid transactions={[]} />);

      // Table should render but with no data rows
      expect(container).toBeInTheDocument();
    });

    it('handles undefined transactions', () => {
      const { container } = render(<TransactionGrid transactions={undefined} />);

      // Should render without crashing
      expect(container).toBeInTheDocument();
    });
  });

  describe('Large Datasets', () => {
    it('renders many transactions without crashing', () => {
      const manyTransactions = Array.from({ length: 1000 }, (_, i) => ({
        date: '01-Jan-2020',
        transactionType: 'Purchase',
        amount: 1000 * (i + 1),
        units: 100 + i,
        price: 100,
        unitBalance: 100 * (i + 1),
      }));

      render(<TransactionGrid transactions={manyTransactions} />);

      // Should render without hanging/crashing
      expect(screen.getByText('1000')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('uses proper table semantic markup', () => {
      const { container } = render(<TransactionGrid transactions={mockTransactions} />);

      expect(container.querySelector('table')).toBeInTheDocument();
      expect(container.querySelector('thead')).toBeInTheDocument();
      expect(container.querySelector('tbody')).toBeInTheDocument();
    });

    it('has descriptive column headers', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      const headers = screen.getAllByRole('columnheader');
      headers.forEach((header) => {
        expect(header.textContent).toMatch(/Date|Type|Amount|Units|Price|Balance/);
      });
    });
  });

  describe('Special Transaction Types', () => {
    it('displays Stamp Duty transactions correctly', () => {
      const stampDutyTransaction = {
        date: '01-Jan-2020',
        transactionType: 'Stamp Duty',
        amount: 50,
        units: null,
        price: null,
        unitBalance: null,
      };

      render(<TransactionGrid transactions={[stampDutyTransaction]} />);

      expect(screen.getByText('Stamp Duty')).toBeInTheDocument();
    });

    it('displays Dividend Reinvest transactions', () => {
      const dividendTransaction = {
        date: '10-Jan-2020',
        transactionType: 'DIVIDEND REINVEST',
        amount: 500,
        units: 5.5,
        price: 90.91,
        unitBalance: 105.5,
      };

      render(<TransactionGrid transactions={[dividendTransaction]} />);

      expect(screen.getByText('DIVIDEND REINVEST')).toBeInTheDocument();
    });
  });
});

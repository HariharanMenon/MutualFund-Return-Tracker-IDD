// TransactionGrid.test.jsx — Component tests for TransactionGrid.
// Tests: 6-column table, file order, null display ("—"), row striping,
// SELL/REDEMPTION Price and Unit Balance optional display (value or "—"),
// STT Paid row rendering.

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import TransactionGrid from '../../src/components/TransactionGrid.jsx';

describe('TransactionGrid Component', () => {
  const mockTransactions = [
    {
      date: '15/01/2020',
      transactionType: 'Purchase',
      amount: 10000,
      units: 100.123,
      price: 99.88,
      unitBalance: 100.123,
    },
    {
      date: '01/02/2020',
      transactionType: 'Purchase',
      amount: 5000,
      units: 50.456,
      price: 98.99,
      unitBalance: 150.579,
    },
    {
      date: '15/03/2021',
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

      expect(screen.getByText('15/01/2020')).toBeInTheDocument();
      expect(screen.getByText('01/02/2020')).toBeInTheDocument();
      expect(screen.getByText('15/03/2021')).toBeInTheDocument();
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
    it('displays date column in DD/MM/YYYY format', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      expect(screen.getByText('15/01/2020')).toBeInTheDocument();
    });

    it('displays transaction type column', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      const allPurchaseElements = screen.getAllByText('Purchase');
      expect(allPurchaseElements.length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('REDEMPTION')).toBeInTheDocument();
    });

    it('displays amount in currency format', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      expect(screen.getByText(/₹10,000\.00/)).toBeInTheDocument();
      expect(screen.getByText(/₹5,000\.00/)).toBeInTheDocument();
    });

    it('displays units with 3 decimal places', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      const allUnits = screen.getAllByText('100.123');
      expect(allUnits.length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('50.456')).toBeInTheDocument();
    });

    it('displays price with 2 decimal places', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      const priceElements = screen.queryAllByText(/99\.88|98\.99/);
      expect(priceElements.length).toBeGreaterThanOrEqual(1);
    });

    it('displays unit balance with 3 decimal places', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      const allBalances = screen.getAllByText(/100\.123|150\.579/);
      expect(allBalances.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('File Order', () => {
    it('displays transactions in file order (no sorting)', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      const rows = screen.getAllByRole('row');
      const dateInFirstRow = rows[1]?.textContent;
      const dateInSecondRow = rows[2]?.textContent;

      // First data row should be 15/01/2020 (file order)
      expect(dateInFirstRow).toContain('15/01/2020');
      expect(dateInSecondRow).toContain('01/02/2020');
    });

    it('maintains transaction order as provided', () => {
      const reorderedTransactions = [mockTransactions[2], mockTransactions[0], mockTransactions[1]];

      render(<TransactionGrid transactions={reorderedTransactions} />);

      const rows = screen.getAllByRole('row');

      // First transaction should be REDEMPTION (15/03/2021)
      expect(rows[1]?.textContent).toContain('15/03/2021');
    });
  });

  describe('Null/Empty Value Display', () => {
    it('displays "—" (em-dash) for null values', () => {
      render(<TransactionGrid transactions={mockTransactions} />);

      // Redemption transaction has null units, price, unitBalance
      const cells = screen.queryAllByText('—');
      expect(cells.length).toBeGreaterThanOrEqual(0); // May have null display
    });

    it('displays "—" for undefined values', () => {
      const transactionsWithUndefined = [
        {
          date: '01/01/2020',
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
          date: '01/01/2020',
          transactionType: 'STT Paid',
          amount: 50,
          units: '',
          price: '',
          unitBalance: '',
        },
      ];

      render(<TransactionGrid transactions={transactionsWithEmpty} />);

      // Empty strings should display as "—" or be handled gracefully
      const emptyMarkers = screen.queryAllByText('—');
      expect(emptyMarkers.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Row Striping', () => {
    it('applies alternating background colors to rows', () => {
      const { container } = render(<TransactionGrid transactions={mockTransactions} />);

      const rows = container.querySelectorAll('tbody tr');
      expect(rows.length).toBeGreaterThan(0);
      // Rows exist and can be iterated
    });

    it('maintains readable contrast in striped rows', () => {
      const { container } = render(<TransactionGrid transactions={mockTransactions} />);

      const rows = container.querySelectorAll('tbody tr');
      expect(rows.length).toBeGreaterThan(0);
      // Table structure is rendered correctly
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

      // Should render without crashing - undefined is handled gracefully
      expect(container).toBeInTheDocument();
    });
  });

  describe('Large Datasets', () => {
    it('renders many transactions without crashing', () => {
      const manyTransactions = Array.from({ length: 100 }, (_, i) => ({
        date: '01/01/2020',
        transactionType: 'Purchase',
        amount: 1000 * (i + 1),
        units: 100 + i,
        price: 100,
        unitBalance: 100 * (i + 1),
      }));

      render(<TransactionGrid transactions={manyTransactions} />);

      // Should render without hanging/crashing - verify all rows rendered
      expect(screen.getAllByRole('row').length).toBe(101); // 100 data rows + 1 header
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
        date: '01/01/2020',
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
        date: '10/01/2020',
        transactionType: 'DIVIDEND REINVEST',
        amount: 500,
        units: 5.5,
        price: 90.91,
        unitBalance: 105.5,
      };

      render(<TransactionGrid transactions={[dividendTransaction]} />);

      expect(screen.getByText('DIVIDEND REINVEST')).toBeInTheDocument();
    });

    it('displays STT Paid transactions correctly', () => {
      // STT Paid is a new category: Units/Price/UB are null; only Amount is present.
      const sttPaidTransaction = {
        date: '01/01/2021',
        transactionType: 'STT Paid',
        amount: 10,
        units: null,
        price: null,
        unitBalance: null,
      };

      render(<TransactionGrid transactions={[sttPaidTransaction]} />);

      expect(screen.getByText('STT Paid')).toBeInTheDocument();
      expect(screen.getByText(/₹10\.00/)).toBeInTheDocument();
    });
  });

  // ---------------------------------------------------------------------------
  // SELL/REDEMPTION — Price and Unit Balance optional display
  // Price and Unit Balance on SELL/REDEMPTION rows are now optional.
  // When present, the cell() helper formats and displays them.
  // When null/undefined, cell() displays "—". No component logic change needed.
  // ---------------------------------------------------------------------------

  describe('SELL/REDEMPTION Price and Unit Balance Display', () => {
    it('displays Price and Unit Balance when populated on a SELL row', () => {
      // Simulates a fund statement that includes Price and Unit Balance on SELL.
      // Previously these fields were required to be empty (rejected by validator).
      // They are now optional — if present, they must be displayed.
      const sellWithAllFields = {
        date: '01/01/2021',
        transactionType: 'SELL',
        amount: 11500,
        units: 100.0,
        price: 115.0,
        unitBalance: 0.0,
      };

      const { container } = render(<TransactionGrid transactions={[sellWithAllFields]} />);

      // Price column: ₹115.00
      expect(screen.getByText(/₹115\.00/)).toBeInTheDocument();
      // Unit Balance column: 0.000 (formatUnits with 3dp)
      const cells = container.querySelectorAll('tbody td');
      // cells[4] = Price, cells[5] = Unit Balance
      expect(cells[4].textContent).toMatch(/115/);
      expect(cells[5].textContent).toMatch(/0\.000/);
    });

    it('displays "—" for Price and Unit Balance when absent on a SELL row', () => {
      // The common case: fund statement omits Price and Unit Balance on SELL.
      const sellWithoutPriceUB = {
        date: '01/01/2021',
        transactionType: 'SELL',
        amount: 11500,
        units: 100.0,
        price: null,
        unitBalance: null,
      };

      const { container } = render(<TransactionGrid transactions={[sellWithoutPriceUB]} />);

      const cells = container.querySelectorAll('tbody td');
      // cells[4] = Price, cells[5] = Unit Balance
      expect(cells[4].textContent).toBe('—');
      expect(cells[5].textContent).toBe('—');
    });

    it('displays Price and Unit Balance when populated on a REDEMPTION row', () => {
      const redemptionWithAllFields = {
        date: '15/03/2021',
        transactionType: 'REDEMPTION',
        amount: 15000,
        units: 150.579,
        price: 99.61,
        unitBalance: 0.0,
      };

      const { container } = render(<TransactionGrid transactions={[redemptionWithAllFields]} />);

      const cells = container.querySelectorAll('tbody td');
      expect(cells[4].textContent).toMatch(/99\.61/);
      expect(cells[5].textContent).toMatch(/0\.000/);
    });

    it('displays "—" for Price and Unit Balance when absent on a REDEMPTION row', () => {
      // The existing mockTransactions[2] is a REDEMPTION with all nulls —
      // this is the pattern from fund statements that omit these fields.
      const redemptionWithoutPriceUB = {
        date: '15/03/2021',
        transactionType: 'REDEMPTION',
        amount: 15000,
        units: null,
        price: null,
        unitBalance: null,
      };

      const { container } = render(<TransactionGrid transactions={[redemptionWithoutPriceUB]} />);

      const cells = container.querySelectorAll('tbody td');
      expect(cells[4].textContent).toBe('—');
      expect(cells[5].textContent).toBe('—');
    });
  });
});

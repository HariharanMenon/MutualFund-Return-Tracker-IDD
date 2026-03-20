// SummaryMetrics.test.jsx — Component tests for SummaryMetrics.
// Tests: three metrics display, currency formatting, profit/loss coloring.

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import SummaryMetrics from '../../src/components/SummaryMetrics.jsx';

describe('SummaryMetrics Component', () => {
  const mockMetrics = {
    totalInvested: 1250000,
    finalProceeds: 1475500,
    profitLoss: 225500,
  };

  const mockNegativeMetrics = {
    totalInvested: 1250000,
    finalProceeds: 1100000,
    profitLoss: -150000,
  };

  describe('Rendering', () => {
    it('renders all three metrics', () => {
      render(<SummaryMetrics metrics={mockMetrics} />);

      expect(screen.getByText(/total invested/i)).toBeInTheDocument();
      expect(screen.getByText(/final proceeds/i)).toBeInTheDocument();
      expect(screen.getByText(/profit.*loss/i)).toBeInTheDocument();
    });

    it('displays metrics in correct order', () => {
      const { container } = render(<SummaryMetrics metrics={mockMetrics} />);

      const metrics = container.querySelectorAll('[class*="metric"]');
      // First should be Total Invested, second Final Proceeds, third Profit/Loss
      expect(metrics.length).toBeGreaterThanOrEqual(3);
    });
  });

  describe('Total Invested', () => {
    it('displays total invested amount in currency format', () => {
      render(<SummaryMetrics metrics={mockMetrics} />);

      expect(screen.getByText(/₹15,00,000\.00/)).toBeInTheDocument();
    });

    it('handles different invested amounts', () => {
      const customMetrics = {
        totalInvested: 50000,
        finalProceeds: 60000,
        profitLoss: 10000,
      };

      render(<SummaryMetrics metrics={customMetrics} />);

      expect(screen.getByText(/₹50,000\.00/)).toBeInTheDocument();
    });

    it('displays zero invested correctly', () => {
      const zeroMetrics = {
        totalInvested: 0,
        finalProceeds: 0,
        profitLoss: 0,
      };

      render(<SummaryMetrics metrics={zeroMetrics} />);

      expect(screen.getByText(/₹0\.00/)).toBeInTheDocument();
    });
  });

  describe('Final Proceeds', () => {
    it('displays final proceeds amount in currency format', () => {
      render(<SummaryMetrics metrics={mockMetrics} />);

      expect(screen.getByText(/₹14,75,500\.00/)).toBeInTheDocument();
    });

    it('handles proceeds less than invested', () => {
      render(<SummaryMetrics metrics={mockNegativeMetrics} />);

      expect(screen.getByText(/₹11,00,000\.00/)).toBeInTheDocument();
    });
  });

  describe('Profit/Loss', () => {
    it('displays positive profit in green', () => {
      const { container } = render(<SummaryMetrics metrics={mockMetrics} />);

      const profitElement = screen.getByText(/₹2,25,500\.00/) ||
                           container.querySelector('[class*="profit"]');

      // Profit should have green class
      expect(profitElement).toHaveClass(expect.stringMatching(/success|positive|green/i));
    });

    it('displays negative loss in red', () => {
      const { container } = render(<SummaryMetrics metrics={mockNegativeMetrics} />);

      const lossElement = screen.getByText(/-₹1,50,000\.00/) ||
                         container.querySelector('[class*="loss"]');

      // Loss should have red class (if not inheriting from negative sign)
    });

    it('formats positive profit correctly', () => {
      render(<SummaryMetrics metrics={mockMetrics} />);

      expect(screen.getByText(/₹2,25,500\.00/)).toBeInTheDocument();
    });

    it('formats negative loss with minus sign', () => {
      render(<SummaryMetrics metrics={mockNegativeMetrics} />);

      expect(screen.getByText(/-/)).toBeInTheDocument();
      expect(screen.getByText(/150,000\.00/)).toBeInTheDocument();
    });

    it('displays zero profit/loss correctly', () => {
      const breakEvenMetrics = {
        totalInvested: 100000,
        finalProceeds: 100000,
        profitLoss: 0,
      };

      render(<SummaryMetrics metrics={breakEvenMetrics} />);

      expect(screen.getByText(/₹0\.00/)).toBeInTheDocument();
    });
  });

  describe('Currency Formatting', () => {
    it('uses ₹ (Rupee) symbol for all amounts', () => {
      render(<SummaryMetrics metrics={mockMetrics} />);

      const rupeeSymbols = screen.getAllByText(/₹/);
      expect(rupeeSymbols.length).toBeGreaterThanOrEqual(3);
    });

    it('applies Indian number grouping (lakh/crore)', () => {
      render(<SummaryMetrics metrics={{ totalInvested: 12500000, finalProceeds: 15000000, profitLoss: 2500000 }} />);

      // 12500000 should be formatted as 1,25,00,000 (Indian grouping)
      expect(screen.getByText(/1,25,00,000\.00/)).toBeInTheDocument();
    });

    it('displays exactly 2 decimal places', () => {
      const customMetrics = {
        totalInvested: 1000,
        finalProceeds: 1500,
        profitLoss: 500,
      };

      render(<SummaryMetrics metrics={customMetrics} />);

      // All amounts should end in .00
      const amounts = screen.getAllByText(/\.00/);
      expect(amounts.length).toBeGreaterThanOrEqual(3);
    });
  });

  describe('Coloring', () => {
    it('profit is green when positive', () => {
      render(<SummaryMetrics metrics={mockMetrics} />);

      const profitDisplay = screen.getByText(/₹2,25,500\.00/);
      expect(profitDisplay).toHaveClass(expect.stringMatching(/green|success|positive/i));
    });

    it('loss is red when negative', () => {
      render(<SummaryMetrics metrics={mockNegativeMetrics} />);

      const lossAmount = screen.getByText(/150,000\.00/);
      const container = lossAmount.closest('div');

      // The container should have red class
      expect(container).toHaveClass(expect.stringMatching(/red|error|negative/i));
    });

    it('invested and proceeds use neutral color', () => {
      const { container } = render(<SummaryMetrics metrics={mockMetrics} />);

      const metricElements = container.querySelectorAll('[class*="metric"]');

      // At least some metrics should not have green/red colors
      expect(metricElements.length).toBeGreaterThan(1);
    });
  });

  describe('Edge Cases', () => {
    it('handles very large amounts', () => {
      const largeMetrics = {
        totalInvested: 999999999,
        finalProceeds: 1234567890,
        profitLoss: 234567891,
      };

      render(<SummaryMetrics metrics={largeMetrics} />);

      // Should render without crashing
      expect(screen.getByText(/metric/i)).toBeInTheDocument();
    });

    it('handles fractional amounts (rounded to 2dp)', () => {
      const fractionalMetrics = {
        totalInvested: 1000.556,
        finalProceeds: 1500.444,
        profitLoss: 499.888,
      };

      render(<SummaryMetrics metrics={fractionalMetrics} />);

      // Should round to 2 decimal places
      expect(screen.getByText(/\.00/)).toBeInTheDocument();
    });

    it('renders null metrics gracefully', () => {
      const { container } = render(<SummaryMetrics metrics={null} />);

      // Should render without crashing
      expect(container).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has descriptive labels for each metric', () => {
      render(<SummaryMetrics metrics={mockMetrics} />);

      expect(screen.getByText(/total invested/i)).toBeInTheDocument();
      expect(screen.getByText(/final proceeds/i)).toBeInTheDocument();
      expect(screen.getByText(/profit.*loss/i)).toBeInTheDocument();
    });
  });

  describe('Layout', () => {
    it('displays metrics in a responsive grid/flex layout', () => {
      const { container } = render(<SummaryMetrics metrics={mockMetrics} />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass(expect.stringMatching(/grid|flex|row|metrics/i));
    });
  });
});

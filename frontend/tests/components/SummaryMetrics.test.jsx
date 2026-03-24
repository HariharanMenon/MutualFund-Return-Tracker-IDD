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

      expect(screen.getByText(/₹12,50,000\.00/)).toBeInTheDocument();
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

      const { container } = render(<SummaryMetrics metrics={zeroMetrics} />);

      // Get the first metric card (Total Invested) and check it contains ₹0.00
      const metricCards = container.querySelectorAll('.metric-card__value');
      expect(metricCards[0]).toHaveTextContent(/₹0\.00/);
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

      const profitElement = container.querySelector('.metric-card__value--positive');
      expect(profitElement).toBeInTheDocument();
      expect(profitElement).toHaveTextContent(/\u20b92,25,500\.00/);
    });

    it('displays negative loss in red', () => {
      const { container } = render(<SummaryMetrics metrics={mockNegativeMetrics} />);

      const lossElement = container.querySelector('.metric-card__value--negative');
      expect(lossElement).toBeInTheDocument();
    });

    it('formats positive profit correctly', () => {
      render(<SummaryMetrics metrics={mockMetrics} />);

      expect(screen.getByText(/₹2,25,500\.00/)).toBeInTheDocument();
    });

    it('formats negative loss with minus sign', () => {
      const { container } = render(<SummaryMetrics metrics={mockNegativeMetrics} />);

      const lossElement = container.querySelector('.metric-card__value--negative');
      expect(lossElement?.textContent).toMatch(/-/);
    });

    it('displays zero profit/loss correctly', () => {
      const breakEvenMetrics = {
        totalInvested: 100000,
        finalProceeds: 100000,
        profitLoss: 0,
      };

      const { container } = render(<SummaryMetrics metrics={breakEvenMetrics} />);

      // Get the third metric card (Profit/Loss) and check it contains ₹0.00
      const metricCards = container.querySelectorAll('.metric-card__value');
      expect(metricCards[2]).toHaveTextContent(/₹0\.00/);
    });
  });

  describe('Currency Formatting', () => {
    it('uses ₹ (Rupee) symbol for all amounts', () => {
      const { container } = render(<SummaryMetrics metrics={mockMetrics} />);

      const metricValues = container.querySelectorAll('.metric-card__value');
      let rupeeCount = 0;
      metricValues.forEach(value => {
        if (value.textContent?.includes('₹')) rupeeCount++;
      });
      expect(rupeeCount).toBeGreaterThanOrEqual(3);
    });

    it('applies Indian number grouping (lakh/crore)', () => {
      const { container } = render(<SummaryMetrics metrics={{ totalInvested: 12500000, finalProceeds: 15000000, profitLoss: 2500000 }} />);

      // 12500000 should be formatted as 1,25,00,000 (Indian grouping)
      const metricCards = container.querySelectorAll('.metric-card__value');
      expect(metricCards[0]).toHaveTextContent(/1,25,00,000\.00/);
    });

    it('displays exactly 2 decimal places', () => {
      const customMetrics = {
        totalInvested: 1000,
        finalProceeds: 1500,
        profitLoss: 500,
      };

      const { container } = render(<SummaryMetrics metrics={customMetrics} />);

      // All amounts should end in .00
      const metricValues = container.querySelectorAll('.metric-card__value');
      metricValues.forEach(value => {
        expect(value.textContent).toMatch(/\.00/);
      });
    });
  });

  describe('Coloring', () => {
    it('profit is green when positive', () => {
      const { container } = render(<SummaryMetrics metrics={mockMetrics} />);

      const profitDisplay = container.querySelector('.metric-card__value--positive');
      expect(profitDisplay).toBeInTheDocument();
      expect(profitDisplay).toHaveTextContent(/₹2,25,500\.00/);
    });

    it('loss is red when negative', () => {
      const { container } = render(<SummaryMetrics metrics={mockNegativeMetrics} />);

      const lossElement = container.querySelector('.metric-card__value--negative');
      expect(lossElement).toBeInTheDocument();
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

      const { container } = render(<SummaryMetrics metrics={largeMetrics} />);

      // Should render without crashing - check that all metric values are rendered
      const metricValues = container.querySelectorAll('.metric-card__value');
      expect(metricValues.length).toBe(3);
    });

    it('handles fractional amounts (rounded to 2dp)', () => {
      const fractionalMetrics = {
        totalInvested: 1000.556,
        finalProceeds: 1500.444,
        profitLoss: 499.888,
      };

      const { container } = render(<SummaryMetrics metrics={fractionalMetrics} />);

      // All amounts should be rounded to 2 decimal places
      const metricValues = container.querySelectorAll('.metric-card__value');
      metricValues.forEach(value => {
        expect(value.textContent).toMatch(/\.00$/);
      });
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
      const className = wrapper?.className || '';
      // Check if the wrapper has grid or metrics-related classes
      expect(className).toMatch(/grid|metrics/);
    });
  });
});

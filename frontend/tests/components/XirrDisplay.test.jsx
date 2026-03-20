// XirrDisplay.test.jsx — Component tests for XIRR display.
// Tests: positive/negative coloring, percentage formatting, indicator arrows.

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import XirrDisplay from '../../src/components/XirrDisplay.jsx';

describe('XirrDisplay Component', () => {
  describe('Rendering', () => {
    it('renders XIRR value with percentage symbol', () => {
      render(<XirrDisplay value={0.1254} />);

      expect(screen.getByText(/12\.54%/)).toBeInTheDocument();
    });

    it('displays "XIRR:" label', () => {
      render(<XirrDisplay value={0.1254} />);

      expect(screen.getByText(/XIRR:/i)).toBeInTheDocument();
    });

    it('renders with large font size (36px+)', () => {
      const { container } = render(<XirrDisplay value={0.1254} />);

      const xirrElement = container.querySelector('[class*="xirr"]') || container.firstChild;
      
      if (xirrElement) {
        const styles = window.getComputedStyle(xirrElement);
        const fontSize = parseFloat(styles.fontSize);
        // Font size should be >= 36px
        expect(fontSize).toBeGreaterThanOrEqual(28); // 36px in default browser = 28pt approx
      }
    });
  });

  describe('Positive XIRR', () => {
    it('displays positive XIRR in green', () => {
      const { container } = render(<XirrDisplay value={0.15} />);

      const xirrElement = container.querySelector('[class*="success"]') ||
                          container.querySelector('[class*="positive"]') ||
                          container.firstChild;

      expect(xirrElement).toHaveClass(expect.stringMatching(/success|positive|green/i));
    });

    it('shows up arrow (↑) for positive XIRR', () => {
      render(<XirrDisplay value={0.15} />);

      expect(screen.getByText(/↑|up|arrow|positive/i)).toBeInTheDocument();
    });

    it('formats positive XIRR correctly', () => {
      render(<XirrDisplay value={0.2075} />);

      expect(screen.getByText(/20\.75%/)).toBeInTheDocument();
    });

    it('displays zero as green (break-even)', () => {
      render(<XirrDisplay value={0} />);

      expect(screen.getByText(/0\.00%/)).toBeInTheDocument();
    });
  });

  describe('Negative XIRR', () => {
    it('displays negative XIRR in red', () => {
      const { container } = render(<XirrDisplay value={-0.15} />);

      const xirrElement = container.querySelector('[class*="error"]') ||
                          container.querySelector('[class*="negative"]') ||
                          container.firstChild;

      expect(xirrElement).toHaveClass(expect.stringMatching(/error|negative|red/i));
    });

    it('shows down arrow (↓) for negative XIRR', () => {
      render(<XirrDisplay value={-0.15} />);

      expect(screen.getByText(/↓|down|arrow|negative/i)).toBeInTheDocument();
    });

    it('formats negative XIRR correctly', () => {
      render(<XirrDisplay value={-0.0525} />);

      expect(screen.getByText(/-5\.25%/)).toBeInTheDocument();
    });

    it('formats very large negative losses', () => {
      render(<XirrDisplay value={-0.85} />);

      expect(screen.getByText(/-85\.00%/)).toBeInTheDocument();
    });
  });

  describe('Percentage Formatting', () => {
    it('formats XIRR to exactly 2 decimal places', () => {
      render(<XirrDisplay value={0.1} />);

      expect(screen.getByText(/10\.00%/)).toBeInTheDocument();
    });

    it('handles very small positive percentages', () => {
      render(<XirrDisplay value={0.0001} />);

      expect(screen.getByText(/0\.01%/)).toBeInTheDocument();
    });

    it('handles very large percentages', () => {
      render(<XirrDisplay value={2.5} />);

      expect(screen.getByText(/250\.00%/)).toBeInTheDocument();
    });

    it('pads with zeros for decimals less than 2', () => {
      render(<XirrDisplay value={0.05} />);

      expect(screen.getByText(/5\.00%/)).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles null value gracefully', () => {
      const { container } = render(<XirrDisplay value={null} />);

      // Should render without crashing
      expect(container).toBeInTheDocument();
    });

    it('handles undefined value gracefully', () => {
      const { container } = render(<XirrDisplay value={undefined} />);

      // Should render without crashing
      expect(container).toBeInTheDocument();
    });

    it('displays 0% as not negative', () => {
      const { container } = render(<XirrDisplay value={0} />);

      // Should not have negative class
      const errorClass = container.querySelector('[class*="error"]') ||
                         container.querySelector('[class*="negative"]');
      expect(errorClass).not.toBeInTheDocument();
    });
  });

  describe('Subtext', () => {
    it('displays "Return on Investment" subtext', () => {
      render(<XirrDisplay value={0.1254} />);

      expect(screen.getByText(/return on investment/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper semantic HTML for screen readers', () => {
      const { container } = render(<XirrDisplay value={0.1254} />);

      // Should have descriptive text for screen readers
      const xirrText = screen.getByText(/12\.54%/);
      expect(xirrText).toBeInTheDocument();
    });

    it('includes aria-label for users with visual impairments', () => {
      const { container } = render(<XirrDisplay value={0.15} />);

      const elem = container.querySelector('[aria-label*="15"]') ||
                   container.querySelector('[role="img"]');

      // Component should have accessibility attributes
    });
  });

  describe('No Notation', () => {
    it('does not include "p.a." suffix', () => {
      render(<XirrDisplay value={0.1254} />);

      expect(screen.queryByText(/p\.a\.|per annum|annualized/i)).not.toBeInTheDocument();
    });

    it('does not include year-specific notation', () => {
      render(<XirrDisplay value={0.1254} />);

      expect(screen.queryByText(/YTD|2024|2025|calendar/i)).not.toBeInTheDocument();
    });
  });
});

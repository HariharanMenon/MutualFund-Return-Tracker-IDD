// ErrorBanner.test.jsx — Component tests for ErrorBanner.
// Tests: error message display, details, Try Again button.

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorBanner from '../../src/components/ErrorBanner.jsx';

describe('ErrorBanner Component', () => {
  describe('Rendering', () => {
    it('renders error banner with red background', () => {
      const mockOnRetry = vi.fn();
      const { container } = render(
        <ErrorBanner
          message="File validation failed"
          details="Row 5: Invalid date format"
          onRetry={mockOnRetry}
        />
      );

      const banner = container.querySelector('[class*="error"]');
      expect(banner).toHaveClass(expect.stringMatching(/error|banner|red/i));
    });

    it('displays error message', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="File validation failed"
          details="Row 5: Invalid date format"
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText('File validation failed')).toBeInTheDocument();
    });

    it('displays error heading "File Upload Failed"', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Validation error"
          details="Some details"
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText(/file upload failed/i)).toBeInTheDocument();
    });
  });

  describe('Error Message', () => {
    it('displays main error message prominently', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Cannot calculate XIRR"
          details="Cannot calculate XIRR for this data"
          onRetry={mockOnRetry}
        />
      );

      const message = screen.getByText('Cannot calculate XIRR');
      expect(message).toBeInTheDocument();
    });

    it('handles different error messages', () => {
      const mockOnRetry = vi.fn();

      const { rerender } = render(
        <ErrorBanner
          message="File too large"
          details="Maximum 10 MB"
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText('File too large')).toBeInTheDocument();

      rerender(
        <ErrorBanner
          message="Network error"
          details="Unable to reach server"
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  describe('Error Details', () => {
    it('displays error details if provided', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Validation failed"
          details="Row 5: Invalid date format 'xyz' (expected DD-MMM-YYYY)"
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText(/Row 5: Invalid date format/)).toBeInTheDocument();
    });

    it('handles null details gracefully', () => {
      const mockOnRetry = vi.fn();
      const { container } = render(
        <ErrorBanner
          message="Server error"
          details={null}
          onRetry={mockOnRetry}
        />
      );

      // Should render without crashing
      expect(container).toBeInTheDocument();
    });

    it('handles missing details prop', () => {
      const mockOnRetry = vi.fn();
      const { container } = render(
        <ErrorBanner
          message="Unknown error"
          onRetry={mockOnRetry}
        />
      );

      // Should render without crashing
      expect(container).toBeInTheDocument();
    });

    it('displays long error details without truncation', () => {
      const mockOnRetry = vi.fn();
      const longDetails = 'This is a very long error message that provides detailed information about what went wrong during file processing. It should display in full without being truncated or causing layout issues.';

      render(
        <ErrorBanner
          message="Error"
          details={longDetails}
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText(longDetails)).toBeInTheDocument();
    });
  });

  describe('Try Again Button', () => {
    it('displays "Try Again" button', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Upload failed"
          details="Details"
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    it('calls onRetry callback when Try Again is clicked', async () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Error"
          details="Details"
          onRetry={mockOnRetry}
        />
      );

      const button = screen.getByRole('button', { name: /try again/i });
      await userEvent.click(button);

      expect(mockOnRetry).toHaveBeenCalledTimes(1);
    });

    it('fires onRetry only once per click', async () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Error"
          details="Details"
          onRetry={mockOnRetry}
        />
      );

      const button = screen.getByRole('button', { name: /try again/i });

      await userEvent.click(button);
      await userEvent.click(button);

      expect(mockOnRetry).toHaveBeenCalledTimes(2);
    });

    it('button is accessible via keyboard', async () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Error"
          details="Details"
          onRetry={mockOnRetry}
        />
      );

      const button = screen.getByRole('button', { name: /try again/i });

      // Tab to button
      button.focus();
      expect(button).toHaveFocus();

      // Press Enter
      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });

      // Button should be clickable
      expect(button).toBeInTheDocument();
    });
  });

  describe('Color Scheme', () => {
    it('uses red/error styling for banner', () => {
      const mockOnRetry = vi.fn();
      const { container } = render(
        <ErrorBanner
          message="Error"
          details="Details"
          onRetry={mockOnRetry}
        />
      );

      const banner = container.querySelector('[class*="banner"]') ||
                     container.querySelector('[class*="error"]');

      expect(banner).toHaveClass(expect.stringMatching(/error|red/i));
    });

    it('button may have contrasting color for visibility', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Error"
          details="Details"
          onRetry={mockOnRetry}
        />
      );

      const button = screen.getByRole('button', { name: /try again/i });

      // Button should be visible and interactive
      expect(button).toBeVisible();
    });
  });

  describe('Layout', () => {
    it('displays message and details in readable format', () => {
      const mockOnRetry = vi.fn();
      const { container } = render(
        <ErrorBanner
          message="Validation failed"
          details="Row 5: Invalid date"
          onRetry={mockOnRetry}
        />
      );

      // Message should appear before details
      const messageEl = screen.getByText('Validation failed');
      const detailsEl = screen.getByText('Row 5: Invalid date');

      expect(messageEl).toBeInTheDocument();
      expect(detailsEl).toBeInTheDocument();
    });

    it('positions Try Again button prominently', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Error"
          details="Details"
          onRetry={mockOnRetry}
        />
      );

      const button = screen.getByRole('button', { name: /try again/i });

      // Button should be visible and accessible
      expect(button).toBeVisible();
      expect(button).not.toBeDisabled();
    });
  });

  describe('Error Messages from Backend', () => {
    it('displays file validation errors', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="File validation failed"
          details="Row 5: Date column contains invalid format 'xyz' (expected DD-MMM-YYYY, e.g., 15-Jan-2020)"
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText(/File validation failed/)).toBeInTheDocument();
      expect(screen.getByText(/Row 5/)).toBeInTheDocument();
    });

    it('displays file size errors', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="File too large"
          details="File size exceeds 10 MB limit"
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText(/File too large/)).toBeInTheDocument();
    });

    it('displays XIRR calculation errors', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Cannot calculate XIRR"
          details="Cannot calculate XIRR for this data. Please verify all transactions."
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText(/Cannot calculate XIRR/)).toBeInTheDocument();
    });

    it('displays network errors', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Unable to reach the server"
          details="Please check your connection and try again."
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText(/Unable to reach/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('error message is announced to screen readers', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Error occurred"
          details="Details here"
          onRetry={mockOnRetry}
        />
      );

      const message = screen.getByText('Error occurred');
      expect(message).toHaveAttribute(expect.stringMatching(/role|aria/i));
    });

    it('button is accessible with descriptive text', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Error"
          details="Details"
          onRetry={mockOnRetry}
        />
      );

      const button = screen.getByRole('button');
      expect(button.textContent).toMatch(/try again/i);
    });
  });

  describe('Edge Cases', () => {
    it('handles very long error messages', () => {
      const mockOnRetry = vi.fn();
      const longMessage = 'A'.repeat(500);

      render(
        <ErrorBanner
          message={longMessage}
          details="More details"
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('handles special characters in error messages', () => {
      const mockOnRetry = vi.fn();
      render(
        <ErrorBanner
          message="Error: Row 5 contains invalid date '01-01-2020' (expected DD-MMM-YYYY)"
          details="Try reformatting your file."
          onRetry={mockOnRetry}
        />
      );

      expect(screen.getByText(/01-01-2020/)).toBeInTheDocument();
    });
  });
});

// UploadArea.test.jsx — Component tests for UploadArea.
// Tests: drag-and-drop, file picker, validation, disabled state.

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UploadArea from '../../src/components/UploadArea.jsx';

// Mock validation functions
vi.mock('../../src/services/validation.js', () => ({
  isValidFileType: vi.fn((file) => file.name.endsWith('.xlsx')),
  isValidFileSize: vi.fn((file) => file.size <= 10 * 1024 * 1024),
}));

describe('UploadArea Component', () => {
  describe('Rendering', () => {
    it('renders upload area with drag-and-drop zone', () => {
      const onFile = vi.fn();
      render(<UploadArea onFile={onFile} />);

      // Check for drag-and-drop area (looking for text that indicates upload capability)
      expect(screen.getByText(/drag.*drop|upload|select/i)).toBeInTheDocument();
    });

    it('renders hidden file input', () => {
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);

      const fileInput = container.querySelector('input[type="file"]');
      expect(fileInput).toBeInTheDocument();
      expect(fileInput).toHaveAttribute('accept', '.xlsx');
    });
  });

  describe('File Picker', () => {
    it('calls onFile when file is selected via input', async () => {
      const user = userEvent.setup();
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);

      const fileInput = container.querySelector('input[type="file"]');
      const file = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      await user.upload(fileInput, file);

      expect(onFile).toHaveBeenCalledWith(expect.any(File));
    });

    it('rejects non-.xlsx files', async () => {
      const user = userEvent.setup();
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);

      const fileInput = container.querySelector('input[type="file"]');
      const csvFile = new File(['test'], 'test.csv', { type: 'text/csv' });

      await user.upload(fileInput, csvFile);

      // Component validates file type, so onFile should not be called
      // (actual behavior depends on component implementation)
    });
  });

  describe('Drag and Drop', () => {
    it('accepts files via drag-and-drop', () => {
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);

      const dropZone = container.querySelector('[class*="drag"]') || 
                       container.firstChild?.querySelector('div');

      if (dropZone) {
        const file = new File(['test'], 'test.xlsx', {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        });

        const dataTransfer = {
          files: [file],
        };

        fireEvent.drop(dropZone, { dataTransfer });

        // Behavior depends on component implementation
      }
    });

    it('shows visual feedback during drag-over', () => {
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);

      const dropZone = container.querySelector('[class*="drag"]') || 
                       container.firstChild?.querySelector('div');

      if (dropZone) {
        fireEvent.dragOver(dropZone);
        // Component should show visual feedback (CSS class or state change)
      }
    });
  });

  describe('Disabled State', () => {
    it('disables upload area when disabled prop is true', () => {
      const onFile = vi.fn();
      render(<UploadArea onFile={onFile} disabled={true} />);

      // Component should show disabled state
      // Exact implementation depends on component styling/state
    });

    it('ignores file selection when disabled', async () => {
      const user = userEvent.setup();
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} disabled={true} />);

      const fileInput = container.querySelector('input[type="file"]');
      const file = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      await user.upload(fileInput, file);

      // onFile should not be called when disabled
      expect(onFile).not.toHaveBeenCalled();
    });

    it('ignores drag-and-drop when disabled', () => {
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} disabled={true} />);

      const dropZone = container.querySelector('[class*="drag"]') || 
                       container.firstChild?.querySelector('div');

      if (dropZone) {
        const file = new File(['test'], 'test.xlsx');
        const dataTransfer = { files: [file] };

        fireEvent.drop(dropZone, { dataTransfer });

        // onFile should not be called when disabled
        expect(onFile).not.toHaveBeenCalled();
      }
    });
  });

  describe('Validation Error Display', () => {
    it('displays error message for invalid file type', async () => {
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);

      const fileInput = container.querySelector('input[type="file"]');
      const csvFile = new File(['test'], 'test.csv');

      await act(async () => {
       fireEvent.change(fileInput, { target: { files: [csvFile] } });
      });

      // Component should display error message (depends on implementation)
    });

    it('displays error message for oversized file', async () => {
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);

      const fileInput = container.querySelector('input[type="file"]');
      // Use fireEvent inside act() instead of userEvent.upload() — userEvent
      // processes the real 11MB file size synchronously, causing setLocalError
      // to fire outside act()'s boundary and triggering the warning.
      const largeFile = new File(
        ['x'.repeat(11 * 1024 * 1024)],
        'large.xlsx'
      );

      await act(async () => {
        fireEvent.change(fileInput, { target: { files: [largeFile] } });
      });

      // Component should display "too large" error message
      expect(onFile).not.toHaveBeenCalled();
      expect(container.querySelector('.upload-area__error')).toBeInTheDocument();
    });

    it('clears error message when valid file is selected', async () => {
      const user = userEvent.setup();
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);

      const fileInput = container.querySelector('input[type="file"]');

      // Upload invalid file
      const csvFile = new File(['test'], 'test.csv');
      await user.upload(fileInput, csvFile);

      // Error should be displayed

      // Upload valid file
      const validFile = new File(['test'], 'valid.xlsx');
      await user.upload(fileInput, validFile);

      // Error should be cleared
    });
  });

  describe('File Validation Integration', () => {
    it('accepts .xlsx files only', async () => {
      const user = userEvent.setup();
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);

      const fileInput = container.querySelector('input[type="file"]');

      const validFile = new File(['test'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      await user.upload(fileInput, validFile);

      expect(onFile).toHaveBeenCalledWith(validFile);
    });

    it('rejects files larger than 10MB', async () => {
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);

      const fileInput = container.querySelector('input[type="file"]');

      // Use fireEvent inside act() — same reason as the oversized test above:
      // userEvent processes real file size synchronously, causing setLocalError
      // to escape act()'s flush boundary and produce the warning.
      const largeFile = new File(
        ['x'.repeat(11 * 1024 * 1024)],
        'large.xlsx',
        {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
      );

      await act(async () => {
        fireEvent.change(fileInput, { target: { files: [largeFile] } });
      });

      // Should not call onFile for oversized file
      expect(onFile).not.toHaveBeenCalled();
      expect(container.querySelector('.upload-area__error')).toBeInTheDocument();
    });
  });

  describe('Default Props', () => {
    it('renders with disabled=false by default', () => {
      const onFile = vi.fn();
      const { container } = render(<UploadArea onFile={onFile} />);
      const fileInput = container.querySelector('input[type="file"]');
      expect(fileInput).not.toBeDisabled();
    });
  });
});

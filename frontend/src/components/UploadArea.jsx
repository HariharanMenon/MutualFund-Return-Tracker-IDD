import { useRef, useState } from 'react';
import { isValidFileSize, isValidFileType } from '../services/validation.js';
import { FILE_SIZE_LIMIT_LABEL, ACCEPTED_FILE_EXTENSION } from '../utils/constants.js';
import './UploadArea.css';

/**
 * UploadArea — drag-and-drop + file picker (spec §4.1).
 *
 * Props:
 *   onFile   {(File) => void}   Called with the validated File object
 *   disabled {boolean}          True while an upload is in progress
 */
export default function UploadArea({ onFile, disabled = false }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [localError, setLocalError] = useState(null);

  function validate(file) {
    if (!isValidFileType(file)) {
      setLocalError(`Only .xlsx files are accepted.`);
      return false;
    }
    if (!isValidFileSize(file)) {
      setLocalError(`File is too large. Maximum allowed size is ${FILE_SIZE_LIMIT_LABEL}.`);
      return false;
    }
    setLocalError(null);
    return true;
  }

  function handleFile(file) {
    if (!file || disabled) return;
    if (validate(file)) onFile(file);
  }

  /* ---- Drag events ---- */
  function onDragOver(e) {
    e.preventDefault();
    if (!disabled) setDragOver(true);
  }

  function onDragLeave() {
    setDragOver(false);
  }

  function onDrop(e) {
    e.preventDefault();
    setDragOver(false);
    if (disabled) return;
    const file = e.dataTransfer.files?.[0];
    handleFile(file);
  }

  /* ---- Input change ---- */
  function onChange(e) {
    const file = e.target.files?.[0];
    handleFile(file);
    // Reset so selecting the same file again fires onChange
    e.target.value = '';
  }

  const areaClass = [
    'upload-area',
    dragOver && !disabled ? 'upload-area--drag-over' : '',
    disabled ? 'upload-area--disabled' : '',
  ].filter(Boolean).join(' ');

  return (
    <div className="upload-area-wrapper">
      {/* Hidden file input */}
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_FILE_EXTENSION}
        className="upload-area__input"
        aria-label="Upload Excel file"
        disabled={disabled}
        onChange={onChange}
      />

      {/* Drop zone */}
      <div
        className={areaClass}
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-disabled={disabled}
        aria-label="Upload Excel file by clicking or dragging"
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); if (!disabled) inputRef.current?.click(); } }}
      >
        <span className="upload-area__icon" aria-hidden="true">📂</span>
        <p className="upload-area__primary">
          {disabled
            ? 'Upload in progress…'
            : 'Drag & drop your .xlsx file here'}
        </p>
        {!disabled && (
          <p className="upload-area__secondary">
            or <span className="upload-area__link">browse files</span>
            <br />
            <span className="upload-area__hint">Maximum size: {FILE_SIZE_LIMIT_LABEL}</span>
          </p>
        )}
      </div>

      {localError && (
        <p className="upload-area__error" role="alert">{localError}</p>
      )}
    </div>
  );
}

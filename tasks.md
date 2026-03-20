# tasks.md — MutualFund-Return-Tracker-IDD Implementation Tracker

**Format:** `- [ ] TXXX [Pn] [Phase] [Deps: ...] Description | path/to/file`
**Priority:** P1 = Backend (blocking) | P2 = Frontend | P3 = Infrastructure/CI

---

## Phase 1 — Foundation & Setup

- [x] T001 [P1] [Phase 1] [Deps: None] Append Node/OS/Render sections to .gitignore | .gitignore
- [x] T002 [P1] [Phase 1] [Deps: None] Root environment variables template | .env.example
- [x] T003 [P1] [Phase 1] [Deps: None] Python dependencies with pinned versions | backend/requirements.txt
- [x] T004 [P1] [Phase 1] [Deps: None] Application config — file limits, date range, column names, CORS | backend/config.py
- [x] T005 [P1] [Phase 1] [Deps: None] Render process file + Python runtime spec | backend/Procfile, backend/runtime.txt
- [x] T006 [P1] [Phase 1] [Deps: None] All __init__.py stubs + exceptions/ + tests/ directory scaffolding | backend/app/**/__init__.py, backend/tests/
- [x] T007 [P2] [Phase 1] [Deps: None] Frontend package.json with pinned React 18.2, Vite 5, Vitest deps | frontend/package.json
- [x] T008 [P2] [Phase 1] [Deps: T007] Vite config with proxy, jsdom test environment | frontend/vite.config.js
- [x] T009 [P2] [Phase 1] [Deps: None] HTML entry point for Vite/React | frontend/index.html
- [x] T010 [P2] [Phase 1] [Deps: None] Frontend environment variables template | frontend/.env.example
- [x] T011 [P1] [Phase 1] [Deps: None] Master task tracker (this file) | tasks.md

---

## Phase 2 — Backend: Utils & Exceptions

- [x] T012 [P1] [Phase 2] [Deps: T004] Transaction type sets, error message templates, column name constants | backend/app/utils/constants.py
- [x] T013 [P1] [Phase 2] [Deps: None] Structured logging utility | backend/app/utils/logger.py
- [x] T014 [P1] [Phase 2] [Deps: T004] DD-MMM-YYYY date parser + 1960–today range validation | backend/app/utils/date_parser.py
- [x] T015 [P1] [Phase 2] [Deps: T012] Transaction type normalizer (all spec variants → canonical form) | backend/app/utils/transaction_normalizer.py
- [x] T016 [P1] [Phase 2] [Deps: None] FileValidationError custom exception | backend/app/exceptions/validation_error.py
- [x] T017 [P1] [Phase 2] [Deps: None] FileProcessingError custom exception | backend/app/exceptions/file_error.py
- [x] T018 [P1] [Phase 2] [Deps: None] XirrCalculationError custom exception | backend/app/exceptions/calculation_error.py
- [x] T019 [P1] [Phase 2] [Deps: T016,T017,T018] exceptions/__init__.py re-exports | backend/app/exceptions/__init__.py

---

## Phase 3 — Backend: Models

- [x] T020 [P1] [Phase 3] [Deps: T012] Pydantic Transaction model (6 fields, conditional optionals) | backend/app/models/transaction.py
- [x] T021 [P1] [Phase 3] [Deps: T020] Pydantic UploadResponse + SummaryMetrics models | backend/app/models/response.py
- [x] T022 [P1] [Phase 3] [Deps: None] Pydantic ErrorDetail model | backend/app/models/error.py

---

## Phase 4 — Backend: Services

- [x] T023 [P1] [Phase 4] [Deps: T017] Excel file loader — first sheet only, returns raw list of dicts | backend/app/services/file_parser.py
- [x] T024 [P1] [Phase 4] [Deps: T014,T015,T016,T020] Full validation engine — column, row, file-level; all 15 error rules | backend/app/services/validator.py
- [x] T025 [P1] [Phase 4] [Deps: T014,T015,T020] Transaction normalizer service — types, dates, decimal rounding | backend/app/services/transaction_processor.py
- [x] T026 [P1] [Phase 4] [Deps: T018,T020,T021] XIRR cash flow builder + numpy_financial call + summary metrics | backend/app/services/xirr_calculator.py

---

## Phase 5 — Backend: API Route + Entry Point

- [x] T027 [P1] [Phase 5] [Deps: T023,T024,T025,T026] POST /api/upload route — orchestrate services, return typed responses | backend/app/api/routes/upload.py
- [x] T028 [P1] [Phase 5] [Deps: T027] API __init__.py files + router registration | backend/app/api/__init__.py, backend/app/api/routes/__init__.py
- [x] T029 [P1] [Phase 5] [Deps: T028] FastAPI app init — CORS, middleware, router inclusion, health check | backend/main.py

---

## Phase 6 — Backend: Tests

- [x] T030 [P1] [Phase 6] [Deps: T029] pytest fixtures — TestClient, temp xlsx factory | backend/tests/conftest.py
- [x] T031 [P1] [Phase 6] [Deps: T030] Test data generator + 6 sample .xlsx fixture files | backend/tests/fixtures/test_data.py, backend/tests/fixtures/*.xlsx
- [x] T032 [P1] [Phase 6] [Deps: T030,T031] Unit tests — Excel loading, first-sheet-only, corrupt file handling | backend/tests/test_file_parser.py
- [x] T033 [P1] [Phase 6] [Deps: T030,T031] Unit tests — all 15 validation rules | backend/tests/test_validator.py
- [x] T034 [P1] [Phase 6] [Deps: T030,T031] Unit tests — XIRR accuracy, Stamp Duty exclusion, convergence failure | backend/tests/test_xirr_calculator.py
- [x] T035 [P1] [Phase 6] [Deps: T030] Unit tests — all transaction type variant normalizations | backend/tests/test_transaction_normalizer.py
- [x] T036 [P1] [Phase 6] [Deps: T030,T031] Integration tests — /api/upload happy path + all error scenarios | backend/tests/test_routes_upload.py

---

## Phase 7 — Frontend: Styles

- [x] T037 [P2] [Phase 7] [Deps: T007] CSS custom properties — colors, spacing, font sizes | frontend/src/styles/variables.css
- [x] T038 [P2] [Phase 7] [Deps: T037] Shimmer + spinner keyframe animations | frontend/src/styles/animations.css
- [x] T039 [P2] [Phase 7] [Deps: T037] 6-column grid layout — proportional widths, row striping | frontend/src/styles/grid.css
- [x] T040 [P2] [Phase 7] [Deps: T037] Responsive media queries — mobile/tablet/desktop | frontend/src/styles/responsive.css

---

## Phase 8 — Frontend: Utils & Services

- [x] T041 [P2] [Phase 8] [Deps: T007] Frontend constants — API URL, file limits, column names | frontend/src/utils/constants.js
- [x] T042 [P2] [Phase 8] [Deps: T041] Shared utility helpers | frontend/src/utils/helpers.js
- [x] T043 [P2] [Phase 8] [Deps: None] Simple console logger | frontend/src/utils/logger.js
- [x] T044 [P2] [Phase 8] [Deps: T041] Formatters — formatCurrency, formatDate, formatPercentage, formatUnits | frontend/src/services/formatting.js
- [x] T045 [P2] [Phase 8] [Deps: T041] Frontend validators — isValidFileSize, isValidFileType | frontend/src/services/validation.js
- [x] T046 [P2] [Phase 8] [Deps: T041,T043] API client — uploadFile() fetch wrapper with error handling | frontend/src/services/api.js

---

## Phase 9 — Frontend: Components

- [x] T047 [P2] [Phase 9] [Deps: T037,T038] ErrorBanner — red banner, message, details, Try Again button | frontend/src/components/ErrorBanner.jsx, ErrorBanner.css
- [x] T048 [P2] [Phase 9] [Deps: T037,T038] LoadingSpinner — "Processing file..." animated spinner | frontend/src/components/LoadingSpinner.jsx, LoadingSpinner.css
- [x] T049 [P2] [Phase 9] [Deps: T037,T038,T039] SkeletonLoader — 6-col, ~8 rows, shimmer animation | frontend/src/components/SkeletonLoader.jsx, SkeletonLoader.css
- [x] T050 [P2] [Phase 9] [Deps: T037,T044] XirrDisplay — 36px+ percentage, green/red, ↑↓ indicator | frontend/src/components/XirrDisplay.jsx, XirrDisplay.css
- [x] T051 [P2] [Phase 9] [Deps: T037,T044] SummaryMetrics — Total Invested, Final Proceeds, Profit/Loss | frontend/src/components/SummaryMetrics.jsx, SummaryMetrics.css
- [x] T052 [P2] [Phase 9] [Deps: T037,T039,T044] TransactionGrid — 6-col table, file order, "—" for nulls, row striping | frontend/src/components/TransactionGrid.jsx, TransactionGrid.css
- [x] T053 [P2] [Phase 9] [Deps: T037,T044,T045] UploadArea — drag-and-drop, file picker, size+type validation, disabled during upload | frontend/src/components/UploadArea.jsx, UploadArea.css

---

## Phase 10 — Frontend: Hooks + App Entry Point

- [x] T054 [P2] [Phase 10] [Deps: T046] useApi — fetch wrapper, network error handling, response parsing | frontend/src/hooks/useApi.js
- [x] T055 [P2] [Phase 10] [Deps: T054,T045] useFileUpload — state machine (idle→loading→skeleton→result/error) | frontend/src/hooks/useFileUpload.js
- [x] T056 [P2] [Phase 10] [Deps: T054] useXirrCalculation — XIRR + transactions + summaryMetrics state | frontend/src/hooks/useXirrCalculation.js
- [x] T057 [P2] [Phase 10] [Deps: T047,T048,T049,T050,T051,T052,T053,T055,T056] App.jsx root — all state wiring, layout | frontend/src/App.jsx, App.css
- [x] T058 [P2] [Phase 10] [Deps: T057] main.jsx — React entry point, mount to #root | frontend/src/main.jsx

---

## Phase 11 — Frontend: Tests

- [ ] T059 [P2] [Phase 11] [Deps: T007,T008] Vitest global setup + testing-library config | frontend/tests/setup.js
- [ ] T060 [P2] [Phase 11] [Deps: T044,T059] Unit tests — formatCurrency, formatDate, formatPercentage, formatUnits | frontend/tests/services/formatting.test.js
- [ ] T061 [P2] [Phase 11] [Deps: T046,T059] Unit tests — uploadFile fetch mock | frontend/tests/services/api.test.js
- [ ] T062 [P2] [Phase 11] [Deps: T055,T059] Hook tests — state transitions, frontend validation logic | frontend/tests/hooks/useFileUpload.test.js
- [ ] T063 [P2] [Phase 11] [Deps: T054,T059] Hook tests — network error handling | frontend/tests/hooks/useApi.test.js
- [ ] T064 [P2] [Phase 11] [Deps: T053,T059] Component tests — drag-drop, file type rejection, disabled state | frontend/tests/components/UploadArea.test.jsx
- [ ] T065 [P2] [Phase 11] [Deps: T050,T059] Component tests — positive green, negative red, format | frontend/tests/components/XirrDisplay.test.jsx
- [ ] T066 [P2] [Phase 11] [Deps: T051,T059] Component tests — three metrics, profit/loss coloring | frontend/tests/components/SummaryMetrics.test.jsx
- [ ] T067 [P2] [Phase 11] [Deps: T052,T059] Component tests — columns, null display, row order | frontend/tests/components/TransactionGrid.test.jsx
- [ ] T068 [P2] [Phase 11] [Deps: T047,T059] Component tests — error message display, retry button | frontend/tests/components/ErrorBanner.test.jsx

---

## Phase 12 — Infrastructure & CI

- [ ] T069 [P3] [Phase 12] [Deps: T029,T058] Render deployment spec — backend web service + static frontend | render.yaml
- [ ] T070 [P3] [Phase 12] [Deps: T029] GitHub Actions CI — pytest on push | .github/workflows/backend-tests.yml
- [ ] T071 [P3] [Phase 12] [Deps: T058] GitHub Actions CI — vitest on push | .github/workflows/frontend-tests.yml
- [ ] T072 [P3] [Phase 12] [Deps: None] Shell scripts — setup.sh, start-dev.sh, test-all.sh, build-frontend.sh, clean.sh | scripts/
- [ ] T073 [P3] [Phase 12] [Deps: T029,T058] Update README.md with quick-start + architecture overview | README.md

---

## Summary

| Phase | Tasks | Status |
|---|---|---|
| Phase 1 — Foundation & Setup | T001–T011 | ✅ Complete |
| Phase 2 — Backend Utils & Exceptions | T012–T019 | ✅ Complete |
| Phase 3 — Backend Models | T020–T022 | ✅ Complete |
| Phase 4 — Backend Services | T023–T026 | ✅ Complete |
| Phase 5 — Backend API + main.py | T027–T029 | ✅ Complete |
| Phase 6 — Backend Tests | T030–T036 | ✅ Complete |
| Phase 7 — Frontend Styles | T037–T040 | ✅ Complete |
| Phase 8 — Frontend Utils & Services | T041–T046 | ✅ Complete |
| Phase 9 — Frontend Components | T047–T053 | ✅ Complete |
| Phase 10 — Frontend Hooks + App | T054–T058 | ✅ Complete |
| Phase 11 — Frontend Tests | T059–T068 | ⏳ Pending |
| Phase 12 — Infrastructure & CI | T069–T073 | ⏳ Pending |

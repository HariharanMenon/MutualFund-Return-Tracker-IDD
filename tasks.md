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
- [x] T014 [P1] [Phase 2] [Deps: T004] DD/MM/YYYY date parser + 1960–today range validation | backend/app/utils/date_parser.py
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

- [x] T059 [P2] [Phase 11] [Deps: T007,T008] Vitest global setup + testing-library config | frontend/tests/setup.js
- [x] T060 [P2] [Phase 11] [Deps: T044,T059] Unit tests — formatCurrency, formatDate, formatPercentage, formatUnits | frontend/tests/services/formatting.test.js
- [x] T061 [P2] [Phase 11] [Deps: T046,T059] Unit tests — uploadFile fetch mock | frontend/tests/services/api.test.js
- [x] T062 [P2] [Phase 11] [Deps: T055,T059] Hook tests — state transitions, frontend validation logic | frontend/tests/hooks/useFileUpload.test.js
- [x] T063 [P2] [Phase 11] [Deps: T054,T059] Hook tests — network error handling | frontend/tests/hooks/useApi.test.js
- [x] T064 [P2] [Phase 11] [Deps: T053,T059] Component tests — drag-drop, file type rejection, disabled state | frontend/tests/components/UploadArea.test.jsx
- [x] T065 [P2] [Phase 11] [Deps: T050,T059] Component tests — positive green, negative red, format | frontend/tests/components/XirrDisplay.test.jsx
- [x] T066 [P2] [Phase 11] [Deps: T051,T059] Component tests — three metrics, profit/loss coloring | frontend/tests/components/SummaryMetrics.test.jsx
- [x] T067 [P2] [Phase 11] [Deps: T052,T059] Component tests — columns, null display, row order | frontend/tests/components/TransactionGrid.test.jsx
- [x] T068 [P2] [Phase 11] [Deps: T047,T059] Component tests — error message display, retry button | frontend/tests/components/ErrorBanner.test.jsx

---

## Phase 12 — Deployment & Documentation

- [x] T069 [P3] [Phase 12] [Deps: T029,T058] Render deployment spec — backend web service + static frontend | render.yaml
- [x] T070 [P3] [Phase 12] [Deps: None] Utility scripts for local development — Unix shell (.sh) and Windows PowerShell (.ps1) variants: setup, start-dev, test-all, build-frontend, clean | scripts/
- [x] T071 [P3] [Phase 12] [Deps: T029,T058] Update README.md with quick-start (OS-specific setup: Mac/Linux shell vs Windows PowerShell) + architecture overview | README.md

---

## Phase 13 — CI/CD Automation (Optional Follow-Up)

- [x] T072 [P3] [Phase 13] [Deps: T029] GitHub Actions CI — pytest on push | .github/workflows/backend-tests.yml
- [x] T073 [P3] [Phase 13] [Deps: T058] GitHub Actions CI — vitest on push | .github/workflows/frontend-tests.yml

---

## Phase 14 — Transaction Type: Gross Purchase Support (Amendment)

> **Context:** Real-world fund statements (e.g., MFUTILITY) include a "Gross Purchase" row that represents the total amount before splitting into "Net Purchase" + "Stamp Duty". This row always has empty Units, Price, and Unit Balance. It must be recognised without error, excluded from XIRR cash flows, and excluded from Total Invested (since Net Purchase and Stamp Duty already account for the same money and are tracked separately).

- [x] T074 [P1] [Phase 14] [Deps: T012] Add GROSS_PURCHASE enum value; GROSS_PURCHASE_VARIANTS frozenset; "gross purchase" keyword in CATEGORY_KEYWORDS (before PURCHASE entry to prevent misclassification); add GROSS_PURCHASE to XIRR_EXCLUDED_CATEGORIES, PRICE_UNIT_BALANCE_EMPTY_CATEGORIES, UNITS_OPTIONAL_CATEGORIES; add GROSS_PURCHASE_NON_EMPTY_PRICE_UNIT_BALANCE error message template; add explanatory comment on why GROSS_PURCHASE is absent from TOTAL_INVESTED_CATEGORIES | backend/app/utils/constants.py

- [x] T075 [P1] [Phase 14] [Deps: T074,T015] Add Tier-1 exact match block for GROSS_PURCHASE_VARIANTS; import GROSS_PURCHASE_VARIANTS from constants | backend/app/utils/transaction_normalizer.py

- [x] T076 [P1] [Phase 14] [Deps: T074,T024] Add GROSS_PURCHASE message branch in the PRICE_UNIT_BALANCE_EMPTY_CATEGORIES error path (appears twice in validator — once for Price check, once for Unit Balance check) | backend/app/services/validator.py

- [x] T077 [P1] [Phase 14] [Deps: T074,T035] Add normalizer tests: Tier-1 exact matches ("Gross Purchase", "gross purchase", "GROSS PURCHASE", "Gross Purchase Systematic"); Tier-2 keyword fallback ("Gross Purchase - via MFUTILITY", "Gross Purchase Systematic - Instalment 2/155"); priority test confirming "Gross Purchase - via MFUTILITY" → GROSS_PURCHASE not PURCHASE; is_known_type() returning True for all above | backend/tests/test_transaction_normalizer.py

- [x] T078 [P1] [Phase 14] [Deps: T074,T031] Add valid_with_gross_purchase() and valid_with_gross_purchase_systematic() fixtures modelling real MFUTILITY pattern: Gross Purchase - via MFUTILITY → Net Purchase → Less: Stamp Duty → SELL | backend/tests/fixtures/test_data.py

- [x] T079 [P1] [Phase 14] [Deps: T074,T078,T033] Add validator tests: valid_with_gross_purchase() passes without error; GROSS_PURCHASE row has units=None, price=None, unit_balance=None; Gross Purchase amount is absent from totalInvested calculation; gross_purchase_with_price() and gross_purchase_with_unit_balance() error cases | backend/tests/test_validator.py

- [x] T080 [P3] [Phase 14] [Deps: None] Update feature spec — add Gross Purchase variants to transaction type list (Section 4.4); add Gross Purchase validation rule alongside Stamp Duty rule (Section 3/Step 4); clarify Total Invested excludes Gross Purchase (Section 5); add Gross Purchase decision log entry (Section 12); update version to 2.1, revised date to June 6, 2026, status to "Ready for Testing and Deployment" | intent/mutual-fund-xirr-tracker-feature.md

- [x] T081 [P3] [Phase 14] [Deps: None] Update product structure doc — add GROSS_PURCHASE to TransactionCategory enum listing; add GROSS_PURCHASE_VARIANTS to variant sets; add "gross purchase" keyword entry in CATEGORY_KEYWORDS with ordering note; update XIRR_EXCLUDED_CATEGORIES, PRICE_UNIT_BALANCE_EMPTY_CATEGORIES, UNITS_OPTIONAL_CATEGORIES listings with explanatory comments; add comprehensive Constants section; add absence-from-TOTAL_INVESTED_CATEGORIES note; update version to 2.2, revised date to June 6, 2026, status to "Ready for Testing and Deployment" | intent/product-structure.md

- [x] T082 [P3] [Phase 14] [Deps: None] Update Intent README — update Key Constraints section to mention Gross Purchase exclusion alongside Stamp Duty; update feature.md entry to v2.1 with status "Ready for Testing and Deployment"; update product-structure.md entry to v2.2 with status "Ready for Testing and Deployment"; update Document Versioning table with new versions and dates; update Version to 3 and Revision; update Document Metadata (last updated date) | intent/Intent_README.md

---

## Phase 15 — Date Format Migration: DD-MMM-YYYY → DD/MM/YYYY (Amendment)

> **Context:** The accepted transaction date format is changing from `DD-MMM-YYYY` (e.g., `15-Jan-2020`) to `DD/MM/YYYY` (e.g., `18/12/2024`). This aligns with the format most Indian fund statement exports use in tabular Excel output. The change touches the core date parser, validation engine, all Pydantic models, the OpenAPI spec, config, frontend formatter, all test fixtures, and all intent/documentation files. Every layer must be updated atomically so no mismatched format references remain.

- [x] T083 [P1] [Phase 15] [Deps: T004] Update `DATE_FORMAT` display label from `"DD-MMM-YYYY"` to `"DD/MM/YYYY"`; update inline comment on strptime conversion code | backend/config.py

- [x] T084 [P1] [Phase 15] [Deps: T083,T014] Replace `_DATE_FMT` constant from `"%d-%b-%Y"` to `"%d/%m/%Y"`; update regex pattern used for pre-validation from `^\d{2}-[A-Za-z]{3}-\d{4}$` to `^\d{2}/\d{2}/\d{4}$`; update `format_date()` output; update all docstrings and inline comments referencing `DD-MMM-YYYY` | backend/app/utils/date_parser.py

- [x] T085 [P1] [Phase 15] [Deps: T084,T012] Update error message template in `INVALID_DATE_FORMAT` from `(expected DD-MMM-YYYY, e.g., 15-Jan-2020)` to `(expected DD/MM/YYYY, e.g., 18/12/2024)`; update any other format-referencing string constants | backend/app/utils/constants.py

- [x] T086 [P1] [Phase 15] [Deps: T084,T024] Update Excel serial-date normalizer inside `validator.py` to produce `DD/MM/YYYY` strings instead of `DD-MMM-YYYY`; update all inline comments referencing the old format | backend/app/services/validator.py

- [x] T087 [P1] [Phase 15] [Deps: T084,T020] Update `date` field `description` and `examples` in Transaction Pydantic model from `"15-Jan-2020"` to `"18/12/2024"` and update docstring | backend/app/models/transaction.py

- [x] T088 [P1] [Phase 15] [Deps: T084,T021,T022] Update all example payloads and field descriptions in `response.py` and `error.py` that embed date strings or format references | backend/app/models/response.py, backend/app/models/error.py

- [x] T089 [P1] [Phase 15] [Deps: T084] Update OpenAPI spec: column requirements description; `pattern` regex for date field (`^\d{2}-[A-Za-z]{3}-\d{4}$` → `^\d{2}/\d{2}/\d{4}$`); all `description` fields and `examples` containing date strings or `DD-MMM-YYYY` references; all inline example error messages | backend/openapi.yaml

- [x] T090 [P1] [Phase 15] [Deps: T085] Update `requirements.txt` comment from `# Better datetime parsing (critical for DD-MMM-YYYY transaction dates)` to reference `DD/MM/YYYY` | backend/requirements.txt

- [x] T091 [P1] [Phase 15] [Deps: T084,T031] Update all valid date strings in `test_data.py` fixtures from `DD-MMM-YYYY` to `DD/MM/YYYY` format; flip `invalid_date_format()` fixture to supply a `DD-MMM-YYYY` string as the invalid example (since that format is now wrong); update fixture docstrings | backend/tests/fixtures/test_data.py

- [x] T092 [P1] [Phase 15] [Deps: T084,T030] Update `invalid_dates_xlsx` fixture description in `conftest.py` from `"DD/MM/YYYY instead of DD-MMM-YYYY"` to `"DD-MMM-YYYY instead of DD/MM/YYYY"` | backend/tests/conftest.py

- [x] T093 [P1] [Phase 15] [Deps: T085,T091,T033] Update `test_validator.py`: change `_raises(..., match="dd-mmm-yyyy")` to match `"dd/mm/yyyy"`; update any inline date literal strings in test rows; update test description strings | backend/tests/test_validator.py

- [x] T094 [P1] [Phase 15] [Deps: T085,T091,T036] Update `test_routes_upload.py`: change assertion `assert "dd-mmm-yyyy" in ...` to `"dd/mm/yyyy"`; update date format assertion test to verify `DD/MM/YYYY` pattern in returned transactions; update any hardcoded date strings | backend/tests/test_routes_upload.py

- [x] T095 [P1] [Phase 15] [Deps: T091,T034,T035,T032] Audit `test_xirr_calculator.py`, `test_transaction_normalizer.py`, and `test_file_parser.py` for any hardcoded `DD-MMM-YYYY` date strings or format references; update to `DD/MM/YYYY` | backend/tests/test_xirr_calculator.py, backend/tests/test_transaction_normalizer.py, backend/tests/test_file_parser.py

- [x] T096 [P2] [Phase 15] [Deps: T044] Update `formatDate()` JSDoc comment and `@param` tag from `DD-MMM-YYYY` to `DD/MM/YYYY`; update any format constant or display label in `constants.js` | frontend/src/services/formatting.js, frontend/src/utils/constants.js

- [x] T097 [P2] [Phase 15] [Deps: T096,T060] Update `formatting.test.js`: rename test description from `'returns date as-is when already in DD-MMM-YYYY format'` to `DD/MM/YYYY`; change test value from `'15-Jan-2020'` to `'18/12/2024'` | frontend/tests/services/formatting.test.js

- [x] T098 [P2] [Phase 15] [Deps: T096,T067] Update `TransactionGrid.test.jsx`: rename test `'displays date column in DD-MMM-YYYY format'`; replace all mock transaction date values from `DD-MMM-YYYY` to `DD/MM/YYYY` format | frontend/tests/components/TransactionGrid.test.jsx

- [x] T099 [P3] [Phase 15] [Deps: None] Update `mutual-fund-xirr-tracker-feature.md`: replace all `DD-MMM-YYYY` references with `DD/MM/YYYY` in validation rules (Section 3), column spec (Section 4), Transaction model code block, all error message examples, constraints table, acceptance checklist, and decision log (Section 12 — rewrite "Why DD-MMM-YYYY?" rationale to "Why DD/MM/YYYY?"); update version to 2.2, revised date to today, status to "Completed" | intent/mutual-fund-xirr-tracker-feature.md

- [x] T100 [P3] [Phase 15] [Deps: None] Update `product-structure.md`: replace `DD-MMM-YYYY` with `DD/MM/YYYY` in `date_parser.py` module comment, processing pipeline description, all example error payloads, and column spec tables; update version to 2.3, revised date to today, status to "Completed" | intent/product-structure.md

- [x] T101 [P3] [Phase 15] [Deps: T099,T100] Update `Intent_README.md`: replace `DD-MMM-YYYY` with `DD/MM/YYYY` in Key Constraints section; update `feature.md` entry to v2.2 and `product-structure.md` entry to v2.3 with new status in Document Versioning table; increment version to 4 and revision; update last-updated date | intent/Intent_README.md

- [x] T102 [P3] [Phase 15] [Deps: None] Update `README.md`: replace `DD-MMM-YYYY` in constraints table, date format row, and all example date strings; update last-updated date if present | README.md

---

## Phase 16 — Developer Documentation (`/docs`)

- [ ] T103 [P3] [Phase 16] [Deps: None] docs/README.md — Documentation index: overview of all docs, when to read each, links | docs/README.md
- [ ] T104 [P3] [Phase 16] [Deps: T070] docs/SETUP.md — Installation & environment setup: prerequisites, .venv creation, backend + frontend setup, running locally | docs/SETUP.md
- [ ] T105 [P3] [Phase 16] [Deps: T029] docs/API.md — Endpoint specifications: POST /api/upload request/response schemas, all error codes, example payloads | docs/API.md
- [ ] T106 [P3] [Phase 16] [Deps: None] docs/ARCHITECTURE.md — Tech stack & design decisions: data flow diagram, service responsibilities, why FastAPI/React/Render, key constraints | docs/ARCHITECTURE.md
- [ ] T107 [P3] [Phase 16] [Deps: T104] docs/DEVELOPMENT.md — Development workflow & conventions: branching, code style, adding a new validation rule, adding a new component | docs/DEVELOPMENT.md
- [ ] T108 [P3] [Phase 16] [Deps: T036,T068] docs/TESTING.md — Testing strategy & coverage: backend pytest layout, frontend vitest layout, how to run, coverage targets, adding new tests | docs/TESTING.md
- [ ] T109 [P3] [Phase 16] [Deps: T069] docs/DEPLOYMENT.md — Render deployment guide: render.yaml walkthrough, first-deploy steps, setting VITE_API_URL, redeploy process | docs/DEPLOYMENT.md
- [ ] T110 [P3] [Phase 16] [Deps: T109] docs/RENDER-FREE-TIER.md — Free tier constraints & workarounds: cold-start delay, memory limit, ephemeral filesystem, concurrent upload limits, skeleton loader rationale | docs/RENDER-FREE-TIER.md
- [ ] T111 [P3] [Phase 16] [Deps: None] docs/TROUBLESHOOTING.md — Common issues & FAQ: venv activation errors, CORS issues, XIRR convergence failures, Render cold-start tip, Excel format errors | docs/TROUBLESHOOTING.md
- [ ] T112 [P3] [Phase 16] [Deps: T106] docs/images/ — Architecture & data flow diagrams (PNG/SVG): system architecture, data flow, component tree | docs/images/

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
| Phase 11 — Frontend Tests | T059–T068 | ✅ Complete |
| Phase 12 — Deployment & Documentation | T069–T071 | ✅ Complete |
| Phase 13 — CI/CD Automation | T072–T073 | ⏳ Pending (Post-Launch) |
| Phase 14 — Gross Purchase Support | T074–T082 | ✅ Complete |
| Phase 15 — Date Format Migration (DD/MM/YYYY) | T083–T102 | ✅ Complete |
| Phase 16 — Developer Documentation | T103–T112 | ⏳ Pending (Post-Launch) |

---

## Document Metadata

- **Type:** Implementation Task Tracker
- **Version:** 2.3
- **Created:** January 15, 2026
- **Last Updated:** June 7, 2026
- **Status:** Active (Phases 1–15 complete; Phase 16 Developer Documentation pending)
- **Coverage:** 112 tasks across 16 phases
- **Author:** Hari (Product Owner & Tech Lead)
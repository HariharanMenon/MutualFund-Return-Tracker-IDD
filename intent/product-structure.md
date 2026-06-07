# Product Structure: MutualFund-Return-Tracker-IDD

**Version:** 2.3  
**Date:** March 19, 2026  
**Last Updated:** June 7, 2026
**Revision:** Date format changed from DD-MMM-YYYY to DD/MM/YYYY
**Context:** Stateless, in-memory file processing on Render free tier (single instance, cold-start delays acceptable)
---

## Overall Product Directory Layout

```
MutualFund-Return-Tracker-IDD/
├── README.md                              # Project overview, quick start guide
├── .gitignore                             # Git ignore rules (Python, Node, Render, OS)
├── .env.example                           # Environment variables template
├── LICENSE                                # Open source license (MIT/Apache)
│
├── intent/                                # Intent & Product Structure Documentation
│   ├── intent_README.md                   # Intent folder guide
│   ├── mutual-fund-xirr-tracker-feature.md # Feature intent document (v1.0)
│   └── product-structure.md               # This file: Product structure & architecture
│
├── backend/                               # Python FastAPI Backend (Render Web Service)
│   ├── main.py                            # FastAPI app entry point
│   ├── config.py                          # Configuration (settings, constants)
│   ├── requirements.txt                   # Python dependencies (pinned versions)
│   ├── runtime.txt                        # Python version for Render (optional)
│   ├── Procfile                           # Process specification for Render
│   ├── openapi.yaml                       # API specs
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       └── upload.py              # POST /api/upload endpoint
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── file_parser.py             # Excel parsing (openpyxl/pandas)
│   │   │   ├── validator.py               # Data validation engine
│   │   │   ├── xirr_calculator.py         # XIRR calculation + summary metrics
│   │   │   └── transaction_processor.py   # Transaction normalization & processing
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py             # Pydantic Transaction model
│   │   │   ├── response.py                # Pydantic response models (UploadResponse)
│   │   │   └── error.py                   # Error/exception models
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── date_parser.py             # Date parsing & validation (DD/MM/YYYY)
│   │   │   ├── transaction_normalizer.py  # Transaction type normalization
│   │   │   ├── constants.py               # Constants (transaction types, limits, errors)
│   │   │   └── logger.py                  # Logging utility
│   │   │
│   │   └── exceptions/
│   │       ├── __init__.py
│   │       ├── validation_error.py        # Custom validation exceptions
│   │       ├── file_error.py              # File processing exceptions
│   │       └── calculation_error.py       # XIRR calculation exceptions
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                    # Pytest configuration & fixtures
│   │   ├── test_file_parser.py            # Unit tests for Excel parsing
│   │   ├── test_validator.py              # Unit tests for validation
│   │   ├── test_xirr_calculator.py        # Unit tests for XIRR calculation
│   │   ├── test_transaction_normalizer.py # Unit tests for normalization
│   │   ├── test_routes_upload.py          # Integration tests for /api/upload
│   │   ├── fixtures/
│   │   │   ├── __init__.py
│   │   │   ├── sample_valid.xlsx          # Valid sample Excel file
│   │   │   ├── sample_invalid_dates.xlsx  # Invalid dates test case
│   │   │   ├── sample_missing_cols.xlsx   # Missing columns test case
│   │   │   ├── sample_stamp_duty.xlsx     # Stamp Duty/STT handling test
│   │   │   ├── sample_no_redemption.xlsx  # Missing final redemption test
│   │   │   ├── sample_large_file.xlsx     # >10k rows test (rejected)
│   │   │   └── test_data.py               # Test data generators
│   │   └── coverage/                      # Coverage reports (auto-generated)
│   │
│   └── logs/                              # Log files (auto-created, ephemeral on Render)
│       └── .gitkeep
│
├── frontend/                              # React + Vite Frontend (Render Static Site)
│   ├── index.html                         # HTML entry point
│   ├── vite.config.js                     # Vite configuration (build, preview)
│   ├── .env.example                       # Frontend environment variables
│   ├── package.json                       # Frontend dependencies (pinned versions)
│   ├── package-lock.json                  # Lock file (commit to git)
│   │
│   ├── src/
│   │   ├── main.jsx                       # React app entry point
│   │   ├── App.jsx                        # Root component (orchestration)
│   │   ├── App.css                        # Global styles
│   │   │
│   │   ├── components/
│   │   │   ├── UploadArea.jsx             # Drag-and-drop upload component
│   │   │   ├── UploadArea.css
│   │   │   │
│   │   │   ├── LoadingSpinner.jsx         # Upload spinner
│   │   │   ├── LoadingSpinner.css
│   │   │   │
│   │   │   ├── SkeletonLoader.jsx         # Grid skeleton loader (cold-start UX)
│   │   │   ├── SkeletonLoader.css
│   │   │   │
│   │   │   ├── XirrDisplay.jsx            # XIRR display panel
│   │   │   ├── XirrDisplay.css
│   │   │   │
│   │   │   ├── SummaryMetrics.jsx         # Summary metrics panel (mandatory)
│   │   │   ├── SummaryMetrics.css
│   │   │   │
│   │   │   ├── TransactionGrid.jsx        # Transaction data grid (6 columns)
│   │   │   ├── TransactionGrid.css
│   │   │   │
│   │   │   ├── ErrorBanner.jsx            # Error display banner
│   │   │   └── ErrorBanner.css
│   │   │
│   │   ├── hooks/
│   │   │   ├── useFileUpload.js           # File upload logic & state
│   │   │   ├── useXirrCalculation.js      # XIRR state management
│   │   │   └── useApi.js                  # API calls with error handling
│   │   │
│   │   ├── services/
│   │   │   ├── api.js                     # API client (fetch-based, simple)
│   │   │   ├── validation.js              # Frontend validation helpers
│   │   │   └── formatting.js              # Data formatting (currency, decimals, dates)
│   │   │
│   │   ├── utils/
│   │   │   ├── constants.js               # Frontend constants (API URLs, messages)
│   │   │   ├── helpers.js                 # Utility functions (format, parse)
│   │   │   └── logger.js                  # Simple console logging
│   │   │
│   │   ├── styles/
│   │   │   ├── variables.css              # CSS custom properties (colors, spacing)
│   │   │   ├── animations.css             # Skeleton shimmer, spinner animations
│   │   │   ├── grid.css                   # Grid layout (6 columns, proportions)
│   │   │   └── responsive.css             # Media queries (mobile, tablet, desktop)
│   │   │
│   │   └── assets/
│   │       ├── icons/                     # SVG icons (upload, check, error, etc.)
│   │       ├── images/                    # Static images (logo, placeholder)
│   │       └── fonts/                     # Custom fonts (if any)
│   │
│   ├── tests/
│   │   ├── setup.js                       # Vitest/Jest configuration
│   │   ├── components/
│   │   │   ├── UploadArea.test.jsx
│   │   │   ├── XirrDisplay.test.jsx
│   │   │   ├── SummaryMetrics.test.jsx
│   │   │   ├── TransactionGrid.test.jsx
│   │   │   └── ErrorBanner.test.jsx
│   │   ├── hooks/
│   │   │   ├── useFileUpload.test.js
│   │   │   └── useApi.test.js
│   │   └── services/
│   │       ├── api.test.js
│   │       └── formatting.test.js
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   └── robots.txt
│   │
│   └── dist/                              # Build output (Render deploys this)
│       └── .gitkeep
│
├── docs/                                  # Documentation (empty for now, created during phases 2-6)
│   └── .gitkeep                           # Placeholder (will contain guides during development)
│
├── .github/
│   └── workflows/
│       ├── backend-tests.yml              # GitHub Actions: pytest on push
│       └── frontend-tests.yml             # GitHub Actions: npm test on push
│
├── scripts/                               # Utility scripts
│   ├── setup.sh                           # One-command dev environment setup (Mac/Linux)
│   ├── start-dev.sh                       # Start both servers locally (Mac/Linux)
│   ├── test-all.sh                        # Run all tests (Mac/Linux)
│   ├── build-frontend.sh                  # Build React for production (Mac/Linux)
│   ├── clean.sh                           # Clean venv, node_modules, caches (Mac/Linux)
│   ├── setup.ps1                          # One-command dev environment setup (Windows)
│   ├── start-dev.ps1                      # Start both servers locally (Windows)
│   ├── test-all.ps1                       # Run all tests (Windows)
│   ├── build-frontend.ps1                 # Build React for production (Windows)
│   └── clean.ps1                          # Clean venv, node_modules, caches (Windows)
│
├── render.yaml                            # Render deployment spec (backend + frontend)
├── .env.example                           # Root-level env template
└── .gitkeep                               # Placeholder for git
```

---

## Directory Structure Explanation

### **Intent Folder (`/intent`)**

**Purpose:** Centralized location for product specification, design decisions, and structural documentation.

| File | Purpose |
|------|---------|
| `Intent_README.md` | Guide to intent folder contents, versioning, update process |
| `mutual-fund-xirr-tracker-feature.md` | Complete feature specification (v1.0 with all clarifications) |
| `product-structure.md` | This file: Product architecture, folder layout, deployment notes |

**Why Separate?**
- Clear distinction between "what we're building" (intent) and "how we're building it" (product structure)
- Easy to reference intent during development
- Version tracking for requirements changes
- Living documentation as product evolves

---

### **Backend (`/backend`)**

#### **Purpose**
- Single FastAPI application (stateless)
- Handles file uploads, validation, XIRR calculation
- In-memory processing (no database, no disk persistence)
- Deploys as Render Web Service (free tier)

#### **Key Files**

**`main.py`** – FastAPI Entry Point
```python
# Key responsibilities:
# - Initialize FastAPI app
# - Configure CORS (allow all origins)
# - Setup middleware (request logging)
# - Register routes (/api/upload)
# - Serve static files (React SPA) from /frontend/dist
# - Health check endpoint (GET / or /health for Render)
```

**`config.py`** – Configuration & Constants
```python
# Settings:
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_TRANSACTIONS = 10000
MIN_DATE = date(1960, 1, 1)
REQUIRED_COLUMNS = ["date", "transaction type", "amount", "units", "price", "unit balance"]
# ... transaction types, error messages, column mapping
```

#### **Backend Constants (`app/utils/constants.py`)**

**TransactionCategory Enum (Canonical Values)**
```python
class TransactionCategory(str, Enum):
    PURCHASE = "PURCHASE"
    SELL = "SELL"
    REDEMPTION = "REDEMPTION"
    DIVIDEND_REINVEST = "DIVIDEND_REINVEST"
    STAMP_DUTY = "STAMP_DUTY"
    GROSS_PURCHASE = "GROSS_PURCHASE"
```

**Transaction Type Variants (Tier 1 — Exact Match)**
- `PURCHASE_VARIANTS`: "purchase", "buy", "sip", "sip purchase", "systematic investment", "systematic investment plan"
- `SELL_VARIANTS`: "sell"
- `REDEMPTION_VARIANTS`: "redemption"
- `DIVIDEND_REINVEST_VARIANTS`: "dividend reinvest", "dividend reinvestment"
- `STAMP_DUTY_VARIANTS`: "stamp duty", "stt paid", "less: stamp duty", "less: stt paid", "stamp duty - stt", "stt"
- `GROSS_PURCHASE_VARIANTS`: "gross purchase", "gross purchase systematic"

**Transaction Type Keywords (Tier 2 — Keyword-Contains Fallback)**
| Category | Keywords |
|----------|----------|
| STAMP_DUTY | "stamp duty", "stt paid", "stt" |
| DIVIDEND_REINVEST | "dividend reinvest", "dividend" |
| REDEMPTION | "redemption", "switch out", "swp" |
| SELL | "sell" |
| GROSS_PURCHASE | "gross purchase" |
| PURCHASE | "switch in", "systematic investment", "purchase", "sip", "buy" |

**Note:** GROSS_PURCHASE keyword is checked **before** PURCHASE to prevent misclassification (e.g., "Gross Purchase - via MFUTILITY" contains "purchase" but must match GROSS_PURCHASE).

**Functional Groupings (Used by Validator & XIRR Calculator)**
```python
# Money outflows in XIRR (negative cash flows)
XIRR_OUTFLOW_CATEGORIES = {PURCHASE, DIVIDEND_REINVEST}

# Money inflows in XIRR (positive cash flows)
XIRR_INFLOW_CATEGORIES = {SELL, REDEMPTION}

# Excluded from XIRR cash flows entirely
XIRR_EXCLUDED_CATEGORIES = {STAMP_DUTY, GROSS_PURCHASE}
# GROSS_PURCHASE excluded because it is a summary row;
# the actual cash flows are captured by Net Purchase + Stamp Duty

# Categories included in Total Invested summary metric
TOTAL_INVESTED_CATEGORIES = {PURCHASE, STAMP_DUTY}
# GROSS_PURCHASE intentionally excluded — would double-count invested amount

# Valid terminal (last) transaction types
TERMINAL_CATEGORIES = {SELL, REDEMPTION}

# Price & Unit Balance must be empty
PRICE_UNIT_BALANCE_EMPTY_CATEGORIES = {SELL, REDEMPTION, STAMP_DUTY, GROSS_PURCHASE}

# Units is optional (can be empty without error)
UNITS_OPTIONAL_CATEGORIES = {STAMP_DUTY, GROSS_PURCHASE}

# Units is required (must be populated)
UNITS_REQUIRED_CATEGORIES = {PURCHASE, SELL, REDEMPTION, DIVIDEND_REINVEST}

# Price & Unit Balance required
PRICE_UNIT_BALANCE_REQUIRED_CATEGORIES = {PURCHASE, DIVIDEND_REINVEST}
```

**Error Message Templates**
- All row-level errors include 1-based row number
- GROSS_PURCHASE error: "Row {row}: Gross Purchase transaction must have empty Price and Unit Balance columns"
- STAMP_DUTY error: "Row {row}: Stamp Duty transaction must have empty Price and Unit Balance columns"
- SELL/REDEMPTION error: "Row {row}: SELL/REDEMPTION transaction must have empty Price and Unit Balance columns"

**`requirements.txt`** – Dependencies (Render installs from this)
```
# Web framework (async HTTP server)
fastapi==0.109.2
uvicorn==0.27.0

# File upload support
python-multipart==0.0.7

# Excel parsing and data processing
openpyxl==3.1.3
pandas==2.3.1

# Financial calculation engine
numpy_financial==1.0.0

# Data validation and serialization
pydantic==2.6.4
pydantic-settings==2.2.1

# Testing Dependencies (Development Only)
pytest==8.2.0
pytest-asyncio==0.24.0
httpx==0.27.0
```

**`Procfile`** (Optional, for Render clarity)
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**`runtime.txt`** (Optional, specifies Python version)
```
python-3.11.7
```

#### **App Services**

**`app/services/file_parser.py`**
- Load Excel file using openpyxl/pandas
- Extract first worksheet only (ignore others)
- Return raw data as list of dicts
- Handle file errors (not found, corrupted, etc.)

**`app/services/validator.py`**
- Validate column headers (case-insensitive, trim spaces)
- Validate each row (date format, types, values, conditional field requirements per transaction type)
- Transaction type-specific rules:
  - **PURCHASE/DIVIDEND_REINVEST:** All fields required (Units, Price, Unit Balance)
  - **SELL/REDEMPTION:** Units required; Price and Unit Balance must be empty
  - **STAMP_DUTY:** Units optional; Price and Unit Balance must be empty
  - **GROSS_PURCHASE:** Units optional; Price and Unit Balance must be empty (summary row, excluded from XIRR and Total Invested)
- Validate file-level rules (final redemption, unit balance consistency)
- Build detailed error messages with row numbers
- Return `ValidationError` on failure, clean data on success

**`app/services/transaction_processor.py`**
- Normalize transaction types (case-insensitive variants, keyword-based fallback for Gross Purchase and others)
- Parse dates to DD/MM/YYYY format
- Round decimals to spec (Amount: 2, Units: 3, Price: 2-4)
- Filter out Stamp Duty/STT and Gross Purchase for XIRR calculation

**`app/services/xirr_calculator.py`**
- Build cash flow array (exclude Stamp Duty/STT and Gross Purchase)
- Calculate XIRR using numpy_financial.irr() or pyxirr
- Handle convergence failures (return error)
- Calculate summary metrics:
  - Total Invested (sum of PURCHASE/SIP/Stamp Duty/STT; **Gross Purchase excluded**)
  - Final Proceeds (SELL/REDEMPTION amount)
  - Profit/Loss (Final Proceeds - Total Invested)
- Return formatted response

#### **API Routes**

**`POST /api/upload`**
```
Request:
  - Content-Type: multipart/form-data
  - file: binary (Excel)

Response (200 OK):
{
  "success": true,
  "xirr": 12.54,
  "summaryMetrics": {
    "totalInvested": 1250000.00,
    "finalProceeds": 1475500.00,
    "profitLoss": 225500.00
  },
  "transactions": [
    { "date": "18/12/2024", "transactionType": "Purchase", ... },
    ...
  ]
}

Response (400 Bad Request):
{
  "success": false,
  "error": {
    "message": "File validation failed",
    "details": "Row 5: Invalid date format 'xyz' (expected DD/MM/YYYY)"
  }
}

Response (413 Payload Too Large):
{
  "success": false,
  "error": {
    "message": "File too large",
    "details": "File size exceeds 10 MB limit"
  }
}

Response (500 Internal Server Error):
{
  "success": false,
  "error": {
    "message": "Cannot calculate XIRR",
    "details": "Cannot calculate XIRR for this data. Please verify all transactions."
  }
}
```

#### **Render Deployment Notes**
- **Build:** `pip install -r backend/requirements.txt`
- **Start:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Cold-start:** ~30 seconds (acceptable; skeleton loader hides this)
- **Ephemeral filesystem:** Logs auto-delete (fine, no persistence needed)
- **Memory limit:** 512 MB (safe with 10k transactions in-memory)
- **No database:** Pure in-memory processing

---

### **Frontend (`/frontend`)**

#### **Purpose**
- React SPA (Single Page Application)
- Vite build tool (fast HMR during dev, optimized builds)
- Deploys as Render Static Site (free tier)
- Pure client-side rendering (no Node.js on server)

#### **Key Files**

**`vite.config.js`** – Vite Configuration
```javascript
export default {
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false  // Disable for free tier optimization
  }
}
```

**`package.json`** – Dependencies
```json
{
  "name": "mf-xirr-tracker-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.1.0"
  }
}
```

#### **Components (7 Total)**

1. **`UploadArea.jsx`** – File input, drag-and-drop, validation
2. **`LoadingSpinner.jsx`** – Shows while uploading (0-2 seconds)
3. **`SkeletonLoader.jsx`** – Shows after 2 seconds (cold-start UX improvement)
4. **`XirrDisplay.jsx`** – Large XIRR percentage (36px+, green/red)
5. **`SummaryMetrics.jsx`** – Total Invested, Final Proceeds, Profit/Loss (mandatory)
6. **`TransactionGrid.jsx`** – 6-column table (Date, Type, Amount, Units, Price, Balance)
7. **`ErrorBanner.jsx`** – Error message + retry button

#### **Hooks (3 Total)**

**`useFileUpload.js`**
- State: file, isLoading, showSkeleton, error
- Logic: validation, upload initiation, error handling
- Returns: state, uploadFile function

**`useXirrCalculation.js`**
- State: xirr, transactions, summaryMetrics
- Logic: updates when API returns data
- Returns: state (read-only in this hook)

**`useApi.js`**
- Logic: fetch call to `/api/upload`
- Error handling: network errors, timeout, validation errors
- Returns: response data or throws error

#### **Services**

**`api.js`** – API Client
```javascript
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_URL}/api/upload`, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) throw new Error('Upload failed');
  return response.json();
};
```

**`formatting.js`** – Data Formatters
- `formatCurrency(amount)` → "₹12,50,000.00"
- `formatDate(dateStr)` → "18/12/2024"
- `formatPercentage(num)` → "12.54%"
- `formatUnits(num)` → "100.123"

**`validation.js`** – Frontend Validation
- `isValidFileSize(file)` → checks ≤ 10 MB
- `isValidFileType(file)` → checks .xlsx only

#### **Styles**

**`variables.css`** – CSS Custom Properties
```css
:root {
  --color-primary: #2563eb;
  --color-success: #059669;
  --color-error: #dc2626;
  --color-bg: #f9fafb;
  --color-border: #e5e7eb;
  
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  
  --font-size-sm: 0.875rem;
  --font-size-md: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 2.25rem;  /* XIRR display */
}
```

**`animations.css`** – Shimmer & Spinner
```css
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

#### **Render Deployment Notes**
- **Build:** `npm run build` (Render auto-runs)
- **Deploy:** Render serves `dist/` folder as static site
- **No server:** Pure static hosting (~no cold-start delay)
- **Environment variables:** Via `.env` or Render dashboard
- **API proxy:** Frontend at `https://mf-xirr.onrender.com`, Backend at same domain (same-origin)

---

### **Tests**

#### **Backend Tests** (`/backend/tests/`)
- **Unit tests:** Each service tested in isolation
- **Fixtures:** Sample Excel files (valid, invalid, edge cases)
- **Integration tests:** `/api/upload` endpoint with mock files
- **Coverage goal:** >80%

**Sample Test Cases:**
- Valid file → returns correct XIRR + metrics
- Missing columns → returns specific error
- Invalid date format → returns row number + error
- Stamp Duty → excluded from XIRR
- No final redemption → validation error
- >10k rows → file size error
- XIRR convergence failure → error response

#### **Frontend Tests** (`/frontend/tests/`)
- **Component tests:** Each component in isolation
- **Hook tests:** useFileUpload, useApi logic
- **Service tests:** API client, formatters
- **Mocked API:** Use fetch mocks for API calls
- **Coverage goal:** >70%

---

### **Documentation** (`/docs`)

**Status:** Empty folder (placeholder for now)

**To be created during phases 2-6:**
- README.md – Documentation index
- SETUP.md – Installation & environment setup
- API.md – Endpoint specifications
- ARCHITECTURE.md – Tech stack & design decisions
- DEVELOPMENT.md – Development workflow & conventions
- TESTING.md – Testing strategy & coverage
- DEPLOYMENT.md – Render deployment guide
- RENDER-FREE-TIER.md – Free tier constraints & workarounds
- TROUBLESHOOTING.md – Common issues & FAQ
- images/ – Diagrams & screenshots

**See:** `/documentation-responsibility-matrix.md` for who creates each document and when

**Folder Structure:**
```
docs/
├── .gitkeep                              # Placeholder
├── (all documentation files added during phases 2-6)
└── images/                               # Diagrams added during development
```

#### **New: `RENDER-FREE-TIER.md`**
This document should include:
- **Cold-start delay:** 30 seconds expected, skeleton loader hides this
- **Memory limit:** 512 MB (safe with 10k transactions, in-memory processing)
- **Ephemeral filesystem:** Logs auto-delete, no persistence needed (fine for stateless MVP)
- **Concurrent uploads:** Single instance shares resources (acceptable for MVP)
- **No background jobs:** Pure sync processing (acceptable)
- **Timeout limits:** May have 30-second request timeout (XIRR calculation must complete <30s)
- **Workarounds:**
  - Skeleton loader + optimistic UI to hide cold-start
  - Monitor calculation time; optimize if needed
  - Consider upgrade path if load increases

---

### **Scripts** (`/scripts/`)

#### **For Unix/Linux/macOS**

**`setup.sh`** – One-command setup
```bash
#!/usr/bin/env bash
# setup.sh — One-command dev environment setup (Mac / Linux)
# Usage: bash scripts/setup.sh
# Run from the repository root.

# Exit immediately if a command exits with a non-zero status
# Treat unset variables as an error, and catch pipeline failures
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Define explicit paths to virtual environment binaries to bypass activation scoping
VENV_PATH="$REPO_ROOT/.venv"
VENV_PYTHON="$VENV_PATH/bin/python3"
VENV_PIP="$VENV_PATH/bin/pip"

# Corporate/Firewall Bypass: Define trusted hosts for pip
TRUSTED_HOSTS=(
  "--trusted-host" "pypi.org"
  "--trusted-host" "files.pythonhosted.org"
  "--trusted-host" "pypi.python.org"
)

echo "==> Setting up backend Python virtual environment..."
# Create the venv if it doesn't already exist
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi

# Upgrade pip and install requirements using direct paths and trusted host flags
"$VENV_PYTHON" -m pip install --upgrade pip --quiet "${TRUSTED_HOSTS[@]}"
"$VENV_PIP" install -r "$REPO_ROOT/backend/requirements.txt" --quiet "${TRUSTED_HOSTS[@]}"
echo "    Backend .venv ready."

echo "==> Setting up frontend Node.js dependencies..."
# Use a subshell ( ... ) to change directories so we automatically 
# snap back to the previous directory when it finishes
(
    cd "$REPO_ROOT/frontend"
    # Note: If npm fails with a similar SSL error, uncomment the line below:
    # npm config set strict-ssl false
    npm install --silent
    echo "    Frontend node_modules ready."
)

echo ""
echo "Setup complete. To start both servers run:"
echo "  bash scripts/start-dev.sh"
```

**`start-dev.sh`** – Start both servers
```bash
#!/usr/bin/env bash
# start-dev.sh — Start backend + frontend dev servers concurrently (Mac / Linux)
# Usage: bash scripts/start-dev.sh
# Run from the repository root.
# Press Ctrl-C to stop both servers.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Define explicit paths to execution tools to bypass virtualenv 'source' leakage
VENV_UVICORN="$REPO_ROOT/.venv/bin/uvicorn"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"

# Fallback to global uvicorn if venv doesn't exist
if [ -f "$VENV_UVICORN" ]; then
    UVICORN_CMD="$VENV_UVICORN"
else
    UVICORN_CMD="uvicorn"
fi

cleanup() {
    echo ""
    echo "==> Stopping servers and cleaning up ports..."
    
    # Kill the entire process group rather than just the single parent PID.
    # This ensures child sub-processes (Node workers, Uvicorn reloaders) are terminated.
    if [ -n "${BACKEND_PID:-}" ]; then
        pkill -P "$BACKEND_PID" 2>/dev/null || true
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    
    if [ -n "${FRONTEND_PID:-}" ]; then
        pkill -P "$FRONTEND_PID" 2>/dev/null || true
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    
    echo "    Done. Ports 8000 and 5173 freed."
}
# Trap exit signals to ensure cleanup runs
trap cleanup EXIT INT TERM

echo "==> Starting backend on http://localhost:8000 ..."
# Run backend inside a cleanly scoped subshell context
(
    cd "$BACKEND_DIR"
    exec "$UVICORN_CMD" main:app --reload --host 127.0.0.1 --port 8000
) &
BACKEND_PID=$!

echo "==> Starting frontend on http://localhost:5173 ..."
# Run frontend inside a cleanly scoped subshell context
(
    cd "$FRONTEND_DIR"
    exec npm run dev
) &
FRONTEND_PID=$!

echo ""
echo "Both servers running concurrently. Press Ctrl-C to stop."

# Wait cleanly for the background processes
wait
```

**`test-all.sh`** – Run all tests
```bash
#!/usr/bin/env bash
# test-all.sh — Run backend pytest + frontend vitest (Mac / Linux)
# Usage: ./scripts/test-all.sh
# Run from the repository root.
# Exits non-zero if any test suite fails.

set -euo pipefail

# Get the directory of the script, then go up one level to the repo root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0

# Define paths to executables
PYTEST_EXE="$REPO_ROOT/.venv/bin/pytest"

# Color codes for clean UI output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --------------------------------------------
# Backend Tests (pytest)
# --------------------------------------------
echo "=============================="
echo " Backend tests (pytest)"
echo "=============================="

if [ ! -x "$PYTEST_EXE" ]; then
    echo "Warning: Virtual environment or pytest executable not found at: $PYTEST_EXE" >&2
    FAILED=1
elif [ ! -d "$REPO_ROOT/backend" ]; then
    echo "Warning: Backend directory missing at $REPO_ROOT/backend" >&2
    FAILED=1
else
    # Wrap in a subshell ( ... ) so directory changes don't affect the rest of the script
    (
        cd "$REPO_ROOT/backend"
        # Run pytest directly from the .venv without activating
        "$PYTEST_EXE" tests/ -v
    ) || FAILED=1
fi

# --------------------------------------------
# Frontend Tests (vitest)
# --------------------------------------------
echo ""
echo "=============================="
echo " Frontend tests (vitest)"
echo "=============================="

if ! command -v npm &> /dev/null; then
    echo "Warning: Node.js/npm is not installed or not in PATH." >&2
    FAILED=1
elif [ ! -d "$REPO_ROOT/frontend" ]; then
    echo "Warning: Frontend directory missing at $REPO_ROOT/frontend" >&2
    FAILED=1
else
    (
        cd "$REPO_ROOT/frontend"
        npm run test
    ) || FAILED=1
fi

# --------------------------------------------
# Test Results Execution
# --------------------------------------------
echo ""
if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}One or more test suites FAILED.${NC}" >&2
    exit 1
fi
```

**`build-frontend.sh`** – Build for production
```bash
#!/usr/bin/env bash
# build-frontend.sh — Build the React + Vite frontend for production (Mac / Linux)
# Usage: bash scripts/build-frontend.sh
# Run from the repository root.
# Output: frontend/dist/  (Render deploys this directory as a static site)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Building frontend..."
cd "$REPO_ROOT/frontend"
npm install --silent
npm run build
echo "    Build complete. Output: frontend/dist/"
```

#### **For Windows**

**`setup.ps1`** – One-command setup
```powershell
# setup.ps1 — One-command dev environment setup (Windows PowerShell)
# Usage: .\scripts\setup.ps1
# Run from the repository root.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# $PSScriptRoot is root/scripts, so Parent is the repository root
$RepoRoot = Split-Path -Parent $PSScriptRoot

# Define explicit paths to avoid scope/activation issues
$VenvPath = Join-Path $RepoRoot ".venv"
$VenvPip  = Join-Path $VenvPath "Scripts\pip.exe"
$VenvPy   = Join-Path $VenvPath "Scripts\python.exe"

# Corporate/Firewall Bypass: Define trusted hosts for pip
$TrustedHosts = @("--trusted-host", "pypi.org", "--trusted-host", "files.pythonhosted.org", "--trusted-host", "pypi.python.org")

Write-Host "==> Setting up backend Python virtual environment..."
# Create the venv if it doesn't exist
if (-not (Test-Path $VenvPath)) {
    python -m venv $VenvPath
}

# Upgrade pip and install requirements using trusted host flags to bypass corporate SSL decryption issues
& $VenvPy -m pip install --upgrade pip --quiet $TrustedHosts
& $VenvPip install -r "$RepoRoot\backend\requirements.txt" --quiet $TrustedHosts
Write-Host "    Backend .venv ready."

Write-Host "==> Setting up frontend Node.js dependencies..."
Push-Location "$RepoRoot\frontend"
try {
    # Note: If npm fails with a similar SSL error, you may need to run: npm config set strict-ssl false
    & npm install --silent
    
    # Check if the external process failed
    if ($LASTEXITCODE -ne 0) {
        throw "npm install failed with exit code $LASTEXITCODE"
    }
    Write-Host "    Frontend node_modules ready."
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Setup complete. To start both servers run:"
Write-Host "  .\scripts\start-dev.ps1"
```

**`start-dev.ps1`** – Start both servers
```powershell
# start-dev.ps1 — Start backend + frontend dev servers (Windows PowerShell)
# Usage: .\scripts\start-dev.ps1
# Run from the repository root.
# Opens the backend in the current terminal and the frontend in a new window.
# Press Ctrl-C in each terminal to stop.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot

# Define explicit paths to execution tools
$VenvUvicorn = Join-Path $RepoRoot ".venv\Scripts\uvicorn.exe"
$BackendDir  = Join-Path $RepoRoot "backend"
$FrontendDir = Join-Path $RepoRoot "frontend"

# Fallback to global uvicorn if venv doesn't exist
$UvicornCmd = if (Test-Path $VenvUvicorn) { $VenvUvicorn } else { "uvicorn" }

Write-Host "==> Starting backend on http://localhost:8000 ..."
# Use a cleaner, single-string format for -ArgumentList to avoid nested quoting bugs
$BackendProcess = Start-Process powershell -ArgumentList "-NoExit -Command `"Set-Location '$BackendDir'; & '$UvicornCmd' main:app --reload --host 127.0.0.1 --port 8000`"" -PassThru

Write-Host "==> Starting frontend on http://localhost:5173 ..."
$FrontendProcess = Start-Process powershell -ArgumentList "-NoExit -Command `"Set-Location '$FrontendDir'; npm run dev`"" -PassThru

Write-Host ""
Write-Host "Both servers launched in separate windows."
Write-Host "Backend Terminal PID : $($BackendProcess.Id)"
Write-Host "Frontend Terminal PID: $($FrontendProcess.Id)"
Write-Host ""
Write-Host "Press ENTER here to stop both servers, or close their windows manually."
$null = Read-Host

Write-Host "==> Stopping servers and cleaning up ports..."

# Helper function to kill the window AND any child processes (Node / Python / Uvicorn) it spawned
function Stop-ProcessTree ($ParentPid) {
    if ($ParentPid) {
        # Visual/Graceful window close first
        Stop-Process -Id $ParentPid -Force -ErrorAction SilentlyContinue
        
        # WMI lookup to catch orphaned child processes holding the ports
        Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $ParentPid } | ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}

Stop-ProcessTree -ParentPid $BackendProcess.Id
Stop-ProcessTree -ParentPid $FrontendProcess.Id

Write-Host "    Done. Ports 8000 and 5173 freed."
```

**`test-all.ps1`** – Run all tests
```powershell
# test-all.ps1 — Run backend pytest + frontend vitest (Windows PowerShell)
# Usage: .\scripts\test-all.ps1
# Run from the repository root.
# Exits with code 1 if any test suite fails.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# If scripts/test-all.ps1, $PSScriptRoot is repo/scripts. Parent is repo root.
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Failed   = $false

# Define paths to executables
$PytestExe = "$RepoRoot\.venv\Scripts\pytest.exe"
$NpmExe    = Get-Command npm -ErrorAction SilentlyContinue

# --------------------------------------------
# Backend Tests (pytest)
# --------------------------------------------
Write-Host "=============================="
Write-Host " Backend tests (pytest)"
Write-Host "=============================="

if (-not (Test-Path $PytestExe)) {
    Write-Warning "Virtual environment or pytest not found at: $PytestExe"
    $Failed = $true
} else {
    Push-Location "$RepoRoot\backend"
    try {
        # Directly call the venv's pytest executable (no activation required)
        & $PytestExe tests/ -v
        if ($LASTEXITCODE -ne 0) { $Failed = $true }
    }
    catch {
        Write-Warning "Backend tests failed to execute: $_"
        $Failed = $true
    }
    finally {
        Pop-Location
    }
}

# --------------------------------------------
# Frontend Tests (vitest)
# --------------------------------------------
Write-Host "`n=============================="
Write-Host " Frontend tests (vitest)"
Write-Host "=============================="

if (-not $NpmExe) {
    Write-Warning "Node.js/npm is not installed or not in PATH."
    $Failed = $true
} else {
    Push-Location "$RepoRoot\frontend"
    try {
        # Using cmd /c ensures npm executes predictably on Windows PowerShell
        cmd /c npm run test
        if ($LASTEXITCODE -ne 0) { $Failed = $true }
    }
    catch {
        Write-Warning "Frontend tests failed to execute: $_"
        $Failed = $true
    }
    finally {
        Pop-Location
    }
}

# --------------------------------------------
# Test Results Execution
# --------------------------------------------
Write-Host ""
if (-not $Failed) {
    Write-Host "All tests passed successfully!" -ForegroundColor Green
    exit 0
} else {
    # Using Write-Host for the error avoids a messy PowerShell script stack trace
    Write-Host "One or more test suites FAILED." -ForegroundColor Red
    exit 1
}
```

**`build-frontend.ps1`** – Build for production
```powershell
# build-frontend.ps1 — Build the React + Vite frontend for production (Windows PowerShell)
# Usage: .\scripts\build-frontend.ps1
# Run from the repository root.
# Output: frontend\dist\  (Render deploys this directory as a static site)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "==> Building frontend..."
Push-Location "$RepoRoot\frontend"
try {
    npm install --silent
    npm run build
    Write-Host "    Build complete. Output: frontend\dist\"
}
finally {
    Pop-Location
}
```

**`clean.ps1`** – Remove generated artefacts
```powershell
# clean.ps1 — Remove generated artefacts (Windows PowerShell)
# Usage: .\scripts\clean.ps1
# Run from the repository root.
# Removes: .venv\ (root), frontend\node_modules, frontend\dist,
#           __pycache__ trees, .pytest_cache, vitest cache.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot

function Remove-IfExists {
    param([string]$Path)
    if (Test-Path $Path) {
        Remove-Item $Path -Recurse -Force
        Write-Host "    Removed: $Path"
    }
}

Write-Host "==> Removing Python virtual environment (root\.venv)..."
Remove-IfExists "$RepoRoot\.venv"

Write-Host "==> Removing Python cache files..."
Get-ChildItem -Path $RepoRoot -Filter "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\.git\\' } |
    ForEach-Object { Remove-Item $_.FullName -Recurse -Force }

Get-ChildItem -Path $RepoRoot -Filter ".pytest_cache" -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\.git\\' } |
    ForEach-Object { Remove-Item $_.FullName -Recurse -Force }

Get-ChildItem -Path $RepoRoot -Filter "*.pyc" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\.git\\' } |
    ForEach-Object { Remove-Item $_.FullName -Force }

Write-Host "==> Removing frontend node_modules..."
Remove-IfExists "$RepoRoot\frontend\node_modules"

Write-Host "==> Removing frontend build output..."
Remove-IfExists "$RepoRoot\frontend\dist"

Write-Host "==> Removing frontend test cache..."
Remove-IfExists "$RepoRoot\frontend\.vitest"

Write-Host "Clean complete."
```

---

### **Render Configuration** (`render.yaml`)

**Create `backend/runtime.txt` (NEW FILE):**
```
python-3.11.7
```

**Deployment Configuration:**
```yaml
# Render Free Tier Deployment Configuration
# Version: 1.0
# Purpose: Deploy MutualFund-Return-Tracker-IDD to Render

services:
  # ============================================
  # Backend Service (FastAPI + Uvicorn)
  # ============================================
  - type: web
    name: mf-xirr-backend
    plan: free
    runtime: python
    rootDir: backend
    
    # Build dependencies
    buildCommand: pip install -r requirements.txt
    
    # Start command
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    
    # Environment variables
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.7
      - key: PORT
        value: 8000

  # ============================================
  # Frontend Service (React + Vite)
  # ============================================
  - type: static_site
    name: mf-xirr-frontend
    plan: free
    
    # Frontend root directory
    rootDir: frontend
    
    # Build command (install deps + build)
    buildCommand: npm install && npm run build
    
    # Static files output directory
    staticPublishPath: dist
    
    # Environment variables for build time
    envVars:
      - key: VITE_API_URL
        value: https://mf-xirr-tracker-backend.onrender.com
        scope: build
```

**Render Free Tier Considerations:**
- ✅ Single backend instance (adequate for MVP)
- ✅ Ephemeral filesystem (fine, no persistence needed)
- ✅ Cold-start delays hidden by skeleton loader
- ✅ 512 MB memory (safe for 10k transaction processing)
- ✅ Python version pinned in `backend/runtime.txt` (ensures consistency)
- ⚠️ No database (stateless by design—no issue)
- ⚠️ Single concurrent upload (rare; acceptable for MVP)
- ⚠️ May spin down after inactivity (documented, expected)

**Key Changes in Updated render.yaml:**
- ✅ Explicit `rootDir` for clearer configuration
- ✅ Build command simplified (removes `cd` navigation)
- ✅ Python version pinned via `backend/runtime.txt`
- ✅ Environment variable scopes defined
- ✅ Comprehensive deployment notes included

---

## Product Structure Key Design Principles

### ✅ **Stateless Architecture**
- No database, no persistent storage
- All processing in-memory
- Perfect for Render free tier
- Results deleted after session ends (user must re-upload)

### ✅ **Single Responsibility**
- Each service handles one concern (file parsing, validation, XIRR calculation)
- Each component displays one piece of UI (Upload, XIRR, Grid, etc.)
- Hooks manage state/side effects for components

### ✅ **Render Free Tier Optimized**
- Backend: Single instance, async FastAPI (handles concurrent requests)
- Frontend: Static site (no cold-start delays)
- Skeleton loader masks backend cold-start (~30 seconds)
- In-memory processing safe with 10k transaction limit

### ✅ **Testability**
- Services isolated (easy to mock)
- Components pure (easy to test with mocked API)
- Fixtures provide realistic test data
- Coverage goals: Backend >80%, Frontend >70%

### ✅ **Documentation Strategy**
- **Intent folder:** Contains feature spec & product structure (complete, ready for ref)
- **Docs folder:** Empty for now, populated during phases 2-6
- **Responsibility:** Clear ownership matrix (see documentation-responsibility-matrix.md)
- **Timing:** Documentation created alongside code (not after)
- **Maintenance:** Each doc owner responsible for updates

### ✅ **Scalability Path**
- Phase 1 (MVP): Render free tier, stateless
- Phase 2 (Growth): Add database, upgrade Render tier
- Phase 3 (Maturity): Add user accounts, persistent storage, multi-fund support

### ✅ **Developer Experience**
- Single `setup.sh` / `setup.ps1` script (Mac/Linux and Windows)
- Single `start-dev.sh` / `start-dev.ps1` script (Mac/Linux and Windows)
- Clear folder naming (services/, components/, hooks/)
- Documented in `/intent` and `/docs`

---

## Development Workflow

### **Local Development**

**Mac/Linux**
```bash
# Clone repo
git clone <repo-url>
cd MutualFund-Return-Tracker-IDD

# Setup
bash scripts/setup.sh

# Start servers
bash scripts/start-dev.sh

# Backend: http://localhost:8000/docs (Swagger)
# Frontend: http://localhost:5173
# API: http://localhost:8000/api/upload
```

**Windows (PowerShell)**
```powershell
# Clone repo
git clone <repo-url>
cd MutualFund-Return-Tracker-IDD

# Setup
.\scripts\setup.ps1

# Start servers
.\scripts\start-dev.ps1

# Backend: http://localhost:8000/docs (Swagger)
# Frontend: http://localhost:5173
# API: http://localhost:8000/api/upload
```

### **Testing**

**Mac/Linux**
```bash
# All tests
bash scripts/test-all.sh

# Backend only
cd backend && python -m pytest tests/

# Frontend only
cd frontend && npm run test
```

**Windows (PowerShell)**
```powershell
# All tests
.\scripts\test-all.ps1

# Backend only
cd backend; python -m pytest tests/

# Frontend only
cd frontend; npm run test
```

### **Deployment to Render**
```bash
# Push to GitHub (same on all platforms)
git push origin main

# Render auto-deploys (via github integration)
# Monitor at https://dashboard.render.com
```

---

## File Organization Summary

| Layer | Location | Purpose |
|-------|----------|---------|
| **Intent & Docs** | `/intent`, `/docs` | Requirements, architecture, guides |
| **Backend Entry** | `backend/main.py` | FastAPI app, routes, middleware |
| **Backend Logic** | `backend/app/services/` | File parsing, validation, XIRR calculation |
| **Backend Models** | `backend/app/models/` | Pydantic schemas, response types |
| **Backend Utils** | `backend/app/utils/` | Date parsing, normalization, constants |
| **Backend Tests** | `backend/tests/` | Unit & integration tests, fixtures |
| **Frontend Entry** | `frontend/src/main.jsx` | React app init |
| **Frontend Root** | `frontend/src/App.jsx` | Root component, state orchestration |
| **Frontend UI** | `frontend/src/components/` | 7 presentational components |
| **Frontend Logic** | `frontend/src/hooks/` | 3 custom hooks (upload, XIRR, API) |
| **Frontend Data** | `frontend/src/services/` | API client, formatters, validators |
| **Frontend Styles** | `frontend/src/styles/` | Global CSS, animations, responsive |
| **Frontend Tests** | `frontend/tests/` | Component, hook, service tests |
| **Deployment** | `render.yaml`, `Procfile` | Render config, process spec |
| **Scripts** | `/scripts` | Setup, dev, test, build automation |

---

## Free Tier Constraints & Mitigation

| Constraint | Impact | Mitigation |
|-----------|--------|-----------|
| **Cold-start delay (30s)** | User waits for response | Skeleton loader + optimistic UI hides delay |
| **512 MB memory** | Limits transaction count | 10k row limit safe, in-memory processing |
| **Ephemeral filesystem** | Logs deleted daily | Acceptable; no persistence needed (stateless) |
| **Single instance** | Concurrent requests queue | Acceptable; users rarely overlap; async FastAPI handles queuing |
| **Spins down after inactivity** | Slow first request after idle | Skeleton loader + documented expected behavior |
| **No database** | Can't persist user data | By design; MVP is stateless; users re-upload to recalculate |

---

## Versioning & Updates

### **Intent Document (`intent/mutual-fund-xirr-tracker-feature.md`)**
- Version 2.2 (current, June 7, 2026 — Date format changed from DD-MMM-YYYY to DD/MM/YYYY)
- Update when feature scope changes
- Backward-compatible with existing product structure

### **Product Structure (`intent/product-structure.md`)**
- Version 2.3 (current, June 7, 2026 — Date format changed from DD-MMM-YYYY to DD/MM/YYYY)
- Update when folder layout, tech stack, or transaction types change
- Independent from intent versioning

### **Code**
- Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
- Tag releases on GitHub
- Render auto-deploys from main branch

---

## Quick Reference

### **Starting Development**

Mac/Linux:
```bash
bash scripts/setup.sh && bash scripts/start-dev.sh
```
Windows (PowerShell):
```powershell
.\scripts\setup.ps1; .\scripts\start-dev.ps1
```

### **Running Tests**

Mac/Linux:
```bash
bash scripts/test-all.sh
```
Windows (PowerShell):
```powershell
.\scripts\test-all.ps1
```

### **Building for Render**

Mac/Linux:
```bash
bash scripts/build-frontend.sh
```
Windows (PowerShell):
```powershell
.\scripts\build-frontend.ps1
```

### **Cleaning Generated Artefacts**

Mac/Linux:
```bash
bash scripts/clean.sh
```
Windows (PowerShell):
```powershell
.\scripts\clean.ps1
```

### **API Playground**
- Backend: `http://localhost:8000/docs` (Swagger UI)
- Test upload: POST to `/api/upload` with Excel file

### **Environment Variables**
- **Backend:** None required (stateless)
- **Frontend:** `VITE_API_URL` (default: `http://localhost:8000`)

---

## Success Metrics

- ✅ Product structure mirrors intent document
- ✅ Development setup <5 minutes with `setup.sh` (Mac/Linux) or `setup.ps1` (Windows)
- ✅ Backend tests >80% coverage
- ✅ Frontend tests >70% coverage
- ✅ Cold-start UX acceptable (skeleton loader hides delay)
- ✅ Render deployment simple (single `render.yaml`)
- ✅ Scaling path clear (stateless → database → persistence)

---

**End of Product Structure Document**

---

### Sign-Off
- **Product Owner:** Hari
- **Last Updated:** June 7, 2026 (Date format changed from DD-MMM-YYYY to DD/MM/YYYY)
- **Status:** Completed — Date Format Migration (DD/MM/YYYY)
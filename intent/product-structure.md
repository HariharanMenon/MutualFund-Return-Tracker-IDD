# Product Structure: MutualFund-Return-Tracker-IDD

**Version:** 1.0  
**Date:** March 19, 2026  
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
│   ├── README.md                          # Intent folder guide
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
│   │   │   ├── date_parser.py             # Date parsing & validation (DD-MMM-YYYY)
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
│   ├── setup.sh                           # One-command dev environment setup
│   ├── start-dev.sh                       # Start both servers locally
│   ├── test-all.sh                        # Run all tests (backend + frontend)
│   ├── build-frontend.sh                  # Build React (Render auto-runs)
│   └── clean.sh                           # Clean venv, node_modules, caches
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
| `README.md` | Guide to intent folder contents, versioning, update process |
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

**`requirements.txt`** – Dependencies (Render installs from this)
```
fastapi==0.104.1
uvicorn==0.24.0
openpyxl==3.11.0
pandas==2.1.0
numpy_financial==1.0.0  # or pyxirr==0.10.x
pydantic==2.5.0
python-multipart==0.0.6
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
- Validate each row (date format, types, values)
- Validate file-level rules (final redemption, unit balance consistency)
- Build detailed error messages with row numbers
- Return `ValidationError` on failure, clean data on success

**`app/services/transaction_processor.py`**
- Normalize transaction types (case-insensitive variants)
- Parse dates to DD-MMM-YYYY format
- Round decimals to spec (Amount: 2, Units: 3, Price: 2-4)
- Filter out Stamp Duty/STT for XIRR calculation

**`app/services/xirr_calculator.py`**
- Build cash flow array (exclude Stamp Duty/STT)
- Calculate XIRR using numpy_financial.irr() or pyxirr
- Handle convergence failures (return error)
- Calculate summary metrics:
  - Total Invested (sum of PURCHASE/SIP/Stamp Duty/STT)
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
    { "date": "15-Jan-2020", "transactionType": "Purchase", ... },
    ...
  ]
}

Response (400 Bad Request):
{
  "success": false,
  "error": {
    "message": "File validation failed",
    "details": "Row 5: Invalid date format 'xyz' (expected DD-MMM-YYYY)"
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
- `formatDate(dateStr)` → "15-Jan-2020"
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

**`setup.sh`** – One-command setup
```bash
#!/bin/bash
# Create Python venv
python3 -m venv backend/venv

# Activate + install backend deps
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# Install frontend deps
cd frontend && npm install && cd ..

echo "Setup complete! Run ./scripts/start-dev.sh to start"
```

**`start-dev.sh`** – Start both servers
```bash
#!/bin/bash
# Start backend (Terminal 1)
cd backend
source venv/bin/activate
uvicorn main:app --reload &

# Start frontend (Terminal 2)
cd frontend
npm run dev &

wait
```

**`test-all.sh`** – Run all tests
```bash
#!/bin/bash
cd backend && python -m pytest tests/ && cd ..
cd frontend && npm test && cd ..
```

**`build-frontend.sh`** – Build for production
```bash
#!/bin/bash
cd frontend
npm run build
echo "Frontend built to /frontend/dist"
```

---

### **Render Configuration** (`render.yaml`)

```yaml
# Render free tier deployment spec
services:
  # Backend: Web Service
  - type: web
    name: mf-xirr-backend
    plan: free
    runtime: python
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    buildCommand: pip install -r backend/requirements.txt
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.7

  # Frontend: Static Site
  - type: static_site
    name: mf-xirr-frontend
    plan: free
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_API_URL
        value: https://mf-xirr-backend.onrender.com
```

**Render Free Tier Considerations:**
- ✅ Single backend instance (adequate for MVP)
- ✅ Ephemeral filesystem (fine, no persistence needed)
- ✅ Cold-start delays hidden by skeleton loader
- ✅ 512 MB memory (safe for 10k transaction processing)
- ⚠️ No database (stateless by design—no issue)
- ⚠️ Single concurrent upload (rare; acceptable for MVP)
- ⚠️ May spin down after inactivity (documented, expected)

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
- Single `setup.sh` script
- Single `start-dev.sh` script
- Clear folder naming (services/, components/, hooks/)
- Documented in `/intent` and `/docs`

---

## Development Workflow

### **Local Development**
```bash
# Clone repo
git clone <repo-url>
cd MutualFund-Return-Tracker-IDD

# Setup
./scripts/setup.sh

# Start servers
./scripts/start-dev.sh

# Backend: http://localhost:8000/docs (Swagger)
# Frontend: http://localhost:5173
# API: http://localhost:8000/api/upload
```

### **Testing**
```bash
# All tests
./scripts/test-all.sh

# Backend only
cd backend && python -m pytest tests/

# Frontend only
cd frontend && npm test
```

### **Deployment to Render**
```bash
# Push to GitHub
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

### **Intent Document (`intent/feature-intent.md`)**
- Version 1.0 (current, March 19, 2026)
- Update when feature scope changes
- Backward-compatible with existing product structure

### **Product Structure (`intent/product-structure.md`)**
- Version 1.0 (current, March 19, 2026)
- Update when folder layout or tech stack changes
- Independent from intent versioning

### **Code**
- Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
- Tag releases on GitHub
- Render auto-deploys from main branch

---

## Quick Reference

### **Starting Development**
```bash
./scripts/setup.sh && ./scripts/start-dev.sh
```

### **Running Tests**
```bash
./scripts/test-all.sh
```

### **Building for Render**
```bash
./scripts/build-frontend.sh
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
- ✅ Development setup <5 minutes with `setup.sh`
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
- **Created:** March 19, 2026
- **Last Updated:** March 19, 2026
- **Status:** Ready for Phase 2 (Backend Build)

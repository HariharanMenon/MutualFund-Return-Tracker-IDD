# MutualFund-Return-Tracker-IDD

A stateless web application that calculates **XIRR (Extended Internal Rate of Return)** for
Indian mutual fund transactions. Upload an Excel statement and instantly see your annualised
return, summary metrics, and the full transaction grid.

Built with an **Intent-Driven Development (IDD)** methodology — every implementation decision
traces directly back to a documented intent.

---

## Features

- Drag-and-drop or file-picker upload of `.xlsx` mutual fund statements
- Strict data validation with row-level error messages
- XIRR calculation (excludes Stamp Duty / STT from cash flows)
- Summary metrics: Total Invested, Final Proceeds, Profit/Loss
- 6-column transaction grid displayed in file order
- Skeleton loader for cold-start UX (Render free tier)
- Fully stateless — no database, no persistence

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | React 18 + Vite 5                   |
| Backend    | Python 3.11 + FastAPI               |
| Validation | Pydantic v2                         |
| Parsing    | openpyxl / pandas                   |
| XIRR       | numpy-financial                     |
| Deployment | Render (free tier — web + static)   |

---

## Prerequisites

| Tool       | Minimum version |
|------------|-----------------|
| Python     | 3.11            |
| Node.js    | 18              |
| npm        | 9               |
| Git        | any             |

---

## Quick Start

### Option A — Automated setup script

**Mac / Linux**
```bash
git clone https://github.com/HariharanMenon/MutualFund-Return-Tracker-IDD.git
cd MutualFund-Return-Tracker-IDD
bash scripts/setup.sh        # create .venv + install dependencies
bash scripts/start-dev.sh    # start backend (8000) + frontend (5173)
```

**Windows PowerShell**
```powershell
git clone https://github.com/HariharanMenon/MutualFund-Return-Tracker-IDD.git
cd MutualFund-Return-Tracker-IDD
.\scripts\setup.ps1          # create .venv + install dependencies
.\scripts\start-dev.ps1      # start backend (8000) + frontend (5173)
```

> Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### Option B — Manual setup

#### Backend

**Mac / Linux**
```bash
# Run from the repository root
python3 -m venv .venv
source .venv/bin/activate
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Windows PowerShell**
```powershell
# Run from the repository root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

#### Frontend

```bash
# Mac / Linux / Windows (same commands)
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

---

## Running Tests

**Mac / Linux**
```bash
bash scripts/test-all.sh
```

**Windows PowerShell**
```powershell
.\scripts\test-all.ps1
```

Or run each suite independently:

```bash
# Backend — activate .venv first (from repo root), then run from backend/
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
cd backend
python -m pytest tests/ -v

# Frontend (from frontend/)
cd frontend
npm run test
```

---

## Building for Production

**Mac / Linux**
```bash
bash scripts/build-frontend.sh   # outputs to frontend/dist/
```

**Windows PowerShell**
```powershell
.\scripts\build-frontend.ps1     # outputs to frontend\dist\
```

---

## Available Scripts

All scripts live in `scripts/` and must be run from the **repository root**.

| Script            | Mac / Linux              | Windows PowerShell           | Purpose                              |
|-------------------|--------------------------|------------------------------|--------------------------------------|
| Setup             | `bash scripts/setup.sh`  | `.\scripts\setup.ps1`        | Create .venv + install all deps      |
| Start dev servers | `bash scripts/start-dev.sh` | `.\scripts\start-dev.ps1` | Start backend + frontend             |
| Run all tests     | `bash scripts/test-all.sh` | `.\scripts\test-all.ps1`  | pytest + vitest                      |
| Build frontend    | `bash scripts/build-frontend.sh` | `.\scripts\build-frontend.ps1` | Vite production build     |
| Clean artefacts   | `bash scripts/clean.sh`  | `.\scripts\clean.ps1`        | Remove .venv, node_modules, dist, caches |

---

## Architecture Overview

```
User Browser
     │
     │  POST /api/upload  (multipart/form-data, .xlsx)
     ▼
┌──────────────────────────────────────────────────────┐
│                FastAPI Backend (Python)              │
│                                                      │
│  file_parser.py      → Load first worksheet only     │
│  validator.py        → 15 validation rules, row-level│
│  transaction_processor.py → Normalise types + dates  │
│  xirr_calculator.py  → Build cash flows, call XIRR  │
│                                                      │
│  Response: { xirr, summaryMetrics, transactions[] }  │
└──────────────────────────────────────────────────────┘
     │
     │  JSON response
     ▼
┌──────────────────────────────────────────────────────┐
│                React Frontend (Vite SPA)             │
│                                                      │
│  UploadArea      → drag-drop / file picker           │
│  LoadingSpinner  → shown 0–2 s during upload         │
│  SkeletonLoader  → shown after 2 s (cold-start UX)   │
│  XirrDisplay     → large %, green/red                │
│  SummaryMetrics  → Invested / Proceeds / P&L         │
│  TransactionGrid → 6-col table, file order           │
│  ErrorBanner     → validation / server errors        │
└──────────────────────────────────────────────────────┘
```

### Data Flow Summary

1. User uploads `.xlsx` → frontend validates size (≤ 10 MB) and type (`.xlsx`)
2. FastAPI receives file → `file_parser` extracts first worksheet
3. `validator` applies 15 rules (column names, date format, types, file-level invariants)
4. `transaction_processor` normalises types and dates
5. `xirr_calculator` builds cash flows (excluding Stamp Duty/STT), calls `numpy_financial`, computes summary metrics
6. Response JSON → React state → components render

### Key Constraints

| Constraint          | Value / Rule                                     |
|---------------------|--------------------------------------------------|
| Max file size       | 10 MB                                            |
| Max transactions    | 10,000 rows                                      |
| Date format         | DD/MM/YYYY only (e.g., 18/12/2024)               |
| Date range          | 01/01/1960 → today                               |
| Final transaction   | Must be SELL/REDEMPTION with Unit Balance = 0    |
| Stamp Duty / STT    | Included in Total Invested; excluded from XIRR   |
| Worksheets          | First sheet only; extras are ignored             |
| Persistence         | None — fully in-memory, stateless                |

---

## Performance Targets

The application is designed to meet these success metrics:

| Metric | Target |
|--------|--------|
| XIRR calculation | < 5 seconds (excluding Render cold-start) |
| File parsing + validation | < 2 seconds |
| Initial page load | < 2 seconds |
| User error resolution | 90%+ on first attempt (via specific error messages) |
| XIRR accuracy | Verified against Excel's XIRR function |

See [`intent/mutual-fund-xirr-tracker-feature.md`](intent/mutual-fund-xirr-tracker-feature.md) §14 for details.

---

## Deployment (Render)

The `render.yaml` blueprint deploys both services:

| Service  | Render type   | Root dir   | Build command                  | Start / publish          |
|----------|---------------|------------|--------------------------------|--------------------------|
| Backend  | Web service   | `backend/` | `pip install -r requirements.txt` | `uvicorn main:app ...` |
| Frontend | Static site   | `frontend/`| `npm install && npm run build` | `dist/`                  |

Steps:
1. Fork / clone the repository to your GitHub account.
2. Connect the repository to Render via **Blueprints**.
3. After the backend service is first deployed, copy its URL and set the
   `VITE_API_URL` environment variable on the frontend service.
4. Trigger a redeploy of the frontend.

> **Cold starts:** The Render free tier spins down after 15 minutes of inactivity.
> The skeleton loader is specifically designed to keep the UI responsive during the
> ~30-second cold-start delay.

---

## Project Structure

```
MutualFund-Return-Tracker-IDD/
├── .gitignore                   # Git ignore rules (Python, Node, Render, OS)
├── .env.example                 # Root-level environment variables template
├── LICENSE                      # MIT licence
├── render.yaml                  # Render deployment blueprint
├── scripts/                     # Dev utility scripts (.sh + .ps1)
├── intent/                      # IDD — feature spec + product structure docs
├── backend/                     # FastAPI application
│   ├── main.py                  # App entry point
│   ├── config.py                # Settings (file limits, dates, CORS)
│   ├── requirements.txt         # Pinned Python dependencies
│   ├── openapi.yaml             # API specification
│   ├── Procfile                 # Render process definition
│   ├── runtime.txt              # Python version for Render
│   ├── pytest.ini               # pytest configuration
│   └── app/
│       ├── api/routes/upload.py # POST /api/upload
│       ├── services/            # file_parser, validator, processor, xirr_calculator
│       ├── models/              # Pydantic models (Transaction, UploadResponse, ErrorDetail)
│       ├── utils/               # date_parser, transaction_normalizer, constants, logger
│       └── exceptions/          # Custom exception classes
└── frontend/                    # React + Vite SPA
    ├── src/
    │   ├── components/          # 7 UI components
    │   ├── hooks/               # useFileUpload, useXirrCalculation, useApi
    │   ├── services/            # api.js, formatting.js, validation.js
    │   └── styles/              # variables.css, animations.css, grid.css, responsive.css
    └── tests/                   # Vitest component + hook + service tests
```

---

## Intent-Driven Development (IDD)

This project is built using **Intent-Driven Development** — a methodology where every implementation decision is traced back to documented intent.

### What is IDD?
**Intent-Driven Development** means:
- **Single source of truth:** All feature requirements, architecture decisions, and design rationale are documented upfront in the [`intent/`](intent/) folder
- **Traceability:** Every line of code, test, or documentation references the specific intent document sections that justify it
- **Reduced ambiguity:** Feature specs, architecture docs, and decision logs eliminate guesswork during development
- **Easier onboarding:** New developers can understand *why* something was built a certain way, not just *how*

### IDD in This Project
This project maintains three core intent documents:
| Document | Purpose | Key Sections |
|----------|---------|--------------|
| [`mutual-fund-xirr-tracker-feature.md`](intent/mutual-fund-xirr-tracker-feature.md) (v2.0) | Feature specification | User journeys, API contracts, 15 validation rules, edge cases, testing checklist, decision log |
| [`product-structure.md`](intent/product-structure.md) (v1.0) | Technical architecture | Folder layout, tech stack rationale, Render free tier optimization, development workflow |
| [`Intent_README.md`](intent/Intent_README.md) | Folder guide | How to read and use intent documents across development phases |

### Benefits
✅ **For Contributors:** Reference intent docs to understand *why* code is structured a certain way  
✅ **For Code Review:** Reviewers check that implementations match the documented spec  
✅ **For Maintenance:** Future enhancements can trace back to original decisions and constraints  
✅ **For Documentation:** README and inline code comments reference specific intent sections (e.g., "See feature.md §6 for validation rules")

### Getting Started with Intent
1. **First time?** Start with [`Intent_README.md`](intent/Intent_README.md) — it guides you through the folder
2. **Building backend?** Reference [`mutual-fund-xirr-tracker-feature.md`](intent/mutual-fund-xirr-tracker-feature.md) for API contracts and validation logic
3. **Building frontend?** Reference [`mutual-fund-xirr-tracker-feature.md`](intent/mutual-fund-xirr-tracker-feature.md) §4 for UI requirements
4. **Deploying?** Reference [`product-structure.md`](intent/product-structure.md) for Render configuration and scaling

---
## Troubleshooting

### Venv activation fails on Windows

**Error:** `Set-ExecutionPolicy : PowerShell script execution is disabled`

**Solution:** Allow PowerShell scripts to run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### CORS errors when calling backend from frontend

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:** Verify:
- Backend is running on port 8000: `http://localhost:8000`
- Frontend proxy is configured in `vite.config.js`
- CORS headers are configured in `backend/config.py`

### XIRR calculation fails with convergence error

**Error:** `Cannot calculate XIRR for this data`

**Solution:** Verify your Excel file has:
- At least 2 transactions (1 buy + 1 redemption minimum)
- Final transaction is SELL/REDEMPTION with Unit Balance = 0
- All dates in DD/MM/YYYY format (e.g., 18/12/2024)
- No missing required columns

See [`intent/mutual-fund-xirr-tracker-feature.md`](intent/mutual-fund-xirr-tracker-feature.md) §6 for complete validation rules.

### Tests fail to run

**Solution:** Ensure you're running from the repository root and have activated the virtual environment:
```bash
source .venv/bin/activate           # Mac/Linux
.venv\Scripts\Activate.ps1          # Windows
cd backend
python -m pytest tests/ -v
```

---

## Future Enhancements

Planned features for v2+:

| Feature | Description | Impact |
|---------|-------------|--------|
| **Portfolio Aggregation** | Upload multiple statements; view combined portfolio metrics | High |
| **Transaction History** | Persistent session storage (browser localStorage) with upload history | Medium |
| **Advanced Filtering** | Filter transactions by date range, type, or category | Low |
| **Custom Date Formats** | Support additional date formats beyond DD/MM/YYYY | Low |

**Design Principles for v2:**
- Maintain stateless backend; use browser localStorage or session exports for persistence
- All enhancements must remain within Render free tier constraints (512 MB RAM, 100,000 monthly requests)
- New features are **optional** — core XIRR + summary metrics remain unchanged

---

## Getting Help
### Documentation
- **Quick start issues?** See [Troubleshooting](#troubleshooting) above
- **Want to understand the architecture?** Read [`product-structure.md`](intent/product-structure.md)
- **Need validation rules?** See [`mutual-fund-xirr-tracker-feature.md`](intent/mutual-fund-xirr-tracker-feature.md) §6
- **Curious about API design?** See [`mutual-fund-xirr-tracker-feature.md`](intent/mutual-fund-xirr-tracker-feature.md) §10.2
- **Setting up development?** See [Quick Start](#quick-start) above

### Performance Debugging
If you encounter slow uploads or calculation times:
1. Check backend logs: `backend/logs/`
2. Verify file size: < 10 MB
3. Check transaction count: 2–10,000 rows
4. Run [`test_xirr_calculator.py`](backend/tests/test_xirr_calculator.py) with your file format
5. See [Performance Targets](#performance-targets) for expected benchmarks

### Version Info
- **Project version:** See `package.json` and `requirements.txt`
- **Python:** 3.11+ (see `backend/runtime.txt`)
- **Node.js:** 18+ (see `frontend/package.json`)
- **Documentation version:** [Intent folder version](intent/)

---

## License

MIT

---

*Last updated: June 7, 2026 — Date format changed from DD-MMM-YYYY to DD/MM/YYYY*
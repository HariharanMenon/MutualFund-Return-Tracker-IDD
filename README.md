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
bash scripts/setup.sh        # create venv + install dependencies
bash scripts/start-dev.sh    # start backend (8000) + frontend (5173)
```

**Windows PowerShell**
```powershell
git clone https://github.com/HariharanMenon/MutualFund-Return-Tracker-IDD.git
cd MutualFund-Return-Tracker-IDD
.\scripts\setup.ps1          # create venv + install dependencies
.\scripts\start-dev.ps1      # start backend (8000) + frontend (5173)
```

> Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### Option B — Manual setup

#### Backend

**Mac / Linux**
```bash
# Run from the repository root
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

**Windows PowerShell**
```powershell
# Run from the repository root
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
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
# Backend (from backend/)
python -m pytest tests/ -v

# Frontend (from frontend/)
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
| Setup             | `bash scripts/setup.sh`  | `.\scripts\setup.ps1`        | Create venv + install all deps       |
| Start dev servers | `bash scripts/start-dev.sh` | `.\scripts\start-dev.ps1` | Start backend + frontend             |
| Run all tests     | `bash scripts/test-all.sh` | `.\scripts\test-all.ps1`  | pytest + vitest                      |
| Build frontend    | `bash scripts/build-frontend.sh` | `.\scripts\build-frontend.ps1` | Vite production build     |
| Clean artefacts   | `bash scripts/clean.sh`  | `.\scripts\clean.ps1`        | Remove venv, node_modules, dist, caches |

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
| Date format         | DD-MMM-YYYY only (e.g., 15-Jan-2020)             |
| Date range          | 1960-01-01 → today                               |
| Final transaction   | Must be SELL/REDEMPTION with Unit Balance = 0    |
| Stamp Duty / STT    | Included in Total Invested; excluded from XIRR   |
| Worksheets          | First sheet only; extras are ignored             |
| Persistence         | None — fully in-memory, stateless                |

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
├── render.yaml                  # Render deployment blueprint
├── scripts/                     # Dev utility scripts (.sh + .ps1)
├── intent/                      # IDD — feature spec + product structure docs
├── backend/                     # FastAPI application
│   ├── main.py                  # App entry point
│   ├── config.py                # Settings (file limits, dates, CORS)
│   ├── requirements.txt         # Pinned Python dependencies
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

## Intent

See [`intent/`](intent/) for the full feature specification and product structure document.

- [`intent/mutual-fund-xirr-tracker-feature.md`](intent/mutual-fund-xirr-tracker-feature.md) — Feature specification (v2.0)
- [`intent/product-structure.md`](intent/product-structure.md) — Architecture & directory layout
- [`intent/Intent_README.md`](intent/Intent_README.md) — Guide to the intent folder

---

## License

MIT

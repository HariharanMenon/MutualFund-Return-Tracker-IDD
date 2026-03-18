# Intent: Mutual Fund XIRR Return Tracker

**Date:** March 18, 2026  
**Status:** Feature Specification – Ready for Development  
**Priority:** MVP (Minimum Viable Product)

---

## 1. Feature Overview

A **stateless web application** that allows users to upload an Excel file containing mutual fund transaction history for a **single fund** and instantly calculates the **XIRR (Extended Internal Rate of Return)** — the annualized return on investment.

The application provides:
- **Excel File Upload** via drag-and-drop or file picker
- **Transaction Grid Display** showing all transactions in a sortable (future) data table
- **XIRR Calculation** prominently displayed with annualized return percentage
- **Optimized Loading States** with spinner (upload) and detailed skeleton loader (backend processing)
- **Strict Data Validation** with detailed error messages

---

## 2. Architecture Overview

### Technology Stack
- **Frontend:** React (SPA)
- **Backend:** Python FastAPI (async)
- **Hosting:** Render Free Tier (single instance, no database)
- **File Processing:** In-memory (no persistence)

### Data Flow
```
User Browser
    ↓
  Upload Excel (FormData)
    ↓
FastAPI Backend (async file handler)
    ↓
Validation + XIRR Calculation (in-memory)
    ↓
Response: {transactions[], xirr: num, validationErrors?}
    ↓
React State Update + Render Grid + Display XIRR
```

---

## 3. User Journey

### Step 1: Access the Application
- User loads the web page (React SPA)
- Sees a clean interface with:
  - Upload area (drag-and-drop + file input)
  - XIRR display area (initially empty/instructional)
  - Grid area (initially empty/instructional)

### Step 2: Upload Excel File
- User uploads Excel file (e.g., mutual_fund_transactions.xlsx)
- **Upload validation** (frontend):
  - File is `.xlsx` format
  - File size ≤ 10 MB
- **Upload spinner starts** (shows "Uploading..." with animated spinner)

### Step 3: Backend Processing
- FastAPI receives multipart file upload
- **File parsing** (openpyxl or pandas):
  - Extract worksheet data
  - Validate columns exist: `Date, Transaction Type, Amount, Units, Price, Unit Balance`
  - Parse each column with strict type checking (with conditional optional fields based on transaction type)

### Step 4: Validation & Error Handling (Strict Mode)
If **any** of the following occur → **reject file with detailed error**:
- Missing required column(s) (Date, Transaction Type, Amount)
- **For Stamp Duty transactions:** Price and Unit Balance must be empty/null; Units is optional (can be empty)
- **For SELL/REDEMPTION transactions:** Price and Unit Balance must be empty/null (only Date, Transaction Type, Amount, Units required)
- **For BUY/Purchase/Systematic Investment Purchase (SIP)/DIVIDEND REINVEST transactions:** All columns required (Date, Transaction Type, Amount, Units, Price, Unit Balance)
- Invalid data types in any row (e.g., non-date in Date column, non-numeric where required)
- Negative amounts (except for SELL/REDEMPTION which have specific handling)
- Missing final redemption/sale transaction (XIRR requires terminal cash flow)
- Inconsistent unit balance where provided (cumulative units don't match Unit Balance column)
- Not enough transactions (< 2 transactions minimum)
- More than 10,000 transactions (too large for this tier)

Return to user: **Specific error message** (e.g., "Row 5: Date column contains invalid format 'xyz' (expected DD-MMM-YYYY)")

### Step 5: Successful Processing
1. **Grid loads** with skeleton loader visible during cold-start delay (Render)
   - Skeleton shows 6-column structure matching final grid layout
   - Displays ~8 fake rows with shimmer animation
2. **Spinner removed** when data arrives
3. **Grid populates** with transaction data (file order, no sorting)
4. **XIRR prominently displayed**:
   - Large, bold font
   - Green if positive, red if negative
   - Format: "12.5%" or "XIRR: 12.5% annualized"
5. **Summary metrics** (optional but recommended):
   - Total invested
   - Current value (final price × final unit balance)
   - Absolute gain/loss

---

## 4. Frontend Requirements (React)

### Components

#### 4.1 Upload Area
- **Drag-and-drop zone** or traditional file input
- Accepts only `.xlsx` files
- File size validation: ≤ 10 MB (show error if exceeded)
- **Disabled during upload** (prevent multiple simultaneous uploads)
- Shows **spinner while uploading** (labeled "Processing file...")

#### 4.2 XIRR Display Panel
- **Prominent, large text** (at least 36px font)
- Shows percentage with direction indicator (↑ green for positive, ↓ red for negative)
- Format: `XIRR: 12.5% p.a.` or similar
- Subtext: "Return on Investment"
- Initially hidden; shows after successful processing

#### 4.3 Transaction Grid
- **Columns (fixed order):**
  1. Date (DD-MMM-YYYY format) — **Always required**
  2. Transaction Type (Buy, Purchase, Systematic Investment Purchase (SIP), SELL, REDEMPTION, DIVIDEND REINVEST, Stamp Duty, etc.) — **Always required**
  3. Amount (₹ or currency symbol) — **Always required**
  4. Units (numeric) — **Required except for Stamp Duty (optional for Stamp Duty)**
  5. Price (₹/unit) — **Optional: Empty for SELL, REDEMPTION, and Stamp Duty transactions**
  6. Unit Balance (cumulative units held) — **Optional: Empty for SELL, REDEMPTION, and Stamp Duty transactions**

- **Display behavior:**
  - Rows in **file order** (no pre-sorting in v1)
  - Grid displays actual data received; empty cells shown as "—" or blank
  - Each row stripes for readability (alternating bg colors)
  - Future: sorting by column headers (not in v1)
  - Future: pagination or virtualization for large datasets

#### 4.4 Skeleton Loader
- **During cold-start delay** (when waiting for backend response):
  - Show grid structural skeleton
  - 6 columns with proportional widths matching final grid
  - ~8 fake rows with gray placeholder bars
  - Shimmer/pulse animation effect
  - **Replaces spinner after ~2 seconds** (allows quick responses to show data immediately)

#### 4.5 Error Display
- **Error banner** (red background):
  - Clear heading: "File Upload Failed"
  - Detailed error message from backend
  - Suggestion to fix (e.g., "Please check column names and data types")
  - "Try Again" button to retry

### State Management
- `fileInput: File | null`
- `isLoading: boolean` (upload + processing)
- `showSkeleton: boolean` (after ~2s of loading)
- `transactions: Transaction[]`
- `xirr: number | null`
- `error: {message: string, details?: string} | null`

### API Endpoint (Frontend → Backend)
```
POST /api/upload
Content-Type: multipart/form-data

Request:
- file: File (binary)

Response (200 OK):
{
  "success": true,
  "xirr": 12.5,
  "transactions": [
    {
      "date": "15-Jan-2020",
      "transactionType": "BUY",
      "amount": 10000,
      "units": 100,
      "price": 100,
      "unitBalance": 100
    },
    ...
  ]
}

Response (400 Bad Request):
{
  "success": false,
  "error": "Row 5: Date column contains invalid format 'xyz' (expected DD-MMM-YYYY)",
  "errorCode": "INVALID_DATE_FORMAT"
}
```

---

## 5. Backend Requirements (FastAPI)

### Endpoint: POST /api/upload

#### Input Validation
1. **File extension check:** Must be `.xlsx` (reject `.xls`, `.csv`, others)
2. **File size check:** ≤ 10 MB (raise HTTP 413 if exceeded)
3. **Multipart form parsing:** Extract file from `FormData`

#### File Processing

**Library:** `openpyxl` or `pandas`

1. **Load worksheet:**
   - Read first sheet only
   - Extract column headers from first row

2. **Column validation:**
   - All 6 columns must exist in the header row: Date, Transaction Type, Amount, Units, Price, Unit Balance (exact names, case-insensitive)
   - Error if any column missing: `"Missing required column: {column_name}"`
   - **Conditional field availability:** Specific columns can be empty (null/blank) for certain transaction types:
     - **Stamp Duty transactions:** Units is optional (can be empty or populated); Price and Unit Balance must be empty
     - **SELL/REDEMPTION transactions:** Price and Unit Balance must be empty (Units required)
     - **Other transactions (Buy, Purchase, SIP, DIVIDEND REINVEST, etc.):** All fields required

3. **Data type parsing & validation:**
   - **Date:** Parse as DD-MMM-YYYY or common formats (e.g., DD/MM/YYYY, YYYY-MM-DD). Error: `"Row {n}: Invalid date format in '{value}' (expected DD-MMM-YYYY)"`
   - **Transaction Type:** Must be non-empty string. Allowed values: `Buy`, `Purchase`, `Systematic Investment Purchase` (SIP), `SELL`, `REDEMPTION`, `DIVIDEND REINVEST`, `DIVIDEND PAYOUT`, `Stamp Duty` (or user-defined; allow flexibility but validate non-empty). All variations of Buy/Purchase/SIP are treated as equivalent investment transactions. Error: `"Row {n}: Transaction Type cannot be empty"`
   - **Amount:** Float. Must be numeric and > 0 for most transaction types. For SELL/REDEMPTION/Stamp Duty: must be > 0. Error: `"Row {n}: Amount must be numeric; got '{value}'"`
   - **Units:** Float. Optional behavior based on transaction type:
     - For **Buy/Purchase/SIP/DIVIDEND REINVEST:** Must be numeric and > 0
     - For **SELL/REDEMPTION:** Must be numeric and > 0 (represents units redeemed)
     - For **Stamp Duty:** Must be numeric if provided (Optional; can be empty or have a value > 0)
     - Error: `"Row {n}: Units must be numeric; got '{value}'"`
   - **Price:** Float. Optional based on transaction type:
     - For **Buy/Purchase/SIP/DIVIDEND REINVEST:** Must be > 0
     - For **SELL/REDEMPTION/Stamp Duty:** Must be empty/null
     - Error: `"Row {n}: Price must be positive; got '{value}'"` (if provided and invalid)
   - **Unit Balance:** Float. Optional based on transaction type:
     - For **Buy/Purchase/SIP/DIVIDEND REINVEST:** Must be ≥ 0 and provided
     - For **SELL/REDEMPTION/Stamp Duty:** Must be empty/null
     - Error: `"Row {n}: Unit Balance must be non-negative; got '{value}'"` (if provided and invalid)

4. **Business logic validation (Strict Mode):**
   - **Minimum transactions:** At least 1 investment row (Buy/Purchase/SIP/DIVIDEND REINVEST with valid Unit Balance) + 1 final redemption/sale = ≥ 2 rows. Error: `"Insufficient data: At least 1 investment (Buy/Purchase/SIP) and 1 redemption/sale transaction required"`
   - **Maximum transactions:** ≤ 10,000 rows. Error: `"File too large: Maximum 10,000 transactions allowed"`
   - **Final redemption check:** Last transaction must be SELL or REDEMPTION, and the cumulative units after this transaction must equal 0. Error: `"Final redemption missing: Last transaction must be a full redemption/sale (final unit balance must be 0)"`
   - **Unit balance consistency (for rows with Unit Balance provided):** For each row with Unit Balance field populated, calculate expected unit balance = sum of all units in previous rows (excluding Stamp Duty/SELL/REDEMPTION) + current row's units. Compare with "Unit Balance" column (allow ±1 tolerance). Error: `"Row {n}: Unit Balance '{actual}' doesn't match cumulative units '{expected}'"`
   - **Stamp Duty handling:** Stamp Duty transactions are cost entries (reduce net returns) and cannot affect unit balance calculation. They must have empty Price and Unit Balance fields; Units is optional. Error: `"Row {n}: Stamp Duty transaction must have empty Price and Unit Balance columns"`
   - **SELL/REDEMPTION handling:** These transactions have no Price or final Unit Balance; the Units field indicates how many units were sold. They are cash outflows for XIRR calculation.
   - **Cash flow analysis:** Ensure at least one investment transaction (Buy/Purchase/SIP/DIVIDEND REINVEST with positive units, positive Unit Balance) and one redemption/sale transaction (SELL/REDEMPTION). Error: `"Transaction mix error: Need both investment (Buy/Purchase/SIP) and redemption/sale transactions to calculate returns"`

5. **XIRR Calculation:**
   - Convert transactions to cash flows:
     - **Buy/Purchase/SIP/DIVIDEND REINVEST:** Negative cash flow (money going out) = -Amount
     - **SELL/REDEMPTION:** Positive cash flow (money coming in) = +Amount
     - **Stamp Duty:** Negative cash flow (cost/fee) = -Amount
     - **Date:** Use the transaction date to calculate time-weighted IRR
   - For SELL/REDEMPTION rows (no Price provided), the Amount field represents the actual cash realized
   - Use `numpy_financial.xirr()` (requires dates + cash flows) or equivalent IRR calculation
   - Convert to annualized percentage
   - **Error handling:** If XIRR fails to converge → `"Unable to calculate XIRR: Verify transaction history contains both positive and negative cash flows"`
   - Round to 2 decimal places: e.g., `12.5`

#### Response Format

**Success (HTTP 200):**
```json
{
  "success": true,
  "xirr": 12.5,
  "transactions": [
    {
      "date": "15-Jan-2020",
      "transactionType": "BUY",
      "amount": 10000,
      "units": 100,
      "price": 100,
      "unitBalance": 100
    }
  ]
}
```

**Validation Error (HTTP 400):**
```json
{
  "success": false,
  "error": "Row 5: Date column contains invalid format 'xyz' (expected DD-MMM-YYYY)",
  "errorCode": "INVALID_DATE_FORMAT"
}
```

**Server Error (HTTP 500):**
```json
{
  "success": false,
  "error": "An unexpected error occurred. Please try again.",
  "errorCode": "INTERNAL_SERVER_ERROR"
}
```

### Performance & Concurrency
- **Async handler:** Use `@app.post("/api/upload")` with `async def` to handle concurrent uploads
- **In-memory processing:** Load file → validate → calculate → respond (no disk writes except temp for file stream)
- **Timeout:** Set request timeout to 30 seconds (Render free tier may cold-start; backend should respond within this)
- **Resource limits:** Max file size 10 MB enforced by FastAPI config (`max_upload_size`)

### Dependencies
```
fastapi
uvicorn
python-multipart
openpyxl  # or pandas
numpy
scipy  # for financial calculations
numpy-financial  # optional; provides IRR function
```

---

## 6. Excel File Format Specification

### Expected Input
- **File format:** `.xlsx` (Excel 2010+)
- **Encoding:** UTF-8
- **Headers:** First row contains required column names
- **Data rows:** Starting from row 2

### Example Valid File

| Date       | Transaction Type | Amount | Units | Price | Unit Balance |
|------------|------------------|--------|-------|-------|-----------------|
| 15-Jan-2020 | Buy              | 10000  | 100   | 100   | 100             |
| 15-Jun-2020 | Stamp Duty       | 50     |       |       |                 |
| 15-Jan-2021 | Purchase         | 15000  | 100   | 150   | 200             |
| 15-Jan-2022 | Systematic Investment Purchase | 20000 | 125 | 160 | 325 |
| 15-Jan-2023 | DIVIDEND REINVEST| 5000   | 30    | 166   | 355             |
| 15-Jun-2023 | Stamp Duty       | 75     | 5     |       |                 |
| 15-Jan-2024 | SELL             | 60000  | 355   |       |                 |

**Key observations from example:**
- **Buy/Purchase/SIP transactions:** All 6 columns populated (Date, Type, Amount, Units, Price, Unit Balance) — all treated as investment transactions
- **DIVIDEND REINVEST transactions:** Same as Buy/Purchase/SIP — all columns required
- **Stamp Duty transactions:** Only Date, Transaction Type, and Amount required; Units is optional (populated in row 6 but empty in row 2); Price and Unit Balance always empty
- **SELL transactions:** Only Date, Transaction Type, Amount, and Units populated; Price and Unit Balance are empty (Amount represents cash realized from sale)
- **Final transaction must be SELL/REDEMPTION:** Ensures fund is fully exited for XIRR calculation
- **Investment variations:** Buy, Purchase, and Systematic Investment Purchase are treated equivalently for validation and calculations

### Column Details
- **Date:** DD-MMM-YYYY (or other common formats; backend will attempt parse) — **Always required**
- **Transaction Type:** Buy, Purchase, Systematic Investment Purchase (SIP), SELL, REDEMPTION, DIVIDEND REINVEST, DIVIDEND PAYOUT, Stamp Duty, etc. — **Always required**
  - **Note:** Buy, Purchase, and any transaction type starting with "Systematic Investment Purchase" are treated as equivalent investment transactions
- **Amount:** Cash amount in ₹
  - **Buy/Purchase/SIP/DIVIDEND REINVEST/Stamp Duty:** Always positive
  - **SELL/REDEMPTION:** Cash received (positive value)
- **Units:** Number of units
  - **Buy/Purchase/SIP/DIVIDEND REINVEST:** Positive (units acquired)
  - **SELL/REDEMPTION:** Positive (units sold/redeemed)
  - **Stamp Duty:** Optional (can be empty or positive if units are affected)
- **Price:** Per-unit price (NAV/unit cost) — **Empty for SELL, REDEMPTION, Stamp Duty**
- **Unit Balance:** Cumulative units held after transaction — **Empty for SELL, REDEMPTION, Stamp Duty**

---

## 7. Error Handling & User Feedback

### Frontend Error Scenarios

| Scenario | Message | Recovery |
|----------|---------|----------|
| File not .xlsx | "Invalid file format. Please upload an Excel (.xlsx) file." | Allow retry with correct format |
| File > 10 MB | "File too large. Maximum size is 10 MB. Your file is 12.3 MB." | Allow retry with smaller file |
| Network timeout | "Upload took too long. Please check your connection and try again." | Allow retry |
| Server error | "An unexpected error occurred. Please try again later." | Allow retry |

### Backend Error Messages (Passed to Frontend)

| Validation Issue | Error Message |
|-----------------|---------------|
| Missing column | `"Missing required column: Transaction Type"` |
| Invalid date | `"Row 5: Invalid date format 'abc' (expected DD-MMM-YYYY)"` |
| Non-numeric amount | `"Row 3: Amount must be numeric; got 'xyz'"` |
| Stamp Duty validation | `"Row 6: Stamp Duty transaction must have empty Price and Unit Balance columns"` |
| SELL missing units | `"Row 8: SELL/REDEMPTION transaction must have Units field populated"` |
| Unit balance mismatch | `"Row 7: Unit Balance '100' doesn't match cumulative units '95'"` |
| No final redemption | `"Final redemption missing: Last transaction must be SELL/REDEMPTION with units = 0 final balance"` |
| Insufficient data | `"Insufficient data: At least 1 investment and 1 redemption/sale transaction required"` |
| File too large | `"File too large: Maximum 10,000 transactions allowed (your file has 15,234)"` |

---

## 8. Loading States & UX

### Phase 1: Upload (0–2 seconds, deterministic)
- **Spinner visible:** "Uploading file..."
- Upload progress: Optional; omit for simplicity if FastAPI handles quickly
- Upload area **disabled** (prevent duplicate submissions)

### Phase 2: Backend Processing with Skeleton (2+ seconds)
- **Spinner replaced with skeleton loader:**
  - Grid area shows 6-column skeleton structure (Date, Transaction Type, Amount, Units, Price, Unit Balance)
  - ~8 placeholder rows with variable heights (some rows shorter to reflect sparse data like Stamp Duty)
  - Shimmer/pulse CSS animation
  - Communicates: "Data is loading, a table with these columns is coming here"
- XIRR area shows loading placeholder (e.g., "— calculating")

### Phase 3: Success (Data Arrives)
- **Skeleton removed instantly**
- **Grid populates** with actual transaction data
- **XIRR displays** in prominent panel
- Summary metrics (if implemented): total invested, current value, gain/loss

### Phase 4: Error (Immediate)
- **Spinner removed**
- **Skeleton hidden**
- **Error banner displayed** with specific message
- **Upload area re-enabled** for retry

---

## 9. Constraints & Limitations

| Constraint | Detail | Reason |
|-----------|--------|--------|
| **Single Fund** | One Excel file = one fund; no multi-fund uploads | Simplifies parsing + XIRR calculation |
| **Stateless** | No database; data deleted after session ends | Free tier cost optimization |
| **Max file size** | 10 MB | Render free tier memory limit (~512 MB) |
| **Max transactions** | 10,000 rows | Performance + memory safety |
| **Required final redemption** | Final transaction must be SELL/REDEMPTION reducing units to 0 | XIRR requires terminal cash flow and complete exit |
| **Strict validation** | File rejected on data inconsistencies; conditional field requirements enforced per transaction type | Ensures accuracy for financial calculations and handles complex fund statements |
| **No authentication** | Public access; no user accounts | Simplifies MVP; can add later |
| **No persistence** | Results not saved; user must re-upload to recalculate | Reduces complexity + storage costs |
| **Concurrent uploads** | All uploads share single Render instance; may be slow if 2+ users simultaneous | Acceptable for free tier; document in FAQ |

---

## 10. Future Enhancements (Not in v1)

- [ ] **Sorting:** Click column headers to sort grid (by Date, Amount, Price, Unit Balance)
- [ ] **Filtering:** Filter transactions by type (BUY/SELL/DIVIDEND)
- [ ] **Pagination:** For datasets > 100 rows
- [ ] **Export results:** Download grid as CSV or PDF
- [ ] **Multiple funds:** Upload 2+ files, compare XIRR across funds
- [ ] **Persistent storage:** Add database to save user records (migrating from free tier)
- [ ] **User accounts:** Authentication, historical data, portfolio tracking
- [ ] **API documentation:** Auto-generated Swagger docs (FastAPI provides this automatically)
- [ ] **Advanced metrics:** CAGR, absolute return %, MWR vs TWR comparison
- [ ] **Currency support:** Handle multi-currency transactions

---

## 11. Testing Criteria (QA Checklist)

### File Upload
- [ ] Accept valid .xlsx files ≤ 10 MB
- [ ] Reject non-.xlsx formats with clear error
- [ ] Reject files > 10 MB with file size error message

### Data Validation
- [ ] Reject missing columns with specific column name
- [ ] Reject invalid date formats with row number + expected format
- [ ] Reject non-numeric values in numeric columns with row number
- [ ] Reject files without final redemption (Unit Balance ≠ 0)
- [ ] Reject files with > 10,000 rows
- [ ] Accept Buy, Purchase, and Systematic Investment Purchase (SIP) as equivalent investment transactions
- [ ] Accept DIVIDEND REINVEST (with space) as valid investment transaction

### XIRR Calculation
- [ ] Calculate correct XIRR for sample fund data (verify manually)
- [ ] Display positive XIRR in green; negative in red
- [ ] Handle edge case: very high XIRR (e.g., quick flip)
- [ ] Handle edge case: very low XIRR (e.g., long hold)

### UI/UX
- [ ] Spinner shows during upload (< 2 seconds typically)
- [ ] Skeleton loader shows during backend processing
- [ ] Grid renders with correct column order
- [ ] Grid displays data in file order (unsorted)
- [ ] XIRR prominently displayed after processing
- [ ] Error banner shows specific validation errors
- [ ] Upload area re-enables after error

### Performance
- [ ] Upload + processing completes within 30 seconds
- [ ] Cold-start skeleton displays within 2–5 seconds
- [ ] Grid renders smoothly (no stuttering with ~5000 rows)

### Concurrency
- [ ] Two simultaneous uploads don't corrupt data
- [ ] Error in one upload doesn't affect another

---

## 12. Decision Log

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **Stateless** | Simplifies deployment on free tier; no DB cost | Users must re-upload for new calculations |
| **FastAPI** | Async handles concurrent uploads; auto Swagger docs | Slightly more setup than Flask |
| **Strict validation** | Ensures financial data accuracy | Rejects borderline files; forces user to clean data |
| **Excel only** | Simpler parsing; mutual fund statements typically in Excel | No CSV or other formats initially |
| **File order display** | Simpler v1; sorting planned later | Less intuitive than pre-sorted; addresses in v2 |
| **Skeleton loader** | Improves perceived performance during cold-start | Slightly more complex React component |
| **10MB, 10k rows limit** | Safe for Render free tier (~512 MB memory) | Some power users may hit limits; upgrade path available |
| **Detailed error messages** | Helps users fix files independently | Requires verbose backend validation logic |

---

## 13. Deployment Notes (Render Free Tier)

### Backend (FastAPI)
- **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment variables:** None required for v1 (no secrets)
- **Build command:** `pip install -r requirements.txt`
- **Cold-start delay:** ~30 seconds on free tier (acceptable; skeleton loader helps UX)

### Frontend (React SPA)
- **Build command:** `npm run build`
- **Deploy as static site** OR within FastAPI server (serve static files)
- **Optimization:** Minify, lazy-load components

### Architecture
```
Render Free Instance
├── FastAPI Backend (serves /api/*)
└── React SPA (serves static /*)
```

---

## 14. Success Metrics

- **Time to calculate XIRR:** < 5 seconds (excluding Render cold-start)
- **User error resolution:** Specific error messages resolve 90%+ of upload issues on first attempt
- **Page load:** Initial page load < 2 seconds
- **Data accuracy:** XIRR calculation verified against financial tooling (e.g., Excel's XIRR function)

---

## 15. Questions for Implementation Review

- [x] **XIRR library choice:** Use `numpy_financial`, `scipy.optimize`, or manual Newton-Raphson implementation? → **Use `numpy_financial` for production-ready XIRR calculation (matches Excel's XIRR function exactly, handles all edge cases, <100ms for 10k transactions, zero maintenance burden)**
- [x] **Skeleton animation:** CSS shimmer or React Skeleton library (e.g., react-skeleton-loader)? → **Use CSS shimmer (pure CSS animation, ~2KB overhead vs +10-15KB for library, GPU-accelerated 60fps, full control over timing, minimizes bundle size for Render free tier cold-start)**
- [x] **Error logging:** Log validation errors for debugging? (Render free tier has limited log retention) → **No, don't log errors for now**
- [x] **CORS configuration:** Allow only frontend domain or open to all origins? → **Open to all origins**
- [x] **Rate limiting:** Implement per-IP rate limit to prevent abuse on free tier? → **No, don't implement per-IP rate limit for now**

---

**End of Intent Document**

---

### Sign-Off
- **Feature Owner:** [Your name]
- **Prepared:** March 18, 2026
- **Ready for:** Development kickoff

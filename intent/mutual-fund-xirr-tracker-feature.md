# Intent: Mutual Fund XIRR Return Tracker

**Date:** March 18, 2026  
**Status:** Completed — Redemption/SELL Enhancements & STT Paid Split & Privacy disclosure
**Priority:** MVP (Minimum Viable Product)  
**Revision:** 2.5 – Redemption/SELL Price/Unit Balance optional; STT Paid split from Stamp Duty; negative SELL/REDEMPTION amounts/units accepted, privacy Disclaimer

---

## 1. Feature Overview

A **stateless web application** that allows users to upload an Excel file containing mutual fund transaction history for a **single fund** and instantly calculates the **XIRR (Extended Internal Rate of Return)** — the annualized return on investment.

The application provides:
- **Excel File Upload** via drag-and-drop or file picker
- **Transaction Grid Display** showing all transactions in a sortable (future) data table
- **XIRR Calculation** prominently displayed with return percentage
- **Summary Metrics** (mandatory): Total Invested, Final Proceeds, Profit/Loss
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
Response: {transactions[], xirr: num, summaryMetrics: {}, validationErrors?}
    ↓
React State Update + Render Grid + Display XIRR + Summary Metrics
```

---

## 3. User Journey

### Step 1: Access the Application
- User loads the web page (React SPA)
- Sees a clean interface with:
  - Upload area (drag-and-drop + file input)
  - XIRR display area (initially empty/instructional)
  - Summary metrics area (initially empty/instructional)
  - Grid area (initially empty/instructional)

### Step 2: Upload Excel File
- User can download `MFTransaction_Template.xlsx` directly from the upload area before uploading, using the "Download sample template" link
- User uploads Excel file (e.g., mutual_fund_transactions.xlsx)
- **Upload validation** (frontend):
  - File is `.xlsx` format
  - File size ≤ 10 MB
- **Upload spinner starts** (shows "Processing file..." with animated spinner)

### Step 3: Backend Processing
- FastAPI receives multipart file upload
- **File parsing** (openpyxl or pandas):
  - Extract **first worksheet only** (additional worksheets are ignored)
  - Validate columns exist: `Date, Transaction Type, Amount, Units, Price, Unit Balance`
  - Column headers are **case-insensitive** with **leading/trailing spaces trimmed**
  - Parse each column with strict type checking (with conditional optional fields based on transaction type)

### Step 4: Validation & Error Handling (Strict Mode)
If **any** of the following occur → **reject file with detailed error**:
- Missing required column(s) (Date, Transaction Type, Amount)
- **For Stamp Duty transactions:** Price and Unit Balance must be empty; Units is optional (can be empty). Stamp Duty is excluded from XIRR cash flows but included in Total Invested.
- **For STT Paid transactions:** Price and Unit Balance must be empty; Units is optional (can be empty). STT Paid is a **separate category** from Stamp Duty. STT Paid amounts are **netted against same-date SELL/REDEMPTION cash flows** in XIRR calculation (reducing the inflow), and are **excluded from Total Invested**.
- **For Gross Purchase transactions (e.g., Gross Purchase - via MFUTILITY, Gross Purchase Systematic - Instalment N/N):** Price and Unit Balance must be empty; Units is optional (can be empty). Gross Purchase is a summary row representing the gross transaction amount before splitting into Net Purchase + Stamp Duty. It is excluded from XIRR cash flows and Total Invested calculation.
- **For SELL/REDEMPTION transactions:** Price and Unit Balance are **optional** (may be populated or empty); Date, Transaction Type, Amount, and Units are required. Amount sign convention: negative amounts are accepted and treated as positive (absolute value used). Units sign convention: absolute value used in unit balance consistency check.
- **For BUY/PURCHASE/SIP/Systematic Investment/DIVIDEND REINVEST transactions:** All columns required (Date, Transaction Type, Amount, Units, Price, Unit Balance)
- Invalid data types in any row (e.g., non-date in Date column, non-numeric where required)
- Date outside acceptable range (transactions must be from 1960 onwards; reject dates before 1960 or in future)
- Dates in invalid DD/MM/YYYY format (e.g., "01-Jan-2020" rejected; only "01/01/2020" accepted)
- Negative amounts (except for SELL/REDEMPTION which have specific sign convention)
- Missing final redemption/sale transaction (XIRR requires terminal cash flow)
- Inconsistent unit balance where provided (cumulative units don't match Unit Balance column)
- Not enough transactions (< 2 transactions minimum: at least 1 investment and 1 redemption/sale)
- More than 10,000 transactions (too large for this tier)
- Last transaction is not SELL/REDEMPTION with Unit Balance = 0

Return to user: **Specific error message** (e.g., "Row 5: Date column contains invalid format 'xyz' (expected DD/MM/YYYY, e.g., 18/12/2024)")

### Step 5: Successful Processing
1. **Grid loads** with skeleton loader visible during cold-start delay (Render)
   - Skeleton shows 6-column structure matching final grid layout
   - Displays ~8 fake rows with shimmer animation
2. **Spinner removed** when data arrives
3. **Grid populates** with transaction data (file order, no sorting)
4. **XIRR prominently displayed:**
   - Large, bold font (at least 36px)
   - Green if positive, red if negative
   - Format: `XIRR: 12.54%` (no "p.a.", "annualized", or year-specific notation)
   - XIRR is calculated for all transactions till date (not year-specific)
5. **Summary metrics displayed** (mandatory):
   - **Total Invested:** Sum of all PURCHASE/BUY/SIP/Systematic Investment/Stamp Duty transactions (Gross Purchase **excluded** — it is a summary row; the actual investment is captured by accompanying Net Purchase and Stamp Duty rows; STT Paid **excluded** — it is netted against redemption in XIRR, not treated as a standalone investment cost)
   - **Final Proceeds:** Sum of all SELL/REDEMPTION transaction amounts (absolute values), less total STT Paid amounts on the same dates
   - **Profit/Loss:** Final Proceeds – Total Invested (formatted as currency, green if positive, red if negative)
   - **Note:** Stamp Duty transactions are included in **both** Total Invested and XIRR cash flows (as negative outflows). STT Paid transactions are **not** included in Total Invested; instead, STT Paid amounts are netted against same-date SELL/REDEMPTION inflows in the XIRR cash flow, reflecting the true net proceeds received. Gross Purchase remains excluded from both.

---

## 4. Frontend Requirements (React)

### Components

#### 4.1 Upload Area
- **Drag-and-drop zone** or traditional file input
- Accepts only `.xlsx` files
- File size validation: ≤ 10 MB (show error if exceeded)
- **Disabled during upload** (prevent multiple simultaneous uploads)
- Shows **spinner while uploading** (labeled "Processing file...")
- **Template download link** ("Download sample template") rendered inline in the secondary text area; hidden when upload is in progress; uses HTML `download` attribute for direct file save without navigation; `onClick` stops propagation to prevent triggering the drop-zone click handler
- **Privacy disclaimer** displayed below the "Maximum size" note with a lock icon and the following text: "🔒 Privacy-safe: Your data is private. Your uploaded file is processed entirely in-memory and discarded immediately after results are returned. No data is stored anywhere." Hidden when upload is in progress (same visibility rule as the template download link)

#### 4.2 XIRR Display Panel
- **Prominent, large text** (at least 36px font)
- Shows percentage with direction indicator (↑ green for positive, ↓ red for negative)
- Format: `XIRR: 12.54%` (rounded to 2 decimal places)
- Subtext: "Return on Investment"
- Initially hidden; shows after successful processing

#### 4.3 Summary Metrics Panel (Mandatory)
- **Display below XIRR panel** with three metrics:
  1. **Total Invested:** ₹12,50,000 (currency symbol, 2 decimal places)
  2. **Final Proceeds:** ₹14,75,500 (sum of all SELL/REDEMPTION amounts less STT Paid; currency symbol, 2 decimal places)
  3. **Profit/Loss:** ₹2,25,500 (green if positive, red if negative, currency symbol, 2 decimal places)
- Initially hidden; shows after successful processing alongside XIRR

#### 4.4 Transaction Grid
- **Columns (fixed order):**
  1. Date (DD/MM/YYYY format) — **Always required**
  2. Transaction Type (Purchase, Buy, SIP, SIP Purchase, Systematic Investment, Systematic Investment Plan, Gross Purchase, Gross Purchase Systematic, Gross Purchase - via MFUTILITY, SELL, REDEMPTION, DIVIDEND REINVEST, Stamp Duty, STT Paid, etc.) — **Always required**
  3. Amount (₹ or currency symbol, 2 decimal places) — **Always required**
  4. Units (numeric, 3 decimal places) — **Required except for Stamp Duty / STT Paid / Gross Purchase (optional)**
  5. Price (₹/unit, 2–4 decimal places as per user entry) — **Optional: Empty for Stamp Duty, Gross Purchase, and STT Paid transactions; optional (may be populated) for SELL/REDEMPTION**
  6. Unit Balance (cumulative units held, 3 decimal places) — **Optional: Empty for Stamp Duty, Gross Purchase, and STT Paid transactions; optional (may be populated) for SELL/REDEMPTION**

- **Display behavior:**
  - Rows in **file order** (no pre-sorting in v1)
  - Grid displays actual data received; empty cells shown as "—" or blank
  - Each row stripes for readability (alternating bg colors)
  - Future: sorting by column headers (not in v1)
  - Future: pagination or virtualization for large datasets

#### 4.5 Skeleton Loader
- **During cold-start delay** (when waiting for backend response):
  - Show grid structural skeleton
  - 6 columns with proportional widths matching final grid
  - ~8 fake rows with gray placeholder bars
  - Shimmer/pulse animation effect
  - **Replaces spinner after ~2 seconds** (allows quick responses to show data immediately)

#### 4.6 Error Display
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
- `summaryMetrics: {totalInvested: number, finalProceeds: number, profitLoss: number} | null`
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
  "xirr": 12.54,
  "summaryMetrics": {
    "totalInvested": 1250000,
    "finalProceeds": 1475500,
    "profitLoss": 225500
  },
  "transactions": [
    {
      "date": "18/12/2024",
      "transactionType": "Purchase",
      "amount": 10000,
      "units": 100.123,
      "price": 100.50,
      "unitBalance": 100.123
    },
    ...
  ]
}

Response (400 Bad Request):
{
  "success": false,
  "error": {
    "message": "File validation failed",
    "details": "Row 5: Date column contains invalid format 'xyz' (expected DD/MM/YYYY, e.g., 18/12/2024)"
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

Response (500 Internal Server Error - XIRR Convergence):
{
  "success": false,
  "error": {
    "message": "Cannot calculate XIRR",
    "details": "Cannot calculate XIRR for this data. Please verify all transactions."
  }
}
```

---

## 5. Backend Requirements (Python + FastAPI)

### Libraries
- **openpyxl** or **pandas:** Excel file parsing
- **pyxirr** or **numpy_financial:** XIRR calculation
- **pydantic:** Data validation
- **python-multipart:** Multipart file upload handling

### Data Model

```python
class Transaction(BaseModel):
    date: str  # DD/MM/YYYY format
    transactionType: str  # Case-insensitive normalized
    amount: float  # Positive for PURCHASE, positive for SELL (inflow)
    units: Optional[float] = None  # 3 decimal places; nullable for Stamp Duty/STT Paid
    price: Optional[float] = None  # 2–4 decimals; nullable for SELL, REDEMPTION, Stamp Duty, STT Paid
    unitBalance: Optional[float] = None  # 3 decimals; nullable for SELL, REDEMPTION, Stamp Duty, STT Paid

class UploadResponse(BaseModel):
    success: bool
    xirr: Optional[float] = None  # 2 decimal places
    summaryMetrics: Optional[dict] = None  # {totalInvested, finalProceeds, profitLoss}
    transactions: Optional[List[Transaction]] = None
    error: Optional[dict] = None  # {message, details}
```

### File Parsing Workflow
1. **Load Excel file** → Extract first worksheet only
2. **Normalize column headers:**
   - Convert to lowercase
   - Trim leading/trailing whitespace
   - Match against: `["date", "transaction type", "amount", "units", "price", "unit balance"]`
3. **Parse rows:**
   - Skip empty rows
   - For each row, extract values and validate
4. **Normalize transaction types** (case-insensitive):
   - Recognize variants: "Purchase", "Buy", "SIP", "SIP Purchase", "Systematic Investment", "Systematic Investment Plan" → all treated as **investment transactions**
   - Recognize variants: "SELL", "Sell" → **SELL transactions**
   - Recognize variants: "REDEMPTION", "Redemption" → **REDEMPTION transactions**
   - Recognize: "DIVIDEND REINVEST", "Dividend Reinvest" → **DIVIDEND REINVEST transactions**
   - Recognize variants: "Stamp Duty", "STAMP DUTY", "Less: Stamp Duty" → **STAMP_DUTY transactions** (included in Total Invested; included in XIRR as outflow)
   - Recognize variants: "STT Paid", "STT PAID", "stt", "Less: STT Paid" → **STT_PAID transactions** (excluded from Total Invested; netted against same-date redemption in XIRR)

---

## 6. Data Validation Rules

### Column-Level Validation

| Column | Required | Type | Format | Nullable | Notes |
|--------|----------|------|--------|----------|-------|
| **Date** | Yes | String | DD/MM/YYYY (e.g., 18/12/2024) | No | Must be between 1960-01-01 and today; reject dates outside this range |
| **Transaction Type** | Yes | String | Case-insensitive; see normalization rules | No | Must match recognized transaction types |
| **Amount** | Yes | Numeric | Positive (PURCHASE/SELL sign convention) | No | For PURCHASE: positive (outflow); For SELL/REDEMPTION: positive (inflow) |
| **Units** | Conditional | Numeric | 3 decimal places | Yes (for Stamp Duty/STT Paid only) | Nullable for Stamp Duty/STT Paid; required for all others |
| **Price** | Conditional | Numeric | 2–4 decimal places as per entry | Yes | Nullable for Stamp Duty, STT Paid, Gross Purchase; **optional** for SELL/REDEMPTION (may be populated); required for PURCHASE, DIVIDEND REINVEST |
| **Unit Balance** | Conditional | Numeric | 3 decimal places | Yes | Nullable for Stamp Duty, STT Paid, Gross Purchase; **optional** for SELL/REDEMPTION (may be populated); required for PURCHASE, DIVIDEND REINVEST |

### Empty Cell Validation
- **Empty cells:** null, blank string (""), or whitespace only
- **When empty is allowed:** As per column-level validation above
- **When empty is NOT allowed:** Validation error with specific field name and row number

### Row-Level Validation

#### Investment Transactions (PURCHASE/Buy/SIP/Systematic Investment/DIVIDEND REINVEST)
- **Required fields:** Date, Transaction Type, Amount, Units, Price, Unit Balance
- **Validation:**
  - Amount > 0
  - Units > 0
  - Price > 0
  - Unit Balance > 0

#### Stamp Duty Transactions
- **Required fields:** Date, Transaction Type, Amount
- **Optional fields:** Units (can be empty)
- **Must be empty:** Price, Unit Balance
- **Validation:**
  - Amount > 0
  - If Units provided: Units > 0
- **XIRR treatment:** Included as negative outflow in XIRR cash flows
- **Total Invested treatment:** Included in Total Invested

#### STT Paid Transactions
- **Required fields:** Date, Transaction Type, Amount
- **Optional fields:** Units (can be empty)
- **Must be empty:** Price, Unit Balance
- **Validation:**
  - Amount > 0
  - If Units provided: Units > 0
- **XIRR treatment:** Netted against same-date SELL/REDEMPTION inflow (reduces the redemption cash flow amount in XIRR)
- **Total Invested treatment:** Excluded from Total Invested

#### SELL / REDEMPTION Transactions
- **Required fields:** Date, Transaction Type, Amount, Units
- **Optional fields:** Price, Unit Balance (may be populated or empty)
- **Validation:**
  - Amount: positive or negative accepted; absolute value used in all calculations
  - Units: positive or negative accepted; absolute value used in unit balance consistency check
  - Final SELL/REDEMPTION must have Unit Balance = 0 (if Unit Balance is provided)

#### DIVIDEND REINVEST Transactions
- **Required fields:** Date, Transaction Type, Amount, Units, Price, Unit Balance
- **Same validation as investment transactions**
- **Constraint:** Cannot be the final transaction (file must end with SELL/REDEMPTION)

### File-Level Validation

| Rule | Error Message | Rejection |
|------|---------------|-----------|
| Missing required columns | `"Missing required column: Transaction Type"` | Yes |
| Missing final SELL/REDEMPTION | `"Final redemption missing: Last transaction must be SELL/REDEMPTION with Unit Balance = 0"` | Yes |
| Last transaction NOT SELL/REDEMPTION | `"Last transaction must be SELL or REDEMPTION; found: DIVIDEND REINVEST"` | Yes |
| Unit balance mismatch | `"Row 7: Unit Balance '100' doesn't match cumulative units '95'"` | Yes |
| Insufficient transactions | `"Insufficient data: At least 2 transactions required (1 investment + 1 redemption)"` | Yes |
| File too large | `"File too large: Maximum 10,000 transactions allowed (your file has 15,234)"` | Yes |
| Invalid date format | `"Row 5: Invalid date format 'abc' (expected DD/MM/YYYY, e.g., 18/12/2024)"` | Yes |
| Date outside range | `"Row 12: Transaction date '01/01/1950' is before 1960; cannot process"` | Yes |
| Non-numeric amount | `"Row 3: Amount must be numeric; got 'xyz'"` | Yes |
| Negative amount | `"Row 4: Amount must be positive; got '-500'"` | Yes |
| Stamp Duty/STT validation | `"Row 6: Stamp Duty transaction must have empty Price and Unit Balance columns"` | Yes |
| SELL missing units | `"Row 8: SELL/REDEMPTION transaction must have Units field populated"` | Yes |
| XIRR convergence failure | `"Cannot calculate XIRR for this data. Please verify all transactions."` | Yes |
| Duplicate rows | Allowed | No |

---

## 7. XIRR Calculation & Summary Metrics

### XIRR Calculation Logic
1. **Filter transactions:** Exclude Gross Purchase and STT Paid transactions from the raw cash flow list (STT Paid is handled separately via netting, not as a standalone outflow)
2. **Build cash flow array:**
   - PURCHASE/Investment transactions: **negative** (cash outflow)
   - STAMP_DUTY transactions: **negative** (cash outflow — true cost of investment)
   - SELL/REDEMPTION transactions: **positive** (cash inflow) — amount = absolute value of transaction amount
   - DIVIDEND REINVEST: **negative** (reinvested = additional investment)
3. **Net STT Paid against same-date redemptions:** For each STT Paid transaction, subtract its amount from the SELL/REDEMPTION cash flow on the same date. This reduces the net inflow for that date, producing a more accurate XIRR that reflects the true proceeds received after STT.
4. **Apply XIRR formula:** Calculate using `numpy_financial.irr()` or `pyxirr.xirr()`
5. **Handle convergence failure:** If XIRR cannot converge (rare edge case), return error: `"Cannot calculate XIRR for this data. Please verify all transactions."`
6. **Format result:** Round to 2 decimal places

### Summary Metrics Calculation

| Metric | Formula | Format |
|--------|---------|--------|
| **Total Invested** | Sum of all PURCHASE/Buy/SIP/Systematic Investment/Stamp Duty transaction amounts (STT Paid and Gross Purchase excluded) | Currency with 2 decimals (₹) |
| **Final Proceeds** | Sum of all SELL/REDEMPTION transaction amounts (absolute values), less total STT Paid amounts | Currency with 2 decimals (₹) |
| **Profit/Loss** | Final Proceeds – Total Invested | Currency with 2 decimals (₹); green if positive, red if negative |

### Display Format
- **XIRR:** `12.54%` (2 decimal places, no "p.a.", "annualized", or year-specific notation)
- **Amount fields:** ₹12,50,000.00 (thousands separator, 2 decimal places)
- **Units:** 100.123 (3 decimal places, no thousands separator)
- **Price:** As entered by user (2–4 decimals, no modification)
- **Unit Balance:** 100.123 (3 decimal places, no thousands separator)

---

## 8. Loading States & UX

### Phase 1: Upload (0–2 seconds, deterministic)
- **Spinner visible:** "Processing file..."
- Upload progress: Optional; omit for simplicity if FastAPI handles quickly
- Upload area **disabled** (prevent duplicate submissions)

### Phase 2: Backend Processing with Skeleton (2+ seconds)
- **Spinner replaced with skeleton loader:**
  - Grid area shows 6-column skeleton structure (Date, Transaction Type, Amount, Units, Price, Unit Balance)
  - ~8 placeholder rows with variable heights (some rows shorter to reflect sparse data like Stamp Duty)
  - Shimmer/pulse CSS animation
  - Communicates: "Data is loading, a table with these columns is coming here"
- XIRR area shows loading placeholder (e.g., "— calculating")
- Summary metrics area shows loading placeholder

### Phase 3: Success (Data Arrives)
- **Skeleton removed instantly**
- **XIRR panel populates** with prominent percentage (green/red indicator)
- **Summary metrics panel populates** with Total Invested, Final Proceeds, Profit/Loss
- **Grid populates** with actual transaction data
- Upload area re-enabled (optional: "Upload another file" button)

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
| **Required final redemption** | Final transaction must be SELL/REDEMPTION with Unit Balance = 0 | XIRR requires terminal cash flow and complete exit |
| **Single worksheet** | Only first worksheet parsed; additional worksheets ignored | Simplifies parsing; user can split files if needed |
| **Date range** | Transactions from 1960 onwards only; reject future dates | Practical range for financial data |
| **Date format** | DD/MM/YYYY only (e.g., 18/12/2024) | Standardizes input; rejects other formats |
| **Decimal precision** | XIRR: 2 decimals; Amount: 2 decimals; Units: 3 decimals; Price: 2–4 (user entry) | Financial standard for India (₹ system) |
| **Strict validation** | File rejected on data inconsistencies; conditional field requirements enforced per transaction type | Ensures accuracy for financial calculations |
| **Column header matching** | Case-insensitive; leading/trailing spaces trimmed | Handles user typos; flexible parsing |
| **Transaction type matching** | Case-insensitive; recognizes common variants | Handles diverse fund statement formats |
| **No authentication** | Public access; no user accounts | Simplifies MVP; can add later |
| **No persistence** | Results not saved; user must re-upload to recalculate | Reduces complexity + storage costs |
| **Concurrent uploads** | All uploads share single Render instance; may be slow if 2+ users simultaneous | Acceptable for free tier; document in FAQ |

---

## 10. Future Enhancements (Not in v1)

- [ ] **Sorting:** Click column headers to sort grid (by Date, Amount, Price, Unit Balance)
- [ ] **Filtering:** Filter transactions by type (PURCHASE/SELL/DIVIDEND)
- [ ] **Pagination:** For datasets > 100 rows
- [ ] **Export results:** Download grid as CSV or PDF with XIRR + summary metrics
- [ ] **Multiple funds:** Upload 2+ files, compare XIRR across funds
- [ ] **Persistent storage:** Add database to save user records (migrating from free tier)
- [ ] **User accounts:** Authentication, historical data, portfolio tracking
- [ ] **API documentation:** Auto-generated Swagger docs (FastAPI provides this automatically)
- [ ] **Advanced metrics:** CAGR, absolute return %, MWR vs TWR comparison
- [ ] **Currency support:** Handle multi-currency transactions
- [ ] **Date format flexibility:** Accept multiple date formats (DD-MMM-YYYY, YYYY-MM-DD, etc.)

---

## 11. Testing Criteria (QA Checklist)

### File Upload
- [ ] Accept valid .xlsx files ≤ 10 MB
- [ ] Reject non-.xlsx formats with clear error
- [ ] Reject files > 10 MB with file size error message

### Column Header Parsing
- [ ] Accept column headers in any case (Date, date, DATE) with case-insensitive matching
- [ ] Trim leading/trailing spaces from column headers
- [ ] Reject files with missing required columns

### Data Validation
- [ ] Reject missing columns with specific column name
- [ ] Reject invalid date formats with row number + expected format (DD/MM/YYYY)
- [ ] Reject dates outside 1960–today range with specific error
- [ ] Reject non-numeric values in numeric columns with row number
- [ ] Reject files without final SELL/REDEMPTION with Unit Balance = 0
- [ ] Reject files with > 10,000 rows
- [ ] Reject negative amounts for PURCHASE transactions
- [ ] Accept Buy, Purchase, SIP, SIP Purchase, Systematic Investment, Systematic Investment Plan as equivalent investment transactions
- [ ] Accept DIVIDEND REINVEST (with space) as valid investment transaction
- [ ] Accept SELL and REDEMPTION as equivalent exit transactions
- [ ] Accept SELL/REDEMPTION rows with Price and Unit Balance populated (no longer rejected)
- [ ] Accept SELL/REDEMPTION rows with negative Amount (sign stripped, absolute value used)
- [ ] Accept SELL/REDEMPTION rows with negative Units (absolute value used in balance check)
- [ ] Reject Stamp Duty / STT Paid with non-empty Price or Unit Balance fields
- [ ] Accept Stamp Duty / STT Paid with empty Units field
- [ ] Reject Stamp Duty / STT Paid transactions where Price or Unit Balance are not empty

### Transaction Type Normalization
- [ ] Accept case-insensitive transaction types (BUY, buy, Buy all valid)
- [ ] Recognize all documented variants (Purchase, Buy, SIP, Systematic Investment, etc.)
- [ ] Reject unrecognized transaction types with clear error

### XIRR Calculation
- [ ] Calculate correct XIRR for sample fund data (verify manually)
- [ ] Exclude Stamp Duty from XIRR cash flows (included as outflow)
- [ ] Net STT Paid against same-date SELL/REDEMPTION in XIRR cash flow
- [ ] Display positive XIRR in green; negative in red
- [ ] Round XIRR to 2 decimal places (e.g., 12.54%)
- [ ] Handle edge case: very high XIRR (e.g., quick flip)
- [ ] Handle edge case: very low XIRR (e.g., long hold)
- [ ] Return error when XIRR cannot converge

### Summary Metrics
- [ ] Total Invested = sum of all PURCHASE/SIP/Systematic Investment/Stamp Duty transactions (STT Paid excluded)
- [ ] Final Proceeds = sum of all SELL/REDEMPTION amounts (absolute values) less total STT Paid amounts
- [ ] Profit/Loss = Final Proceeds – Total Invested
- [ ] Display metrics with ₹ symbol and 2 decimal places
- [ ] Color code Profit/Loss (green positive, red negative)

### Grid Display
- [ ] Grid renders with correct column order
- [ ] Grid displays data in file order (unsorted)
- [ ] Empty cells shown as "—" or blank
- [ ] Units displayed with 3 decimal places
- [ ] Amount displayed with 2 decimal places and ₹ symbol
- [ ] Price displayed as user entered (2–4 decimals)
- [ ] Unit Balance displayed with 3 decimal places

### UI/UX
- [ ] Spinner shows during upload (< 2 seconds typically)
- [ ] Skeleton loader shows during backend processing
- [ ] XIRR prominently displayed after processing (at least 36px)
- [ ] Summary metrics displayed below XIRR
- [ ] Error banner shows specific validation errors
- [ ] Upload area re-enables after error
- [ ] Error messages are actionable (e.g., "Row 5: Invalid date...")

### Performance
- [ ] Upload + processing completes within 30 seconds
- [ ] Cold-start skeleton displays within 2–5 seconds
- [ ] Grid renders smoothly (no stuttering with ~5000 rows)

### Concurrency
- [ ] Two simultaneous uploads don't corrupt data
- [ ] Error in one upload doesn't affect another

### Multiple Worksheets
- [ ] Only first worksheet is parsed
- [ ] Additional worksheets are ignored without error

### Edge Cases
- [ ] Duplicate rows allowed (same date, type, amount)
- [ ] Very old transactions (1960–1970) accepted
- [ ] Recent transactions accepted

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
| **Case-insensitive headers** | Handles diverse fund statement formats | Requires normalization logic |
| **DD/MM/YYYY only** | Standardizes input; aligns with Indian tabular Excel fund statement exports | Rejects other formats including DD-MMM-YYYY; can be extended in future version |
| **Mandatory summary metrics** | Provides financial context for XIRR; improves UX | Slightly more backend processing |
| **Stamp Duty/STT included in XIRR as outflow** | Stamp Duty/STT represent a real cash cost paid by the investor and should be reflected in the true annualised return; including them as negative outflows produces a more accurate XIRR | Slightly lowers the reported XIRR vs the previous approach, but more accurately reflects real investment cost |
| **Gross Purchase excluded from XIRR and Total Invested** | Gross Purchase is a summary row; the actual cash flows are captured by Net Purchase + Stamp Duty in the same transaction group. Including it would double-count the invested amount. | Real-world fund statements (e.g., MFUTILITY) always split gross amount into Net Purchase + Stamp Duty rows, so exclusion is semantically correct. |
| **STT Paid split from Stamp Duty** | STT Paid (Securities Transaction Tax) is levied at redemption time and should be netted against the redemption inflow in XIRR, not treated as a purchase-side cost. Keeping it separate from Stamp Duty allows correct categorization. | Requires a new `STT_PAID` category, separate normalizer variants, and netting logic in the XIRR calculator. |
| **SELL/REDEMPTION Price/Unit Balance optional** | Some fund statement exports populate Price and Unit Balance on SELL/REDEMPTION rows. Rejecting these was unnecessarily strict; the fields are informational and do not affect XIRR or summary calculation. | Removes a validation that previously caused file rejections for otherwise valid data. |
| **Negative SELL/REDEMPTION amounts/units accepted** | Some fund statement exports represent SELL/REDEMPTION amounts or units as negative numbers. Accepting and taking the absolute value avoids unnecessary user friction while producing identical calculation results. | Adds sign-stripping logic in the normalizer; no impact on calculation accuracy. |

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
- **Summary metrics accuracy:** Total Invested, Final Proceeds, Profit/Loss calculated correctly

---

## 15. Resolved Implementation Questions

### XIRR Library Choice
**Decision:** Use `numpy_financial` (or `pyxirr` as alternative)
- **Rationale:** Production-ready, matches Excel's XIRR function exactly, handles all edge cases, <100ms for 10k transactions, zero maintenance burden
- **Fallback:** If XIRR fails to converge, return error message to user

### Skeleton Animation
**Decision:** Use CSS shimmer (pure CSS animation)
- **Rationale:** ~2KB overhead vs +10-15KB for library, GPU-accelerated 60fps, full control over timing, minimizes bundle size for Render free tier cold-start

### Error Logging
**Decision:** No error logging for now
- **Rationale:** Render free tier has limited log retention; data is transient anyway

### CORS Configuration
**Decision:** Open to all origins
- **Rationale:** No sensitive data; stateless application; no authentication

### Rate Limiting
**Decision:** No per-IP rate limiting for now
- **Rationale:** Acceptable for free tier MVP; can add if abuse occurs

---

## 16. Implementation Roadmap

### Phase 1: Setup (Week 1)
- [ ] Environment setup (Python, Node.js, Git, VS Code)
- [ ] GitHub repository initialized
- [ ] Pre-installation checklist completed

### Phase 2: Specification (Week 1)
- [x] Feature intent document completed (this document)
- [ ] API specification finalized
- [ ] Database schema (N/A for stateless v1)

### Phase 3: Backend Build (Week 2)
- [ ] FastAPI project scaffold
- [ ] File upload endpoint (`POST /api/upload`)
- [ ] Excel parsing (openpyxl/pandas)
- [ ] Validation engine
- [ ] XIRR calculation logic
- [ ] Error handling + response formatting
- [ ] Testing + sample data

### Phase 4: Frontend Build (Week 2–3)
- [ ] React project scaffold (Vite)
- [ ] Upload component (drag-and-drop)
- [ ] XIRR display panel
- [ ] Summary metrics panel
- [ ] Transaction grid component
- [ ] Skeleton loader + animations
- [ ] Error banner + retry logic
- [ ] State management (useState/Context or simple React state)
- [ ] Styling (CSS Modules or Tailwind)

### Phase 5: Local Testing (Week 3)
- [ ] Manual testing of happy path
- [ ] Error scenario testing
- [ ] Edge case validation
- [ ] Performance testing (file size, transaction count)
- [ ] Cross-browser testing

### Phase 6: Render Deployment (Week 3)
- [ ] Backend deployment to Render
- [ ] Frontend deployment to Render (static site)
- [ ] CORS configuration
- [ ] API endpoint verification
- [ ] Cold-start testing

### Phase 7: End-to-End Verification (Week 4)
- [ ] Live testing on Render
- [ ] User acceptance testing
- [ ] Documentation (README, FAQ)
- [ ] Launch readiness

---

**End of Feature Document**

---

### Sign-Off
- **Feature Owner:** Hari
- **Prepared:** March 18, 2026  
- **Revised:** June 7, 2026 (Date format changed from DD-MMM-YYYY to DD/MM/YYYY)
- **Revised:** June 8, 2026 (Download Sample Template feature added to Upload Area)
- **Revised:** June 8, 2026 (Stamp Duty / STT Paid included in XIRR cash flows as outflows)
- **Revised:** June 11, 2026 (Redemption/SELL enhancements: Price/Unit Balance optional; STT Paid split from Stamp Duty as separate category; negative amounts/units accepted & privacy disclaimer in screen)
- **Status:** Completed — Redemption/SELL Enhancements, STT Paid Split & Privacy Disclaimer
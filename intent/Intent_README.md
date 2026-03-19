# Intent Folder

## Overview

The **Intent Folder** (`/intent`) is the centralized documentation hub for the **MutualFund-Return-Tracker-IDD** project. It contains:

- **What we're building** (feature specifications, user needs, success metrics)
- **How we're structuring it** (architecture, folder layout, tech stack decisions)
- **Why we made certain choices** (decision logs, trade-offs, rationale)

This folder is the **source of truth** during development. Every phase references these documents to stay aligned with the original vision and technical strategy.

---

## Contents

### 1. **README.md** (This File)
- **File location:** `/intent/README.md`
- **Purpose:** Guide to the intent folder structure, versioning, and update process
- **Audience:** All team members (developers, reviewers, stakeholders)
- **Update frequency:** Low (reflects folder organization, not project changes)

### 2. **mutual-fund-xirr-tracker-feature.md** — Feature Specification (v2.0)
- **File location:** `/intent/mutual-fund-xirr-tracker-feature.md`
- **Shorthand in conversation:** "feature.md"
- **Purpose:** Complete feature specification for the XIRR tracker application
- **Scope:** User journeys, UI requirements, API contracts, validation rules, edge cases, testing checklist, decision log
- **Audience:** Developers (backend & frontend), QA, product owner
- **Update frequency:** As feature scope evolves (new validations, UI changes, API revisions)
- **Status:** Ready for Development (March 19, 2026)
- **Size:** ~670 lines, 16 major sections

### 3. **product-structure.md** — Architecture & Product Structure (v1.0)
- **File location:** `/intent/product-structure.md`
- **Shorthand in conversation:** "structure.md" or "architecture doc" or "product-structure.md"
- **Purpose:** Technical architecture, folder layout, deployment strategy, and file organization
- **Scope:** Directory structure, tech stack rationale, Render free tier optimization, development workflow, scaling path
- **Audience:** Developers, DevOps, tech leads
- **Update frequency:** When folder organization or tech stack changes (less frequent than feature doc)
- **Status:** Ready for Phase 2 (Backend Build)
- **Size:** ~850 lines, comprehensive architecture reference

---

## Project Vision (Quick Recap)

**Build a lightweight, user-friendly web application that empowers Indian retail investors to upload their mutual fund transaction records and instantly calculate XIRR (Extended Internal Rate of Return) alongside a clean, interactive transaction ledger.**

### Core Problem
Retail MF investors struggle to:
- Track transactions across multiple funds
- Calculate XIRR (the standard MF performance metric in India)
- View organized transaction records
- Understand returns independent of market timing

### Core Solution
A **free, stateless, browser-based tool** that:
1. Accepts Excel files with MF transaction data
2. Parses and validates transaction records
3. Calculates precise XIRR in <5 seconds
4. Displays results in an interactive dashboard
5. Requires zero backend account or data persistence

---

## How to Use This Folder

### For First-Time Readers
1. Start here (Intent README)
2. Read **mutual-fund-xirr-tracker-feature.md** (feature.md) for the complete feature spec
3. Read **product-structure.md** (structure.md) for technical architecture

### During Phase 1 (Setup)
- Reference the **project overview** section to understand vision and scope
- No need to read entire intent documents yet

### During Phase 2 (Spec Writing)
- Reference **feature.md** section 3.4 (Validation) to create test cases
- Reference **feature.md** section 10.2 (API Endpoint) to formalize OpenAPI spec
- Reference **feature.md** section 4.4 (Transaction Grid) to design Pydantic models

### During Phase 3 (Backend Development)
- Reference **feature.md** for all requirements (validation rules, API contract, error messages)
- Reference **product-structure.md** for folder layout and service organization
- Reference the **Decision Log** (in feature.md) when weighing trade-offs

### During Phase 4 (Frontend Development)
- Reference **feature.md** section 4 (Frontend Requirements) for UI details
- Reference **feature.md** section 10.2 (API Endpoint) to understand the backend contract
- Reference **product-structure.md** for component organization

### During Code Review (Phases 3-4)
- Check that code matches the feature spec (requirements in feature.md)
- Check that code lives in the right folder (structure in product-structure.md)
- Check that decisions align with the decision log

### During Deployment (Phase 6)
- Use **product-structure.md** for deployment architecture (Render config, environment variables)
- Use **feature.md** for success metrics (XIRR accuracy, performance targets)

---

## Document Versioning

### Intent Documents (This Folder)

| Document | Version | Date | Status | Next Update Trigger |
|----------|---------|------|--------|---------------------|
| **feature.md** | 2.0 | March 19, 2026 | Ready for Development | New validation rules, UI changes, API revisions |
| **product-structure.md** | 1.0 | March 19, 2026 | Ready for Phase 2 | Folder reorganization, tech stack changes |

### Version Numbering
- **Feature Doc:** Major.Minor (2.0, 2.1, 3.0)
  - Major bump: Feature scope change (new endpoint, new validation)
  - Minor bump: Clarifications, edge case additions
- **Product Structure:** Major.Minor (1.0, 1.1, 2.0)
  - Major bump: Significant restructuring (new service, new test framework)
  - Minor bump: File organization tweak, dependency update

### Code Versioning (Separate)
- Uses semantic versioning: 1.0.0, 1.1.0, 2.0.0
- Tags on GitHub releases
- Independent from intent document versions

---

## Key Information from Feature Spec (Quick Reference)

### Technology Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python + FastAPI (async) |
| Frontend | React + Vite (SPA) |
| Data Processing | pandas, openpyxl (parsing), pyxirr (XIRR calculation) |
| Hosting | Render free tier (Web Service + Static Site) |
| Source Control | GitHub |

### MVP Scope (Phase 1-4)
✅ Single fund upload (one file per session)
✅ XIRR calculation + summary metrics
✅ Transaction grid display (6 columns, file order, no sorting in v1)
✅ Drag-and-drop file upload
✅ Skeleton loader for cold-start UX
✅ Strict validation with actionable error messages
✅ Render free tier deployment

❌ Multi-fund tracking
❌ User accounts / data persistence
❌ CSV support
❌ Real-time portfolio tracking

### Core Features
- **Excel File Upload:** Drag-and-drop or file picker (≤10 MB, .xlsx only)
- **XIRR Calculation:** Annualized return, green/red color-coded, rounded to 2 decimal places
- **Summary Metrics:** Total Invested, Final Proceeds, Profit/Loss (mandatory)
- **Transaction Grid:** 6-column display (Date, Type, Amount, Units, Price, Unit Balance)
- **Validation:** Strict (rejects invalid formats, missing columns, data type mismatches)
- **Error Handling:** Detailed error messages (e.g., "Row 5: Invalid date format")

### Key Constraints
- **File Format:** DD-MMM-YYYY dates only (e.g., "15-Jan-2020")
- **Transaction Limit:** 10,000 rows max (safe for Render 512 MB memory)
- **File Transactions:** Minimum 2 (1 buy + 1 redemption)
- **Final Transaction:** Must be SELL/REDEMPTION with Unit Balance = 0
- **XIRR Calculation:** Excludes Stamp Duty/STT Paid from return calculation

### Success Metrics
- XIRR calculation < 5 seconds (excluding cold-start)
- File parsing & validation < 2 seconds
- Page load < 2 seconds
- User error resolution on first attempt (90%+ with clear error messages)
- XIRR accuracy verified against Excel's XIRR function

---

## Key Information from Product Structure (Quick Reference)

### Directory Layout
```
MutualFund-Return-Tracker-IDD/
├── intent/                    # This folder (feature spec & architecture)
│   ├── README.md
│   ├── mutual-fund-xirr-tracker-feature.md
│   └── product-structure.md
│
├── backend/                   # FastAPI (Python)
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── Procfile
│   ├── openapi.yaml
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── upload.py
│   │   ├── services/
│   │   │   ├── file_parser.py
│   │   │   ├── validator.py
│   │   │   ├── xirr_calculator.py
│   │   │   └── transaction_processor.py
│   │   ├── models/
│   │   ├── utils/
│   │   ├── exceptions/
│   │   └── tests/
│   └── logs/
│
├── frontend/                  # React + Vite
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── utils/
│   │   ├── assets/
│   │   └── tests/
│   └── dist/
│
├── scripts/                   # Automation (setup, dev, test, build)
├── docs/                      # Additional documentation (created during dev)
├── .github/                   # GitHub Actions CI/CD
├── render.yaml                # Render deployment config
├── .gitignore
├── .env.example
├── LICENSE
└── README.md
```

### Backend Architecture (Key Services)
| Service | Responsibility | Key Methods |
|---------|-----------------|-------------|
| **file_parser.py** | Excel parsing (openpyxl/pandas), extract first sheet only | `parse_excel()` |
| **validator.py** | Data validation (columns, types, dates, amounts, balances) | `validate_transactions()` |
| **xirr_calculator.py** | XIRR calculation, summary metrics (total invested, proceeds, P/L) | `calculate_xirr()`, `get_summary_metrics()` |
| **transaction_processor.py** | Normalize transaction types, handle edge cases | `process_transaction()`, `normalize_type()` |

### Frontend Architecture (Key Components)
| Component | Responsibility | File |
|-----------|-----------------|------|
| **UploadArea** | Drag-and-drop file input, file validation | `UploadArea.jsx` |
| **LoadingSpinner** | Shows during upload (<2 seconds) | `LoadingSpinner.jsx` |
| **SkeletonLoader** | Shows during backend processing (cold-start UX) | `SkeletonLoader.jsx` |
| **XirrDisplay** | Displays XIRR prominently (36px, green/red) | `XirrDisplay.jsx` |
| **SummaryMetrics** | Shows Total Invested, Final Proceeds, P/L | `SummaryMetrics.jsx` |
| **TransactionGrid** | 6-column table with transaction data | `TransactionGrid.jsx` |
| **ErrorBanner** | Displays validation errors with retry button | `ErrorBanner.jsx` |

### Render Free Tier Optimization
- **Backend:** Single FastAPI instance (async handles concurrent requests)
- **Frontend:** Static React site (no server-side rendering)
- **Cold-Start Mitigation:** Skeleton loader hides ~30s delay
- **Memory Safe:** 10k transaction limit with 512 MB memory
- **Stateless by Design:** No database, no persistent file storage

---

## Development Phases (7 Total)

| Phase | Focus | Owner | Duration | Status |
|-------|-------|-------|----------|--------|
| **Phase 1: Setup** | Environment setup, git repo, pre-install checklist | You | ~3 hours | In Progress |
| **Phase 2: Spec Writing** | API specs, Pydantic models, test fixtures (from feature.md) | You | ~4 hours | Pending |
| **Phase 3: Backend** | FastAPI setup, file parser, validator, XIRR calculator, tests | You | ~15 hours | Pending |
| **Phase 4: Frontend** | React components, state management, API integration, styling | You | ~15 hours | Pending |
| **Phase 5: Local Testing** | Manual testing, edge cases, performance, cross-browser | You | ~4 hours | Pending |
| **Phase 6: Deployment** | Render setup, deploy backend & frontend, CORS config | You | ~3 hours | Pending |
| **Phase 7: Verification** | Live testing, UAT, docs, launch readiness | You | ~2 hours | Pending |

### What is Phase 2: Spec Writing?

Phase 2 creates **detailed technical specifications** from feature.md that serve as blueprints for Phase 3 backend development. Note: feature.md and product-structure.md (the intent documents) are **already complete**—Phase 2 formalizes *how* to implement them.

**Phase 2 Deliverables:**

1. **API Specification (OpenAPI/Swagger)**
   - Formalize the HTTP contract for `POST /api/upload` from feature.md section 10.2
   - Define exact request/response shapes, status codes, error responses
   - Document all possible error scenarios (400, 500, etc.)

2. **Pydantic Data Models**
   - Convert feature.md section 4.4 (Transaction Grid columns) into Python dataclasses
   - Create models for: `Transaction`, `SummaryMetrics`, `UploadResponse`, `ValidationError`
   - Add validation rules (format, range, required fields) from feature.md section 3.4

3. **Test Fixtures & Test Cases**
   - Create sample Excel files for each edge case in feature.md section 3.4
   - Define expected outputs (XIRR values, error messages)
   - Map validation rules to test cases (e.g., "invalid date format" → `test_invalid_date.xlsx`)

4. **Error Code Reference**
   - Codify all error messages from feature.md section 3.4
   - Map to HTTP status codes (400 for validation, 500 for server errors)
   - Example: "Row 5: Date '01-01-2020' is invalid (expected DD-MMM-YYYY)"

**Why Phase 2 Matters:**
- Phase 3 (backend) uses these specs as a reference while coding
- Prevents misinterpretation of feature.md requirements
- Makes testing systematic and reproducible
- Serves as documentation for the API contract

---

## Decision Log (Key Decisions)

### Why Stateless?
✅ Simpler deployment on free tier (no database cost)
✅ Faster development (no schema design, migrations)
⚠️ Trade-off: Users must re-upload for new calculations (acceptable for MVP)

### Why Excel Only?
✅ Mutual fund statements typically delivered as Excel files
✅ Simpler parsing (openpyxl is mature)
⚠️ Trade-off: No CSV support (can add in v2)

### Why Strict Validation?
✅ Ensures financial data accuracy (critical for returns calculation)
✅ Catches data quality issues early
⚠️ Trade-off: Rejects borderline files; forces user to clean data

### Why DD-MMM-YYYY Dates Only?
✅ Standardized format (aligns with Indian financial statements)
✅ Reduces parsing ambiguity
⚠️ Trade-off: Rejects other formats (can support more in v2)

### Why No Sorting in v1?
✅ Simpler frontend implementation (file order, no state overhead)
✅ Faster shipping (less code)
⚠️ Trade-off: Less intuitive (sorting added in v2)

### Why Skeleton Loader?
✅ Improves perceived performance during cold-start delays
✅ User sees progress, not a frozen spinner
⚠️ Trade-off: Slightly more complex React component

### Why FastAPI?
✅ Async handles concurrent file uploads efficiently
✅ Auto-generated Swagger docs
✅ Better performance than Flask for I/O-bound work
⚠️ Trade-off: Slightly steeper learning curve than Flask

### Why Render Free Tier?
✅ Zero cost for MVP (sufficient for learning project)
✅ Simple one-click deployment
✅ Good documentation, active community
⚠️ Trade-off: Cold-start delays, 512 MB memory limit, single instance

---

## How Intent Relates to Code

### Example 1: File Validation
- **Intent (feature.md, Section 3):** "Date column must be DD-MMM-YYYY format. Reject if invalid."
- **Product Structure:** "Validation logic lives in `backend/app/services/validator.py`"
- **Code:** `validator.py` implements date parsing and returns specific error message

### Example 2: UI Layout
- **Intent (feature.md, Section 4.2):** "XIRR displayed at 36px minimum, green if positive, red if negative"
- **Product Structure:** "XIRR display lives in `frontend/src/components/XirrDisplay.jsx`"
- **Code:** `XirrDisplay.jsx` renders with specific styling and conditional coloring

### Example 3: API Response
- **Intent (feature.md, Section 10.2):** "Response includes xirr (number), summaryMetrics (object), transactions (array), and optional error"
- **Product Structure:** "Response models live in `backend/app/models/response.py`"
- **Code:** Pydantic models define response shape; FastAPI serializes to JSON

### Example 4: Transaction Grid
- **Intent (feature.md, Section 4.4):** "Grid shows 6 columns: Date, Type, Amount, Units, Price, Unit Balance. Display in file order."
- **Product Structure:** "Grid component is `frontend/src/components/TransactionGrid.jsx`"
- **Code:** Component renders table with 6 columns, accepts transactions array, no sorting applied

---

## When to Update Intent Documents

### Update **feature.md** When:
- ✏️ Adding a new validation rule (e.g., "reject dates before 1960")
- ✏️ Changing UI requirements (e.g., "XIRR font now 48px")
- ✏️ Modifying API response format (e.g., "add confidence interval to XIRR")
- ✏️ Adding a new feature (e.g., "multi-fund tracking")
- ✏️ Discovering a major edge case during testing
- ✏️ Changing success metrics or performance targets

**Do NOT update just for:**
- Bug fixes (document in commit message)
- Code refactoring (doesn't change behavior)
- Performance improvements (document in PR)
- Internal implementation details

### Update **product-structure.md** When:
- 📁 Adding a new folder or service (e.g., `backend/app/cache/`)
- 📁 Changing tech stack (e.g., switching from FastAPI to Flask)
- 📁 Restructuring existing folders (e.g., moving components around)
- 📁 Adding new type of test (e.g., E2E tests with Playwright)
- 📁 Changing deployment strategy (e.g., Docker containers)

**Do NOT update just for:**
- File additions (add, don't reorganize)
- README updates
- Documentation folder changes
- Dependency upgrades (unless it changes architecture)

---

## How to Update Intent Documents

### Step 1: Identify the Need
- Feature change? → Update `feature.md`
- Structure change? → Update `product-structure.md`
- Both? → Update both

### Step 2: Edit the Document
1. Open the relevant file (`feature.md` or `product-structure.md`)
2. Locate the section to update
3. Make your change (clear, concise language)
4. Update the version number and date at the top:
   ```markdown
   **Version:** 2.1  
   **Date:** March 25, 2026  
   **Revision:** Added multi-fund support to scope
   ```

### Step 3: Notify the Team
- Create a PR with the intent document change
- Add summary to PR description: "Updated feature.md v2.0 → v2.1: Added date range filtering"
- Reference the specific section: "See section 3.5: Feature Additions"
- Require review before merge (someone else approves)
- Link to GitHub issue if applicable

### Step 4: Tag the Release
- After merging, tag the commit: `git tag v2.1-feature.md`
- Update GitHub releases with changelog

---

## Real-World Example: Adding a Feature During Development

**Scenario:** You're in Phase 3 (Backend), and stakeholders request that XIRR also display the "YTD XIRR" (year-to-date return).

### Step 1: Update Intent
1. Open `feature.md`
2. Find section "4.2 XIRR Display Panel"
3. Add: "Additionally display YTD XIRR (year-to-date return)"
4. Update decision log if this represents a new design decision
5. Update version: 2.0 → 2.1
6. Create PR with title: `intent: Add YTD XIRR display to feature spec`

### Step 2: Update Structure if Needed
1. Check if backend service needs a new module (e.g., `xirr_ytd_calculator.py`)
2. If yes, update `product-structure.md` to reflect new file
3. Version: 1.0 → 1.1

### Step 3: Implement Code
1. Create backend logic to calculate YTD XIRR
2. Create frontend component to display YTD XIRR
3. Reference feature.md in code comments

### Step 4: Update Tests
1. Add test cases that verify YTD XIRR calculation
2. Reference feature.md section in test docstrings

### Step 5: Merge & Release
1. Merge intent changes first (separate PR)
2. Then merge code changes (code PR)
3. Tag both: `git tag v2.1-feature.md v1.0.1-code`

---

## Governance

### Who Maintains Intent Documents?
- **Feature.md:** Product Owner (Hari) + Tech Lead (during implementation)
- **Product-Structure.md:** Tech Lead + Backend/Frontend Leads

### How Often Should I Reference These?
| Role | Frequency | Action |
|------|-----------|--------|
| **Backend Developer** | Daily | Check feature.md for API spec, validation rules |
| **Frontend Developer** | Daily | Check feature.md for UI requirements |
| **Code Reviewer** | Per PR | Verify code matches intent |
| **Product Owner** | Weekly | Track scope, monitor changes, update intent |
| **Tech Lead** | Weekly | Ensure architecture matches product-structure.md |

### Who Approves Changes to Intent?
- **Feature.md changes:** Product Owner + one developer
- **Product-Structure.md changes:** Tech Lead + one senior developer
- **Both:** Agreement required before implementation begins

---

## Filename Clarity: Actual Names vs Shorthand

To avoid confusion when working with Claude or other developers, it's important to understand the difference between actual filenames and conversational shorthand:

| Document | Actual Filename | Shorthand in Conversation | Use Full Path When |
|----------|-----------------|---------------------------|-------------------|
| Feature Specification | `mutual-fund-xirr-tracker-feature.md` | "feature.md" | Asking Claude to read or analyze |
| Architecture Guide | `product-structure.md` | "structure.md" or "architecture" | Asking Claude to generate code |
| Intent Guide | `README.md` | "Intent README" | Linking in documentation |

**Examples:**

✅ **Casual conversation:** "See feature.md section 3.4 for validation rules"
✅ **Asking Claude to build:** "Read `/intent/mutual-fund-xirr-tracker-feature.md` and create the validator"
✅ **Code comments:** "// Based on feature.md, this validates dates"
✅ **Documentation links:** `[Feature Spec](./mutual-fund-xirr-tracker-feature.md)`

❌ **Don't say:** "Read feature.md" (ambiguous—what file?)
❌ **Don't say:** "Check structure.md for backend" (missing path context)

---

| Document | Purpose | Audience | Size |
|----------|---------|----------|------|
| [feature.md](./mutual-fund-xirr-tracker-feature.md) | Complete feature spec (16 sections, all details) | Developers, QA, Product | ~670 lines |
| [product-structure.md](./product-structure.md) | Architecture & folder layout (complete reference) | Developers, DevOps | ~850 lines |
| [../README.md](../README.md) | Project overview & quick start | Everyone | ~100 lines |
| [../backend/](../backend/) | Backend source code (to implement) | Backend developers | TBD |
| [../frontend/](../frontend/) | Frontend source code (to implement) | Frontend developers | TBD |

---

## FAQ: Intent Folder

### Q: Do I need to read all three documents before coding?
**A:** No, but read at least the relevant section from `feature.md` for your task. For example, if building the upload endpoint, read section 3 (File Validation) and section 10.2 (API Endpoint). For UI work, read section 4 (Frontend Requirements).

### Q: What if I find a mistake in the intent documents?
**A:** Create an issue or PR with a fix. Mistakes in intent documents catch bugs early, so they're super valuable to fix.

### Q: Can I change the intent documents while coding?
**A:** Yes, but follow this workflow:
1. **Small clarifications:** Fix directly (typos, wording)
2. **Scope changes:** Create a PR, get approval first (blocks coding until approved)
3. **Edge case discoveries:** Update feature.md with the edge case, then implement

### Q: Why are intent documents separate from code?
**A:** Intent documents are **what we decided to build**; code is **how we build it**. Keeping them separate makes it easy to see the original design even if code evolves due to bugs, refactoring, or optimization.

### Q: What's the difference between feature.md and product-structure.md?
**A:**
- **feature.md = WHAT:** User journeys, API spec, validation rules, UI details, edge cases, decision log
- **product-structure.md = HOW:** Folder layout, tech stack rationale, services/components, deployment strategy

### Q: Do intent documents replace code comments?
**A:** No, they're complementary. Intent documents explain *why* decisions were made; code comments explain *how* code works.

### Q: What if I disagree with a decision in the intent?
**A:** Great! Raise it in a discussion:
1. Comment in the PR discussing the decision
2. Provide your rationale
3. Propose an alternative
4. Get consensus before changing intent

---

## Maintenance Schedule

### During Development (Weekly)
- [ ] Check if any code PRs conflict with intent documents
- [ ] Flag scope creep (new features not in intent)

### End of Each Phase
- [ ] Review decisions made during phase
- [ ] Update intent documents if new insights discovered
- [ ] Update version numbers

### Monthly
- [ ] Check if trade-offs are still valid
- [ ] Review decision log, see if any decisions need revisiting
- [ ] Check if scaling path (stateless → database) is still on track

### Before Deployment (Phase 6)
- [ ] Verify all features coded match feature.md
- [ ] Verify all code lives in folders per product-structure.md
- [ ] Update success metrics section with actual results

---

## Summary

The **Intent Folder** is your source of truth. It captures:
- ✅ **What** you're building (feature spec with requirements)
- ✅ **How** you're structuring it (product structure with architecture)
- ✅ **Why** you made certain choices (decision log with trade-offs)

During development, keep these documents close. They'll help you:
- 📖 Stay aligned with the original vision
- 🎯 Make consistent decisions
- 👥 Onboard new team members quickly
- ✅ Review code against intent
- 🗺️ Plan next phases strategically
- 🐛 Troubleshoot bugs (often intent documents reveal root causes)

### Next Steps
1. **Phase 1 (Now):** Setup development environment (from main README.md)
2. **Phase 2:** Write API specification (reference feature.md)
3. **Phase 3:** Build backend (reference feature.md for requirements, product-structure.md for folder layout)
4. **Phase 4:** Build frontend (reference feature.md for UI details, product-structure.md for components)
5. **Ongoing:** Reference intent documents in every PR, every code review, every decision

Happy building! 🚀

---

**Document Metadata**
- **Type:** Intent Folder Guide
- **Version:** 1.0
- **Created:** March 19, 2026
- **Author:** Hari (Product Owner)
- **Last Updated:** March 19, 2026
- **Status:** Active (Referenced during all development phases)


# Senus Board Intelligence

AI-native financial intelligence platform for analysing the historical performance of Senus PLC.

The application extracts financial information from source documents, validates and stores it, calculates Board-level KPIs deterministically, and uses AI to generate financial commentary and answer questions about the business.

## Assumptions

- FY2024 and FY2025 are treated as comparable full financial years.
- The 8 December 2025 balance sheet is treated as a point-in-time snapshot,
  not as a financial period.
- Financial calculations use only metrics that have passed validation.
- Missing metrics are returned as unavailable rather than estimated.
- The application is scoped to Senus PLC 
- EUR is the reporting currency for financial metrics.

## Features

- Board-level financial dashboard
- Historical financial statements
- PDF document ingestion
- Automated financial metric extraction
- Validation and reconciliation
- Deterministic KPI calculations
- Latest balance-sheet snapshot
- AI-generated Board insights
- Financial Q&A grounded in validated data

## Architecture

```text
                    React / TypeScript
                           |
                           v
                        FastAPI
                           |
             +-------------+-------------+
             |                           |
        Documents API                Financial APIs
             |                           |
           MinerU                         |
             |                           |
    Deterministic Extraction             |
             |                           |
    Extraction Candidates                |
             |                           |
        Validation ----------------------+
             |
             v
       ReportedMetric
             |
             v
      SQLAlchemy / SQLite
             |
             v
    Financial Calculations
             |
        +----+----+
        |         |
        v         v
    Dashboard   AI Context
                  |
                  v
              Qwen3:8B
```


## Financial Data Pipeline

```text
PDF
 ↓
MinerU
 ↓
Structured document content
 ↓
Deterministic extraction
 ↓
Extraction candidates
 ↓
Validation and reconciliation
 ↓
ReportedMetric database records
 ↓
Financial calculations
 ↓
Dashboard + AI analysis
```

Extracted values are not automatically treated as trusted financial data.

Candidates are validated using accounting relationships, required metric checks, cross-statement comparisons and source-priority rules before being promoted into the financial model.

## AI Design

The LLM is deliberately not used for financial calculations.

Financial calculations are implemented deterministically in Python, including:

- Revenue growth
- Gross margin
- Operating margin
- EBITDA
- EBITDA margin
- Free cash flow
- Working capital
- Current ratio
- Cash ratio
- Revenue per employee

Qwen3:8B receives structured context containing validated reported metrics and calculated KPIs.

Its role is limited to:

- Board commentary
- Financial interpretation
- Trend analysis
- Risk identification
- Financial Q&A

If requested information is unavailable, the model is instructed not to invent it.

## Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- React Router
- Recharts

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Pydantic Settings

### AI & Document Processing

- Qwen3:8B
- Ollama
- MinerU

### Database

- SQLite

The database connection is configured through `DATABASE_URL`, allowing another SQL database such as PostgreSQL to be introduced without changing the financial business logic.

### Testing

- pytest

## Data Model

Core entities:

- `Company`
- `Document`
- `ReportingPeriod`
- `ExtractionCandidate`
- `ReportedMetric`

The distinction between `ExtractionCandidate` and `ReportedMetric` creates a boundary between raw extraction and validated financial data.

Reported metrics retain source-document and source-page information for traceability.

## Application

### Board Report

Provides an executive financial overview including:

- Revenue
- Gross Margin
- EBITDA
- Operating Cash Flow
- Cash
- Current Ratio
- Revenue and margin trends
- Liquidity
- Cash burn
- Latest balance sheet
- AI financial snapshot

### Financials

Displays historical reported financial metrics and backend-calculated KPIs.

FY2024 and FY2025 are treated as full financial years, while the December 2025 balance sheet is treated separately as a point-in-time snapshot.

### Documents

Provides the ingestion workflow:


Upload PDF
→ MinerU
→ Extraction
→ Validation
→ Financial Database


Validated extraction results are automatically promoted into the financial model.

### AI Analysis

Interactive financial intelligence assistant grounded in the same validated dataset used by the dashboard.

Example questions:


How has revenue changed?

What are the biggest financial risks?

How is liquidity?

Compare FY2024 and FY2025.

What is our latest cash position?


## Project Structure


senus-board-intelligence/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │       ├── ai/
│   │       ├── extraction/
│   │       └── financials/
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   └── .env.example
│
└── README.md


## Local Setup

### Backend

```powershell
cd backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
Copy-Item .env.example .env

uvicorn app.main:app --reload
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```powershell
cd frontend

npm install
Copy-Item .env.example .env

npm run dev
```

Frontend:

```text
http://localhost:5173
```

### Backend Environment

```env
DATABASE_URL=sqlite:///./senus.db

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

MINERU_API_URL=http://127.0.0.1:8001

UPLOAD_DIR=uploads

CORS_ORIGINS=http://localhost:5173
```

### Frontend Environment

```env
VITE_API_URL=http://127.0.0.1:8000
```


## Prerequisites

- Python 3.12+
- Node.js 20+
- Ollama installed
- Qwen3:8B downloaded (`ollama pull qwen3:8b`)
- MinerU installed and available via `mineru-api`


# Running the application

Start each component in a separate terminal.

### Terminal 1 — MinerU

mineru-api --host 127.0.0.1 --port 8001

### Terminal 2 — Backend

cd backend
uvicorn app.main:app --reload

### Terminal 3 — Frontend

cd frontend
npm run dev

### Terminal 4 — Ollama

ollama serve


## Tests

Install development dependencies:

```powershell
cd backend
pip install -r requirements-dev.txt
```

Run the test suite:

```powershell
python -m pytest -v
```

Tests cover:

- Revenue growth
- Gross margin
- Operating margin
- EBITDA
- EBITDA margin
- Free cash flow
- Working capital
- Current ratio
- Cash ratio
- Revenue per employee
- Missing-value behaviour
- Required metric validation
- Source-priority selection
- Cross-statement conflicts
- Financial reconciliation
- Balance-sheet snapshot validation

Tests use known Senus financial values rather than arbitrary example data.

## Key Engineering Decisions

### Deterministic Finance

Financial calculations are implemented in Python rather than delegated to an LLM.

This keeps Board-level metrics deterministic, testable and reproducible.

### Validation Before Trust

An extracted value does not immediately become a financial fact.

```text
ExtractionCandidate
        ↓
Validation
        ↓
ReportedMetric
```

This provides an explicit trust boundary between document extraction and the data used by the Board Report.

### Grounded AI

The LLM operates after extraction, validation and calculation.

The database and financial calculation layer remain the source of truth, while the LLM is used only for interpretation and commentary.

### Reporting Period Separation

The December 2025 information is a point-in-time balance-sheet snapshot.

It is not treated as another financial year because it does not contain comparable full-year revenue, profitability or cash-flow information.

### Modular Monolith

The system uses a modular monolith rather than unnecessary microservices.

API, extraction, financial and AI responsibilities remain separated while the application stays straightforward to run and maintain.

## Validation Approach

Financial outputs are checked using:

1. Accounting reconciliation rules
2. Cross-statement comparisons
3. Required metric checks
4. Source-priority rules
5. Automated financial calculation tests
6. Automated validator tests
7. Manual comparison against source financial statements

The database and deterministic financial calculation layer remain the application's financial source of truth.

## AI-Assisted Development

AI tools were used during development for:

- Architecture discussion
- Code generation
- Debugging
- Prompt design
- Test generation
- Frontend iteration

Generated code and financial outputs were reviewed against application behaviour and source financial information rather than accepted automatically.

## Production Considerations

The current application is designed for local demonstration.

A production version could introduce:

- PostgreSQL
- Alembic migrations
- Object storage
- Durable background workers
- Hosted AI inference
- Authentication and authorization
- Structured logging and monitoring
- CI/CD

The existing service boundaries allow these changes without rewriting the core financial logic.
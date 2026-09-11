# Intelligent Document Extraction, Validation & API Platform

This implementation is aligned with the supplied internship case study.

## What it supports

- PDF / JPG / PNG upload
- PDF page-limit validation (3 pages)
- empty/corrupted/unsupported-file handling
- native PDF text extraction
- OCR fallback for scanned/image PDFs and images using Tesseract
- four supplied document categories:
  - invoice
  - balance_sheet
  - profit_and_loss
  - cash_flow_statement
- structured JSON
- source evidence text and page number where extraction finds a value
- financial validation with PASS / FAIL / NOT_APPLICABLE
- SQLite persistence
- dashboard
- raw JSON view
- REST APIs
- Swagger at `/docs`
- automated tests

## Important accuracy note

The case study requires complete extraction of all meaningful visible fields and explicitly says not to invent missing values. This repository therefore treats OCR/rule-based extraction conservatively: fields not found are `null` and validation becomes `NOT_APPLICABLE` when required source values are absent.

For the strongest submission, connect an approved document/LLM service as an additional extraction layer and preserve the same JSON contract. Do not hardcode expected answers.

## Project structure

```text
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/documents.py
│   │   ├── core/config.py
│   │   ├── core/database.py
│   │   ├── core/logging.py
│   │   ├── models/document.py
│   │   ├── schemas/document.py
│   │   ├── schemas/extraction.py
│   │   └── services/
│   │       ├── document_validation_service.py
│   │       ├── ocr_service.py
│   │       ├── extraction_service.py
│   │       ├── financial_validation_service.py
│   │       └── document_service.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── templates/
│   └── static/
├── sample_outputs/
├── docs/
├── .env.example
└── README.md
```

## Windows setup

### 1. Install Tesseract OCR

Install Tesseract for Windows and make sure `tesseract.exe` is on PATH.

If it is not on PATH, set the Tesseract command before starting Python, or add it to Windows PATH.

### 2. Create environment

```powershell
cd backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start

```powershell
uvicorn app.main:app --reload
```

Open:

- Dashboard: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/v1/health`

## Linux / Render setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

For a Render deployment, a native Tesseract package must also be installed in the build environment. A Docker deployment is recommended for reliable OCR dependencies.

## API

### Health

```http
GET /api/v1/health
```

### Process

```http
POST /api/v1/documents/process
Content-Type: multipart/form-data

file=<document.pdf>
document_type=invoice
```

Allowed document types:

```text
invoice
balance_sheet
profit_and_loss
cash_flow_statement
```

### List

```http
GET /api/v1/documents
```

### Latest result by name

```http
GET /api/v1/documents/{document_name}
```

## Validation behavior

A financial check returns:

- `PASS` when calculated and reported values reconcile within tolerance
- `FAIL` when they do not
- `NOT_APPLICABLE` when required source fields are missing

Parenthesized numbers such as `(1,250.00)` are interpreted as negative.

## Supplied dataset

The supplied dataset contains invoice images and annual Balance Sheet, Profit & Loss and Cash Flow PDFs. The statement PDFs are image/scanned-style documents, so OCR fallback is important.

## Testing

```bash
cd backend
pytest -q
```

## Deployment

The case study requires a live frontend, live backend, Swagger URL and public GitHub repository.

Recommended submission flow:

1. Push this repository to GitHub.
2. Deploy the backend to Render/Railway/Koyeb or another suitable platform.
3. Ensure Tesseract is installed in the runtime image.
4. Configure persistent storage/database. SQLite is acceptable for a prototype but persistent disk or PostgreSQL is preferable for hosted evaluation.
5. Submit:
   - frontend URL
   - backend URL
   - `/docs`
   - GitHub URL

## Security

- no API keys are committed
- uploads are validated
- file names are reduced to their basename
- server errors do not expose stack traces
- `.env` is ignored

## AI usage declaration

This project may be developed with permitted AI coding assistants. The candidate should state exactly where an assistant was used and must be able to explain, debug and modify the submitted code during the interview.

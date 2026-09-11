# Architecture

             ┌─────────────────────────┐
             │ HTML/CSS/JavaScript UI  │
             │ Upload + Dashboard      │
             └────────────┬────────────┘
                          │ HTTP
                          ▼
             ┌─────────────────────────┐
             │ FastAPI REST API        │
             │ validation + errors     │
             └────────────┬────────────┘
                          ▼
             ┌─────────────────────────┐
             │ Document Validation     │
             │ type / size / pages     │
             └────────────┬────────────┘
                          ▼
             ┌─────────────────────────┐
             │ Text Extraction / OCR   │
             │ PyMuPDF + Tesseract     │
             └────────────┬────────────┘
                          ▼
             ┌─────────────────────────┐
             │ Field & Table Extraction│
             │ structured JSON         │
             └────────────┬────────────┘
                          ▼
             ┌─────────────────────────┐
             │ Financial Validation    │
             │ PASS / FAIL / N/A       │
             └────────────┬────────────┘
                          ▼
             ┌─────────────────────────┐
             │ SQLite / Persistent DB  │
             └────────────┬────────────┘
                          ▼
             ┌─────────────────────────┐
             │ Dashboard + GET API     │
             └─────────────────────────┘

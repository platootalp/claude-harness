---
name: document-handling
description: Handle office document files — Word (.docx), PDF (.pdf), PowerPoint (.pptx), and Excel (.xlsx). Routes to the appropriate format handler based on file type. Use when creating, reading, editing, or converting office documents.
---

# Document Handling

Routes to the appropriate format handler based on file type.

## Decision Matrix

| File Type | Route To | Capabilities |
|-----------|----------|-------------|
| `.docx` | `docx` | Create (docx-js), edit (XML), convert to PDF |
| `.pdf` | `pdf` | Read, merge, split, rotate, watermark, create, OCR, form fill, encrypt |
| `.pptx` | `pptx` | Create (pptxgenjs), edit, read, design principles |
| `.xlsx` | `xlsx` | Create (openpyxl), edit, formulas, formatting, financial models |

## How to Use

1. Identify the file format from context (file extension or user request)
2. Invoke the appropriate sub-skill directly
3. This orchestrator only routes; it does not duplicate sub-skill content

## Sub-skills

- **docx** — Word documents: create with docx-js (npm), edit via XML unpack/repack, tracked changes, comments
- **pdf** — PDF operations: pypdf (merge/split), pdfplumber (extract), reportlab (create), pytesseract (OCR)
- **pptx** — PowerPoint: create with pptxgenjs, edit templates, design principles (color palettes, visual motifs)
- **xlsx** — Spreadsheets: pandas (data), openpyxl (formulas/formatting), financial model color coding
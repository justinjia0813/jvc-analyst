---
name: invoice-manager
description: OCR PDF invoices, generate reimbursement summary Excel, and archive travel invoices. In vc-analyst, this is an operations helper and is outside the investment decision workflow.
source_repo: https://github.com/justinjia0813/invoice-manager
---

# Invoice Manager

`invoice-manager` is an external skill collected into `vc-analyst` for VC operations work after travel or month-end reimbursement.

## Canonical Source

- Repository: <https://github.com/justinjia0813/invoice-manager>
- Role: PDF invoice OCR -> reviewed invoice JSON -> reimbursement summary Excel + archived PDFs
- System dependencies: `poppler`, `tesseract`, `tesseract-lang`
- Python dependencies: `openpyxl`, `pdf2image`, `pytesseract`

## vc-analyst Integration

Use this skill only for operational expense organization.

Standard chain:

1. Put invoice PDFs into the upstream skill's `input/` folder.
2. Run OCR to produce an intermediate invoice JSON file.
3. Review date, amount, location, expense type, seller, and project name.
4. Generate the monthly reimbursement summary and archive PDFs.
5. Use the same `projects/{company-slug}` slug when a trip maps to a tracked investment project.

## Boundary

This skill is not part of the investment decision flow.

It can help maintain clean travel and project-operation records, but invoice data should not be used as diligence evidence unless the user explicitly provides it as project source material and it is copied into the project's `00-source/` archive.

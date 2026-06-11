# Skill Registry

This registry lists external skills collected into the `vc-analyst` toolkit.

The source repositories remain the canonical implementation. This repository keeps only workflow-level integration notes so the VC toolkit can route work without copying code that may drift.

| Skill | Canonical source | Local entry | Toolkit role | Invocation points |
| --- | --- | --- | --- | --- |
| `meeting-notes` | <https://github.com/justinjia0813/meeting-notes> | `skills/meeting-notes/SKILL.md` | Turn transcript text plus user notes into a structured `.docx` interview memo. | `/intake`, `/founder-sync`, `/ref-check` |
| `invoice-manager` | <https://github.com/justinjia0813/invoice-manager> | `skills/invoice-manager/SKILL.md` | OCR travel invoices, generate reimbursement summary Excel, and archive PDFs by trip/project. | Operations helper, outside investment decision flow |

## Integration Rules

- Keep source materials local. Do not upload pitch decks, transcripts, financial files, or founder communication records to third-party web tools.
- Treat `meeting-notes` output as fact-layer material. Any interpretation, uncertainty, evasive answer, or diligence gap belongs in the corresponding project Markdown file.
- Treat `invoice-manager` as operational infrastructure. It may reference a project slug for archive naming, but it should not affect investment judgment.
- If the external skill implementation changes, update the registry entry and `WORKFLOW.md` link instead of pasting the upstream code into this repository.

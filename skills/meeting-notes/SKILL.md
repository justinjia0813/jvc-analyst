---
name: meeting-notes
description: Generate structured Word interview notes from transcript text and user notes. In vc-analyst, use this as the fact-layer intake for founder meetings, customer calls, and reference checks.
source_repo: https://github.com/justinjia0813/meeting-notes
---

# Meeting Notes

`meeting-notes` is an external skill collected into `vc-analyst` as a reusable fact-layer generator.

## Canonical Source

- Repository: <https://github.com/justinjia0813/meeting-notes>
- Role: AI transcript + user notes -> structured interview memo `.docx`
- Dependency: `python-docx`
- Output naming: `{YYYYMMDD}_{project}_访谈纪要.docx`

## vc-analyst Integration

Use this skill when an investment workflow starts from a meeting transcript, founder call, customer interview, or reference-check conversation.

Standard chain:

1. Use `/asr` to turn audio or video into transcript text when needed.
2. Use `meeting-notes` to generate the structured `.docx` memo.
3. Store the `.docx` under `projects/{company-slug}/00-source/`.
4. Extract only the relevant facts into the active Markdown file:
   - `/intake` -> project fact card
   - `/founder-sync` -> `03-founder-sync.md`
   - `/ref-check` -> `05-ref-check.md`

## Boundary

The `.docx` output is a fact layer. Do not use it to silently add investment conclusions.

Interpretation belongs in the project archive and must preserve the source label:

- `[创始人自述]` for unverified founder claims
- `[客户访谈]` for customer statements
- `[待交叉验证]` for single-source claims
- `[推测]` for analyst inference

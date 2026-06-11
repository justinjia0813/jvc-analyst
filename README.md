# vc-analyst

`vc-analyst` is a local-first toolkit for early-stage VC diligence workflows in China-market RMB funds.

The toolkit does not make investment decisions. It structures evidence, exposes gaps, prepares questions, and keeps project archives recoverable across conversations.

## Current Scope

- Project archive conventions for Pre-seed to Series B diligence
- Markdown-first workflow stages: intake, prescreen, modular DD, founder sync, bear case, ref check, IC memo, decision archive, retro
- External skill registry for adjacent high-frequency work

## Included Skills

| Skill | Source repo | Role in this toolkit |
| --- | --- | --- |
| `meeting-notes` | <https://github.com/justinjia0813/meeting-notes> | Converts interview transcripts and user notes into structured Word meeting notes for `/intake`, `/founder-sync`, and `/ref-check`. |
| `invoice-manager` | <https://github.com/justinjia0813/invoice-manager> | Handles travel invoice OCR, reimbursement summary generation, and trip archive organization as an operations helper. |

See [`library/skill-registry.md`](library/skill-registry.md) and [`skills/`](skills/) for the local registry entries.

## Repository Layout

```text
.
├── CLAUDE.md
├── WORKFLOW.md
├── library/
│   └── skill-registry.md
└── skills/
    ├── invoice-manager/
    │   └── SKILL.md
    └── meeting-notes/
        └── SKILL.md
```

Future project archives should follow the structure defined in [`WORKFLOW.md`](WORKFLOW.md). Confidential deal materials belong under local `projects/{company-slug}/00-source/` and should not be uploaded to third-party tools.

---
name: jvc-research-core
description: Shared non-user-invocable evidence-ledger and audit runtime for installed jvc research skills. Use only when another jvc skill explicitly routes to this sibling component; never route a user request here directly.
user_invocable: false
version: "2.0.0"
---

# JVC Research Core

Maintain one append-only evidence ledger and audit final artifacts for the calling jvc skill.

## Required execution

1. Resolve this sibling from the calling `SKILL.md` path; do not depend on the current working directory.
2. Initialize a new ledger with `researchctl.py init`, or validate an existing ledger with `init --resume`.
3. Add every scope, question, query, source, claim, correction, and waiver through `researchctl.py`; never edit `evidence_registry.jsonl` directly.
4. Run `researchctl.py audit --skill <calling-skill> --artifact <path>` after the final artifact is stable. The default `--mode deliver` fits routine work; pass `--mode gate` only for `/jvc-ic-memo`, L3 work, or when the user asks for `--rigor`.
5. Read both the command exit status and `audit.json` before reporting completion.

## Completion

`deliver` mode (default): evidence gaps never stop delivery.

- exit `0`: deliver the full artifact, judgments included. `status` is only the evidence-maturity label (`ready` / `partial` / `blocked`); the artifact may state it in one closing line `证据成熟度：<status>`, and must never claim a higher level.
- exit `20`: an integrity problem (missing or unreadable artifact, broken ledger, dangling source reference, overclaimed maturity). Fix it and rerun.

`gate` mode (IC memo, L3, `--rigor`):

- `ready` / exit `0`: the calling skill may claim completion.
- `partial` / exit `10`: deliver only with an explicit incomplete-research label and narrowed conclusions.
- `blocked` / exit `20`: deliver evidence gaps and next actions; do not form the affected judgment.

Either mode: exit `1` means repair the tool, profile, ledger, or artifact and rerun.

## Boundaries

- Do not search the web, choose sources, make investment judgments, or rewrite artifacts.
- Do not fall back to prompt-only completion when this runtime is missing or fails.
- Read `references/evidence-contract.md` for record fields, independence, conflict, waiver, and audit rules.

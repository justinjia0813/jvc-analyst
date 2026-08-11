---
name: jvc-research-core
description: Shared non-user-invocable evidence-ledger and audit runtime for installed jvc research skills. Use only when another jvc skill explicitly routes to this sibling component; never route a user request here directly.
user_invocable: false
version: "2.0.0"
---

# JVC Research Core

本组件是不可直接调用的证据引擎。它只负责证据台账、主张继承、产物审计：为调用方维护追加式记录并执行确定性检查；不搜索、不编排原子 Skill，也不推进业务阶段。

它的三种审查状态仍为 ready、partial、blocked：分别表示通过审查、收窄后不完整交付、停止受影响判断。这些状态描述证据和产物质量，不代表用户批准研究级别升级、进入尽调、提交 IC（Investment Committee，投资决策委员会，负责审议投资项目）或生成干净终版。

## Required execution

1. Resolve this sibling from the calling `SKILL.md` path; do not depend on the current working directory.
2. Initialize a new ledger with `researchctl.py init`, or validate an existing ledger with `init --resume`.
3. Add every scope, question, query, source, claim, correction, and waiver through `researchctl.py`; never edit `evidence_registry.jsonl` directly.
4. Run `researchctl.py audit --skill <calling-skill> --artifact <path>` after the final artifact is stable.
5. Read both the command exit status and `audit.json` before reporting completion.

## Completion

- `ready` / exit `0`: the calling skill may claim completion.
- `partial` / exit `10`: deliver only with an explicit incomplete-research label and narrowed conclusions.
- `blocked` / exit `20`: deliver evidence gaps and next actions; do not form the affected judgment.
- exit `1`: repair the tool, profile, ledger, or artifact and rerun.

## Boundaries

- Do not search the web, choose sources, make investment judgments, or rewrite artifacts.
- Do not create workflow events, choose the next business stage, or interpret `ready` as approval to advance.
- Do not fall back to prompt-only completion when this runtime is missing or fails.
- Read `references/evidence-contract.md` for record fields, independence, conflict, waiver, and audit rules.

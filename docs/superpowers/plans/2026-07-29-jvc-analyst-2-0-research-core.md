# jvc-analyst 2.0 Research Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the Venture Capital（VC，风险投资，指围绕创业公司融资与投资判断开展的专业投资活动）skill suite to 2.0 by adding a shared, non-user-invocable evidence ledger and deterministic completion gate while preserving every existing `/jvc-*` entrypoint.

**Architecture:** A hidden sibling skill, `jvc-research-core`, owns one append-only JavaScript Object Notation Lines（JSONL，逐行 JavaScript 对象表示法数据格式，每行保存一条可独立校验的记录）ledger and one standard-library command. Business skills keep their domain prompts and artifact generators, declare compact profiles, and must initialize or resume the ledger, register evidence through the command, and audit final artifacts before claiming completion. The core does not search the web, make investment judgments, or replace existing workbook and document validators.

**Tech Stack:** Python 3 standard library (`argparse`, `hashlib`, `json`, `os`, `pathlib`, `tempfile`, `zipfile`, `xml.etree.ElementTree`; Extensible Markup Language（XML，可扩展标记语言，用于描述结构化文档内容）), Bash, existing repository checks, Yao Meta Skill library gates, Test-Driven Development（TDD，测试驱动开发，先用失败检查锁定行为再写最小实现）.

---

## Locked decisions

- Keep all twelve current user-invocable skill names and slash commands.
- Add `jvc-research-core` as a hidden sibling support skill; do not add a user slash command.
- Use one canonical `evidence_registry.jsonl` per research chain.
- Use platform-provided search, browser, and local-file tools; ship no network-capable research script.
- Preserve only a minimal evidence package for normal web pages: metadata, relevant excerpt, access time, source class, scope, stance, and content fingerprint.
- Store `scope`, `question`, `query`, `source`, `claim`, and `waiver` records.
- Write the ledger only through `researchctl.py`; direct edits invalidate the append chain.
- Return `ready` with exit `0`, `partial` with exit `10`, `blocked` with exit `20`, and tool/data errors with exit `1`.
- A waiver can downgrade one business-evidence blocker to `partial`; it cannot produce `ready` or waive integrity/security rules.
- Integrate eleven investment-research skills; keep `jvc-invoice-manager` outside the evidence runtime.
- Do not modify `.worktrees/jvc-research-report`.
- Do not stage `.superpowers/` or `assets/xiaohongshu/jvc-track-research/`.

## Execution boundary

The current workspace intentionally contains frontmatter-only edits in all twelve `skills/jvc-*/SKILL.md` files. This implementation overlaps those files, so execute in the current workspace instead of starting from a clean worktree that would silently omit the user changes.

Before every commit:

```bash
git diff --cached --name-only
git diff --cached --check
```

Only the files named by the current task may be staged. Never use `git add .`.

## File map

### Create

- `skills/jvc-research-core/SKILL.md` — hidden execution entry and stop rules.
- `skills/jvc-research-core/agents/interface.yaml` — portable hidden-component metadata.
- `skills/jvc-research-core/manifest.json` — library lifecycle, permissions, output, and rollback contract.
- `skills/jvc-research-core/references/evidence-contract.md` — deferred record and audit contract.
- `skills/jvc-research-core/reports/output-risk-profile.md` — likely ledger/audit failure modes.
- `skills/jvc-research-core/scripts/researchctl.py` — append-only ledger and audit command.
- `skills/jvc-research-core/scripts/check_package.py` — one runnable standard-library self-check.
- `skills/jvc-research-core/profiles/jvc-bear-case.json`
- `skills/jvc-research-core/profiles/jvc-bull-case.json`
- `skills/jvc-research-core/profiles/jvc-comps-dd.json`
- `skills/jvc-research-core/profiles/jvc-ic-memo.json`
- `skills/jvc-research-core/profiles/jvc-knowledge-tree-builder.json`
- `skills/jvc-research-core/profiles/jvc-market-sizing.json`
- `skills/jvc-research-core/profiles/jvc-meeting-notes.json`
- `skills/jvc-research-core/profiles/jvc-prescreen.json`
- `skills/jvc-research-core/profiles/jvc-roi-modeler.json`
- `skills/jvc-research-core/profiles/jvc-talk-notes.json`
- `skills/jvc-research-core/profiles/jvc-track-research.json`
- `scripts/check-research-core-install.py` — temporary-directory setup simulation.
- `scripts/render-output-review-kit.py` — offline, blind-safe Markdown and workbook renderer for human review.
- `evals/research-core/cases.json` — five real acceptance-case contracts.
- `evals/research-core/output_cases.jsonl` — populated baseline and 2.0 output comparisons.
- `reports/research-core-2.0-release.md` — release evidence and honest remaining gaps.
- `reports/jvc_skill_case_quality_2026-07-29.md` — fresh 2.0 suite-wide quality evidence.
- `reports/research-core-output-eval.json`
- `reports/research-core-output-eval.md`
- `reports/output_blind_review_pack.json`
- `reports/output_blind_review_pack.md`
- `reports/output_blind_answer_key.json`
- `reports/output_review_decisions.json`
- `reports/output_review_kit.json`
- `reports/output_review_kit.md`
- `reports/output_review_kit.html`

### Modify

- `skills/jvc-bear-case/SKILL.md`
- `skills/jvc-bull-case/SKILL.md`
- `skills/jvc-comps-dd/SKILL.md`
- `skills/jvc-ic-memo/SKILL.md`
- `skills/jvc-invoice-manager/SKILL.md`
- `skills/jvc-knowledge-tree-builder/SKILL.md`
- `skills/jvc-market-sizing/SKILL.md`
- `skills/jvc-meeting-notes/SKILL.md`
- `skills/jvc-prescreen/SKILL.md`
- `skills/jvc-roi-modeler/SKILL.md`
- `skills/jvc-talk-notes/SKILL.md`
- `skills/jvc-track-research/SKILL.md`
- `setup`
- `README.md`
- `CLAUDE.md`
- `manifest.json`
- `agents/interface.yaml`
- `library/skill-registry.md`
- `scripts/check-skill-evals.py`
- `scripts/check-governance.py`
- `scripts/check-review-fixes.sh`
- `evals/output/cases.json`
- `reports/skill-ir.json`
- `reports/output_quality_scorecard.md`
- `reports/route_scorecard.md`
- `reports/review-studio.json`
- `reports/review-studio.md`
- `reports/trust_report.json`
- `reports/trust_report.md`
- `security/network_policy.json`
- `security/permission_policy.json`
- `docs/superpowers/specs/2026-07-29-jvc-analyst-2-0-research-core-design.md`

### Task 0: Confirm the live baseline and preserve user work

**Files:** Read only.

- [ ] **Step 1: Confirm the expected dirty boundary**

Run:

```bash
git status --short
git diff --numstat -- skills
```

Expected:

- twelve modified `skills/jvc-*/SKILL.md` files;
- `3/1` line counts for the simple frontmatter edits, `5/3` for `jvc-knowledge-tree-builder`, and `5/1` for `jvc-talk-notes` and `jvc-track-research`;
- untracked `.superpowers/` and `assets/xiaohongshu/jvc-track-research/`;
- no staged files.

If the skill diff has grown beyond that known frontmatter boundary, stop and re-read the overlapping files before implementation.

- [ ] **Step 2: Record the deterministic baseline**

Run:

```bash
python3 scripts/check-skill-evals.py
python3 scripts/check-governance.py
```

Expected:

- skill eval passes with `13 trigger cases, 12 output cases`;
- governance fails only with a trust-report hash mismatch because the frontmatter edits are not yet reflected in the package fingerprint.

- [ ] **Step 3: Confirm the independent report worktree is untouched**

Run:

```bash
git -C .worktrees/jvc-research-report status --short
```

Expected: report the worktree's current state for comparison only. Do not edit, stage, clean, or commit anything there.

### Task 1: Create the hidden library boundary

**Files:**

- Create: `skills/jvc-research-core/SKILL.md`
- Create: `skills/jvc-research-core/agents/interface.yaml`
- Create: `skills/jvc-research-core/manifest.json`
- Create: `skills/jvc-research-core/references/evidence-contract.md`
- Create: `skills/jvc-research-core/reports/output-risk-profile.md`

- [ ] **Step 1: Prove the package does not exist**

Run:

```bash
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/validate_skill.py skills/jvc-research-core
```

Expected: non-zero exit with a missing skill-directory or missing `SKILL.md` error.

- [ ] **Step 2: Create the lean hidden `SKILL.md`**

Create exactly this behavior:

```markdown
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
4. Run `researchctl.py audit --skill <calling-skill> --artifact <path>` after the final artifact is stable.
5. Read both the command exit status and `audit.json` before reporting completion.

## Completion

- `ready` / exit `0`: the calling skill may claim completion.
- `partial` / exit `10`: deliver only with an explicit incomplete-research label and narrowed conclusions.
- `blocked` / exit `20`: deliver evidence gaps and next actions; do not form the affected judgment.
- exit `1`: repair the tool, profile, ledger, or artifact and rerun.

## Boundaries

- Do not search the web, choose sources, make investment judgments, or rewrite artifacts.
- Do not fall back to prompt-only completion when this runtime is missing or fails.
- Read `references/evidence-contract.md` for record fields, independence, conflict, waiver, and audit rules.
```

- [ ] **Step 3: Create library metadata**

Create `manifest.json`:

```json
{
  "name": "jvc-research-core",
  "version": "2.0.0",
  "owner": "jvc-analyst",
  "updated_at": "2026-07-29",
  "status": "active",
  "maturity_tier": "library",
  "lifecycle_stage": "library",
  "context_budget_tier": "production",
  "review_cadence": "quarterly",
  "target_platforms": ["codex", "claude", "generic", "agent-skills-compatible"],
  "factory_components": ["agents", "references", "profiles", "scripts", "reports"],
  "input_files": "file-backed fixture: scope JSON, evidence JSONL, skill profile, and local final artifacts",
  "output_contract": ["evidence_registry.jsonl", "audit.json", "audit.md", "ready/partial/blocked exit status"],
  "rollback_boundary": "Revert the core and profile commit; research inputs and pre-existing artifacts stay outside the package boundary."
}
```

Create `agents/interface.yaml`:

```yaml
interface:
  display_name: "JVC Research Core"
  short_description: "Hidden evidence-ledger and audit runtime for jvc research skills"
  default_prompt: "Use only when an installed jvc skill explicitly routes to this sibling runtime."
compatibility:
  canonical_format: "agent-skills"
  adapter_targets:
    - "codex"
    - "claude"
    - "generic"
  activation:
    mode: "support-only"
    paths:
      - "skills/jvc-research-core/SKILL.md"
  execution:
    context: "local"
    shell: "bash"
  trust:
    source_tier: "local"
    remote_inline_execution: "forbid"
    remote_metadata_policy: "allow-metadata-only"
```

- [ ] **Step 4: Create the deferred evidence contract**

`references/evidence-contract.md` must contain these exact sections and rules:

```markdown
# Evidence Contract

## Canonical files

- `evidence_registry.jsonl` is the only evidence source of truth.
- `audit.json` and `audit.md` are reproducible derivatives.
- Business reports, workbooks, and interview notes remain owned by the calling skill.

## Record types

- `scope`: originating skill, subject, decision, inclusions, exclusions, geography, time range, and user assumptions.
- `question`: question text, priority, hypothesis, falsifier, evidence requirement, and state.
- `query`: linked question, direction, exact query, tool class, target source class, execution time, search round, whether the round changed the core judgment, result count, outcome, and result summary or no-result reason.
- `source`: title, publisher, author, publication/access dates, source class, link or local path, excerpt, definition, geography, sample, statistical scope, stance, independence key, and content fingerprint.
- `claim`: linked question, claim text, claim kind, topic, importance, support sources, counter sources, upstream claim identifiers, scope, confidence, reasoning, conflict resolution, and state.
- `waiver`: rule, reason, scope, approver, approval time, and residual risk.

## Shared fields and append chain

Every input record has `schema_version`, `record_id`, `record_type`, `created_at`, `actor`, `created_by_skill`, and optional `supersedes`.
The core adds `sequence`, `previous_fingerprint`, and `record_fingerprint`.
Corrections append a same-type record whose `supersedes` points to the effective prior record.
`init`, `record`, and audit-index writes hold the same exclusive single-writer lock; a present lock fails closed and must not be removed until the recorded process is confirmed absent.

## Evidence rules

- Search must answer a registered question.
- No-result searches are evidence of search effort, not evidence of non-existence.
- High-priority questions must end as supported, refuted, or an explicit evidence gap.
- Profiles that require counter-search also require two latest distinct search rounds that no longer change the core judgment.
- Decision-critical third-party facts require distinct source classes, independence keys, publishers, locations, and evidence-packet fingerprints.
- Syndicated or same-origin reports count once.
- Company claims remain company claims until independently corroborated.
- Counterevidence must be preserved; unresolved material conflict blocks the affected claim.
- Cross-skill claims name their upstream claim identifiers; every referenced upstream skill must have a still-valid audit.
- Ordinary web pages store only claim-relevant excerpts and metadata.
- `content_fingerprint` is computed by the core over the canonical evidence packet; caller-supplied mismatches are rejected.

## Waivers

Only business-evidence rules are waivable.
Schema, chain, broken-reference, fingerprint, path, and command-integrity rules are never waivable.
A waiver must match one blocker in the latest still-valid audit for the same skill; generic `record` input cannot create waivers.
A valid waiver changes a matching blocker to `partial`, never `ready`.

## Audit validity

An audit binds the calling skill, ledger sequence, ledger-prefix fingerprint, artifact paths and fingerprints, profile fingerprint, core-runtime fingerprint, and upstream audit bindings.
Later valid appends do not invalidate prior audits.
Changing an audited prefix, artifact, profile, core runtime, or upstream audit invalidates the affected audit and its downstream dependents.
A preliminary `partial` requires `研究状态：partial` in the final artifact and one rerun; otherwise the audit is `blocked`.
```

- [ ] **Step 5: Create the output-risk profile**

Create `reports/output-risk-profile.md` with this table:

```markdown
# Output Risk Profile

| Risk | Required prevention | Release evidence |
| --- | --- | --- |
| Direct ledger edit | Fingerprint chain and core-only writes | Tamper self-check |
| Partial batch append | Validate full batch before atomic replace | Batch rollback self-check |
| Concurrent append loss | Exclusive single-writer lock | Lock-contention self-check |
| Same-origin triangulation | Distinct class, independence key, publisher, location, and packet fingerprint | Conflicting-source fixture |
| Company claim promoted to fact | Claim-kind audit rule | Blocked fixture |
| Counterevidence hidden | Counter-query and counter-source checks | Public research fixture |
| Premature search stop | Two stable search rounds per high-priority public-research question | Audit self-check |
| Stale completion claim | Ledger-prefix and artifact fingerprints | Stale-audit self-check |
| Stale runtime or profile | Core and profile fingerprints | Stale-audit self-check |
| Invalid upstream evidence | Claim lineage and recursive audit bindings | Cross-skill audit self-check |
| Waiver produces ready | Status floor at partial | Waiver self-check |
| Hidden runtime missing | No prompt-only fallback | Install simulation |
| Unsupported public claim | Real end-to-end run plus blind human review | Release report |
```

- [ ] **Step 6: Validate the boundary**

Run:

```bash
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/validate_skill.py skills/jvc-research-core
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/resource_boundary_check.py skills/jvc-research-core --max-initial-tokens 1000
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/governance_check.py skills/jvc-research-core --require-manifest
```

Expected:

- structure validation passes;
- initial load is at or below `1000` tokens;
- governance metadata is present; missing scripts/profiles may remain visible as work-in-progress evidence but must not be described as complete.

- [ ] **Step 7: Commit the boundary**

```bash
git add skills/jvc-research-core/SKILL.md \
  skills/jvc-research-core/agents/interface.yaml \
  skills/jvc-research-core/manifest.json \
  skills/jvc-research-core/references/evidence-contract.md \
  skills/jvc-research-core/reports/output-risk-profile.md
git commit -m "Add research core skill boundary"
```

### Task 2: Implement the append-only ledger with one failing check

**Files:**

- Create: `skills/jvc-research-core/scripts/check_package.py`
- Create: `skills/jvc-research-core/scripts/researchctl.py`

- [ ] **Step 1: Write the first failing self-check**

Start `check_package.py` with standard-library assertions for a valid scope, two-record batch, evidence-packet fingerprint validation, tamper detection, and atomic rollback:

```python
from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
from researchctl import LedgerError, append_records, init_registry, load_registry, resolve_record_id


def record(record_id: str, record_type: str, **fields: object) -> dict[str, object]:
    return {
        "schema_version": 1,
        "record_id": record_id,
        "record_type": record_type,
        "created_at": "2026-07-29T00:00:00Z",
        "actor": "test-agent",
        "created_by_skill": "jvc-track-research",
        **fields,
    }


def expect_error(action, message: str) -> None:
    try:
        action()
    except LedgerError as exc:
        assert message in str(exc), exc
    else:
        raise AssertionError(f"expected LedgerError containing {message!r}")


def check_ledger() -> None:
    with TemporaryDirectory() as temporary:
        run_dir = Path(temporary) / "run"
        scope = record(
            "SC1",
            "scope",
            subject="玻璃基板",
            decision="确定下一轮尽调重点",
            inclusions=["半导体先进封装"],
            exclusions=["显示面板盖板玻璃"],
            geography="全球及中国",
            time_range="2024-2029",
            user_assumptions=[],
        )
        init_registry(run_dir, "jvc-track-research", scope)
        append_records(
            run_dir,
            [
                record(
                    "Q1",
                    "question",
                    question_text="玻璃基板量产良率是否仍限制规模交付？",
                    priority="high",
                    hypothesis="量产良率是当前商业化瓶颈",
                    falsifier="公开量产数据证明良率不再影响交付",
                    evidence_needed=["量产良率", "客户验证"],
                    state="open",
                ),
                record(
                    "QU1",
                    "query",
                    question_id="Q1",
                    direction="counter",
                    query_text="glass substrate mass production yield",
                    tool_class="web-search",
                    target_source_class="company-filing",
                    executed_at="2026-07-29T00:01:00Z",
                    search_round=1,
                    changed_core_judgment=False,
                    result_count=0,
                    outcome="no-result",
                    result_summary="未找到满足目标来源类型的反向证据",
                ),
            ],
        )
        entries = load_registry(run_dir)
        assert [entry["sequence"] for entry in entries] == [1, 2, 3]
        append_records(
            run_dir,
            [
                record(
                    "Q2",
                    "question",
                    supersedes="Q1",
                    question_text="玻璃基板量产良率是否限制未来十二个月规模交付？",
                    priority="high",
                    hypothesis="量产良率是当前商业化瓶颈",
                    falsifier="未来十二个月量产数据证明良率不影响交付",
                    evidence_needed=["量产良率", "客户验证"],
                    state="open",
                )
            ],
        )
        entries = load_registry(run_dir)
        assert resolve_record_id(entries, "Q1") == "Q2"
        before = (run_dir / "evidence_registry.jsonl").read_bytes()
        bad_source = record(
            "S1",
            "source",
            title="错误指纹来源",
            publisher="测试机构",
            author="测试作者",
            published_at="2026-07-01",
            accessed_at="2026-07-29T00:01:00Z",
            source_class="technical-paper",
            location="https://example.invalid/source",
            excerpt="测试摘录",
            definition="测试定义",
            geography="全球",
            sample="测试样本",
            statistical_scope="测试统计口径",
            stance="neutral",
            independence_key="test-source",
            content_fingerprint="0" * 64,
        )
        expect_error(lambda: append_records(run_dir, [bad_source]), "content_fingerprint mismatch")
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        bad = record(
            "C1",
            "claim",
            question_id="MISSING",
            claim_text="测试断裂引用",
            claim_kind="unknown",
            topic="technical_maturity",
            importance="decision_critical",
            support_source_ids=[],
            counter_source_ids=[],
            derived_from_claim_ids=[],
            scope="先进封装玻璃基板",
            confidence="unknown",
            reasoning="仅用于验证引用完整性",
            conflict_resolution="none",
            state="unverified",
        )
        expect_error(lambda: append_records(run_dir, [bad]), "unknown reference")
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        lock = run_dir / ".evidence_registry.jsonl.lock"
        lock.write_text("test-writer", encoding="ascii")
        expect_error(lambda: append_records(run_dir, [bad]), "another registry writer")
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        lock.unlink()
        lines = before.decode("utf-8").splitlines()
        changed = json.loads(lines[0])
        changed["subject"] = "被篡改"
        lines[0] = json.dumps(changed, ensure_ascii=False, sort_keys=True)
        (run_dir / "evidence_registry.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        expect_error(lambda: load_registry(run_dir), "fingerprint")


if __name__ == "__main__":
    check_ledger()
    print("research core ledger checks passed")
```

- [ ] **Step 2: Run the check and verify the expected failure**

Run:

```bash
python3 skills/jvc-research-core/scripts/check_package.py
```

Expected: non-zero exit because `researchctl.py` does not exist.

- [ ] **Step 3: Implement record validation and the fingerprint chain**

Create `researchctl.py` with these public constants and functions:

```python
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

SCHEMA_VERSION = 1
REGISTRY_NAME = "evidence_registry.jsonl"
DERIVED_FIELDS = {"sequence", "previous_fingerprint", "record_fingerprint"}
BASE_FIELDS = {
    "schema_version",
    "record_id",
    "record_type",
    "created_at",
    "actor",
    "created_by_skill",
}
REQUIRED_FIELDS = {
    "scope": {"subject", "decision", "inclusions", "exclusions", "geography", "time_range", "user_assumptions"},
    "question": {"question_text", "priority", "hypothesis", "falsifier", "evidence_needed", "state"},
    "query": {"question_id", "direction", "query_text", "tool_class", "target_source_class", "executed_at", "search_round", "changed_core_judgment", "result_count", "outcome", "result_summary"},
    "source": {"title", "publisher", "author", "published_at", "accessed_at", "source_class", "location", "excerpt", "definition", "geography", "sample", "statistical_scope", "stance", "independence_key", "content_fingerprint"},
    "claim": {"question_id", "claim_text", "claim_kind", "topic", "importance", "support_source_ids", "counter_source_ids", "derived_from_claim_ids", "scope", "confidence", "reasoning", "conflict_resolution", "state"},
    "waiver": {"rule", "reason", "scope", "approved_by", "approved_at", "residual_risk"},
}
REFERENCE_FIELDS = {
    "question_id": "question",
    "support_source_ids": "source",
    "counter_source_ids": "source",
    "derived_from_claim_ids": "claim",
    "supersedes": None,
}
LIST_FIELDS = {
    "inclusions",
    "exclusions",
    "user_assumptions",
    "evidence_needed",
    "support_source_ids",
    "counter_source_ids",
    "derived_from_claim_ids",
}
SOURCE_CLASSES = {
    "regulatory-filing",
    "government",
    "company-filing",
    "company-material",
    "technical-paper",
    "trade-association",
    "customer-interview",
    "expert-interview",
    "reputable-media",
    "market-database",
    "user-document",
    "other",
}
ENUM_FIELDS = {
    ("question", "priority"): {"high", "medium", "low"},
    ("question", "state"): {"open", "supported", "refuted", "gap"},
    ("query", "direction"): {"support", "counter", "neutral"},
    ("query", "outcome"): {"captured", "no-result", "error"},
    ("source", "source_class"): SOURCE_CLASSES,
    ("source", "stance"): {"support", "counter", "neutral", "mixed"},
    ("claim", "claim_kind"): {
        "third_party_fact",
        "company_claim",
        "user_observation",
        "model_estimate",
        "agent_inference",
        "unknown",
    },
    ("claim", "importance"): {"decision_critical", "material", "context"},
    ("claim", "confidence"): {"high", "medium", "low", "unknown"},
    ("claim", "conflict_resolution"): {"none", "reconciled", "narrowed", "unresolved"},
    ("claim", "state"): {"supported", "refuted", "narrowed", "unverified"},
}
RECORD_PREFIXES = {
    "scope": "SC",
    "question": "Q",
    "query": "QU",
    "source": "S",
    "claim": "C",
    "waiver": "W",
}
NON_EMPTY_LIST_FIELDS = {"inclusions", "evidence_needed"}
NON_WAIVABLE_RULES = {
    "required_scope",
    "high_priority_question_open",
    "artifact_missing",
    "artifact_names",
    "artifact_unreadable",
    "artifact_suffix",
    "artifact_source_reference",
    "artifact_source_coverage",
    "artifact_workbook_sheets",
    "artifact_docx",
    "partial_label_missing",
    "upstream_audit_missing",
    "upstream_audit_blocked",
    "upstream_audit_ambiguous",
    "search_stability_changed",
}


class LedgerError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def record_fingerprint(payload: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in payload.items() if key != "record_fingerprint"}
    return hashlib.sha256(canonical_bytes(unsigned)).hexdigest()


def source_content_fingerprint(record: dict[str, Any]) -> str:
    evidence_packet = {
        key: record[key]
        for key in (
            "title",
            "publisher",
            "author",
            "published_at",
            "source_class",
            "location",
            "excerpt",
            "definition",
            "geography",
            "sample",
            "statistical_scope",
        )
    }
    return hashlib.sha256(canonical_bytes(evidence_packet)).hexdigest()


def normalize_input_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(record)
    if normalized.get("record_type") == "source":
        required_without_fingerprint = REQUIRED_FIELDS["source"] - {"content_fingerprint"}
        if not (required_without_fingerprint - normalized.keys()):
            expected = source_content_fingerprint(normalized)
            supplied = normalized.get("content_fingerprint")
            if supplied not in (None, expected):
                raise LedgerError(f"{normalized.get('record_id', '<unknown>')}: content_fingerprint mismatch")
            normalized["content_fingerprint"] = expected
    return normalized


def validate_timestamp(value: Any, field: str, record_id: str) -> None:
    if not isinstance(value, str) or "T" not in value or not value.endswith("Z"):
        raise LedgerError(f"{record_id}: {field} must be an ISO 8601 UTC timestamp")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise LedgerError(f"{record_id}: invalid {field}") from exc


def validate_input_record(record: dict[str, Any]) -> None:
    if not isinstance(record, dict):
        raise LedgerError("record must be a JSON object")
    if DERIVED_FIELDS & record.keys():
        raise LedgerError("caller must not set derived chain fields")
    missing = BASE_FIELDS - record.keys()
    if missing:
        raise LedgerError(f"{record.get('record_id', '<unknown>')}: missing fields {sorted(missing)}")
    if type(record["schema_version"]) is not int or record["schema_version"] != SCHEMA_VERSION:
        raise LedgerError(f"{record['record_id']}: unsupported schema_version")
    record_type = record["record_type"]
    if not isinstance(record_type, str):
        raise LedgerError(f"{record['record_id']}: record_type must be a string")
    if record_type not in REQUIRED_FIELDS:
        raise LedgerError(f"{record['record_id']}: unknown record_type {record_type!r}")
    prefix = RECORD_PREFIXES[record_type]
    suffix = str(record["record_id"])[len(prefix):]
    if (
        not str(record["record_id"]).startswith(prefix)
        or not suffix.isdigit()
        or suffix.startswith("0")
    ):
        raise LedgerError(f"{record['record_id']}: invalid record_id prefix")
    missing = REQUIRED_FIELDS[record_type] - record.keys()
    if missing:
        raise LedgerError(f"{record['record_id']}: missing fields {sorted(missing)}")
    record_id = str(record["record_id"])
    for field in BASE_FIELDS - {"schema_version"}:
        if not isinstance(record[field], str) or not record[field].strip():
            raise LedgerError(f"{record_id}: {field} must be a non-empty string")
    validate_timestamp(record["created_at"], "created_at", record_id)
    for field in REQUIRED_FIELDS[record_type] - LIST_FIELDS:
        if field in {"result_count", "search_round"}:
            if isinstance(record[field], bool) or not isinstance(record[field], int) or record[field] < 0:
                raise LedgerError(f"{record_id}: {field} must be a non-negative integer")
            if field == "search_round" and record[field] == 0:
                raise LedgerError(f"{record_id}: search_round must be positive")
        elif field == "changed_core_judgment":
            if type(record[field]) is not bool:
                raise LedgerError(f"{record_id}: changed_core_judgment must be boolean")
        elif not isinstance(record[field], str) or not record[field].strip():
            raise LedgerError(f"{record_id}: {field} must be a non-empty string")
    for field in REQUIRED_FIELDS[record_type] & LIST_FIELDS:
        if not isinstance(record[field], list) or any(
            not isinstance(item, str) or not item.strip() for item in record[field]
        ):
            raise LedgerError(f"{record_id}: {field} must be a string list")
        if len(record[field]) != len(set(record[field])):
            raise LedgerError(f"{record_id}: {field} contains duplicates")
        if field in NON_EMPTY_LIST_FIELDS and not record[field]:
            raise LedgerError(f"{record_id}: {field} must not be empty")
    for (expected_type, field), allowed in ENUM_FIELDS.items():
        if record_type == expected_type and record[field] not in allowed:
            raise LedgerError(f"{record_id}: invalid {field} {record[field]!r}")
    if record_type == "query":
        validate_timestamp(record["executed_at"], "executed_at", record_id)
        if record["target_source_class"] not in SOURCE_CLASSES:
            raise LedgerError(f"{record_id}: invalid target_source_class")
        if record["outcome"] == "no-result" and record["result_count"] != 0:
            raise LedgerError(f"{record_id}: no-result requires result_count 0")
        if record["outcome"] == "captured" and record["result_count"] == 0:
            raise LedgerError(f"{record_id}: captured requires a positive result_count")
    if record_type == "source":
        validate_timestamp(record["accessed_at"], "accessed_at", record_id)
        if record["content_fingerprint"] != source_content_fingerprint(record):
            raise LedgerError(f"{record_id}: content_fingerprint mismatch")
    if record_type == "waiver":
        validate_timestamp(record["approved_at"], "approved_at", record_id)
        if record["rule"] in NON_WAIVABLE_RULES:
            raise LedgerError(f"{record_id}: rule cannot be waived: {record['rule']}")
        if record["actor"] != record["approved_by"] or record["created_at"] != record["approved_at"]:
            raise LedgerError(f"{record_id}: waiver actor and approval time must match provenance")
    if record_type == "claim":
        has_counter = bool(record["counter_source_ids"])
        if has_counter and record["conflict_resolution"] == "none":
            raise LedgerError(f"{record_id}: counter evidence requires conflict_resolution")
        if not has_counter and record["conflict_resolution"] != "none":
            raise LedgerError(f"{record_id}: conflict_resolution requires counter evidence")
        if record["conflict_resolution"] == "narrowed" and record["state"] != "narrowed":
            raise LedgerError(f"{record_id}: narrowed conflict requires narrowed state")


def effective_records(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    effective = {record["record_id"]: record for record in records}
    for record in records:
        superseded = record.get("supersedes")
        if superseded:
            effective.pop(str(superseded), None)
    return effective


def resolve_record_id(records: list[dict[str, Any]], record_id: str) -> str:
    successors = {
        str(record["supersedes"]): str(record["record_id"])
        for record in records
        if record.get("supersedes")
    }
    resolved = str(record_id)
    while resolved in successors:
        resolved = successors[resolved]
    return resolved
```

Secure Hash Algorithm 256-bit（SHA-256，256 位安全散列算法，用于生成稳定内容指纹）is the only hash needed; do not add a cryptography dependency.

- [ ] **Step 4: Implement reference checks and atomic writes**

Add:

```python
def validate_references(
    new_records: list[dict[str, Any]],
    existing_records: list[dict[str, Any]],
) -> None:
    known = {record["record_id"]: record for record in existing_records}
    superseded_ids = {
        str(record["supersedes"])
        for record in existing_records
        if record.get("supersedes")
    }
    for record in new_records:
        record_id = str(record["record_id"])
        if record_id in known:
            raise LedgerError(f"duplicate record_id: {record_id}")
        for field, expected_type in REFERENCE_FIELDS.items():
            raw = record.get(field)
            values = raw if isinstance(raw, list) else ([] if raw in (None, "") else [raw])
            for value in values:
                target = known.get(str(value))
                if target is None:
                    raise LedgerError(f"{record_id}: unknown reference {value!r}")
                if expected_type and target["record_type"] != expected_type:
                    raise LedgerError(f"{record_id}: {field} must reference {expected_type}")
        superseded = record.get("supersedes")
        if superseded:
            superseded_id = str(superseded)
            if superseded_id in superseded_ids:
                raise LedgerError(f"{record_id}: record already superseded: {superseded_id}")
            if known[superseded_id]["record_type"] != record["record_type"]:
                raise LedgerError(f"{record_id}: supersedes must keep record_type")
            superseded_ids.add(superseded_id)
        known[record_id] = record


def chained_records(
    existing: list[dict[str, Any]],
    additions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    previous = existing[-1]["record_fingerprint"] if existing else ""
    sequence = len(existing)
    output = []
    for raw in additions:
        sequence += 1
        record = {
            **raw,
            "sequence": sequence,
            "previous_fingerprint": previous,
        }
        record["record_fingerprint"] = record_fingerprint(record)
        previous = record["record_fingerprint"]
        output.append(record)
    return output


def atomic_write(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            for record in records:
                handle.write(canonical_bytes(record).decode("utf-8") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
```

- [ ] **Step 5: Implement registry load, init, and append**

Add:

```python
def registry_path(run_dir: Path) -> Path:
    return Path(run_dir).resolve() / REGISTRY_NAME


@contextmanager
def registry_lock(run_dir: Path) -> Iterator[None]:
    # ponytail: fail closed on a stale lock; add PID/lease recovery only if crashes make it operationally necessary.
    path = registry_path(run_dir).with_name(f".{REGISTRY_NAME}.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise LedgerError(f"another registry writer is active: {path}") from exc
    try:
        os.write(descriptor, str(os.getpid()).encode("ascii"))
        os.close(descriptor)
        yield
    finally:
        try:
            os.close(descriptor)
        except OSError:
            pass
        path.unlink(missing_ok=True)


def load_registry(run_dir: Path) -> list[dict[str, Any]]:
    path = registry_path(run_dir)
    if not path.is_file():
        raise LedgerError(f"missing registry: {path}")
    records = []
    previous = ""
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LedgerError(f"invalid JSONL at line {line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise LedgerError(f"record at line {line_number} must be an object")
        if record.get("sequence") != line_number:
            raise LedgerError(f"sequence mismatch at line {line_number}")
        if record.get("previous_fingerprint") != previous:
            raise LedgerError(f"previous fingerprint mismatch at line {line_number}")
        expected = record_fingerprint(record)
        if record.get("record_fingerprint") != expected:
            raise LedgerError(f"record fingerprint mismatch at line {line_number}")
        previous = expected
        records.append(record)
    if not records:
        raise LedgerError(f"empty registry: {path}")
    replayed = [
        {key: value for key, value in record.items() if key not in DERIVED_FIELDS}
        for record in records
    ]
    for record in replayed:
        validate_input_record(record)
    validate_references(replayed, [])
    effective_scopes = [
        record
        for record in effective_records(replayed).values()
        if record["record_type"] == "scope"
    ]
    if len(effective_scopes) != 1:
        raise LedgerError("registry must contain exactly one effective scope")
    return records


def init_registry(run_dir: Path, skill: str, scope: dict[str, Any]) -> None:
    with registry_lock(run_dir):
        path = registry_path(run_dir)
        if path.exists():
            raise LedgerError(f"registry already exists: {path}")
        scope = normalize_input_record(scope)
        validate_input_record(scope)
        if scope["record_type"] != "scope" or scope["created_by_skill"] != skill:
            raise LedgerError("scope must be created by the initializing skill")
        atomic_write(path, chained_records([], [scope]))


def append_records(run_dir: Path, additions: list[dict[str, Any]]) -> None:
    with registry_lock(run_dir):
        existing = load_registry(run_dir)
        additions = [normalize_input_record(record) for record in additions]
        for record in additions:
            validate_input_record(record)
            if record["record_type"] == "scope" and not record.get("supersedes"):
                raise LedgerError(f"{record['record_id']}: additional scope must supersede the active scope")
        validate_references(additions, existing)
        atomic_write(registry_path(run_dir), [*existing, *chained_records(existing, additions)])
```

`load_registry` must validate replayed historical records using their original order. If direct reuse of `validate_references` makes derived-field stripping unclear, add a private `validate_replayed_references()` rather than weakening the chain check.

- [ ] **Step 6: Run the ledger check**

Run:

```bash
python3 skills/jvc-research-core/scripts/check_package.py
```

Expected: `research core ledger checks passed`.

- [ ] **Step 7: Commit the ledger slice**

```bash
git add skills/jvc-research-core/scripts/researchctl.py \
  skills/jvc-research-core/scripts/check_package.py
git commit -m "Add append-only research ledger"
```

### Task 3: Add profiles and the three-state audit engine

**Files:**

- Modify: `skills/jvc-research-core/scripts/check_package.py`
- Modify: `skills/jvc-research-core/scripts/researchctl.py`
- Create: all eleven files under `skills/jvc-research-core/profiles/`

- [ ] **Step 1: Extend the self-check with failing audit cases**

Add imports:

```python
from researchctl import (
    LedgerError,
    append_records,
    audit_run,
    init_registry,
    load_registry,
    resolve_record_id,
    saved_audit_is_valid,
    write_waiver,
)
```

Add reusable fixture helpers and the audit assertions after the ledger check:

```python
def source(source_id: str, source_class: str, independence_key: str) -> dict[str, object]:
    return record(
        source_id,
        "source",
        title=f"来源 {source_id}",
        publisher=f"机构 {independence_key}",
        author="测试作者",
        published_at="2026-07-01",
        accessed_at="2026-07-29T00:00:00Z",
        source_class=source_class,
        location=f"https://example.invalid/{source_id}",
        excerpt="与测试主张直接相关的最小摘录",
        definition="量产良率指符合客户交付规格的良品占比",
        geography="全球",
        sample="公开披露的量产项目",
        statistical_scope="截至 2026-07-01 的已披露项目",
        stance="neutral",
        independence_key=independence_key,
    )


def build_ready_fixture(root: Path) -> tuple[Path, Path]:
    run_dir = root / "run"
    report = root / "report.md"
    report.write_text("关键事实 [S1] [S2]\n", encoding="utf-8")
    scope = record(
        "SC1",
        "scope",
        subject="玻璃基板",
        decision="确定下一轮尽调重点",
        inclusions=["先进封装"],
        exclusions=["显示盖板"],
        geography="全球及中国",
        time_range="2024-2029",
        user_assumptions=[],
    )
    init_registry(run_dir, "jvc-track-research", scope)
    append_records(
        run_dir,
        [
            record(
                "Q1",
                "question",
                question_text="玻璃基板量产良率是否仍限制规模交付？",
                priority="high",
                hypothesis="良率限制规模交付",
                falsifier="量产证据证明良率不构成瓶颈",
                evidence_needed=["量产良率", "规模交付"],
                state="supported",
            ),
            record(
                "QU1",
                "query",
                question_id="Q1",
                direction="counter",
                query_text="玻璃基板 良率 不构成瓶颈",
                tool_class="web-search",
                target_source_class="company-filing",
                executed_at="2026-07-29T00:02:00Z",
                search_round=1,
                changed_core_judgment=False,
                result_count=1,
                outcome="captured",
                result_summary="找到一项满足来源类型要求的反向材料并已登记",
            ),
            record(
                "QU2",
                "query",
                question_id="Q1",
                direction="support",
                query_text="玻璃基板 量产 良率 交付",
                tool_class="web-search",
                target_source_class="technical-paper",
                executed_at="2026-07-29T00:02:30Z",
                search_round=2,
                changed_core_judgment=False,
                result_count=1,
                outcome="captured",
                result_summary="第二轮检索未改变良率仍为瓶颈的核心判断",
            ),
            source("S1", "regulatory-filing", "issuer-a"),
            source("S2", "technical-paper", "authors-b"),
            record(
                "C1",
                "claim",
                question_id="Q1",
                claim_text="现有公开证据仍指向量产良率瓶颈",
                claim_kind="third_party_fact",
                topic="technical_maturity",
                importance="decision_critical",
                support_source_ids=["S1", "S2"],
                counter_source_ids=[],
                derived_from_claim_ids=[],
                scope="先进封装玻璃基板",
                confidence="medium",
                reasoning="两类独立来源指向同一瓶颈",
                conflict_resolution="none",
                state="supported",
            ),
        ],
    )
    return run_dir, report


def add_gap(run_dir: Path) -> None:
    append_records(
        run_dir,
        [
            record(
                "Q2",
                "question",
                question_text="客户导入节奏能否在公开信息中独立验证？",
                priority="high",
                hypothesis="公开证据暂不足",
                falsifier="找到两类独立客户采用证据",
                evidence_needed=["客户采用", "量产时间"],
                state="gap",
            ),
            record(
                "QU3",
                "query",
                question_id="Q2",
                direction="support",
                query_text="玻璃基板 客户导入 量产 时间",
                tool_class="web-search",
                target_source_class="company-filing",
                executed_at="2026-07-29T00:04:00Z",
                search_round=1,
                changed_core_judgment=False,
                result_count=0,
                outcome="no-result",
                result_summary="未找到可独立验证客户导入节奏的披露",
            ),
            record(
                "QU4",
                "query",
                question_id="Q2",
                direction="counter",
                query_text="玻璃基板 客户延迟 取消 导入",
                tool_class="web-search",
                target_source_class="reputable-media",
                executed_at="2026-07-29T00:05:00Z",
                search_round=2,
                changed_core_judgment=False,
                result_count=0,
                outcome="no-result",
                result_summary="第二轮仍未找到可独立验证的采用或取消证据",
            ),
        ],
    )


def add_blocked_company_claim(run_dir: Path) -> None:
    append_records(
        run_dir,
        [
            record(
                "C2",
                "claim",
                question_id="Q1",
                claim_text="项目已经形成规模收入",
                claim_kind="company_claim",
                topic="commercialization",
                importance="decision_critical",
                support_source_ids=["S1"],
                counter_source_ids=[],
                derived_from_claim_ids=[],
                scope="规模收入",
                confidence="low",
                reasoning="仅有公司侧材料",
                conflict_resolution="none",
                state="supported",
            )
        ],
    )


def check_audit() -> None:
    with TemporaryDirectory() as temporary:
        run_dir, report = build_ready_fixture(Path(temporary))
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "ready"
        ready_entry = json.loads((run_dir / "audit.json").read_text(encoding="utf-8"))["audits"][0]
        ic_report = Path(temporary) / "ic.md"
        ic_report.write_text("投资结论 [S1] [S2]\n", encoding="utf-8")
        append_records(
            run_dir,
            [
                record(
                    "C3",
                    "claim",
                    created_by_skill="jvc-ic-memo",
                    question_id="Q1",
                    claim_text="良率瓶颈仍应列为投资委员会核心风险",
                    claim_kind="agent_inference",
                    topic="technical_maturity",
                    importance="decision_critical",
                    support_source_ids=["S1", "S2"],
                    counter_source_ids=[],
                    derived_from_claim_ids=["C1"],
                    scope="先进封装玻璃基板",
                    confidence="medium",
                    reasoning="继承已审研究主张并收窄为投资风险",
                    conflict_resolution="none",
                    state="supported",
                )
            ],
        )
        assert audit_run(run_dir, "jvc-ic-memo", [ic_report])["status"] == "ready"
        audit_entries = json.loads((run_dir / "audit.json").read_text(encoding="utf-8"))["audits"]
        ic_entry = next(entry for entry in audit_entries if entry["skill"] == "jvc-ic-memo")
        original_report = report.read_text(encoding="utf-8")
        report.write_text(original_report + "变更\n", encoding="utf-8")
        assert not saved_audit_is_valid(ic_entry, load_registry(run_dir))
        report.write_text(original_report, encoding="utf-8")
        assert saved_audit_is_valid(ic_entry, load_registry(run_dir))
        add_gap(run_dir)
        assert saved_audit_is_valid(ready_entry, load_registry(run_dir))
        report.write_text(original_report + "变更\n", encoding="utf-8")
        assert not saved_audit_is_valid(ready_entry, load_registry(run_dir))
        report.write_text(original_report, encoding="utf-8")
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "blocked"
        report.write_text("研究状态：partial\n" + original_report, encoding="utf-8")
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "partial"
        add_blocked_company_claim(run_dir)
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "blocked"
        write_waiver(
            run_dir,
            skill="jvc-track-research",
            rule="company_claim_unverified",
            reason="用户只需要保留公司口径用于下一轮访谈",
            scope="C2",
            approved_by="test-user",
            approved_at="2026-07-29T00:03:00Z",
            residual_risk="商业化仍未被第三方验证",
        )
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "partial"
        expect_error(
            lambda: write_waiver(
                run_dir,
                skill="jvc-track-research",
                rule="artifact_missing",
                reason="测试不可豁免规则",
                scope="report.md",
                approved_by="test-user",
                approved_at="2026-07-29T00:04:00Z",
                residual_risk="产物仍然缺失",
            ),
            "cannot be waived",
        )
```

Call `check_audit()` from `__main__`.

- [ ] **Step 2: Run the check and verify it fails**

Run:

```bash
python3 skills/jvc-research-core/scripts/check_package.py
```

Expected: non-zero exit because `audit_run` and `write_waiver` do not exist.

- [ ] **Step 3: Create the exact profile schema**

Every profile is a JSON object with:

```json
{
  "schema_version": 1,
  "skill": "jvc-track-research",
  "required_record_types": ["scope", "question", "query", "source", "claim"],
  "current_skill_record_types": ["question", "query", "source", "claim"],
  "requires_counter_query": true,
  "minimum_independent_sources": 2,
  "artifact_policy": {
    "kind": "markdown",
    "allowed_suffixes": [".md"],
    "required_names": [],
    "required_sheets": []
  }
}
```

Office Open XML Workbook（XLSX，Office 开放 XML 工作簿格式，用于可计算的表格产物）and Microsoft Word Open XML Document（DOCX，Microsoft Word 开放 XML 文档格式，用于可编辑纪要）are both inspected as ZIP-contained XML with the standard library. Use these exact values:

| Profile | `required_record_types` | `current_skill_record_types` | Counter query | Min independent sources | Artifact policy |
| --- | --- | --- | ---: | ---: | --- |
| `jvc-meeting-notes` | `scope,source` | `source` | false | 1 | `docx`, suffix `.docx` |
| `jvc-talk-notes` | `scope,source` | `source` | false | 1 | `docx`, suffix `.docx` |
| `jvc-prescreen` | `scope,question,source,claim` | `question,claim` | false | 1 | `markdown`, suffix `.md` |
| `jvc-bull-case` | `scope,question,source,claim` | `claim` | false | 2 | `markdown`, suffix `.md` |
| `jvc-bear-case` | `scope,question,source,claim` | `question,claim` | false | 1 | `markdown`, suffix `.md` |
| `jvc-track-research` | `scope,question,query,source,claim` | `question,query,source,claim` | true | 2 | `markdown`, suffix `.md` |
| `jvc-comps-dd` | `scope,question,query,source,claim` | `question,query,source,claim` | true | 2 | `xlsx`, suffix `.xlsx`, sheets `companies,segmentation,sources,coverage_notes` |
| `jvc-market-sizing` | `scope,question,query,source,claim` | `question,query,source,claim` | true | 2 | `xlsx`, suffix `.xlsx`, sheets `assumptions,top_down,bottom_up,reconciliation,orthogonality_check,sources` |
| `jvc-knowledge-tree-builder` | `scope,question,source,claim` | `source,claim` | false | 1 | `multi`, names `knowledge_tree.md,knowledge_graph.mmd,nodes.json,evidence_index.md,open_questions.md` |
| `jvc-roi-modeler` | `scope,question,source,claim` | `claim` | false | 1 | `xlsx`, suffix `.xlsx`, sheets `investment_terms,financial_forecast,financing_dilution,ownership,exit_scenarios,returns,sensitivity,sources` |
| `jvc-ic-memo` | `scope,question,source,claim` | `claim` | false | 2 | `markdown`, suffix `.md` |

For profiles without sheets or names, store empty arrays. Do not add freshness windows until a real skill has a domain-specific window.

- [ ] **Step 4: Implement profile loading and artifact checks**

Add:

```python
import re
import zipfile
from xml.etree import ElementTree

CORE_ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = CORE_ROOT / "profiles"


def load_profile(skill: str) -> dict[str, Any]:
    path = PROFILE_ROOT / f"{skill}.json"
    if not path.is_file():
        raise LedgerError(f"missing profile for {skill}")
    profile = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(profile, dict):
        raise LedgerError(f"invalid profile {skill}: expected object")
    required = {
        "schema_version",
        "skill",
        "required_record_types",
        "current_skill_record_types",
        "requires_counter_query",
        "minimum_independent_sources",
        "artifact_policy",
    }
    missing = required - profile.keys()
    if missing or profile.get("schema_version") != 1 or profile.get("skill") != skill:
        raise LedgerError(f"invalid profile {skill}: missing={sorted(missing)}")
    required_types = profile["required_record_types"]
    current_types = profile["current_skill_record_types"]
    if (
        not isinstance(required_types, list)
        or not required_types
        or any(not isinstance(value, str) for value in required_types)
        or not set(required_types) <= set(REQUIRED_FIELDS)
        or not isinstance(current_types, list)
        or any(not isinstance(value, str) for value in current_types)
        or not set(current_types) <= set(required_types)
    ):
        raise LedgerError(f"invalid profile {skill}: record types")
    if type(profile["requires_counter_query"]) is not bool:
        raise LedgerError(f"invalid profile {skill}: requires_counter_query")
    minimum = profile["minimum_independent_sources"]
    if type(minimum) is not int or minimum < 1:
        raise LedgerError(f"invalid profile {skill}: minimum_independent_sources")
    policy = profile["artifact_policy"]
    if not isinstance(policy, dict) or policy.get("kind") not in {"markdown", "xlsx", "docx", "multi"}:
        raise LedgerError(f"invalid profile {skill}: artifact_policy")
    for field in ("allowed_suffixes", "required_names", "required_sheets"):
        values = policy.get(field)
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise LedgerError(f"invalid profile {skill}: artifact_policy.{field}")
    return profile


def file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def profile_fingerprint(profile: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(profile)).hexdigest()


def core_runtime_fingerprint() -> str:
    return file_fingerprint(Path(__file__).resolve())


def workbook_sheets(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return {str(node.attrib["name"]) for node in root.findall("x:sheets/x:sheet", namespace)}


def artifact_text(path: Path) -> str:
    if path.suffix.lower() in {".md", ".mmd", ".json"}:
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".xlsx", ".docx"}:
        with zipfile.ZipFile(path) as archive:
            return "\n".join(
                archive.read(name).decode("utf-8", errors="ignore")
                for name in archive.namelist()
                if name.endswith(".xml")
            )
    return ""


def validate_artifacts(
    profile: dict[str, Any],
    artifacts: list[Path],
    all_source_ids: set[str],
    required_source_ids: set[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    findings = []
    fingerprints = []
    policy = profile["artifact_policy"]
    allowed = set(policy.get("allowed_suffixes", []))
    names = {path.name for path in artifacts}
    cited_source_ids: set[str] = set()
    missing_names = set(policy.get("required_names", [])) - names
    if missing_names:
        findings.append({"rule": "artifact_names", "severity": "block", "message": f"missing artifacts: {sorted(missing_names)}"})
    for raw in artifacts:
        path = Path(raw).resolve()
        if not path.is_file():
            findings.append({"rule": "artifact_missing", "severity": "block", "message": str(path)})
            continue
        if allowed and path.suffix.lower() not in allowed:
            findings.append({"rule": "artifact_suffix", "severity": "block", "message": str(path)})
        fingerprints.append({"path": str(path), "fingerprint": file_fingerprint(path)})
        try:
            text = artifact_text(path)
        except (KeyError, OSError, UnicodeError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
            findings.append({"rule": "artifact_unreadable", "severity": "block", "message": f"{path}: {exc}"})
            continue
        if text:
            used = set(re.findall(r"\[(S[1-9]\d*)\]", text))
            cited_source_ids.update(used)
            unknown = used - all_source_ids
            if unknown:
                findings.append({"rule": "artifact_source_reference", "severity": "block", "message": f"unknown sources: {sorted(unknown)}"})
        if path.suffix.lower() == ".xlsx":
            try:
                missing = set(policy.get("required_sheets", [])) - workbook_sheets(path)
            except (KeyError, OSError, UnicodeError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
                findings.append({"rule": "artifact_unreadable", "severity": "block", "message": f"{path}: {exc}"})
                continue
            if missing:
                findings.append({"rule": "artifact_workbook_sheets", "severity": "block", "message": f"missing sheets: {sorted(missing)}"})
        if path.suffix.lower() == ".docx":
            with zipfile.ZipFile(path) as archive:
                if "word/document.xml" not in archive.namelist():
                    findings.append({"rule": "artifact_docx", "severity": "block", "message": "word/document.xml missing"})
    missing_required = required_source_ids - cited_source_ids
    if missing_required:
        findings.append({"rule": "artifact_source_coverage", "severity": "block", "message": f"uncited current-stage sources: {sorted(missing_required)}"})
    return findings, fingerprints
```

The workbook and document checks intentionally validate only the evidence-runtime boundary. Existing dedicated format validators remain mandatory and are not duplicated here.

- [ ] **Step 5: Implement common audit findings**

Add:

```python
def add_finding(findings: list[dict[str, str]], rule: str, severity: str, message: str) -> None:
    finding = {"rule": rule, "severity": severity, "message": message}
    if finding not in findings:
        findings.append(finding)


def audit_records(
    records: list[dict[str, Any]],
    skill: str,
    profile: dict[str, Any],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    effective = effective_records(records)
    active = list(effective.values())
    by_type = {
        record_type: [record for record in active if record["record_type"] == record_type]
        for record_type in REQUIRED_FIELDS
    }
    for record_type in profile["required_record_types"]:
        if not by_type.get(record_type):
            add_finding(findings, f"required_{record_type}", "block", f"missing {record_type}")
    for record_type in profile["current_skill_record_types"]:
        if not any(record["created_by_skill"] == skill for record in by_type.get(record_type, [])):
            add_finding(findings, f"current_{record_type}", "block", f"{skill} created no {record_type}")
    queries = by_type.get("query", [])
    claims = by_type.get("claim", [])
    claim_states_by_question: dict[str, set[str]] = {}
    for claim in claims:
        question_id = resolve_record_id(records, claim["question_id"])
        claim_states_by_question.setdefault(question_id, set()).add(str(claim["state"]))
    for question in by_type.get("question", []):
        if question["priority"] != "high":
            continue
        if question["state"] == "open":
            add_finding(findings, "high_priority_question_open", "block", question["record_id"])
        elif question["state"] == "gap":
            add_finding(findings, "high_priority_question_gap", "partial", question["record_id"])
        elif question["state"] not in claim_states_by_question.get(question["record_id"], set()):
            add_finding(findings, "resolved_question_without_claim", "block", question["record_id"])
        if profile["requires_counter_query"]:
            question_id = str(question["record_id"])
            related_queries = [
                query
                for query in queries
                if resolve_record_id(records, query["question_id"]) == question_id
            ]
            rounds = sorted({int(query["search_round"]) for query in related_queries})
            if len(rounds) < 2:
                add_finding(findings, "search_stability_missing", "block", question_id)
            else:
                latest_rounds = set(rounds[-2:])
                if any(
                    query["changed_core_judgment"]
                    for query in related_queries
                    if query["search_round"] in latest_rounds
                ):
                    add_finding(findings, "search_stability_changed", "block", question_id)

    counter_questions = {
        resolve_record_id(records, record["question_id"])
        for record in queries
        if record.get("direction") == "counter"
    }
    sources = {record["record_id"]: record for record in by_type.get("source", [])}
    for claim in claims:
        if claim.get("created_by_skill") != skill:
            continue
        rule_scope = str(claim["record_id"])
        critical = claim["importance"] == "decision_critical"
        evidence_severity = "block" if critical else "partial"
        claim_question_id = resolve_record_id(records, claim["question_id"])
        if critical and profile["requires_counter_query"] and claim_question_id not in counter_questions:
            add_finding(findings, "counter_query_missing", "block", rule_scope)
        support_ids = [
            resolve_record_id(records, source_id)
            for source_id in claim["support_source_ids"]
        ]
        counter_ids = [
            resolve_record_id(records, source_id)
            for source_id in claim["counter_source_ids"]
        ]
        evidence_ids = counter_ids if claim["state"] == "refuted" else support_ids
        evidence = [sources[source_id] for source_id in evidence_ids]
        for source in evidence:
            for field in ("published_at", "definition", "geography", "sample", "statistical_scope"):
                if source[field].strip().casefold() in {"unknown", "未知"}:
                    add_finding(
                        findings,
                        "source_scope_unknown",
                        evidence_severity,
                        f"{source['record_id']}:{field}",
                    )
        if critical and claim["claim_kind"] in {"third_party_fact", "agent_inference"}:
            classes = {source["source_class"] for source in evidence}
            independence_keys = {source["independence_key"].casefold() for source in evidence}
            publishers = {source["publisher"].casefold() for source in evidence}
            locations = {source["location"].casefold() for source in evidence}
            fingerprints = {source["content_fingerprint"] for source in evidence}
            minimum = int(profile["minimum_independent_sources"])
            if any(
                len(values) < minimum
                for values in (classes, independence_keys, publishers, locations, fingerprints)
            ):
                add_finding(findings, "independent_sources", "block", rule_scope)
        if claim["claim_kind"] == "company_claim":
            independent_keys = {source["independence_key"] for source in evidence}
            external_sources = [
                source
                for source in evidence
                if source["source_class"] not in {"company-filing", "company-material"}
            ]
            if len(independent_keys) < 2 or not external_sources:
                add_finding(findings, "company_claim_unverified", evidence_severity, rule_scope)
        if claim["claim_kind"] == "unknown":
            add_finding(findings, "claim_kind_unknown", evidence_severity, rule_scope)
        if claim["conflict_resolution"] == "unresolved":
            add_finding(findings, "conflict_unresolved", evidence_severity, rule_scope)
        if not evidence_ids:
            add_finding(findings, "claim_unsupported", evidence_severity, rule_scope)
        if claim["state"] == "unverified":
            add_finding(findings, "claim_unverified", evidence_severity, rule_scope)
        elif claim["state"] == "narrowed":
            add_finding(findings, "claim_narrowed", "partial", rule_scope)
    return findings
```

- [ ] **Step 6: Implement waivers, status, and audit persistence**

Add:

```python
def apply_waivers(
    findings: list[dict[str, str]],
    records: list[dict[str, Any]],
    skill: str,
) -> list[dict[str, str]]:
    waivers = [
        record
        for record in effective_records(records).values()
        if record["record_type"] == "waiver" and record["created_by_skill"] == skill
    ]
    output = []
    for finding in findings:
        matched = next(
            (
                waiver
                for waiver in waivers
                if waiver["rule"] == finding["rule"]
                and waiver["scope"] == finding["message"]
            ),
            None,
        )
        if matched and finding["rule"] not in NON_WAIVABLE_RULES and finding["severity"] == "block":
            output.append({**finding, "severity": "partial", "waiver_id": matched["record_id"]})
        else:
            output.append(finding)
    return output


def status_for(findings: list[dict[str, str]]) -> str:
    if any(finding["severity"] == "block" for finding in findings):
        return "blocked"
    if any(finding["severity"] == "partial" for finding in findings):
        return "partial"
    return "ready"


def ledger_prefix_fingerprint(records: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(canonical_bytes(record))
        digest.update(b"\n")
    return digest.hexdigest()


def audit_binding(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "skill": entry["skill"],
        "ledger_sequence": entry["ledger_sequence"],
        "ledger_prefix_fingerprint": entry["ledger_prefix_fingerprint"],
        "artifacts": entry["artifacts"],
        "profile_fingerprint": entry["profile_fingerprint"],
        "core_runtime_fingerprint": entry["core_runtime_fingerprint"],
        "status": entry["status"],
        "audit_key": entry["audit_key"],
        "dependency_audits": entry.get("dependency_audits", []),
    }


def dependency_findings(
    run_dir: Path,
    records: list[dict[str, Any]],
    skill: str,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    effective = effective_records(records)
    sources = {
        record["record_id"]: record
        for record in effective.values()
        if record["record_type"] == "source"
    }
    claims = {
        record["record_id"]: record
        for record in effective.values()
        if record["record_type"] == "claim"
    }
    dependencies: set[str] = set()
    for claim in claims.values():
        if claim["created_by_skill"] != skill:
            continue
        for source_id in [*claim["support_source_ids"], *claim["counter_source_ids"]]:
            source_skill = sources[resolve_record_id(records, source_id)]["created_by_skill"]
            if source_skill != skill:
                dependencies.add(source_skill)
        for claim_id in claim["derived_from_claim_ids"]:
            claim_skill = claims[resolve_record_id(records, claim_id)]["created_by_skill"]
            if claim_skill != skill:
                dependencies.add(claim_skill)
    if not dependencies:
        return [], []

    audit_path = Path(run_dir) / "audit.json"
    if not audit_path.is_file():
        return (
            [
                {"rule": "upstream_audit_missing", "severity": "block", "message": dependency}
                for dependency in sorted(dependencies)
            ],
            [],
        )
    payload = json.loads(audit_path.read_text(encoding="utf-8"))
    entries = payload.get("audits", []) if isinstance(payload, dict) else []
    valid_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict) and saved_audit_is_valid(entry, records)
    ]
    findings = []
    bindings = []
    for dependency in sorted(dependencies):
        candidates = [
            entry for entry in valid_entries if entry.get("skill") == dependency
        ]
        if not candidates:
            add_finding(findings, "upstream_audit_missing", "block", dependency)
            continue
        latest_sequence = max(int(entry["ledger_sequence"]) for entry in candidates)
        latest = [
            entry for entry in candidates
            if int(entry["ledger_sequence"]) == latest_sequence
        ]
        if len(latest) != 1:
            add_finding(findings, "upstream_audit_ambiguous", "block", dependency)
            continue
        entry = latest[0]
        bindings.append(audit_binding(entry))
        if entry["status"] == "blocked":
            add_finding(findings, "upstream_audit_blocked", "block", dependency)
        elif entry["status"] == "partial":
            add_finding(findings, "upstream_audit_partial", "partial", dependency)
    return findings, bindings


def audit_run(run_dir: Path, skill: str, artifacts: list[Path]) -> dict[str, Any]:
    if not artifacts:
        raise LedgerError("at least one final artifact is required")
    artifacts = [Path(path).resolve() for path in artifacts]
    if len(artifacts) != len(set(artifacts)):
        raise LedgerError("duplicate final artifact path")
    records = load_registry(run_dir)
    profile = load_profile(skill)
    upstream_findings, dependency_audits = dependency_findings(Path(run_dir), records, skill)
    source_ids = {
        record["record_id"]
        for record in effective_records(records).values()
        if record["record_type"] == "source"
    }
    current_claims = [
        record
        for record in effective_records(records).values()
        if record["record_type"] == "claim" and record["created_by_skill"] == skill
    ]
    required_source_ids = {
        resolve_record_id(records, source_id)
        for claim in current_claims
        for source_id in [*claim["support_source_ids"], *claim["counter_source_ids"]]
    }
    if not current_claims and "source" in profile["current_skill_record_types"]:
        required_source_ids.update(
            record["record_id"]
            for record in effective_records(records).values()
            if record["record_type"] == "source" and record["created_by_skill"] == skill
        )
    findings = [
        *audit_records(records, skill, profile),
        *upstream_findings,
    ]
    artifact_findings, artifact_fingerprints = validate_artifacts(
        profile,
        artifacts,
        source_ids,
        required_source_ids,
    )
    findings = apply_waivers([*findings, *artifact_findings], records, skill)
    if status_for(findings) == "partial" and not any(
        "研究状态：partial" in artifact_text(path)
        for path in artifacts
    ):
        add_finding(
            findings,
            "partial_label_missing",
            "block",
            "final artifact must contain 研究状态：partial",
        )
    result = {
        "schema_version": 1,
        "skill": skill,
        "ledger_sequence": len(records),
        "ledger_prefix_fingerprint": ledger_prefix_fingerprint(records),
        "artifacts": artifact_fingerprints,
        "dependency_audits": dependency_audits,
        "profile_fingerprint": profile_fingerprint(profile),
        "core_runtime_fingerprint": core_runtime_fingerprint(),
        "audited_at": utc_now(),
        "status": status_for(findings),
        "findings": findings,
    }
    write_audit_outputs(Path(run_dir), result)
    return result
```

Add the complete persistence functions:

```python
def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def audit_key(result: dict[str, Any]) -> str:
    identity = {
        "skill": result["skill"],
        "ledger_sequence": result["ledger_sequence"],
        "ledger_prefix_fingerprint": result["ledger_prefix_fingerprint"],
        "profile_fingerprint": result["profile_fingerprint"],
        "core_runtime_fingerprint": result["core_runtime_fingerprint"],
        "artifacts": sorted(
            (
                {"path": item["path"], "fingerprint": item["fingerprint"]}
                for item in result["artifacts"]
            ),
            key=lambda item: item["path"],
        ),
        "dependency_audit_keys": sorted(
            dependency["audit_key"]
            for dependency in result.get("dependency_audits", [])
        ),
    }
    return hashlib.sha256(canonical_bytes(identity)).hexdigest()


def saved_audit_is_valid(entry: dict[str, Any], records: list[dict[str, Any]]) -> bool:
    try:
        expected_key = audit_key(entry)
    except (KeyError, TypeError, ValueError):
        return False
    if not isinstance(entry.get("audit_key"), str) or entry["audit_key"] != expected_key:
        return False
    try:
        current_profile_fingerprint = profile_fingerprint(load_profile(str(entry["skill"])))
    except (KeyError, LedgerError):
        return False
    if entry.get("profile_fingerprint") != current_profile_fingerprint:
        return False
    if entry.get("core_runtime_fingerprint") != core_runtime_fingerprint():
        return False
    try:
        sequence = int(entry.get("ledger_sequence", 0))
    except (TypeError, ValueError):
        return False
    if sequence < 1 or sequence > len(records):
        return False
    if entry.get("ledger_prefix_fingerprint") != ledger_prefix_fingerprint(records[:sequence]):
        return False
    for artifact in entry.get("artifacts", []):
        path = Path(str(artifact.get("path", "")))
        try:
            valid_artifact = path.is_file() and artifact.get("fingerprint") == file_fingerprint(path)
        except OSError:
            valid_artifact = False
        if not valid_artifact:
            return False
    for dependency in entry.get("dependency_audits", []):
        if not isinstance(dependency, dict) or not saved_audit_is_valid(dependency, records):
            return False
    return True


def render_audit_markdown(entries: list[dict[str, Any]]) -> str:
    lines = [
        "# Research Audit",
        "",
        "| Skill | Ledger sequence | Status | Findings |",
        "| --- | ---: | --- | ---: |",
    ]
    for entry in entries:
        lines.append(
            f"| `{entry['skill']}` | {entry['ledger_sequence']} | "
            f"`{entry['status']}` | {len(entry['findings'])} |"
        )
    lines.append("")
    for entry in entries:
        lines.extend((f"## {entry['skill']} @ {entry['ledger_sequence']}", ""))
        lines.extend(
            (
                f"- Audited at: `{entry['audited_at']}`",
                f"- Ledger prefix: `{entry['ledger_prefix_fingerprint']}`",
                f"- Profile: `{entry['profile_fingerprint']}`",
                f"- Core runtime: `{entry['core_runtime_fingerprint']}`",
            )
        )
        for artifact in entry["artifacts"]:
            lines.append(f"- Artifact: `{artifact['path']}` `{artifact['fingerprint']}`")
        for dependency in entry.get("dependency_audits", []):
            lines.append(
                f"- Upstream: `{dependency['skill']}` `{dependency['status']}` "
                f"`{dependency['audit_key']}`"
            )
        lines.append("")
        if not entry["findings"]:
            lines.extend(("- No findings.", ""))
            continue
        for finding in entry["findings"]:
            lines.append(
                f"- `{finding['severity']}` `{finding['rule']}`: {finding['message']}"
            )
        lines.append("")
    return "\n".join(lines)


def write_audit_outputs(run_dir: Path, result: dict[str, Any]) -> None:
    with registry_lock(run_dir):
        records = load_registry(run_dir)
        json_path = Path(run_dir) / "audit.json"
        existing = {"schema_version": 1, "audits": []}
        if json_path.is_file():
            try:
                loaded = json.loads(json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                loaded = None
            if isinstance(loaded, dict) and isinstance(loaded.get("audits"), list):
                existing = loaded
        key = audit_key(result)
        candidate = {**result, "audit_key": key}
        if not saved_audit_is_valid(candidate, records):
            raise LedgerError("audit inputs changed while the audit was running")
        entries = [
            entry
            for entry in existing["audits"]
            if isinstance(entry, dict)
            and saved_audit_is_valid(entry, records)
            and entry["audit_key"] != key
        ]
        entries.append(candidate)
        entries.sort(key=lambda entry: (entry["ledger_sequence"], entry["skill"]))
        atomic_write_text(
            json_path,
            json.dumps({"schema_version": 1, "audits": entries}, ensure_ascii=False, indent=2) + "\n",
        )
        atomic_write_text(Path(run_dir) / "audit.md", render_audit_markdown(entries))


def write_waiver(
    run_dir: Path,
    *,
    skill: str,
    rule: str,
    reason: str,
    scope: str,
    approved_by: str,
    approved_at: str,
    residual_risk: str,
) -> None:
    load_profile(skill)
    records = load_registry(run_dir)
    if rule in NON_WAIVABLE_RULES:
        raise LedgerError(f"rule cannot be waived: {rule}")
    audit_path = Path(run_dir) / "audit.json"
    if not audit_path.is_file():
        raise LedgerError("waiver requires a current blocked audit")
    payload = json.loads(audit_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("audits"), list):
        raise LedgerError("invalid audit.json")
    entries = [
        entry
        for entry in payload.get("audits", [])
        if isinstance(entry, dict)
        and entry.get("skill") == skill
        and saved_audit_is_valid(entry, records)
    ]
    if not entries:
        raise LedgerError("waiver requires a current blocked audit")
    latest_sequence = max(int(entry["ledger_sequence"]) for entry in entries)
    latest = [entry for entry in entries if int(entry["ledger_sequence"]) == latest_sequence]
    if len(latest) != 1 or not any(
        finding.get("severity") == "block"
        and finding.get("rule") == rule
        and finding.get("message") == scope
        for finding in latest[0].get("findings", [])
    ):
        raise LedgerError("waiver must match one current blocked finding")
    used_ids = {record["record_id"] for record in records}
    suffix = len(records) + 1
    while f"W{suffix}" in used_ids:
        suffix += 1
    waiver = {
        "schema_version": 1,
        "record_id": f"W{suffix}",
        "record_type": "waiver",
        "created_at": approved_at,
        "actor": approved_by,
        "created_by_skill": skill,
        "rule": rule,
        "reason": reason,
        "scope": scope,
        "approved_by": approved_by,
        "approved_at": approved_at,
        "residual_risk": residual_risk,
    }
    append_records(run_dir, [waiver])
```

`write_waiver()` uses the normal append path; it never edits JSONL directly.

- [ ] **Step 7: Run the audit check**

Run:

```bash
python3 skills/jvc-research-core/scripts/check_package.py
```

Expected: `research core ledger checks passed` followed by successful audit assertions and exit `0`.

- [ ] **Step 8: Run Yao library gates**

Run:

```bash
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/validate_skill.py skills/jvc-research-core
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/resource_boundary_check.py skills/jvc-research-core --max-initial-tokens 1000
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/governance_check.py skills/jvc-research-core --require-manifest
```

Expected: all exit `0`; `SKILL.md` remains within the `1000`-token budget.

- [ ] **Step 9: Commit profiles and audit**

```bash
git add skills/jvc-research-core/profiles \
  skills/jvc-research-core/scripts/researchctl.py \
  skills/jvc-research-core/scripts/check_package.py
git commit -m "Add research evidence audit profiles"
```

### Task 4: Expose the fixed command-line contract

**Files:**

- Modify: `skills/jvc-research-core/scripts/researchctl.py`
- Modify: `skills/jvc-research-core/scripts/check_package.py`
- Modify: `skills/jvc-research-core/references/evidence-contract.md`

Command-Line Interface（CLI，命令行界面，指通过固定命令和参数调用本地程序的接口）behavior is the user-visible enforcement boundary.

- [ ] **Step 1: Add failing subprocess checks**

Add to `check_package.py`:

```python
import subprocess


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(Path(__file__).with_name("researchctl.py")), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )


def check_cli() -> None:
    help_result = run_cli("--help")
    assert help_result.returncode == 0, help_result.stderr
    for command in ("init", "record", "audit", "waive"):
        assert command in help_result.stdout
```

Call `check_cli()` from `__main__`.

- [ ] **Step 2: Run and verify the failure**

Run:

```bash
python3 skills/jvc-research-core/scripts/check_package.py
```

Expected: failure because `researchctl.py` has no argument parser.

- [ ] **Step 3: Implement the four subcommands**

Add:

```python
import argparse

EXIT_BY_STATUS = {"ready": 0, "partial": 10, "blocked": 20}


def read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise LedgerError(f"{path}: expected one JSON object")
    return payload


def read_jsonl_input(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise LedgerError(f"{path}:{line_number}: expected JSON object")
        records.append(payload)
    if not records:
        raise LedgerError(f"{path}: no records")
    return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintain and audit a jvc evidence registry.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create or resume a research ledger.")
    init.add_argument("--skill", required=True)
    init.add_argument("--run-dir", required=True, type=Path)
    init.add_argument("--scope-file", type=Path)
    init.add_argument("--resume", action="store_true")

    record_parser = subparsers.add_parser("record", help="Atomically append validated records.")
    record_parser.add_argument("--run-dir", required=True, type=Path)
    record_parser.add_argument("--input", required=True, type=Path)

    audit = subparsers.add_parser("audit", help="Audit one skill stage and its final artifacts.")
    audit.add_argument("--run-dir", required=True, type=Path)
    audit.add_argument("--skill", required=True)
    audit.add_argument("--artifact", required=True, action="append", type=Path)

    waive = subparsers.add_parser("waive", help="Append one human-approved business-evidence waiver.")
    waive.add_argument("--run-dir", required=True, type=Path)
    waive.add_argument("--skill", required=True)
    waive.add_argument("--rule", required=True)
    waive.add_argument("--reason", required=True)
    waive.add_argument("--scope", required=True)
    waive.add_argument("--approved-by", required=True)
    waive.add_argument("--residual-risk", required=True)
    return parser
```

- [ ] **Step 4: Implement command dispatch without prompt-only fallback**

Add:

```python
def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "init":
            load_profile(args.skill)
            if args.resume:
                if args.scope_file is not None:
                    raise LedgerError("--resume cannot be combined with --scope-file")
                load_registry(args.run_dir)
                print(f"research ledger resumed: {registry_path(args.run_dir)}")
                return 0
            if args.scope_file is None:
                raise LedgerError("--scope-file is required without --resume")
            init_registry(args.run_dir, args.skill, read_json_object(args.scope_file))
            print(f"research ledger initialized: {registry_path(args.run_dir)}")
            return 0
        if args.command == "record":
            records = read_jsonl_input(args.input)
            if any(record.get("record_type") == "waiver" for record in records):
                raise LedgerError("waiver records must use the waive command")
            for creating_skill in {str(record.get("created_by_skill", "")) for record in records}:
                load_profile(creating_skill)
            append_records(args.run_dir, records)
            print(f"research records appended: {args.input}")
            return 0
        if args.command == "waive":
            write_waiver(
                args.run_dir,
                skill=args.skill,
                rule=args.rule,
                reason=args.reason,
                scope=args.scope,
                approved_by=args.approved_by,
                approved_at=utc_now(),
                residual_risk=args.residual_risk,
            )
            print(f"research waiver appended: {args.rule}")
            return 0
        result = audit_run(args.run_dir, args.skill, args.artifact)
        print(json.dumps({"status": result["status"], "audit": str(Path(args.run_dir) / "audit.json")}, ensure_ascii=False))
        return EXIT_BY_STATUS[result["status"]]
    except (LedgerError, OSError, UnicodeError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"research core error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Test exact exit states**

Replace `check_cli()` with:

```python
def check_cli() -> None:
    help_result = run_cli("--help")
    assert help_result.returncode == 0, help_result.stderr
    for command in ("init", "record", "audit", "waive"):
        assert command in help_result.stdout

    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        run_dir, report = build_ready_fixture(root)
        audit_arguments = (
            "audit",
            "--run-dir",
            str(run_dir),
            "--skill",
            "jvc-track-research",
            "--artifact",
            str(report),
        )
        assert run_cli(*audit_arguments).returncode == 0
        add_gap(run_dir)
        report.write_text(
            "研究状态：partial\n" + report.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        assert run_cli(*audit_arguments).returncode == 10
        add_blocked_company_claim(run_dir)
        assert run_cli(*audit_arguments).returncode == 20

        malformed = root / "malformed.jsonl"
        malformed.write_text("{\n", encoding="utf-8")
        before = (run_dir / "evidence_registry.jsonl").read_bytes()
        failed = run_cli(
            "record",
            "--run-dir",
            str(run_dir),
            "--input",
            str(malformed),
        )
        assert failed.returncode == 1
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
```

Run:

```bash
python3 skills/jvc-research-core/scripts/check_package.py
python3 skills/jvc-research-core/scripts/researchctl.py --help
```

Expected: self-check exits `0`; help lists `init`, `record`, `audit`, and `waive`.

- [ ] **Step 6: Synchronize the reference commands**

Add exact examples for:

```bash
python3 "<core>/scripts/researchctl.py" init --skill "<skill>" --run-dir "<run-dir>" --scope-file "<scope.json>"
python3 "<core>/scripts/researchctl.py" init --skill "<skill>" --run-dir "<run-dir>" --resume
python3 "<core>/scripts/researchctl.py" record --run-dir "<run-dir>" --input "<records.jsonl>"
python3 "<core>/scripts/researchctl.py" audit --run-dir "<run-dir>" --skill "<skill>" --artifact "<artifact>"
python3 "<core>/scripts/researchctl.py" waive --run-dir "<run-dir>" --skill "<skill>" --rule "<rule>" --reason "<reason>" --scope "<scope>" --approved-by "<person>" --residual-risk "<risk>"
```

State explicitly that angle-bracket values are resolved inputs, not literal defaults.

- [ ] **Step 7: Commit the fixed command**

```bash
git add skills/jvc-research-core/scripts/researchctl.py \
  skills/jvc-research-core/scripts/check_package.py \
  skills/jvc-research-core/references/evidence-contract.md
git commit -m "Expose research core completion gate"
```

### Task 5: Integrate the existing skill prompts without rewriting their domain logic

**Files:**

- Modify: all twelve existing `skills/jvc-*/SKILL.md` files listed in the file map.
- Modify: `evals/trigger_cases.json`

- [ ] **Step 1: Reconfirm the overlapping frontmatter edits**

Run:

```bash
git diff -- skills/jvc-bear-case/SKILL.md \
  skills/jvc-bull-case/SKILL.md \
  skills/jvc-comps-dd/SKILL.md \
  skills/jvc-ic-memo/SKILL.md \
  skills/jvc-invoice-manager/SKILL.md \
  skills/jvc-knowledge-tree-builder/SKILL.md \
  skills/jvc-market-sizing/SKILL.md \
  skills/jvc-meeting-notes/SKILL.md \
  skills/jvc-prescreen/SKILL.md \
  skills/jvc-roi-modeler/SKILL.md \
  skills/jvc-talk-notes/SKILL.md \
  skills/jvc-track-research/SKILL.md
```

Expected: the previously observed Chinese descriptions, slash-command trigger phrases, `user_invocable: true`, and current version fields. Preserve the descriptions and `user_invocable` fields.

- [ ] **Step 2: Set versions deliberately**

Set `version: "2.0.0"` on the eleven core-integrated skills:

```text
jvc-bear-case
jvc-bull-case
jvc-comps-dd
jvc-ic-memo
jvc-knowledge-tree-builder
jvc-market-sizing
jvc-meeting-notes
jvc-prescreen
jvc-roi-modeler
jvc-talk-notes
jvc-track-research
```

Keep `jvc-invoice-manager` at `version: "1.0.0"` because its operational behavior is unchanged. Its existing `user_invocable: true` frontmatter update is intentionally adopted into the package.

- [ ] **Step 3: Add one compact mandatory core block to the eleven integrated skills**

Insert this section after each skill's input section or before its first execution step:

```markdown
## 2.0 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill <本 skill 名称> --run-dir <研究目录> --scope-file <scope.json>`。
2. 复用已有研究链时运行 `init --skill <本 skill 名称> --run-dir <研究目录> --resume`。
3. `scope`、问题、检索、来源、主张和更正只能通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，不得直接编辑 `evidence_registry.jsonl`。
4. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
5. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
6. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill <本 skill 名称> --artifact <最终产物>`；多文件产物重复传入 `--artifact`。
7. `ready` 才能称为完成；首次得到 `partial` 时先在标题和结论中写入 `研究状态：partial`，再重跑终审，只有当前产物得到退出状态 `10` 才能交付；`blocked` 只能交付证据缺口和下一步，不能形成受影响的判断；工具错误必须修复后重跑。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。
```

Replace `<本 skill 名称>` with the literal skill name in each file. The angle-bracket values for run directory, scope file, record batch, and artifact are documented runtime metavariables supplied by the user or resolved from the current task; no hard-coded default path is allowed.

- [ ] **Step 4: Add only the profile-specific evidence responsibility**

Append one sentence to each core block:

| Skill | Exact sentence |
| --- | --- |
| `jvc-meeting-notes` | `本 skill 登记逐字稿、用户随笔和纪要来源，区分受访者自述、用户观察和原始文本。` |
| `jvc-talk-notes` | `本 skill 登记逐字稿、用户随笔和问答纪要来源，区分受访者自述、用户观察和原始文本。` |
| `jvc-prescreen` | `本 skill 从已有本地来源登记初筛主张；未要求联网时不扩展来源宇宙。` |
| `jvc-bull-case` | `本 skill 复用已有来源，登记正向主张、反向证据和反证条件，不复制来源记录。` |
| `jvc-bear-case` | `本 skill 复用已有来源，登记反向问题、主张和可证伪条件，不把推测写成事实。` |
| `jvc-track-research` | `本 skill 必须登记问题、正向与反向检索、来源和主张，并执行独立来源审查。` |
| `jvc-comps-dd` | `本 skill 必须登记公司字段级主张、来源日期、估值或市值口径及反向证据。` |
| `jvc-market-sizing` | `本 skill 必须把外部事实、用户假设和模型估算分开登记。` |
| `jvc-knowledge-tree-builder` | `本 skill 把 source_manifest 来源映射进统一账本，并保持知识树节点与来源编号一致。` |
| `jvc-roi-modeler` | `本 skill 登记条款、预测和模型假设来源，保持已知条款与用户假设分离。` |
| `jvc-ic-memo` | `本 skill 只消费有效审查记录；新增事实必须先登记，不能在 memo 中补造来源。` |

Do not rewrite the rest of each domain prompt. Delete only a sentence that becomes an exact duplicate of this new block; retain domain-specific source hierarchy, milestone, formula, output, and prohibition rules.

- [ ] **Step 5: Make the invoice exclusion explicit**

Add:

```markdown
## 2.0 边界

本 skill 不接入 `jvc-research-core`，不创建投资证据账本，也不把发票、报销人或支付信息传入投资研究链。
```

- [ ] **Step 6: Strengthen deterministic contract signals**

For each of the eleven connected trigger cases in `evals/trigger_cases.json`, add these strings to `skill_contract_signals`:

```json
["2.0 证据内核", "researchctl.py", "ready", "partial", "blocked"]
```

For `invoice-operational-boundary`, add:

```json
["2.0 边界", "不接入 `jvc-research-core`"]
```

Do not change prompts, expected routes, near-neighbor explanations, or the no-route teaching case.

- [ ] **Step 7: Run the route/output fixture check**

Run:

```bash
python3 scripts/check-skill-evals.py
```

Expected: still `13 trigger cases, 12 output cases`; all new contract signals resolve.

- [ ] **Step 8: Review the prompt diff as one controlled rule group**

Run:

```bash
git diff --word-diff=plain -- skills/jvc-*/SKILL.md
```

Expected:

- existing descriptions and domain bodies are preserved;
- eleven versions are `2.0.0`;
- invoice remains `1.0.0`;
- no user-visible output format or slash command is renamed;
- only the core execution block, profile sentence, invoice boundary, and exact duplicate deletions appear.

- [ ] **Step 9: Commit all twelve intentionally adopted skill files**

```bash
git add skills/jvc-bear-case/SKILL.md \
  skills/jvc-bull-case/SKILL.md \
  skills/jvc-comps-dd/SKILL.md \
  skills/jvc-ic-memo/SKILL.md \
  skills/jvc-invoice-manager/SKILL.md \
  skills/jvc-knowledge-tree-builder/SKILL.md \
  skills/jvc-market-sizing/SKILL.md \
  skills/jvc-meeting-notes/SKILL.md \
  skills/jvc-prescreen/SKILL.md \
  skills/jvc-roi-modeler/SKILL.md \
  skills/jvc-talk-notes/SKILL.md \
  skills/jvc-track-research/SKILL.md \
  evals/trigger_cases.json
git commit -m "Route jvc research skills through evidence core"
```

### Task 6: Install the hidden core and extend suite governance

**Files:**

- Create: `scripts/check-research-core-install.py`
- Modify: `setup`
- Modify: `agents/interface.yaml`
- Modify: `manifest.json`
- Modify: `library/skill-registry.md`
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `scripts/check-skill-evals.py`
- Modify: `scripts/check-governance.py`
- Modify: `scripts/check-review-fixes.sh`
- Modify: `evals/output/cases.json`
- Modify: `reports/skill-ir.json`
- Modify: `security/network_policy.json`
- Modify: `security/permission_policy.json`

- [ ] **Step 1: Split user skills from support components in `setup`**

Replace the one `SKILLS` array with:

```bash
USER_SKILLS=(
  jvc-prescreen
  jvc-bull-case
  jvc-track-research
  jvc-knowledge-tree-builder
  jvc-comps-dd
  jvc-market-sizing
  jvc-roi-modeler
  jvc-bear-case
  jvc-ic-memo
  jvc-meeting-notes
  jvc-talk-notes
  jvc-invoice-manager
)

SUPPORT_COMPONENTS=(
  jvc-research-core
)

ALL_COMPONENTS=("${USER_SKILLS[@]}" "${SUPPORT_COMPONENTS[@]}")
```

Use `ALL_COMPONENTS` in every registration loop and registration count. Use `USER_SKILLS` only for the final `Available skills:` slash-command list. Print one separate line:

```bash
echo "Support: ${#SUPPORT_COMPONENTS[@]} hidden component"
```

Do not print `/jvc-research-core`.

- [ ] **Step 2: Write the failing install simulation**

Create:

```python
#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
USER_SKILLS = {
    "jvc-prescreen",
    "jvc-bull-case",
    "jvc-track-research",
    "jvc-knowledge-tree-builder",
    "jvc-comps-dd",
    "jvc-market-sizing",
    "jvc-roi-modeler",
    "jvc-bear-case",
    "jvc-ic-memo",
    "jvc-meeting-notes",
    "jvc-talk-notes",
    "jvc-invoice-manager",
}


def main() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        package = root / "jvc-analyst"
        home = root / "home"
        (home / ".codex").mkdir(parents=True)
        package.mkdir()
        shutil.copy2(ROOT / "setup", package / "setup")
        shutil.copytree(ROOT / "skills", package / "skills")
        result = subprocess.run(
            ["bash", str(package / "setup")],
            cwd=package,
            env={**os.environ, "HOME": str(home)},
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        installed = home / ".codex" / "skills"
        assert USER_SKILLS <= {path.name for path in installed.iterdir()}
        assert (installed / "jvc-research-core" / "scripts" / "researchctl.py").is_file()
        assert "  /jvc-research-core" not in result.stdout
        assert "Support: 1 hidden component" in result.stdout
    print("research core install simulation passed")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the install simulation**

Run:

```bash
python3 scripts/check-research-core-install.py
```

Expected: `research core install simulation passed`.

- [ ] **Step 4: Teach suite evals about hidden skills**

Add:

```python
def all_skill_names() -> set[str]:
    return {path.parent.name for path in (ROOT / "skills").glob("jvc-*/SKILL.md")}


def user_invocable_skill_names() -> set[str]:
    names = set()
    for path in (ROOT / "skills").glob("jvc-*/SKILL.md"):
        text = path.read_text(encoding="utf-8")
        if "user_invocable: false" not in text:
            names.add(path.parent.name)
    return names
```

Use `user_invocable_skill_names()` for trigger-route coverage. Use `all_skill_names()` for output coverage so the core must have a deterministic artifact case.

- [ ] **Step 5: Add the core output fixture assertion**

Add one output case to `evals/output/cases.json`:

```json
{
  "id": "research-core-audit-contract",
  "skill": "jvc-research-core",
  "artifact_family": "json_markdown_audit",
  "assertions": [
    {
      "type": "file_exists",
      "path": "skills/jvc-research-core/scripts/researchctl.py"
    },
    {
      "type": "contains",
      "path": "skills/jvc-research-core/SKILL.md",
      "text": "ready"
    },
    {
      "type": "contains",
      "path": "skills/jvc-research-core/SKILL.md",
      "text": "partial"
    },
    {
      "type": "contains",
      "path": "skills/jvc-research-core/SKILL.md",
      "text": "blocked"
    }
  ]
}
```

Do not reformat the entire one-line JSON file. Patch the smallest exact object boundary and validate the resulting JSON immediately.

- [ ] **Step 6: Update package metadata and registry**

Make these exact changes:

- `manifest.json`: version `2.0.0`, `updated_at` `2026-07-29`, add `"evidence ledger and deterministic audit"` to `output_contracts`.
- `agents/interface.yaml`: add `skills/jvc-research-core/SKILL.md` to activation paths and state that it is support-only.
- `library/skill-registry.md`: add a separate “Hidden support component” row; do not count it as a slash command.
- `README.md`: show `12 user skills + 1 hidden research core`, add the four fixed commands, the three statuses, and the fact that search remains agent-mediated.
- `CLAUDE.md`: add one rule that connected research skills cannot claim completion without a current core audit.

- [ ] **Step 7: Update security metadata without adding network permission**

In `security/network_policy.json`:

- keep `network_capable_scripts` empty;
- state that `researchctl.py` has no network code;
- retain agent-mediated web search notes.

In `security/permission_policy.json`:

- expand `file_read` to include scope, evidence ledger, profiles, and final artifacts;
- expand `file_write` to include registry and audit outputs at explicit run directories;
- expand `subprocess` to include local core checks;
- keep remote inline execution forbidden and retain the current expiry unless the owner explicitly changes it.

- [ ] **Step 8: Update governance checks**

Add to `check_interface()`:

```python
require_text("skills/jvc-research-core/SKILL.md", "user_invocable: false")
require_text("setup", "SUPPORT_COMPONENTS")
require_text("setup", "jvc-research-core")
```

Add to `check_security()`:

```python
require(not network.get("network_capable_scripts"), "research core must not add network-capable scripts")
```

In `check_skill_ir()`, continue requiring all skill directories, including the hidden core.

- [ ] **Step 9: Update Skill Intermediate Representation**

Skill Intermediate Representation（Skill IR，技能中间表示，用于跨平台描述 skill 工作、输出、脚本和失败模式）gets one new entry:

```json
{
  "name": "jvc-research-core",
  "job": "Maintain one append-only evidence registry and deterministically audit calling-skill artifacts.",
  "outputs": ["JSONL evidence registry", "JSON audit", "Markdown audit", "ready/partial/blocked status"],
  "near_neighbors": [],
  "scripts": [
    "skills/jvc-research-core/scripts/researchctl.py",
    "skills/jvc-research-core/scripts/check_package.py"
  ],
  "user_invocable": false,
  "failure_modes": [
    "Direct ledger edit",
    "Same-origin sources counted as independent",
    "Unverified company claim promoted to fact",
    "Stale artifact reported as audited",
    "Waiver produces ready"
  ]
}
```

- [ ] **Step 10: Extend the full local gate**

Add these commands to `scripts/check-review-fixes.sh` before governance:

```bash
python3 skills/jvc-research-core/scripts/check_package.py
python3 scripts/check-research-core-install.py
```

Add both new Python files to the existing `py_compile` list.

- [ ] **Step 11: Run the deterministic integration checks**

Run:

```bash
python3 skills/jvc-research-core/scripts/check_package.py
python3 scripts/check-research-core-install.py
python3 scripts/check-skill-evals.py
python3 scripts/check-governance.py
```

Expected:

- core and install checks pass;
- skill eval now passes `13 trigger cases, 13 output cases`;
- governance fails only on the expected stale trust-report hash until Task 8 refreshes generated reports.

- [ ] **Step 12: Commit install and governance source files**

```bash
git add setup README.md CLAUDE.md manifest.json agents/interface.yaml \
  library/skill-registry.md \
  scripts/check-research-core-install.py \
  scripts/check-skill-evals.py \
  scripts/check-governance.py \
  scripts/check-review-fixes.sh \
  evals/output/cases.json \
  reports/skill-ir.json \
  security/network_policy.json \
  security/permission_policy.json
git commit -m "Integrate research core package runtime"
```

### Task 7: Run real acceptance cases and build blind review evidence

**Files:**

- Create: `evals/research-core/cases.json`
- Create: `evals/research-core/output_cases.jsonl`
- Create: run artifacts under `evals/research-core/runs/<case-id>/`
- Create: blind-review files listed in the file map.
- Create: `reports/output_review_adjudication.json`
- Create: `reports/output_review_adjudication.md`

- [ ] **Step 1: Create the five acceptance contracts**

Create:

```json
{
  "schema_version": 1,
  "cases": [
    {
      "id": "local-interview-to-prescreen",
      "skill_chain": ["jvc-meeting-notes", "jvc-prescreen"],
      "input": "脱敏虚构工业视觉公司逐字稿、用户随笔和 deck 摘要",
      "expected_status": "ready",
      "must_prove": ["受访者自述与用户观察分离", "初筛主张可追溯"]
    },
    {
      "id": "glass-substrate-conflicting-public-sources",
      "skill_chain": ["jvc-track-research"],
      "input": "玻璃基板先进封装赛道，要求主动寻找量产良率与商业化相反证据",
      "expected_status": "ready",
      "must_prove": ["两类独立来源", "冲突口径保留", "反向检索", "停止条件"]
    },
    {
      "id": "market-model-fact-vs-assumption",
      "skill_chain": ["jvc-market-sizing"],
      "input": "工业视觉质检软件中国市场，给定用户渗透率假设",
      "expected_status": "ready",
      "must_prove": ["外部事实与用户假设分离", "模型估算可追溯"]
    },
    {
      "id": "audited-chain-to-ic-memo",
      "skill_chain": ["jvc-bull-case", "jvc-bear-case", "jvc-ic-memo"],
      "input": "复用前三类已审材料形成投决备忘录",
      "expected_status": "ready",
      "must_prove": ["前序审查仍有效", "新增事实先登记", "风险与反证保留"]
    },
    {
      "id": "missing-critical-commercial-proof",
      "skill_chain": ["jvc-track-research"],
      "input": "只有公司融资稿支持规模收入，且无独立客户或财务证据",
      "expected_status": "blocked",
      "must_prove": ["公司主张不升级为事实", "不能伪装成 ready"]
    }
  ]
}
```

- [ ] **Step 2: Execute the local and model cases through the real skill paths**

For every case:

1. place input files under `evals/research-core/runs/<case-id>/input/`;
2. run the named installed skill chain;
3. keep all temporary record-input files outside the canonical ledger;
4. save the final artifact, `evidence_registry.jsonl`, `audit.json`, and `audit.md`;
5. rerun audit after the final artifact is stable;
6. compare actual status with `expected_status`.

For the public cases, use current platform search tools and actual retrieved sources. Cite only sources actually opened. Store only minimal excerpts and metadata. Do not use a third-party search Application Programming Interface（API，应用程序编程接口，供程序调用外部服务的标准接口）or add a network script.

- [ ] **Step 3: Inspect the artifacts the user would consume**

Check:

- Markdown reports for source labels, unresolved conflicts, and narrowed conclusions;
- workbooks with the existing workbook validator and a manual spot-check of formulas and source sheets;
- generated interview documents with existing filename and format checks;
- `audit.md` for correct status and actionable findings;
- the negative case for exit `20`.

If any case fails for a domain-output problem, fix the relevant profile or skill once and rerun that case plus the deterministic gates. Do not weaken the common audit to force a pass.

- [ ] **Step 4: Produce two exact baseline/candidate comparisons**

Use the public track case and market-model case.

- Baseline: run the corresponding 1.0 skill text from commit `ebdaa5d`.
- Candidate: run the 2.0 skill plus core on the same input and date.
- Preserve both complete outputs without version labels inside `evals/research-core/output_cases.jsonl`.
- Assertions must cover factual accuracy, traceability, independent sources, conflict/counterevidence handling, calibration, and next-step usefulness.

Each JSONL row follows the Yao Output Eval contract and contains:

- stable `id`, exact fixed `prompt`, and relative `input_files`;
- the completed 1.0 artifact verbatim in `baseline_output`;
- the completed 2.0 artifact verbatim in `with_skill_output`;
- case-specific weighted `assertions`, including required and forbidden
  evidence behavior plus `failure_type`;
- `human_review.expected_winner` set to `with_skill`.

Build each row only after both artifacts exist, then parse every line with
`json.loads` before running the Yao evaluator. This file is execution evidence
and must not contain invented, abbreviated, or synthetic results.

- [ ] **Step 5: Generate the blind pack using the existing Yao script**

Run:

```bash
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/run_output_eval.py \
  --cases evals/research-core/output_cases.jsonl \
  --output-json reports/research-core-output-eval.json \
  --output-md reports/research-core-output-eval.md \
  --blind-pack-json reports/output_blind_review_pack.json \
  --blind-pack-md reports/output_blind_review_pack.md \
  --blind-answer-key-json reports/output_blind_answer_key.json
```

Expected:

- two blind pairs;
- no candidate regression in deterministic assertions;
- the Markdown pack hides which variant is 1.0 or 2.0.

- [ ] **Step 6: Prepare the reviewer-facing kit**

Run:

```bash
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/prepare_output_review_kit.py \
  --blind-pack-json reports/output_blind_review_pack.json \
  --blind-pack-md reports/output_blind_review_pack.md \
  --decisions reports/output_review_decisions.json \
  --output-json reports/output_review_kit.json \
  --output-md reports/output_review_kit.md \
  --output-html reports/output_review_kit.html \
  --write-template

python3 scripts/render-output-review-kit.py \
  --input reports/output_review_kit.json \
  --output reports/output_review_kit.html \
  --check
```

Expected:

- two cases with `awaiting-decision`;
- the answer key is not exposed in the kit;
- Markdown headings, lists, links, and tables render as reading views instead of source text;
- workbook cell dumps render as row-and-column grids;
- exact raw output remains available only inside a collapsed verification section.

- [ ] **Step 7: Pause for human blind review**

Ask the user to review `reports/output_review_kit.html` without opening `reports/output_blind_answer_key.json`. The reviewer must record:

- winner `A` or `B`;
- confidence from `0` to `1`;
- a reason grounded in the six approved quality dimensions.

Do not infer or fill the human decision. Release remains blocked until both decisions are complete.

- [ ] **Step 8: Rebuild the review kit with decisions**

After the user supplies decisions, update `reports/output_review_decisions.json` and rerun Step 6 without `--write-template`.

Then adjudicate only after the rebuilt kit reports both cases ready:

```bash
python3 -B /Users/justinjia/.agents/skills/yao-meta-skill/scripts/adjudicate_output_review.py \
  --blind-pack reports/output_blind_review_pack.json \
  --answer-key reports/output_blind_answer_key.json \
  --decisions reports/output_review_decisions.json \
  --output-json reports/output_review_adjudication.json \
  --output-md reports/output_review_adjudication.md
```

Expected:

- two `ready-for-adjudication` cases;
- no invalid or blank decisions;
- reviewer and review date recorded.
- two adjudicated judgments, no pending or invalid decisions;
- blind-review attestation true and `ready_for_human_evidence` true.

- [ ] **Step 9: Commit actual acceptance evidence**

```bash
git add evals/research-core \
  reports/research-core-output-eval.json \
  reports/research-core-output-eval.md \
  reports/output_blind_review_pack.json \
  reports/output_blind_review_pack.md \
  reports/output_blind_answer_key.json \
  reports/output_review_decisions.json \
  reports/output_review_kit.json \
  reports/output_review_kit.md \
  reports/output_review_kit.html \
  reports/output_review_adjudication.json \
  reports/output_review_adjudication.md \
  scripts/render-output-review-kit.py \
  docs/superpowers/plans/2026-07-29-jvc-analyst-2-0-research-core.md
git add -f \
  evals/research-core/runs/audited-chain-to-ic-memo/input \
  evals/research-core/runs/audited-chain-to-ic-memo/validation.log \
  evals/research-core/runs/glass-substrate-conflicting-public-sources/input \
  evals/research-core/runs/glass-substrate-conflicting-public-sources/validation.log \
  evals/research-core/runs/local-interview-to-prescreen/input \
  evals/research-core/runs/local-interview-to-prescreen/validation.log \
  evals/research-core/runs/market-model-fact-vs-assumption/input \
  evals/research-core/runs/market-model-fact-vs-assumption/validation.log \
  evals/research-core/runs/missing-critical-commercial-proof/input \
  evals/research-core/runs/missing-critical-commercial-proof/validation.log
git commit -m "Add research core acceptance evidence"
```

### Task 8: Refresh release evidence and pass the final gates

**Files:**

- Create: `reports/research-core-2.0-release.md`
- Create: `reports/jvc_skill_case_quality_2026-07-29.md`
- Modify: package reports listed in the file map.
- Modify: `docs/superpowers/specs/2026-07-29-jvc-analyst-2-0-research-core-design.md`
- Modify: `scripts/check-review-fixes.sh` to keep the stale-name check from treating a `/vc-analyst` filesystem path as a bare legacy name.
- Modify: this plan to preserve the reviewed Task 8 release boundary.

- [ ] **Step 1: Preserve the design clarification**

Confirm the design document includes:

- `created_by_skill`;
- `audit --skill`;
- ledger-prefix audit validity;
- later valid appends preserving prior audits;
- `record` as the only evidence write path.

Run:

```bash
git diff -- docs/superpowers/specs/2026-07-29-jvc-analyst-2-0-research-core-design.md
```

Expected: only the already reviewed cross-skill audit clarification and record-integrity additions.

- [ ] **Step 2: Write the new suite quality report**

Create `reports/jvc_skill_case_quality_2026-07-29.md` with:

- all twelve user skills plus hidden core;
- deterministic results;
- five real case results;
- two blind-review decisions;
- strongest and weakest outputs;
- remaining gaps;
- explicit separation between fixture evidence, model/tool execution evidence, and human review.

Do not overwrite the historical 2026-06-26 report.

- [ ] **Step 3: Update scorecards and Review Studio**

Update:

- `reports/output_quality_scorecard.md`: add core artifact family, real-case evidence, baseline delta, and blind-review state.
- `reports/route_scorecard.md`: keep thirteen trigger cases and state that the hidden core has no route.
- `reports/review-studio.json` and `.md`: mark a gate `pass` only when the actual evidence exists; keep warnings for any missing adapter permission probe or unrun platform.

No telemetry, review, or quality score may be invented.

- [ ] **Step 4: Update the trust report inventory**

Add:

```json
{"path": "skills/jvc-research-core/scripts/researchctl.py", "interface": "argparse", "help_surface": "--help", "capabilities": ["file_read", "file_write"]}
```

and:

```json
{"path": "skills/jvc-research-core/scripts/check_package.py", "interface": "self-check", "help_surface": "none", "capabilities": ["file_read", "file_write"]}
```

Also add `scripts/check-research-core-install.py` as a local temporary-directory check. State explicitly that no core script has network capability.

- [ ] **Step 5: Recompute the package fingerprint after all source files are final**

Run:

```bash
python3 scripts/check-governance.py
```

Expected: one trust-report hash mismatch showing the concrete new expected fingerprint.

Update that exact fingerprint in both `reports/trust_report.json` and `reports/trust_report.md`, update the review date and 2.0 script inventory, then rerun:

```bash
python3 scripts/check-governance.py
```

Expected: `governance assets passed` with the same fingerprint.

- [ ] **Step 6: Run every relevant local gate**

Run:

```bash
python3 skills/jvc-research-core/scripts/check_package.py
python3 scripts/check-research-core-install.py
python3 scripts/check-skill-evals.py
python3 scripts/check-docx-filename-rule.py
python3 scripts/check-docx-format-consistency.py
python3 scripts/check-docx-template-customization.py
bash scripts/check-excel-workbooks.sh
bash scripts/check-jvc-assets.sh
bash scripts/check-review-fixes.sh
git diff --check
```

Expected:

- all exit `0`;
- skill eval reports `13 trigger cases, 13 output cases`;
- no stale unprefixed slash commands;
- no source-contract hash mismatch;
- no generated `__pycache__` directory is staged.

- [ ] **Step 7: Re-run Yao library gates**

Run:

```bash
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/validate_skill.py skills/jvc-research-core
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/resource_boundary_check.py skills/jvc-research-core --max-initial-tokens 1000
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/governance_check.py skills/jvc-research-core --require-manifest
```

Expected: all exit `0`; no initial-load regression.

- [ ] **Step 8: Write the release report**

`reports/research-core-2.0-release.md` must state:

- exact commands and exit results;
- five case statuses;
- blind-review decisions and whether 2.0 won;
- package fingerprint;
- current date and source-access dates;
- unsupported platforms or missing runtime probes;
- invoice exclusion;
- independent `jvc-research-report` worktree exclusion;
- rollback boundary.

If blind review does not show a material evidence-quality improvement, do not label the package `2.0.0`; return to the smallest failed rule or profile and rerun only affected cases plus the full final gate.

- [ ] **Step 9: Stage only release files and inspect**

```bash
git add docs/superpowers/specs/2026-07-29-jvc-analyst-2-0-research-core-design.md \
  docs/superpowers/plans/2026-07-29-jvc-analyst-2-0-research-core.md \
  scripts/check-review-fixes.sh \
  reports/jvc_skill_case_quality_2026-07-29.md \
  reports/output_quality_scorecard.md \
  reports/route_scorecard.md \
  reports/review-studio.json \
  reports/review-studio.md \
  reports/trust_report.json \
  reports/trust_report.md \
  reports/research-core-2.0-release.md
git diff --cached --name-only
git diff --cached --check
```

Expected: only the listed design clarification, stale-name root-cause fix, plan update, and release evidence files.

- [ ] **Step 10: Commit the 2.0 release evidence**

```bash
git commit -m "Release jvc-analyst 2.0 research core"
```

- [ ] **Step 11: Verify the final repository boundary**

Run:

```bash
git log -8 --oneline --decorate
git status --short
git -C .worktrees/jvc-research-report status --short
```

Expected:

- implementation commits are visible in task order;
- only the pre-existing `.superpowers/` and `assets/xiaohongshu/jvc-track-research/` remain untracked unless the user separately changed something;
- the report worktree state matches Task 0, unless the user explicitly accepts a later external state change;
- no research input, private transcript, credential, or unreviewed blind decision is accidentally staged.

User override, 2026-07-30: `.worktrees/jvc-research-report` is currently absent
and unregistered. Justin asked not to restore it for this release. Keep it
excluded and do not treat its absence as a `2.0.0` handoff blocker.

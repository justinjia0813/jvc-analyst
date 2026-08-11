# Evidence Contract

## Engine boundary

Research Core only maintains the evidence ledger, resolves effective records through claim inheritance, and audits artifacts for the calling Skill. It does not select or run research Skills, interpret professional research, or advance a project. 它不得创建工作流阶段事件；研究级别升级、进入尽调、提交 IC（Investment Committee，投资决策委员会，负责审议投资项目）和生成干净终版仍由 `jvc-deal-flow` 的人工闸门控制。

`ready` means the configured evidence and artifact checks passed. `partial` means a narrowed artifact may be delivered only with explicit incompleteness. `blocked` means the affected judgment must stop at evidence gaps and next actions. None of the three states is a business-stage approval.

## Canonical files

- `evidence_registry.jsonl` is the only evidence source of truth.
- `audit.json` and `audit.md` are reproducible derivatives.
- Business reports, workbooks, and interview notes remain owned by the calling skill.

## Fixed commands and completion states

```bash
python3 "<core>/scripts/researchctl.py" init --skill "<skill>" --run-dir "<run-dir>" --scope-file "<scope.json>"
python3 "<core>/scripts/researchctl.py" init --skill "<skill>" --run-dir "<run-dir>" --resume
python3 "<core>/scripts/researchctl.py" record --run-dir "<run-dir>" --input "<records.jsonl>"
python3 "<core>/scripts/researchctl.py" audit --run-dir "<run-dir>" --skill "<skill>" --artifact "<artifact>"
python3 "<core>/scripts/researchctl.py" waive --run-dir "<run-dir>" --skill "<skill>" --rule "<rule>" --reason "<reason>" --scope "<scope>" --approved-by "<person>" --residual-risk "<risk>"
```

Values enclosed by `<...>` are placeholders for inputs already resolved by the caller; they are neither literal values nor defaults.
`audit` exits `0` for `ready`, `10` for `partial`, and `20` for `blocked`.
Command, input, validation, or tool errors exit `1` and are not replaced by a prompt-only fallback.

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
主张继承通过 `derived_from_claim_ids` 指向上游有效 Claim；上游更正或审查失效会沿绑定关系使相关下游审查失效，不复制或静默改写上游主张。
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
Later valid appends or corrections from other skills that are unrelated to the audit do not invalidate it merely by increasing the ledger sequence or correcting a record in the shared prefix. An audit is invalid until rerun when the audited skill appends a new effective research record or correction after its audit sequence; a waiver or audit binding related to one of its old blockers changes; or an artifact, profile, core runtime, or bound upstream audit changes. A bound upstream correction propagates through the upstream audit binding, and each relevant invalidation also invalidates affected downstream dependents.
A preliminary `partial` requires `研究状态：partial` in the final artifact and one rerun; otherwise the audit is `blocked`.

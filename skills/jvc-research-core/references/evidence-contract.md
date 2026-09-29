# Evidence Contract

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
`init`, `record`, and audit-index writes hold the same exclusive single-writer lock; a present lock fails closed and must not be removed until the recorded process is confirmed absent.

## Evidence rules

- Search must answer a registered question.
- No-result searches are evidence of search effort, not evidence of non-existence.
- High-priority questions must end as supported, refuted, or an explicit evidence gap.
- Profiles that require counter-search also require two latest distinct search rounds that no longer change the core judgment.
- Decision-critical third-party facts require distinct source classes, independence keys, publishers, locations, and evidence-packet fingerprints.
- Syndicated or same-origin reports count once.
- Company claims remain company claims until independently corroborated.
- Internal management interviews are `company-material`, not independent `expert-interview` evidence. Record the original speaker and relationship; document form and uploader do not change source identity.
- Decision-critical model estimates using company material or filings register their input claims separately and link `derived_from_claim_ids`. The core blocks an empty lineage for these estimates; nonempty lineage still needs review for input identity, completeness, importance, and meaning. Pure user-specified assumptions remain distinguishable from company evidence.
- A decision-critical model also follows effective input lineage: an unverified, refuted, or unresolved company input blocks the model even if that input was labeled less important. An intermediate model directly using company evidence also requires input lineage. This does not prove the lineage is complete or semantically appropriate; those checks remain the caller's responsibility.
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
Before status-label checks, the audit computes the substantive status from evidence, dependencies, and artifact integrity. A substantive `partial` or `blocked` requires the matching visible `研究状态：partial` or `研究状态：blocked` label; any explicit status label must match, including for `ready`. A missing or conflicting label blocks delivery and the finding states the expected label. Correct the label and conclusion boundaries, then rerun; relabeling cannot remove substantive blockers.
Market-sizing workbooks require an actual Excel formula in each of `top_down`, `bottom_up`, and `reconciliation`. The audit also rejects nontrivial literal model inputs, wrong-row reconciliation references, and conflicting result/formula calculations. Missing caches for distinct duplicate formulas require recalculation before comparison; missing inputs may remain blank with guarded formulas and explicit gaps. These are artifact integrity checks, not a formula engine or proof of units, business assumptions, input propagation, or visual quality. The caller still performs executable perturbation checks and inspects every rendered sheet.

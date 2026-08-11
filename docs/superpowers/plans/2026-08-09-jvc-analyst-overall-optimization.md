# jvc-analyst 工具包整体优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` in this session. Implement one task at a time, then run specification review and code-quality review before starting the next task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按 Priority 0–2（P0–P2，优先级 0–2，数字越小表示越优先）把工具包迁移到已确认的分类、总控/引擎边界、快速 Pre-Screen、赛道研究链、单表 Market Sizing、输出级接口和统一治理合同，同时保持 ROI Modeler 基线与 Investment Committee（IC，投资决策委员会，负责审议项目）Memo 人工审批边界不退化。

**Architecture:** Reuse the existing `jvc-deal-flow` as Flow and `jvc-research-core` as the evidence engine. Keep every research Skill independently invocable. Narrative artifacts use Markdown; formula-linked Market Sizing and Return on Investment（ROI，投资回报率，用于衡量回报相对投入资本的水平）Modeler use Comma-Separated Values（CSV，逗号分隔值，一种便于公式审计的文本表格格式）. Output Skills assemble audited upstream artifacts without silently researching new claims.

**Tech Stack:** Markdown Skill contracts, Python 3 standard library, shell package checks, existing Research Core profiles, JavaScript Object Notation（JSON，JavaScript 对象表示法，用于保存结构化夹具）fixtures, Mermaid diagrams, existing report renderer.

---

## Execution constraints

- Design authority: `docs/superpowers/specs/2026-08-09-jvc-analyst-overall-optimization-design.md`.
- Current workspace is already an isolated linked worktree on `feature/overall-promo`; do not create another worktree.
- Preserve all existing ROI Modeler edits and the untracked user file `roi-modeler-template.xlsx`; never edit, delete, move, or package that workbook.
- Do not commit, push, create remote issues, or perform any other remote write. Any commit language in a referenced workflow is not authorization.
- Use `apply_patch` for text-file edits. Do not overwrite unrelated dirty changes.
- New validator behavior follows test-driven development: add a failing runnable check, observe the expected failure, implement the minimum behavior, then rerun green.
- Pure documentation, fixture, profile, and registry edits do not require artificial unit tests, but must be covered by the nearest package or governance check.
- Every English abbreviation must be expanded on first use with English full name, Chinese full name, and a one-sentence explanation.
- Do not introduce a second orchestrator, evidence engine, database, compatibility framework, or generic Agent platform.
- Do not proceed from P0 to P1 or P1 to P2 until the batch verification commands pass.

## Baseline evidence

Before implementation began, the following commands ran successfully in the current worktree:

```bash
./scripts/check-prescreen-assets.sh
./scripts/check-track-research-assets.sh
./scripts/check-market-sizing-assets.sh
./scripts/check-comps-dd-assets.sh
./scripts/check-ic-memo-assets.sh
./scripts/check-roi-modeler-assets.sh
python3 skills/jvc-knowledge-tree-builder/scripts/check_package.py
python3 skills/jvc-research-report/scripts/check_package.py
python3 skills/jvc-deal-flow/scripts/check_package.py
python3 skills/jvc-research-core/scripts/check_package.py
python3 scripts/check-v3-foundation.py
python3 scripts/check-research-core-install.py
python3 scripts/check-skill-evals.py
python3 scripts/check-governance.py
./scripts/check-jvc-assets.sh
git diff --check
```

The baseline completed with exit code 0. This establishes that later failures are introduced by this plan unless the shared worktree changes concurrently.

## P0 — 架构、总控与快速筛选

### Task 1: Freeze taxonomy and the Flow / Research Core boundary

**Files:**

- Modify: `README.md`
- Modify: `library/skill-registry.md`
- Modify: `skills/jvc-deal-flow/SKILL.md`
- Modify: `skills/jvc-deal-flow/references/workflow-contract.md`
- Modify: `skills/jvc-research-core/SKILL.md`
- Modify: `skills/jvc-research-core/references/evidence-contract.md`
- Modify: `scripts/check-jvc-assets.sh`
- Test: `skills/jvc-deal-flow/scripts/check_package.py`
- Test: `skills/jvc-research-core/scripts/check_package.py`

- [ ] **Step 1: Add failing contract assertions**

Add assertions to the nearest existing package checks for:

- README headings for control/engine, track-level, project-level, output-level, and utility categories;
- Flow as the only project orchestrator, responsible for state, dependencies, minimum dispatch, reruns, and human gates;
- Research Core as a non-user-invocable evidence engine, responsible for ledger, inheritance, artifact audit, and research status;
- the dependency edges `Track Research → Knowledge Tree Builder`, `Track Research → Market Sizing`, project artifacts → IC Memo, and track artifacts → Research Report;
- the rule that Flow does not parse or recompute professional research and Research Core does not advance workflow stages;
- a `dealflowctl.py` package case where a new source event marks dependent artifacts as affected but does not emit an automatic Skill-run or stage-advance event.

Run:

```bash
./scripts/check-jvc-assets.sh
python3 skills/jvc-deal-flow/scripts/check_package.py
python3 skills/jvc-research-core/scripts/check_package.py
```

Expected: at least one new assertion fails because the taxonomy and boundary text are absent.

- [ ] **Step 2: Update the user-facing taxonomy**

Rewrite the README tool overview around these categories without adding a new Skill:

```text
控制与引擎：Flow / Research Core
赛道级：Track Research / Knowledge Tree Builder / Market Sizing
项目级：Pre-Screen / Bull Case / Bear Case / Comparable Companies Analysis / Due Diligence（Comps/DD，可比公司分析/尽职调查，指比较相似公司并验证项目事实与风险）/ Meeting Notes / Talk Notes / ROI Modeler
输出级：IC Memo / Research Report
日常工具：Invoice Manager
```

State the target output principle: narrative research uses Markdown, formula-linked models use CSV, office and publishing formats are explicit exceptions. During P0, keep the still-current Market Sizing and Comps/DD filenames truthful and mark their P1/P2 migration status; do not make README claim a format that has not been implemented. Remove the transitional status when the corresponding batch closes.

- [ ] **Step 3: Update Flow and Research Core contracts**

Add the target responsibility boundary and dependency view to both Skill contracts. Preserve:

- optional orchestrated-project mode;
- independent atomic Skill invocation;
- minimum sufficient research level;
- user approval for research-level upgrades, diligence entry, IC submission, and clean-final generation;
- `ready` / `partial` / `blocked` evidence semantics.

Do not change `dealflowctl.py` unless the new state-machine case proves the existing event model cannot express “affected but not rerun.” The desired result is a state/view assertion, not an embedded task runner.

- [ ] **Step 4: Make the checks green**

Run the three commands from Step 1. Expected: exit code 0.

- [ ] **Step 5: Self-review**

Search for wording that calls Research Core the orchestrator or describes Deal Flow as only an optional aside. Confirm the target distinction is consistent without deleting the rule that standalone Skill calls remain valid.

### Task 2: Rebuild Pre-Screen as a top-down Research Level 0（L0，研究级别 0，指约 30–60 分钟的资源筛选）artifact

**Files:**

- Modify: `skills/jvc-prescreen/SKILL.md`
- Modify: `templates/prescreen-template.md`
- Modify: `examples/prescreen-example.md`
- Create: `examples/prescreen-missing-data-example.md`
- Create: `skills/jvc-prescreen/scripts/validate_output.py`
- Create: `skills/jvc-prescreen/scripts/check_package.py`
- Modify: `skills/jvc-research-core/profiles/jvc-prescreen.json`
- Modify: `scripts/check-prescreen-assets.sh`
- Modify: `evals/output/cases.json`
- Modify only if trigger language changes: `evals/trigger_cases.json`

- [ ] **Step 1: Write the failing asset check**

Expand `scripts/check-prescreen-assets.sh` so it requires the Skill, template, and examples to cover:

- business model and upstream/downstream value chain;
- track validity and demand/payment evidence;
- top-down market range with formula, unit, source or assumption, and confidence;
- five-year company revenue in conservative/base/optimistic scenarios;
- valuation and transaction-condition return range;
- Multiple on Invested Capital（MOIC，投入资本倍数，指退出回款除以投入资本）and Internal Rate of Return（IRR，内部收益率，指使投资现金流净现值为零的年化收益率）definitions;
- `【第三方事实】`, `【公司自述】`, `【用户观察】`, `【模型估算】`, and `【未知/待验证】` labels;
- a missing-data example that narrows the result rather than inventing values;
- a runnable output validator with supported, no-market-anchor, no-transaction-term, and incompatible-unit fixtures.

Run:

```bash
python3 skills/jvc-prescreen/scripts/check_package.py
./scripts/check-prescreen-assets.sh
```

Expected: FAIL because the output validator is missing and the current seven-dimension contract prohibits estimates and lacks the new sections.

- [ ] **Step 2: Replace the conflicting behavior contract**

Update `jvc-prescreen` to version 4.0.0 and keep it at L0 by default. Replace “不得补估算值” with:

- estimates are allowed only as visible `【模型估算】` ranges;
- every estimate shows formula, units, source/user input/assumption, and confidence;
- no unsupported industry constant may enter the base case;
- missing customer/payer/product blocks the revenue and return calculation;
- missing valuation or investment amount produces a conditional sensitivity frame, not a point return;
- sufficient financing-round data routes to ROI Modeler instead of duplicating its full model;
- five-year revenue uses the one path closest to the business—market share, customers × revenue per customer, capacity × price, or another disclosed driver—rather than forcing market share on every project;
- no market anchor produces a formula and evidence gap only, not a market number;
- incompatible units are labeled `【未知/待验证】` and do not propagate downstream;
- estimates use decision-useful rounding and reject unsupported decimal precision.

The output remains `01-prescreen.md` and must not auto-create Research Level 1（L1，研究级别 1，指开始建立结构化研究假设）artifacts.

- [ ] **Step 3: Replace the template and examples**

Use the exact section order from the design:

```text
快筛结论
商业模式
上下游与价值分配
赛道有效性
市场规模粗算
五年收入情景
交易与回报粗算
风险、证伪条件与下一步
来源、假设与未知项
```

The primary example must include transparent arithmetic. The missing-data example must visibly omit numerical output that cannot be supported. Implement the minimum standard-library validator to check required sections, visible labels, formula/unit/source/confidence fields, conditional missing-data markers, and forbidden unsupported precision. It validates artifacts; it does not attempt to judge the investment conclusion.

- [ ] **Step 4: Update profile and output evaluation**

Keep the Research Core artifact kind as Markdown. Update the output fixture expectations so they assert the new sections, labels, conditional-failure behavior, and no final investment decision. Do not require Research Core initialization for L0.

- [ ] **Step 5: Run green checks**

```bash
python3 skills/jvc-prescreen/scripts/check_package.py
./scripts/check-prescreen-assets.sh
python3 scripts/check-skill-evals.py
python3 skills/jvc-research-core/scripts/check_package.py
git diff --check
```

Expected: all exit code 0.

### Task 3: Close P0 governance and verify the ROI baseline

**Files:**

- Modify: `manifest.json`
- Modify: `reports/skill-ir.json`
- Modify: `reports/trust_report.json`
- Modify: `reports/trust_report.md`
- Modify: `evals/trigger_cases.json`
- Modify: `evals/output/cases.json`
- Modify: `scripts/check-governance.py`
- Modify: `scripts/check-skill-evals.py`
- Modify as needed: `inspired-design.md`

- [ ] **Step 1: Add failing P0 governance assertions**

Require the registry and machine-readable contracts to describe:

- target classification;
- Flow / Research Core boundary;
- `jvc-prescreen` 4.0 Markdown output;
- existing `jvc-roi-modeler` 4.0 CSV output;
- output evaluations for both a supported and a missing-data Pre-Screen case.

Run:

```bash
python3 scripts/check-skill-evals.py
python3 scripts/check-governance.py
```

Expected: FAIL on the new assertions before governance assets are updated.

- [ ] **Step 2: Synchronize only P0 governance assets**

Update the files above without prematurely claiming P1/P2 output migrations. Add the Pre-Screen validator and package check to the trust inventory with their exact local file-read/write/subprocess behavior and no-network boundary. Refresh the trust report hash only after all P0 source-contract edits are finished:

```bash
python3 scripts/check-governance.py --write-hash
```

- [ ] **Step 3: Run the P0 batch gate**

```bash
./scripts/check-prescreen-assets.sh
./scripts/check-roi-modeler-assets.sh
python3 skills/jvc-deal-flow/scripts/check_package.py
python3 skills/jvc-research-core/scripts/check_package.py
python3 scripts/check-skill-evals.py
python3 scripts/check-governance.py
./scripts/check-jvc-assets.sh
git diff --check
```

Expected: all exit code 0. Do not start P1 until this gate is green.

## P1 — 赛道研究链与 Market Sizing

### Task 4: Create the Track Research → Knowledge Tree handoff and visual-first output

**Files:**

- Modify: `skills/jvc-track-research/SKILL.md`
- Modify: `templates/track-research-template.md`
- Modify: `examples/track-research-example.md`
- Modify: `skills/jvc-knowledge-tree-builder/SKILL.md`
- Modify: `skills/jvc-knowledge-tree-builder/README.md`
- Modify: `skills/jvc-knowledge-tree-builder/references/output-contract.md`
- Modify: `skills/jvc-knowledge-tree-builder/manifest.json`
- Create: `skills/jvc-knowledge-tree-builder/scripts/validate_output.py`
- Modify: `skills/jvc-knowledge-tree-builder/scripts/check_package.py`
- Create: `examples/knowledge-tree-example/knowledge_tree.md`
- Create: `examples/knowledge-tree-example/knowledge_graph.mmd`
- Create: `examples/knowledge-tree-example/nodes.json`
- Create: `examples/knowledge-tree-example/evidence_index.md`
- Create: `examples/knowledge-tree-example/open_questions.md`
- Modify: `scripts/check-track-research-assets.sh`
- Modify: `skills/jvc-research-core/profiles/jvc-track-research.json`
- Modify: `skills/jvc-research-core/profiles/jvc-knowledge-tree-builder.json`

- [ ] **Step 1: Write failing checks for the handoff and validator**

In the Track asset check require a handoff block containing root question, branches, entities/relations, source identifiers, effective claim identifiers, Market Sizing variables with units and data gaps, and open questions.

In `check_package.py`, create temporary valid and invalid five-file knowledge packages. The invalid cases must include:

- no Mermaid block in `knowledge_tree.md`;
- duplicate node identifier;
- missing parent;
- parent cycle;
- isolated node that is neither the root nor an explicit open question;
- missing evidence mapping for a claimed relation;
- Mermaid syntax that fails a real local render.

Run:

```bash
./scripts/check-track-research-assets.sh
python3 skills/jvc-knowledge-tree-builder/scripts/check_package.py
```

Expected: FAIL because the handoff and `validate_output.py` do not exist.

- [ ] **Step 2: Implement the minimum output validator**

Use Python standard library only. Validate the existing five-file package without adding a sixth artifact:

- `knowledge_tree.md` contains a Mermaid diagram near the beginning;
- `knowledge_graph.mmd` contains a supported graph declaration;
- `nodes.json` contains unique node identifiers, valid parents, and no parent cycles;
- evidence-bearing nodes and relations have a visible pointer or explicit gap;
- required files exist and are non-empty.

Return non-zero with actionable messages. Keep the structural validator in the Python standard library and do not create a generic graph library.

The package check must also use the existing local Quarto renderer to render the valid tracked `knowledge_tree.md` to Portable Document Format（PDF，可移植文档格式，用于保持固定版式）and require an intentionally malformed Mermaid fixture to fail rendering. A missing renderer is a failed visual gate, not a silent skip. Convert the valid PDF page to an image with existing Poppler tooling and inspect it with `view_image` for layout, cropping, spacing, missing labels, and consistency.

- [ ] **Step 3: Update both Skill contracts**

Within the Track Research → Knowledge Tree chain, Track Research remains the only owner of the first complete web-based sector study and `tracks/{track-slug}/landscape.md` remains the authoritative narrative. This does not prohibit Pre-Screen, Market Sizing, or Comps/DD from using task-specific public research. Knowledge Tree Builder consumes the Track artifact plus the Research Core ledger and local sources. Make `knowledge_tree.md` the visual-first user artifact while preserving the other four outputs for reuse and audit.

- [ ] **Step 4: Update templates, example, profiles, and package manifest**

Keep output names unchanged. Add the validator invocation before Research Core audit. Preserve source inheritance through `derived_from_claim_ids`; do not duplicate Track Research claims as new unlinked facts. Change the Knowledge Tree profile so it requires an effective source in the shared ledger but does not force the Knowledge Tree Skill to create a duplicate current-skill source record. State that upstream changes only mark affected nodes, relations, and open questions; execution of the minimum update still requires user approval.

- [ ] **Step 5: Run green checks**

```bash
./scripts/check-track-research-assets.sh
python3 skills/jvc-knowledge-tree-builder/scripts/check_package.py
python3 skills/jvc-research-core/scripts/check_package.py
git diff --check
```

Expected: all exit code 0.

### Task 5: Migrate Market Sizing from Excel to one auditable CSV

**Files:**

- Modify: `skills/jvc-market-sizing/SKILL.md`
- Create: `skills/jvc-market-sizing/references/model-contract.md`
- Create: `skills/jvc-market-sizing/scripts/validate_csv.py`
- Create: `skills/jvc-market-sizing/scripts/check_package.py`
- Create: `templates/market-sizing-template.csv`
- Modify: `templates/market-sizing-template.md`
- Create: `examples/market-sizing-example.csv`
- Modify: `examples/market-sizing-example.md`
- Modify: `skills/jvc-research-core/profiles/jvc-market-sizing.json`
- Modify: `scripts/check-market-sizing-assets.sh`
- Modify: `scripts/check-excel-workbooks.sh`
- Modify: `scripts/check-jvc-assets.sh`

- [ ] **Step 1: Write the failing package check**

Create `check_package.py` first. It must run the future validator against a valid fixture and invalid fixtures for:

- wrong header;
- non-Unicode Transformation Format 8-bit（UTF-8，八位 Unicode 转换格式，用于统一文本编码）input;
- missing one of the six sections;
- duplicate `row_id`;
- unknown source identifier;
- missing unit or year on a model row;
- scenario cell that is neither numeric nor a formula;
- malformed formula;
- missing Top-down / Bottom-up reconciliation;
- missing orthogonality disclosure;
- a key summary formula that does not reference declared inputs;
- conservative/base/optimistic ordering that is reversed without a disclosed business explanation;
- `confidence` outside the contract's fixed enumeration.

Run:

```bash
python3 skills/jvc-market-sizing/scripts/check_package.py
```

Expected: FAIL because `validate_csv.py` is missing.

- [ ] **Step 2: Implement the CSV validator**

Use this exact header:

```text
section,row_id,item,year,unit,conservative,base,optimistic,source_or_formula,confidence,notes
```

Allow only these sections:

```text
assumptions
top_down
bottom_up
reconciliation
orthogonality_check
sources
```

Use Python standard library only. Validate UTF-8 input, structure, numeric/formula cells, source references, units, years, scenario ordering with an explicit-note exception, fixed confidence values, reconciliation presence, and orthogonality disclosure. Do not implement a spreadsheet calculation engine; validate formula syntax and declared row references, while numeric fixtures prove the expected arithmetic separately.

- [ ] **Step 3: Replace the Skill output contract and template**

Update `jvc-market-sizing` to version 4.0.0, output `market-sizing.csv`, retain Top-down / Bottom-up / reconciliation / orthogonality logic, and invoke `validate_csv.py` before Research Core audit. Change the profile artifact kind from `xlsx` to `csv` and allowed suffix to `.csv`.

`templates/market-sizing-template.md` becomes the human-readable model contract, not a second data template. `templates/market-sizing-template.csv` is the sole active data template.

- [ ] **Step 4: Replace active examples and Excel checks**

Create a formula-bearing CSV example and update the Markdown walkthrough. Remove Market Sizing from `check-excel-workbooks.sh`; leave the old workbook only as an explicitly non-authoritative historical fixture if binary deletion is impractical, and remove every active contract reference to it.

- [ ] **Step 5: Run green checks**

```bash
python3 skills/jvc-market-sizing/scripts/check_package.py
./scripts/check-market-sizing-assets.sh
./scripts/check-excel-workbooks.sh
python3 skills/jvc-research-core/scripts/check_package.py
git diff --check
```

Expected: all exit code 0.

### Task 6: Close the P1 integration gate

**Files:**

- Modify: `skills/jvc-deal-flow/references/workflow-contract.md`
- Modify: `library/skill-registry.md`
- Modify: `README.md`
- Modify: `manifest.json`
- Modify: `reports/skill-ir.json`
- Modify: `reports/trust_report.json`
- Modify: `reports/trust_report.md`
- Modify: `evals/output/cases.json`
- Modify: `evals/research-core/cases.json`
- Modify: `evals/research-core/output_cases.jsonl`
- Create: `evals/research-core/baselines/industrial_vision_software_market_20260729.csv`
- Create: `evals/research-core/candidates/industrial_vision_software_market_20260729.csv`
- Create: `evals/research-core/runs/market-model-fact-vs-assumption/industrial_vision_software_market_20260729.csv`
- Modify: `evals/research-core/runs/market-model-fact-vs-assumption/evidence_registry.jsonl`
- Modify: `evals/research-core/runs/market-model-fact-vs-assumption/audit.json`
- Modify: `evals/research-core/runs/market-model-fact-vs-assumption/audit.md`
- Modify: `scripts/check-governance.py`
- Modify: `scripts/check-skill-evals.py`

- [ ] **Step 1: Add failing integration assertions**

Require all active contracts to agree on:

- `landscape.md` → five-file knowledge package;
- visual-first `knowledge_tree.md`;
- `market-sizing.csv` as the sole active Market Sizing model;
- the Knowledge Tree and Market Sizing validators;
- Flow impact marking without automatic rerun.
- active Research Core evaluation cases use CSV rather than the former workbook cell dump.

Run the relevant eval and governance checks and observe the expected failure.

- [ ] **Step 2: Synchronize P1 governance assets**

Update only the now-implemented P1 contracts. Migrate the active Market Sizing baseline, candidate, run artifact, evidence pointer, audit result, case index, and output case to CSV; old workbook and cell-dump files may remain only as clearly unreferenced historical fixtures. Add new scripts to the trust inventory with their actual capabilities. Do not claim P2 migrations yet. Refresh the source-contract hash after all edits.

- [ ] **Step 3: Run the P1 batch gate**

```bash
./scripts/check-track-research-assets.sh
python3 skills/jvc-knowledge-tree-builder/scripts/check_package.py
python3 skills/jvc-market-sizing/scripts/check_package.py
./scripts/check-market-sizing-assets.sh
./scripts/check-excel-workbooks.sh
python3 skills/jvc-deal-flow/scripts/check_package.py
python3 skills/jvc-research-core/scripts/check_package.py
python3 scripts/check-skill-evals.py
python3 scripts/check-governance.py
./scripts/check-jvc-assets.sh
git diff --check
```

Expected: all exit code 0. Do not start P2 until this gate is green.

## P2 — 输出级接口与全仓治理

### Task 7: Migrate Comps/DD to a Markdown primary artifact

**Files:**

- Modify: `skills/jvc-comps-dd/SKILL.md`
- Modify: `templates/comps-dd-template.md`
- Modify: `examples/comps-dd-example.md`
- Modify: `skills/jvc-research-core/profiles/jvc-comps-dd.json`
- Modify: `scripts/check-comps-dd-assets.sh`
- Modify: `scripts/check-excel-workbooks.sh`
- Modify: `scripts/check-jvc-assets.sh`
- Modify: `evals/output/cases.json`

- [ ] **Step 1: Add failing Markdown contract assertions**

Require the Skill, template, example, profile, and output evaluation to agree on `03-comps-dd.md`, with sections for scope, company segmentation, comparable metrics, target-vs-comparable analysis, upstream/downstream, overseas benchmarks, source index, coverage gaps, and next diligence actions.

Run:

```bash
./scripts/check-comps-dd-assets.sh
python3 scripts/check-skill-evals.py
```

Expected: FAIL because active contracts still require an Excel workbook.

- [ ] **Step 2: Replace the output contract**

Update the Skill to a Markdown primary artifact. Preserve source-backed comparison and counter-search requirements. Do not add formulas or a CSV attachment unless a real example cannot be represented legibly in Markdown.

Change the Research Core profile to Markdown, remove Comps/DD from the active workbook check, and remove every active `generate-workbook.py` / `validate-workbook.py` requirement for this Skill.

- [ ] **Step 3: Run green checks**

```bash
./scripts/check-comps-dd-assets.sh
./scripts/check-excel-workbooks.sh
python3 scripts/check-skill-evals.py
python3 skills/jvc-research-core/scripts/check_package.py
git diff --check
```

Expected: all exit code 0.

### Task 8: Make Research Report an audited output assembler and update IC inputs

**Files:**

- Modify: `skills/jvc-research-report/SKILL.md`
- Modify: `skills/jvc-research-report/templates/industry-report.md`
- Modify: `skills/jvc-research-report/references/output-contract.md`
- Modify: `skills/jvc-research-report/scripts/check_package.py`
- Create: `skills/jvc-research-report/scripts/validate_assembly.py`
- Modify: `skills/jvc-research-report/manifest.json`
- Modify: `skills/jvc-research-report/agents/interface.yaml`
- Modify: `skills/jvc-research-report/evals/semantic_config.json`
- Modify: `skills/jvc-research-report/evals/trigger_cases.json`
- Create: `skills/jvc-research-core/profiles/jvc-research-report.json`
- Modify: `skills/jvc-research-core/manifest.json`
- Create: `examples/research-report-example/research-report.md`
- Remove or demote: `examples/research-report-example/report.md`
- Modify: `skills/jvc-ic-memo/SKILL.md`
- Modify: `skills/jvc-ic-memo/references/ic-memo-template.md`
- Modify: `skills/jvc-deal-flow/references/workflow-contract.md`
- Modify: `scripts/check-ic-memo-assets.sh`

- [ ] **Step 1: Add failing package and interface checks**

Require Research Report to support two stages:

1. assembly of `research-report.md` from Track Research, Knowledge Tree, Market Sizing, and optional Comps/DD;
2. existing validation and rendering of the canonical Markdown.

Require assembly to preserve source identifiers, inherit upstream claims, expose coverage gaps, and forbid web research or new facts. Require direct publish mode when a complete canonical Markdown file already exists.

Extend `check_package.py` before implementing `validate_assembly.py`. Build temporary upstream artifacts and assert that a faithful assembly passes while an assembly with a new source identifier, new factual number, or unsupported claim marker fails. The check must compare actual upstream content with the candidate report; string-presence checks against a static fixture are insufficient.

Require IC Memo input mapping to use `03-comps-dd.md`, `market-sizing.csv`, and `05-roi-modeler.csv` while preserving the pre-review → explicit user approval → clean-final gate.

Run:

```bash
python3 skills/jvc-research-report/scripts/check_package.py
./scripts/check-ic-memo-assets.sh
```

Expected: FAIL on the new assembly and input-map assertions.

- [ ] **Step 2: Update Research Report without replacing the renderer**

Keep `build_report.py` as the existing publishing implementation. Implement a small read-only standard-library `validate_assembly.py` that accepts the upstream artifacts and candidate report, then checks source-identifier inheritance, normalized factual-number inheritance, unsupported internal labels, and visible coverage gaps. Reuse the existing IC final validator's number-normalization behavior where it can be shared without changing IC semantics; do not create a general document framework.

Update the Skill contract, interface, Skill-local evaluations, and template so the agent writes `research-report.md` from audited upstream artifacts, runs the assembly validator, and only then calls the renderer. Add a Markdown Research Core profile for the canonical source artifact. Do not make the renderer rewrite content or access the network.

- [ ] **Step 3: Update IC Memo inputs and preserve the approval gate**

Replace active workbook mappings with the new Markdown / CSV artifacts. Do not relax `validate_final.py`, `check_package.py`, `ready` semantics, or explicit user approval.

- [ ] **Step 4: Run green checks**

```bash
python3 skills/jvc-research-report/scripts/check_package.py
./scripts/check-ic-memo-assets.sh
python3 skills/jvc-ic-memo/scripts/check_package.py
python3 skills/jvc-research-core/scripts/check_package.py
python3 scripts/check-research-core-install.py
git diff --check
```

Expected: all exit code 0. Render the tracked `research-report.md` to PDF, convert all pages to images, and inspect them with `view_image` for layout, cropping, spacing, missing content, Mermaid or image failures, and visual consistency before closing the task.

### Task 9: Final governance, adversarial evaluation, and completion audit

**Files:**

- Modify: `README.md`
- Modify: `CLAUDE.md` only if an active old output contract remains
- Modify: `library/skill-registry.md`
- Modify: `manifest.json`
- Modify: `reports/skill-ir.json`
- Modify: `reports/trust_report.json`
- Modify: `reports/trust_report.md`
- Modify: `reports/review-studio.json`
- Modify: `reports/review-studio.md`
- Modify: `reports/output_quality_scorecard.md`
- Modify or explicitly archive: `reports/research-core-output-eval.json`
- Modify or explicitly archive: `reports/research-core-output-eval.md`
- Modify or explicitly archive: `reports/output_blind_review_pack.json`
- Modify or explicitly archive: `reports/output_blind_review_pack.md`
- Modify or explicitly archive: `reports/output_blind_answer_key.json`
- Modify or explicitly archive: `reports/output_review_kit.json`
- Modify or explicitly archive: `reports/output_review_kit.md`
- Modify or explicitly archive: `reports/output_review_kit.html`
- Modify or explicitly archive: `reports/output_review_adjudication.json`
- Modify or explicitly archive: `reports/output_review_adjudication.md`
- Modify or explicitly archive: `reports/output_review_decisions.json`
- Modify: `security/permission_policy.json`
- Modify: `evals/trigger_cases.json`
- Modify: `evals/output/cases.json`
- Modify: `evals/research-core/cases.json`
- Modify: `evals/research-core/output_cases.jsonl`
- Modify: `scripts/check-governance.py`
- Modify: `scripts/check-skill-evals.py`
- Modify: `scripts/check-jvc-assets.sh`
- Modify: `inspired-design.md`

- [ ] **Step 1: Add final consistency assertions**

Require every active user-facing and machine-readable contract to agree on:

- categories and Flow / Research Core roles;
- Pre-Screen Markdown behavior;
- visual-first five-file knowledge package;
- Market Sizing and ROI CSV outputs;
- Comps/DD Markdown output;
- Research Report canonical Markdown plus rendered outputs;
- IC Memo review/final sequence;
- office and invoice exceptions.

Add adversarial output fixtures for unsupported Pre-Screen estimates, missing Market Sizing source rows, broken knowledge relationships, Research Report adding a new number, and IC Memo clean-final leakage where the existing test surface supports them.

Update Review Studio, the output quality scorecard, and the permission policy unconditionally: they currently enumerate old Research Report, Excel, and file-write boundaries. The permission policy must describe CSV model writes without broadening network or external-write authority.

Inspect every derived output-evaluation and blind-review report listed in the file map. If it can be deterministically regenerated from the new active CSV cases without inventing a human judgment, regenerate it. Otherwise preserve the recorded result, add an explicit historical-legacy-workbook status, and remove it from Review Studio and other active governance evidence. A historical report must never be cited as proof that the new CSV contract passed.

- [ ] **Step 2: Remove active legacy references**

Use repository-wide search. No active contract may still claim:

- Market Sizing outputs Excel;
- Comps/DD outputs Excel;
- Research Report only formats a prewritten report and cannot assemble upstream artifacts;
- Knowledge Tree Builder's primary human result is a separate non-visual tree;
- Research Core is the project orchestrator.

Historical design files and clearly labeled legacy binary fixtures may retain historical wording; active README, Skill, interface, template, example, profile, manifest, registry, evaluation, security, report, and check files may not. Encode this active-path set in the governance check so the negative search is repeatable rather than a one-time manual grep.

- [ ] **Step 3: Refresh governance evidence**

Update trust inventory for all new local scripts with exact interfaces, capabilities, dependency notes, and no-network behavior. Then run:

```bash
python3 scripts/check-governance.py --write-hash
```

- [ ] **Step 4: Run full verification**

```bash
python3 skills/jvc-prescreen/scripts/check_package.py
./scripts/check-prescreen-assets.sh
./scripts/check-track-research-assets.sh
python3 skills/jvc-knowledge-tree-builder/scripts/check_package.py
python3 skills/jvc-market-sizing/scripts/check_package.py
./scripts/check-market-sizing-assets.sh
./scripts/check-comps-dd-assets.sh
./scripts/check-roi-modeler-assets.sh
./scripts/check-ic-memo-assets.sh
python3 skills/jvc-research-report/scripts/check_package.py
python3 skills/jvc-ic-memo/scripts/check_package.py
python3 skills/jvc-deal-flow/scripts/check_package.py
python3 skills/jvc-research-core/scripts/check_package.py
python3 scripts/check-v3-foundation.py
python3 scripts/check-research-core-install.py
./scripts/check-excel-workbooks.sh
python3 scripts/check-skill-evals.py
python3 scripts/check-governance.py
./scripts/check-jvc-assets.sh
./scripts/check-bull-case-assets.sh
./scripts/check-bear-case-assets.sh
./scripts/check-talk-notes-assets.sh
./scripts/check-review-fixes.sh
python3 scripts/check-docx-template-customization.py
python3 scripts/check-docx-format-consistency.py
python3 scripts/check-docx-filename-rule.py
git diff --check
git status --short --untracked-files=all
git clean -ndX
```

Expected: all functional and governance commands exit 0. Compare the final status line by line with the complete plan file map and the recorded pre-existing ROI changes; the untouched `roi-modeler-template.xlsx` is allowed, but an unplanned tracked, untracked, or ignored generated artifact is not. `git clean -ndX` is dry-run evidence only and must not be followed by a destructive clean command.

Render the tracked knowledge-tree example and Research Report to PDF, convert every page to images, and inspect them with `view_image`. Record the inspected paths and verify layout, cropping, spacing, missing labels/content, diagram rendering, and cross-page consistency. Automated text checks do not replace this visual gate.

- [ ] **Step 5: Requirement-by-requirement completion audit**

Read the design's §15 completion standard and map each item to current files and fresh command output. Treat missing, indirect, or outdated evidence as incomplete. Do not mark the overall goal complete until every item is proven.

## Review protocol for every task

1. Implementer self-reviews the actual diff and reports `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
2. A fresh specification reviewer compares the diff only against the full task text and design authority. Any missing or extra behavior returns to the implementer.
3. After specification approval, a fresh code-quality reviewer checks correctness, minimality, regression risk, tests, and unrelated edits. Important findings return to the implementer.
4. The primary agent independently inspects `git diff`, reruns the task verification, and only then marks the task complete.
5. No agent commits or pushes.

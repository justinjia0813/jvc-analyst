# JVC 投资决策备忘录预审版与终版实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 `/jvc-ic-memo` 先生成经过审查的 Markdown 预审版，并且只在用户明确批准后，发布供 IC（Investment Committee，投资决策委员会，负责审议投资项目）成员阅读的干净 Markdown 终版。

**Architecture:** Keep one skill and one self-contained template. The existing research core audits only `06-ic-memo-review.md`; a new standard-library validator checks the approved final candidate for leaked evidence markers and page references（页码引用）, empty sections, malformed Markdown, and numbers absent from the review before `06-ic-memo.md` is published. Existing `ic_review` deal-flow gating supplies the orchestrated-project approval boundary, so the deal-flow state machine and research core do not change.

**Tech Stack:** Markdown skill contracts, Python 3 standard library, existing shell/JSON（JavaScript Object Notation，JavaScript 对象表示法，用于保存结构化测试夹具）fixture checks, existing `jvc-research-core`, existing `jvc-deal-flow` gate.

---

## Execution constraints

- The approved design is `docs/superpowers/specs/2026-08-08-jvc-ic-memo-review-final-design.md`.
- Do not change `skills/jvc-research-core/` or `skills/jvc-deal-flow/scripts/dealflowctl.py`; their existing interfaces already cover this design.
- Do not add a Markdown generator or a second skill. The agent writes both artifacts; the new script validates only.
- Do not add Quarto configuration or styling. Quarto owns HTML (HyperText Markup Language, 超文本标记语言，用于浏览器呈现) rendering after this workflow.
- 如果已有终版存在而新候选失败，必须保留已有终版；校验器和 skill 都不得覆盖它。
- Commit steps below are checkpoints, not authorization. Skip every commit unless the user explicitly authorizes local commits; never push without separate authorization.

## File map

**Create**

- `skills/jvc-ic-memo/scripts/validate_final.py` — read-only final Markdown validator.
- `skills/jvc-ic-memo/scripts/check_package.py` — runnable standard-library regression check for the validator.
- `skills/jvc-ic-memo/references/ic-memo-template.md` — the sole installed template authority, moved from the repository-level template path.
- `examples/ic-memo-final-example.md` — compact clean-final example derived from the review example.

**Modify**

- `skills/jvc-ic-memo/SKILL.md` — v5 single-skill, two-stage workflow and output contract.
- `scripts/check-jvc-assets.sh` — package/path/contract checks for the IC memo skill.
- `examples/ic-memo-example.md` — identify the existing evidence-rich fixture as the pre-review example.
- `evals/trigger_cases.json` — route contract signals for pre-review, approval, and clean final.
- `evals/output/cases.json` — assertions for both Markdown artifacts.
- `skills/jvc-deal-flow/SKILL.md` — map `ic_memo` to pre-review and `ic_review` approval to finalization.
- `skills/jvc-deal-flow/references/workflow-contract.md` — clarify the existing gate without changing transitions.
- `CLAUDE.md` — make the clean final the explicit exception to visible evidence labels.
- `README.md` — document both artifacts, filenames, sequence, and checks.
- `library/skill-registry.md` — update the skill summary.
- `manifest.json` — publish the two-artifact output contract.
- `reports/skill-ir.json` — update job, outputs, scripts, and failure modes.
- `reports/trust_report.json` and `reports/trust_report.md` — inventory the two new local scripts.

**Delete after move**

- `templates/ic-memo-template.md` — remove the duplicate root template after its content becomes the skill-owned reference.

## Task 1: Build the read-only final validator with a runnable regression check

**Files:**

- Create: `skills/jvc-ic-memo/scripts/check_package.py`
- Create: `skills/jvc-ic-memo/scripts/validate_final.py`

- [ ] **Step 1: Write the failing package check**

Create `skills/jvc-ic-memo/scripts/check_package.py` with this complete content:

```python
#!/usr/bin/env python3
"""Regression checks for the clean IC memo final validator."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_final.py")

REVIEW = """# IC Memo 预审版 — 星尘工坊

> 研究状态：ready

## 1. 执行摘要

公司 2026 年年化收入约 420 万元，覆盖 18 条产线。[S1]

## 2. 投资亮点

低代码训练平台可能降低部署成本。（来源：deck p.5）

## 3. 投资风险

未来收入仍可能受到订单转化速度影响。[未核实]

## 附录：质量报告

- 数字一致性检查通过。

## 来源索引

- [S1] 虚构项目材料 https://example.com/source
"""

CLEAN = """# IC Memo — 星尘工坊

## 1. 执行摘要

公司 2026 年年化收入约 420 万元，覆盖 18 条产线。

## 2. 投资亮点

低代码训练平台可能降低部署成本。

## 3. 投资风险

未来收入仍可能受到订单转化速度影响。
"""


def run(review: Path, final: Path, expect: int) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        (sys.executable, str(SCRIPT), "--review", str(review), "--final", str(final)),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"validator returned {result.returncode}, expected {expect}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        review = write(root / "06-ic-memo-review.md", REVIEW)
        final = write(root / "06-ic-memo.md", CLEAN)

        run(review, final, 0)

        invalid_cases = {
            "source-id": CLEAN + "\n[S1]\n",
            "source-note": CLEAN + "\n（来源：内部材料）\n",
            "page-reference": CLEAN + "\n参见 deck p.5。\n",
            "url": CLEAN + "\nhttps://example.com/source\n",
            "status": CLEAN + "\n> 研究状态：partial\n",
            "internal-section": CLEAN + "\n## 附录：质量报告\n\n通过。\n",
            "placeholder": CLEAN + "\n待确认\n",
            "new-number": CLEAN.replace("420 万元", "430 万元"),
            "empty-section": CLEAN + "\n## 4. 行业概况\n\n---\n",
            "malformed-table": CLEAN + "\n| 指标 | 数值 |\n| 收入 | 420 万元 |\n",
            "unclosed-fence": CLEAN + "\n```text\nnot closed\n",
        }
        for name, content in invalid_cases.items():
            candidate = write(root / f"{name}.md", content)
            result = run(review, candidate, 1)
            assert "validation failed" in result.stderr

        published = write(root / "published.md", CLEAN)
        before = published.read_text(encoding="utf-8")
        run(review, write(root / "bad-candidate.md", invalid_cases["new-number"]), 1)
        assert published.read_text(encoding="utf-8") == before

    print("jvc-ic-memo package check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the package check and verify the validator is missing**

Run:

```bash
python3 skills/jvc-ic-memo/scripts/check_package.py
```

Expected: FAIL because `skills/jvc-ic-memo/scripts/validate_final.py` does not exist.

- [ ] **Step 3: Implement the minimum validator**

Create `skills/jvc-ic-memo/scripts/validate_final.py` with this complete content:

```python
#!/usr/bin/env python3
"""Validate a clean IC memo final against its approved pre-review."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FORBIDDEN_PATTERNS = (
    ("source id", re.compile(r"\[S(?:\d+|编号)[^\]\n]*\]", re.IGNORECASE)),
    ("source note", re.compile(r"(?:资料)?来源[:：]")),
    (
        "page reference",
        re.compile(
            r"(?:\b(?:deck|report|pdf)\s+p(?:p)?\.?\s*\d+|第\s*\d+\s*页)",
            re.IGNORECASE,
        ),
    ),
    ("web link", re.compile(r"https?://", re.IGNORECASE)),
    ("internal label", re.compile(r"\[[^\]\n]+\]")),
    (
        "research status",
        re.compile(r"(?im)^(?:>\s*)?研究状态\s*[:：]\s*(?:ready|partial|blocked)\b"),
    ),
    (
        "internal section",
        re.compile(
            r"(?m)^#{1,6}\s+(?:附录[:：]\s*)?"
            r"(?:质量报告|来源索引|待用户裁定事项|未覆盖章节)\s*$"
        ),
    ),
)

PLACEHOLDER_RE = re.compile(
    r"待确认\s*⚠️?|\bTBD\b|\bTODO\b",
    re.IGNORECASE,
)
CHAPTER_RE = re.compile(r"(?m)^##\s+[^\n]+$")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEPARATOR_CELL_RE = re.compile(r"^:?-{3,}:?$")
NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9_])\d[\d,]*(?:\.\d+)?"
    r"(?:\s*(?:亿元|万元|元|%|倍|年|月|日|人|家|项|条|轮))?"
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"missing Markdown file: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"empty Markdown file: {path}")
    return text


def numeric_tokens(text: str) -> set[str]:
    return {re.sub(r"[\s,]", "", match.group(0)) for match in NUMBER_RE.finditer(text)}


def empty_chapters(text: str) -> list[str]:
    headings = list(CHAPTER_RE.finditer(text))
    empty: list[str] = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end() : end]
        meaningful = [
            line.strip()
            for line in body.splitlines()
            if line.strip() and line.strip() != "---" and not line.lstrip().startswith("#")
        ]
        if not meaningful:
            empty.append(heading.group(0).removeprefix("## ").strip())
    return empty


def table_errors(text: str) -> list[str]:
    groups: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if TABLE_ROW_RE.match(line):
            current.append((line_number, line))
        elif current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)

    errors: list[str] = []
    for rows in groups:
        cells = [row.strip().strip("|").split("|") for _, row in rows]
        if len(rows) < 2 or not all(
            TABLE_SEPARATOR_CELL_RE.fullmatch(cell.strip()) for cell in cells[1]
        ):
            errors.append(f"table at line {rows[0][0]} is missing a separator row")
            continue
        if any(len(row) != len(cells[0]) for row in cells[1:]):
            errors.append(f"table at line {rows[0][0]} has inconsistent columns")
    return errors


def validate(review: str, final: str) -> list[str]:
    errors: list[str] = []

    if not re.search(r"(?m)^#\s+\S", final):
        errors.append("final is missing a level-one title")
    if not CHAPTER_RE.search(final):
        errors.append("final is missing level-two chapters")
    if len(re.findall(r"(?m)^```", final)) % 2:
        errors.append("final has an unclosed fenced code block")

    for label, pattern in FORBIDDEN_PATTERNS:
        if pattern.search(final):
            errors.append(f"final contains {label}")
    if PLACEHOLDER_RE.search(final):
        errors.append("final contains a placeholder")

    empty = empty_chapters(final)
    if empty:
        errors.append(f"final contains empty chapters: {', '.join(empty)}")
    errors.extend(table_errors(final))

    new_numbers = sorted(numeric_tokens(final) - numeric_tokens(review))
    if new_numbers:
        errors.append(f"final contains numbers absent from review: {', '.join(new_numbers)}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--final", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        errors = validate(read_text(args.review), read_text(args.final))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"validation failed: {error}", file=sys.stderr)
        return 1

    print("IC memo final validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the package check and help surface**

Run:

```bash
python3 skills/jvc-ic-memo/scripts/check_package.py
python3 skills/jvc-ic-memo/scripts/validate_final.py --help
```

Expected: the package check prints `jvc-ic-memo package check passed`; help lists required `--review` and `--final` arguments.

- [ ] **Step 5: Optional commit checkpoint**

Only with explicit user authorization:

```bash
git add skills/jvc-ic-memo/scripts/check_package.py skills/jvc-ic-memo/scripts/validate_final.py
git commit -m "feat: validate clean IC memo finals"
```

## Task 2: Make the IC memo package self-contained

**Files:**

- Modify: `scripts/check-jvc-assets.sh`
- Create by move: `skills/jvc-ic-memo/references/ic-memo-template.md`
- Delete by move: `templates/ic-memo-template.md`

- [ ] **Step 1: Add failing package-path assertions**

Append these exact checks after the invoice-manager checks in `scripts/check-jvc-assets.sh`:

```bash
require_file "skills/jvc-ic-memo/references/ic-memo-template.md"
require_file "skills/jvc-ic-memo/scripts/validate_final.py"
require_file "skills/jvc-ic-memo/scripts/check_package.py"
reject_path "templates/ic-memo-template.md"
```

- [ ] **Step 2: Verify the old template location fails the new contract**

Run:

```bash
bash scripts/check-ic-memo-assets.sh
```

Expected: FAIL with missing `skills/jvc-ic-memo/references/ic-memo-template.md` or unexpected legacy path `templates/ic-memo-template.md`.

- [ ] **Step 3: Move the existing template without duplicating it**

Create the destination directory, then use `apply_patch` to move the tracked file:

```bash
mkdir -p skills/jvc-ic-memo/references
```

```text
*** Begin Patch
*** Update File: templates/ic-memo-template.md
*** Move to: skills/jvc-ic-memo/references/ic-memo-template.md
*** End Patch
```

- [ ] **Step 4: Verify the package-path contract passes**

Run:

```bash
bash scripts/check-ic-memo-assets.sh
```

Expected: PASS with no output.

- [ ] **Step 5: Optional commit checkpoint**

Only with explicit user authorization:

```bash
git add scripts/check-jvc-assets.sh skills/jvc-ic-memo/references/ic-memo-template.md templates/ic-memo-template.md
git commit -m "fix: package the IC memo template with its skill"
```

## Task 3: Replace the single-output skill contract with the approved two-stage workflow

**Files:**

- Modify: `scripts/check-jvc-assets.sh`
- Modify: `skills/jvc-ic-memo/SKILL.md`
- Modify: `skills/jvc-ic-memo/references/ic-memo-template.md`

- [ ] **Step 1: Add failing contract assertions**

Append these checks next to the Task 2 IC memo assertions in `scripts/check-jvc-assets.sh`:

```bash
require_text "skills/jvc-ic-memo/SKILL.md" 'version: "5.0.0"'
require_text "skills/jvc-ic-memo/SKILL.md" "06-ic-memo-review.md"
require_text "skills/jvc-ic-memo/SKILL.md" "预审通过"
require_text "skills/jvc-ic-memo/SKILL.md" "06-ic-memo.md"
require_text "skills/jvc-ic-memo/SKILL.md" "validate_final.py"
require_text "skills/jvc-ic-memo/SKILL.md" "不做机械标签删除"
require_text "skills/jvc-ic-memo/references/ic-memo-template.md" "预审版"
require_text "skills/jvc-ic-memo/references/ic-memo-template.md" "终版转换合同"
```

- [ ] **Step 2: Verify the old skill contract fails**

Run:

```bash
bash scripts/check-ic-memo-assets.sh
```

Expected: FAIL because the v4 skill has no two-stage output contract.

- [ ] **Step 3: Update the skill identity and anti-rationalization rules**

In `skills/jvc-ic-memo/SKILL.md`:

- Set `version: "5.0.0"`.
- Change the description to say the default output is an evidence-rich pre-review and the approved output is a clean IC final.
- Add these exact anti-rationalization rules:

```markdown
- “终版只是把预审版引用删掉” → 不做机械标签删除；根据用户裁定重新组织正文，避免把未核实内容伪装成确定事实。
- “预审版已经 ready，可以自动生成终版” → `ready` 不是用户批准；只有用户明确表达“预审通过”或等价授权后才能进入终版阶段。
- “终版更干净，可以顺手补一个数字” → 终版不得增加获批预审版中不存在的事实、数字或判断。
```

- [ ] **Step 4: Replace Phase 5 and execution/output sections with the two-stage contract**

Keep the existing material scan, skeleton, chapter ordering, skill mapping, and three review checks. Replace the old single “终稿组装” behavior with this exact contract:

````markdown
### Phase 5: 预审版组装与审查

1. 修复 Phase 4 发现的问题；需要用户裁定的数据冲突保留在预审版。
2. 组装 `06-ic-memo-review.md`，包含正文引用、证据状态、质量报告、冲突、缺口和未覆盖章节。
3. 只把预审版传给 `jvc-research-core audit`；同时读取退出状态和 `audit.json`。
4. `blocked` 时只报告阻断项；`partial` 时显式报告剩余不确定性；`ready` 也必须停止并等待用户批准。

### Phase 6: 人工批准后的终版

1. 只有用户明确表达“预审通过”或等价授权后才进入本阶段。
2. 读取最新预审版、最新 audit 和本轮用户裁定；仍有未裁定数字冲突时停止。
3. 重新组织正文，不做机械标签删除：充分信息写成确定性陈述，不完全确定但获准保留的信息使用“可能”“预计”“约”“区间为”或情景表达。
4. 删除来源、引用、证据状态、研究状态、质量报告、缺口标签、占位符和内部操作说明；没有有效内容的章节直接省略。
5. 将候选文件写到临时路径，运行：

```bash
python3 "<skill-root>/scripts/validate_final.py" \
  --review "<project-dir>/06-ic-memo-review.md" \
  --final "<candidate.md>"
```

6. 校验通过后才发布为 `06-ic-memo.md`；校验失败时保留已有终版并报告候选文件问题。
````

Update the evidence-core section so every occurrence of “最终产物” that refers to evidence citations or `audit --artifact` becomes “预审版 `06-ic-memo-review.md`”. State explicitly that the clean final is a user-approved presentation derivative and is not passed to the citation-requiring research-core profile.

- [ ] **Step 5: Replace the output-format section**

Use this exact output summary:

```markdown
## 输出格式

两个顺序生成的标准 Markdown 文件，共用十七章顺序：

| 阶段 | 文件 | 读者 | 必含内容 |
| --- | --- | --- | --- |
| 预审 | `06-ic-memo-review.md` | 投资经理 | 引用、证据状态、冲突、缺口、质量报告 |
| 终版 | `06-ic-memo.md` | IC 委员 | 经批准的信息、判断、风险和情景表达 |

默认只生成预审版并停止。没有用户明确批准，不得生成或覆盖终版。两份文件都保持标准 Markdown；Quarto 视觉与 HTML 输出不属于本 skill。
```

Split the hard constraints into “两版共同约束”, “预审版约束”, and “终版约束”. Keep risk/logic balance, consistent units, no invented data, and no agent-authored final invest/pass decision as shared constraints.

- [ ] **Step 6: Update the template’s production and output contracts**

In `skills/jvc-ic-memo/references/ic-memo-template.md`:

- Set template `version: 3.0` and date `2026-08-08`.
- Rename Phase 5 to “预审版交付” and add Phase 6 “批准后生成终版”.
- State once near the top that all per-chapter source and checklist examples describe the pre-review.
- Add this section after the global quality redlines:

```markdown
### 终版转换合同

终版不是删除引用后的预审版。用户批准预审后，按以下规则重新组织：

- 已确认信息使用确定性陈述；
- 获准保留的不确定信息使用概率、区间、预计或情景表达；
- 来源、引用、证据状态、质量报告和缺口标签不进入终版；
- 数字冲突必须先由用户裁定；
- 不新增预审版中没有的事实、数字或判断；
- 没有有效内容的章节直接省略。
```

- Replace the current “投资建议” subsection with:

```markdown
### 待 IC 决定事项

[列出需要 IC 判断的交易条件、收益情景和关键前提；不替用户写建议投、不投或有条件投。]
```

- Replace the old Office-output table with:

```markdown
| 文件 | 规范 |
| --- | --- |
| `06-ic-memo-review.md` | 内部预审主文件，保留引用、证据状态和质量报告 |
| `06-ic-memo.md` | 获批后生成的干净终版，只保留面向 IC 的信息 |

两份文件只使用标准 Markdown；Quarto 负责后续 HTML 输出和视觉样式。
```

- [ ] **Step 7: Run focused package checks**

Run:

```bash
bash scripts/check-ic-memo-assets.sh
python3 skills/jvc-ic-memo/scripts/check_package.py
```

Expected: both pass.

- [ ] **Step 8: Optional commit checkpoint**

Only with explicit user authorization:

```bash
git add scripts/check-jvc-assets.sh skills/jvc-ic-memo/SKILL.md skills/jvc-ic-memo/references/ic-memo-template.md
git commit -m "feat: split IC memo review and final stages"
```

## Task 4: Add review/final examples and deterministic output-contract coverage

**Files:**

- Modify: `examples/ic-memo-example.md`
- Create: `examples/ic-memo-final-example.md`
- Modify: `evals/output/cases.json`
- Modify: `evals/trigger_cases.json`

- [ ] **Step 1: Update the output fixture assertions first**

Replace the `ic-memo-markdown-contract` assertions in `evals/output/cases.json` with:

```json
[
  {"type": "file_exists", "path": "examples/ic-memo-example.md"},
  {"type": "contains", "path": "examples/ic-memo-example.md", "text": "IC Memo 预审版"},
  {"type": "contains", "path": "examples/ic-memo-example.md", "text": "## 附录：质量报告"},
  {"type": "contains_any", "path": "examples/ic-memo-example.md", "texts": ["[需要用户提供]", "[未核实]"]},
  {"type": "file_exists", "path": "examples/ic-memo-final-example.md"},
  {"type": "contains", "path": "examples/ic-memo-final-example.md", "text": "# IC Memo — 星尘工坊"},
  {"type": "contains_any", "path": "examples/ic-memo-final-example.md", "texts": ["可能", "预计", "约", "区间"]},
  {"type": "not_contains_any", "path": "examples/ic-memo-final-example.md", "texts": ["[S", "[未核实]", "[需要用户提供]", "来源：", "deck p.", "质量报告", "研究状态", "http://", "https://", "建议投资", "不建议投资"]}
]
```

- [ ] **Step 2: Update the IC memo trigger case first**

Change `ic-memo-full-synthesis` to this contract:

```json
{
  "id": "ic-memo-review-then-final",
  "prompt": "把前序尽调材料合成 IC memo，先生成带证据和缺口的预审版，等我明确审批后再生成不含引用和证据状态的干净终版。",
  "expected_skill": "jvc-ic-memo",
  "prompt_signals": ["IC memo", "预审版", "明确审批", "干净终版"],
  "skill_contract_signals": [
    "十七章",
    "06-ic-memo-review.md",
    "预审通过",
    "06-ic-memo.md",
    "不做机械标签删除",
    "validate_final.py",
    "证据内核（必须）",
    "researchctl.py",
    "ready",
    "partial",
    "blocked",
    "init --skill jvc-ic-memo",
    "record --run-dir <研究目录> --input <records.jsonl>",
    "audit --run-dir <研究目录> --skill jvc-ic-memo",
    "不得退回纯 prompt 模式"
  ],
  "near_neighbors": [
    {
      "skill": "jvc-bull-case",
      "why_not": "bull-case only extracts positive arguments and cannot own the audited pre-review, human approval gate, and clean IC final."
    }
  ]
}
```

- [ ] **Step 3: Run fixture validation and confirm it fails**

Run:

```bash
python3 scripts/check-skill-evals.py
```

Expected: FAIL because the final example is missing and the existing example title still describes a generic memo.

- [ ] **Step 4: Mark the existing example as the pre-review fixture**

Change only its title and internal framing; preserve its evidence-rich content:

```markdown
# IC Memo 预审版 — 星尘工坊（虚构示例）

> 本文件供投资经理预审，保留来源、证据状态、缺口和质量报告；不是提交 IC 的干净终版。
```

Keep the existing seventeen chapters and quality report below that header.

- [ ] **Step 5: Add the compact clean-final example**

Create `examples/ic-memo-final-example.md` with content derived only from numbers and claims already present in the review fixture:

```markdown
# IC Memo — 星尘工坊

## 1. 执行摘要

星尘工坊面向中小制造企业提供视觉质检软件、低代码模型训练平台和产线边缘部署盒子。公司处于 Pre-A 阶段，年化收入约 420 万元，产品已覆盖约 18 条产线。

本轮计划融资 3,000 万元。投前估值、拟投资金额和完整财务预测尚未形成统一交易方案，因此本轮回报取决于最终估值、后续稀释和退出安排。

## 2. 投资亮点

中小制造企业同时面临人工成本上升、良率要求提高和客户验厂压力，视觉质检自动化具备持续需求。低代码训练平台可能减少算法工程师驻场时间，并提高相似产线之间的交付复用率。

团队具有机器视觉项目交付和制造业算法经验，对工业现场的理解可能缩短产品迭代周期。

## 3. 投资风险

公司当前收入规模较小，未来收入仍可能受到订单转化速度、部署人天和客户预算的影响。如果每条产线仍需要算法工程师长期驻场，商业模式可能更接近项目制集成，毛利率和估值中枢将相应下降。

低代码训练能力可能主要适用于划痕、凹坑等简单外观缺陷。在复杂缺陷场景下，产品仍可能需要较深的算法介入，可服务市场空间因而存在收窄风险。

当前交易估值和退出路径尚未确定。若 5 年内无法实现公开市场退出，投资回报可能更多依赖并购或回购安排。

## 8. 公司概况

星尘工坊科技（苏州）有限公司成立于 2024 年，主营面向中小制造企业的低代码视觉质检软件。

## 9. 产品矩阵

| 产品 | 主要功能 | 价格区间 | 当前阶段 |
| --- | --- | --- | --- |
| 低代码训练平台 | 样本上传、标注、训练、验证和部署 | 每年约 8–20 万元 | 导入期 |
| 边缘部署盒子 | 在产线现场运行推理模型 | 每台约 2–5 万元 | 导入期 |

## 17. 交易与收益情景

本轮拟融资 3,000 万元。最终投资回报需要在投前估值、投资金额、持股比例、后续稀释和退出估值确定后测算。估值较高或退出时间延后时，回报倍数可能明显下降。
```

- [ ] **Step 6: Validate the clean example with both check paths**

Run:

```bash
python3 skills/jvc-ic-memo/scripts/validate_final.py \
  --review examples/ic-memo-example.md \
  --final examples/ic-memo-final-example.md
python3 scripts/check-skill-evals.py
```

Expected: both pass.

- [ ] **Step 7: Optional commit checkpoint**

Only with explicit user authorization:

```bash
git add examples/ic-memo-example.md examples/ic-memo-final-example.md evals/output/cases.json evals/trigger_cases.json
git commit -m "test: cover IC memo review and final artifacts"
```

## Task 5: Align deal-flow, repository rules, and human-facing documentation

**Files:**

- Modify: `scripts/check-jvc-assets.sh`
- Modify: `skills/jvc-deal-flow/SKILL.md`
- Modify: `skills/jvc-deal-flow/references/workflow-contract.md`
- Modify: `CLAUDE.md`
- Modify: `README.md`
- Modify: `library/skill-registry.md`
- Modify: `manifest.json`
- Modify: `reports/skill-ir.json`

- [ ] **Step 1: Add failing repository-contract assertions**

Add these exact assertions beside the other IC memo checks in `scripts/check-jvc-assets.sh`:

```bash
require_text "CLAUDE.md" "预审版必须完整暴露"
require_text "CLAUDE.md" "终版是唯一例外"
require_text "README.md" "06-ic-memo-review.md"
require_text "README.md" "预审通过"
require_text "library/skill-registry.md" "预审版"
require_text "skills/jvc-deal-flow/references/workflow-contract.md" "06-ic-memo-review.md"
require_text "skills/jvc-deal-flow/references/workflow-contract.md" "批准后生成 `06-ic-memo.md`"
```

- [ ] **Step 2: Run the focused asset check and verify documentation fails**

Run:

```bash
bash scripts/check-ic-memo-assets.sh
```

Expected: FAIL on the first missing documentation signal.

- [ ] **Step 3: Align the existing deal-flow gate without changing Python state**

In `skills/jvc-deal-flow/references/workflow-contract.md`, replace the two IC rows with:

```markdown
| `ic_memo` | L3 | `06-ic-memo-review.md` 通过自身证据审查 | `ic_review` |
| `ic_review` | L3 | 用户修改、停止或批准预审；批准后生成 `06-ic-memo.md` | `decision_record` 或返回修改 |
```

In `skills/jvc-deal-flow/SKILL.md`, add after the existing gate rule:

```markdown
在 `ic_memo` 阶段只生成并审查 `06-ic-memo-review.md`；进入 `ic_review` 后请求人工闸门。只有 `gate_decided=approve` 才调用 `/jvc-ic-memo` 的终版阶段，校验并发布 `06-ic-memo.md`，然后再进入 `decision_record`。
```

Do not add a gate or transition; the existing `ic_review` gate already represents this approval.

- [ ] **Step 4: Add the explicit repository-rule exception**

Replace the current blanket `/jvc-ic-memo` bullet in `CLAUDE.md` with:

```markdown
- `/jvc-prescreen`、`/jvc-bear-case` 和 `/jvc-ic-memo` 的预审版必须完整暴露未覆盖问题和反面证据。经用户明确批准生成的 `06-ic-memo.md` 终版是唯一例外：它不显示引用、证据状态、缺口标签或质量报告，但只能来自已审预审版；不完全确定的信息使用概率、区间或情景表达，不得改写为虚假确定事实。
```

- [ ] **Step 5: Update README and registry contracts**

In `README.md`:

- Change the tool-table output to `` `06-ic-memo-review.md` + `06-ic-memo.md` ``.
- Replace “十段式初稿” with “十七章预审版；预审通过后生成干净终版”.
- In the project tree, place `06-ic-memo-review.md` immediately before `06-ic-memo.md`.
- Add `python3 skills/jvc-ic-memo/scripts/check_package.py` to maintenance checks.

Use this exact skill summary in both `README.md` and `library/skill-registry.md`:

```markdown
先生成含引用、证据状态、冲突和质量报告的十七章预审版；用户明确预审通过后，再生成不含审查痕迹、供 IC 阅读和 Quarto 渲染的干净 Markdown 终版。
```

- [ ] **Step 6: Update package and skill intermediate representation metadata**

Add this string to `manifest.json` `output_contracts`:

```json
"Audited IC memo pre-review and user-approved clean Markdown final"
```

Replace the `jvc-ic-memo` object fields in `reports/skill-ir.json` with:

```json
"job": "Synthesize prior diligence into an audited IC memo pre-review, stop for explicit user approval, then produce a clean Markdown final without visible evidence metadata.",
"outputs": ["Audited Markdown IC memo pre-review", "Approved clean Markdown IC memo final"],
"near_neighbors": ["jvc-prescreen", "jvc-bull-case", "jvc-bear-case"],
"scripts": ["skills/jvc-ic-memo/scripts/validate_final.py", "skills/jvc-ic-memo/scripts/check_package.py"],
"failure_modes": ["Skips pre-review approval", "Leaks citations or evidence status into final", "Adds facts or numbers during finalization", "Overwrites a prior final after failed validation", "Outputs invest/pass recommendation"]
```

- [ ] **Step 7: Run focused and cross-workflow checks**

Run:

```bash
bash scripts/check-ic-memo-assets.sh
python3 skills/jvc-deal-flow/scripts/check_package.py
python3 scripts/check-v3-foundation.py
python3 scripts/check-skill-evals.py
```

Expected: all pass. The deal-flow check proves existing transitions still work unchanged.

- [ ] **Step 8: Optional commit checkpoint**

Only with explicit user authorization:

```bash
git add scripts/check-jvc-assets.sh skills/jvc-deal-flow/SKILL.md skills/jvc-deal-flow/references/workflow-contract.md CLAUDE.md README.md library/skill-registry.md manifest.json reports/skill-ir.json
git commit -m "docs: align JVC workflow with IC memo approval gate"
```

## Task 6: Refresh trust metadata and run full verification

**Files:**

- Modify: `reports/trust_report.json`
- Modify: `reports/trust_report.md`

- [ ] **Step 1: Add the two scripts to the machine-readable inventory**

Insert these entries in `reports/trust_report.json` `script_inventory` next to the deal-flow scripts:

```json
{
  "path": "skills/jvc-ic-memo/scripts/validate_final.py",
  "interface": "argparse",
  "help_surface": "--help",
  "capabilities": ["file_read"]
},
{
  "path": "skills/jvc-ic-memo/scripts/check_package.py",
  "interface": "self-check",
  "help_surface": "none",
  "capabilities": ["file_read", "file_write", "subprocess"]
}
```

Also append this dependency-review note:

```json
"The IC memo final validator and package check use the Python standard library only."
```

- [ ] **Step 2: Update the human-readable script surface**

Add these rows to `reports/trust_report.md`:

```markdown
| `skills/jvc-ic-memo/scripts/validate_final.py` | argparse CLI（Command-Line Interface，命令行界面，供终端以参数调用校验器） | file read；无网络 |
| `skills/jvc-ic-memo/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时目录 |
```

Update the dependency-review sentence to state that the IC memo validator is standard-library-only.

- [ ] **Step 3: Confirm the source-contract hash is stale before refreshing it**

Run:

```bash
python3 scripts/check-governance.py
```

Expected: FAIL with `trust report hash mismatch` because source-contract files changed.

- [ ] **Step 4: Refresh the hash and rerun governance**

Run:

```bash
python3 scripts/check-governance.py --write-hash
python3 scripts/check-governance.py
```

Expected: PASS with `governance assets passed`.

- [ ] **Step 5: Run the complete relevant verification set**

Run:

```bash
python3 skills/jvc-ic-memo/scripts/check_package.py
python3 skills/jvc-ic-memo/scripts/validate_final.py \
  --review examples/ic-memo-example.md \
  --final examples/ic-memo-final-example.md
bash scripts/check-ic-memo-assets.sh
bash scripts/check-jvc-assets.sh
python3 scripts/check-skill-evals.py
python3 scripts/check-v3-foundation.py
python3 skills/jvc-deal-flow/scripts/check_package.py
python3 scripts/check-research-core-install.py
python3 scripts/check-governance.py
git diff --check
```

Expected: every command passes and `git diff --check` prints nothing.

- [ ] **Step 6: Review the final diff and worktree without changing unrelated files**

Run:

```bash
git diff --stat
git diff -- skills/jvc-ic-memo scripts/check-jvc-assets.sh examples evals CLAUDE.md README.md library/skill-registry.md manifest.json reports/skill-ir.json reports/trust_report.json reports/trust_report.md skills/jvc-deal-flow
git status --short
```

Expected: only the files named in this plan plus the approved spec/plan are changed. `.superpowers/` may remain an unrelated untracked brainstorming artifact; do not add or delete it without user direction.

- [ ] **Step 7: Optional final commit checkpoint**

Only with explicit user authorization:

```bash
git add skills/jvc-ic-memo scripts/check-jvc-assets.sh examples/ic-memo-example.md examples/ic-memo-final-example.md evals/trigger_cases.json evals/output/cases.json skills/jvc-deal-flow/SKILL.md skills/jvc-deal-flow/references/workflow-contract.md CLAUDE.md README.md library/skill-registry.md manifest.json reports/skill-ir.json reports/trust_report.json reports/trust_report.md docs/superpowers/specs/2026-08-08-jvc-ic-memo-review-final-design.md docs/superpowers/plans/2026-08-08-jvc-ic-memo-review-final.md
git commit -m "feat: add IC memo pre-review and clean final workflow"
```

Do not push.

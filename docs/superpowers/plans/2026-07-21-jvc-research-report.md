# JVC Research Report Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `/jvc-research-report`, a production-grade local skill that validates fixed-format industry-research Markdown and generates a `lustinus RESEARCH` PDF (Portable Document Format，可移植文档格式，用于固定页面布局并便于打印分发), an HTML (HyperText Markup Language，超文本标记语言，用于描述页面内容结构) preview, and a build report without rewriting the research content.

**Architecture:** One Python command loads safe YAML (YAML Ain't Markup Language，YAML 不是标记语言，一种结构化元数据格式), validates canonical `/jvc-track-research` sections and `[S<n>]` citations, renders Markdown through `markdown-it-py`, applies one print CSS (Cascading Style Sheets，层叠样式表，用于控制页面视觉和分页), and renders with WeasyPrint. Assets stay local, remote resource fetching is denied, and all three outputs are staged before replacing the previous successful build.

**Tech Stack:** Python 3.14, `markdown-it-py==4.0.0`, `PyYAML==6.0.3`, `WeasyPrint==68.1`, `Pillow==12.1.1`, standard-library command-line and filesystem modules, existing `pdfinfo`/`pdftotext`/`pdftoppm` checks.

---

## Locked decisions

- Skill command: `/jvc-research-report`, satisfying the repository's `jvc-` naming rule.
- User-visible report brand: exactly `lustinus RESEARCH`.
- Mode: `production`; route confusion, deterministic rendering, repeated use, and visual quality warrant production gates.
- Input: fixed-format `report.md`, reusable `brand.yml`, and local images.
- Output: exactly `report.pdf`, `report.html`, and `build-report.txt`.
- Content boundary: validate and format only; no research, rewriting, summarizing, reordering, or chart generation.
- Compatibility: current unnumbered `/jvc-track-research` headings, optional `0`/`A–I` prefixes, and optional `缩写说明`/`未核实与待补证据` sections.

## Official references

- [WeasyPrint 应用程序编程接口文档](https://doc.courtbouillon.org/weasyprint/stable/api_reference.html): API = Application Programming Interface，应用程序编程接口，即代码调用约定。Use `HTML.render()` for pagination and page count, `Document.write_pdf()` for output, and an allowed-protocol fetcher to block remote assets.
- [markdown-it-py usage guide](https://markdown-it-py.readthedocs.io/en/latest/using.html): use `MarkdownIt("commonmark").enable("table")`, token parsing, and render rules for headings and images.
- [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation): use `yaml.safe_load`, which recognizes standard YAML tags without constructing arbitrary Python objects.

## File map

### Create

- `skills/jvc-research-report/SKILL.md`
- `skills/jvc-research-report/agents/interface.yaml`
- `skills/jvc-research-report/manifest.json`
- `skills/jvc-research-report/requirements.txt`
- `skills/jvc-research-report/references/output-contract.md`
- `skills/jvc-research-report/assets/brand.yml`
- `skills/jvc-research-report/assets/report.css`
- `skills/jvc-research-report/templates/industry-report.md`
- `skills/jvc-research-report/scripts/build_report.py`
- `skills/jvc-research-report/scripts/check_package.py`
- `skills/jvc-research-report/evals/trigger_cases.json`
- `skills/jvc-research-report/reports/output-risk-profile.md`
- `skills/jvc-research-report/reports/artifact-design-profile.md`
- `examples/research-report-example/report.md`
- `examples/research-report-example/assets/technology-routes.svg`

### Modify

- `setup`, `agents/interface.yaml`, `library/skill-registry.md`, `README.md`, `manifest.json`
- `skills/jvc-track-research/SKILL.md`
- `scripts/check-jvc-assets.sh`, `scripts/check-review-fixes.sh`, `scripts/check-skill-evals.py`, `scripts/check-governance.py`
- `evals/trigger_cases.json`, `evals/output/cases.json`
- `reports/skill-ir.json`, `reports/route_scorecard.md`, `reports/output_quality_scorecard.md`
- `reports/trust_report.json`, `reports/trust_report.md`, `reports/review-studio.json`, `reports/review-studio.md`
- `security/network_policy.json`, `security/permission_policy.json`

## Task 1: Create the production skill boundary

**Files:** Create the package metadata, reference, reports, brand, and route fixtures listed above.

- [ ] **Step 1: Confirm the skill package does not exist yet**

```bash
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/validate_skill.py skills/jvc-research-report
```

Expected: non-zero exit because `skills/jvc-research-report` does not exist.

- [ ] **Step 2: Create the lean routing entrypoint**

Create `SKILL.md` with this exact behavior:

```markdown
---
name: jvc-research-report
description: Use when the user already has a local fixed-structure industry or track research Markdown file and wants it validated and rendered as a branded printable report plus browser preview without rewriting the research content. Do not use for first-pass research, content rewriting, chart generation, investment-committee memo drafting, or arbitrary Markdown conversion.
metadata:
  author: jvc-analyst
---

# /jvc-research-report — lustinus RESEARCH 行业研报生成

把已完成的固定格式行业研究 Markdown 校验并编译为 PDF（Portable Document Format，可移植文档格式，用于固定版式）和 HTML（HyperText Markup Language，超文本标记语言，用于浏览器预览）。

## 输入

- 固定章节的 `report.md`
- 可复用的 `brand.yml`
- Markdown 引用的本地图片

内容不完整时回到 `/jvc-track-research`；本 skill 不补研究、不改观点。

## 执行

1. 运行 `python3 scripts/build_report.py report.md --brand brand.yml --output output`。
2. 构建失败时原样返回具体错误，不猜测、不覆盖上一版成功产物。
3. 成功后检查 `build-report.txt`，再渲染并检查全部 PDF 页面。
4. 交付 `report.pdf`、`report.html` 和 `build-report.txt`。

## 规则

- 不重写、摘要、重排或补充正文。
- 只读取本地 Markdown、YAML、图片和字体；远程图片直接报错。
- `[S<n>]` 必须在来源索引中有唯一条目。
- 表格和图片只排版，不生成新图表。
- 英文缩写首次出现时给出英文全称、中文全称和一句解释。

## Reference Map

- `references/output-contract.md` — 输入结构、品牌字段、卡片语法和失败规则。
- `assets/brand.yml` — 默认品牌配置。
- `templates/industry-report.md` — 固定格式模板。
- `scripts/build_report.py` — 确定性校验和渲染器。
```

- [ ] **Step 3: Create production metadata and pins**

Create `manifest.json`:

```json
{
  "name": "jvc-research-report",
  "version": "0.1.0",
  "owner": "jvc-analyst",
  "updated_at": "2026-07-21",
  "status": "active",
  "maturity_tier": "production",
  "lifecycle_stage": "production",
  "context_budget_tier": "production",
  "review_cadence": "quarterly",
  "skill_archetype": "production",
  "target_platforms": ["codex", "claude", "generic", "agent-skills-compatible"],
  "factory_components": ["references", "scripts", "assets", "templates", "evals", "reports"],
  "input_files": "file-backed fixture: fixed-format report.md, brand.yml, and local images",
  "output_contract": ["report.pdf", "report.html", "build-report.txt"],
  "rollback_boundary": "A failed build leaves the previous successful output files unchanged; package rollback is a Git revert."
}
```

Create `agents/interface.yaml`:

```yaml
interface:
  display_name: "JVC Research Report"
  short_description: "Render fixed-format industry research as lustinus RESEARCH PDF and HTML."
  default_prompt: "Use /jvc-research-report to validate this fixed-format local industry-research Markdown and generate report.pdf, report.html, and build-report.txt without rewriting content."
compatibility:
  canonical_format: "agent-skills"
  adapter_targets: ["codex", "claude", "generic"]
  activation:
    mode: "manual"
    paths: ["skills/jvc-research-report/SKILL.md"]
  execution:
    context: "local"
    shell: "bash"
  trust:
    source_tier: "local"
    remote_inline_execution: "forbid"
    remote_metadata_policy: "allow-metadata-only"
```

Create `requirements.txt`:

```text
markdown-it-py==4.0.0
Pillow==12.1.1
PyYAML==6.0.3
WeasyPrint==68.1
```

- [ ] **Step 4: Create the brand and deferred contracts**

Create `assets/brand.yml`:

```yaml
name: lustinus RESEARCH
logo: null
accent_color: "#A06B2C"
header: lustinus RESEARCH
footer: Internal Research
disclaimer: Internal research only. Verify sources before external distribution.
sans_font: PingFang SC
serif_font: Songti SC
```

`references/output-contract.md` must define required frontmatter (`title`, `date`), all eleven canonical sections, optional prefixes/extra sections, `[!FACT]`/`[!INFERENCE]`/`[!OPEN QUESTION]`, image-alt captions, `表：` table captions, italic `来源：` lines, unique source IDs, hard errors, and warnings.

`reports/output-risk-profile.md` must cover overflow, missing/local assets, citation drift, font substitution, rollback, and mandatory visual inspection. `reports/artifact-design-profile.md` must record A4, `lustinus RESEARCH`, ink/copper/fact/risk colors, serif/sans roles, cover/contents/section rhythm, and caption/source adjacency.

- [ ] **Step 5: Add route cases and run Yao production gates**

Create `evals/trigger_cases.json` with `recommended_threshold: 0.33`, `negative_patterns: ["从零研究", "任意结构", "重写", "联网补充"]`, and these exact cases:

```json
{
  "should_trigger": [
    {"text": "把这份固定章节和来源索引的行业研究 Markdown 编译成 lustinus RESEARCH 报告，不要改正文。", "family": "fixed_report_render"},
    {"text": "将已经完成的 jvc-track-research 文档校验后输出 PDF、HTML 预览和构建报告。", "family": "track_output_render"},
    {"text": "按 brand.yml 重新生成本地研报，保留上一版直到新版本成功。", "family": "branded_rebuild"}
  ],
  "should_not_trigger": [
    {"text": "帮我从零研究玻璃基板赛道并补齐资料。", "family": "first_pass_research"},
    {"text": "把这篇任意结构的 Markdown 快速转成 PDF。", "family": "arbitrary_markdown"},
    {"text": "重写这份研报并联网补充更多事实。", "family": "content_rewriting"}
  ],
  "near_neighbor": [
    {"text": "先研究赛道，再决定是否需要正式报告。", "family": "track_research_first"},
    {"text": "把公司尽调材料合成为投委会备忘录。", "family": "ic_memo"},
    {"text": "已有完整行业研究，只需要固定版式和分页。", "family": "render_only"}
  ]
}
```

`/jvc-ic-memo` means Investment Committee Memo，投资委员会备忘录，用于投决材料合成.

```bash
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/validate_skill.py skills/jvc-research-report
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/resource_boundary_check.py skills/jvc-research-report --max-initial-tokens 1000
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/trigger_eval.py \
  --description-file skills/jvc-research-report/SKILL.md \
  --cases skills/jvc-research-report/evals/trigger_cases.json \
  --semantic-config skills/jvc-research-report/evals/semantic_config.json
```

Expected: all exit `0`; initial-load tokens are at or below `1000`.

- [ ] **Step 6: Commit the routeable boundary**

```bash
git add skills/jvc-research-report
git commit -m "Add research report skill contract"
```

## Task 2: Implement input validation with one runnable check

**Files:** Create `scripts/check_package.py` and `scripts/build_report.py` inside the new skill.

- [ ] **Step 1: Write the failing check**

The check must import `build_report.py` and assert one valid in-memory document plus missing-date, wrong-order, undefined-source, duplicate-source, remote-image, and path-escape failures. Run it before creating the builder.

```bash
python3 skills/jvc-research-report/scripts/check_package.py
```

Expected: non-zero exit because `build_report.py` is missing.

- [ ] **Step 2: Implement the parser and validators**

Use these exact contracts:

```python
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import mimetypes
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import yaml
from markdown_it import MarkdownIt
from PIL import Image
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from weasyprint.urls import FatalURLFetchingError, URLFetcher

VERSION = "0.1.0"


class BuildError(RuntimeError):
    pass


REQUIRED_FIELDS = ("title", "date")
SECTION_ALIASES = (
    ("研究设定与一页快照",),
    ("行业定义与边界",),
    ("行业简史与产业生命周期",),
    ("技术路线与商业可行性",),
    ("产业链图谱",),
    ("产业趋势、景气度与周期位置",),
    ("关键玩家", "关键玩家分层"),
    ("监管、政策与标准",),
    ("投资相关问题", "投资相关问题与反证账本"),
    ("后续工作交接包",),
    ("来源索引",),
)


def split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        raise BuildError("report.md: missing YAML frontmatter")
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise BuildError("report.md: YAML frontmatter is not closed")
    try:
        metadata = yaml.safe_load(text[4:marker]) or {}
    except yaml.YAMLError as exc:
        raise BuildError(f"report.md: invalid YAML: {exc}") from exc
    if not isinstance(metadata, dict):
        raise BuildError("report.md: frontmatter must be a mapping")
    return metadata, text[marker + 5 :]


def validate_metadata(metadata: dict[str, object]) -> list[str]:
    missing = [field for field in REQUIRED_FIELDS if not metadata.get(field)]
    if missing:
        raise BuildError(f"report.md: missing required metadata: {', '.join(missing)}")
    optional = ("subtitle", "authors", "sector", "region", "classification", "cover_image", "disclaimer")
    return [f"optional metadata missing: {field}" for field in optional if not metadata.get(field)]


def normalized_heading(value: str) -> str:
    value = re.sub(r"^\s*(?:0|[A-I])[.、)]\s*", "", value.strip(), flags=re.IGNORECASE)
    return re.sub(r"\s+", "", value)


def level_two_headings(body: str) -> list[str]:
    tokens = MarkdownIt("commonmark").enable("table").parse(body)
    return [tokens[i + 1].content for i, token in enumerate(tokens[:-1]) if token.type == "heading_open" and token.tag == "h2"]


def validate_structure(body: str) -> None:
    headings = [normalized_heading(value) for value in level_two_headings(body)]
    cursor = -1
    for aliases in SECTION_ALIASES:
        accepted = {normalized_heading(alias) for alias in aliases}
        positions = [index for index, heading in enumerate(headings) if heading in accepted and index > cursor]
        if not positions:
            raise BuildError(f"report.md: missing or out-of-order section: {aliases[0]}")
        cursor = positions[0]


def validate_sources(body: str) -> None:
    match = re.search(r"(?m)^##\s+(?:[A-I][.、)]\s*)?来源索引\s*$", body)
    if not match:
        raise BuildError("report.md: missing source index")
    used = set(re.findall(r"\[S([1-9]\d*)\]", body[: match.start()]))
    defined = re.findall(r"(?m)^\|\s*S([1-9]\d*)\s*\|", body[match.end() :])
    duplicates = sorted(source for source in set(defined) if defined.count(source) > 1)
    if duplicates:
        raise BuildError(f"report.md: duplicate source IDs: {', '.join('S' + item for item in duplicates)}")
    missing = sorted(used - set(defined), key=int)
    if missing:
        raise BuildError(f"report.md: undefined sources: {', '.join('S' + item for item in missing)}")
```

- [ ] **Step 3: Run and commit the validation slice**

```bash
python3 skills/jvc-research-report/scripts/check_package.py
git add skills/jvc-research-report/scripts
git commit -m "Validate fixed research report inputs"
```

Expected: package check passes before the commit.

## Task 3: Implement local-only rendering and rollback

**Files:** Modify both scripts; create `assets/report.css`.

- [ ] **Step 1: Extend the check before implementation**

Build a temporary valid report and assert the output directory contains exactly the three contract files, PDF bytes begin `%PDF`, HTML contains `lustinus RESEARCH`, and an invalid rebuild leaves all three file-content hashes unchanged.

Expected before implementation: check fails because the command-line renderer is incomplete.

- [ ] **Step 2: Add local asset, font, and fetch guards**

URL = Uniform Resource Locator，统一资源定位符，用于标识资源地址。All report resources must resolve as local relative paths before embedding.

Implement:

```python
def local_path(base: Path, raw: str, label: str) -> Path:
    parsed = urlparse(raw)
    if parsed.scheme or raw.startswith("//"):
        raise BuildError(f"{label}: remote or absolute URL is not allowed: {raw}")
    path = (base / raw).resolve()
    try:
        path.relative_to(base.resolve())
    except ValueError as exc:
        raise BuildError(f"{label}: path escapes the report directory: {raw}") from exc
    if not path.is_file():
        raise BuildError(f"{label}: missing file: {raw}")
    return path


def data_uri(path: Path) -> str:
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{media_type};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def local_url_fetcher(url: str, headers: dict[str, str] | None = None):
    if urlparse(url).scheme != "data":
        raise FatalURLFetchingError(f"remote resource blocked: {url}")
    return URLFetcher(allowed_protocols={"data"}, fail_on_errors=True).fetch(url, headers)
```

For named fonts, require `fc-match` to return the configured family. For a local font path, embed it as a `data:` `@font-face`. Reject invalid `accent_color`, missing images/fonts, remote images, and `../` escapes. Use Pillow only to warn when a raster image is below 1200 pixels wide.

- [ ] **Step 3: Add token rendering and print CSS**

Configure `MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table")`. Add stable IDs to level-two headings, embed standalone local images with alt-text captions, collect the contents, and transform only the three approved callout markers, bold `表：` captions, and italic `来源：` lines.

Escape every frontmatter and brand string with `html.escape` before placing it in HTML. The cover may embed optional local logo and cover image data, but missing optional values only produce warnings. Warn for optional metadata gaps, raster images under 1200 pixels, tables above six columns, and missing image/table captions. After render, assert `document.make_bookmark_tree()` contains the canonical section bookmarks.

The cover must render title, subtitle, date, authors, sector, region, classification, optional logo/cover image, and effective disclaimer. The effective disclaimer is the report frontmatter value when present, otherwise the brand default.

`report.css` must include:

```css
@page {
  size: A4;
  margin: 20mm 16mm 18mm;
  @top-left { content: "lustinus RESEARCH"; color: #A06B2C; font-size: 8pt; }
  @top-right { content: string(report-title); color: #667085; font-size: 8pt; }
  @bottom-left { content: string(classification); color: #667085; font-size: 8pt; }
  @bottom-right { content: counter(page) " / " counter(pages); color: #667085; font-size: 8pt; }
}
@page cover { margin: 0; @top-left { content: none; } @top-right { content: none; } @bottom-left { content: none; } @bottom-right { content: none; } }
:root { --ink: #20252B; --copper: #A06B2C; --fact: #2E6F62; --risk: #A33A32; }
html { color: var(--ink); font-size: 10pt; line-height: 1.55; }
body { counter-reset: figure table; }
.cover { page: cover; height: 297mm; padding: 28mm 24mm; box-sizing: border-box; border-top: 9mm solid var(--ink); }
.cover h1 { string-set: report-title content(); font-size: 28pt; line-height: 1.2; margin-top: 42mm; }
.classification { string-set: classification content(); }
.toc { break-after: page; }
.toc a::after { content: leader(".") target-counter(attr(href), page); }
.report-body > h1:first-child { display: none; }
h2 { break-before: page; border-top: 3px solid var(--copper); padding-top: 8mm; }
h3 { break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 8pt; }
table { counter-increment: table; }
caption::before { content: "表 " counter(table) " · "; }
thead { display: table-header-group; }
tr, figure, blockquote { break-inside: avoid; }
th, td { border: 0.3pt solid #CBD1D8; padding: 2mm; vertical-align: top; overflow-wrap: anywhere; }
figure img { display: block; max-width: 100%; max-height: 175mm; margin: 0 auto 2mm; }
figure { counter-increment: figure; }
figcaption::before { content: "图 " counter(figure) " · "; }
.source-line { color: #667085; font-size: 7.5pt; }
.callout { border-left: 3px solid var(--copper); background: #F7F3ED; padding: 3mm 4mm; }
.callout-fact { border-color: var(--fact); background: #F0F7F5; }
.callout-open-question { border-color: var(--risk); background: #FBF1F0; }
```

Replace only validated color/font tokens with `str.replace`; do not add a template engine.

- [ ] **Step 4: Render and publish transactionally**

```python
document = HTML(string=html_text, url_fetcher=local_url_fetcher).render(font_config=FontConfiguration())
page_count = len(document.pages)
document.write_pdf(staging / "report.pdf")
(staging / "report.html").write_text(html_text, encoding="utf-8")
(staging / "build-report.txt").write_text(build_log(page_count, warnings), encoding="utf-8")
publish_staged(staging, output_dir)
```

`build-report.txt` must record input path, generation time, builder version `0.1.0`, page count, every warning, and the structure/source/render/bookmark check results. A warning-free build must still say `warnings: none` and mark each check `pass`.

`publish_staged` backs up only the three known existing files, replaces all three, and restores the backup on any error. The command is:

```text
python3 build_report.py report.md --brand brand.yml --output output
```

Return `0` on success and `2` with a concrete message such as `build failed: report.md: missing required metadata: date` on validation/render failure.

- [ ] **Step 5: Run and commit the renderer slice**

```bash
python3 skills/jvc-research-report/scripts/check_package.py
git add skills/jvc-research-report/assets/report.css skills/jvc-research-report/scripts
git commit -m "Render local research reports to PDF"
```

Expected: valid build has exactly three files; invalid rebuild preserves their hashes.

## Task 4: Add the file-backed fixture and visual verification path

**Files:** Create `templates/industry-report.md`, `examples/research-report-example/report.md`, and `examples/research-report-example/assets/technology-routes.svg`; extend `scripts/check_package.py`.

- [ ] **Step 1: Create the canonical template**

The template must include complete frontmatter, all eleven canonical headings in order, all three callouts, one captioned table, one local-image example, and a source-index table with `编号 / 标题 / 机构或作者 / 日期 / 链接 / 来源类型 / 可信度` columns.

Use instructional bracket text such as `【填写研究口径；所有事实附来源】`; do not include blank claims that could be mistaken for evidence.

- [ ] **Step 2: Create a complete fictional fixture**

Create a report about `工业视觉质检（虚构示例）`, dated `2026-07-21`, classified `Internal`, with source IDs `S1`–`S3`. Every source row must say `虚构样例，仅用于版式回归`; no real market claim may appear.

Create a 1200-by-600 SVG (Scalable Vector Graphics，可缩放矢量图形，一种适合图表的矢量格式) with four labeled route boxes and no script, external reference, foreign object, logo, or copied brand asset.

- [ ] **Step 3: Extend the package check to build the tracked fixture**

After generating into a temporary directory, extract text with `pdftotext` and assert:

```python
assert "工业视觉质检" in extracted_text
for heading in ("研究设定与一页快照", "技术路线与商业可行性", "后续工作交接包", "来源索引"):
    assert heading in extracted_text
assert "lustinus RESEARCH" in html_text
assert "callout-fact" in html_text
assert "technology-routes.svg" not in html_text
assert "data:image/svg+xml;base64," in html_text
```

These checks prove the preview is self-contained and exposes no absolute local path.

- [ ] **Step 4: Run text, page, and visual checks**

```bash
rm -rf /tmp/jvc-research-report-check
python3 skills/jvc-research-report/scripts/build_report.py \
  examples/research-report-example/report.md \
  --brand skills/jvc-research-report/assets/brand.yml \
  --output /tmp/jvc-research-report-check
pdfinfo /tmp/jvc-research-report-check/report.pdf
pdftotext /tmp/jvc-research-report-check/report.pdf /tmp/jvc-research-report-check/report.txt
pdftoppm -png -r 110 /tmp/jvc-research-report-check/report.pdf /tmp/jvc-research-report-check/page
```

Expected: valid A4 pages; extracted title, canonical sections, and source index; one PNG (Portable Network Graphics，便携式网络图形，一种无损位图格式) per page.

Use the image viewer on the cover, contents, dense table, callout, figure, and source-index pages. Fail for clipping, horizontal overflow, missing glyphs, detached captions, accidental blank pages, or inconsistent page furniture.

- [ ] **Step 5: Commit the fixture**

```bash
git add skills/jvc-research-report/templates examples/research-report-example skills/jvc-research-report/scripts/check_package.py
git commit -m "Add research report fixture and visual checks"
```

## Task 5: Integrate routing, installation, and documentation

**Files:** Modify root setup/interface/registry/README/manifest, track-research handoff, checks, evals, and security policies.

- [ ] **Step 1: Add failing route-confusion expectations**

Add to `scripts/check-skill-evals.py:69-81`:

```python
("jvc-track-research", "jvc-research-report"),
("jvc-research-report", "jvc-track-research"),
("jvc-research-report", "jvc-ic-memo"),
```

Run `python3 scripts/check-skill-evals.py`.

Expected: failure listing the missing pairs and missing trigger/output coverage.

- [ ] **Step 2: Add root trigger and output cases**

Add this trigger case:

```json
{
  "id": "research-report-fixed-markdown-render",
  "prompt": "我已经有一份固定章节和 [S1] 来源索引的赛道研究 Markdown，请不要改内容，按 lustinus RESEARCH 版式生成可打印 PDF、HTML 预览和构建报告。",
  "expected_skill": "jvc-research-report",
  "prompt_signals": ["固定章节", "不要改内容", "lustinus RESEARCH", "PDF"],
  "skill_contract_signals": ["不重写", "report.pdf", "report.html", "build-report.txt"],
  "near_neighbors": [
    {"skill": "jvc-track-research", "why_not": "track-research creates research content; this prompt already has finished Markdown and asks only for validation and rendering."},
    {"skill": "jvc-ic-memo", "why_not": "ic-memo synthesizes company diligence; this is an industry-report renderer."}
  ]
}
```

Add `jvc-research-report` as a second near neighbor on the existing `track-research-sector-map` case. Add one `research_pdf` output case asserting the fixture, builder, stylesheet, template, and three output names.

Stage `evals/output/cases.json` later with `git add -f` because the tracked path is covered by an `output/` ignore rule.

- [ ] **Step 3: Register and document the new skill**

- Add `jvc-research-report` after `jvc-track-research` in `setup`.
- Add `jvc-research-report` after `jvc-track-research` in the `skills` array in `scripts/check-jvc-assets.sh`.
- Add `skills/jvc-research-report/SKILL.md` to root `agents/interface.yaml`.
- Add a registry row: finished industry Markdown → `lustinus RESEARCH` report outputs; not research or rewriting.
- Change the README badge from 12 to 13 skills; add overview row, short usage section, and `report.pdf` under `tracks/{track-slug}/`.
- Add `/jvc-research-report` to the completed-content handoff in `/jvc-track-research`.
- Bump root `manifest.json` to `0.3.0`, set `updated_at` to `2026-07-21`, and add `Branded research PDF and HTML previews` to `output_contracts`.
- Add local HTML/images/fonts/research PDFs to existing permission scopes. Keep `network_capable_scripts` empty and state that the renderer accepts only embedded `data:` resources.
- Add both report scripts to `scripts/check-review-fixes.sh`, and run `check_package.py` before governance.

- [ ] **Step 4: Run integration checks**

```bash
bash scripts/check-jvc-assets.sh
python3 scripts/check-skill-evals.py
python3 skills/jvc-research-report/scripts/check_package.py
```

Expected: asset check passes; evals report `14 trigger cases, 13 output cases`; package check passes.

- [ ] **Step 5: Commit integration**

```bash
git add setup agents/interface.yaml library/skill-registry.md README.md manifest.json \
  skills/jvc-track-research/SKILL.md scripts/check-jvc-assets.sh scripts/check-review-fixes.sh \
  scripts/check-skill-evals.py evals/trigger_cases.json security/network_policy.json security/permission_policy.json
git add -f evals/output/cases.json
git commit -m "Integrate research report skill"
```

## Task 6: Update production governance and trust evidence

**Files:** Modify Skill Intermediate Representation, scorecards, trust reports, Review Studio, and `scripts/check-governance.py`.

- [ ] **Step 1: Confirm the expected governance failure**

```bash
python3 scripts/check-governance.py
```

Expected: non-zero exit with `skill-ir skill mismatch`.

- [ ] **Step 2: Add the new semantic contract**

Add to `reports/skill-ir.json`:

```json
{
  "name": "jvc-research-report",
  "job": "Validate completed fixed-format local industry research Markdown and render a lustinus RESEARCH PDF, HTML preview, and build report without changing content.",
  "outputs": ["PDF research report", "HTML preview", "Build report"],
  "near_neighbors": ["jvc-track-research", "jvc-ic-memo"],
  "scripts": [
    "skills/jvc-research-report/scripts/build_report.py",
    "skills/jvc-research-report/scripts/check_package.py"
  ],
  "failure_modes": [
    "Rewrites or supplements research content",
    "Fetches remote assets",
    "Accepts unresolved source IDs",
    "Produces clipped or overflowing pages",
    "Overwrites a previous successful build after failure"
  ]
}
```

Update the route and output scorecards to the actual counts and add the new rows. State that file-backed rendering plus visual inspection improves evidence but is not model-executed or blind-review evidence.

Add the two scripts and pinned dependencies to both trust reports. Add the rendered fixture evidence to the existing Output Lab gate, keep its status `warn`, and do not upgrade the public-release claim.

- [ ] **Step 3: Add a narrow trust-hash refresh option**

Add `--write-hash` to the existing governance script with:

```python
def write_trust_hash(value: str) -> None:
    json_path = ROOT / "reports/trust_report.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    data["package_sha256"] = value
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    markdown_path = ROOT / "reports/trust_report.md"
    markdown = markdown_path.read_text(encoding="utf-8")
    updated, count = re.subn(r"`[0-9a-f]{64}`", f"`{value}`", markdown, count=1)
    if count != 1:
        raise AssertionError("trust report markdown hash was not uniquely identifiable")
    markdown_path.write_text(updated, encoding="utf-8")
```

When `--write-hash` is present, compute and write the hash before normal checks. Reports are outside the hash scope, so the value stays stable.

- [ ] **Step 4: Refresh the source-contract hash and run governance**

SHA-256 = Secure Hash Algorithm 256-bit，256 位安全哈希算法，用于生成源文件集合的内容指纹。

```bash
python3 scripts/check-governance.py --write-hash
python3 scripts/check-governance.py
```

Expected: both exit `0`; the second prints one 64-character lowercase hash that appears in both trust reports.

- [ ] **Step 5: Commit governance after the source set is final**

```bash
git add reports scripts/check-governance.py
git commit -m "Govern research report skill"
```

## Task 7: Final regression and actual artifact inspection

**Files:** Verify only; do not add generated report files, page images, caches, or visual-companion files.

- [ ] **Step 1: Run all skill-local gates**

```bash
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/validate_skill.py skills/jvc-research-report
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/resource_boundary_check.py skills/jvc-research-report --max-initial-tokens 1000
python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/trigger_eval.py \
  --description-file skills/jvc-research-report/SKILL.md \
  --cases skills/jvc-research-report/evals/trigger_cases.json \
  --semantic-config skills/jvc-research-report/evals/semantic_config.json
python3 skills/jvc-research-report/scripts/check_package.py
```

Expected: all exit `0`; no initial-load warning; package check passes.

- [ ] **Step 2: Run the full repository regression**

```bash
bash scripts/check-review-fixes.sh
git diff --check
```

Expected: all asset, workbook, document, eval, governance, syntax, and whitespace checks pass.

- [ ] **Step 3: Rebuild and visually inspect the final sample**

Repeat Task 4's build and page rendering after all governance edits. Inspect the cover, contents, dense table, callouts, figure, and source index. The work is incomplete until the real PDF has no clipping, overflow, missing glyphs, unexpected blank pages, detached captions, or inconsistent page furniture.

- [ ] **Step 4: Clean and audit the commit boundary**

```bash
find skills/jvc-research-report scripts -type d -name __pycache__ -prune -exec rm -rf {} +
git status --short
git log --oneline -7
```

Expected: no generated report, rendered page, cache, or temporary file is tracked. Preserve the pre-existing untracked `.superpowers/` and `assets/xiaohongshu/jvc-track-research/` trees unchanged.

- [ ] **Step 5: Stop before user-level installation**

Do not run `./setup` automatically because it writes to user-level skill directories. Report local completion and offer installation as a separate confirmed action.

## Final acceptance checklist

- `/jvc-research-report` activates only for completed fixed-format local Markdown rendering.
- The report shows `lustinus RESEARCH` exactly and contains no copied third-party brand assets.
- The builder never rewrites content or fetches remote assets.
- Valid input produces exactly the three contracted files.
- Invalid input returns a specific error and preserves the previous successful outputs.
- Current `/jvc-track-research` headings work after required frontmatter is added.
- Source IDs are unique and complete.
- HTML is self-contained and contains no absolute local paths.
- PDF contains cover, contents, sections, captions, citations, page furniture, and page numbers.
- Text extraction, rendered-page inspection, Yao production gates, repository evals, governance, and full regression pass.
- User-level installation requires separate confirmation.

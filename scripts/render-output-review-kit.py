#!/usr/bin/env python3
"""Render the blind-review JSON as a human-readable, offline HTML page."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from io import StringIO
from pathlib import Path
from typing import Any


CELL_LINE = re.compile(r'^- `([A-Z]+\d+)` \(([^)]+)\): (.*)$')
CELL_ADDRESS = re.compile(r"^([A-Z]+)(\d+)$")
HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
ORDERED_ITEM = re.compile(r"^\s*\d+\.\s+(.+)$")
BULLET_ITEM = re.compile(r"^\s*[-*+]\s+(.+)$")
TABLE_DIVIDER = re.compile(r"^\|?(?:\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?$")
MARKDOWN_LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+)\)")
URL = re.compile(r'https?://[^\s<>"]+')
URL_TRAILING_PUNCTUATION = ".,;:!?，。；：！？)]}"
MAX_SHEET_ROWS = 2_000
MAX_SHEET_COLUMNS = 200
MAX_SHEET_CELLS = 50_000
FORBIDDEN_BLIND_FIELDS = (
    "output_blind_answer_key",
    "expected_winner",
    "variant_a_role",
    "variant_b_role",
    "score_winner_role",
    "with_skill",
)


def escape(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def emphasis(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escape(text))


def linkify_urls(text: str) -> str:
    rendered: list[str] = []
    position = 0
    for match in URL.finditer(text):
        rendered.append(emphasis(text[position : match.start()]))
        candidate = match.group(0)
        url = candidate.rstrip(URL_TRAILING_PUNCTUATION)
        trailing = candidate[len(url) :]
        if url:
            safe_url = escape(url)
            rendered.append(f'<a href="{safe_url}" target="_blank" rel="noreferrer">{safe_url}</a>')
        rendered.append(emphasis(trailing))
        position = match.end()
    rendered.append(emphasis(text[position:]))
    return "".join(rendered)


def render_plain(text: str) -> str:
    rendered: list[str] = []
    position = 0
    for match in MARKDOWN_LINK.finditer(text):
        rendered.append(linkify_urls(text[position : match.start()]))
        safe_url = escape(match.group(2))
        rendered.append(f'<a href="{safe_url}" target="_blank" rel="noreferrer">{emphasis(match.group(1))}</a>')
        position = match.end()
    rendered.append(linkify_urls(text[position:]))
    return "".join(rendered)


def inline(text: str) -> str:
    parts = text.split("`")
    return "".join(
        f"<code>{escape(part)}</code>" if index % 2 else render_plain(part)
        for index, part in enumerate(parts)
    )


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_table(rows: list[list[str]], class_name: str = "data-table") -> str:
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    head = "".join(f"<th>{inline(cell)}</th>" for cell in normalized[0])
    body = "".join(
        "<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>"
        for row in normalized[1:]
    )
    return f'<div class="table-scroll"><table class="{class_name}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def render_csv(text: str) -> str:
    rows = list(csv.reader(StringIO(text)))
    return render_table(rows, "data-table csv-table")


def decoded_cell_value(raw: str) -> str:
    if raw.startswith('"') and raw.endswith('"'):
        try:
            value = json.loads(raw)
            return str(value)
        except json.JSONDecodeError:
            pass
    return raw


def column_number(letters: str, limit: int = MAX_SHEET_COLUMNS) -> int:
    number = 0
    for letter in letters:
        number = number * 26 + ord(letter) - ord("A") + 1
        if number > limit:
            return limit + 1
    return number


def column_letters(number: int) -> str:
    value = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        value = chr(ord("A") + remainder) + value
    return value


def render_cell_dump(lines: list[str]) -> str:
    cells: dict[tuple[int, int], str] = {}
    max_row = 0
    max_column = 0
    if len(lines) > MAX_SHEET_CELLS:
        return '<p class="render-warning">工作表超过安全渲染上限，请展开原始文本核对。</p>'
    for line in lines:
        match = CELL_LINE.match(line)
        address = CELL_ADDRESS.match(match.group(1)) if match else None
        if not match or not address:
            continue
        row_text = address.group(2)
        if len(row_text) > len(str(MAX_SHEET_ROWS)):
            return '<p class="render-warning">工作表地址超过安全渲染上限，请展开原始文本核对。</p>'
        row = int(row_text)
        column = column_number(address.group(1))
        if row < 1 or row > MAX_SHEET_ROWS or column > MAX_SHEET_COLUMNS:
            return '<p class="render-warning">工作表地址超过安全渲染上限，请展开原始文本核对。</p>'
        cells[(row, column)] = decoded_cell_value(match.group(3))
        max_row = max(max_row, row)
        max_column = max(max_column, column)
    if max_row * max_column > MAX_SHEET_CELLS:
        return '<p class="render-warning">工作表网格超过安全渲染上限，请展开原始文本核对。</p>'
    rows = [["行", *(column_letters(column) for column in range(1, max_column + 1))]]
    for row in range(1, max_row + 1):
        rows.append([str(row), *(cells.get((row, column), "") for column in range(1, max_column + 1))])
    return render_table(rows, "data-table sheet-grid")


def looks_like_csv(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 2 or any(line.lstrip().startswith(("#", "|", "-", "*", ">")) for line in lines):
        return False
    try:
        rows = list(csv.reader(lines))
    except csv.Error:
        return False
    widths = {len(row) for row in rows}
    return len(widths) == 1 and next(iter(widths), 0) > 1


def is_block_start(lines: list[str], index: int) -> bool:
    line = lines[index]
    stripped = line.strip()
    if not stripped:
        return True
    if (
        stripped.startswith("```")
        or HEADING.match(line)
        or CELL_LINE.match(line)
        or BULLET_ITEM.match(line)
        or ORDERED_ITEM.match(line)
        or stripped.startswith(">")
        or stripped in {"---", "***", "___"}
    ):
        return True
    return index + 1 < len(lines) and "|" in line and TABLE_DIVIDER.match(lines[index + 1].strip()) is not None


def render_markdown(text: str) -> str:
    if not text.strip():
        return '<p class="empty">无正文。</p>'
    if looks_like_csv(text):
        return render_csv(text)

    lines = text.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        if stripped.startswith("```"):
            language = stripped[3:].strip().lower()
            index += 1
            fenced: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                fenced.append(lines[index])
                index += 1
            index += index < len(lines)
            content = "\n".join(fenced)
            output.append(render_csv(content) if language == "csv" else f'<pre class="code-block"><code>{escape(content)}</code></pre>')
            continue

        heading = HEADING.match(line)
        if heading:
            level = min(len(heading.group(1)) + 1, 6)
            output.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            index += 1
            continue

        if index + 1 < len(lines) and "|" in line and TABLE_DIVIDER.match(lines[index + 1].strip()):
            rows = [table_cells(line)]
            index += 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(table_cells(lines[index]))
                index += 1
            output.append(render_table(rows))
            continue

        if CELL_LINE.match(line):
            cells: list[str] = []
            while index < len(lines) and CELL_LINE.match(lines[index]):
                cells.append(lines[index])
                index += 1
            output.append(render_cell_dump(cells))
            continue

        bullet = BULLET_ITEM.match(line)
        if bullet:
            items: list[str] = []
            while index < len(lines):
                match = BULLET_ITEM.match(lines[index])
                if not match or CELL_LINE.match(lines[index]):
                    break
                items.append(f"<li>{inline(match.group(1))}</li>")
                index += 1
            output.append(f'<ul class="content-list">{"".join(items)}</ul>')
            continue

        ordered = ORDERED_ITEM.match(line)
        if ordered:
            items = []
            while index < len(lines):
                match = ORDERED_ITEM.match(lines[index])
                if not match:
                    break
                items.append(f"<li>{inline(match.group(1))}</li>")
                index += 1
            output.append(f'<ol class="content-list">{"".join(items)}</ol>')
            continue

        if stripped.startswith(">"):
            quotes: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quotes.append(lines[index].strip().lstrip(">").strip())
                index += 1
            output.append(f"<blockquote>{inline(' '.join(quotes))}</blockquote>")
            continue

        if stripped in {"---", "***", "___"}:
            output.append("<hr>")
            index += 1
            continue

        paragraph = [stripped]
        index += 1
        while index < len(lines) and not is_block_start(lines, index):
            paragraph.append(lines[index].strip())
            index += 1
        output.append(f"<p>{inline(' '.join(paragraph))}</p>")

    return "\n".join(output)


def status_label(status: str) -> str:
    return {
        "awaiting-decision": "待判断",
        "needs-fix": "需修正",
        "ready-for-adjudication": "可裁决",
    }.get(status, status)


def footer_text(state: dict[str, Any]) -> str:
    return {
        "awaiting-decision": "尚未记录人工判断。",
        "needs-fix": "当前判断字段不完整，需要修正后才能裁决。",
        "ready-for-adjudication": "人工判断字段完整，可以进入裁决。",
    }.get(str(state.get("status", "")), str(state.get("blocking_reason", "")))


def render_rubric(items: list[dict[str, Any]]) -> str:
    return "".join(
        f'<li><code>{escape(item.get("id", ""))}</code><span>{escape(item.get("description", ""))}</span>'
        f'<strong>{escape(item.get("weight", ""))}</strong></li>'
        for item in items
    )


def render_variant(label: str, output: str) -> str:
    return f"""<article class="variant">
            <header class="variant-head"><h4>版本 {label}</h4><span>默认阅读视图</span></header>
            <div class="rendered-markdown">{render_markdown(output)}</div>
            <details class="raw"><summary>查看原始文本</summary><pre>{escape(output)}</pre></details>
          </article>"""


def render_cases(cases: list[dict[str, Any]]) -> str:
    cards: list[str] = []
    for number, case in enumerate(cases, start=1):
        state = case.get("decision_state", {})
        status = str(state.get("status", "awaiting-decision"))
        cards.append(
            f"""
      <article class="case-card" id="case-{escape(case.get('case_id', ''))}">
        <header class="case-head">
          <div><span>案例 {number:02d}</span><h3>{escape(case.get('case_id', ''))}</h3></div>
          <strong class="status {escape(status)}">{escape(status_label(status))}</strong>
        </header>
        <details class="brief" open>
          <summary>任务与审阅标准</summary>
          <div class="prompt rendered-markdown">{render_markdown(str(case.get('prompt', '')))}</div>
          <ul class="rubric">{render_rubric(case.get('rubric', []))}</ul>
        </details>
        <section class="variants" aria-label="匿名输出版本">
          {render_variant("A", str(case.get("variant_a", {}).get("output", "")))}
          {render_variant("B", str(case.get("variant_b", {}).get("output", "")))}
        </section>
        <footer>{escape(footer_text(state))}</footer>
      </article>"""
        )
    return "\n".join(cards)


def review_steps(payload: dict[str, Any]) -> list[str]:
    return [
        "先阅读每个案例的任务口径与六项审阅标准。",
        "对照版本 A 与版本 B 的结论、证据、冲突处理和下一步动作。",
        "分别记录胜者 A/B、0–1 置信度和简短理由；不确定时降低置信度，不猜隐藏标签。",
        "完成两个案例后，将判断交给项目维护者登记并裁决。",
    ]


def privacy_steps() -> list[str]:
    return [
        "答案密钥未嵌入本页面。",
        "做出两个判断前不要查看隐藏标签或答案密钥。",
        "理由中不要粘贴私人数据。",
        "未完成的判断必须保持待定，不能计为人工同意。",
    ]


def render_page(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    steps = "".join(f"<li>{escape(step)}</li>" for step in review_steps(payload))
    privacy = "".join(f"<li>{escape(item)}</li>" for item in privacy_steps())
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VC Analyst 2.0 输出盲审</title>
  <style>
    :root {{ --navy:#17365d; --ink:#20242a; --muted:#6e6a64; --line:#ded8cf; --paper:#fff; --soft:#f6f3ed; --accent:#b45309; --ok:#26734d; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; background:#eeeae3; color:var(--ink); font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }}
    a {{ color:#155a9c; overflow-wrap:anywhere; }}
    code, pre {{ font-family:"SFMono-Regular",Consolas,monospace; }}
    .topbar {{ position:sticky; top:0; z-index:20; display:flex; justify-content:space-between; gap:18px; padding:12px max(20px,calc((100vw - 1560px)/2)); background:rgba(255,255,255,.96); border-bottom:1px solid var(--line); }}
    .topbar strong {{ color:var(--navy); }}
    .topbar nav {{ display:flex; gap:18px; }}
    .topbar a {{ color:var(--navy); text-decoration:none; }}
    main {{ max-width:1560px; margin:auto; padding:28px 22px 80px; }}
    .hero, .panel, .case-card {{ background:var(--paper); border:1px solid var(--line); border-radius:12px; }}
    .hero {{ padding:34px; }}
    .eyebrow, .case-head span {{ color:var(--muted); font-size:12px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }}
    h1 {{ margin:5px 0 8px; color:var(--navy); font:700 clamp(36px,5vw,68px)/1.05 Georgia,"Songti SC",serif; }}
    .lede {{ max-width:780px; margin:0; color:var(--muted); font-size:19px; }}
    .stats {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-top:24px; }}
    .stats div {{ padding:14px 16px; background:var(--soft); border-radius:8px; }}
    .stats span {{ display:block; color:var(--muted); font-size:13px; }}
    .stats strong {{ color:var(--navy); font-size:30px; }}
    .guide {{ display:grid; grid-template-columns:1.25fr .75fr; gap:16px; margin:18px 0; }}
    .panel {{ padding:20px 24px; }}
    h2, h3, h4 {{ color:var(--navy); }}
    h2 {{ margin:0 0 10px; }}
    .case-card {{ margin:22px 0; padding:24px; scroll-margin-top:64px; }}
    .case-head {{ display:flex; justify-content:space-between; gap:16px; align-items:start; }}
    .case-head h3 {{ margin:2px 0 0; font-size:24px; overflow-wrap:anywhere; }}
    .status {{ padding:5px 11px; border:1px solid var(--line); border-radius:999px; color:var(--accent); white-space:nowrap; }}
    .status.ready-for-adjudication {{ color:var(--ok); }}
    details.brief {{ margin:18px 0; padding:14px 16px; background:var(--soft); border-radius:8px; }}
    summary {{ color:var(--navy); cursor:pointer; font-weight:700; }}
    .prompt {{ margin-top:14px; padding-bottom:14px; border-bottom:1px solid var(--line); }}
    .rubric {{ list-style:none; margin:14px 0 0; padding:0; display:grid; gap:8px; }}
    .rubric li {{ display:grid; grid-template-columns:190px 1fr 42px; gap:12px; align-items:start; }}
    .rubric code {{ overflow-wrap:anywhere; word-break:break-word; font-size:12px; }}
    .rubric strong {{ text-align:right; }}
    .variants {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:18px; align-items:start; }}
    .variant {{ min-width:0; border:1px solid var(--line); border-radius:10px; background:#fff; overflow:hidden; }}
    .variant-head {{ position:sticky; top:49px; z-index:10; display:flex; justify-content:space-between; align-items:center; padding:12px 16px; background:#eef3f8; border-bottom:1px solid #ccd7e3; }}
    .variant-head h4 {{ margin:0; font-size:18px; }}
    .variant-head span {{ color:var(--muted); font-size:12px; }}
    .rendered-markdown {{ padding:18px; overflow-wrap:anywhere; }}
    .rendered-markdown h2 {{ margin:1.5em 0 .55em; padding-bottom:.25em; border-bottom:1px solid var(--line); font-size:24px; }}
    .rendered-markdown h3 {{ margin:1.35em 0 .45em; font-size:20px; }}
    .rendered-markdown h4, .rendered-markdown h5, .rendered-markdown h6 {{ margin:1.2em 0 .4em; font-size:17px; }}
    .rendered-markdown p {{ margin:.65em 0; }}
    .content-list {{ margin:.55em 0 1em; padding-left:1.45em; }}
    .content-list li {{ margin:.28em 0; }}
    blockquote {{ margin:1em 0; padding:.6em 1em; border-left:4px solid #9aaabd; background:var(--soft); color:var(--muted); }}
    .table-scroll {{ margin:12px 0 18px; overflow:auto; border:1px solid var(--line); border-radius:7px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; line-height:1.45; }}
    th {{ position:sticky; top:0; background:#eef3f8; color:var(--navy); text-align:left; }}
    th, td {{ min-width:90px; padding:8px 10px; border-bottom:1px solid var(--line); border-right:1px solid var(--line); vertical-align:top; }}
    tr:last-child td {{ border-bottom:0; }}
    th:last-child, td:last-child {{ border-right:0; }}
    .sheet-grid th, .sheet-grid td {{ min-width:130px; }}
    .sheet-grid th:first-child, .sheet-grid td:first-child {{ position:sticky; left:0; z-index:2; min-width:46px; width:46px; background:#f4f6f8; color:var(--muted); text-align:right; }}
    .sheet-grid th:first-child {{ z-index:3; }}
    .render-warning {{ padding:12px 14px; border-left:4px solid var(--accent); background:#fff7ed; color:#7c2d12; }}
    .raw {{ margin:0 16px 16px; padding:10px 12px; border:1px dashed var(--line); border-radius:7px; }}
    .raw pre, .code-block {{ white-space:pre-wrap; overflow-wrap:anywhere; font-size:12px; line-height:1.55; }}
    footer {{ margin-top:16px; padding-top:12px; border-top:1px solid var(--line); color:var(--muted); font-size:13px; }}
    @media (max-width:900px) {{
      .stats, .guide, .variants {{ grid-template-columns:1fr; }}
      .rubric li {{ grid-template-columns:1fr; }}
      .rubric strong {{ text-align:left; }}
      .variant-head {{ position:static; }}
      main {{ padding-inline:12px; }}
      .hero, .case-card {{ padding:18px; }}
      .topbar nav {{ display:none; }}
    }}
  </style>
</head>
<body>
  <header class="topbar"><strong>VC Analyst 2.0 · 输出盲审</strong><nav><a href="#guide">审阅说明</a><a href="#cases">案例</a></nav></header>
  <main>
    <section class="hero">
      <span class="eyebrow">Blind A/B Human Review</span>
      <h1>先读结论，再核证据</h1>
      <p class="lede">报告默认按 Markdown 排版；工作簿单元格导出自动转成表格。两个版本仍保持匿名，原始文本保留在折叠区供核对。</p>
      <div class="stats">
        <div><span>案例</span><strong>{escape(summary['case_count'])}</strong></div>
        <div><span>可裁决</span><strong>{escape(summary['ready_for_adjudication_count'])}</strong></div>
        <div><span>待判断</span><strong>{escape(summary['pending_decision_count'])}</strong></div>
        <div><span>异常</span><strong>{escape(summary['invalid_decision_count'])}</strong></div>
      </div>
    </section>
    <section class="guide" id="guide">
      <article class="panel"><h2>审阅流程</h2><ol>{steps}</ol></article>
      <aside class="panel"><h2>盲审边界</h2><ul>{privacy}</ul></aside>
    </section>
    <section id="cases">{render_cases(payload.get("cases", []))}</section>
  </main>
</body>
</html>
"""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_output(page: str, payload: dict[str, Any]) -> None:
    require(page.count('class="variant"') == len(payload.get("cases", [])) * 2, "variant count mismatch")
    require(page.count('class="rendered-markdown"') >= len(payload.get("cases", [])) * 2, "rendered views are missing")
    require('class="data-table' in page, "Markdown tables were not rendered")
    require('class="data-table sheet-grid"' in page, "workbook cell dump was not rendered as a spreadsheet grid")
    require('<details class="raw">' in page, "raw source fallback is missing")
    require("<div class=\"variant\"><h4>" not in page, "legacy raw variant layout returned")
    require("scripts/yao.py" not in page, "invalid Yao command leaked into reviewer page")
    for field in FORBIDDEN_BLIND_FIELDS:
        require(field not in page, f"blind mapping field leaked: {field}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("reports/output_review_kit.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/output_review_kit.html"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    page = render_page(payload)
    if args.check:
        check_output(page, payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page, encoding="utf-8")
    print(f"rendered {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

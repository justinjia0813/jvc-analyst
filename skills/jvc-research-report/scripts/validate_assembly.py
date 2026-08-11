#!/usr/bin/env python3
"""Read-only assembly validator for the canonical research-report.md.

Two-stage Research Report contract:

1. 组装：从 Track Research、Knowledge Tree、Market Sizing 和可选的 Comps/DD 组装
   `research-report.md`。本脚本只读地核对组装产物：
   - 来源标识继承：报告引用的每个 `[S<n>]` 必须已存在于上游产物；
   - 事实数字继承：报告正文（frontmatter 除外）出现的每个数字必须已存在于
     上游产物（复用 IC Memo 终版校验器的数字归一化，不改其语义）。来源索引的
     日期/URL/来源 ID 属于元数据，不参与数字继承，但其描述单元格中的其他数字
     同样必须继承上游；标签括号内的数字同样参与继承。只做四位年份 `N` 与
     `N年` 的等价归一化；亿/万 量纲换算继续保守拒绝（错误信息提示疑似单位
     表示不一致并给出上游单位表示）；
   - 证据状态标签继承：`[模型估算]`、`[未知/待验证]`、`[用户观察]`、
     `[推测]`、`[创始人自述]` 等标签只能继承上游（半角 `[...]` 与全角
     `【...】` 等价），不能由报告自行引入；含 估算/未知/待验证/观察/假设/
     自述/推测/核实/访谈 关键字、但不在白名单中的未知标签一律拒绝；
   - frontmatter 白名单：组装路径只允许当前 canonical 已知顶层键
     title/subtitle/date/authors/sector/region/classification/cover_image/
     disclaimer，未知键拒绝（不改变 build_report 直接发布兼容性）；
   - 覆盖缺口可见：报告必须包含 `未核实与待补证据`（或 `覆盖缺口`）章节，
     且对每个缺失的可选上游输入（如 Comps/DD）按规范名在章节中显式列出。
2. 发布：已有完整 canonical `research-report.md` 时直接进入渲染
   （build_report.py，直接发布模式）。直接发布信任用户对 canonical 的声明：
   build_report 只校验文档内部一致性（章节/来源索引内自洽/本地资源），
   **不证明** assembly 继承或 Research Core 审计；如需证据继承校验，必须提供
   上游产物并运行本脚本。

边界（与 IC Memo 终版校验器同性质）：本校验是 set-based token 继承——只要
数字/标签 token 在上游出现过，就能在报告中复用（包括拼进全新主张）；它不能
证明重组句子的语义等价。主张级审计仍需上游 claim 与人工复核。

本脚本只使用 Python 标准库；数字归一化复用
`skills/jvc-ic-memo/scripts/validate_final.py` 的 `numbers`（上游侧）与
`NUMBER`/`CHINESE_QUANTITY`/`UNIT_ALIASES`（报告侧），不改变 IC 语义。
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

_IC_MEMO_SCRIPTS = (
    Path(__file__).resolve().parents[3] / "skills" / "jvc-ic-memo" / "scripts"
)
sys.path.insert(0, str(_IC_MEMO_SCRIPTS))

from validate_final import (  # noqa: E402  (reused IC number normalization)
    CHINESE_QUANTITY,
    NUMBER,
    UNIT_ALIASES,
    numbers,
)

SOURCE_REFERENCE = re.compile(r"\[S(\d+)\]", re.IGNORECASE)
# 报告侧数字提取只移除 [S<n>] 来源引用；标签括号内的数字仍参与继承（1b）。
SOURCE_ONLY = re.compile(
    r"\[[ \t]*S\d+(?:[ \t]*(?:[,，、;/+&]|[-–—])[ \t]*S?\d+)*[ \t]*\]",
    re.IGNORECASE,
)
HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)[ \t]*#*[ \t]*$")
FRONTMATTER = re.compile(r"\A---[ \t]*\r?\n.*?\r?\n---[ \t]*\r?\n", re.DOTALL)
# 证据状态标签同时接受半角 [...] 与全角 【...】（生态内两种写法都在使用）。
MARKER = re.compile(r"\[[^\]\n]*\]|【[^】\n]*】")
FRONTMATTER_KEY = re.compile(r"^(?P<key>[^:\s][^:]*?)\s*:")
SOURCE_INDEX_ID_CELL = re.compile(r"^\s*\|\s*S\d+\s*\|", re.IGNORECASE)
URL_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://\S+")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
FOUR_DIGIT = re.compile(r"\d{4}")

# 内在证据状态标签：组装器只能继承上游已存在的标签，不能新造。
INTERNAL_LABELS = (
    "[未核实]",
    "[推测]",
    "[创始人自述]",
    "[公司自述]",
    "[用户关注点]",
    "[用户观察]",
    "[用户假设]",
    "[模型估算]",
    "[未知/待验证]",
    "[未披露]",
    "[需要用户提供]",
    "[待确认]",
    "[待补充]",
    "[未覆盖]",
    "[第三方事实]",
    "[公司口径]",
    "[证据缺口]",
)
# 含这些关键字、但不在 INTERNAL_LABELS 中的未知标签一律拒绝（封堵未来新标签）。
LABEL_KEYWORDS = re.compile(r"估算|未知|待验证|观察|假设|自述|推测|核实|访谈")
# 组装路径 canonical frontmatter 只允许以下顶层键；未知键直接拒绝（1d）。
FRONTMATTER_KEYS = (
    "title",
    "subtitle",
    "date",
    "authors",
    "sector",
    "region",
    "classification",
    "cover_image",
    "disclaimer",
)
GAP_HEADINGS = ("未核实与待补证据", "覆盖缺口")
MISSING_INPUT_NAMES = {
    "track-research": ("track-research", "landscape", "赛道研究"),
    "knowledge-tree": ("knowledge-tree", "knowledge_tree", "知识树"),
    "market-sizing": ("market-sizing", "市场规模"),
    "comps-dd": ("comps-dd", "Comps/DD", "03-comps-dd.md", "可比公司"),
}
REQUIRED_INPUTS = ("track-research", "knowledge-tree", "market-sizing")
OPTIONAL_INPUTS = ("comps-dd",)


class AssemblyError(RuntimeError):
    pass


def split_frontmatter(text: str) -> tuple[str, str]:
    match = FRONTMATTER.match(text)
    if match is None:
        return "", text
    return match.group(0), text[match.end() :]


def split_source_index(body: str) -> tuple[str, str]:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if match and match.group(1).strip() in ("来源索引",):
            return "\n".join(lines[:index]), "\n".join(lines[index:])
    return body, ""


def source_ids(text: str) -> set[str]:
    return {f"S{int(number)}" for number in SOURCE_REFERENCE.findall(text)}


def market_sizing_source_ids(text: str) -> set[str]:
    """sources 行用 stdlib csv.reader 解析：支持带引号的逗号（如 "S1, S4"）。"""
    found: set[str] = set()
    try:
        rows = csv.reader(io.StringIO(text))
        for fields in rows:
            if len(fields) >= 2 and fields[0].strip() == "sources":
                for row_id in re.findall(r"S\d+", fields[1], flags=re.IGNORECASE):
                    found.add(row_id.upper())
    except csv.Error:
        pass
    return found


def read_inputs(paths: dict[str, Path]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for name, path in paths.items():
        if path is None:
            texts[name] = ""
            continue
        if name == "knowledge-tree" and path.is_dir():
            parts = []
            for child in sorted(path.iterdir()):
                if not child.is_file():
                    continue
                try:
                    parts.append(child.read_text(encoding="utf-8"))
                except (OSError, UnicodeError) as error:
                    raise AssemblyError(
                        f"cannot read knowledge-tree: {child.name}: {error}"
                    ) from error
            texts[name] = "\n".join(parts)
            continue
        try:
            texts[name] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise AssemblyError(f"cannot read {name}: {path}: {error}") from error
    return texts


def check_frontmatter_keys(frontmatter: str) -> list[str]:
    errors: list[str] = []
    for line in frontmatter.splitlines():
        match = FRONTMATTER_KEY.match(line)
        if match and match.group("key") not in FRONTMATTER_KEYS:
            errors.append(f"unknown frontmatter key: {match.group('key')}")
    return errors


def report_numbers(text: str) -> set[str]:
    """报告侧数字提取：只移除 `[S<n>]` 来源引用，不剥离标签括号（1b）。"""
    text = SOURCE_ONLY.sub("", text)
    found: set[str] = set()
    for match in NUMBER.finditer(text):
        number = re.sub(r"[\s,]", "", match.group("number"))
        units: list[str] = []
        for group in ("prefix", "suffix"):
            unit = match.group(group)
            if unit:
                unit = unit.lower()
                units.append(UNIT_ALIASES.get(unit, unit))
        found.add(number + "".join(units))
    for match in CHINESE_QUANTITY.finditer(text):
        unit = match.group("unit")
        found.add(match.group("number") + UNIT_ALIASES.get(unit, unit))
    return found


def clean_source_index(source_index: str) -> str:
    """来源索引是元数据载体：日期/URL/来源 ID 不参与数字继承，
    描述单元格中的其他数字仍须继承上游（1c）。"""
    cleaned = URL_TOKEN.sub("", ISO_DATE.sub("", source_index))
    lines = []
    for line in cleaned.splitlines():
        if line.lstrip().startswith("|"):
            line = SOURCE_INDEX_ID_CELL.sub("|", line)
        lines.append(line)
    return "\n".join(lines)


def expand_year_tokens(tokens: set[str]) -> set[str]:
    """四位年份最小归一化：`2026` 与 `2026年` 等价（1f）。"""
    expanded = set(tokens)
    for token in tokens:
        if FOUR_DIGIT.fullmatch(token):
            expanded.add(token + "年")
        elif FOUR_DIGIT.fullmatch(token[:-1]) and token.endswith("年"):
            expanded.add(token[:-1])
    return expanded


SCALE_UNIT = re.compile(r"^(?P<value>\d+(?:\.\d+)?)(?P<unit>亿美元|万美元|亿元|万元)$")


def scale_unit_hint(number: str, upstream: set[str]) -> str | None:
    """亿/万 换算继续保守拒绝，只在错误信息里提示疑似单位表示不一致（1f）。"""
    match = SCALE_UNIT.fullmatch(number)
    if not match:
        return None
    scale = 1e8 if match.group("unit").startswith("亿") else 1e4
    target = float(match.group("value")) * scale
    for candidate in sorted(upstream):
        candidate_match = SCALE_UNIT.fullmatch(candidate)
        if not candidate_match:
            continue
        candidate_scale = 1e8 if candidate_match.group("unit").startswith("亿") else 1e4
        if abs(float(candidate_match.group("value")) * candidate_scale - target) < 1e-6:
            return candidate
    return None


def gap_section(body: str) -> str:
    lines = body.splitlines()
    active = False
    captured: list[str] = []
    for line in lines:
        match = HEADING.match(line)
        if match and match.group(1).strip() in GAP_HEADINGS:
            active = True
            captured.append(line)
            continue
        if active and match and match.group(1).strip() not in GAP_HEADINGS:
            break
        if active:
            captured.append(line)
    return "\n".join(captured)


def check_coverage_gaps(upstreams: dict[str, str], provided: set[str], body: str) -> list[str]:
    errors: list[str] = []
    gap = gap_section(body)
    if not gap:
        errors.append("report has no visible coverage gap section (未核实与待补证据 or 覆盖缺口)")
        return errors
    for name in OPTIONAL_INPUTS:
        if name in provided:
            continue
        if not any(token in gap for token in MISSING_INPUT_NAMES[name]):
            errors.append(f"coverage gap does not name missing input: {name}")
    return errors


def validate_assembly(
    track_research: Path,
    knowledge_tree: Path,
    market_sizing: Path,
    comps_dd: Path | None,
    report_path: Path,
) -> list[str]:
    paths: dict[str, Path] = {
        "track-research": track_research,
        "knowledge-tree": knowledge_tree,
        "market-sizing": market_sizing,
        "comps-dd": comps_dd,
    }
    for name in REQUIRED_INPUTS:
        if paths[name] is None or not paths[name].exists():
            raise AssemblyError(f"missing required upstream: {name}")
    upstreams = read_inputs(paths)
    provided = {name for name, text in upstreams.items() if text}
    upstream_text = "\n".join(upstreams.values())
    upstream_label_text = upstream_text.replace("【", "[").replace("】", "]")

    upstream_sources = set()
    for name in REQUIRED_INPUTS + OPTIONAL_INPUTS:
        if upstreams[name]:
            upstream_sources |= source_ids(upstreams[name])
    upstream_sources |= market_sizing_source_ids(upstreams["market-sizing"])

    upstream_numbers = set()
    for name in REQUIRED_INPUTS + OPTIONAL_INPUTS:
        if upstreams[name]:
            upstream_numbers |= numbers(upstreams[name])
    upstream_numbers = expand_year_tokens(upstream_numbers)

    try:
        report_text = report_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise AssemblyError(f"cannot read report: {report_path}: {error}") from error
    frontmatter, body = split_frontmatter(report_text)
    claim_body, source_index = split_source_index(body)

    errors: list[str] = []
    errors.extend(check_frontmatter_keys(frontmatter))

    report_sources = source_ids(body)
    for source in sorted(report_sources - upstream_sources):
        errors.append(f"source absent from upstream: {source}")

    # 数字继承：作用于含来源索引的全文；frontmatter 豁免（1d 设计）；来源索引的
    # 日期/URL/来源 ID 属元数据豁免，其余数字（含标签括号内）必须继承。
    numbers_text = claim_body + "\n" + clean_source_index(source_index)
    report_number_tokens = expand_year_tokens(report_numbers(numbers_text))
    for number in sorted(report_number_tokens - upstream_numbers):
        hint = scale_unit_hint(number, upstream_numbers)
        if hint is not None:
            errors.append(
                f"number absent from upstream: {number}"
                f"（疑似单位表示不一致：上游为 {hint}，请保持上游单位表示）"
            )
        else:
            errors.append(f"number absent from upstream: {number}")

    for marker in MARKER.findall(body):
        normalized = marker.replace("【", "[").replace("】", "]")
        if normalized in INTERNAL_LABELS:
            if normalized not in upstream_label_text:
                errors.append(f"label absent from upstream: {marker}")
        elif LABEL_KEYWORDS.search(normalized):
            errors.append(f"unknown evidence label: {marker}")

    errors.extend(check_coverage_gaps(upstreams, provided, body))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate that research-report.md only inherits audited upstream content."
    )
    parser.add_argument("--track-research", required=True, type=Path, help="Track Research landscape.md")
    parser.add_argument("--knowledge-tree", required=True, type=Path, help="knowledge_tree.md or its five-file package directory")
    parser.add_argument("--market-sizing", required=True, type=Path, help="market-sizing.csv")
    parser.add_argument("--comps-dd", type=Path, default=None, help="optional 03-comps-dd.md")
    parser.add_argument("--report", required=True, type=Path, help="candidate research-report.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        errors = validate_assembly(
            args.track_research,
            args.knowledge_tree,
            args.market_sizing,
            args.comps_dd,
            args.report,
        )
    except AssemblyError as error:
        print(f"assembly validation failed: {error}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"assembly validation failed: {error}", file=sys.stderr)
        return 1
    print("assembly validation passed: report inherits audited upstream content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

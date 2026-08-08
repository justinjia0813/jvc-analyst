#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


H1 = re.compile(r"^ {0,3}#(?!#)\s+\S")
H2 = re.compile(r"^ {0,3}##(?!#)\s+\S")
H2_SECTION = re.compile(r"^ {0,3}##(?!#)\s+(\d{1,2})(?:[.．、]\s*|\s+)(.*?)\s*(?:#+\s*)?$")
SUBHEADING = re.compile(r"^ {0,3}#{3,6}(?:\s|$)")
HORIZONTAL_RULE = re.compile(r"^ {0,3}(?:(?:\*\s*){3,}|(?:-\s*){3,}|(?:_\s*){3,})$")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEPARATOR = re.compile(r"^:?-{3,}:?$")
CHINESE_NUMBER = r"[零〇一二三四五六七八九十百千万两廿卅]+"
PAGE_NUMBER = rf"(?:\d+|{CHINESE_NUMBER})"
PAGE_REFERENCE = rf"第\s*{PAGE_NUMBER}(?:\s*(?:[-–—~]|至|到)\s*{PAGE_NUMBER})?\s*页"
ENGLISH_PAGE_REFERENCE = r"(?:p{1,2}\.?|pages?)\s*\d+(?:\s*[-–—~]\s*\d+)?"
LINE_CONTAINER = r"^[ \t]*(?:(?:>[ \t]*)+)?(?:(?:[-+*]|\d+[.)])[ \t]+)?"
SECTION_TITLES = (
    "执行摘要",
    "投资亮点",
    "投资风险",
    "行业概况",
    "市场规模",
    "产业链分析",
    "竞争格局",
    "公司概况",
    "产品矩阵",
    "核心团队",
    "核心壁垒",
    "主要客户",
    "Cap Table",
    "收入预测模型",
    "可比公司",
    "投资回报模型",
    "交易-收益测算总结",
)

PROHIBITED = (
    (
        "evidence status",
        re.compile(rf"{LINE_CONTAINER}证据状态\s*[:：]", re.MULTILINE),
    ),
    (
        "source id",
        re.compile(
            r"\[\s*S(?:\d+|编号)(?:\s*(?:[,，、;/+&]|[-–—])\s*S?(?:\d+|编号))*\s*\]",
            re.IGNORECASE,
        ),
    ),
    (
        "source/evidence label",
        re.compile(r"\[[^\]\n]*访谈[^\]\n]*\]"),
    ),
    (
        "internal bracketed label",
        re.compile(
            r"\[[^\]\n]*(?:来源|核实|验证|提供|推测|推断|估算|未知|自述|报告|新闻|deck|缺口|观察|访谈|待确认|待补充|需补充|未覆盖)[^\]\n]*\]",
            re.IGNORECASE,
        ),
    ),
    (
        "checkbox/template placeholder",
        re.compile(
            r"\[[ xX]\]|\[(?:公司名称|公司简称|项目名称|日期|金额|待填写|请填写|[^\]\n]*占位[^\]\n]*)\]"
        ),
    ),
    (
        "source note",
        re.compile(
            rf"{LINE_CONTAINER}(?:资料来源|数据来源|来源说明|来源)\s*(?:[:：]|于)|"
            r"[（(]\s*(?:资料来源|数据来源|来源说明|来源)\s*[:：][^）)\n]*[）)]",
            re.MULTILINE,
        ),
    ),
    (
        "source heading",
        re.compile(r"^ {0,3}#{1,6}\s+(?:数据来源|资料来源|来源说明|来源)(?:\s+#+)?\s*$", re.MULTILINE),
    ),
    ("web link", re.compile(r"(?:[A-Za-z][A-Za-z0-9+.-]*://|www\.)\S+", re.IGNORECASE)),
    (
        "page reference",
        re.compile(
            rf"(?:(?<![A-Za-z])(?:deck|report|pdf)(?![A-Za-z]).{{0,24}}?"
            rf"(?:{ENGLISH_PAGE_REFERENCE}|{PAGE_REFERENCE}|页码(?:\s*[:：]?\s*\d+)?)|"
            rf"(?<![A-Za-z]){ENGLISH_PAGE_REFERENCE}|{PAGE_REFERENCE})",
            re.IGNORECASE,
        ),
    ),
    (
        "research status",
        re.compile(r"研究状态\s*(?:[:：]|为)"),
    ),
    (
        "review-only evidence label",
        re.compile(r"\[\s*(?:第三方事实|公司口径)\s*\]"),
    ),
    (
        "numeric footnote",
        re.compile(r"\[\s*\d+\s*\]"),
    ),
    (
        "decision language",
        re.compile(
            r"不建议投资|有条件投资|建议投资|推荐投资|"
            r"建议通过(?:本轮)?投资|"
            r"(?:不建议投|有条件投|建议投|不投)(?=\s*(?:[。！？!?；;，,：:]|$))"
        ),
    ),
    (
        "internal gap/placeholder",
        re.compile(
            rf"(?:证据缺口|信息缺口)|"
            rf"{LINE_CONTAINER}(?:待补充|需补充|未覆盖|缺少证据|需要用户提供|此部分缺少输入素材)",
            re.MULTILINE,
        ),
    ),
    (
        "internal operation instruction",
        re.compile(r"内部操作说明"),
    ),
    (
        "internal section",
        re.compile(r"^ {0,3}#{1,6}\s+.*(?:质量报告|来源索引|待用户裁定事项|未覆盖章节)", re.MULTILINE),
    ),
    ("placeholder", re.compile(r"待确认|\b(?:TBD|TODO)\b", re.IGNORECASE)),
)

UNITS = sorted(
    (
        "亿美元",
        "万美元",
        "人民币",
        "个百分点",
        "平方米",
        "亿元",
        "万元",
        "公斤",
        "千克",
        "GWh",
        "MWh",
        "kWh",
        "USD",
        "CNY",
        "RMB",
        "MW",
        "kW",
        "km",
        "美元",
        "元",
        "万",
        "亿",
        "年",
        "月",
        "日",
        "天",
        "岁",
        "条",
        "个",
        "家",
        "人",
        "项",
        "次",
        "笔",
        "轮",
        "台",
        "套",
        "吨",
        "克",
        "亩",
        "米",
        "倍",
        "x",
        "×",
        "股",
        "成",
        "%",
        "％",
        "$",
        "¥",
        "￥",
    ),
    key=len,
    reverse=True,
)
UNIT_ALIASES = {
    "％": "%",
    "cny": "rmb",
    "人民币": "rmb",
    "元": "rmb",
    "¥": "rmb",
    "￥": "rmb",
    "美元": "usd",
    "$": "usd",
    "x": "倍",
    "×": "倍",
}
UNIT_PATTERN = "|".join(map(re.escape, UNITS))
PREFIX_UNIT_PATTERN = "|".join(
    map(re.escape, ("人民币", "美元", "USD", "CNY", "RMB", "$", "¥", "￥"))
)
NUMBER = re.compile(
    rf"(?<!\d)(?:(?P<prefix>{PREFIX_UNIT_PATTERN})[ \t]*)?"
    rf"(?P<number>[-+]?(?:(?:\d{{1,3}}(?:[ ,]\d{{3}})+|\d+)(?:\.\d+)?|\.\d+))"
    rf"(?:[ \t]*(?P<suffix>{UNIT_PATTERN}))?(?!\d)",
    re.IGNORECASE,
)
CHINESE_UNITS = tuple(
    unit for unit in UNITS if re.search(r"[\u4e00-\u9fff%％]", unit) and unit != "人民币"
)
CHINESE_UNIT_PATTERN = "|".join(map(re.escape, CHINESE_UNITS))
CHINESE_QUANTITY = re.compile(
    r"(?P<number>[零〇一二三四五六七八九十百千两廿卅][零〇一二三四五六七八九十百千万亿两廿卅]*?)"
    rf"(?P<unit>{CHINESE_UNIT_PATTERN})"
)
NUMBER_METADATA = re.compile(
    r"\[(?:\s*S(?:\d+|编号)(?:\s*(?:[,，、;/+&]|[-–—])\s*S?(?:\d+|编号))*\s*|"
    r"\s*\d+\s*|[^\]\n]*(?:来源|核实|验证|提供|推测|自述|报告|新闻|deck|缺口|"
    r"待确认|待补充|需补充|未覆盖|第三方事实|公司口径|观察|访谈|推断|估算|未知)[^\]\n]*)\]",
    re.IGNORECASE,
)
QUALITY_APPENDIX = re.compile(r"^ {0,3}##(?!#)\s+附录：质量报告(?:\s+#+)?\s*$")
MARKDOWN_HEADING = re.compile(r"^ {0,3}#{1,6}(?:\s|$)")


def read_text(path: Path, label: str) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"cannot read {label}: {error}") from error
    if not text.strip():
        raise ValueError(f"{label} is empty")
    return text


def blockquote_content(line: str) -> tuple[int, str]:
    depth = 0
    prefix = re.match(r"^ {0,3}>[ \t]?", line)
    while prefix:
        depth += 1
        line = line[prefix.end() :]
        prefix = re.match(r"^ {0,3}>[ \t]?", line)
    return depth, line


def outside_fences(text: str) -> list[str | None]:
    visible: list[str | None] = []
    marker = ""
    width = 0
    fence_depth = 0
    for line in text.splitlines():
        quote_depth, candidate = blockquote_content(line)
        indent = len(candidate) - len(candidate.lstrip(" "))
        candidate = candidate[indent:] if indent <= 3 else ""
        if marker:
            visible.append(None)
            if quote_depth == fence_depth and re.fullmatch(
                rf"{re.escape(marker)}{{{width},}}[ \t]*", candidate
            ):
                marker = ""
            continue
        match = re.match(r"(`{3,}|~{3,})", candidate)
        if match:
            marker = match.group(1)[0]
            width = len(match.group(1))
            fence_depth = quote_depth
            visible.append(None)
        else:
            visible.append(line)
    if marker:
        raise ValueError("unclosed fenced code block")
    return visible


def check_sections(lines: list[str | None]) -> None:
    headings = [(index, line) for index, line in enumerate(lines) if line is not None]
    if not any(H1.match(line) for _, line in headings):
        raise ValueError("missing level-one heading")
    h2_indexes = [index for index, line in headings if H2.match(line)]
    if not h2_indexes:
        raise ValueError("missing level-two section")
    section_numbers = []
    for index in h2_indexes:
        match = H2_SECTION.fullmatch(lines[index])  # type: ignore[arg-type]
        if not match:
            raise ValueError("section numbering: unnumbered level-two section")
        number = int(match.group(1))
        if number < 1 or number > len(SECTION_TITLES):
            raise ValueError("section numbering: number outside 1-17")
        if match.group(2) != SECTION_TITLES[number - 1]:
            raise ValueError("section mapping: title does not match section number")
        section_numbers.append(number)
    if any(current <= previous for previous, current in zip(section_numbers, section_numbers[1:])):
        raise ValueError("section numbering: sections must be unique and strictly increasing")
    for start in h2_indexes:
        end = next(
            (
                index
                for index, line in headings
                if index > start and (H1.match(line) or H2.match(line))
            ),
            len(lines),
        )
        body = [blockquote_content(line)[1] for line in lines[start + 1 : end] if line is not None]
        body = re.sub(r"<!--.*?-->", "", "\n".join(body), flags=re.DOTALL).splitlines()
        meaningful = False
        index = 0
        while index < len(body):
            line = body[index]
            content = line.strip()
            if has_pipe(content) and index + 1 < len(body):
                separator = table_cells(body[index + 1])
                if separator and all(TABLE_SEPARATOR.fullmatch(cell) for cell in separator):
                    index += 2
                    while index < len(body) and has_pipe(body[index]):
                        if any(table_cells(body[index])):
                            meaningful = True
                            break
                        index += 1
                    if meaningful:
                        break
                    continue
            if (
                content
                and not HORIZONTAL_RULE.match(content)
                and not SUBHEADING.match(content)
                and not re.fullmatch(r"(?:[-+*]|\d+[.)])", content)
            ):
                meaningful = True
                break
            index += 1
        if not meaningful:
            raise ValueError("empty level-two section")


def table_cells(line: str) -> list[str]:
    line = line.strip()
    cells = re.split(r"(?<!\\)\|", line)
    if line.startswith("|"):
        cells = cells[1:]
    if line.endswith("|") and not line.endswith(r"\|"):
        cells = cells[:-1]
    return [cell.strip() for cell in cells]


def has_pipe(line: str) -> bool:
    return bool(re.search(r"(?<!\\)\|", line))


def check_tables(lines: list[str | None]) -> None:
    index = 0
    while index < len(lines):
        line = lines[index]
        if line is None:
            index += 1
            continue
        quote_depth, content = blockquote_content(line)
        if not has_pipe(content):
            index += 1
            continue
        table: list[str] = []
        while index < len(lines) and lines[index] is not None:
            depth, content = blockquote_content(lines[index])  # type: ignore[arg-type]
            if depth != quote_depth or not has_pipe(content):
                break
            table.append(content)
            index += 1
        rows = [table_cells(row) for row in table]
        has_separator = len(rows) >= 2 and all(TABLE_SEPARATOR.fullmatch(cell) for cell in rows[1])
        outer_pipes = all(TABLE_ROW.match(row) for row in table)
        if len(rows) == 1 and outer_pipes:
            if all(TABLE_SEPARATOR.fullmatch(cell) for cell in rows[0]):
                raise ValueError("malformed Markdown table: missing header row")
            raise ValueError("malformed Markdown table: missing separator row")
        if not has_separator and len(rows) >= 2 and outer_pipes:
            raise ValueError("malformed Markdown table: missing separator row")
        if has_separator and any(len(row) != len(rows[0]) for row in rows):
            raise ValueError("malformed Markdown table: inconsistent column count")


def number_input(text: str) -> str:
    visible = []
    marker = ""
    width = 0
    fence_depth = 0
    for line in text.splitlines():
        quote_depth, candidate = blockquote_content(line)
        indent = len(candidate) - len(candidate.lstrip(" "))
        candidate = candidate[indent:] if indent <= 3 else ""
        if marker:
            if quote_depth == fence_depth and re.fullmatch(
                rf"{re.escape(marker)}{{{width},}}[ \t]*", candidate
            ):
                marker = ""
            else:
                visible.append(NUMBER_METADATA.sub("", line))
            continue
        fence = re.match(r"(`{3,}|~{3,})", candidate)
        if fence:
            marker = fence.group(1)[0]
            width = len(fence.group(1))
            fence_depth = quote_depth
            continue
        if QUALITY_APPENDIX.fullmatch(line):
            break
        section = H2_SECTION.fullmatch(line)
        if section:
            number = int(section.group(1))
            if 1 <= number <= len(SECTION_TITLES) and section.group(2) == SECTION_TITLES[number - 1]:
                continue
        if MARKDOWN_HEADING.match(line):
            line = MARKDOWN_HEADING.sub("", line, count=1)
        visible.append(NUMBER_METADATA.sub("", line))
    return "\n".join(visible)


def numbers(text: str) -> set[str]:
    found = set()
    text = number_input(text)
    for match in NUMBER.finditer(text):
        number = re.sub(r"[\s,]", "", match.group("number"))
        units = []
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


def validate(review: str, final: str) -> None:
    lines = outside_fences(final)
    for name, pattern in PROHIBITED:
        if pattern.search(final):
            raise ValueError(f"contains {name}")
    check_sections(lines)
    check_tables(lines)
    new_numbers = sorted(numbers(final) - numbers(review))
    if new_numbers:
        raise ValueError(f"number absent from review: {new_numbers[0]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a clean IC memo against its review version.")
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--final", required=True, type=Path)
    args = parser.parse_args()
    try:
        validate(read_text(args.review, "review"), read_text(args.final, "final"))
    except ValueError as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1
    print("IC memo final validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

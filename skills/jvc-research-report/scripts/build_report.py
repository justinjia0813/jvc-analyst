from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

import yaml
from markdown_it import MarkdownIt
from markdown_it.token import Token


VERSION = "0.1.0"


class BuildError(RuntimeError):
    pass


REQUIRED_FIELDS = ("title", "date")
OPTIONAL_FIELDS = (
    "subtitle",
    "authors",
    "sector",
    "region",
    "classification",
    "cover_image",
    "disclaimer",
)
TEXT_FIELDS = ("subtitle", "sector", "region", "classification", "disclaimer")
SECTION_ALIASES = (
    ("研究设定与一页快照",),
    ("行业定义与边界",),
    ("行业简史与产业生命周期",),
    ("技术路线与商业可行性",),
    ("产业链图谱",),
    ("产业趋势、景气度与周期位置",),
    ("关键玩家", "关键玩家分层"),
    ("监管、政策与标准", "监管 / 政策 / 标准"),
    ("投资相关问题", "投资相关问题与反证账本"),
    ("后续工作交接包",),
    ("来源索引",),
)
OPTIONAL_SECTIONS = ("缩写说明", "未核实与待补证据")


def split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if text.startswith("---\n"):
        newline = "\n"
    elif text.startswith("---\r\n"):
        newline = "\r\n"
    else:
        raise BuildError("report.md: missing YAML frontmatter")
    opening = f"---{newline}"
    closing = f"{newline}---{newline}"
    marker = text.find(closing, len(opening))
    if marker < 0:
        raise BuildError("report.md: YAML frontmatter is not closed")
    try:
        metadata = yaml.safe_load(text[len(opening) : marker])
    except yaml.YAMLError as exc:
        raise BuildError(f"report.md: invalid YAML: {exc}") from exc
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise BuildError("report.md: frontmatter must be a mapping")
    return metadata, text[marker + len(closing) :]


def _missing(value: object) -> bool:
    return not value or isinstance(value, str) and not value.strip()


def validate_metadata(metadata: dict[str, object]) -> list[str]:
    missing = [field for field in REQUIRED_FIELDS if _missing(metadata.get(field))]
    if missing:
        raise BuildError(f"report.md: missing required metadata: {', '.join(missing)}")
    if not isinstance(metadata["title"], str):
        raise BuildError("report.md: metadata title must be a non-empty string")
    report_date = metadata["date"]
    if not isinstance(report_date, (str, date, datetime)):
        raise BuildError("report.md: metadata date must be a non-empty string or date")
    for field in TEXT_FIELDS:
        value = metadata.get(field)
        if value is not None and not isinstance(value, str):
            raise BuildError(f"report.md: metadata {field} must be a string")
    authors = metadata.get("authors")
    if authors is not None and not (
        isinstance(authors, str) and bool(authors.strip())
        or isinstance(authors, list)
        and all(isinstance(author, str) for author in authors)
    ):
        raise BuildError(
            "report.md: metadata authors must be a non-empty string or list of strings"
        )
    cover_image = metadata.get("cover_image")
    if cover_image is not None and not isinstance(cover_image, str):
        raise BuildError("report.md: metadata cover_image must be a string")
    return [
        f"optional metadata missing: {field}"
        for field in OPTIONAL_FIELDS
        if _missing(metadata.get(field))
    ]


def normalized_heading(value: str) -> str:
    without_prefix = re.sub(
        r"^\s*(?:0|[A-I])[.、)]\s*",
        "",
        value.strip(),
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", "", without_prefix).casefold()


def _markdown_tokens(body: str) -> list[Token]:
    return MarkdownIt("commonmark").enable("table").parse(body)


def level_two_headings(body: str) -> list[str]:
    tokens = _markdown_tokens(body)
    return [
        tokens[index + 1].content
        for index, token in enumerate(tokens[:-1])
        if token.type == "heading_open" and token.tag == "h2" and token.level == 0
    ]


def validate_structure(body: str) -> None:
    alias_indexes = {
        normalized_heading(alias): index
        for index, aliases in enumerate(SECTION_ALIASES)
        for alias in aliases
    }
    optional = {normalized_heading(section) for section in OPTIONAL_SECTIONS}
    canonical_order = []
    seen = set()
    for value in level_two_headings(body):
        heading = normalized_heading(value)
        if heading in optional:
            continue
        if heading not in alias_indexes:
            raise BuildError(f"report.md: unexpected section: {value}")
        canonical_index = alias_indexes[heading]
        if canonical_index in seen:
            raise BuildError(
                f"report.md: duplicate canonical section: "
                f"{SECTION_ALIASES[canonical_index][0]}"
            )
        seen.add(canonical_index)
        canonical_order.append(canonical_index)

    for index, aliases in enumerate(SECTION_ALIASES):
        if index not in seen:
            raise BuildError(f"report.md: missing required section: {aliases[0]}")
    if canonical_order != list(range(len(SECTION_ALIASES))):
        first_wrong = next(
            actual
            for expected, actual in enumerate(canonical_order)
            if actual != expected
        )
        raise BuildError(
            f"report.md: out-of-order section: {SECTION_ALIASES[first_wrong][0]}"
        )


def _source_index_tokens(tokens: list[Token]) -> list[Token]:
    for index, token in enumerate(tokens[:-1]):
        if token.type != "heading_open" or token.tag != "h2" or token.level != 0:
            continue
        if normalized_heading(tokens[index + 1].content) != normalized_heading("来源索引"):
            continue
        end = len(tokens)
        for later_index, later in enumerate(tokens[index + 3 :], index + 3):
            if later.type == "heading_open" and later.tag == "h2" and later.level == 0:
                end = later_index
                break
        return tokens[index + 3 : end]
    raise BuildError("report.md: missing source index")


def _source_definitions(tokens: list[Token]) -> list[str]:
    defined = []
    in_tbody = False
    first_cell_pending = False
    in_first_cell = False
    for token in tokens:
        if token.type == "tbody_open":
            in_tbody = True
        elif token.type == "tbody_close":
            in_tbody = False
        elif in_tbody and token.type == "tr_open":
            first_cell_pending = True
        elif in_tbody and token.type == "td_open" and first_cell_pending:
            first_cell_pending = False
            in_first_cell = True
        elif token.type == "td_close" and in_first_cell:
            in_first_cell = False
        elif in_first_cell and token.type == "inline":
            match = re.fullmatch(r"S([1-9]\d*)", token.content.strip())
            if match:
                defined.append(match.group(1))
    return defined


def _used_sources(tokens: list[Token]) -> set[str]:
    used = set()
    in_source_index = False
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2" and token.level == 0:
            in_source_index = normalized_heading(
                tokens[index + 1].content
            ) == normalized_heading("来源索引")
            continue
        if in_source_index or token.type != "inline":
            continue
        for child in token.children or ():
            if child.type in ("text", "image"):
                used.update(re.findall(r"\[S([1-9]\d*)\]", child.content))
    return used


def validate_sources(body: str) -> list[str]:
    tokens = _markdown_tokens(body)
    used = _used_sources(tokens)
    defined = _source_definitions(_source_index_tokens(tokens))
    duplicates = sorted(
        (source for source in set(defined) if defined.count(source) > 1),
        key=int,
    )
    if duplicates:
        raise BuildError(
            "report.md: duplicate source IDs: "
            + ", ".join("S" + source for source in duplicates)
        )
    missing = sorted(used - set(defined), key=int)
    if missing:
        raise BuildError(
            "report.md: undefined sources: "
            + ", ".join("S" + source for source in missing)
        )
    unused = sorted(set(defined) - used, key=int)
    return [
        "unused source definitions: " + ", ".join("S" + source for source in unused)
    ] if unused else []


def local_path(base: Path, raw: str, label: str) -> Path:
    try:
        parsed = urlparse(raw)
    except ValueError as exc:
        raise BuildError(f"{label}: invalid path: {raw}") from exc
    if (
        not raw
        or parsed.scheme
        or parsed.netloc
        or raw.startswith(("//", "\\\\"))
        or Path(raw).is_absolute()
    ):
        raise BuildError(f"{label}: remote or absolute path is not allowed: {raw}")
    path = (base / raw).resolve()
    try:
        path.relative_to(base.resolve())
    except ValueError as exc:
        raise BuildError(f"{label}: path escapes the report directory: {raw}") from exc
    if not path.is_file():
        raise BuildError(f"{label}: missing file: {raw}")
    return path


def _image_sources(body: str) -> list[str]:
    sources = []
    for token in _markdown_tokens(body):
        for child in token.children or ():
            if child.type == "image":
                sources.append(child.attrGet("src") or "")
    return sources


def validate_report(text: str, report_path: Path) -> list[str]:
    metadata, body = split_frontmatter(text)
    warnings = validate_metadata(metadata)
    validate_structure(body)
    warnings.extend(validate_sources(body))

    report_root = Path(report_path).resolve().parent
    cover_image = metadata.get("cover_image")
    if cover_image:
        if not isinstance(cover_image, str):
            raise BuildError("report.md cover_image: path must be a string")
        local_path(report_root, cover_image, "report.md cover_image")
    for source in _image_sources(body):
        local_path(report_root, source, "report.md image")
    return warnings

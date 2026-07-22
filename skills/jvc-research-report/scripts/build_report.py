from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import yaml
from markdown_it import MarkdownIt


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


def _missing(value: object) -> bool:
    return not value or isinstance(value, str) and not value.strip()


def validate_metadata(metadata: dict[str, object]) -> list[str]:
    missing = [field for field in REQUIRED_FIELDS if _missing(metadata.get(field))]
    if missing:
        raise BuildError(f"report.md: missing required metadata: {', '.join(missing)}")
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


def _markdown_tokens(body: str):
    return MarkdownIt("commonmark").enable("table").parse(body)


def level_two_headings(body: str) -> list[str]:
    tokens = _markdown_tokens(body)
    return [
        tokens[index + 1].content
        for index, token in enumerate(tokens[:-1])
        if token.type == "heading_open" and token.tag == "h2"
    ]


def validate_structure(body: str) -> None:
    headings = [normalized_heading(value) for value in level_two_headings(body)]
    cursor = -1
    for aliases in SECTION_ALIASES:
        accepted = {normalized_heading(alias) for alias in aliases}
        positions = [index for index, heading in enumerate(headings) if heading in accepted]
        if not positions:
            raise BuildError(f"report.md: missing required section: {aliases[0]}")
        following = [position for position in positions if position > cursor]
        if not following:
            raise BuildError(f"report.md: out-of-order section: {aliases[0]}")
        cursor = following[0]


def _source_index_bounds(body: str) -> tuple[int, int]:
    lines = body.splitlines(keepends=True)
    tokens = _markdown_tokens(body)
    for index, token in enumerate(tokens[:-1]):
        if token.type != "heading_open" or token.tag != "h2":
            continue
        if normalized_heading(tokens[index + 1].content) != normalized_heading("来源索引"):
            continue
        start_line = token.map[0]
        end_line = len(lines)
        for later in tokens[index + 3 :]:
            if later.type == "heading_open" and later.tag == "h2":
                end_line = later.map[0]
                break
        return sum(map(len, lines[:start_line])), sum(map(len, lines[:end_line]))
    raise BuildError("report.md: missing source index")


def validate_sources(body: str) -> list[str]:
    source_start, source_end = _source_index_bounds(body)
    used = set(re.findall(r"\[S([1-9]\d*)\]", body[:source_start]))
    source_block = body[source_start:source_end]
    defined = re.findall(r"(?m)^[ \t]{0,3}\|\s*S([1-9]\d*)\s*\|", source_block)
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
    parsed = urlparse(raw)
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

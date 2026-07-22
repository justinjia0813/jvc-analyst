from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import os
import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Sequence
from urllib.parse import urlparse
from xml.etree import ElementTree

import yaml
from markdown_it import MarkdownIt
from markdown_it.token import Token
from PIL import Image, UnidentifiedImageError
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from weasyprint.urls import FatalURLFetchingError, URLFetcher


VERSION = "0.1.0"
OUTPUT_FILES = ("report.pdf", "report.html", "build-report.txt")
BRAND_DEFAULTS: dict[str, object] = {
    "name": "lustinus RESEARCH",
    "logo": None,
    "accent_color": "#A06B2C",
    "header": "lustinus RESEARCH",
    "footer": "Internal Research",
    "disclaimer": (
        "Internal research only. Verify sources before external distribution."
    ),
    "sans_font": "PingFang SC",
    "serif_font": "Songti SC",
}
FONT_EXTENSIONS = {".otf", ".ttc", ".ttf", ".woff", ".woff2"}


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
    return MarkdownIt(
        "commonmark", {"html": False, "linkify": False}
    ).enable("table").parse(body)


def level_two_headings(body: str) -> list[str]:
    return _level_two_headings(_markdown_tokens(body))


def _level_two_headings(tokens: Sequence[Token]) -> list[str]:
    return [
        tokens[index + 1].content
        for index, token in enumerate(tokens[:-1])
        if token.type == "heading_open" and token.tag == "h2" and token.level == 0
    ]


def validate_structure(body: str) -> None:
    _validate_structure_tokens(_markdown_tokens(body))


def _validate_structure_tokens(tokens: Sequence[Token]) -> None:
    alias_indexes = {
        normalized_heading(alias): index
        for index, aliases in enumerate(SECTION_ALIASES)
        for alias in aliases
    }
    optional = {normalized_heading(section) for section in OPTIONAL_SECTIONS}
    canonical_order = []
    seen = set()
    for value in _level_two_headings(tokens):
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
                content = child.content
                if child.type == "text":
                    content = re.sub(r"<[^>]*>", "", content)
                used.update(re.findall(r"\[S([1-9]\d*)\]", content))
    return used


def validate_sources(body: str) -> list[str]:
    return _validate_source_tokens(_markdown_tokens(body))


def _validate_source_tokens(tokens: list[Token]) -> list[str]:
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


def _image_sources(tokens: Sequence[Token]) -> list[str]:
    sources = []
    for token in tokens:
        for child in token.children or ():
            if child.type == "image":
                sources.append(child.attrGet("src") or "")
    return sources


def validate_report(text: str, report_path: Path) -> list[str]:
    metadata, body = split_frontmatter(text)
    tokens = _markdown_tokens(body)
    return _validate_parsed(metadata, tokens, report_path)


def _validate_parsed(
    metadata: dict[str, object], tokens: list[Token], report_path: Path
) -> list[str]:
    warnings = validate_metadata(metadata)
    _validate_structure_tokens(tokens)
    warnings.extend(_validate_source_tokens(tokens))

    report_root = Path(report_path).resolve().parent
    cover_image = metadata.get("cover_image")
    if cover_image:
        if not isinstance(cover_image, str):
            raise BuildError("report.md cover_image: path must be a string")
        local_path(report_root, cover_image, "report.md cover_image")
    for source in _image_sources(tokens):
        local_path(report_root, source, "report.md image")
    return warnings


def data_uri(path: Path, media_type: str | None = None) -> str:
    media_type = media_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except (OSError, UnicodeError) as exc:
        raise BuildError(f"cannot read local asset {path.name}: {exc}") from exc
    return f"data:{media_type};base64,{encoded}"


def local_url_fetcher(url: str, headers: dict[str, str] | None = None):
    try:
        scheme = urlparse(url).scheme.casefold()
    except ValueError as exc:
        raise FatalURLFetchingError(f"invalid resource URL: {url}") from exc
    if scheme != "data":
        raise FatalURLFetchingError(f"remote resource blocked: {url}")
    return URLFetcher(
        allowed_protocols={"data"}, fail_on_errors=True
    ).fetch(url, headers)


def load_brand(path: Path) -> dict[str, object]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise BuildError(f"brand.yml: cannot read {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise BuildError(f"brand.yml: invalid YAML: {exc}") from exc
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise BuildError("brand.yml: must be a mapping")

    brand = {**BRAND_DEFAULTS, **loaded}
    if brand["name"] != "lustinus RESEARCH":
        raise BuildError("brand.yml: name must be exactly lustinus RESEARCH")
    accent = brand["accent_color"]
    if not isinstance(accent, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", accent):
        raise BuildError("brand.yml: accent_color must be a six-digit hex color")
    for field in ("header", "footer", "disclaimer", "sans_font", "serif_font"):
        value = brand[field]
        if not isinstance(value, str) or not value.strip():
            raise BuildError(f"brand.yml: {field} must be a non-empty string")
    logo = brand["logo"]
    if logo is not None and (not isinstance(logo, str) or not logo.strip()):
        raise BuildError("brand.yml: logo must be null or a non-empty string")
    return brand


def _css_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def _scan_font(path: Path, label: str) -> tuple[str, str]:
    try:
        result = subprocess.run(
            ("fc-scan", "--format", "%{family}\n%{charset}\n", str(path)),
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise BuildError(f"{label}: font scan failed: {exc}") from exc
    lines = result.stdout.splitlines()
    if result.returncode or len(lines) < 2 or not lines[0].strip() or not lines[1].strip():
        detail = result.stderr.strip() or "fontconfig could not parse family/charset"
        raise BuildError(f"{label}: invalid font file: {path.name}: {detail}")
    return lines[0].strip(), lines[1].strip()


def _font_charset(path: Path, label: str) -> list[tuple[int, int]]:
    try:
        result = subprocess.run(
            ("fc-query", "--format", "%{charset}\n", str(path)),
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise BuildError(f"{label}: font charset query failed: {exc}") from exc
    if result.returncode or not result.stdout.strip():
        detail = result.stderr.strip() or "fontconfig returned no charset"
        raise BuildError(f"{label}: invalid font charset: {path.name}: {detail}")
    ranges = []
    for item in result.stdout.split():
        if not re.fullmatch(r"[0-9A-Fa-f]+(?:-[0-9A-Fa-f]+)?", item):
            raise BuildError(f"{label}: invalid font charset range: {item}")
        bounds = item.split("-", 1)
        start = int(bounds[0], 16)
        end = int(bounds[-1], 16)
        if end < start:
            raise BuildError(f"{label}: invalid font charset range: {item}")
        ranges.append((start, end))
    return ranges


def _font_css(
    value: str, brand_root: Path, role: str
) -> tuple[str, str, list[tuple[int, int]]]:
    try:
        parsed = urlparse(value)
    except ValueError as exc:
        raise BuildError(f"brand.yml {role}_font: invalid font: {value}") from exc
    looks_like_path = bool(Path(value).suffix) or "/" in value or "\\" in value
    if parsed.scheme or parsed.netloc or Path(value).is_absolute() or value.startswith("//"):
        raise BuildError(
            f"brand.yml {role}_font: remote or absolute path is not allowed: {value}"
        )
    if looks_like_path:
        path = local_path(brand_root, value, f"brand.yml {role}_font")
        if path.suffix.casefold() not in FONT_EXTENSIONS:
            raise BuildError(
                f"brand.yml {role}_font: unsupported font extension: {path.suffix}"
            )
        try:
            path.open("rb").close()
        except OSError as exc:
            raise BuildError(f"brand.yml {role}_font: cannot read {value}: {exc}") from exc
        _scan_font(path, f"brand.yml {role}_font")
        charset = _font_charset(path, f"brand.yml {role}_font")
        family = f"lustinus-{role}"
        face = (
            "@font-face {"
            f"font-family: {_css_string(family)};"
            f"src: url({_css_string(data_uri(path))});"
            "}"
        )
        return _css_string(family), face, charset

    try:
        matched = subprocess.run(
            ("fc-match", "-f", "%{family}\\n%{file}\\n", value),
            text=True,
            capture_output=True,
            check=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildError(f"brand.yml {role}_font: font lookup failed: {exc}") from exc
    if len(matched) < 2:
        raise BuildError(f"brand.yml {role}_font: font lookup returned no file: {value}")
    families = {
        family.strip().casefold()
        for line in matched[:1]
        for family in line.split(",")
        if family.strip()
    }
    if value.strip().casefold() not in families:
        actual = matched[0] if matched else "no match"
        raise BuildError(
            f"brand.yml {role}_font: system font family not found: "
            f"{value} (fc-match returned {actual})"
        )
    font_path = Path(matched[1])
    if not font_path.is_file():
        raise BuildError(f"brand.yml {role}_font: matched font file is missing: {font_path}")
    return (
        _css_string(value),
        "",
        _font_charset(font_path, f"brand.yml {role}_font"),
    )


def _image_uri(path: Path, label: str, warnings: list[str]) -> str:
    try:
        with Image.open(path) as image:
            image_format = image.format
            image.verify()
        with Image.open(path) as image:
            width = image.width
        media_type = Image.MIME.get(image_format or "")
        if not media_type or not media_type.startswith("image/"):
            raise UnidentifiedImageError(f"unknown raster format: {image_format}")
        if width < 1200:
            warnings.append(f"low-resolution image ({width}px wide): {path.name}")
        return data_uri(path, media_type)
    except (OSError, UnidentifiedImageError):
        pass

    try:
        raw = path.read_bytes()
        if re.search(br"<!\s*(?:DOCTYPE|ENTITY)\b", raw, flags=re.IGNORECASE):
            raise BuildError(f"{label}: invalid SVG: declarations are not allowed: {path.name}")
        pull_parser = ElementTree.XMLPullParser(events=("pi",))
        pull_parser.feed(raw)
        pull_parser.close()
        for _event, instruction in pull_parser.read_events():
            match = re.fullmatch(
                r"xml-stylesheet\b(.*)", instruction.text or "", flags=re.IGNORECASE | re.DOTALL
            )
            if not match:
                continue
            hrefs = re.findall(
                r"\bhref\s*=\s*(['\"])(.*?)\1",
                match.group(1),
                flags=re.IGNORECASE | re.DOTALL,
            )
            if len(hrefs) != 1 or not hrefs[0][1].strip().casefold().startswith("data:"):
                raise BuildError(
                    f"{label}: external or malformed xml-stylesheet href is not allowed: {path.name}"
                )
        root = ElementTree.fromstring(raw)
    except BuildError:
        raise
    except (OSError, ElementTree.ParseError) as exc:
        raise BuildError(f"{label}: invalid SVG or unknown image: {path.name}: {exc}") from exc
    if root.tag.rsplit("}", 1)[-1].casefold() != "svg":
        raise BuildError(f"{label}: invalid SVG root: {path.name}")

    css_url = re.compile(
        r"url\(\s*(?:(['\"])(.*?)\1|([^)]*))\s*\)",
        re.IGNORECASE | re.DOTALL,
    )

    def allowed_location(value: str) -> bool:
        value = value.strip()
        return value.startswith("#") or value.casefold().startswith("data:")

    def validate_css(value: str, *, check_import: bool = False) -> None:
        if check_import and re.search(r"@import\b", value, flags=re.IGNORECASE):
            raise BuildError(f"{label}: external SVG @import is not allowed: {path.name}")
        for match in css_url.finditer(value):
            location = (match.group(2) or match.group(3) or "").strip().strip("'\"")
            if not allowed_location(location):
                raise BuildError(
                    f"{label}: external SVG CSS URL is not allowed: {path.name}"
                )

    presentation_attributes = {
        "style",
        "fill",
        "stroke",
        "filter",
        "clip-path",
        "mask",
        "marker-start",
        "marker-mid",
        "marker-end",
        "cursor",
    }
    for element in root.iter():
        for attribute, value in element.attrib.items():
            local_name = attribute.rsplit("}", 1)[-1].casefold()
            if local_name in ("href", "src") and not allowed_location(value):
                raise BuildError(
                    f"{label}: external SVG {local_name} is not allowed: {path.name}"
                )
            if local_name in presentation_attributes:
                validate_css(value, check_import=local_name == "style")
        if element.tag.rsplit("}", 1)[-1].casefold() == "style":
            validate_css("".join(element.itertext()), check_import=True)
    return data_uri(path, "image/svg+xml")


CALLOUTS = {
    "[!FACT]": "callout-fact",
    "[!INFERENCE]": "callout-inference",
    "[!OPEN QUESTION]": "callout-open-question",
}


def _is_source_line(children: list[Token]) -> bool:
    if len(children) < 3 or children[0].type != "em_open" or children[-1].type != "em_close":
        return False
    visible = "".join(
        child.content
        for child in children[1:-1]
        if child.type in ("text", "code_inline", "image")
    )
    return visible.strip().startswith("来源：")


def _prepare_tokens(
    tokens: list[Token], report_root: Path, warnings: list[str]
) -> list[tuple[str, str]]:
    alias_indexes = {
        normalized_heading(alias): index
        for index, aliases in enumerate(SECTION_ALIASES)
        for alias in aliases
    }
    toc: list[tuple[str, str]] = []
    extra_index = 0
    for index, token in enumerate(tokens[:-1]):
        if token.type == "heading_open" and token.tag == "h2" and token.level == 0:
            label = tokens[index + 1].content
            canonical = alias_indexes.get(normalized_heading(label))
            if canonical is None:
                extra_index += 1
                target = f"section-extra-{extra_index:02d}"
            else:
                target = f"section-{canonical + 1:02d}"
            token.attrSet("id", target)
            toc.append((target, label))

    for index in range(len(tokens) - 2):
        if (
            tokens[index].type == "paragraph_open"
            and tokens[index + 1].type == "inline"
            and tokens[index + 2].type == "paragraph_close"
        ):
            inline = tokens[index + 1]
            children = inline.children or []
            if len(children) == 1 and children[0].type == "image":
                tokens[index].meta["figure"] = True
                tokens[index + 2].meta["figure"] = True
                children[0].meta["standalone"] = True
            if _is_source_line(children):
                tokens[index].meta["source_line"] = True
            if (
                inline.content.strip().startswith("表：")
                and index + 3 < len(tokens)
                and tokens[index + 3].type == "table_open"
            ):
                tokens[index].hidden = True
                inline.hidden = True
                inline.children = []
                tokens[index + 2].hidden = True
                tokens[index + 3].meta["caption"] = inline.content.strip()

    for index, token in enumerate(tokens):
        if token.type != "blockquote_open":
            continue
        inline = next(
            (
                candidate
                for candidate in tokens[index + 1 :]
                if candidate.type in ("inline", "blockquote_close")
            ),
            None,
        )
        if inline is None or inline.type != "inline":
            continue
        marker = next(
            (
                marker
                for marker in CALLOUTS
                if inline.content == marker or inline.content.startswith(marker + "\n")
            ),
            None,
        )
        if marker is None:
            continue
        token.meta["callout"] = CALLOUTS[marker]
        children = list(inline.children or [])
        if children and children[0].type == "text" and children[0].content == marker:
            children.pop(0)
            if children and children[0].type == "softbreak":
                children.pop(0)
        elif children and children[0].type == "text":
            children[0].content = children[0].content[len(marker) :].lstrip()
        inline.children = children

    for token in tokens:
        for child in token.children or ():
            if child.type != "image":
                continue
            source = child.attrGet("src") or ""
            path = local_path(report_root, source, "report.md image")
            child.attrSet("src", _image_uri(path, "report.md image", warnings))
            caption = child.content.strip()
            child.meta["caption"] = caption
            if not caption:
                warnings.append(f"image caption missing: {path.name}")

    for index, token in enumerate(tokens):
        if token.type != "table_open":
            continue
        if "caption" not in token.meta:
            warnings.append("table caption missing")
        end = next(
            (
                later
                for later in range(index + 1, len(tokens))
                if tokens[later].type == "tr_close"
            ),
            len(tokens),
        )
        columns = sum(
            candidate.type == "th_open" for candidate in tokens[index + 1 : end]
        )
        if columns > 6:
            warnings.append(f"table has {columns} columns; more than 6 may overflow")

    for index, token in enumerate(tokens):
        if token.type == "paragraph_open" and token.meta.get("figure"):
            next_index = index + 3
            if not (
                next_index < len(tokens)
                and tokens[next_index].type == "paragraph_open"
                and tokens[next_index].meta.get("source_line")
            ):
                warnings.append("image source line missing")
        if token.type == "table_open":
            close_index = next(
                (
                    later
                    for later in range(index + 1, len(tokens))
                    if tokens[later].type == "table_close"
                ),
                len(tokens),
            )
            next_index = close_index + 1
            if not (
                next_index < len(tokens)
                and tokens[next_index].type == "paragraph_open"
                and tokens[next_index].meta.get("source_line")
            ):
                warnings.append("table source line missing")
    return toc


def _render_markdown(tokens: list[Token], markdown: MarkdownIt) -> str:
    def paragraph_open(tokens, index, options, env):
        if tokens[index].meta.get("figure"):
            return "<figure>"
        if tokens[index].meta.get("source_line"):
            return '<p class="source-line">'
        return markdown.renderer.renderToken(tokens, index, options, env)

    def paragraph_close(tokens, index, options, env):
        if tokens[index].meta.get("figure"):
            return "</figure>\n"
        return markdown.renderer.renderToken(tokens, index, options, env)

    def image_rule(tokens, index, options, env):
        token = tokens[index]
        source = html.escape(token.attrGet("src") or "", quote=True)
        caption = html.escape(str(token.meta.get("caption", "")))
        image = f'<img src="{source}" alt="{caption}">'
        if token.meta.get("standalone"):
            return image + (f"<figcaption>{caption}</figcaption>" if caption else "")
        return image

    def table_open(tokens, index, options, env):
        caption = tokens[index].meta.get("caption")
        rendered = "<table>"
        if caption:
            rendered += f"<caption>{html.escape(str(caption))}</caption>"
        return rendered + "\n"

    def blockquote_open(tokens, index, options, env):
        callout = tokens[index].meta.get("callout")
        if callout:
            return f'<blockquote class="callout {callout}">\n'
        return markdown.renderer.renderToken(tokens, index, options, env)

    markdown.renderer.rules.update(
        {
            "paragraph_open": paragraph_open,
            "paragraph_close": paragraph_close,
            "image": image_rule,
            "table_open": table_open,
            "blockquote_open": blockquote_open,
        }
    )
    return markdown.renderer.render(tokens, markdown.options, {})


def _escaped(value: object) -> str:
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    elif isinstance(value, (date, datetime)):
        value = value.isoformat()
    return html.escape(str(value), quote=True)


def _cover_html(
    metadata: dict[str, object],
    brand: dict[str, object],
    report_root: Path,
    brand_root: Path,
    warnings: list[str],
) -> str:
    logo = ""
    if brand["logo"]:
        path = local_path(brand_root, str(brand["logo"]), "brand.yml logo")
        logo = (
            '<img class="cover-logo" alt="lustinus RESEARCH" '
            f'src="{_image_uri(path, "brand.yml logo", warnings)}">'
        )
    cover_image = ""
    if metadata.get("cover_image"):
        path = local_path(
            report_root, str(metadata["cover_image"]), "report.md cover_image"
        )
        cover_image = (
            '<img class="cover-image" alt="" '
            f'src="{_image_uri(path, "report.md cover_image", warnings)}">'
        )
    details = "".join(
        f'<div class="cover-detail"><span>{html.escape(label)}</span>{_escaped(metadata[field])}</div>'
        for field, label in (
            ("authors", "Authors"),
            ("sector", "Sector"),
            ("region", "Region"),
        )
        if not _missing(metadata.get(field))
    )
    subtitle = (
        f'<p class="subtitle">{_escaped(metadata["subtitle"])}</p>'
        if not _missing(metadata.get("subtitle"))
        else ""
    )
    disclaimer = metadata.get("disclaimer") or brand["disclaimer"]
    classification = metadata.get("classification") or ""
    return (
        '<section class="cover">'
        f'<div class="brand-name">{_escaped(brand["name"])}</div>'
        f"{logo}{cover_image}"
        f'<h1>{_escaped(metadata["title"])}</h1>'
        f"{subtitle}"
        f'<p class="report-date">{_escaped(metadata["date"])}</p>'
        f'<div class="cover-details">{details}</div>'
        f'<p class="classification">{_escaped(classification)}</p>'
        f'<p class="disclaimer">{_escaped(disclaimer)}</p>'
        f'<p class="brand-footer">{_escaped(brand["footer"])}</p>'
        "</section>"
    )


def _font_corpora(
    metadata: dict[str, object], brand: dict[str, object], tokens: list[Token]
) -> tuple[str, str]:
    sans = [
        "目录",
        "表",
        "图",
        "0123456789 /",
        str(brand["name"]),
        str(brand["footer"]),
    ]
    for field in (
        "title",
        "subtitle",
        "date",
        "authors",
        "sector",
        "region",
        "classification",
    ):
        value = metadata.get(field)
        if not _missing(value):
            if isinstance(value, list):
                sans.extend(str(item) for item in value)
            else:
                sans.append(str(value))
    sans.append(str(metadata.get("disclaimer") or brand["disclaimer"]))
    for field, label in (("authors", "Authors"), ("sector", "Sector"), ("region", "Region")):
        if not _missing(metadata.get(field)):
            sans.append(label)

    serif = []
    sans_inline = False
    in_table = False
    hidden_h1_inline = (
        1
        if len(tokens) >= 3
        and tokens[0].type == "heading_open"
        and tokens[0].tag == "h1"
        and tokens[0].level == 0
        and tokens[1].type == "inline"
        and tokens[2].type == "heading_close"
        else -1
    )
    for index, token in enumerate(tokens):
        if token.type in ("code_block", "fence"):
            serif.append(token.content)
        if token.type == "heading_open" and token.tag in ("h2", "h3"):
            sans_inline = True
        elif token.type == "table_open":
            in_table = True
        if token.meta.get("caption"):
            sans.append(str(token.meta["caption"]))
        if token.type == "inline":
            if index == hidden_h1_inline:
                continue
            visible = []
            for child in token.children or ():
                if child.type in ("text", "code_inline"):
                    visible.append(child.content)
                elif child.type == "image" and child.meta.get("standalone"):
                    if child.meta.get("caption"):
                        sans.append(str(child.meta["caption"]))
            (sans if sans_inline or in_table else serif).extend(visible)
        if token.type == "heading_close" and token.tag in ("h2", "h3"):
            sans_inline = False
        elif token.type == "table_close":
            in_table = False
    return "\n".join(sans), "\n".join(serif)


def _warn_font_fallback(
    role: str,
    family: str,
    charset: list[tuple[int, int]],
    visible_text: str,
    warnings: list[str],
) -> None:
    missing = sorted(
        {
            character
            for character in visible_text
            if not character.isspace()
            and not any(start <= ord(character) <= end for start, end in charset)
        },
        key=ord,
    )
    if missing:
        sample = ", ".join(f"{character} U+{ord(character):04X}" for character in missing[:8])
        warnings.append(
            f"font fallback ({role}_font {family}): missing {len(missing)} glyphs: {sample}"
        )


def _stylesheet(
    brand: dict[str, object],
    brand_root: Path,
    corpora: tuple[str, str],
    warnings: list[str],
) -> str:
    css_path = Path(__file__).resolve().parent.parent / "assets" / "report.css"
    try:
        css = css_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BuildError(f"report.css: cannot read: {exc}") from exc
    sans_family = str(brand["sans_font"])
    serif_family = str(brand["serif_font"])
    sans, sans_face, sans_charset = _font_css(sans_family, brand_root, "sans")
    serif, serif_face, serif_charset = _font_css(serif_family, brand_root, "serif")
    _warn_font_fallback("sans", sans_family, sans_charset, corpora[0], warnings)
    _warn_font_fallback("serif", serif_family, serif_charset, corpora[1], warnings)
    replacements = {
        "__ACCENT_COLOR__": str(brand["accent_color"]),
        "__SANS_FONT__": sans,
        "__SERIF_FONT__": serif,
        "__FONT_FACES__": sans_face + serif_face,
    }
    for placeholder, value in replacements.items():
        css = css.replace(placeholder, value)
    if re.search(r"__[A-Z_]+__", css):
        raise BuildError("report.css: unresolved placeholder")
    return css


def _html_document(
    metadata: dict[str, object],
    brand: dict[str, object],
    cover: str,
    toc: list[tuple[str, str]],
    body: str,
    css: str,
) -> str:
    toc_items = "".join(
        f'<li><a href="#{html.escape(target, quote=True)}">{html.escape(label)}</a></li>'
        for target, label in toc
    )
    return (
        "<!doctype html>\n"
        '<html lang="zh-CN"><head><meta charset="utf-8">'
        f"<title>{_escaped(metadata['title'])}</title>"
        f"<style>{css}</style></head><body>"
        f"{cover}"
        '<nav class="toc"><div class="toc-title">目录</div>'
        f"<ol>{toc_items}</ol></nav>"
        f'<main class="report-body">{body}</main>'
        "</body></html>\n"
    )


def _bookmark_labels(tree: list[tuple]) -> list[str]:
    labels: list[str] = []
    for label, _target, children, _state in tree:
        labels.append(label)
        labels.extend(_bookmark_labels(children))
    return labels


def validate_bookmarks(tree: list[tuple]) -> None:
    aliases = {
        normalized_heading(alias): index
        for index, section_aliases in enumerate(SECTION_ALIASES)
        for alias in section_aliases
    }
    present = {
        aliases[normalized_heading(label)]
        for label in _bookmark_labels(tree)
        if normalized_heading(label) in aliases
    }
    missing = [
        aliases[0] for index, aliases in enumerate(SECTION_ALIASES) if index not in present
    ]
    if missing:
        raise BuildError("PDF bookmarks missing canonical sections: " + ", ".join(missing))


def build_log(input_path: Path, page_count: int, warnings: list[str]) -> str:
    warning_lines = "warnings: none" if not warnings else "warnings:\n" + "".join(
        f"- {warning}\n" for warning in dict.fromkeys(warnings)
    ).rstrip("\n")
    return (
        f"input: {input_path.resolve()}\n"
        f"generated_at: {datetime.now().astimezone().isoformat()}\n"
        f"builder_version: {VERSION}\n"
        f"page_count: {page_count}\n"
        f"{warning_lines}\n"
        "structure: pass\n"
        "source: pass\n"
        "render: pass\n"
        "bookmark: pass\n"
    )


def publish_staged(staging: Path, output_dir: Path) -> None:
    backup = staging / ".backup"
    backups: dict[str, Path] = {}
    published: list[str] = []
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        backup.mkdir()
        for name in OUTPUT_FILES:
            source = staging / name
            if not source.is_file():
                raise OSError(f"staged output missing: {name}")
            target = output_dir / name
            if target.exists():
                if not target.is_file():
                    raise OSError(f"existing output is not a file: {name}")
                saved = backup / name
                os.replace(target, saved)
                backups[name] = saved
        for name in OUTPUT_FILES:
            os.replace(staging / name, output_dir / name)
            published.append(name)
    except OSError as exc:
        rollback_errors = []
        for name in published:
            try:
                (output_dir / name).unlink(missing_ok=True)
            except OSError as rollback_exc:
                rollback_errors.append(str(rollback_exc))
        for name, saved in backups.items():
            try:
                os.replace(saved, output_dir / name)
            except OSError as rollback_exc:
                rollback_errors.append(str(rollback_exc))
        suffix = f"; rollback failed: {'; '.join(rollback_errors)}" if rollback_errors else ""
        raise BuildError(f"cannot publish report outputs: {exc}{suffix}") from exc


def build_report(report_path: Path, brand_path: Path, output_dir: Path) -> None:
    try:
        text = report_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BuildError(f"report.md: cannot read {report_path}: {exc}") from exc
    metadata, body = split_frontmatter(text)
    markdown = MarkdownIt(
        "commonmark", {"html": False, "linkify": False}
    ).enable("table")
    try:
        tokens = markdown.parse(body)
    except Exception as exc:
        raise BuildError(f"report.md: Markdown parse failed: {exc}") from exc
    warnings = _validate_parsed(metadata, tokens, report_path)
    brand = load_brand(brand_path)
    report_root = report_path.resolve().parent
    brand_root = brand_path.resolve().parent
    toc = _prepare_tokens(tokens, report_root, warnings)
    corpora = _font_corpora(metadata, brand, tokens)
    rendered_body = _render_markdown(tokens, markdown)
    cover = _cover_html(metadata, brand, report_root, brand_root, warnings)
    css = _stylesheet(brand, brand_root, corpora, warnings)
    html_text = _html_document(metadata, brand, cover, toc, rendered_body, css)

    try:
        document = HTML(
            string=html_text, url_fetcher=local_url_fetcher
        ).render(font_config=FontConfiguration())
        page_count = len(document.pages)
        if page_count < 1:
            raise BuildError("render produced no pages")
        validate_bookmarks(document.make_bookmark_tree())
    except BuildError:
        raise
    except FatalURLFetchingError as exc:
        raise BuildError(f"render failed: {exc}") from exc
    except Exception as exc:
        raise BuildError(f"render failed: {exc}") from exc

    try:
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix=".jvc-report-", dir=output_dir.parent) as temporary:
            staging = Path(temporary)
            document.write_pdf(staging / "report.pdf")
            (staging / "report.html").write_text(html_text, encoding="utf-8")
            (staging / "build-report.txt").write_text(
                build_log(report_path, page_count, warnings), encoding="utf-8"
            )
            publish_staged(staging, output_dir)
    except BuildError:
        raise
    except FatalURLFetchingError as exc:
        raise BuildError(f"cannot write report outputs: {exc}") from exc
    except Exception as exc:
        raise BuildError(f"cannot write report outputs: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a local lustinus research report")
    parser.add_argument("report", type=Path)
    parser.add_argument("--brand", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        build_report(args.report, args.brand, args.output)
    except BuildError as exc:
        parser.exit(2, f"build failed: {exc}\n")
    except Exception as exc:
        parser.exit(2, f"build failed: unexpected build error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

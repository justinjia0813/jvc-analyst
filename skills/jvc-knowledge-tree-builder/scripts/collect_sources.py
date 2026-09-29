#!/usr/bin/env python3
"""Collect a deterministic source inventory for jvc-knowledge-tree-builder."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


TEXT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".csv",
    ".tsv",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".html",
    ".htm",
    ".xml",
    ".org",
    ".rst",
    ".canvas",
    ".drawio",
}

DOCX_EXTENSIONS = {".docx"}
PDF_EXTENSIONS = {".pdf"}
DEFAULT_EXCLUDES = {
    ".git",
    ".hg",
    ".svn",
    ".DS_Store",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "__pycache__",
}


@dataclass
class SourceFile:
    source_id: str
    path: str
    relative_path: str
    extension: str
    size_bytes: int
    readable: bool
    extract_status: str
    text_sample: str


def normalize_text(text: str, max_chars: int) -> str:
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def read_text_file(path: Path, max_chars: int) -> tuple[bool, str, str]:
    try:
      raw = path.read_bytes()
      text = raw.decode("utf-8")
    except UnicodeDecodeError:
      try:
        text = raw.decode("utf-8", errors="replace")
      except Exception as exc:  # pragma: no cover - defensive branch
        return False, f"decode_failed:{exc.__class__.__name__}", ""
    except Exception as exc:
      return False, f"read_failed:{exc.__class__.__name__}", ""
    return True, "text_sampled", normalize_text(text, max_chars)


def read_docx(path: Path, max_chars: int) -> tuple[bool, str, str]:
    try:
        with zipfile.ZipFile(path) as archive:
            xml_bytes = archive.read("word/document.xml")
    except Exception as exc:
        return False, f"docx_extract_failed:{exc.__class__.__name__}", ""

    try:
        root = ElementTree.fromstring(xml_bytes)
    except ElementTree.ParseError:
        return False, "docx_xml_parse_failed", ""

    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    parts = [node.text for node in root.findall(".//w:t", namespace) if node.text]
    return True, "docx_text_sampled", normalize_text(" ".join(parts), max_chars)


def iter_input_files(paths: Iterable[Path], excludes: set[str]) -> Iterable[Path]:
    for path in paths:
        resolved = path.expanduser().resolve()
        if not resolved.exists():
            continue
        if resolved.is_file():
            if not any(part in excludes for part in resolved.parts):
                yield resolved
            continue
        for root, dirs, files in os.walk(resolved):
            dirs[:] = sorted([name for name in dirs if name not in excludes])
            for filename in sorted(files):
                if filename in excludes:
                    continue
                yield Path(root) / filename


def collect(paths: list[Path], max_files: int, max_chars: int, excludes: set[str]) -> dict:
    files: list[SourceFile] = []
    access_issues: list[dict] = []
    roots = [str(path.expanduser().resolve()) for path in paths]

    for idx, file_path in enumerate(iter_input_files(paths, excludes), start=1):
        if len(files) >= max_files:
            access_issues.append(
                {
                    "path": str(file_path),
                    "issue": f"max_files_limit_reached:{max_files}",
                }
            )
            break

        suffix = file_path.suffix.lower()
        readable = False
        status = "unsupported_extension"
        sample = ""

        if suffix in TEXT_EXTENSIONS:
            readable, status, sample = read_text_file(file_path, max_chars)
        elif suffix in DOCX_EXTENSIONS:
            readable, status, sample = read_docx(file_path, max_chars)
        elif suffix in PDF_EXTENSIONS:
            status = "pdf_requires_pdf_tool"

        if not readable:
            access_issues.append({"path": str(file_path), "issue": status})

        try:
            common_root = Path(os.path.commonpath([str(file_path), *roots]))
            relative = str(file_path.relative_to(common_root))
        except Exception:
            relative = file_path.name

        files.append(
            SourceFile(
                source_id=f"S{idx}",
                path=str(file_path),
                relative_path=relative,
                extension=suffix or "<none>",
                size_bytes=file_path.stat().st_size,
                readable=readable,
                extract_status=status,
                text_sample=sample,
            )
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_roots": roots,
        "file_count": len(files),
        "readable_count": sum(1 for item in files if item.readable),
        "files": [asdict(item) for item in files],
        "access_issues": access_issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect source manifest for jvc-knowledge-tree-builder.")
    parser.add_argument("paths", nargs="+", help="Input files or folders.")
    parser.add_argument("--output", help="Write JSON manifest to this path. Defaults to stdout.")
    parser.add_argument("--max-files", type=int, default=200)
    parser.add_argument("--max-chars", type=int, default=4000)
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional filename or directory name to exclude. Can be repeated.",
    )
    args = parser.parse_args()

    manifest = collect(
        paths=[Path(value) for value in args.paths],
        max_files=args.max_files,
        max_chars=args.max_chars,
        excludes=DEFAULT_EXCLUDES.union(args.exclude),
    )

    output = json.dumps(manifest, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())

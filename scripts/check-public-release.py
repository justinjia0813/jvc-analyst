#!/usr/bin/env python3
"""Privacy gate to run before publishing this repository.

Blocks the release when any tracked file contains:
- a name from the private deny list (default ~/.config/jvc-analyst/private-names.txt,
  kept outside the repository so the list itself is never published); the
  repository owner in a github.com/<owner>/jvc-analyst URL is exempt;
- a local absolute home path (/Users/<name>, /home/<name>, C:\\Users\\<name>);
- a personal e-mail address;
- an API key, token or private-key block;
- author / company metadata inside .docx, .xlsx or .pptx files.

Usage: python3 scripts/check-public-release.py [--deny-list PATH]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DENY_LIST = Path.home() / ".config/jvc-analyst/private-names.txt"
OFFICE_SUFFIXES = {".docx", ".xlsx", ".pptx"}
ALLOWED_OFFICE_AUTHORS = {"", "jvc-analyst"}

PATTERNS = {
    "local home path": re.compile(r"(/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|[A-Za-z]:\\Users\\[A-Za-z0-9._-]+)"),
    "e-mail address": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "secret": re.compile(
        r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}"
        r"|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
    ),
}
ALLOWED_EMAILS = re.compile(r"(noreply@anthropic\.com|@example\.(com|org)|@users\.noreply\.github\.com)$")
ALLOWED_PATH_OWNERS = {"/Users/you", "/Users/username", "/home/user", "/home/you"}
OFFICE_META = re.compile(r"<(dc:creator|cp:lastModifiedBy|Company|Manager)>([^<]*)<")


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / name for name in output.decode().split("\0") if name]


def load_deny_list(path: Path) -> list[str]:
    if not path.is_file():
        return []
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.append(line)
    return names


def office_text(path: Path) -> tuple[str, list[str]]:
    texts, metadata = [], []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith(".xml"):
                continue
            data = archive.read(name).decode("utf-8", "ignore")
            if name.startswith("docProps/"):
                metadata += [value.strip() for _, value in OFFICE_META.findall(data)]
            texts.append(re.sub(r"<[^>]+>", " ", data))
    return " ".join(texts), metadata


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--deny-list", type=Path, default=DEFAULT_DENY_LIST)
    args = parser.parse_args(argv)

    deny = load_deny_list(args.deny_list)
    findings: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        if relative == "scripts/check-public-release.py":
            continue
        try:
            if path.suffix in OFFICE_SUFFIXES:
                text, metadata = office_text(path)
                for value in metadata:
                    if value not in ALLOWED_OFFICE_AUTHORS:
                        findings.append(f"{relative}: office metadata {value!r}")
            else:
                text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, zipfile.BadZipFile):
            continue
        scrubbed = re.sub(r"github\.com/[A-Za-z0-9-]+/jvc-analyst", "github.com/<owner>/jvc-analyst", text)
        for name in deny:
            if name in scrubbed:
                findings.append(f"{relative}: private name {name!r}")
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                value = match.group(0)
                if label == "e-mail address" and ALLOWED_EMAILS.search(value):
                    continue
                if label == "local home path" and value in ALLOWED_PATH_OWNERS:
                    continue
                findings.append(f"{relative}: {label} {value!r}")

    if not deny:
        print(f"warning: deny list not found at {args.deny_list}; private-name check skipped", file=sys.stderr)
    if findings:
        print("public release check failed:", file=sys.stderr)
        for finding in sorted(set(findings)):
            print(f"  {finding}", file=sys.stderr)
        return 1
    print(f"public release check passed: {len(tracked_files())} files, {len(deny)} private names")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
set -euo pipefail

scripts/check-jvc-assets.sh
scripts/check-excel-workbooks.sh
python3 scripts/check-docx-template-customization.py
python3 scripts/check-docx-format-consistency.py
python3 scripts/check-docx-filename-rule.py
python3 scripts/check-v3-foundation.py
python3 scripts/check-skill-evals.py
python3 skills/jvc-research-core/scripts/check_package.py
python3 scripts/check-research-core-install.py
python3 skills/jvc-research-report/scripts/check_package.py
python3 skills/jvc-ic-memo/scripts/check_package.py
python3 skills/jvc-knowledge-tree-builder/scripts/check_package.py
python3 scripts/check-atomic-cognition.py
python3 scripts/check-asset-scan.py
python3 scripts/check-governance.py
python3 scripts/check-public-release.py

python3 -m py_compile \
  scripts/check-governance.py \
  scripts/check-public-release.py \
  scripts/check-research-core-install.py \
  scripts/check-skill-evals.py \
  scripts/check-v3-foundation.py \
  scripts/generate-workbook.py \
  scripts/validate-workbook.py \
  skills/jvc-research-core/scripts/check_package.py \
  skills/jvc-research-core/scripts/researchctl.py \
  skills/jvc-research-report/scripts/build_report.py \
  skills/jvc-research-report/scripts/check_package.py \
  skills/jvc-meeting-notes/scripts/generate_meeting_notes.py \
  skills/jvc-invoice-manager/scripts/process_invoices.py \
  skills/jvc-invoice-manager/scripts/generate_summary.py

# Use the same repository file boundary as the asset scan; no ripgrep dependency.
python3 - <<'PYSCAN'
from pathlib import Path
import re
import subprocess

pattern = re.compile(r"(?<![j/])vc-analyst|`/(prescreen|bull-case|bear-case|track-research|comps-dd|market-sizing|roi-modeler|ic-memo|meeting-notes|talk-notes|invoice-manager)`")
assert not pattern.search("/tmp/vc-analyst/report.md")
assert pattern.search("vc-analyst")
paths = subprocess.check_output([
    "git", "ls-files", "--cached", "--others", "--exclude-standard", "-z",
    "--", "*.md", "*.sh", "*.py",
]).decode().split("\0")
failures = []
for name in sorted(set(paths) - {"", "scripts/check-review-fixes.sh"}):
    for line_number, line in enumerate(Path(name).read_text().splitlines(), 1):
        if pattern.search(line):
            failures.append(f"{name}:{line_number}: stale package name or slash command")
if failures:
    raise SystemExit("\n".join(failures))
PYSCAN

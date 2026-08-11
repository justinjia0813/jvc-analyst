#!/usr/bin/env bash
# Minimal read-only guard for the three historical Excel fixtures.
#
# These tracked .xlsx files are pre-CSV legacy fixtures kept as historical
# records. They are NOT active contracts: active Market Sizing / ROI Modeler
# outputs are CSV and Comps/DD output is Markdown. This script proves the
# fixtures exist, are tracked, are non-empty, and are byte-identical to their
# tracked blob at HEAD (git show HEAD:path | cmp -s). It never parses workbook
# contents and never touches untracked user files (e.g. roi-modeler-template.xlsx).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fixtures=(
  "examples/market-sizing-example.xlsx"
  "examples/comps-dd-example.xlsx"
  "examples/roi-modeler-example.xlsx"
)

for fixture in "${fixtures[@]}"; do
  if ! git -C "$repo_root" ls-files --error-unmatch -- "$fixture" >/dev/null 2>&1; then
    echo "FAIL: $fixture is not tracked (must remain a tracked historical fixture)" >&2
    exit 1
  fi
  if [ ! -s "$repo_root/$fixture" ]; then
    echo "FAIL: $fixture is missing or empty" >&2
    exit 1
  fi
  # Byte-compare against the tracked blob without parsing workbook contents.
  if ! git -C "$repo_root" show "HEAD:$fixture" | cmp -s - "$repo_root/$fixture"; then
    echo "FAIL: $fixture differs from its tracked blob at HEAD" >&2
    exit 1
  fi
  echo "ok (tracked historical fixture, matches HEAD blob): $fixture"
done

cat <<'EOF'
The three example .xlsx workbooks are historical fixtures only and are NOT
active contracts. Active outputs are CSV (market-sizing.csv, roi-modeler.csv)
and Markdown (03-comps-dd.md, research-report.md). Each fixture is verified
byte-identical to its tracked blob at HEAD; no untracked user file was read
and no workbook contents were parsed.
EOF

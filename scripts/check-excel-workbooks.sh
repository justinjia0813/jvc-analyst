#!/usr/bin/env bash
set -euo pipefail

python3 -c "import openpyxl" >/dev/null

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

check_workbook() {
  local name="$1"
  local template="templates/${name}-template.md"
  local generated="${tmpdir}/${name}.xlsx"
  local example="examples/${name}-example.xlsx"

  python3 scripts/generate-workbook.py "$template" "$generated"
  python3 scripts/validate-workbook.py "$generated" "$template"
  python3 scripts/validate-workbook.py "$example" "$template"
}

check_workbook "comps-dd"
check_workbook "market-sizing"
check_workbook "roi-modeler"

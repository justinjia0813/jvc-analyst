#!/usr/bin/env bash
set -euo pipefail

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "missing file: $path" >&2
    return 1
  fi
}

require_text() {
  local path="$1"
  local text="$2"
  if ! grep -Fq "$text" "$path"; then
    echo "missing text in $path: $text" >&2
    return 1
  fi
}

reject_text() {
  local path="$1"
  local text="$2"
  if grep -Fq "$text" "$path"; then
    echo "unexpected text in $path: $text" >&2
    return 1
  fi
}

require_file "scripts/generate-workbook.py"
require_file "scripts/validate-workbook.py"
require_file "scripts/check-excel-workbooks.sh"

require_file "skills/bear-case/SKILL.md"
require_file "templates/bear-case-template.md"
require_file "examples/bear-case-example.md"
require_file "scripts/check-bear-case-assets.sh"

require_file "examples/comps-dd-example.xlsx"
require_file "examples/market-sizing-example.xlsx"
require_file "examples/roi-modeler-example.xlsx"

require_text "WORKFLOW.md" '| `/bear-case` | 给项目素材，输出最锋利的不投理由 | 已建 |'
require_text "WORKFLOW.md" "05-comps-dd.xlsx"
require_text "WORKFLOW.md" "05-market-sizing.xlsx"
require_text "WORKFLOW.md" "05-roi-modeler.xlsx"
require_text "WORKFLOW.md" "comps-dd.xlsx"
reject_text "WORKFLOW.md" "comparables.md"

require_text "CLAUDE.md" "所有投资面向输出"
require_text "CLAUDE.md" "限制、敏感性、未验证假设"

require_text "skills/prescreen/SKILL.md" "description: Use when"
require_text "skills/ic-memo/SKILL.md" "description: Use when"

require_text "skills/comps-dd/SKILL.md" "scripts/generate-workbook.py"
require_text "skills/comps-dd/SKILL.md" "scripts/validate-workbook.py"
require_text "skills/market-sizing/SKILL.md" "scripts/generate-workbook.py"
require_text "skills/market-sizing/SKILL.md" "scripts/validate-workbook.py"
require_text "skills/roi-modeler/SKILL.md" "scripts/generate-workbook.py"
require_text "skills/roi-modeler/SKILL.md" "scripts/validate-workbook.py"

scripts/check-bear-case-assets.sh
scripts/check-excel-workbooks.sh

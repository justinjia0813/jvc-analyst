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

require_file "skills/market-sizing/SKILL.md"
require_file "templates/market-sizing-template.md"
require_file "examples/market-sizing-example.md"
require_file "examples/market-sizing-example.xlsx"
require_file "scripts/generate-workbook.py"
require_file "scripts/validate-workbook.py"

require_text "skills/market-sizing/SKILL.md" "name: market-sizing"
require_text "skills/market-sizing/SKILL.md" ".xlsx"
require_text "skills/market-sizing/SKILL.md" "自上而下"
require_text "skills/market-sizing/SKILL.md" "自下而上"
require_text "skills/market-sizing/SKILL.md" "正交"
require_text "skills/market-sizing/SKILL.md" "复算"
require_text "skills/market-sizing/SKILL.md" "多算"
require_text "skills/market-sizing/SKILL.md" "scripts/generate-workbook.py"
require_text "skills/market-sizing/SKILL.md" "scripts/validate-workbook.py"

require_text "templates/market-sizing-template.md" "# /market-sizing 市场规模建模 Excel 模板"
require_text "templates/market-sizing-template.md" "## Sheet: assumptions"
require_text "templates/market-sizing-template.md" "## Sheet: top_down"
require_text "templates/market-sizing-template.md" "## Sheet: bottom_up"
require_text "templates/market-sizing-template.md" "## Sheet: reconciliation"
require_text "templates/market-sizing-template.md" "## Sheet: orthogonality_check"
require_text "templates/market-sizing-template.md" "TAM"
require_text "templates/market-sizing-template.md" "SAM"
require_text "templates/market-sizing-template.md" "SOM"

require_text "examples/market-sizing-example.md" "# /market-sizing 市场规模建模 Excel 示例"
require_text "examples/market-sizing-example.md" "top_down"
require_text "examples/market-sizing-example.md" "bottom_up"
require_text "examples/market-sizing-example.md" "orthogonality_check"
require_text "examples/market-sizing-example.md" "[未核实]"

require_text "WORKFLOW.md" '| `/market-sizing` | 针对细分赛道做市场规模建模，输出 Excel | 已建 |'
require_text "library/skill-registry.md" '`market-sizing`'

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

require_file "skills/roi-modeler/SKILL.md"
require_file "templates/roi-modeler-template.md"
require_file "examples/roi-modeler-example.md"

require_text "skills/roi-modeler/SKILL.md" "name: roi-modeler"
require_text "skills/roi-modeler/SKILL.md" ".xlsx"
require_text "skills/roi-modeler/SKILL.md" "未来五年"
require_text "skills/roi-modeler/SKILL.md" "融资稀释"
require_text "skills/roi-modeler/SKILL.md" "保守"
require_text "skills/roi-modeler/SKILL.md" "中性"
require_text "skills/roi-modeler/SKILL.md" "乐观"
require_text "skills/roi-modeler/SKILL.md" "MOIC"
require_text "skills/roi-modeler/SKILL.md" "IRR"

require_text "templates/roi-modeler-template.md" "# /roi-modeler 投资回报 Excel 模板"
require_text "templates/roi-modeler-template.md" "## Sheet: investment_terms"
require_text "templates/roi-modeler-template.md" "## Sheet: financial_forecast"
require_text "templates/roi-modeler-template.md" "## Sheet: financing_dilution"
require_text "templates/roi-modeler-template.md" "## Sheet: exit_scenarios"
require_text "templates/roi-modeler-template.md" "## Sheet: returns"
require_text "templates/roi-modeler-template.md" "MOIC"
require_text "templates/roi-modeler-template.md" "IRR"

require_text "examples/roi-modeler-example.md" "# /roi-modeler 投资回报 Excel 示例"
require_text "examples/roi-modeler-example.md" "保守"
require_text "examples/roi-modeler-example.md" "中性"
require_text "examples/roi-modeler-example.md" "乐观"
require_text "examples/roi-modeler-example.md" "[未核实]"

require_text "WORKFLOW.md" '| `/roi-modeler` | 计算投资回报和融资稀释，输出 Excel | 已建 |'
require_text "library/skill-registry.md" '`roi-modeler`'

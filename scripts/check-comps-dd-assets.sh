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

require_file "skills/comps-dd/SKILL.md"
require_file "templates/comps-dd-template.md"
require_file "examples/comps-dd-example.md"
require_file "examples/comps-dd-example.xlsx"
require_file "scripts/generate-workbook.py"
require_file "scripts/validate-workbook.py"

require_text "skills/comps-dd/SKILL.md" "name: comps-dd"
require_text "skills/comps-dd/SKILL.md" ".xlsx"
require_text "skills/comps-dd/SKILL.md" "上市公司"
require_text "skills/comps-dd/SKILL.md" "初创公司"
require_text "skills/comps-dd/SKILL.md" "国内为主"
require_text "skills/comps-dd/SKILL.md" "海外龙头"
require_text "skills/comps-dd/SKILL.md" "最近一年收入"
require_text "skills/comps-dd/SKILL.md" "最新估值"
require_text "skills/comps-dd/SKILL.md" "scripts/generate-workbook.py"
require_text "skills/comps-dd/SKILL.md" "scripts/validate-workbook.py"

require_text "templates/comps-dd-template.md" "# /comps-dd 竞品尽调 Excel 模板"
require_text "templates/comps-dd-template.md" "## Sheet: companies"
require_text "templates/comps-dd-template.md" "公司名称"
require_text "templates/comps-dd-template.md" "国家/地区"
require_text "templates/comps-dd-template.md" "技术路线"
require_text "templates/comps-dd-template.md" "产品"
require_text "templates/comps-dd-template.md" "最近一年收入"
require_text "templates/comps-dd-template.md" "最新估值"
require_text "templates/comps-dd-template.md" "## Sheet: sources"

require_text "examples/comps-dd-example.md" "# /comps-dd 竞品尽调 Excel 示例"
require_text "examples/comps-dd-example.md" "companies"
require_text "examples/comps-dd-example.md" "[未核实]"

require_text "WORKFLOW.md" '| `/comps-dd` | 调研竞争对手，输出上市公司和初创公司对比 Excel | 已建 |'
require_text "library/skill-registry.md" '`comps-dd`'

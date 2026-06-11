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

require_file "skills/prescreen/SKILL.md"
require_file "templates/prescreen-template.md"
require_file "examples/prescreen-example.md"

require_text "skills/prescreen/SKILL.md" "name: prescreen"
require_text "skills/prescreen/SKILL.md" "templates/prescreen-template.md"
require_text "skills/prescreen/SKILL.md" "bear case"
require_text "skills/prescreen/SKILL.md" "[未核实]"

require_text "templates/prescreen-template.md" "# /prescreen 初筛纪要"
require_text "templates/prescreen-template.md" "## 一页事实摘要"
require_text "templates/prescreen-template.md" "## 七维初筛判断"
require_text "templates/prescreen-template.md" "## Bear Case 雏形"
require_text "templates/prescreen-template.md" "## 未覆盖的关键问题"
require_text "templates/prescreen-template.md" "## [未核实] 清单"

require_text "examples/prescreen-example.md" "# /prescreen 初筛纪要"
require_text "examples/prescreen-example.md" "[公开信息"
require_text "examples/prescreen-example.md" "[未核实]"

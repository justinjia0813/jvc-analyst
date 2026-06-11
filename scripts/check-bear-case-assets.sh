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
    echo "forbidden text in $path: $text" >&2
    return 1
  fi
}

require_file "skills/bear-case/SKILL.md"
require_file "templates/bear-case-template.md"
require_file "examples/bear-case-example.md"

require_text "skills/bear-case/SKILL.md" "name: bear-case"
require_text "skills/bear-case/SKILL.md" "description: Use when"
require_text "skills/bear-case/SKILL.md" "templates/bear-case-template.md"
require_text "skills/bear-case/SKILL.md" "挑剔 LP"
require_text "skills/bear-case/SKILL.md" "竞品 CEO"
require_text "skills/bear-case/SKILL.md" "怀疑论同行"
require_text "skills/bear-case/SKILL.md" "可证伪性"
require_text "skills/bear-case/SKILL.md" "下一步取证"

require_text "templates/bear-case-template.md" "# /bear-case 反向论证"
require_text "templates/bear-case-template.md" "## 反方论点总览"
require_text "templates/bear-case-template.md" "## 1. 挑剔 LP 视角"
require_text "templates/bear-case-template.md" "## 2. 竞品 CEO 视角"
require_text "templates/bear-case-template.md" "## 3. 怀疑论同行视角"
require_text "templates/bear-case-template.md" "## 可证伪验证计划"

require_text "examples/bear-case-example.md" "# /bear-case 反向论证"
require_text "examples/bear-case-example.md" "[未核实]"
require_text "examples/bear-case-example.md" "[待交叉验证]"
require_text "examples/bear-case-example.md" "可证伪性"
require_text "examples/bear-case-example.md" "下一步取证"
reject_text "examples/bear-case-example.md" "建议不投"
reject_text "examples/bear-case-example.md" "pass 掉"

require_text "WORKFLOW.md" '| `/bear-case` | 给项目素材，输出最锋利的不投理由 | 已建 |'
require_text "library/skill-registry.md" '`bear-case`'

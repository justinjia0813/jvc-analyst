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

require_file "skills/ic-memo/SKILL.md"
require_file "templates/ic-memo-template.md"
require_file "examples/ic-memo-example.md"

require_text "skills/ic-memo/SKILL.md" "name: ic-memo"
require_text "skills/ic-memo/SKILL.md" "description: Use when"
require_text "skills/ic-memo/SKILL.md" "templates/ic-memo-template.md"
require_text "skills/ic-memo/SKILL.md" "风险与反方观点"
require_text "skills/ic-memo/SKILL.md" "不替用户决策"
require_text "skills/ic-memo/SKILL.md" "[未核实]"

require_text "templates/ic-memo-template.md" "# /ic-memo 投决备忘录"
require_text "templates/ic-memo-template.md" "## 交易摘要"
require_text "templates/ic-memo-template.md" "## 公司概况"
require_text "templates/ic-memo-template.md" "## 市场与竞争"
require_text "templates/ic-memo-template.md" "## 产品与技术"
require_text "templates/ic-memo-template.md" "## 团队"
require_text "templates/ic-memo-template.md" "## 财务与单位经济"
require_text "templates/ic-memo-template.md" "## 投资逻辑"
require_text "templates/ic-memo-template.md" "## 风险与反方观点"
require_text "templates/ic-memo-template.md" "## 估值与条款"
require_text "templates/ic-memo-template.md" "## 待决事项"
require_text "templates/ic-memo-template.md" "## 未覆盖的关键问题"
require_text "templates/ic-memo-template.md" "## 来源索引"

require_text "examples/ic-memo-example.md" "# /ic-memo 投决备忘录"
require_text "examples/ic-memo-example.md" "[示例素材"
require_text "examples/ic-memo-example.md" "[未核实]"
require_text "examples/ic-memo-example.md" "风险与反方观点"
reject_text "examples/ic-memo-example.md" "建议投资"
reject_text "examples/ic-memo-example.md" "不建议投资"
reject_text "examples/ic-memo-example.md" "pass 掉"

require_text "WORKFLOW.md" '| `/ic-memo` | 给所有素材，按模板合成 IC memo 初稿 | 已建 |'
require_text "library/skill-registry.md" '`ic-memo`'

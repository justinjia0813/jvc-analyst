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

require_file "skills/track-research/SKILL.md"
require_file "templates/track-research-template.md"
require_file "examples/track-research-example.md"

require_text "skills/track-research/SKILL.md" "name: track-research"
require_text "skills/track-research/SKILL.md" "产业知识图谱"
require_text "skills/track-research/SKILL.md" "行业简史"
require_text "skills/track-research/SKILL.md" "技术路线"
require_text "skills/track-research/SKILL.md" "产业趋势"
require_text "skills/track-research/SKILL.md" "templates/track-research-template.md"

require_text "templates/track-research-template.md" "# /track-research 产业知识图谱"
require_text "templates/track-research-template.md" "## 行业定义与边界"
require_text "templates/track-research-template.md" "## 行业简史"
require_text "templates/track-research-template.md" "## 技术路线"
require_text "templates/track-research-template.md" "## 产业链图谱"
require_text "templates/track-research-template.md" "## 产业趋势"
require_text "templates/track-research-template.md" "## 关键玩家"
require_text "templates/track-research-template.md" "## 未核实与待补证据"

require_text "examples/track-research-example.md" "# /track-research 产业知识图谱"
require_text "examples/track-research-example.md" "[公开资料"
require_text "examples/track-research-example.md" "[未核实]"

require_text "WORKFLOW.md" '| `/track-research` | 给细分赛道，快速构建产业知识图谱 | 已建 |'
require_text "library/skill-registry.md" '`track-research`'

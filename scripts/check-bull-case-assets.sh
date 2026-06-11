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

require_file "skills/bull-case/SKILL.md"
require_file "templates/bull-case-template.md"
require_file "examples/bull-case-example.md"

require_text "skills/bull-case/SKILL.md" "name: bull-case"
require_text "skills/bull-case/SKILL.md" "templates/bull-case-template.md"
require_text "skills/bull-case/SKILL.md" "行业趋势"
require_text "skills/bull-case/SKILL.md" "技术节点"
require_text "skills/bull-case/SKILL.md" "团队优势"
require_text "skills/bull-case/SKILL.md" "商业化进展"
require_text "skills/bull-case/SKILL.md" "标题级"
require_text "skills/bull-case/SKILL.md" "正文级"

require_text "templates/bull-case-template.md" "# /bull-case 投资亮点"
require_text "templates/bull-case-template.md" "## 标题级亮点"
require_text "templates/bull-case-template.md" "## 正文级亮点"
require_text "templates/bull-case-template.md" "### 1. 行业趋势"
require_text "templates/bull-case-template.md" "### 2. 技术节点"
require_text "templates/bull-case-template.md" "### 3. 团队优势"
require_text "templates/bull-case-template.md" "### 4. 商业化进展"
require_text "templates/bull-case-template.md" "## 仍需验证"

require_text "examples/bull-case-example.md" "# /bull-case 投资亮点"
require_text "examples/bull-case-example.md" "[示例素材"
require_text "examples/bull-case-example.md" "事实依据"
require_text "examples/bull-case-example.md" "判断论点"
reject_text "examples/bull-case-example.md" "建议投资"
reject_text "examples/bull-case-example.md" "必投"

require_text "WORKFLOW.md" '| `/bull-case` | 给项目素材，输出最锋利的投资亮点 | 已建 |'
require_text "library/skill-registry.md" '`bull-case`'

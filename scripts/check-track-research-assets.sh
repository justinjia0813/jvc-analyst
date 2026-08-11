#!/usr/bin/env bash
set -euo pipefail

scripts/check-jvc-assets.sh jvc-track-research

required_files=(
  templates/track-research-template.md
  examples/track-research-example.md
  skills/jvc-knowledge-tree-builder/scripts/validate_output.py
  skills/jvc-knowledge-tree-builder/scripts/check_package.py
)

for file in "${required_files[@]}"; do
  test -f "$file" || { echo "missing Track Research handoff asset: $file" >&2; exit 1; }
done

for file in skills/jvc-track-research/SKILL.md templates/track-research-template.md examples/track-research-example.md; do
  for text in \
    "知识树与市场模型交接" \
    "根问题" \
    "主要分支" \
    "实体与关系" \
    "来源编号" \
    "有效主张编号" \
    "Market Sizing（Market Sizing，市场规模测算" \
    "变量" \
    "单位" \
    "数据缺口" \
    "开放问题"; do
    rg -Fq "$text" "$file" || { echo "$file missing handoff contract: $text" >&2; exit 1; }
  done
done

for text in \
  'tracks/{track-slug}/landscape.md' \
  "首次完整联网赛道研究的唯一负责人" \
  "任务专项公开研究"; do
  rg -Fq "$text" skills/jvc-track-research/SKILL.md || {
    echo "skills/jvc-track-research/SKILL.md missing ownership boundary: $text" >&2
    exit 1
  }
done

python3 skills/jvc-knowledge-tree-builder/scripts/check_package.py

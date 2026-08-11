#!/usr/bin/env bash
set -euo pipefail

scripts/check-jvc-assets.sh jvc-prescreen

required_files=(
  templates/prescreen-template.md
  examples/prescreen-example.md
  examples/prescreen-missing-data-example.md
  skills/jvc-prescreen/scripts/validate_output.py
  skills/jvc-prescreen/scripts/check_package.py
)

for file in "${required_files[@]}"; do
  test -f "$file" || { echo "missing prescreen asset: $file" >&2; exit 1; }
done

for file in skills/jvc-prescreen/SKILL.md examples/prescreen-example.md; do
  rg -Fq "Return on Investment Modeler（ROI Modeler，投资回报建模工具" "$file" || {
    echo "$file missing correct ROI Modeler expansion order" >&2
    exit 1
  }
  if rg -Fq "ROI Modeler（Return on Investment Modeler" "$file"; then
    echo "$file uses ROI Modeler before its full expansion" >&2
    exit 1
  fi
done

for file in skills/jvc-prescreen/SKILL.md templates/prescreen-template.md examples/prescreen-example.md; do
  for text in \
    "商业模式" \
    "上下游与价值分配" \
    "赛道有效性" \
    "市场规模粗算" \
    "五年收入情景" \
    "交易与回报粗算" \
    "风险、证伪条件与下一步" \
    "来源、假设与未知项" \
    "公式：" \
    "单位：" \
    "依据：" \
    "置信度：" \
    "Top-down" \
    "Multiple on Invested Capital" \
    "Internal Rate of Return" \
    "【第三方事实】" \
    "【公司自述】" \
    "【用户观察】" \
    "【模型估算】" \
    "【未知/待验证】"; do
    rg -Fq "$text" "$file" || { echo "$file missing: $text" >&2; exit 1; }
  done
done

for text in \
  "商业模式要素：缺失" \
  "商业模式要素：完整" \
  "市场锚点：存在" \
  "市场锚点：缺失" \
  "交易条款：完整" \
  "交易条款：缺少估值或投资额" \
  "单位勾稽：不兼容" \
  "影响章节：" \
  "ROI Modeler" \
  "01-prescreen.md"; do
  rg -Fq "$text" skills/jvc-prescreen/SKILL.md || {
    echo "skills/jvc-prescreen/SKILL.md missing: $text" >&2
    exit 1
  }
done

for text in "商业模式要素：缺失" "市场锚点：缺失" "仅列公式，不输出市场数字" "交易条款：缺少估值或投资额" "条件式敏感性框架" "单位勾稽：不兼容" "下游传播：停止" "影响章节：" "不给任何数值回报或结果（单点或区间）"; do
  rg -Fq "$text" examples/prescreen-missing-data-example.md || {
    echo "missing-data example missing: $text" >&2
    exit 1
  }
done

python3 skills/jvc-prescreen/scripts/check_package.py

prescreen_tmp_dir="$(mktemp -d)"
trap 'rm -rf "$prescreen_tmp_dir"' EXIT
for example in examples/prescreen-example.md examples/prescreen-missing-data-example.md; do
  example_dir="$prescreen_tmp_dir/$(basename "$example" .md)"
  mkdir "$example_dir"
  cp "$example" "$example_dir/01-prescreen.md"
  python3 skills/jvc-prescreen/scripts/validate_output.py "$example_dir/01-prescreen.md"
done

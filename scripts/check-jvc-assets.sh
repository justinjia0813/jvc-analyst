#!/usr/bin/env bash
set -euo pipefail

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "missing file: $path" >&2
    return 1
  fi
}

require_dir() {
  local path="$1"
  if [[ ! -d "$path" ]]; then
    echo "missing directory: $path" >&2
    return 1
  fi
}

reject_path() {
  local path="$1"
  if [[ -e "$path" ]]; then
    echo "unexpected legacy path: $path" >&2
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
    echo "unexpected text in $path: $text" >&2
    return 1
  fi
}

reject_backticked_legacy_slash_commands() {
  local pattern='`/(prescreen|bull-case|bear-case|track-research|comps-dd|market-sizing|roi-modeler|ic-memo|meeting-notes|talk-notes|invoice-manager)`'
  if rg -n "$pattern" --glob '*.md' .; then
    echo "found legacy slash command without jvc- prefix" >&2
    return 1
  fi
}

check_skill() {
  local skill="$1"
  require_file "skills/${skill}/SKILL.md"
  require_text "skills/${skill}/SKILL.md" "name: ${skill}"
  require_text "setup" "${skill}"
  require_text "library/skill-registry.md" "\`${skill}\`"
}

skills=(
  jvc-prescreen
  jvc-bull-case
  jvc-bear-case
  jvc-track-research
  jvc-research-report
  jvc-knowledge-tree-builder
  jvc-comps-dd
  jvc-market-sizing
  jvc-roi-modeler
  jvc-ic-memo
  jvc-meeting-notes
  jvc-talk-notes
  jvc-invoice-manager
)

if [[ $# -gt 0 ]]; then
  skills=("$@")
fi

require_file "setup"
require_file "manifest.json"
require_file "agents/interface.yaml"
require_file "security/network_policy.json"
require_file "security/permission_policy.json"
require_file "evals/trigger_cases.json"
require_file "evals/output/cases.json"
require_file "scripts/check-skill-evals.py"
require_file "scripts/check-governance.py"
require_file "reports/skill-ir.json"
require_file "reports/trust_report.json"
require_file "reports/trust_report.md"
require_file "reports/review-studio.json"
require_file "reports/review-studio.md"
require_text "README.md" "# jvc-analyst"
require_text "README.md" "## 工具总览"
require_text "README.md" "### 控制与引擎"
require_text "README.md" "### 赛道级工具"
require_text "README.md" "### 项目级工具"
require_text "README.md" "### 输出级工具"
require_text "README.md" "### 日常工具"
require_text "README.md" "叙事研究默认使用 Markdown，公式模型默认使用 CSV"
require_text "README.md" "PDF（Portable Document Format，可移植文档格式"
require_text "README.md" "HTML（HyperText Markup Language，超文本标记语言"
require_text "README.md" "DOCX（Office Open XML Document，Office 开放 XML 文档"
require_text "README.md" "TAM（Total Addressable Market，总潜在市场"
require_text "README.md" "SAM（Serviceable Available Market，可服务市场"
require_text "README.md" "SOM（Serviceable Obtainable Market，可获得市场"
require_text "README.md" "Optical Character Recognition（OCR，光学字符识别"
require_text "library/skill-registry.md" "Comps/DD（Comparable Companies Analysis / Due Diligence，可比公司分析/尽职调查，用于系统核验竞争与可比对象）"
require_text "library/skill-registry.md" "OCR（Optical Character Recognition，光学字符识别"
require_text "library/skill-registry.md" "PDF（Portable Document Format，可移植文档格式"
reject_text "library/skill-registry.md" "Comps DD（Due Diligence"
reject_text "library/skill-registry.md" "Comps DD"
require_text "README.md" "P1（Priority 1，优先级 1"
require_text "library/skill-registry.md" "P1（Priority 1，优先级 1"
require_text "library/skill-registry.md" "P2（Priority 2，优先级 2"
reject_text "README.md" "P1（Phase 1"
reject_text "README.md" "P2（Phase 2"
reject_text "library/skill-registry.md" "P1（Phase 1"
reject_text "library/skill-registry.md" "P2（Phase 2"
require_text "README.md" "## 项目档案目录约定"
require_text "CLAUDE.md" "jvc-analyst"
reject_path "WORKFLOW.md"

for legacy in \
  prescreen bull-case bear-case track-research comps-dd market-sizing roi-modeler ic-memo meeting-notes talk-notes invoice-manager
do
  reject_path "skills/${legacy}"
done

for skill in "${skills[@]}"; do
  check_skill "$skill"
done

require_file "skills/jvc-meeting-notes/scripts/generate_meeting_notes.py"
require_file "skills/jvc-meeting-notes/templates/访谈纪要模板.docx"
require_file "skills/jvc-meeting-notes/requirements.txt"
require_file "scripts/check-docx-template-customization.py"
require_file "scripts/check-docx-format-consistency.py"
require_file "scripts/check-docx-filename-rule.py"
require_text "skills/jvc-meeting-notes/SKILL.md" "integrated_from: meeting-notes"
require_text "skills/jvc-meeting-notes/SKILL.md" "JVC_DOCX_TEMPLATE"
require_text "skills/jvc-meeting-notes/SKILL.md" "templates/custom.docx"
require_text "skills/jvc-meeting-notes/SKILL.md" "【YYYY年MM月DD日访谈】{访谈对象}.docx"
require_text "skills/jvc-talk-notes/SKILL.md" "skills/jvc-meeting-notes/scripts/generate_meeting_notes.py"
require_text "skills/jvc-talk-notes/SKILL.md" "问答纪要"
require_text "skills/jvc-talk-notes/SKILL.md" "JVC_DOCX_TEMPLATE"
require_text "skills/jvc-talk-notes/SKILL.md" "subsections.heading"
require_text "skills/jvc-talk-notes/SKILL.md" "事实层索引"
require_text "skills/jvc-talk-notes/SKILL.md" "【YYYY年MM月DD日访谈】{访谈对象}.docx"

require_file "skills/jvc-invoice-manager/scripts/process_invoices.py"
require_file "skills/jvc-invoice-manager/scripts/generate_summary.py"
require_file "skills/jvc-invoice-manager/templates/报销模板.xlsx"
require_file "skills/jvc-invoice-manager/requirements.txt"
require_text "skills/jvc-invoice-manager/SKILL.md" "integrated_from: invoice-manager"

require_file "skills/jvc-ic-memo/references/ic-memo-template.md"
require_file "skills/jvc-ic-memo/scripts/validate_final.py"
require_file "skills/jvc-ic-memo/scripts/check_package.py"
reject_path "templates/ic-memo-template.md"
require_text "skills/jvc-ic-memo/SKILL.md" 'version: "5.0.0"'
require_text "skills/jvc-ic-memo/SKILL.md" "06-ic-memo-review.md"
require_text "skills/jvc-ic-memo/SKILL.md" "预审通过"
require_text "skills/jvc-ic-memo/SKILL.md" "06-ic-memo.md"
require_text "skills/jvc-ic-memo/SKILL.md" "validate_final.py"
require_text "skills/jvc-ic-memo/SKILL.md" "不做机械标签删除"
require_text "skills/jvc-ic-memo/SKILL.md" "只生成明确标注不完整的预审版"
require_text "skills/jvc-ic-memo/SKILL.md" "素材缺失不等于可绕过"
require_text "skills/jvc-ic-memo/SKILL.md" "页码引用"
require_text "skills/jvc-ic-memo/references/ic-memo-template.md" "预审版"
require_text "skills/jvc-ic-memo/references/ic-memo-template.md" "终版转换合同"
require_text "skills/jvc-ic-memo/references/ic-memo-template.md" "页码引用"
require_text "skills/jvc-ic-memo/references/ic-memo-template.md" "[S编号]"
require_text "CLAUDE.md" "预审版必须完整暴露"
require_text "CLAUDE.md" "终版是唯一例外"
require_text "README.md" "06-ic-memo-review.md"
require_text "README.md" "预审通过"
require_text "library/skill-registry.md" "预审版"
require_text "skills/jvc-deal-flow/references/workflow-contract.md" "06-ic-memo-review.md"
require_text "skills/jvc-deal-flow/references/workflow-contract.md" '批准后生成 `06-ic-memo.md`'
require_text "skills/jvc-deal-flow/references/workflow-contract.md" '`jvc-track-research` → `jvc-knowledge-tree-builder`'
require_text "skills/jvc-deal-flow/references/workflow-contract.md" '`jvc-track-research` → `jvc-market-sizing`'
require_text "skills/jvc-deal-flow/references/workflow-contract.md" '项目产物 → `jvc-ic-memo`'
require_text "skills/jvc-deal-flow/references/workflow-contract.md" '赛道产物 → `jvc-research-report`'

require_text "skills/jvc-bear-case/SKILL.md" "IC boss"
require_text "templates/bear-case-template.md" "IC boss"
require_text "templates/bear-case-template.md" "IP 归属 / TAM/SAM 口径"
require_text "examples/bear-case-example.md" "IC boss"
require_text "examples/bear-case-example.md" "IP 和市场口径不清"

require_text "skills/jvc-comps-dd/SKILL.md" 'version: "4.0.0"'
require_text "skills/jvc-comps-dd/SKILL.md" '唯一活跃主产物：`03-comps-dd.md`'
reject_text "skills/jvc-comps-dd/SKILL.md" "scripts/generate-workbook.py"
reject_text "skills/jvc-comps-dd/SKILL.md" "scripts/validate-workbook.py"
reject_text "skills/jvc-comps-dd/SKILL.md" ".xlsx"
require_file "skills/jvc-market-sizing/references/model-contract.md"
require_file "skills/jvc-market-sizing/scripts/validate_csv.py"
require_file "skills/jvc-market-sizing/scripts/check_package.py"
require_file "templates/market-sizing-template.csv"
require_file "examples/market-sizing-example.csv"
require_text "skills/jvc-market-sizing/SKILL.md" 'version: "4.0.0"'
require_text "skills/jvc-market-sizing/SKILL.md" "market-sizing.csv"
require_text "skills/jvc-market-sizing/SKILL.md" "scripts/validate_csv.py"
reject_text "skills/jvc-market-sizing/SKILL.md" "scripts/generate-workbook.py"
reject_text "skills/jvc-market-sizing/SKILL.md" "scripts/validate-workbook.py"
reject_text "skills/jvc-market-sizing/SKILL.md" ".xlsx"
require_file "skills/jvc-roi-modeler/references/model-contract.md"
require_file "skills/jvc-roi-modeler/scripts/validate_csv.py"
require_file "templates/roi-modeler-template.csv"
require_text "skills/jvc-roi-modeler/SKILL.md" "scripts/validate_csv.py"
require_text "templates/comps-dd-template.md" '最终输出文件：`03-comps-dd.md`'
require_text "templates/market-sizing-template.md" '`market-sizing.csv`'
require_text "examples/market-sizing-example.md" "market-sizing-example.csv"
require_text "templates/roi-modeler-template.md" "{项目名}_jvc-roi-modeler_{YYYYMMDD}.csv"

reject_backticked_legacy_slash_commands

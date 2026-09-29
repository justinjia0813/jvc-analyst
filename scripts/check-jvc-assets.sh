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
  if ! grep -Fq -- "$text" "$path"; then
    echo "missing text in $path: $text" >&2
    return 1
  fi
}

reject_backticked_legacy_slash_commands() {
  local pattern='`/(prescreen|bull-case|bear-case|track-research|comps-dd|market-sizing|roi-modeler|ic-memo|meeting-notes|talk-notes|invoice-manager)`'
  local path result
  git ls-files --cached --others --exclude-standard -z -- '*.md' |
  while IFS= read -r -d '' path; do
    if grep -nE "$pattern" -- "$path"; then
      echo "found legacy slash command without jvc- prefix: $path" >&2
      return 1
    else
      result=$?
      [[ "$result" -eq 1 ]] || return "$result"
    fi
  done
}

check_skill() {
  local skill="$1"
  require_file "skills/${skill}/SKILL.md"
  require_text "skills/${skill}/SKILL.md" "name: ${skill}"
  require_text "setup" "${skill}"
  require_text "library/skill-registry.md" "\`${skill}\`"
}

skills=(
  jvc-meeting-notes
  jvc-interview-prep
  jvc-prescreen
  jvc-business-economics
  jvc-track-research
  jvc-workbook
  jvc-thesis-test
  jvc-ic-memo
  jvc-dd-report-digest
  jvc-portfolio-tracking
  jvc-research-report
  jvc-knowledge-tree-builder
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
require_text "README.md" "## 项目档案目录约定"
require_text "README.md" "## 从 3.0 迁移"
require_text "CLAUDE.md" "jvc-analyst"
reject_path "WORKFLOW.md"

for legacy in \
  prescreen bull-case bear-case track-research comps-dd market-sizing roi-modeler ic-memo meeting-notes talk-notes invoice-manager
do
  reject_path "skills/${legacy}"
done

# Retired in 4.0: must not reappear as installable skills.
for retired in \
  jvc-bull-case jvc-bear-case jvc-talk-notes jvc-claim-audit jvc-customer-validation \
  jvc-founder-assessment jvc-financing-milestones jvc-diligence-plan jvc-industry-mechanics \
  jvc-competitive-positioning jvc-market-sizing jvc-comps-dd jvc-roi-modeler \
  jvc-return-underwriting jvc-decision-memo jvc-deal-flow
do
  reject_path "skills/${retired}"
  require_text "setup" "${retired}"
done

for skill in "${skills[@]}"; do
  check_skill "$skill"
done

require_file "skills/jvc-meeting-notes/scripts/generate_meeting_notes.py"
require_file "skills/jvc-meeting-notes/templates/访谈纪要模板.docx"
require_file "skills/jvc-meeting-notes/requirements.txt"
require_file "skills/jvc-meeting-notes/references/layouts.md"
require_file "scripts/check-docx-template-customization.py"
require_file "scripts/check-docx-format-consistency.py"
require_file "scripts/check-docx-filename-rule.py"
require_text "skills/jvc-meeting-notes/SKILL.md" "integrated_from: meeting-notes"
require_text "skills/jvc-meeting-notes/SKILL.md" "三项自查"
require_text "skills/jvc-meeting-notes/references/layouts.md" "JVC_DOCX_TEMPLATE"
require_text "skills/jvc-meeting-notes/references/layouts.md" "templates/custom.docx"
require_text "skills/jvc-meeting-notes/references/layouts.md" "【YYYY年MM月DD日访谈】{访谈对象}.docx"
require_text "skills/jvc-meeting-notes/references/layouts.md" "subsections"

require_file "skills/jvc-invoice-manager/scripts/process_invoices.py"
require_file "skills/jvc-invoice-manager/scripts/generate_summary.py"
require_file "skills/jvc-invoice-manager/templates/报销模板.xlsx"
require_file "skills/jvc-invoice-manager/requirements.txt"
require_text "skills/jvc-invoice-manager/SKILL.md" "integrated_from: invoice-manager"

require_file "skills/jvc-ic-memo/references/ic-memo-template.md"
require_file "skills/jvc-ic-memo/scripts/validate_final.py"
require_file "skills/jvc-ic-memo/scripts/check_package.py"
reject_path "templates/ic-memo-template.md"
require_text "skills/jvc-ic-memo/SKILL.md" 'version: "6.0.0"'
require_text "skills/jvc-ic-memo/SKILL.md" "06-ic-memo-review.md"
require_text "skills/jvc-ic-memo/SKILL.md" "预审通过"
require_text "skills/jvc-ic-memo/SKILL.md" "06-ic-memo.md"
require_text "skills/jvc-ic-memo/SKILL.md" "validate_final.py"
require_text "skills/jvc-ic-memo/SKILL.md" "--mode gate"
require_text "skills/jvc-ic-memo/SKILL.md" "不做机械标签删除"
require_text "skills/jvc-ic-memo/SKILL.md" "只生成明确标注不完整的预审版"
require_text "skills/jvc-ic-memo/SKILL.md" "素材缺失不等于可绕过"
require_text "skills/jvc-ic-memo/SKILL.md" "页码引用"
require_text "skills/jvc-ic-memo/references/ic-memo-template.md" "预审版"
require_text "skills/jvc-ic-memo/references/ic-memo-template.md" "终版转换合同"
require_text "skills/jvc-ic-memo/references/ic-memo-template.md" "页码引用"
require_text "skills/jvc-ic-memo/references/ic-memo-template.md" "[S编号]"
require_text "CLAUDE.md" "先出预审版"
require_text "CLAUDE.md" "终版只能来自已审查的"
require_text "README.md" "06-ic-memo-review.md"
require_text "README.md" "预审通过"
require_text "library/skill-registry.md" "预审版"

require_text "skills/jvc-thesis-test/SKILL.md" "什么情况下就错了"
require_text "skills/jvc-thesis-test/SKILL.md" "04-bull-case.md"
require_text "skills/jvc-thesis-test/SKILL.md" "04-bear-case.md"

require_text "skills/jvc-workbook/SKILL.md" "scripts/generate-workbook.py"
require_text "skills/jvc-workbook/SKILL.md" "scripts/validate-workbook.py"
require_text "skills/jvc-workbook/SKILL.md" "market-sizing-template.md"
require_text "skills/jvc-workbook/SKILL.md" "comps-dd-template.md"
require_text "skills/jvc-workbook/SKILL.md" "roi-modeler-template.md"
require_text "templates/comps-dd-template.md" "05-comps-dd.xlsx"
require_text "templates/market-sizing-template.md" "05-market-sizing.xlsx"
require_text "templates/roi-modeler-template.md" "05-roi-modeler.xlsx"

require_text "skills/jvc-research-core/SKILL.md" "--mode gate"
require_text "skills/jvc-research-core/references/caller-contract.md" "--mode deliver"

reject_backticked_legacy_slash_commands

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
require_text "skills/jvc-meeting-notes/SKILL.md" "integrated_from: https://github.com/justinjia0813/meeting-notes"
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
require_text "skills/jvc-invoice-manager/SKILL.md" "integrated_from: https://github.com/justinjia0813/invoice-manager"

require_text "skills/jvc-bear-case/SKILL.md" "IC boss"
require_text "templates/bear-case-template.md" "IC boss"
require_text "templates/bear-case-template.md" "IP 归属 / TAM/SAM 口径"
require_text "examples/bear-case-example.md" "IC boss"
require_text "examples/bear-case-example.md" "IP 和市场口径不清"

require_text "skills/jvc-comps-dd/SKILL.md" "scripts/generate-workbook.py"
require_text "skills/jvc-comps-dd/SKILL.md" "scripts/validate-workbook.py"
require_text "skills/jvc-market-sizing/SKILL.md" "scripts/generate-workbook.py"
require_text "skills/jvc-market-sizing/SKILL.md" "scripts/validate-workbook.py"
require_text "skills/jvc-roi-modeler/SKILL.md" "scripts/generate-workbook.py"
require_text "skills/jvc-roi-modeler/SKILL.md" "scripts/validate-workbook.py"
require_text "templates/comps-dd-template.md" "{赛道或项目名}_jvc-comps-dd_{YYYYMMDD}.xlsx"
require_text "templates/market-sizing-template.md" "{细分赛道}_jvc-market-sizing_{YYYYMMDD}.xlsx"
require_text "templates/roi-modeler-template.md" "{项目名}_jvc-roi-modeler_{YYYYMMDD}.xlsx"

reject_backticked_legacy_slash_commands

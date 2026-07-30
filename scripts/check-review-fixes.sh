#!/usr/bin/env bash
set -euo pipefail

scripts/check-jvc-assets.sh
scripts/check-excel-workbooks.sh
python3 scripts/check-docx-template-customization.py
python3 scripts/check-docx-format-consistency.py
python3 scripts/check-docx-filename-rule.py
python3 scripts/check-v3-foundation.py
python3 scripts/check-skill-evals.py
python3 skills/jvc-research-core/scripts/check_package.py
python3 scripts/check-research-core-install.py
python3 skills/jvc-research-report/scripts/check_package.py
python3 scripts/check-governance.py

python3 -m py_compile \
  scripts/check-governance.py \
  scripts/check-research-core-install.py \
  scripts/check-skill-evals.py \
  scripts/check-v3-foundation.py \
  scripts/generate-workbook.py \
  scripts/validate-workbook.py \
  skills/jvc-research-core/scripts/check_package.py \
  skills/jvc-research-core/scripts/researchctl.py \
  skills/jvc-research-report/scripts/build_report.py \
  skills/jvc-research-report/scripts/check_package.py \
  skills/jvc-meeting-notes/scripts/generate_meeting_notes.py \
  skills/jvc-invoice-manager/scripts/process_invoices.py \
  skills/jvc-invoice-manager/scripts/generate_summary.py

stale_pattern='(?<![j/])vc-analyst|`/(prescreen|bull-case|bear-case|track-research|comps-dd|market-sizing|roi-modeler|ic-memo|meeting-notes|talk-notes|invoice-manager)`'
if printf '%s\n' '/tmp/vc-analyst/report.md' | rg --pcre2 -q "$stale_pattern"; then
  echo "stale-name pattern must allow vc-analyst in filesystem paths" >&2
  exit 1
fi
if ! printf '%s\n' 'vc-analyst' | rg --pcre2 -q "$stale_pattern"; then
  echo "stale-name pattern must reject the bare legacy package name" >&2
  exit 1
fi
if rg --pcre2 -n "$stale_pattern" --glob '*.md' --glob '*.sh' --glob '*.py' --glob '!scripts/check-review-fixes.sh' .; then
  echo "found stale vc-analyst or unprefixed slash command reference" >&2
  exit 1
fi

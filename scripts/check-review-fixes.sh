#!/usr/bin/env bash
set -euo pipefail

scripts/check-jvc-assets.sh
scripts/check-excel-workbooks.sh
python3 scripts/check-docx-template-customization.py
python3 scripts/check-docx-format-consistency.py

python3 -m py_compile \
  scripts/generate-workbook.py \
  scripts/validate-workbook.py \
  skills/jvc-meeting-notes/scripts/generate_meeting_notes.py \
  skills/jvc-invoice-manager/scripts/process_invoices.py \
  skills/jvc-invoice-manager/scripts/generate_summary.py

stale_pattern='(?<!j)vc-analyst|`/(prescreen|bull-case|bear-case|track-research|comps-dd|market-sizing|roi-modeler|ic-memo|meeting-notes|talk-notes|invoice-manager)`'
if rg --pcre2 -n "$stale_pattern" --glob '*.md' --glob '*.sh' --glob '*.py' --glob '!scripts/check-review-fixes.sh' .; then
  echo "found stale vc-analyst or unprefixed slash command reference" >&2
  exit 1
fi

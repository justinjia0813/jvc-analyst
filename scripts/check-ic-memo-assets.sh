#!/usr/bin/env bash
set -euo pipefail

scripts/check-jvc-assets.sh jvc-ic-memo

skill="skills/jvc-ic-memo/SKILL.md"
template="skills/jvc-ic-memo/references/ic-memo-template.md"

# Active IC Memo inputs are the Markdown / CSV artifacts, not legacy workbooks.
for artifact in '03-comps-dd.md' 'market-sizing.csv' '05-roi-modeler.csv'; do
  if ! grep -Fq "$artifact" "$skill"; then
    echo "missing active input mapping in $skill: $artifact" >&2
    exit 1
  fi
  if ! grep -Fq "$artifact" "$template"; then
    echo "missing active input mapping in $template: $artifact" >&2
    exit 1
  fi
done

# The pre-review -> explicit user approval -> clean-final gate must not relax.
for gate in '预审通过' 'validate_final.py' '06-ic-memo.md' 'ready'; do
  if ! grep -Fq "$gate" "$skill"; then
    echo "missing approval gate wording in $skill: $gate" >&2
    exit 1
  fi
done

# No legacy workbook wording in the active mapping.
if rg -n 'Excel 各 sheet|\.xlsx|工作簿' "$skill" "$template"; then
  echo "found a legacy IC Memo workbook contract" >&2
  exit 1
fi

#!/usr/bin/env bash
set -euo pipefail

scripts/check-jvc-assets.sh jvc-comps-dd

required_headings=(
  "## 范围与口径"
  "## 公司分层"
  "## 可比指标"
  "## 目标与可比公司对照"
  "## 上下游"
  "## 海外标杆"
  "## 来源索引"
  "## 覆盖缺口"
  "## 下一步尽调动作"
)

require_exact_line() {
  local path="$1"
  local text="$2"
  if ! grep -Fxq "$text" "$path"; then
    echo "missing exact line in $path: $text" >&2
    return 1
  fi
}

check_output_name() {
  [[ "$1" == "03-comps-dd.md" ]]
}

check_markdown_sections() {
  local path="$1"
  local heading
  for heading in "${required_headings[@]}"; do
    grep -Fxq "$heading" "$path" || return 1
  done
}

check_markdown_profile() {
  python3 - "$1" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    policy = json.load(handle)["artifact_policy"]

expected = {
    "kind": "markdown",
    "allowed_suffixes": [".md"],
    "required_names": ["03-comps-dd.md"],
    "required_sheets": [],
}
if policy != expected:
    raise SystemExit(1)
PY
}

check_comps_eval() {
  python3 - <<'PY'
import json

with open("evals/output/cases.json", encoding="utf-8") as handle:
    cases = [case for case in json.load(handle)["cases"] if case.get("skill") == "jvc-comps-dd"]

if len(cases) != 1:
    raise SystemExit(1)
case = cases[0]
if case.get("id") != "comps-dd-markdown-contract" or case.get("artifact_family") != "markdown":
    raise SystemExit(1)
for assertion in case.get("assertions", []):
    if assertion.get("type") == "workbook_sheets" or str(assertion.get("path", "")).endswith(".xlsx"):
        raise SystemExit(1)

# The output eval must reject legacy workbook references in the template and
# the example, not only in the SKILL and profile.
for path in ("templates/comps-dd-template.md", "examples/comps-dd-example.md"):
    negative = [
        assertion
        for assertion in case.get("assertions", [])
        if assertion.get("type") == "not_contains_any" and assertion.get("path") == path
    ]
    if len(negative) != 1:
        raise SystemExit(1)
    texts = negative[0].get("texts", [])
    for forbidden in (".xlsx", "generate-workbook.py", "validate-workbook.py"):
        if forbidden not in texts:
            raise SystemExit(1)

# The output eval must pin the fixed artifact name through the Research Core
# profile required_names, matching the SKILL/template "03-comps-dd.md" claim.
profile_assertions = [
    assertion
    for assertion in case.get("assertions", [])
    if assertion.get("type") == "contains"
    and assertion.get("path") == "skills/jvc-research-core/profiles/jvc-comps-dd.json"
]
if not any('"required_names": ["03-comps-dd.md"]' in assertion.get("text", "") for assertion in profile_assertions):
    raise SystemExit(1)
PY
}

require_exact_line skills/jvc-comps-dd/SKILL.md '唯一活跃主产物：`03-comps-dd.md`'
require_exact_line templates/comps-dd-template.md '最终输出文件：`03-comps-dd.md`'
check_output_name "03-comps-dd.md"
if check_output_name "05-comps-dd.xlsx"; then
  echo "legacy workbook output name was accepted" >&2
  exit 1
fi

check_markdown_sections templates/comps-dd-template.md
check_markdown_sections examples/comps-dd-example.md
if check_markdown_sections <(sed '/^## 范围与口径$/d' examples/comps-dd-example.md) 2>/dev/null; then
  echo "Markdown missing a required section was accepted" >&2
  exit 1
fi

check_markdown_profile skills/jvc-research-core/profiles/jvc-comps-dd.json
if check_markdown_profile <(sed 's/"kind": "markdown"/"kind": "xlsx"/' skills/jvc-research-core/profiles/jvc-comps-dd.json) 2>/dev/null; then
  echo "non-Markdown Research Core profile was accepted" >&2
  exit 1
fi

if rg -n '\.xlsx|generate-workbook\.py|validate-workbook\.py|"kind": "xlsx"' \
  skills/jvc-comps-dd/SKILL.md \
  templates/comps-dd-template.md \
  examples/comps-dd-example.md \
  skills/jvc-research-core/profiles/jvc-comps-dd.json; then
  echo "found an active Comps/DD workbook contract" >&2
  exit 1
fi

if ! check_comps_eval; then
  echo "Comps/DD output eval is not the Markdown contract" >&2
  exit 1
fi

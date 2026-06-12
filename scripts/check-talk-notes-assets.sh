#!/usr/bin/env bash
set -euo pipefail

bash scripts/check-jvc-assets.sh jvc-talk-notes

grep -Fq "name: jvc-talk-notes" skills/jvc-talk-notes/SKILL.md
grep -Fq "问答纪要" skills/jvc-talk-notes/SKILL.md
grep -Fq "skills/jvc-meeting-notes/scripts/generate_meeting_notes.py" skills/jvc-talk-notes/SKILL.md
grep -Fq "skills/jvc-meeting-notes/templates/访谈纪要模板.docx" skills/jvc-talk-notes/SKILL.md
grep -Fq "JVC_DOCX_TEMPLATE" skills/jvc-talk-notes/SKILL.md
grep -Fq "subsections.heading" skills/jvc-talk-notes/SKILL.md
grep -Fq "事实层索引" skills/jvc-talk-notes/SKILL.md
grep -Fq "完整回答" skills/jvc-talk-notes/SKILL.md
grep -Fq "不要输出" skills/jvc-talk-notes/SKILL.md

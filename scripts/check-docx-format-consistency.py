#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "skills/jvc-meeting-notes/scripts/generate_meeting_notes.py"
DEFAULT_TEMPLATE = ROOT / "skills/jvc-meeting-notes/templates/访谈纪要模板.docx"
EXPECTED_PAGE = (21.0, 29.7)
EXPECTED_MARGINS = (2.54, 2.54, 3.17, 3.17)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def run_generator(data: Path, output: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            str(data),
            "--template",
            str(DEFAULT_TEMPLATE),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def rounded_section(doc: Document) -> tuple[tuple[float, float], tuple[float, float, float, float]]:
    section = doc.sections[0]
    page = (round(section.page_width.cm, 2), round(section.page_height.cm, 2))
    margins = (
        round(section.top_margin.cm, 2),
        round(section.bottom_margin.cm, 2),
        round(section.left_margin.cm, 2),
        round(section.right_margin.cm, 2),
    )
    return page, margins


def nonempty_styles(path: Path) -> list[str]:
    return [p.style.name for p in Document(path).paragraphs if p.text.strip()]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        meeting_json = tmp / "meeting.json"
        talk_json = tmp / "talk.json"
        meeting_doc = tmp / "meeting.docx"
        talk_doc = tmp / "talk.docx"

        write_json(
            meeting_json,
            {
                "title": "2026/06/12 线上 访谈{格式测试}",
                "filename": "meeting.docx",
                "sections": [
                    {"heading": "一、公司基本情况", "content": "公司简介。"},
                    {
                        "heading": "二、公司核心技术",
                        "subsections": [
                            {"heading": "技术路线", "content": "技术内容。"},
                        ],
                    },
                ],
            },
        )
        write_json(
            talk_json,
            {
                "title": "2026/06/12 线上 客户访谈{格式测试}",
                "filename": "talk.docx",
                "sections": [
                    {"heading": "一、访谈基本信息", "content": "日期、形式、受访人。"},
                    {
                        "heading": "二、问答纪要",
                        "subsections": [
                            {"heading": "Q1：客户如何使用？", "content": "问题：...\n回答摘要：..."},
                        ],
                    },
                ],
            },
        )

        run_generator(meeting_json, meeting_doc)
        run_generator(talk_json, talk_doc)

        for label, path in {"meeting": meeting_doc, "talk": talk_doc}.items():
            page, margins = rounded_section(Document(path))
            assert page == EXPECTED_PAGE, f"{label} page size mismatch: {page}"
            assert margins == EXPECTED_MARGINS, f"{label} margin mismatch: {margins}"

        meeting_styles = nonempty_styles(meeting_doc)
        talk_styles = nonempty_styles(talk_doc)
        assert meeting_styles[:4] == talk_styles[:4], (
            "meeting and talk should share title, section, body, and section styles: "
            f"{meeting_styles[:4]} != {talk_styles[:4]}"
        )
        assert meeting_styles[4] == talk_styles[4], (
            f"subsection style mismatch: {meeting_styles[4]} != {talk_styles[4]}"
        )
        assert meeting_styles[4] == "JVC Subsection Heading", (
            f"meeting subsection should use JVC Subsection Heading, got {meeting_styles[4]}"
        )
        assert talk_styles[4] == "JVC Subsection Heading", (
            f"talk Q&A heading should use JVC Subsection Heading, got {talk_styles[4]}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

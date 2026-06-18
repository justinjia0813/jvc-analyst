#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "skills/jvc-meeting-notes/scripts/generate_meeting_notes.py"


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def run_generator(data: Path, output_dir: Path) -> None:
    subprocess.run(
        [sys.executable, str(GENERATOR), str(data), "--output", str(output_dir)],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def assert_generated(output_dir: Path, expected_name: str, legacy_name: str) -> None:
    expected = output_dir / expected_name
    legacy = output_dir / legacy_name
    assert expected.exists(), f"missing canonical filename: {expected.name}"
    assert not legacy.exists(), f"legacy filename should not be generated: {legacy.name}"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        meeting_json = tmp / "meeting.json"
        meeting_output = tmp / "meeting-output"
        write_json(
            meeting_json,
            {
                "title": "2026/06/12 线上 访谈{深安锂能}",
                "filename": "20260612_深安锂能_访谈纪要.docx",
                "sections": [{"heading": "一、公司基本情况", "content": "公司简介。"}],
            },
        )
        run_generator(meeting_json, meeting_output)
        assert_generated(
            meeting_output,
            "【2026年06月12日访谈】深安锂能.docx",
            "20260612_深安锂能_访谈纪要.docx",
        )

        talk_json = tmp / "talk.json"
        talk_output = tmp / "talk-output"
        write_json(
            talk_json,
            {
                "title": "2026/06/12 线上 客户访谈{深安锂能}",
                "interviewee": "张三",
                "filename": "20260612_深安锂能_客户_问答纪要.docx",
                "sections": [
                    {"heading": "一、访谈基本信息", "content": "日期、形式、受访人。"},
                    {
                        "heading": "二、问答纪要",
                        "subsections": [
                            {
                                "heading": "Q1：客户如何使用？",
                                "content": "完整回答：测试回答。\n对应事实层维度：客户\n待验证点：无明显待验证点。",
                            }
                        ],
                    },
                ],
            },
        )
        run_generator(talk_json, talk_output)
        assert_generated(
            talk_output,
            "【2026年06月12日访谈】张三.docx",
            "20260612_深安锂能_客户_问答纪要.docx",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from build_report import BuildError, validate_report


SECTIONS = (
    "研究设定与一页快照",
    "行业定义与边界",
    "行业简史与产业生命周期",
    "技术路线与商业可行性",
    "产业链图谱",
    "产业趋势、景气度与周期位置",
    "关键玩家",
    "监管 / 政策 / 标准",
    "投资相关问题与反证账本",
    "后续工作交接包",
    "来源索引",
)


def document(
    *,
    metadata: str = "title: 测试报告\ndate: 2026-07-22",
    sections: tuple[str, ...] = SECTIONS,
    citation: str = "[S1]",
    sources: str = "| S1 | 本地测试来源 |",
    image: str = "",
) -> str:
    body = []
    for index, section in enumerate(sections):
        prefix = "I、" if section == "来源索引" else ("A) " if index == 1 else "")
        body.extend((f"## {prefix}{section}", ""))
        if section == "研究设定与一页快照":
            body.extend((f"正文引用 {citation}", image, ""))
        if section == "来源索引":
            body.extend(("| ID | 来源 |", "| --- | --- |", sources, ""))
    return f"---\n{metadata}\n---\n" + "\n".join(body)


def expect_error(label: str, text: str, report_path: Path, expected: str) -> None:
    try:
        validate_report(text, report_path)
    except BuildError as exc:
        assert expected in str(exc), f"{label}: unexpected error: {exc}"
    else:
        raise AssertionError(f"{label}: expected BuildError")


def main() -> None:
    with TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory)
        report_path = root / "report.md"

        warnings = validate_report(document(), report_path)
        assert any("optional metadata missing" in warning for warning in warnings)

        expect_error(
            "missing date",
            document(metadata="title: 测试报告"),
            report_path,
            "date",
        )

        wrong_order = list(SECTIONS)
        wrong_order[1], wrong_order[2] = wrong_order[2], wrong_order[1]
        expect_error(
            "wrong order",
            document(sections=tuple(wrong_order)),
            report_path,
            "out-of-order",
        )

        expect_error(
            "undefined source",
            document(citation="[S2]"),
            report_path,
            "undefined sources: S2",
        )
        expect_error(
            "duplicate source",
            document(sources="| S1 | 来源甲 |\n| S1 | 来源乙 |"),
            report_path,
            "duplicate source IDs: S1",
        )
        expect_error(
            "remote image",
            document(image="![远程图片](https://example.com/image.png)"),
            report_path,
            "remote or absolute",
        )
        expect_error(
            "path escape",
            document(image="![越界图片](../outside.png)"),
            report_path,
            "escapes the report directory",
        )

    print("PASS: fixed research report input validation")


if __name__ == "__main__":
    main()

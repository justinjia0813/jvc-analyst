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
    source_table: str | None = None,
    image: str = "",
    after_sources: str = "",
) -> str:
    body = []
    for index, section in enumerate(sections):
        prefix = "I、" if section == "来源索引" else ("A) " if index == 1 else "")
        body.extend((f"## {prefix}{section}", ""))
        if section == "研究设定与一页快照":
            body.extend((f"正文引用 {citation}", image, ""))
        if section == "来源索引":
            body.extend(
                (
                    source_table
                    if source_table is not None
                    else f"| ID | 来源 |\n| --- | --- |\n{sources}",
                    "",
                )
            )
    if after_sources:
        body.extend((after_sources, ""))
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
        validate_report(document().replace("\n", "\r\n"), report_path)

        expect_error(
            "missing date",
            document(metadata="title: 测试报告"),
            report_path,
            "date",
        )
        expect_error(
            "falsy non-mapping frontmatter",
            document(metadata="[]"),
            report_path,
            "frontmatter must be a mapping",
        )
        expect_error(
            "title type",
            document(metadata="title: [测试报告]\ndate: 2026-07-22"),
            report_path,
            "metadata title must be a non-empty string",
        )
        expect_error(
            "date type",
            document(metadata="title: 测试报告\ndate: {year: 2026}"),
            report_path,
            "metadata date must be a non-empty string or date",
        )
        expect_error(
            "authors type",
            document(
                metadata=(
                    "title: 测试报告\n"
                    "date: 2026-07-22\n"
                    "authors: {name: 测试作者}"
                )
            ),
            report_path,
            "metadata authors must be a non-empty string or list of strings",
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
            "nested canonical heading",
            document().replace(
                "## A) 行业定义与边界",
                "> ## A) 行业定义与边界",
                1,
            ),
            report_path,
            "missing required section: 行业定义与边界",
        )
        expect_error(
            "duplicate canonical heading",
            document(after_sources="## 行业定义与边界"),
            report_path,
            "duplicate canonical section: 行业定义与边界",
        )
        expect_error(
            "unexpected heading",
            document(after_sources="## 附录"),
            report_path,
            "unexpected section: 附录",
        )

        expect_error(
            "undefined source",
            document(citation="[S2]"),
            report_path,
            "undefined sources: S2",
        )
        expect_error(
            "preamble source reference",
            document().replace(
                "---\n## 研究设定与一页快照",
                "---\n前导语 [S999]\n\n## 研究设定与一页快照",
                1,
            ),
            report_path,
            "undefined sources: S999",
        )
        expect_error(
            "level-three heading source reference",
            document(
                after_sources="## 未核实与待补证据\n### 待验证问题 [S998]"
            ),
            report_path,
            "undefined sources: S998",
        )
        expect_error(
            "image alt source reference",
            document(citation="", image="![图片说明 [S997]](missing.png)"),
            report_path,
            "undefined sources: S997",
        )
        expect_error(
            "duplicate source",
            document(sources="| S1 | 来源甲 |\n| S1 | 来源乙 |"),
            report_path,
            "duplicate source IDs: S1",
        )
        validate_report(
            document(
                source_table="ID | 来源\n--- | ---\nS1 | 本地测试来源",
            ),
            report_path,
        )
        expect_error(
            "fenced code is not a source definition",
            document(source_table="```text\n| S1 | 伪定义 |\n```"),
            report_path,
            "undefined sources: S1",
        )
        unused_warnings = validate_report(document(citation=""), report_path)
        assert "unused source definitions: S1" in unused_warnings
        ignored_reference_warnings = validate_report(
            document(
                citation="",
                source_table=(
                    "ID | 来源\n"
                    "--- | ---\n"
                    "S1 | 来源描述中的 [S2]"
                ),
                after_sources=(
                    "## 未核实与待补证据\n"
                    "```text\n[S3]\n```\n"
                    "行内代码 `[S4]`\n"
                    "<span data-source=\"[S5]\"></span>"
                ),
            ),
            report_path,
        )
        assert "unused source definitions: S1" in ignored_reference_warnings
        expect_error(
            "citation after source index",
            document(after_sources="## 未核实与待补证据\n后置引用 [S2]"),
            report_path,
            "undefined sources: S2",
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
        expect_error(
            "malformed URL",
            document(
                metadata=(
                    "title: 测试报告\n"
                    "date: 2026-07-22\n"
                    "cover_image: 'http://[invalid'"
                )
            ),
            report_path,
            "report.md cover_image: invalid path",
        )

    print("PASS: fixed research report input validation")


if __name__ == "__main__":
    main()

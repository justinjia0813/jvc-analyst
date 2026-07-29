from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.dont_write_bytecode = True

from build_report import (
    BuildError,
    _font_charset,
    _warn_font_fallback,
    build_log as format_build_log,
    local_path,
    publish_staged,
    validate_report,
)


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


def run_builder(report_path: Path, brand_path: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        (
            sys.executable,
            str(Path(__file__).with_name("build_report.py")),
            str(report_path),
            "--brand",
            str(brand_path),
            "--output",
            str(output),
        ),
        text=True,
        capture_output=True,
        check=False,
    )


def check_tracked_fixture() -> None:
    repository = Path(__file__).resolve().parents[3]
    fixture = repository / "examples" / "research-report-example" / "report.md"
    brand = Path(__file__).resolve().parent.parent / "assets" / "brand.yml"
    assert fixture.is_file(), f"tracked fixture missing: {fixture}"
    pdftotext = shutil.which("pdftotext")
    assert pdftotext, "pdftotext is required for tracked fixture PDF checks"

    with TemporaryDirectory() as temporary_directory:
        output = Path(temporary_directory) / "output"
        built = run_builder(fixture, brand, output)
        assert built.returncode == 0, built.stderr
        expected_outputs = {"report.pdf", "report.html", "build-report.txt"}
        assert {path.name for path in output.iterdir()} == expected_outputs

        pdf = output / "report.pdf"
        assert pdf.read_bytes().startswith(b"%PDF")
        extracted = subprocess.run(
            (pdftotext, str(pdf), "-"),
            text=True,
            capture_output=True,
            check=False,
        )
        assert extracted.returncode == 0, extracted.stderr
        assert "工业视觉质检" in extracted.stdout
        for heading in (
            "研究设定与一页快照",
            "技术路线与商业可行性",
            "后续工作交接包",
            "来源索引",
        ):
            assert heading in extracted.stdout

        html_text = (output / "report.html").read_text(encoding="utf-8")
        assert "lustinus RESEARCH" in html_text
        assert "callout-fact" in html_text
        assert "technology-routes.svg" not in html_text
        assert "data:image/svg+xml;base64," in html_text
        assert str(fixture.parent.resolve()) not in html_text

        build_log = (output / "build-report.txt").read_text(encoding="utf-8")
        for check in ("structure", "source", "render", "bookmark"):
            assert f"{check}: pass" in build_log


def main() -> None:
    check_tracked_fixture()
    with TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory)
        report_path = root / "report.md"

        charset_result = subprocess.CompletedProcess(
            args=(), returncode=0, stdout="10-12 1-3 3-9 a-f 20\n", stderr=""
        )
        with patch("build_report.subprocess.run", return_value=charset_result):
            assert _font_charset(root / "font.ttf", "test font") == [
                (0x1, 0x12),
                (0x20, 0x20),
            ]

        class CountingRanges(list[tuple[int, int]]):
            iterations = 0

            def __iter__(self):
                self.iterations += 1
                return super().__iter__()

        counting_ranges = CountingRanges([(0x20, 0x7E)])
        repeated_warnings: list[str] = []
        _warn_font_fallback(
            "serif", "Test Font", counting_ranges, "가" * 100, repeated_warnings
        )
        assert counting_ranges.iterations == 1
        assert repeated_warnings == [
            "font fallback (serif_font Test Font): missing 1 glyphs: 가 U+AC00"
        ]

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
        expect_error(
            "visible angled source reference",
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
            "undefined sources: S5",
        )
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
            "encoded path escape",
            document(image="![越界图片](%2e%2e%2foutside.png)"),
            report_path,
            "escapes the report directory",
        )
        expect_error(
            "encoded absolute path",
            document(image="![绝对路径](%2Ftmp%2Foutside.png)"),
            report_path,
            "remote or absolute",
        )
        expect_error(
            "encoded scheme",
            document(image="![远程图片](https%3A%2F%2Fexample.com%2Fimage.png)"),
            report_path,
            "remote or absolute",
        )
        try:
            local_path(
                report_path.parent,
                "%ZZ.png",
                "report.md image",
                uri_encoded=True,
            )
        except BuildError as exc:
            assert "invalid percent escape" in str(exc)
        else:
            raise AssertionError("local_path accepted a malformed percent escape")
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

        from PIL import Image

        Image.new("RGB", (32, 16), "#A06B2C").save(root / "local.png")
        Image.new("RGB", (32, 16), "#A06B2C").save(root / "中文图片.png")
        Image.new("RGB", (32, 16), "#A06B2C").save(root / "space image.png")
        Image.new("RGB", (32, 16), "#A06B2C").save(root / "logo%mark.png")
        Image.new("RGB", (32, 16), "#A06B2C").save(root / "cover%20image.png")
        (root / "font%20file.ttf").write_bytes(b"raw path fixture")
        (root / "vector.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="5">'
            '<rect width="10" height="5" fill="#A06B2C"/></svg>',
            encoding="utf-8",
        )
        brand_path = root / "brand.yml"
        valid_brand = (
            "name: lustinus RESEARCH\n"
            "logo: local.png\n"
            'accent_color: "#A06B2C"\n'
            "header: lustinus RESEARCH\n"
            'footer: "<Internal Research>"\n'
            "disclaimer: Internal research only. Verify sources before external distribution.\n"
            "sans_font: PingFang SC\n"
            "serif_font: Songti SC\n"
        )
        raw_resource_brand = valid_brand.replace(
            "logo: local.png", "logo: logo%mark.png"
        )
        brand_path.write_text(raw_resource_brand, encoding="utf-8")
        raw_resource_report = document(
            metadata=(
                "title: Raw Resource Paths\n"
                "date: 2026-07-22\n"
                "cover_image: cover%20image.png"
            )
        )
        report_path.write_text(raw_resource_report, encoding="utf-8")
        raw_resource_output = root / "raw-resource-output"
        raw_resource_build = run_builder(
            report_path, brand_path, raw_resource_output
        )
        assert raw_resource_build.returncode == 0, raw_resource_build.stderr
        raw_resource_html = (raw_resource_output / "report.html").read_text(
            encoding="utf-8"
        )
        assert raw_resource_html.count('src="data:image/png;base64,') == 2
        assert local_path(root, "font%20file.ttf", "brand.yml serif_font") == (
            root / "font%20file.ttf"
        ).resolve()

        brand_path.write_text(valid_brand, encoding="utf-8")
        encoded_names_report = document(
            image="![中文文件名](中文图片.png)\n\n![空格文件名](<space image.png>)"
        )
        report_path.write_text(encoded_names_report, encoding="utf-8")
        encoded_names_output = root / "encoded-names-output"
        encoded_names_build = run_builder(
            report_path, brand_path, encoded_names_output
        )
        assert encoded_names_build.returncode == 0, encoded_names_build.stderr
        encoded_names_html = (encoded_names_output / "report.html").read_text(
            encoding="utf-8"
        )
        assert encoded_names_html.count('src="data:image/png;base64,') == 3

        report_path.write_text(
            document(image="![空字节路径](%00.png)"), encoding="utf-8"
        )
        nul_path_build = run_builder(report_path, brand_path, root / "nul-path-output")
        assert nul_path_build.returncode == 2
        assert "report.md image: invalid path: %00.png" in nul_path_build.stderr
        assert "Traceback" not in nul_path_build.stderr

        rich_content = (
            "\n![本地图](local.png)\n\n"
            "*来源：本地测试来源*\n\n"
            "> [!FACT]\n"
            "> 已验证事实 [S1]\n\n"
            "> [!INFERENCE]\n"
            "> 测试推断\n\n"
            "> [!OPEN QUESTION]\n"
            "> 待验证问题\n\n"
            "> [!FACT] 不是合法标记\n\n"
            "![](local.png)\n\n"
            "![矢量图](vector.svg)\n\n"
            "表：测试表\n\n"
            "| A | B | C | D | E | F | G |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| 1 | 2 | 3 | 4 | 5 | 6 | 7 |\n\n"
            "*来源：本地测试来源*"
        )
        valid_report = document(
            metadata=(
                "title: 本地渲染测试\n"
                'subtitle: "自包含 <HTML> 与 PDF"\n'
                "date: 2026-07-22\n"
                "authors: [测试作者]\n"
                "sector: 测试行业\n"
                "region: 中国\n"
                "classification: Internal\n"
                "cover_image: local.png"
            ),
            image=rich_content,
        )
        report_path.write_text(valid_report, encoding="utf-8")
        output = root / "output"
        built = run_builder(report_path, brand_path, output)
        assert built.returncode == 0, built.stderr

        expected_outputs = {"report.pdf", "report.html", "build-report.txt"}
        assert {path.name for path in output.iterdir()} == expected_outputs
        assert (output / "report.pdf").read_bytes().startswith(b"%PDF")
        html_text = (output / "report.html").read_text(encoding="utf-8")
        assert "lustinus RESEARCH" in html_text
        assert "code { font-family: inherit; }" in html_text
        assert 'src="data:image/png;base64,' in html_text
        assert "local.png" not in html_text
        assert "vector.svg" not in html_text
        assert "data:image/svg+xml;base64," in html_text
        assert 'class="cover-logo"' in html_text
        assert 'class="cover-image"' in html_text
        assert "&lt;HTML&gt;" in html_text
        assert "&lt;Internal Research&gt;" in html_text
        assert '<figcaption>本地图</figcaption>' in html_text
        assert 'class="callout callout-fact"' in html_text
        assert 'class="callout callout-inference"' in html_text
        assert 'class="callout callout-open-question"' in html_text
        assert "[!INFERENCE]" not in html_text
        assert "[!OPEN QUESTION]" not in html_text
        assert "<blockquote>\n<p>[!FACT] 不是合法标记</p>" in html_text
        assert "<caption>表：测试表</caption>" in html_text
        assert 'class="source-line"' in html_text
        assert 'id="section-11"' in html_text
        assert 'href="#section-11"' in html_text
        build_log = (output / "build-report.txt").read_text(encoding="utf-8")
        for check in ("structure", "source", "render", "bookmark"):
            assert f"{check}: pass" in build_log
        for warning in (
            "optional metadata missing: disclaimer",
            "low-resolution image",
            "image caption missing",
            "table caption missing",
            "table has 7 columns",
            "image source line missing",
            "table source line missing",
        ):
            assert warning in build_log
        assert "low-resolution image" in build_log
        assert "low-resolution image (10px wide): vector.svg" not in build_log

        (output / "user-notes.txt").write_text("preserve me", encoding="utf-8")
        rebuilt = run_builder(report_path, brand_path, output)
        assert rebuilt.returncode == 0, rebuilt.stderr
        assert (output / "user-notes.txt").read_text(encoding="utf-8") == "preserve me"

        linked_source_report = document(
            image=(
                "\n![带链接来源的图片](local.png)\n\n"
                "*来源：[本地测试来源](https://example.com/source)*"
            )
        )
        report_path.write_text(linked_source_report, encoding="utf-8")
        linked_source = run_builder(report_path, brand_path, output)
        assert linked_source.returncode == 0, linked_source.stderr
        linked_html = (output / "report.html").read_text(encoding="utf-8")
        assert '<p class="source-line"><em>来源：<a href=' in linked_html
        linked_log = (output / "build-report.txt").read_text(encoding="utf-8")
        assert "image source line missing" not in linked_log

        tail_image_report = document(
            after_sources="## 未核实与待补证据\n\n![文末图片](vector.svg)"
        )
        report_path.write_text(tail_image_report, encoding="utf-8")
        tail_image = run_builder(report_path, brand_path, output)
        assert tail_image.returncode == 0, tail_image.stderr
        tail_html = (output / "report.html").read_text(encoding="utf-8")
        assert "<figure><img" in tail_html
        assert "<figcaption>文末图片</figcaption></figure>" in tail_html

        Image.new("RGB", (24, 12), "#2E6F62").save(
            root / "renamed.bin", format="PNG"
        )
        brand_path.write_text(
            valid_brand.replace("logo: local.png", "logo: null"),
            encoding="utf-8",
        )
        renamed_report = document(image="\n![改名位图](renamed.bin)")
        report_path.write_text(renamed_report, encoding="utf-8")
        renamed_image = run_builder(report_path, brand_path, output)
        assert renamed_image.returncode == 0, renamed_image.stderr
        renamed_html = (output / "report.html").read_text(encoding="utf-8")
        assert "data:image/png;base64," in renamed_html
        renamed_log = (output / "build-report.txt").read_text(encoding="utf-8")
        assert "low-resolution image (24px wide): renamed.bin" in renamed_log

        (root / "safe-locations.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg">'
            '<text data-note="literal url(ftp://example.com/not-a-resource)">'
            "https://example.com/display-only</text>"
            '<a href="data:text/plain;base64,//8=">'
            "<text>safe data link</text>"
            "</a></svg>",
            encoding="utf-8",
        )
        report_path.write_text(
            document(image="\n![安全矢量图](safe-locations.svg)"), encoding="utf-8"
        )
        safe_svg = run_builder(report_path, brand_path, output)
        assert safe_svg.returncode == 0, safe_svg.stderr

        report_path.write_text(
            document(
                metadata=(
                    "title: 测试报告\n"
                    "date: 2026-07-22\n"
                    "unused_private_note: 𐀀"
                )
            ),
            encoding="utf-8",
        )
        unknown_metadata = run_builder(report_path, brand_path, output)
        assert unknown_metadata.returncode == 0, unknown_metadata.stderr
        unknown_log = (output / "build-report.txt").read_text(encoding="utf-8")
        assert "U+10000" not in unknown_log

        hidden_h1_report = document().replace(
            "\n---\n## 研究设定与一页快照",
            "\n---\n# Hidden 𐀀\n\n## 研究设定与一页快照",
            1,
        )
        report_path.write_text(hidden_h1_report, encoding="utf-8")
        hidden_h1 = run_builder(report_path, brand_path, output)
        assert hidden_h1.returncode == 0, hidden_h1.stderr
        hidden_h1_log = (output / "build-report.txt").read_text(encoding="utf-8")
        assert "U+10000" not in hidden_h1_log

        visible_h1_report = hidden_h1_report.replace(
            "# Hidden 𐀀", "# Hidden ASCII\n\n# Visible 𐀀", 1
        )
        report_path.write_text(visible_h1_report, encoding="utf-8")
        visible_h1 = run_builder(report_path, brand_path, output)
        assert visible_h1.returncode == 0, visible_h1.stderr
        visible_h1_log = (output / "build-report.txt").read_text(encoding="utf-8")
        assert "U+10000" in visible_h1_log

        bm_match = subprocess.run(
            ("fc-match", "-f", "%{family}\n", "BM Jua"),
            text=True,
            capture_output=True,
            check=True,
        ).stdout.splitlines()[0]
        fallback_family = (
            "BM Jua"
            if "bm jua" in {name.strip().casefold() for name in bm_match.split(",")}
            else "Verdana"
        )
        if fallback_family == "BM Jua":
            role_brand = (
                valid_brand.replace("logo: local.png", "logo: null")
                .replace("sans_font: PingFang SC", "sans_font: BM Jua")
                .replace("serif_font: Songti SC", "serif_font: Verdana")
            )
            role_report = document(
                metadata=(
                    "title: ASCII Report\n"
                    "subtitle: 가\n"
                    "date: 2026-07-22"
                )
            ).replace("正文引用 [S1]", "Body [S1]")
            brand_path.write_text(role_brand, encoding="utf-8")
            report_path.write_text(role_report, encoding="utf-8")
            role_build = run_builder(report_path, brand_path, output)
            assert role_build.returncode == 0, role_build.stderr
            role_log = (output / "build-report.txt").read_text(encoding="utf-8")
            assert "font fallback (sans_font BM Jua)" in role_log
            assert "font fallback (serif_font Verdana)" not in role_log

            code_report = document(
                metadata="title: ASCII Report\ndate: 2026-07-22",
                image=(
                    "\nInline `가`\n\n"
                    "```text\n가\n```\n\n"
                    "    가"
                ),
            ).replace("正文引用 [S1]", "Body [S1]")
            report_path.write_text(code_report, encoding="utf-8")
            code_build = run_builder(report_path, brand_path, output)
            assert code_build.returncode == 0, code_build.stderr
            code_log = (output / "build-report.txt").read_text(encoding="utf-8")
            assert "font fallback (serif_font Verdana)" in code_log
            assert "U+AC00" in code_log

            inline_role_brand = (
                valid_brand.replace("logo: local.png", "logo: null")
                .replace("sans_font: PingFang SC", "sans_font: Verdana")
                .replace("serif_font: Songti SC", "serif_font: BM Jua")
            )
            brand_path.write_text(inline_role_brand, encoding="utf-8")
            heading_code_report = document(
                metadata="title: ASCII Report\ndate: 2026-07-22",
                image="### Inline `‥`",
            ).replace("正文引用 [S1]", "Body [S1]")
            report_path.write_text(heading_code_report, encoding="utf-8")
            heading_code_build = run_builder(report_path, brand_path, output)
            assert heading_code_build.returncode == 0, heading_code_build.stderr
            heading_code_log = (output / "build-report.txt").read_text(encoding="utf-8")
            heading_sans_warning = next(
                line
                for line in heading_code_log.splitlines()
                if "font fallback (sans_font Verdana)" in line
            )
            assert "U+2025" in heading_sans_warning

            body_code_report = document(
                metadata="title: ASCII Report\ndate: 2026-07-22",
                image="Inline `‥`",
            ).replace("正文引用 [S1]", "Body [S1]")
            report_path.write_text(body_code_report, encoding="utf-8")
            body_code_build = run_builder(report_path, brand_path, output)
            assert body_code_build.returncode == 0, body_code_build.stderr
            body_code_log = (output / "build-report.txt").read_text(encoding="utf-8")
            body_sans_warning = next(
                line
                for line in body_code_log.splitlines()
                if "font fallback (sans_font Verdana)" in line
            )
            assert "U+2025" not in body_sans_warning
            assert "font fallback (serif_font BM Jua)" not in body_code_log

        fallback_brand = (
            valid_brand.replace("logo: local.png", "logo: null")
            .replace("sans_font: PingFang SC", f"sans_font: {fallback_family}")
            .replace("serif_font: Songti SC", f"serif_font: {fallback_family}")
        )
        brand_path.write_text(fallback_brand, encoding="utf-8")
        report_path.write_text(document(), encoding="utf-8")
        fallback_build = run_builder(report_path, brand_path, output)
        assert fallback_build.returncode == 0, fallback_build.stderr
        fallback_log = (output / "build-report.txt").read_text(encoding="utf-8")
        assert "font fallback" in fallback_log
        assert fallback_family in fallback_log

        hashes = {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        }
        (root / "bogus.ttf").write_bytes(b"not a font")
        brand_path.write_text(
            valid_brand.replace("sans_font: PingFang SC", "sans_font: bogus.ttf"),
            encoding="utf-8",
        )
        broken_font = run_builder(report_path, brand_path, output)
        assert broken_font.returncode == 2
        assert "invalid font file" in broken_font.stderr
        assert "Traceback" not in broken_font.stderr
        assert {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        } == hashes

        brand_path.write_text(valid_brand, encoding="utf-8")
        (root / "bogus.svg").write_text("<svg>", encoding="utf-8")
        report_path.write_text(
            document(image="\n![损坏矢量图](bogus.svg)"), encoding="utf-8"
        )
        broken_svg = run_builder(report_path, brand_path, output)
        assert broken_svg.returncode == 2
        assert "invalid SVG" in broken_svg.stderr
        assert {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        } == hashes

        (root / "remote.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink">'
            '<image xlink:href="https://example.com/remote.png"/>'
            "</svg>",
            encoding="utf-8",
        )
        report_path.write_text(
            document(image="\n![外链矢量图](remote.svg)"), encoding="utf-8"
        )
        remote_svg = run_builder(report_path, brand_path, output)
        assert remote_svg.returncode == 2
        assert "external SVG" in remote_svg.stderr
        assert {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        } == hashes

        (root / "ftp-css.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg">'
            "<style>.remote { fill: url(ftp://example.com/color.svg#paint); }</style>"
            '<rect class="remote" width="10" height="10"/>'
            "</svg>",
            encoding="utf-8",
        )
        report_path.write_text(
            document(image="\n![FTP 样式](ftp-css.svg)"), encoding="utf-8"
        )
        ftp_css = run_builder(report_path, brand_path, output)
        assert ftp_css.returncode == 2
        assert "external SVG CSS URL" in ftp_css.stderr
        assert {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        } == hashes

        (root / "relative-css.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg">'
            '<rect style="fill: url(../outside.svg#paint)" width="10" height="10"/>'
            "</svg>",
            encoding="utf-8",
        )
        report_path.write_text(
            document(image="\n![相对样式](relative-css.svg)"), encoding="utf-8"
        )
        relative_css = run_builder(report_path, brand_path, output)
        assert relative_css.returncode == 2
        assert "external SVG CSS URL" in relative_css.stderr
        assert {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        } == hashes

        (root / "stylesheet-pi.svg").write_text(
            '<?xml-stylesheet type="text/css" href="https://example.com/report.css"?>'
            '<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>',
            encoding="utf-8",
        )
        report_path.write_text(
            document(image="\n![处理指令](stylesheet-pi.svg)"), encoding="utf-8"
        )
        stylesheet_pi = run_builder(report_path, brand_path, output)
        assert stylesheet_pi.returncode == 2
        assert "xml-stylesheet" in stylesheet_pi.stderr
        assert {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        } == hashes

        report_path.write_text(
            renamed_report.replace("date: 2026-07-22\n", "", 1),
            encoding="utf-8",
        )
        failed = run_builder(report_path, brand_path, output)
        assert failed.returncode == 2
        assert "build failed: report.md: missing required metadata: date" in failed.stderr
        assert {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        } == hashes

        report_path.write_text(renamed_report, encoding="utf-8")
        brand_path.write_text(
            brand_path.read_text(encoding="utf-8").replace("#A06B2C", "copper"),
            encoding="utf-8",
        )
        invalid_brand = run_builder(report_path, brand_path, output)
        assert invalid_brand.returncode == 2
        assert invalid_brand.stderr.startswith(
            "build failed: brand.yml: accent_color"
        )
        assert "Traceback" not in invalid_brand.stderr
        assert {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        } == hashes

        assert "warnings: none" in format_build_log(report_path, 1, [])
        transaction_output = root / "transaction-output"
        transaction_staging = root / "transaction-staging"
        transaction_output.mkdir()
        transaction_staging.mkdir()
        for name in expected_outputs:
            (transaction_output / name).write_bytes(f"old:{name}".encode())
        for name in ("report.pdf", "report.html"):
            (transaction_staging / name).write_bytes(f"new:{name}".encode())
        transaction_hashes = {
            name: hashlib.sha256((transaction_output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        }
        try:
            publish_staged(transaction_staging, transaction_output)
        except BuildError as exc:
            assert "staged output missing: build-report.txt" in str(exc)
        else:
            raise AssertionError("publish_staged accepted an incomplete staged set")
        assert {
            name: hashlib.sha256((transaction_output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        } == transaction_hashes

        replacement_output = root / "replacement-output"
        replacement_staging = root / "replacement-staging"
        replacement_output.mkdir()
        replacement_staging.mkdir()
        for name in expected_outputs:
            (replacement_output / name).write_bytes(f"old:{name}".encode())
            (replacement_staging / name).write_bytes(f"new:{name}".encode())
        unknown = replacement_output / "unknown.txt"
        unknown.write_bytes(b"keep me")
        replacement_hashes = {
            name: hashlib.sha256((replacement_output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        }
        real_replace = os.replace

        def fail_third_publish(source: object, target: object) -> None:
            source_path = Path(source)
            target_path = Path(target)
            if (
                source_path.parent == replacement_staging
                and target_path.parent == replacement_output
                and source_path.name == "build-report.txt"
            ):
                raise OSError("controlled third publish failure")
            real_replace(source, target)

        with patch("build_report.os.replace", side_effect=fail_third_publish):
            try:
                publish_staged(replacement_staging, replacement_output)
            except BuildError as exc:
                assert "cannot publish report outputs" in str(exc)
                assert "controlled third publish failure" in str(exc)
            else:
                raise AssertionError("publish_staged accepted a partial publish failure")
        assert {
            name: hashlib.sha256((replacement_output / name).read_bytes()).hexdigest()
            for name in expected_outputs
        } == replacement_hashes
        assert unknown.read_bytes() == b"keep me"

    print("PASS: fixed research report validation and rendering")


if __name__ == "__main__":
    main()

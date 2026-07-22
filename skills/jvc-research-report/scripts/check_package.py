from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from build_report import (
    BuildError,
    build_log as format_build_log,
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

        from PIL import Image

        Image.new("RGB", (32, 16), "#A06B2C").save(root / "local.png")
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
        brand_path.write_text(valid_brand, encoding="utf-8")
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

    print("PASS: fixed research report validation and rendering")


if __name__ == "__main__":
    main()

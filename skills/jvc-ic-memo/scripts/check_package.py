#!/usr/bin/env python3
import subprocess
import sys
import tempfile
from pathlib import Path


VALIDATOR = Path(__file__).with_name("validate_final.py")
REVIEW = """# IC Memo 预审版

研究状态：ready
来源：[S1] 项目资料

## 正文

公司计划于 2026 年实现收入 420 万元，并建成 18 条产线。

## 质量报告

数字口径已复核。
"""
CLEAN = """# IC Memo

## 1. 执行摘要

公司计划于 2026年实现收入 420万元，并建成 18条产线。
收入来源于订阅服务。
收入来源：订阅服务。
系统已达到 production-ready 条件。
市场缺口为产品提供了切入空间。
建议投入研发以提升产品性能。
建议通过技术评审后发布。

| 指标 | 数值 |
| --- | --- |
| 收入 | 420万元 |

指标 | 数值
--- | ---
产线 | 18条
"""


def run(review: Path, final: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--review", str(review), "--final", str(final)],
        text=True,
        capture_output=True,
        check=False,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_failure(result: subprocess.CompletedProcess[str], name: str, diagnostic: str) -> None:
    require(result.returncode == 1, f"{name}: expected exit 1, got {result.returncode}: {result.stderr}")
    require("validation failed:" in result.stderr, f"{name}: missing failure message: {result.stderr}")
    require(diagnostic in result.stderr, f"{name}: expected {diagnostic!r}: {result.stderr}")


def main() -> int:
    require(VALIDATOR.is_file(), f"missing validator: {VALIDATOR}")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        review = root / "review.md"
        clean = root / "clean.md"
        review.write_text(REVIEW, encoding="utf-8")
        clean.write_text(CLEAN, encoding="utf-8")

        result = run(review, clean)
        require(result.returncode == 0, f"valid: {result.stderr}")
        require("IC memo final validation passed" in result.stdout, f"valid: {result.stdout}")

        bad_cases = {
            "source-id": (CLEAN + "\n[S1]\n", "source id"),
            "source-note": (CLEAN + "\n资料来源：访谈\n", "source"),
            "source-origin": (CLEAN + "\n来源于内部访谈\n", "source"),
            "source-prefix": (CLEAN + "\n> - 数据来源：访谈\n", "source"),
            "source-parentheses": (CLEAN + "\n交易数据（来源：访谈）。\n", "source"),
            "source-heading": (CLEAN + "\n## 来源\n\n项目访谈。\n", "source"),
            "data-source-heading": (CLEAN + "\n## 数据来源\n\n项目访谈。\n", "source"),
            "source-explanation-heading": (CLEAN + "\n## 来源说明\n\n项目访谈。\n", "source"),
            "source-explanation-inline": (CLEAN + "\n来源说明：项目访谈。\n", "source"),
            "data-source-origin": (CLEAN + "\n数据来源于访谈。\n", "source"),
            "material-source-origin": (CLEAN + "\n资料来源于访谈。\n", "source"),
            "page-reference": (CLEAN + "\ndeck p.5\n", "page reference"),
            "standalone-page-p": (CLEAN + "\np.12\n", "page reference"),
            "standalone-page-pp": (CLEAN + "\npp. 12\n", "page reference"),
            "chinese-page-reference": (CLEAN + "\n详见第三页。\n", "page reference"),
            "url": (CLEAN + "\nhttps://example.com/report\n", "web link"),
            "ftp-url": (CLEAN + "\nftp://example.com/report\n", "web link"),
            "status": (CLEAN + "\n研究状态：partial\n", "research status"),
            "status-prefix": (CLEAN + "\n> - 研究状态：blocked\n", "research status"),
            "status-approved": (CLEAN + "\n研究状态：已批准\n", "research status"),
            "status-inline": (CLEAN + "\n本研究状态为 partial。\n", "research status"),
            "review-label-third-party": (CLEAN + "\n[第三方事实]\n", "review-only evidence label"),
            "review-label-company": (CLEAN + "\n[公司口径]\n", "review-only evidence label"),
            "observation-label": (CLEAN + "\n[用户观察]\n", "internal bracketed label"),
            "interview-label": (CLEAN + "\n[内部访谈]\n", "source/evidence label"),
            "model-estimate-label": (CLEAN + "\n[模型估算]\n", "internal bracketed label"),
            "agent-inference-label": (CLEAN + "\n[代理推断]\n", "internal bracketed label"),
            "unknown-label": (CLEAN + "\n[未知]\n", "internal bracketed label"),
            "numeric-footnote": (CLEAN + "\n客户留存率稳定。[1]\n", "numeric footnote"),
            "decision-invest": (CLEAN + "\n建议投资。\n", "decision language"),
            "decision-pass": (CLEAN + "\n不建议投资。\n", "decision language"),
            "decision-conditional": (CLEAN + "\n有条件投资。\n", "decision language"),
            "decision-short-invest": (CLEAN + "\n建议投。\n", "decision language"),
            "decision-short-pass": (CLEAN + "\n不投。\n", "decision language"),
            "decision-short-conditional": (CLEAN + "\n有条件投。\n", "decision language"),
            "decision-recommend": (CLEAN + "\n推荐投资。\n", "decision language"),
            "decision-approve-round": (CLEAN + "\n建议通过本轮投资。\n", "decision language"),
            "evidence-gap": (CLEAN + "\n> - 证据缺口：客户复购。\n", "internal gap/placeholder"),
            "information-gap": (CLEAN + "\n信息缺口：供应链。\n", "internal gap/placeholder"),
            "evidence-gap-inline": (CLEAN + "\n当前判断仍存在证据缺口。\n", "internal gap/placeholder"),
            "information-gap-inline": (CLEAN + "\n该结论暴露出信息缺口。\n", "internal gap/placeholder"),
            "internal-operation-inline": (CLEAN + "\n正文后附内部操作说明。\n", "internal operation instruction"),
            "pending-supplement": (CLEAN + "\n待补充客户数据。\n", "internal gap/placeholder"),
            "needs-supplement": (CLEAN + "\n需补充客户数据。\n", "internal gap/placeholder"),
            "not-covered": (CLEAN + "\n未覆盖海外市场。\n", "internal gap/placeholder"),
            "missing-evidence": (CLEAN + "\n缺少证据支持。\n", "internal gap/placeholder"),
            "user-input-needed": (CLEAN + "\n需要用户提供财务数据。\n", "internal gap/placeholder"),
            "missing-input-material": (CLEAN + "\n此部分缺少输入素材。\n", "internal gap/placeholder"),
            "evidence-status-company": (CLEAN + "\n证据状态：[公司口径]\n", "evidence status"),
            "evidence-status-third-party": (CLEAN + "\n证据状态：[第三方事实]\n", "evidence status"),
            "evidence-status-other": (CLEAN + "\n> - 证据状态：已复核\n", "evidence status"),
            "internal-section": (CLEAN + "\n## 待用户裁定事项\n\n无。\n", "internal section"),
            "placeholder": (CLEAN + "\nTODO：补充材料\n", "placeholder"),
            "new-number": (CLEAN + "\n预计新增 19 条产线。\n", "number absent"),
            "letter-prefixed-new-number": (CLEAN + "\n新产品代号 X19。\n", "number absent"),
            "empty-section": (CLEAN + "\n## 2. 投资亮点\n\n---\n\n### 子标题\n", "empty level-two section"),
            "empty-section-containers": (CLEAN + "\n## 2. 投资亮点\n\n>\n> -\n*\n1.\n", "empty level-two section"),
            "empty-section-comment": (CLEAN + "\n## 2. 投资亮点\n\n<!-- 内部注释 -->\n", "empty level-two section"),
            "empty-section-multiline-comment": (CLEAN + "\n## 2. 投资亮点\n\n<!--\n内部注释\n-->\n", "empty level-two section"),
            "unnumbered-section": (CLEAN.replace("## 1. 执行摘要", "## 执行摘要"), "section numbering"),
            "duplicate-section": (CLEAN + "\n## 1. 执行摘要\n\n正文。\n", "section numbering"),
            "descending-section": (CLEAN.replace("## 1. 执行摘要", "## 2. 投资亮点") + "\n## 1. 执行摘要\n\n正文。\n", "section numbering"),
            "out-of-range-section": (CLEAN.replace("## 1. 执行摘要", "## 18. 执行摘要"), "section numbering"),
            "wrong-section-title": (CLEAN.replace("## 1. 执行摘要", "## 1. 公司摘要"), "section mapping"),
            "empty-table-section": (
                CLEAN + "\n## 2. 投资亮点\n\n| 指标 | 数值 |\n| --- | --- |\n| | |\n",
                "empty level-two section",
            ),
            "source-id-combination": (CLEAN + "\n[S1, S2]\n", "source id"),
            "source-id-placeholder": (CLEAN + "\n[S编号]\n", "source id"),
            "internal-bracket-label": (CLEAN + "\n[待验证]\n", "internal bracketed label"),
            "checkbox": (CLEAN + "\n- [ ] 内部检查\n", "checkbox/template placeholder"),
            "template-placeholder": (CLEAN + "\n[公司名称]\n", "checkbox/template placeholder"),
            "malformed-table": (CLEAN + "\n| 指标 | 数值 |\n| 产线 | 18条 |\n", "malformed Markdown table"),
            "single-table-header": (CLEAN + "\n| 指标 | 数值 |\n", "malformed Markdown table"),
            "single-table-separator": (CLEAN + "\n| --- | --- |\n", "malformed Markdown table"),
            "malformed-table-columns": (CLEAN + "\n| 指标 | 数值 |\n| --- | --- |\n| 产线 | 18条 | 无 |\n", "malformed Markdown table"),
            "plain-table-columns": (CLEAN + "\n指标 | 数值\n--- | ---\n产线 | 18条 | 无\n", "malformed Markdown table"),
            "unclosed-fence": (CLEAN + "\n```text\n未闭合\n", "unclosed fenced code block"),
            "unclosed-blockquote-fence": (CLEAN + "\n> ```text\n> 未闭合\n", "unclosed fenced code block"),
            "top-fence-quoted-close": (CLEAN + "\n```text\n内容\n> ```\n", "unclosed fenced code block"),
            "quoted-fence-top-close": (CLEAN + "\n> ```text\n> 内容\n```\n", "unclosed fenced code block"),
            "blockquote-table-missing-separator": (CLEAN + "\n> | 指标 | 数值 |\n> | 产线 | 18条 |\n", "malformed Markdown table"),
            "blockquote-table-columns": (CLEAN + "\n> | 指标 | 数值 |\n> | --- | --- |\n> | 产线 | 18条 | 无 |\n", "malformed Markdown table"),
        }
        bad = root / "bad.md"
        for name, (content, diagnostic) in bad_cases.items():
            bad.write_text(content, encoding="utf-8")
            require_failure(run(review, bad), name, diagnostic)

        for label in (
            "来源",
            "未核实",
            "待验证",
            "需要用户提供",
            "推测",
            "公司自述",
            "质量报告",
            "新闻",
            "deck",
            "证据缺口",
            "待确认",
            "待补充",
            "需补充",
            "未覆盖",
        ):
            bad.write_text(CLEAN + f"\n[{label}]\n", encoding="utf-8")
            require_failure(run(review, bad), f"bracket-label-{label}", "internal bracketed label")

        bracket_review = root / "bracket-review.md"
        bracket_final = root / "bracket-final.md"
        bracket_review.write_text(REVIEW + "\n敏感区间为 [5%, 10%]。\n", encoding="utf-8")
        bracket_final.write_text(CLEAN + "\n敏感区间为 [5%, 10%]。\n", encoding="utf-8")
        result = run(bracket_review, bracket_final)
        require(result.returncode == 0, f"legal-bracket-range: {result.stderr}")

        numbering_review = root / "numbering-review.md"
        numbering_final = root / "numbering-final.md"
        numbering_review.write_text(REVIEW + "\n章节编号包含 1、3、17。\n", encoding="utf-8")
        numbering_final.write_text(
            CLEAN + "\n## 3. 投资风险\n\n正文。\n\n## 17. 交易-收益测算总结\n\n正文。\n",
            encoding="utf-8",
        )
        result = run(numbering_review, numbering_final)
        require(result.returncode == 0, f"numbering-subsequence: {result.stderr}")

        decimal_review = root / "decimal-review.md"
        decimal_final = root / "decimal-final.md"
        decimal_review.write_text(REVIEW + "\n基准回报率为 5%。\n", encoding="utf-8")
        decimal_final.write_text(CLEAN + "\n实际回报率为 .5%。\n", encoding="utf-8")
        require_failure(run(decimal_review, decimal_final), "leading-point-decimal", "number absent")

        unit_review = root / "unit-review.md"
        unit_final = root / "unit-final.md"
        unit_review.write_text(REVIEW + "\n成本为 5元。\n", encoding="utf-8")
        unit_final.write_text(CLEAN + "\n回报率为 5%。\n", encoding="utf-8")
        require_failure(run(unit_review, unit_final), "number-unit-change", "number absent")

        currency_review = root / "currency-review.md"
        currency_final = root / "currency-final.md"
        currency_review.write_text(REVIEW + "\n成本为 USD 5。\n", encoding="utf-8")
        currency_final.write_text(CLEAN + "\n成本为 RMB 5。\n", encoding="utf-8")
        require_failure(run(currency_review, currency_final), "currency-prefix-change", "number absent")

        currency_final.write_text(CLEAN + "\n成本为 5 USD。\n", encoding="utf-8")
        result = run(currency_review, currency_final)
        require(result.returncode == 0, f"currency-position: {result.stderr}")

        percent_review = root / "percent-review.md"
        percent_final = root / "percent-final.md"
        percent_review.write_text(REVIEW + "\n回报率为 5%。\n", encoding="utf-8")
        percent_final.write_text(CLEAN + "\n回报率为 5％。\n", encoding="utf-8")
        result = run(percent_review, percent_final)
        require(result.returncode == 0, f"percent-alias: {result.stderr}")

        multiple_review = root / "multiple-review.md"
        multiple_final = root / "multiple-final.md"
        multiple_review.write_text(REVIEW + "\n市销率为 17倍。\n", encoding="utf-8")
        for name, multiple in (("ascii-multiple-alias", "17x"), ("unicode-multiple-alias", "17×")):
            multiple_final.write_text(CLEAN + f"\n市销率为 {multiple}。\n", encoding="utf-8")
            result = run(multiple_review, multiple_final)
            require(result.returncode == 0, f"{name}: {result.stderr}")

        chinese_quantity_final = root / "chinese-quantity-final.md"
        chinese_quantity_final.write_text(CLEAN + "\n预计新增三千万元收入。\n", encoding="utf-8")
        require_failure(run(review, chinese_quantity_final), "chinese-quantity", "number absent")

        code_number_final = root / "code-number-final.md"
        code_number_final.write_text(CLEAN + "\n```text\n预计新增 77 条产线。\n```\n", encoding="utf-8")
        require_failure(run(review, code_number_final), "code-block-number", "number absent")

        heading_business_number_final = root / "heading-business-number-final.md"
        heading_business_number_final.write_text(
            CLEAN + "\n### 预计新增 999 万元收入\n",
            encoding="utf-8",
        )
        require_failure(run(review, heading_business_number_final), "heading-business-number", "number absent")

        review_heading_number = root / "review-heading-number.md"
        review_heading_number.write_text(REVIEW + "\n# 预计收入 88 万元\n", encoding="utf-8")
        bad.write_text(CLEAN + "\n预计收入 88 万元。\n", encoding="utf-8")
        result = run(review_heading_number, bad)
        require(result.returncode == 0, f"review-heading-number: {result.stderr}")

        metadata_number_review = root / "metadata-number-review.md"
        metadata_number_review.write_text(REVIEW + "\n[模型估算 777 万元]\n", encoding="utf-8")
        bad.write_text(CLEAN + "\n预计收入 777 万元。\n", encoding="utf-8")
        require_failure(run(metadata_number_review, bad), "metadata-number", "number absent")

        heading_number_review = root / "heading-number-review.md"
        heading_number_review.write_text(
            REVIEW + "\n## 17. 交易-收益测算总结\n\n正文。\n",
            encoding="utf-8",
        )
        multiple_final.write_text(CLEAN + "\n市销率为17x。\n", encoding="utf-8")
        require_failure(run(heading_number_review, multiple_final), "heading-number", "number absent")

        appendix_number_review = root / "appendix-number-review.md"
        appendix_number_review.write_text(
            REVIEW + "\n## 附录：质量报告\n\n质量表记录 99 条。\n",
            encoding="utf-8",
        )
        bad.write_text(CLEAN + "\n预计新增 99 条产线。\n", encoding="utf-8")
        require_failure(run(appendix_number_review, bad), "appendix-number", "number absent")

        page_review = root / "page-review.md"
        page_review.write_text(REVIEW + "\n方案包含编号 3 和 5。\n", encoding="utf-8")
        for name, reference in (
            ("arabic-page-range", "第3-5页"),
            ("chinese-page-range", "第三至五页"),
        ):
            bad.write_text(CLEAN + f"\n详见{reference}。\n", encoding="utf-8")
            require_failure(run(page_review, bad), name, "page reference")

        for name, reference in (
            ("page-p-compact", "deck p3"),
            ("page-p-spaced", "deck p 3"),
            ("page-p", "deck p.3"),
            ("page-pp-range", "report pp.3-5"),
            ("page-word", "PDF page 3"),
            ("pages-word-range", "deck pages 3-5"),
        ):
            bad.write_text(CLEAN + f"\n{reference}\n", encoding="utf-8")
            require_failure(run(page_review, bad), name, "page reference")

        missing = root / "missing.md"
        require_failure(run(missing, clean), "missing-review", "cannot read review")
        require_failure(run(review, missing), "missing-final", "cannot read final")

        empty = root / "empty.md"
        empty.write_text(" \n", encoding="utf-8")
        require_failure(run(review, empty), "empty-final", "final is empty")

        invalid = root / "invalid.md"
        invalid.write_bytes(b"\xff")
        require_failure(run(review, invalid), "invalid-encoding", "cannot read final")

        published = root / "published.md"
        bad_candidate = root / "bad-candidate.md"
        published.write_text(CLEAN, encoding="utf-8")
        bad_candidate.write_text(bad_cases["new-number"][0], encoding="utf-8")
        review_before = review.read_bytes()
        candidate_before = bad_candidate.read_bytes()
        published_before = published.read_bytes()
        require_failure(run(review, bad_candidate), "readonly", "number absent")
        require(review.read_bytes() == review_before, "validator modified review.md")
        require(bad_candidate.read_bytes() == candidate_before, "validator modified bad-candidate.md")
        require(published.read_bytes() == published_before, "validator modified published.md")

    print("jvc-ic-memo package check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

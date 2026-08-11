#!/usr/bin/env python3
import subprocess
import sys
import tempfile
from pathlib import Path


VALIDATOR = Path(__file__).with_name("validate_output.py")
SECTIONS = (
    "快筛结论",
    "商业模式",
    "上下游与价值分配",
    "赛道有效性",
    "市场规模粗算",
    "五年收入情景",
    "交易与回报粗算",
    "风险、证伪条件与下一步",
    "来源、假设与未知项",
)


def document(body: dict[str, str] | None = None, omit: set[str] | None = None) -> str:
    content = {
        "快筛结论": "研究资源判断：继续研究。这是研究资源判断，不替用户作投资决定。",
        "商业模式": "商业模式要素：完整。客户：工厂；付费者：工厂采购部门；产品：质检软件；收入与交付：订阅并部署。",
        "上下游与价值分配": "上游算力；中游软件；下游工厂。价值分配、议价权与卡点待核验。",
        "赛道有效性": "【第三方事实】客户仍采购质检服务；【公司自述】已有付费合同；【用户观察】部署依赖工程师。",
        "市场规模粗算": "市场锚点：存在。\n\n【第三方事实】上位市场为十二亿元。\n\n【模型估算】情景：低；公式：上位市场 × 可服务比例；单位：亿元/年；依据：【第三方事实】上位市场与【用户观察】比例；置信度：低；结果：约 8 亿元。\n\n【模型估算】情景：中；公式：上位市场 × 可服务比例；单位：亿元/年；依据：【第三方事实】上位市场与【用户观察】比例；置信度：低；结果：约 10 亿元。\n\n【模型估算】情景：高；公式：上位市场 × 可服务比例；单位：亿元/年；依据：【第三方事实】上位市场与【用户观察】比例；置信度：低；结果：约 12 亿元。",
        "五年收入情景": "唯一驱动路径：客户数 × 单客收入。\n\n【模型估算】情景：低；公式：50 家 × 20 万元/家/年；单位：万元/年；依据：【公司自述】单客收入与【用户观察】客户情景；置信度：低；结果：约 1000 万元。\n\n【模型估算】情景：中；公式：100 家 × 20 万元/家/年；单位：万元/年；依据：【公司自述】单客收入与【用户观察】客户情景；置信度：低；结果：约 2000 万元。\n\n【模型估算】情景：高；公式：150 家 × 20 万元/家/年；单位：万元/年；依据：【公司自述】单客收入与【用户观察】客户情景；置信度：低；结果：约 3000 万元。",
        "交易与回报粗算": "交易条款：完整。\n\nMultiple on Invested Capital（MOIC，投入资本倍数，指退出回款除以投入资本）；Internal Rate of Return（IRR，内部收益率，指使投资现金流净现值为零的年化收益率）。\n\n【模型估算】公式：退出回款 ÷ 投资额；单位：倍；依据：【公司自述】投后估值 2 亿元与【用户观察】投资额 2000 万元；置信度：低；结果：MOIC 约 2–4 倍，IRR 约 15%–32%。",
        "风险、证伪条件与下一步": "前三风险：需求、交付、竞争。反证：复购不足。下一步：核验合同。",
        "来源、假设与未知项": "【未知/待验证】续费率。标签口径：第三方、公司、用户、模型和未知项分开。",
    }
    if body:
        content.update(body)
    omitted = omit or set()
    return "# Pre-Screen\n\nResearch Level 0（L0，研究级别 0，约 30–60 分钟的资源筛选）\n\n" + "\n\n".join(
        f"## {section}\n\n{content[section]}" for section in SECTIONS if section not in omitted
    ) + "\n"


def run(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_failure(result: subprocess.CompletedProcess[str], name: str, diagnostic: str) -> None:
    require(result.returncode == 1, f"{name}: expected exit 1, got {result.returncode}: {result.stderr}")
    require("validation failed:" in result.stderr, f"{name}: missing failure prefix: {result.stderr}")
    require(diagnostic in result.stderr, f"{name}: expected {diagnostic!r}: {result.stderr}")


def main() -> int:
    require(VALIDATOR.is_file(), f"missing validator: {VALIDATOR}")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        artifact = root / "01-prescreen.md"
        artifact.write_text(document(), encoding="utf-8")
        result = run(artifact)
        require(result.returncode == 0, f"valid: {result.stderr}")
        require("prescreen validation passed" in result.stdout, f"valid: {result.stdout}")

        cases = {
            "market-without-anchor": (
                {
                    "市场规模粗算": "【未知/待验证】市场锚点：缺失；处理：仅列公式，不输出市场数字。\n\n【模型估算】公式：上位市场 × 可服务比例；单位：亿元/年；依据：无市场锚点；置信度：低；结果：约 12 亿元。"
                },
                "quantitative market output without anchor",
            ),
            "return-without-terms": (
                {
                    "交易与回报粗算": "Multiple on Invested Capital（MOIC，投入资本倍数，指退出回款除以投入资本）；Internal Rate of Return（IRR，内部收益率，指使投资现金流净现值为零的年化收益率）。\n\n【未知/待验证】交易条款：缺少估值或投资额；处理：条件式敏感性框架。\n\nMOIC：3 倍；IRR：25%。"
                },
                "quantitative return without terms",
            ),
            "incompatible-units-propagated": (
                {
                    "市场规模粗算": "市场锚点：存在。\n\n【未知/待验证】单位勾稽：不兼容；下游传播：继续。\n\n【模型估算】公式：数量 × 价格；单位：亿元/年；依据：【第三方事实】数量以吨计、价格以元/件计；置信度：低；结果：约 10 亿元。"
                },
                "incompatible unit propagation",
            ),
            "missing-model-audit-field": (
                {
                    "五年收入情景": "【模型估算】情景：低/中/高；公式：客户数 × 单客收入；单位：万元/年；结果：约 1000/2000/3000 万元。"
                },
                "model estimate missing 依据",
            ),
            "estimate-without-confidence": (
                {
                    "市场规模粗算": "市场锚点：存在。\n\n【模型估算】情景：低/中/高；公式：上位市场 × 可服务比例；单位：亿元/年；依据：【第三方事实】上位市场与【用户观察】比例；结果：约 8/10/12 亿元。"
                },
                "model estimate missing 置信度",
            ),
            "unsupported-precision": (
                {
                    "市场规模粗算": "市场锚点：存在。\n\n【模型估算】情景：基准；公式：上位市场 × 可服务比例；单位：亿元/年；依据：【第三方事实】上位市场与【用户观察】比例；置信度：低；结果：12.347 亿元。"
                },
                "unsupported decimal precision",
            ),
            "market-anchor-percentage-bypass": (
                {
                    "市场规模粗算": "【未知/待验证】市场锚点：缺失；处理：仅列公式，不输出市场数字。\n\n渗透率结果：12%。"
                },
                "quantitative market output without anchor",
            ),
            "market-anchor-quantitative-bypass": (
                {
                    "市场规模粗算": "市场锚点：缺失；处理：仅列公式，不输出市场数字。\n\n目标客户约占 12%，约 300 家。"
                },
                "quantitative market output without anchor",
            ),
            "return-range-without-terms": (
                {
                    "交易与回报粗算": "Multiple on Invested Capital（MOIC，投入资本倍数，指退出回款除以投入资本）；Internal Rate of Return（IRR，内部收益率，指使投资现金流净现值为零的年化收益率）。\n\n【未知/待验证】交易条款：缺少估值或投资额；处理：条件式敏感性框架。\n\n结果：2–4 倍、15%–32%。"
                },
                "quantitative return without terms",
            ),
            "business-stop-unlabeled-results": (
                {
                    "商业模式": "【未知/待验证】商业模式要素：缺失（客户）；收入测算：阻断；回报测算：阻断。",
                    "五年收入情景": "收入结果：1000 万元。",
                    "交易与回报粗算": "交易条款：完整。\n\n回报结果：2 倍。",
                },
                "quantitative output after business-model stop",
            ),
            "business-stop-quantitative-bypass": (
                {
                    "商业模式": "商业模式要素：缺失（客户）；收入测算：阻断；回报测算：阻断。",
                    "五年收入情景": "收入约 1 亿元。",
                    "交易与回报粗算": "交易条款：完整。\n\nMOIC 约 3 倍。",
                },
                "quantitative output after business-model stop",
            ),
            "unit-stop-downstream-result": (
                {
                    "上下游与价值分配": "【未知/待验证】单位勾稽：不兼容；下游传播：停止；影响章节：市场规模粗算。",
                },
                "model result after incompatible unit stop",
            ),
            "single-market-scenario": (
                {
                    "市场规模粗算": "市场锚点：存在。\n\n【模型估算】情景：中；公式：上位市场 × 可服务比例；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：约 10 亿元。"
                },
                "market scenarios must be low/mid/high",
            ),
            "multiple-revenue-paths": (
                {
                    "五年收入情景": "唯一驱动路径：客户数 × 单客收入。\n\n唯一驱动路径：产能 × 售价。\n\n【模型估算】情景：低；公式：50 家 × 20 万元/家/年；单位：万元/年；依据：【公司自述】单客收入；置信度：低；结果：约 1000 万元。\n\n【模型估算】情景：中；公式：100 家 × 20 万元/家/年；单位：万元/年；依据：【公司自述】单客收入；置信度：低；结果：约 2000 万元。\n\n【模型估算】情景：高；公式：150 家 × 20 万元/家/年；单位：万元/年；依据：【公司自述】单客收入；置信度：低；结果：约 3000 万元。"
                },
                "exactly one revenue driver path",
            ),
            "combined-revenue-path": (
                {
                    "五年收入情景": "唯一驱动路径：客户数 × 单客收入与产能 × 售价。\n\n【模型估算】情景：低；公式：50 家 × 20 万元/家/年；单位：万元/年；依据：【公司自述】单客收入；置信度：低；结果：约 1000 万元。\n\n【模型估算】情景：中；公式：100 家 × 20 万元/家/年；单位：万元/年；依据：【公司自述】单客收入；置信度：低；结果：约 2000 万元。\n\n【模型估算】情景：高；公式：150 家 × 20 万元/家/年；单位：万元/年；依据：【公司自述】单客收入；置信度：低；结果：约 3000 万元。"
                },
                "invalid revenue driver path",
            ),
            "unlabeled-numeric-model-result": (
                {
                    "市场规模粗算": "市场锚点：存在。\n\n情景：低；公式：上位市场 × 比例；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：8 亿元。\n\n【模型估算】情景：中；公式：上位市场 × 比例；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：10 亿元。\n\n【模型估算】情景：高；公式：上位市场 × 比例；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：12 亿元。"
                },
                "quantitative model output missing model label",
            ),
            "invalid-resource-conclusion": (
                {"快筛结论": "推荐投资。这个结论不替用户作投资决定。"},
                "invalid research-resource conclusion",
            ),
            "missing-decision-boundary": (
                {"快筛结论": "研究资源判断：继续研究。"},
                "missing no-investment-decision boundary",
            ),
            "final-investment-language": (
                {"快筛结论": "研究资源判断：继续研究。这个项目值得投资。不替用户作投资决定。"},
                "final investment decision",
            ),
            "complete-terms-unlabeled-return": (
                {
                    "交易与回报粗算": "交易条款：完整。\n\nMultiple on Invested Capital（MOIC，投入资本倍数，指退出回款除以投入资本）；Internal Rate of Return（IRR，内部收益率，指使投资现金流净现值为零的年化收益率）。\n\nMOIC 约 3 倍，IRR 约 25%。"
                },
                "quantitative model output missing model label",
            ),
            "model-return-missing-result-field": (
                {
                    "交易与回报粗算": "交易条款：完整。\n\nMultiple on Invested Capital（MOIC，投入资本倍数，指退出回款除以投入资本）；Internal Rate of Return（IRR，内部收益率，指使投资现金流净现值为零的年化收益率）。\n\n【模型估算】MOIC 约 2.347 倍，IRR 约 17.234%；公式：退出回款 ÷ 投资额；单位：倍、%/年；依据：【公司自述】交易条款；置信度：低。"
                },
                "quantitative model output missing 结果",
            ),
            "market-chinese-number-bypass": (
                {
                    "市场规模粗算": "市场锚点：缺失；处理：仅列公式，不输出市场数字。\n\n市场规模约十二亿元。"
                },
                "quantitative market output without anchor",
            ),
            "business-chinese-and-shorthand-bypass": (
                {
                    "商业模式": "商业模式要素：缺失（客户）；收入测算：阻断；回报测算：阻断。",
                    "五年收入情景": "收入约 1000万。",
                    "交易与回报粗算": "交易条款：完整。\n\nMOIC：三倍；IRR：百分之二十五。",
                },
                "quantitative output after business-model stop",
            ),
            "bare-moic-equals": (
                {
                    "交易与回报粗算": "交易条款：完整。\n\nMultiple on Invested Capital（MOIC，投入资本倍数，指退出回款除以投入资本）；Internal Rate of Return（IRR，内部收益率，指使投资现金流净现值为零的年化收益率）。\n\nMOIC=2.5。"
                },
                "quantitative model output missing model label",
            ),
            "empty-model-audit-value": (
                {
                    "市场规模粗算": "市场锚点：存在。\n\n【模型估算】情景：低；公式：上位市场 × 比例；单位：亿元/年；依据：；置信度：低；结果：8 亿元。\n\n【模型估算】情景：中；公式：上位市场 × 比例；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：10 亿元。\n\n【模型估算】情景：高；公式：上位市场 × 比例；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：12 亿元。"
                },
                "model estimate empty 依据",
            ),
            "complete-terms-without-return-model": (
                {
                    "交易与回报粗算": "交易条款：完整。\n\nMultiple on Invested Capital（MOIC，投入资本倍数，指退出回款除以投入资本）；Internal Rate of Return（IRR，内部收益率，指使投资现金流净现值为零的年化收益率）。"
                },
                "complete terms require audited return model",
            ),
            "unstructured-resource-conclusion": (
                {"快筛结论": "现在不能判断是否继续研究。本判断不替用户作投资决定。"},
                "invalid research-resource conclusion",
            ),
            "market-chinese-quantity-bypass": (
                {
                    "市场规模粗算": "市场锚点：缺失；处理：仅列公式，不输出市场数字。\n\n目标客户约三百家。"
                },
                "quantitative market output without anchor",
            ),
            "market-chinese-usd-bypass": (
                {
                    "市场规模粗算": "市场锚点：缺失；处理：仅列公式，不输出市场数字。\n\n市场规模约十二亿美元。"
                },
                "quantitative market output without anchor",
            ),
            "whitespace-model-audit-value": (
                {
                    "市场规模粗算": "市场锚点：存在。\n\n【模型估算】情景：低；公式：上位市场 × 比例；单位：亿元/年；依据：   ；置信度：低；结果：8 亿元。\n\n【模型估算】情景：中；公式：上位市场 × 比例；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：10 亿元。\n\n【模型估算】情景：高；公式：上位市场 × 比例；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：12 亿元。"
                },
                "model estimate empty 依据",
            ),
            "market-scenarios-pending-results": (
                {
                    "市场规模粗算": "市场锚点：存在。\n\n【模型估算】情景：低；公式：80 亿元 × 8%；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：待计算。\n\n【模型估算】情景：中；公式：100 亿元 × 10%；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：待计算。\n\n【模型估算】情景：高；公式：120 亿元 × 12%；单位：亿元/年；依据：【第三方事实】上位市场；置信度：低；结果：待计算。"
                },
                "model estimate result is not quantitative",
            ),
            "return-pending-result": (
                {
                    "交易与回报粗算": "交易条款：完整。\n\n【模型估算】MOIC、IRR 待计算；公式：退出回款 5000 万元 ÷ 投资额 2000 万元；单位：倍、%/年；依据：【公司自述】交易条款；置信度：低；结果：待计算。"
                },
                "model estimate result is not quantitative",
            ),
            "ambiguous-resource-conclusion-suffix": (
                {"快筛结论": "研究资源判断：继续研究或等待关键材料。本判断不替用户作投资决定。"},
                "invalid research-resource conclusion",
            ),
        }
        for name, (replacement, diagnostic) in cases.items():
            artifact.write_text(document(replacement), encoding="utf-8")
            require_failure(run(artifact), name, diagnostic)

        for missing_element in ("客户", "付费者", "产品"):
            artifact.write_text(
                document({"商业模式": f"{missing_element}：未识别；其余商业模式字段待核验。"}),
                encoding="utf-8",
            )
            require_failure(run(artifact), f"missing-business-status-{missing_element}", "invalid business-model status")

        for conclusion in ("继续研究", "等待关键材料", "暂不继续"):
            artifact.write_text(
                document({"快筛结论": f"研究资源判断：{conclusion}。本判断不替用户作投资决定。"}),
                encoding="utf-8",
            )
            result = run(artifact)
            require(result.returncode == 0, f"valid-conclusion-{conclusion}: {result.stderr}")

        blocked_cases = {
            "market": (
                "市场规模粗算",
                {"市场规模粗算": "市场锚点：存在。\n\n【未知/待验证】受单位口径阻断，不输出市场模型。"},
            ),
            "revenue": (
                "五年收入情景",
                {"五年收入情景": "【未知/待验证】受单位口径阻断，不输出收入模型。"},
            ),
            "return": (
                "交易与回报粗算",
                {"交易与回报粗算": "交易条款：完整。\n\n【未知/待验证】受单位口径阻断，不输出回报模型。"},
            ),
        }
        for name, (section, replacement) in blocked_cases.items():
            replacement["上下游与价值分配"] = f"【未知/待验证】单位勾稽：不兼容；下游传播：停止；影响章节：{section}。"
            artifact.write_text(document(replacement), encoding="utf-8")
            result = run(artifact)
            require(result.returncode == 0, f"blocked-section-{name}: {result.stderr}")

        artifact.write_text(
            document(
                {
                    "上下游与价值分配": "【未知/待验证】单位勾稽：不兼容；下游传播：停止；影响章节：市场规模粗算。",
                    "市场规模粗算": "市场锚点：存在。\n\n单位：亿元/万元。",
                }
            ),
            encoding="utf-8",
        )
        result = run(artifact)
        require(result.returncode == 0, f"unit-only-blocked-section: {result.stderr}")

        artifact.write_text(
            document({"来源、假设与未知项": "【模型估算】仅说明标签含义；【未知/待验证】续费率。"}),
            encoding="utf-8",
        )
        result = run(artifact)
        require(result.returncode == 0, f"model-label-only-source-note: {result.stderr}")

        artifact.write_text(
            document({"上下游与价值分配": "【未知/待验证】单位勾稽：不兼容；下游传播：停止；影响章节：未用于模型。"}),
            encoding="utf-8",
        )
        result = run(artifact)
        require(result.returncode == 0, f"unmodeled-unit-gap: {result.stderr}")

        artifact.write_text(document(omit={"来源、假设与未知项"}), encoding="utf-8")
        require_failure(run(artifact), "missing-section", "missing required section")

        artifact.write_text(document().replace("Research Level 0（L0，研究级别 0，约 30–60 分钟的资源筛选）\n\n", ""), encoding="utf-8")
        require_failure(run(artifact), "missing-l0-declaration", "missing complete L0 declaration")

        wrong_name = root / "prescreen.md"
        wrong_name.write_text(document(), encoding="utf-8")
        require_failure(run(wrong_name), "wrong-filename", "artifact basename must be 01-prescreen.md")

        artifact.unlink()
        require_failure(run(artifact), "missing-file", "cannot read artifact")

        artifact.write_text(document(), encoding="utf-8")
        before = artifact.read_bytes()
        run(artifact)
        require(artifact.read_bytes() == before, "validator modified artifact")

    print("jvc-prescreen package check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

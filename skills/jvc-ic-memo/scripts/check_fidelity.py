#!/usr/bin/env python3
"""Exercise the default final-publication CLI with synthetic reviewed statements."""
import subprocess
import sys
import tempfile
from pathlib import Path

REVIEW = """# IC Memo 预审版

## 1. 执行摘要
甲公司预计 2027 年收入 3000 万元，已确认订单 800 万元。[S1]

乙公司预计 2027 年收入 800 万元。[S2]

客户尚未完成验收，预计明年完成。[S3]

## 3. 投资风险
收入兑现取决于客户验收。[S3]

若续费率低于 60%，则经营贡献转负。[S4]

## 14. 收入预测模型
| 公司 | 2027 年收入 | 订单 |
| --- | --- | --- |
| 甲公司 | 3000 万元 | 800 万元 |
| 乙公司 | 800 万元 | 3000 万元 |

## 附录：质量报告
已核对上述来源。
"""
FINAL = REVIEW.split("## 附录")[0].replace("预审版", "")
for source in ("[S1]", "[S2]", "[S3]", "[S4]"):
    FINAL = FINAL.replace(source, "")


def main():
    validator = Path(__file__).with_name("validate_final.py")
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        review, final = folder / "review.md", folder / "final.md"
        review.write_text(REVIEW)
        cases = {
            "valid-formatting": (FINAL.replace("3000 万元", "**3000万元**"), True),
            "swap-metrics": (FINAL.replace("收入 3000 万元，已确认订单 800 万元", "收入 800 万元，已确认订单 3000 万元"), False),
            "remove-forecast": (FINAL.replace("甲公司预计", "甲公司"), False),
            "reverse-completion": (FINAL.replace("尚未完成验收，预计明年完成", "已完成验收"), False),
            "swap-entity": (FINAL.replace("甲公司预计 2027 年收入 3000", "乙公司预计 2027 年收入 3000"), False),
            "swap-table-columns": (FINAL.replace("| 甲公司 | 3000 万元 | 800 万元 |", "| 甲公司 | 800 万元 | 3000 万元 |"), False),
            "remove-risk-section": (FINAL.split("## 3.")[0] + "## 14." + FINAL.split("## 14.")[1], False),
            "remove-one-risk": (FINAL.replace("收入兑现取决于客户验收。", ""), False),
            "change-condition": (FINAL.replace("低于 60%", "高于 60%"), False),
            "new-qualitative-claim": (FINAL.replace("客户尚未", "公司拥有独家技术。客户尚未"), False),
            "hide-claim-in-code": (FINAL + "\n```text\n公司拥有独家技术。\n```\n", False),
            "remove-context": (FINAL.replace("客户尚未完成验收，预计明年完成。", ""), False),
            "change-title-subject": (FINAL.replace("# IC Memo", "# IC Memo 乙公司"), False),
        }
        for name, (text, success) in cases.items():
            final.write_text(text)
            before = (review.read_bytes(), final.read_bytes())
            run = subprocess.run([sys.executable, str(validator), "--review", str(review), "--final", str(final)], capture_output=True, text=True)
            assert (run.returncode == 0) == success, (name, run.stdout, run.stderr)
            if not success:
                assert "fidelity:" in run.stderr, (name, run.stderr)
            assert before == (review.read_bytes(), final.read_bytes()), "validator must be read-only"
        review.write_text(REVIEW.replace("## 3. 投资风险", "## 投资风险"))
        final.write_text(cases["remove-risk-section"][0])
        run = subprocess.run([sys.executable, str(validator), "--review", str(review), "--final", str(final)], capture_output=True, text=True)
        assert run.returncode == 1 and "must be numbered" in run.stderr, run.stderr
    print(f"IC fidelity regressions passed: {len(cases) + 1} cases")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import re
import sys
from pathlib import Path


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
LABELS = (
    "【第三方事实】",
    "【公司自述】",
    "【用户观察】",
    "【模型估算】",
    "【未知/待验证】",
)
MODEL_FIELDS = ("公式：", "单位：", "依据：", "置信度：")
L0_DECLARATION = "Research Level 0（L0，研究级别 0，约 30–60 分钟的资源筛选）"
MODEL_SECTIONS = ("市场规模粗算", "五年收入情景", "交易与回报粗算")
FACT_LABELS = ("【第三方事实】", "【公司自述】", "【用户观察】")
CHINESE_NUMERAL = r"(?=[零〇一二两三四五六七八九十百千万亿]*[零〇一二两三四五六七八九十])[零〇一二两三四五六七八九十百千万亿]+"
QUANTITATIVE_VALUE = re.compile(
    rf"(?:"
    r"\d+(?:\.\d+)?\s*(?:万|亿)?(?:元|美元|美金|USD|RMB)"
    r"|\d+(?:\.\d+)?\s*万(?![元亿])"
    r"|\d+(?:\.\d+)?\s*[%％]"
    r"|\d+(?:\.\d+)?\s*(?:倍|[xX×])"
    r"|\d+(?:\.\d+)?\s*(?:万|亿)?(?:家|个|件|台|套|条|吨|公斤|千克|克|人|户|辆|座|平方米|平米|亩|GWh|MWh|kWh|GW|MW|kW)"
    rf"|{CHINESE_NUMERAL}(?:元|美元|美金)"
    rf"|{CHINESE_NUMERAL}(?:家|个|件|台|套|条|吨|公斤|千克|克|人|户|辆|座|平方米|平米|亩|GWh|MWh|kWh|GW|MW|kW)"
    rf"|{CHINESE_NUMERAL}倍"
    rf"|百分之{CHINESE_NUMERAL}"
    r")",
    re.IGNORECASE,
)
RETURN_METRIC = re.compile(r"(?:MOIC|IRR|投入资本倍数|内部收益率)", re.IGNORECASE)
RETURN_ASSIGNMENT = re.compile(
    r"(?:MOIC|IRR|投入资本倍数|内部收益率)\s*[=＝:：]\s*(?:\d+(?:\.\d+)?|[零〇一二两三四五六七八九十百千万亿]+)",
    re.IGNORECASE,
)
UNIT_SCOPES = set(MODEL_SECTIONS)


def fail(message: str) -> int:
    print(f"validation failed: {message}", file=sys.stderr)
    return 1


def section_text(text: str, name: str) -> str:
    match = re.search(rf"^## {re.escape(name)}\s*$\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def has_quantitative_value(line: str) -> bool:
    return bool(QUANTITATIVE_VALUE.search(line) or RETURN_ASSIGNMENT.search(line))


def is_quantitative_model_line(line: str) -> bool:
    if not has_quantitative_value(line):
        return False
    model_signal = "【模型估算】" in line or "情景：" in line or "结果：" in line or bool(RETURN_METRIC.search(line))
    if any(label in line for label in FACT_LABELS) and not model_signal:
        return False
    return model_signal or not any(label in line for label in FACT_LABELS)


def quantitative_model_lines(content: str) -> list[str]:
    return [line for line in content.splitlines() if is_quantitative_model_line(line)]


def numeric_result_lines(content: str) -> list[str]:
    return [line for line in content.splitlines() if has_quantitative_value(field_value(line, "结果：") or "")]


def scenario_error(content: str, label: str) -> str | None:
    scenarios = []
    for line in numeric_result_lines(content):
        match = re.search(r"情景：(低|中|高)", line)
        if "【模型估算】" in line and match:
            scenarios.append(match.group(1))
    if sorted(scenarios) != ["中", "低", "高"]:
        return f"{label} scenarios must be low/mid/high"
    return None


def status_count(content: str, patterns: tuple[str, ...]) -> int:
    return sum(len(re.findall(pattern, content)) for pattern in patterns)


def field_value(line: str, field: str) -> str | None:
    match = re.search(rf"{re.escape(field)}\s*([^；。\n]*)", line)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def model_field_error(line: str) -> str | None:
    for field in (*MODEL_FIELDS, "结果："):
        if field_value(line, field) is None:
            return f"model estimate empty {field.removesuffix('：')}"
    return None


def revenue_path_error(content: str) -> str | None:
    lines = [line.strip("* `。") for line in content.splitlines() if "唯一驱动路径：" in line]
    if len(lines) != 1:
        return "exactly one revenue driver path"
    path = lines[0].partition("唯一驱动路径：")[2]
    if any(connector in path for connector in ("与", "以及", "取平均", "两条路径")):
        return "invalid revenue driver path"
    if path in ("市场份额", "客户数 × 单客收入", "产能 × 售价"):
        return None
    if path.startswith("其他单一驱动：") and path.removeprefix("其他单一驱动：").strip():
        return None
    return "invalid revenue driver path"


def validate(text: str) -> str | None:
    headings = re.findall(r"^## (.+?)\s*$", text, re.MULTILINE)
    if tuple(headings) != SECTIONS:
        return "missing required section or section order mismatch"

    for section in SECTIONS:
        if not section_text(text, section):
            return f"missing required section content: {section}"

    for label in LABELS:
        if label not in text:
            return f"missing visible label: {label}"

    if L0_DECLARATION not in text:
        return "missing complete L0 declaration"

    conclusion = section_text(text, "快筛结论")
    choices = re.findall(r"研究资源判断：(继续研究|等待关键材料|暂不继续)(?=[。；;\n]|$)", conclusion)
    if len(choices) != 1:
        return "invalid research-resource conclusion"
    if "不替用户作投资决定" not in conclusion:
        return "missing no-investment-decision boundary"
    if re.search(r"(?:建议投资|不建议投资|有条件投资|应该投资|推荐投资|值得投资|建议投。|不投。|有条件投。)", text):
        return "final investment decision"

    market = section_text(text, "市场规模粗算")
    business = section_text(text, "商业模式")
    revenue = section_text(text, "五年收入情景")
    returns = section_text(text, "交易与回报粗算")

    if status_count(business, (r"商业模式要素：完整", r"商业模式要素：缺失（[^）]+）")) != 1:
        return "invalid business-model status"
    if status_count(market, (r"市场锚点：存在", r"市场锚点：缺失")) != 1:
        return "invalid market-anchor status"
    if status_count(returns, (r"交易条款：完整", r"交易条款：缺少估值或投资额")) != 1:
        return "invalid transaction-term status"

    business_missing = "商业模式要素：缺失" in business
    market_missing = "市场锚点：缺失" in market
    terms_missing = "交易条款：缺少估值或投资额" in returns

    if market_missing:
        if "仅列公式，不输出市场数字" not in market:
            return "missing no-market-anchor handling"
        if quantitative_model_lines(market):
            return "quantitative market output without anchor"

    if terms_missing:
        if "条件式敏感性框架" not in returns:
            return "missing conditional return framework"
        if quantitative_model_lines(returns):
            return "quantitative return without terms"

    if business_missing:
        if "收入测算：阻断" not in text or "回报测算：阻断" not in text:
            return "missing business-model stop handling"
        if quantitative_model_lines(revenue) or quantitative_model_lines(returns):
            return "quantitative output after business-model stop"

    blocked_sections: set[str] = set()
    for line in (line for line in text.splitlines() if "单位勾稽：不兼容" in line):
        if "下游传播：停止" not in line:
            return "incompatible unit propagation"
        scope_match = re.search(r"影响章节：([^；。`]+)", line)
        if not scope_match:
            return "missing incompatible-unit scope"
        scope = scope_match.group(1)
        if scope == "未用于模型":
            continue
        affected = scope.split("、")
        if not affected or any(section not in UNIT_SCOPES for section in affected):
            return "invalid incompatible-unit scope"
        if any(quantitative_model_lines(section_text(text, section)) for section in affected):
            return "model result after incompatible unit stop"
        blocked_sections.update(affected)

    for section in MODEL_SECTIONS:
        for line in section_text(text, section).splitlines():
            if not is_quantitative_model_line(line):
                continue
            if "【模型估算】" not in line:
                return "quantitative model output missing model label"
            for field in MODEL_FIELDS:
                if field not in line:
                    return f"model estimate missing {field.removesuffix('：')}"
            if "结果：" not in line:
                return "quantitative model output missing 结果"
            error = model_field_error(line)
            if error:
                return error
            result = field_value(line, "结果：") or ""
            if not has_quantitative_value(result):
                return "model estimate result is not quantitative"
            if re.search(r"\d+\.\d{2,}", result):
                return "unsupported decimal precision"

    if not market_missing and "市场规模粗算" not in blocked_sections:
        error = scenario_error(market, "market")
        if error:
            return error

    if not business_missing and "五年收入情景" not in blocked_sections:
        error = scenario_error(revenue, "revenue")
        if error:
            return error
        error = revenue_path_error(revenue)
        if error:
            return error

    if not terms_missing and "交易与回报粗算" not in blocked_sections:
        audited_returns = [
            line
            for line in quantitative_model_lines(returns)
            if "【模型估算】" in line
            and "MOIC" in line
            and "IRR" in line
            and has_quantitative_value(field_value(line, "结果：") or "")
            and model_field_error(line) is None
        ]
        if not audited_returns:
            return "complete terms require audited return model"

    return None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return fail("usage: validate_output.py <01-prescreen.md>")
    path = Path(argv[1])
    if path.name != "01-prescreen.md":
        return fail("artifact basename must be 01-prescreen.md")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return fail(f"cannot read artifact: {error}")
    error = validate(text)
    if error:
        return fail(error)
    print("prescreen validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

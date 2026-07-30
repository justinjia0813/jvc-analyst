#!/usr/bin/env python3
"""验证 JVC Analyst 3.0 的公开基础合同。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LEVELS = {
    "jvc-prescreen": "L0+",
    "jvc-meeting-notes": "L1+",
    "jvc-talk-notes": "L1+",
    "jvc-track-research": "L1+",
    "jvc-knowledge-tree-builder": "L1+",
    "jvc-bull-case": "L2+",
    "jvc-bear-case": "L2+",
    "jvc-comps-dd": "L2+",
    "jvc-market-sizing": "L2+",
    "jvc-roi-modeler": "L2+",
    "jvc-research-report": "L2+",
    "jvc-ic-memo": "L3",
    "jvc-invoice-manager": "不适用",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(relative_path: str) -> str:
    path = ROOT / relative_path
    require(path.is_file(), f"缺少文件：{relative_path}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    manifest = json.loads(read("manifest.json"))
    require(manifest.get("version") == "3.0.0", "manifest.json 版本必须为 3.0.0")

    claude = read("CLAUDE.md")
    for signal in ("L0 快筛", "L1 初筛", "L2 尽调", "L3 重仓/领投", "砍流程不砍纪律"):
        require(signal in claude, f"CLAUDE.md 缺少 {signal!r}")

    readme = read("README.md")
    for signal in (
        "spec/CONTEXT.md",
        "spec/hypotheses.md",
        "spec/tasks.md",
        "STATE.md                    # L2+",
        "decision-journal.md",
        "旧项目迁移",
    ):
        require(signal in readme, f"README.md 缺少 {signal!r}")

    context = read("templates/project-context-template.md")
    for signal in ("last_verified", "领域术语", "判断标准", "已关闭的决策", "已重开"):
        require(signal in context, f"项目上下文模板缺少 {signal!r}")

    hypotheses = read("templates/hypotheses-template.md")
    for signal in (
        "认识论类型",
        "假设只能选择",
        "证据状态",
        "证伪条件",
        "支持证据",
        "反驳证据",
        "motive_check",
    ):
        require(signal in hypotheses, f"假设模板缺少 {signal!r}")

    for skill, level in EXPECTED_LEVELS.items():
        content = read(f"skills/{skill}/SKILL.md")
        require("version: \"3.0.0\"" in content, f"{skill}：版本必须为 3.0.0")
        require("## 3.0 适用级别" in content, f"{skill}：缺少 3.0 适用级别合同")
        require(f"最低适用级别：**{level}**" in content, f"{skill}：最低适用级别应为 {level}")
        require("## 反合理化约束" in content, f"{skill}：缺少反合理化约束")

    prescreen = read("skills/jvc-prescreen/SKILL.md")
    require("L0 不初始化证据内核" in prescreen, "jvc-prescreen：L0 必须保持零额外研究文件")

    print("JVC Analyst 3.0 基础合同检查通过")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"JVC Analyst 3.0 基础合同检查失败：{exc}")
        raise SystemExit(1)

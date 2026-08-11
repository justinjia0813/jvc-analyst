#!/usr/bin/env python3
"""Validate jvc governance assets and source-contract hash."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HASH_PLACEHOLDER = "REPLACE_WITH_SOURCE_CONTRACT_HASH"
EXPECTED_TAXONOMY = {
    "control_and_engine": ["jvc-deal-flow", "jvc-research-core"],
    "track_level": ["jvc-track-research", "jvc-knowledge-tree-builder", "jvc-market-sizing"],
    "project_level": [
        "jvc-prescreen",
        "jvc-bull-case",
        "jvc-bear-case",
        "jvc-comps-dd",
        "jvc-meeting-notes",
        "jvc-talk-notes",
        "jvc-roi-modeler",
    ],
    "output_level": ["jvc-ic-memo", "jvc-research-report"],
    "utility": ["jvc-invoice-manager"],
}
EXPECTED_ORCHESTRATION = {
    "project_orchestrator": "jvc-deal-flow",
    "unique_cross_stage_orchestrator": True,
    "atomic_skills_independently_invocable": True,
    "evidence_engine": "jvc-research-core",
    "evidence_engine_user_invocable": False,
    "evidence_engine_advances_workflow_stages": False,
    "evidence_engine_responsibilities": ["evidence_ledger", "claim_inheritance", "artifact_audit"],
}
EXPECTED_P0_CONTRACTS = {
    "jvc-prescreen": {
        "version": "4.0.0",
        "research_level": "L0",
        "artifact_kind": "markdown",
        "outputs": ["01-prescreen.md"],
        "initializes_research_core": False,
        "validator": "skills/jvc-prescreen/scripts/validate_output.py",
        "package_check": "skills/jvc-prescreen/scripts/check_package.py",
    },
    "jvc-roi-modeler": {
        "version": "4.0.0",
        "artifact_kind": "csv",
        "layout": "single_table",
        "formula_driven": True,
        "validator": "skills/jvc-roi-modeler/scripts/validate_csv.py",
    },
}
EXPECTED_P1_CONTRACTS = {
    "jvc-track-research": {
        "version": "4.0.0",
        "artifact_kind": "markdown",
        "outputs": ["tracks/{track-slug}/landscape.md"],
        "handoffs": ["jvc-knowledge-tree-builder", "jvc-market-sizing"],
    },
    "jvc-knowledge-tree-builder": {
        "version": "4.0.0",
        "artifact_kind": "five_file_package",
        "primary_output": "knowledge_tree.md",
        "visual_first": True,
        "outputs": [
            "knowledge_tree.md",
            "knowledge_graph.mmd",
            "nodes.json",
            "evidence_index.md",
            "open_questions.md",
        ],
        "validator": "skills/jvc-knowledge-tree-builder/scripts/validate_output.py",
        "package_check": "skills/jvc-knowledge-tree-builder/scripts/check_package.py",
    },
    "jvc-market-sizing": {
        "version": "4.0.0",
        "artifact_kind": "csv",
        "layout": "single_table",
        "outputs": ["market-sizing.csv"],
        "validator": "skills/jvc-market-sizing/scripts/validate_csv.py",
        "package_check": "skills/jvc-market-sizing/scripts/check_package.py",
    },
}
EXPECTED_HASH_SCOPE = (
    "manifest, inspired-design.md, agents, security, skills, templates, scripts, evals, library, "
    "README, CLAUDE, setup; generated reports and local telemetry are excluded"
)

# Task 9: active governance path set for the repeatable negative search. Historical
# design docs (docs/superpowers), clearly labeled legacy fixtures, and the archived
# legacy workbook reports (reports/legacy) may retain historical wording; every other
# active contract may not.
ACTIVE_GOVERNANCE_ROOTS = (
    "README.md",
    "CLAUDE.md",
    "manifest.json",
    "inspired-design.md",
    "agents",
    "security",
    "skills",
    "templates",
    "examples",
    "scripts",
    "evals",
    "library",
    "reports/skill-ir.json",
    "reports/trust_report.json",
    "reports/trust_report.md",
    "reports/review-studio.json",
    "reports/review-studio.md",
    "reports/output_quality_scorecard.md",
)

# Phrases that prove a pre-CSV / pre-Markdown output contract is still active.
LEGACY_ACTIVE_PHRASES = (
    "05-market-sizing.xlsx",
    "05-comps-dd.xlsx",
    "05-roi-modeler.xlsx",
    "market-sizing-workbook-contract",
    "comps-dd-workbook-contract",
    "roi-modeler-workbook-contract",
    "当前仍输出 Excel",
    "P2 待迁移",
    "固定研报排版",
)

# The 11 historical pre-CSV output-eval / blind-review reports. Their top-level
# originals in reports/ are preserved byte-for-byte as records (never deleted,
# moved, or rewritten); their marked copies live in reports/legacy/ as
# historical-legacy-workbook archives. Neither set may be cited as proof that a
# new CSV/Markdown contract passed.
LEGACY_WORKBOOK_REPORTS = (
    "research-core-output-eval.json",
    "research-core-output-eval.md",
    "output_blind_review_pack.json",
    "output_blind_review_pack.md",
    "output_blind_answer_key.json",
    "output_review_kit.json",
    "output_review_kit.md",
    "output_review_kit.html",
    "output_review_adjudication.json",
    "output_review_adjudication.md",
    "output_review_decisions.json",
)

# Deliberate exceptions in the active path set: invoice/meeting/talk notes keep
# their operational DOCX / Excel+PDF exceptions, the ROI xlsx remains the
# user-provided input baseline (never an output claim), and the governance/check
# scripts themselves must keep the legacy phrases as negative-test fixtures
# (they assert that legacy contracts are rejected and would otherwise match
# their own assertion strings).
ACTIVE_NEGATIVE_SEARCH_EXCLUSIONS = (
    "skills/jvc-invoice-manager/",
    "skills/jvc-meeting-notes/",
    "skills/jvc-talk-notes/",
    "skills/jvc-roi-modeler/references/model-contract.md",
    "scripts/check-governance.py",
    "scripts/check-comps-dd-assets.sh",
    "scripts/check-skill-evals.py",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    require(path.is_file(), f"missing file: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_text(relative_path: str, text: str) -> None:
    path = ROOT / relative_path
    require(path.is_file(), f"missing file: {relative_path}")
    content = path.read_text(encoding="utf-8")
    require(text in content, f"{relative_path} missing {text!r}")


def require_not_text(relative_path: str, text: str) -> None:
    path = ROOT / relative_path
    require(path.is_file(), f"missing file: {relative_path}")
    require(text not in path.read_text(encoding="utf-8"), f"{relative_path} contains obsolete {text!r}")


def strip_archive_banner(content: bytes, banner_lines: int) -> bytes:
    """Return the archive copy body after removing its top banner lines."""
    lines = content.split(b"\n")
    body = b"\n".join(lines[banner_lines:])
    if body.endswith(b"\n"):
        body = body[:-1]
    return body


def source_contract_files() -> list[Path]:
    included: list[Path] = []
    roots = [
        "manifest.json",
        "inspired-design.md",
        "agents",
        "security",
        "skills",
        "templates",
        "scripts",
        "evals",
        "library",
        "README.md",
        "CLAUDE.md",
        "setup",
    ]
    for root_name in roots:
        root = ROOT / root_name
        if root.is_file():
            included.append(root)
        elif root.is_dir():
            included.extend(path for path in root.rglob("*") if path.is_file())

    return sorted(
        path
        for path in included
        if "__pycache__" not in path.parts and not path.name.endswith(".pyc")
        and not (path.parent.parent.name == "skills" and path.name == "data.json")
    )


def require_complete_taxonomy(taxonomy: Any, source: str) -> None:
    require(isinstance(taxonomy, dict), f"{source} taxonomy must be an object")
    actual_skills = {path.parent.name for path in (ROOT / "skills").glob("jvc-*/SKILL.md")}
    flattened: set[str] = set()
    for category, skills in taxonomy.items():
        require(isinstance(skills, list), f"{source} taxonomy category {category} must be a list")
        require(
            all(isinstance(skill, str) and skill for skill in skills),
            f"{source} taxonomy category {category} contains an invalid skill",
        )
        require(len(skills) == len(set(skills)), f"{source} taxonomy category {category} contains duplicates")
        overlaps = flattened & set(skills)
        require(not overlaps, f"{source} taxonomy categories overlap: {sorted(overlaps)}")
        flattened.update(skills)
    require(
        flattened == actual_skills,
        f"{source} taxonomy skill mismatch: expected {sorted(actual_skills)}, got {sorted(flattened)}",
    )


def compute_source_contract_hash() -> str:
    digest = hashlib.sha256()
    for path in source_contract_files():
        relative = path.relative_to(ROOT).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def write_trust_hash(value: str) -> None:
    json_path = ROOT / "reports/trust_report.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    markdown_path = ROOT / "reports/trust_report.md"
    markdown = markdown_path.read_text(encoding="utf-8")
    hash_pattern = r"`[0-9a-f]{64}`"
    date_pattern = r"^日期：\d{4}-\d{2}-\d{2}$"
    require(len(re.findall(hash_pattern, markdown)) == 1, "trust report markdown hash was not uniquely identifiable")
    require(len(re.findall(date_pattern, markdown, flags=re.MULTILINE)) == 1, "trust report markdown date was not uniquely identifiable")

    generated_at = date.today().isoformat()
    data["generated_at"] = generated_at
    data["package_sha256"] = value
    updated, hash_count = re.subn(hash_pattern, f"`{value}`", markdown, count=1)
    updated, date_count = re.subn(date_pattern, f"日期：{generated_at}", updated, count=1, flags=re.MULTILINE)
    require(hash_count == 1, "trust report markdown hash was not uniquely identifiable")
    require(date_count == 1, "trust report markdown date was not uniquely identifiable")

    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(updated, encoding="utf-8")


def check_manifest() -> None:
    manifest = load_json("manifest.json")
    for field in [
        "name",
        "version",
        "owner",
        "updated_at",
        "status",
        "maturity_tier",
        "lifecycle_stage",
        "review_cadence",
        "target_platforms",
    ]:
        require(field in manifest, f"manifest missing {field}")
    require(manifest["name"] == "jvc-analyst", "manifest name must be jvc-analyst")
    require(manifest["status"] in {"experimental", "active", "deprecated"}, "invalid manifest status")
    require(manifest["maturity_tier"] in {"scaffold", "production", "library", "governed"}, "invalid maturity_tier")
    require(manifest["review_cadence"] in {"monthly", "quarterly", "semiannual", "annual", "per-release"}, "invalid review_cadence")
    taxonomy = manifest.get("taxonomy")
    require_complete_taxonomy(taxonomy, "manifest")
    require(taxonomy == EXPECTED_TAXONOMY, "manifest taxonomy mismatch")
    require(manifest.get("orchestration") == EXPECTED_ORCHESTRATION, "manifest orchestration mismatch")
    require(manifest.get("p0_contracts") == EXPECTED_P0_CONTRACTS, "manifest P0 contracts mismatch")
    require(manifest.get("p1_contracts") == EXPECTED_P1_CONTRACTS, "manifest P1 contracts mismatch")


def check_interface() -> None:
    require_text("agents/interface.yaml", "display_name: \"jvc-analyst\"")
    require_text("agents/interface.yaml", "remote_inline_execution: \"forbid\"")
    for skill_path in (ROOT / "skills").glob("jvc-*/SKILL.md"):
        require_text("agents/interface.yaml", f"skills/{skill_path.parent.name}/SKILL.md")
    require_text("skills/jvc-research-core/SKILL.md", "user_invocable: false")
    require_text("skills/jvc-deal-flow/SKILL.md", "唯一项目总控")
    require_text("skills/jvc-deal-flow/SKILL.md", "所有原子 Skill 仍可独立调用")
    require_text("skills/jvc-research-core/SKILL.md", "不推进业务阶段")
    require_text("setup", "SUPPORT_COMPONENTS")
    require_text("setup", "jvc-research-core")
    require_text("README.md", "固定输出 `01-prescreen.md`")
    require_text("README.md", "非最终投决")
    require_text("library/skill-registry.md", "固定输出 `01-prescreen.md`")
    require_text("library/skill-registry.md", "非最终投决")
    for path in ("README.md", "library/skill-registry.md"):
        require_not_text(path, "七维")
        require_not_text(path, "bear case 雏形")


def check_p0_consistency() -> None:
    require_text(
        "inspired-design.md",
        "| 自主研究循环 | `/jvc-deal-flow` + 原子 Skill + Research Core | **复用现行受控循环**",
    )
    require_not_text("inspired-design.md", "**新建** `/jvc-research-loop`")
    require_text(
        "inspired-design.md",
        "| 证据模型 / 研究分级 | Research Core + Research Level 0–3（L0–L3，研究级别 0–3，按决策场景控制流程密度） | **增量演进**",
    )
    require_not_text("inspired-design.md", "| 证据模型 / 研究分级 | 无 |")
    require_not_text("skills/jvc-ic-memo/SKILL.md", "加权回报用 roi-modeler 计算")
    require_text(
        "skills/jvc-ic-memo/SKILL.md",
        "直接汇总 ROI Modeler 三种情景的 MOIC/IRR；如需加权，权重必须由用户另供",
    )

    ic_memo = (ROOT / "skills/jvc-ic-memo/SKILL.md").read_text(encoding="utf-8")
    for expected in (
        "prescreen (快筛结论/商业模式)",
        "prescreen (风险、证伪条件与下一步)",
        "prescreen (商业模式/上下游与价值分配)",
    ):
        require(expected in ic_memo, f"skills/jvc-ic-memo/SKILL.md missing {expected!r}")
    team_rows = [line for line in ic_memo.splitlines() if line.startswith("| 10. 核心团队 |")]
    require(len(team_rows) == 1, "IC memo must contain exactly one core-team source mapping")
    require("prescreen" not in team_rows[0], "IC memo core-team mapping must not use Pre-Screen 4.0")
    require("meeting-notes" in team_rows[0] and "deck" in team_rows[0], "IC memo core-team mapping must use meeting-notes and deck")

    registry = (ROOT / "library/skill-registry.md").read_text(encoding="utf-8")
    control_rows = [line for line in registry.splitlines() if line.startswith("| 控制与引擎 |")]
    require(len(control_rows) == 2, "skill registry must contain two control-and-engine rows")
    require(any("`jvc-deal-flow`" in line for line in control_rows), "skill registry missing Flow control-and-engine row")
    require(any("`jvc-research-core`" in line for line in control_rows), "skill registry missing Research Core control-and-engine row")
    core_row = next(line for line in control_rows if "`jvc-research-core`" in line)
    require("不可直接调用；只由已接入的研究 Skill 使用" in core_row, "skill registry Research Core trigger boundary mismatch")


def check_p1_consistency() -> None:
    for path in ("README.md", "library/skill-registry.md"):
        require_text(path, "market-sizing.csv")
        require_text(path, "knowledge_tree.md")
        require_text(path, "visual-first")
        require_not_text(path, "P1 待迁移")
        require_not_text(path, "05-market-sizing.xlsx")
    require_text("README.md", "tracks/{track-slug}/landscape.md")
    require_text("README.md", "knowledge_graph.mmd")
    require_text("README.md", "nodes.json")
    require_text("README.md", "evidence_index.md")
    require_text("README.md", "open_questions.md")
    require_text("library/skill-registry.md", "P2（Priority 2，优先级 2")
    workflow = "skills/jvc-deal-flow/references/workflow-contract.md"
    require_text(workflow, "`tracks/{track-slug}/landscape.md` → 五文件知识包")
    require_text(workflow, "只显式标记受影响或 `stale`")
    require_text(workflow, "不得自动重跑")
    require_text(workflow, "执行仍需用户批准")
    require_text(workflow, "`market-sizing.csv`")


def check_skill_ir() -> None:
    skill_ir = load_json("reports/skill-ir.json")
    require(skill_ir.get("schema_version") == 1, "skill-ir schema_version must be 1")
    skill_names = {item.get("name") for item in skill_ir.get("skills", [])}
    actual_skills = {path.parent.name for path in (ROOT / "skills").glob("jvc-*/SKILL.md")}
    require(skill_names == actual_skills, f"skill-ir skill mismatch: expected {sorted(actual_skills)}, got {sorted(skill_names)}")
    taxonomy = skill_ir.get("taxonomy")
    require_complete_taxonomy(taxonomy, "skill-ir")
    require(taxonomy == EXPECTED_TAXONOMY, "skill-ir taxonomy mismatch")
    require(skill_ir.get("orchestration") == EXPECTED_ORCHESTRATION, "skill-ir orchestration mismatch")
    skills = {item["name"]: item for item in skill_ir["skills"]}
    prescreen = skills["jvc-prescreen"]
    require(
        {key: prescreen.get(key) for key in ("version", "research_level", "artifact_kind", "outputs", "initializes_research_core", "scripts")}
        == {
            "version": "4.0.0",
            "research_level": "L0",
            "artifact_kind": "markdown",
            "outputs": ["01-prescreen.md"],
            "initializes_research_core": False,
            "scripts": [
                "skills/jvc-prescreen/scripts/validate_output.py",
                "skills/jvc-prescreen/scripts/check_package.py",
            ],
        },
        "skill-ir jvc-prescreen contract mismatch",
    )
    require(
        prescreen.get("failure_modes")
        == [
            "Invents a market number without an anchor",
            "Calculates revenue or return without an identifiable customer, payer, and product",
            "Propagates incompatible units",
            "Outputs a final investment decision",
        ],
        "skill-ir jvc-prescreen failure modes mismatch",
    )
    roi = skills["jvc-roi-modeler"]
    require(
        {key: roi.get(key) for key in ("version", "artifact_kind", "layout", "formula_driven", "outputs", "scripts")}
        == {
            "version": "4.0.0",
            "artifact_kind": "csv",
            "layout": "single_table",
            "formula_driven": True,
            "outputs": ["Formula-driven single-table CSV return model"],
            "scripts": ["skills/jvc-roi-modeler/scripts/validate_csv.py"],
        },
        "skill-ir jvc-roi-modeler contract mismatch",
    )
    track = skills["jvc-track-research"]
    knowledge = skills["jvc-knowledge-tree-builder"]
    market = skills["jvc-market-sizing"]
    require(
        {key: track.get(key) for key in EXPECTED_P1_CONTRACTS["jvc-track-research"]}
        == EXPECTED_P1_CONTRACTS["jvc-track-research"],
        "skill-ir jvc-track-research contract mismatch",
    )
    require(
        {key: knowledge.get(key) for key in EXPECTED_P1_CONTRACTS["jvc-knowledge-tree-builder"]}
        == EXPECTED_P1_CONTRACTS["jvc-knowledge-tree-builder"],
        "skill-ir jvc-knowledge-tree-builder contract mismatch",
    )
    require(
        {key: market.get(key) for key in EXPECTED_P1_CONTRACTS["jvc-market-sizing"]}
        == EXPECTED_P1_CONTRACTS["jvc-market-sizing"],
        "skill-ir jvc-market-sizing contract mismatch",
    )
    comps = skills["jvc-comps-dd"]
    require(
        {key: comps.get(key) for key in ("artifact_kind", "outputs", "scripts")}
        == {
            "artifact_kind": "markdown",
            "outputs": ["03-comps-dd.md"],
            "scripts": [],
        },
        "skill-ir jvc-comps-dd contract mismatch",
    )
    require("Excel" not in json.dumps(comps, ensure_ascii=False), "skill-ir jvc-comps-dd must not claim Excel")
    research_report = skills["jvc-research-report"]
    require("research-report.md" in research_report.get("outputs", []), "skill-ir jvc-research-report must list research-report.md")
    require(
        "skills/jvc-research-report/scripts/validate_assembly.py" in research_report.get("scripts", []),
        "skill-ir jvc-research-report must list validate_assembly.py",
    )
    require("组装" in research_report.get("job", ""), "skill-ir jvc-research-report job must describe assembly")
    ic_memo = skills["jvc-ic-memo"]
    require(
        ic_memo.get("outputs") == ["Audited IC memo pre-review", "User-approved clean Markdown final"],
        "skill-ir jvc-ic-memo outputs mismatch",
    )
    prescreen_profile = load_json("skills/jvc-research-core/profiles/jvc-prescreen.json")
    require(
        prescreen_profile.get("artifact_policy")
        == {
            "kind": "markdown",
            "allowed_suffixes": [".md"],
            "required_names": ["01-prescreen.md"],
            "required_sheets": [],
        },
        "jvc-prescreen Research Core profile mismatch",
    )
    roi_profile = load_json("skills/jvc-research-core/profiles/jvc-roi-modeler.json")
    require(roi_profile.get("artifact_policy", {}).get("kind") == "csv", "jvc-roi-modeler profile must use CSV")
    for path in (
        "skills/jvc-prescreen/scripts/validate_output.py",
        "skills/jvc-prescreen/scripts/check_package.py",
        "skills/jvc-roi-modeler/scripts/validate_csv.py",
        "skills/jvc-knowledge-tree-builder/scripts/validate_output.py",
        "skills/jvc-knowledge-tree-builder/scripts/check_package.py",
        "skills/jvc-market-sizing/scripts/validate_csv.py",
        "skills/jvc-market-sizing/scripts/check_package.py",
        "templates/roi-modeler-template.csv",
    ):
        require((ROOT / path).is_file(), f"missing P0 contract asset: {path}")
    require(skill_ir.get("evals", {}).get("trigger_cases") == "evals/trigger_cases.json", "skill-ir missing trigger eval link")
    require(skill_ir.get("reports", {}).get("trust_report") == "reports/trust_report.md", "skill-ir missing trust report link")


def check_security() -> None:
    network = load_json("security/network_policy.json")
    permission = load_json("security/permission_policy.json")
    require(network.get("schema_version") == 1, "network policy schema_version must be 1")
    require(isinstance(network.get("network_capable_scripts"), list), "network policy missing script list")
    require(not network.get("network_capable_scripts"), "research core must not add network-capable scripts")
    approvals = permission.get("approvals")
    require(isinstance(approvals, list) and approvals, "permission policy missing approvals")
    approved = {approval.get("capability") for approval in approvals if approval.get("decision") == "approved"}
    for capability in {"file_read", "file_write", "subprocess"}:
        require(capability in approved, f"permission policy missing approved {capability}")
    write_scope = next(
        (approval.get("scope", "") for approval in approvals if approval.get("capability") == "file_write"),
        "",
    )
    require("CSV model" in write_scope, "permission policy file_write must describe CSV model writes")
    require(" XLSX," not in write_scope, "permission policy file_write must not enumerate XLSX generally")
    require("invoice Excel summary" in write_scope, "permission policy file_write must keep the invoice Excel exception")
    read_scope = next(
        (approval.get("scope", "") for approval in approvals if approval.get("capability") == "file_read"),
        "",
    )
    require("CSV model files" in read_scope, "permission policy file_read must describe CSV model reads")


def check_script_inventory(inventory: Any) -> None:
    require(isinstance(inventory, list) and inventory, "trust report missing script inventory")
    entries_by_path: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(inventory):
        require(isinstance(entry, dict), f"script inventory entry {index} must be an object")
        path = entry.get("path")
        require(isinstance(path, str) and path, f"script inventory entry {index} missing path")
        require(path not in entries_by_path, f"duplicate script inventory path: {path}")
        require((ROOT / path).is_file(), f"script inventory path does not exist: {path}")
        entries_by_path[path] = entry

    required_paths = {
        "skills/jvc-deal-flow/scripts/dealflowctl.py",
        "skills/jvc-deal-flow/scripts/check_package.py",
        "skills/jvc-ic-memo/scripts/validate_final.py",
        "skills/jvc-ic-memo/scripts/check_package.py",
        "skills/jvc-prescreen/scripts/validate_output.py",
        "skills/jvc-prescreen/scripts/check_package.py",
        "skills/jvc-roi-modeler/scripts/validate_csv.py",
        "skills/jvc-research-core/scripts/researchctl.py",
        "skills/jvc-research-core/scripts/check_package.py",
        "skills/jvc-research-report/scripts/validate_assembly.py",
        "scripts/check-skill-evals.py",
        "scripts/check-research-core-install.py",
    }
    missing = required_paths - entries_by_path.keys()
    require(not missing, f"script inventory missing required scripts: {sorted(missing)}")

    expected_entries = {
        "skills/jvc-ic-memo/scripts/validate_final.py": {
            "interface": "argparse",
            "help_surface": "--help",
            "capabilities": ["file_read"],
        },
        "skills/jvc-ic-memo/scripts/check_package.py": {
            "interface": "self-check",
            "help_surface": "none",
            "capabilities": ["file_read", "file_write", "subprocess"],
        },
        "skills/jvc-prescreen/scripts/validate_output.py": {
            "interface": "cli",
            "help_surface": "usage",
            "capabilities": ["file_read"],
            "network": False,
        },
        "skills/jvc-prescreen/scripts/check_package.py": {
            "interface": "self-check",
            "help_surface": "none",
            "capabilities": ["file_read", "file_write", "subprocess"],
            "write_scope": "temporary_directories_only",
            "network": False,
        },
        "skills/jvc-research-core/scripts/check_package.py": {
            "interface": "self-check",
            "help_surface": "none",
            "capabilities": ["file_read", "file_write", "subprocess"],
        },
        "skills/jvc-knowledge-tree-builder/scripts/validate_output.py": {
            "interface": "cli",
            "help_surface": "usage",
            "capabilities": ["file_read"],
            "network": False,
        },
        "skills/jvc-knowledge-tree-builder/scripts/check_package.py": {
            "interface": "self-check",
            "help_surface": "none",
            "capabilities": ["file_read", "file_write", "subprocess"],
            "write_scope": "temporary_directories_only",
            "network": False,
        },
        "skills/jvc-market-sizing/scripts/validate_csv.py": {
            "interface": "cli",
            "help_surface": "usage",
            "capabilities": ["file_read"],
            "network": False,
        },
        "skills/jvc-market-sizing/scripts/check_package.py": {
            "interface": "self-check",
            "help_surface": "none",
            "capabilities": ["file_read", "file_write", "subprocess"],
            "write_scope": "temporary_directories_only",
            "network": False,
        },
        "skills/jvc-research-report/scripts/validate_assembly.py": {
            "interface": "cli",
            "help_surface": "usage",
            "capabilities": ["file_read"],
            "network": False,
        },
        "scripts/check-skill-evals.py": {
            "interface": "cli",
            "help_surface": "none",
            "capabilities": ["file_read", "file_write", "subprocess"],
            "write_scope": "temporary_directories_only",
        },
    }
    for path, expected in expected_entries.items():
        actual = {field: entries_by_path[path].get(field) for field in expected}
        require(actual == expected, f"script inventory metadata mismatch for {path}: expected {expected}, got {actual}")


def check_trust_report() -> None:
    trust = load_json("reports/trust_report.json")
    require(trust.get("schema_version") == 1, "trust report schema_version must be 1")
    require(trust.get("package") == "jvc-analyst", "trust report package mismatch")
    require(trust.get("hash_scope") == EXPECTED_HASH_SCOPE, "trust report hash_scope mismatch")
    generated_at = trust.get("generated_at")
    require(isinstance(generated_at, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", generated_at), "trust report generated_at must use YYYY-MM-DD")
    actual_hash = compute_source_contract_hash()
    expected_hash = trust.get("package_sha256")
    require(expected_hash != HASH_PLACEHOLDER, "trust report package_sha256 placeholder was not replaced")
    require(expected_hash == actual_hash, f"trust report hash mismatch: expected {actual_hash}, got {expected_hash}")
    check_script_inventory(trust.get("script_inventory"))

    dependency_note = "The IC memo final validator and package check use the Python standard library only."
    dependency_notes = trust.get("dependency_review", {}).get("notes", [])
    require(dependency_note in dependency_notes, "trust report missing IC memo dependency note")
    require(
        "The Pre-Screen validator and package check use the Python standard library only."
        in dependency_notes,
        "trust report missing Pre-Screen dependency note",
    )
    require(
        "The Research Report assembly validator uses the Python standard library only."
        in dependency_notes,
        "trust report missing Research Report assembly dependency note",
    )
    for note in (
        "The Knowledge Tree validator uses the Python standard library only; its package check also invokes local Quarto and Poppler tools.",
        "The Market Sizing validator and package check use the Python standard library only.",
    ):
        require(note in dependency_notes, f"trust report missing dependency note: {note}")
    research_evidence = trust.get("research_report_evidence", {})
    require(
        research_evidence.get("fixture") == "examples/research-report-example/research-report.md",
        "trust research_report_evidence fixture must be the canonical research-report.md",
    )
    artifact = research_evidence.get("artifact_check", {})
    require(artifact.get("page_count") == 14, "trust research_report_evidence page_count must be 14")
    require(
        artifact.get("pdftoppm") == "pass: 14 of 14 pages rendered",
        "trust research_report_evidence pdftoppm must report 14 of 14 pages rendered",
    )
    build_log = (ROOT / "reports/task9-visual/research-report-build.txt").read_text(encoding="utf-8")
    build_match = re.search(r"page_count:\s*(\d+)", build_log)
    require(
        build_match is not None and int(build_match.group(1)) == artifact.get("page_count"),
        "trust research_report_evidence page_count must match reports/task9-visual/research-report-build.txt",
    )
    visual = artifact.get("visual_inspection", "")
    require(
        visual.startswith("pass") and "2026-08-10" in visual and "MAIN-VISUAL-INSPECTION.md" in visual,
        "trust research_report_evidence must record the main-agent 2026-08-10 visual inspection (reports/task9-visual/MAIN-VISUAL-INSPECTION.md)",
    )

    network_policy = trust.get("network_policy", {})
    require(network_policy.get("network_capable_scripts") == [], "trust report network-capable script list must be empty")
    network_notes = network_policy.get("notes", [])
    require(any(isinstance(note, str) and "IC memo" in note for note in network_notes), "trust report missing IC memo network note")
    require(
        any(isinstance(note, str) and "Pre-Screen validator and package check" in note for note in network_notes),
        "trust report missing Pre-Screen network note",
    )
    require(
        any(isinstance(note, str) and "Knowledge Tree and Market Sizing validators and package checks" in note for note in network_notes),
        "trust report missing P1 validator network note",
    )
    require(
        any(isinstance(note, str) and "Research Report assembly validator" in note for note in network_notes),
        "trust report missing Research Report assembly network note",
    )

    markdown = (ROOT / "reports/trust_report.md").read_text(encoding="utf-8")
    for expected in [
        expected_hash,
        f"日期：{generated_at}",
        "| `skills/jvc-ic-memo/scripts/validate_final.py` | argparse CLI | file read；无网络 |",
        "| `skills/jvc-ic-memo/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时目录 |",
        "| `skills/jvc-prescreen/scripts/validate_output.py` | CLI | file read；无网络 |",
        "| `skills/jvc-prescreen/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时目录；无网络 |",
        "| `skills/jvc-knowledge-tree-builder/scripts/validate_output.py` | CLI | file read；无网络 |",
        "| `skills/jvc-knowledge-tree-builder/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时目录；调用本地 Quarto 与 Poppler；无网络 |",
        "| `skills/jvc-market-sizing/scripts/validate_csv.py` | CLI | file read；无网络 |",
        "| `skills/jvc-market-sizing/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时目录；无网络 |",
        "| `skills/jvc-research-report/scripts/validate_assembly.py` | CLI | file read；无网络 |",
        "| `skills/jvc-research-core/scripts/check_package.py` | self-check | file read, file write, subprocess；无网络 |",
        "| `scripts/check-skill-evals.py` | CLI | file read, file write, subprocess；仅使用临时目录 |",
        "`inspired-design.md`",
        "IC memo validator/package check 仅使用 Python 标准库",
        "Pre-Screen validator/package check 仅使用 Python 标准库",
        "IC memo validator 和 IC memo package check 均无网络能力",
        "Pre-Screen validator and package check 均无网络能力",
        "Knowledge Tree 与 Market Sizing validator/package check 均无网络能力",
        "Research Report assembly validator 无网络能力",
    ]:
        require(expected in markdown, f"reports/trust_report.md missing {expected!r}")


def check_review_studio() -> None:
    review = load_json("reports/review-studio.json")
    require(review.get("schema_version") == 1, "review-studio schema_version must be 1")
    gates = review.get("gates")
    require(isinstance(gates, list) and len(gates) == 13, "review-studio must include 13 gates")
    for gate in gates:
        require(gate.get("status") in {"pass", "warn", "block"}, f"invalid gate status: {gate}")
        if gate.get("status") != "pass":
            require(gate.get("review_action"), f"non-pass gate missing review_action: {gate.get('key')}")

    # No gate evidence, the top-level decision, or any other JSON field may cite
    # the 11 archived legacy reports or the demoted report.md fixture.
    forbidden = tuple(f"reports/{name}" for name in LEGACY_WORKBOOK_REPORTS) + (
        "examples/research-report-example/report.md",
    )
    found: list[tuple[str, str]] = []

    def walk(node: Any, where: str) -> None:
        if isinstance(node, str):
            for legacy in forbidden:
                if legacy in node:
                    found.append((where, legacy))
        elif isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{where}.{key}" if where else key)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{where}[{index}]")

    walk(review, "")
    require(not found, f"review-studio must not cite historical artifacts: {found}")

    output_gate = next(gate for gate in gates if gate.get("key") == "output-lab")
    evidence = output_gate.get("evidence", [])
    require(
        "examples/research-report-example/research-report.md" in evidence,
        "review-studio output-lab missing canonical research-report example",
    )
    require_text("reports/review-studio.md", "Review Studio")


def check_legacy_archive() -> None:
    """The 11 historical reports stay preserved as top-level originals and are
    archived as explicitly marked copies under reports/legacy/; neither set is
    active governance evidence for the new CSV contract."""
    for name in LEGACY_WORKBOOK_REPORTS:
        original = ROOT / "reports" / name
        require(original.is_file(), f"historical report original missing: reports/{name}")
        copy = ROOT / "reports/legacy" / name
        require(copy.is_file(), f"historical report archive copy missing: reports/legacy/{name}")
        require(copy.stat().st_size > 0, f"historical report archive copy empty: reports/legacy/{name}")

    status = (ROOT / "reports/legacy/STATUS.md").read_text(encoding="utf-8")
    for expected in (
        "historical-legacy-workbook",
        "已移出活跃治理证据",
        "不得",
        "新合同通过",
    ):
        require(expected in status, f"reports/legacy/STATUS.md missing {expected!r}")

    legacy_json = ("output_blind_answer_key.json", "output_blind_review_pack.json", "output_review_adjudication.json", "output_review_decisions.json", "output_review_kit.json", "research-core-output-eval.json")
    for name in legacy_json:
        data = load_json(f"reports/legacy/{name}")
        block = data.get("historical_legacy_workbook")
        require(isinstance(block, dict), f"reports/legacy/{name} missing historical_legacy_workbook block")
        # The archive copy is the tracked top-level original plus the marker
        # block only: after removing historical_legacy_workbook the body must
        # equal the original JSON exactly, so a tampered body is detected even
        # though reports/legacy/ is untracked.
        original = load_json(f"reports/{name}")
        body = {key: value for key, value in data.items() if key != "historical_legacy_workbook"}
        require(
            body == original,
            f"reports/legacy/{name} body must equal the top-level original after removing historical_legacy_workbook",
        )
        require(block.get("status") == "archived", f"reports/legacy/{name} block status must be archived")
        require(
            block.get("classification") == "historical-legacy-workbook",
            f"reports/legacy/{name} block classification mismatch",
        )
        require(
            block.get("not_active_governance_evidence") is True,
            f"reports/legacy/{name} must declare not_active_governance_evidence",
        )
        require(
            block.get("not_proof_of_new_csv_contract") is True,
            f"reports/legacy/{name} must declare not_proof_of_new_csv_contract",
        )
        require(
            isinstance(block.get("archived_at"), str)
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", block.get("archived_at", "")),
            f"reports/legacy/{name} block archived_at must use YYYY-MM-DD",
        )

    legacy_markdown = ("output_blind_review_pack.md", "output_review_adjudication.md", "output_review_kit.md", "research-core-output-eval.md")
    for name in legacy_markdown:
        content = (ROOT / f"reports/legacy/{name}").read_text(encoding="utf-8")
        require(
            "Historical legacy workbook" in content,
            f"reports/legacy/{name} missing historical banner",
        )
        require(
            "不作为任何新 CSV 合同通过的证明" in content,
            f"reports/legacy/{name} missing not-proof banner",
        )
        # After removing the known five-line top archive banner the copy must be
        # byte-for-byte equal to the tracked top-level original.
        original = (ROOT / f"reports/{name}").read_bytes()
        copy = (ROOT / f"reports/legacy/{name}").read_bytes()
        body = strip_archive_banner(copy, 5)
        require(
            body == original or body + b"\n" == original,
            f"reports/legacy/{name} body must equal the top-level original after removing the archive banner",
        )

    html = (ROOT / "reports/legacy/output_review_kit.html").read_text(encoding="utf-8")
    require("Historical legacy workbook" in html, "reports/legacy/output_review_kit.html missing historical comment")
    # After removing the single top archive comment line the copy must be
    # byte-for-byte equal to the tracked top-level original.
    html_original = (ROOT / "reports/output_review_kit.html").read_bytes()
    html_copy = (ROOT / "reports/legacy/output_review_kit.html").read_bytes()
    html_body = strip_archive_banner(html_copy, 1)
    require(
        html_body == html_original or html_body + b"\n" == html_original,
        "reports/legacy/output_review_kit.html body must equal the top-level original after removing the archive comment",
    )


def check_final_consistency() -> None:
    # Comps/DD Markdown: Skill, template, example, profile, README, registry, and
    # skill-ir must all agree on the fixed 03-comps-dd.md artifact.
    for path in ("README.md", "library/skill-registry.md"):
        require_text(path, "03-comps-dd.md")
        require_not_text(path, "05-comps-dd.xlsx")
        require_not_text(path, "05-market-sizing.xlsx")
    require_text("templates/comps-dd-template.md", "最终输出文件：`03-comps-dd.md`")
    require_text("skills/jvc-comps-dd/SKILL.md", "唯一活跃主产物：`03-comps-dd.md`")
    comps_profile = load_json("skills/jvc-research-core/profiles/jvc-comps-dd.json")
    require(
        comps_profile.get("artifact_policy") == {
            "kind": "markdown",
            "allowed_suffixes": [".md"],
            "required_names": ["03-comps-dd.md"],
            "required_sheets": [],
        },
        "jvc-comps-dd Research Core profile must require 03-comps-dd.md Markdown",
    )

    # Research Report: canonical Markdown plus rendered outputs, two stages.
    for path in ("README.md", "library/skill-registry.md"):
        require_text(path, "research-report.md")
    report_skill = (ROOT / "skills/jvc-research-report/SKILL.md").read_text(encoding="utf-8")
    for marker in ("组装", "发布", "validate_assembly.py", "直接发布", "research-report.md"):
        require(marker in report_skill, f"Research Report SKILL missing two-stage marker {marker!r}")
    require(
        (ROOT / "examples/research-report-example/research-report.md").is_file(),
        "missing canonical research-report example",
    )
    report_manifest = load_json("skills/jvc-research-report/manifest.json")
    require(
        "research-report.md" in report_manifest.get("output_contract", []),
        "Research Report manifest output_contract must list research-report.md",
    )

    # IC Memo review/final sequence: pre-review -> explicit user approval -> clean final.
    for path in ("README.md", "library/skill-registry.md"):
        require_text(path, "06-ic-memo-review.md")
        require_text(path, "06-ic-memo.md")
        require_text(path, "预审通过")
    ic_skill = (ROOT / "skills/jvc-ic-memo/SKILL.md").read_text(encoding="utf-8")
    require("预审版" in ic_skill and "干净终版" in ic_skill, "IC Memo SKILL missing pre-review/final sequence")

    # office / invoice exceptions: DOCX notes and invoice Excel+PDF remain explicit
    # exceptions; no active contract may claim general research Excel output.
    for path in ("README.md", "library/skill-registry.md"):
        require_text(path, "jvc-meeting-notes")
        require_text(path, "jvc-talk-notes")
    require_text("README.md", "报销汇总 Excel")
    require_text("library/skill-registry.md", "报销汇总 Excel")

    # Research Report may no longer be described as a pure formatter that never
    # assembles upstream artifacts.
    require_not_text("README.md", "固定研报排版")
    require_not_text("README.md", "校验已完成的固定章节行业研究并排版，不改正文")
    require_not_text("library/skill-registry.md", "不负责研究生成或正文改写")


def check_active_negative_search() -> None:
    # Scan the static active roots plus every locally resolvable path that
    # Review Studio cites as gate evidence, so a legacy phrase added to any
    # currently- or future-evidenced report is caught.
    scan_roots: list[str] = list(ACTIVE_GOVERNANCE_ROOTS)
    review = load_json("reports/review-studio.json")
    for gate in review.get("gates", []):
        for evidence in gate.get("evidence", []):
            if not isinstance(evidence, str) or not evidence:
                continue
            candidate = ROOT / evidence
            if candidate.is_file() or candidate.is_dir():
                relative = candidate.relative_to(ROOT).as_posix()
                if relative not in scan_roots:
                    scan_roots.append(relative)
    for root_name in scan_roots:
        root = ROOT / root_name
        if root.is_file():
            paths = [root]
        elif root.is_dir():
            paths = sorted(path for path in root.rglob("*") if path.is_file())
        else:
            continue
        for path in paths:
            relative = path.relative_to(ROOT).as_posix()
            if "__pycache__" in path.parts or path.name.endswith(".pyc"):
                continue
            if relative.startswith(ACTIVE_NEGATIVE_SEARCH_EXCLUSIONS):
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for phrase in LEGACY_ACTIVE_PHRASES:
                if phrase in content:
                    raise AssertionError(f"active path {relative} contains legacy contract phrase {phrase!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-hash", action="store_true", help="refresh trust report source-contract hashes")
    args = parser.parse_args(argv)

    try:
        if args.write_hash:
            write_trust_hash(compute_source_contract_hash())
        check_manifest()
        check_interface()
        check_p0_consistency()
        check_p1_consistency()
        check_skill_ir()
        check_security()
        check_trust_report()
        check_review_studio()
        check_legacy_archive()
        check_final_consistency()
        check_active_negative_search()
    except StopIteration:
        print("governance check failed: required item not found (StopIteration)", file=sys.stderr)
        return 1
    except (AssertionError, OSError, ValueError) as exc:
        print(f"governance check failed: {exc}", file=sys.stderr)
        return 1

    print(f"governance assets passed: source_contract_sha256={compute_source_contract_hash()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

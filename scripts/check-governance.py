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


def source_contract_files() -> list[Path]:
    included: list[Path] = []
    roots = [
        "manifest.json",
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


def check_interface() -> None:
    require_text("agents/interface.yaml", "display_name: \"jvc-analyst\"")
    require_text("agents/interface.yaml", "remote_inline_execution: \"forbid\"")
    for skill_path in (ROOT / "skills").glob("jvc-*/SKILL.md"):
        require_text("agents/interface.yaml", f"skills/{skill_path.parent.name}/SKILL.md")
    require_text("skills/jvc-research-core/SKILL.md", "user_invocable: false")
    require_text("setup", "SUPPORT_COMPONENTS")
    require_text("setup", "jvc-research-core")


def check_skill_ir() -> None:
    skill_ir = load_json("reports/skill-ir.json")
    require(skill_ir.get("schema_version") == 1, "skill-ir schema_version must be 1")
    skill_names = {item.get("name") for item in skill_ir.get("skills", [])}
    actual_skills = {path.parent.name for path in (ROOT / "skills").glob("jvc-*/SKILL.md")}
    require(skill_names == actual_skills, f"skill-ir skill mismatch: expected {sorted(actual_skills)}, got {sorted(skill_names)}")
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
        "skills/jvc-research-core/scripts/researchctl.py",
        "skills/jvc-research-core/scripts/check_package.py",
        "scripts/check-research-core-install.py",
    }
    missing = required_paths - entries_by_path.keys()
    require(not missing, f"script inventory missing required scripts: {sorted(missing)}")

    expected_ic_memo_entries = {
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
    }
    for path, expected in expected_ic_memo_entries.items():
        actual = {field: entries_by_path[path].get(field) for field in expected}
        require(actual == expected, f"script inventory metadata mismatch for {path}: expected {expected}, got {actual}")


def check_trust_report() -> None:
    trust = load_json("reports/trust_report.json")
    require(trust.get("schema_version") == 1, "trust report schema_version must be 1")
    require(trust.get("package") == "jvc-analyst", "trust report package mismatch")
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
    network_policy = trust.get("network_policy", {})
    require(network_policy.get("network_capable_scripts") == [], "trust report network-capable script list must be empty")
    network_notes = network_policy.get("notes", [])
    require(any(isinstance(note, str) and "IC memo" in note for note in network_notes), "trust report missing IC memo network note")

    markdown = (ROOT / "reports/trust_report.md").read_text(encoding="utf-8")
    for expected in [
        expected_hash,
        f"日期：{generated_at}",
        "| `skills/jvc-ic-memo/scripts/validate_final.py` | argparse CLI | file read；无网络 |",
        "| `skills/jvc-ic-memo/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时目录 |",
        "IC memo validator/package check 仅使用 Python 标准库",
        "IC memo validator 和 IC memo package check 均无网络能力",
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
    require_text("reports/review-studio.md", "Review Studio")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-hash", action="store_true", help="refresh trust report source-contract hashes")
    args = parser.parse_args(argv)

    try:
        if args.write_hash:
            write_trust_hash(compute_source_contract_hash())
        check_manifest()
        check_interface()
        check_skill_ir()
        check_security()
        check_trust_report()
        check_review_studio()
    except AssertionError as exc:
        print(f"governance check failed: {exc}", file=sys.stderr)
        return 1

    print(f"governance assets passed: source_contract_sha256={compute_source_contract_hash()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

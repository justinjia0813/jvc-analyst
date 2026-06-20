#!/usr/bin/env python3
"""Validate jvc governance assets and source-contract hash."""

from __future__ import annotations

import hashlib
import json
import sys
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
    approvals = permission.get("approvals")
    require(isinstance(approvals, list) and approvals, "permission policy missing approvals")
    approved = {approval.get("capability") for approval in approvals if approval.get("decision") == "approved"}
    for capability in {"file_read", "file_write", "subprocess"}:
        require(capability in approved, f"permission policy missing approved {capability}")


def check_trust_report() -> None:
    trust = load_json("reports/trust_report.json")
    require(trust.get("schema_version") == 1, "trust report schema_version must be 1")
    require(trust.get("package") == "jvc-analyst", "trust report package mismatch")
    actual_hash = compute_source_contract_hash()
    expected_hash = trust.get("package_sha256")
    require(expected_hash != HASH_PLACEHOLDER, "trust report package_sha256 placeholder was not replaced")
    require(expected_hash == actual_hash, f"trust report hash mismatch: expected {actual_hash}, got {expected_hash}")
    require(isinstance(trust.get("script_inventory"), list) and trust["script_inventory"], "trust report missing script inventory")
    require_text("reports/trust_report.md", expected_hash)


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


def main() -> int:
    try:
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

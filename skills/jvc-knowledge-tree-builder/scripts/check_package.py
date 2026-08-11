#!/usr/bin/env python3
"""Runnable package checks for jvc-knowledge-tree-builder."""

from __future__ import annotations

import json
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
VALIDATOR = Path(__file__).with_name("validate_output.py")
EXAMPLE = REPOSITORY / "examples" / "knowledge-tree-example"
QUARTO = shutil.which("quarto")
PDFTOPPM = shutil.which("pdftoppm")
# ponytail: Quarto 1.10 returns zero for this fixed Mermaid error card; drop the
# size check when the renderer propagates parse failures through its exit code.
MERMAID_ERROR_CARD_SIZE = (2048, 432)
OUTPUTS = {
    "knowledge_tree.md",
    "knowledge_graph.mmd",
    "nodes.json",
    "evidence_index.md",
    "open_questions.md",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_validator(package: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(package)],
        text=True,
        capture_output=True,
        check=False,
    )


def require_failure(package: Path, name: str, diagnostic: str) -> None:
    result = run_validator(package)
    require(
        result.returncode == 1 and diagnostic in result.stderr,
        f"{name}: expected {diagnostic!r}: {result.stdout}{result.stderr}",
    )


def fixture(root: Path, name: str) -> Path:
    path = root / name
    shutil.copytree(EXAMPLE, path)
    return path


def read_nodes(package: Path) -> dict[str, object]:
    return json.loads((package / "nodes.json").read_text(encoding="utf-8"))


def write_nodes(package: Path, data: dict[str, object]) -> None:
    (package / "nodes.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def check_validator() -> None:
    require(VALIDATOR.is_file(), f"missing validator: {VALIDATOR}")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        valid = fixture(root, "valid")
        result = run_validator(valid)
        require(
            result.returncode == 0 and "knowledge tree validation passed" in result.stdout,
            f"valid fixture: {result.stdout}{result.stderr}",
        )

        no_mermaid = fixture(root, "no-mermaid")
        tree = no_mermaid / "knowledge_tree.md"
        tree.write_text(tree.read_text(encoding="utf-8").replace("```{mermaid}", "```text"), encoding="utf-8")
        require_failure(no_mermaid, "no-mermaid", "knowledge_tree.md missing complete Mermaid near beginning")

        duplicate = fixture(root, "duplicate")
        data = read_nodes(duplicate)
        data["nodes"].append(dict(data["nodes"][1]))
        write_nodes(duplicate, data)
        require_failure(duplicate, "duplicate", "duplicate node id: technology")

        missing_parent = fixture(root, "missing-parent")
        data = read_nodes(missing_parent)
        data["nodes"][1]["parent_id"] = "missing"
        write_nodes(missing_parent, data)
        require_failure(missing_parent, "missing-parent", "missing parent for technology: missing")

        cycle = fixture(root, "cycle")
        data = read_nodes(cycle)
        data["nodes"][1]["parent_id"] = "delivery"
        write_nodes(cycle, data)
        require_failure(cycle, "cycle", "parent cycle")

        disconnected = fixture(root, "disconnected-ancestry")
        data = read_nodes(disconnected)
        data["nodes"].append(
            {
                "id": "disconnected-child",
                "title": "断链节点",
                "question": "这个节点能否追溯到根问题？",
                "summary": "父节点是独立开放问题。",
                "parent_id": "open-repurchase",
                "evidence_refs": [],
                "evidence_gap": "尚无证据",
                "status": "needs-evidence",
            }
        )
        write_nodes(disconnected, data)
        require_failure(
            disconnected,
            "disconnected-ancestry",
            "node ancestry does not reach root: disconnected-child",
        )

        isolated = fixture(root, "isolated")
        data = read_nodes(isolated)
        data["nodes"].append(
            {
                "id": "isolated",
                "title": "孤立节点",
                "question": "该节点应归入哪个分支？",
                "summary": "当前未挂到根问题。",
                "parent_id": None,
                "evidence_refs": ["S1"],
                "status": "source-backed",
            }
        )
        write_nodes(isolated, data)
        require_failure(isolated, "isolated", "isolated non-root node: isolated")

        relation_gap = fixture(root, "relation-gap")
        data = read_nodes(relation_gap)
        data["relations"][0]["evidence_refs"] = []
        write_nodes(relation_gap, data)
        require_failure(
            relation_gap,
            "relation-gap",
            "claimed relation missing evidence mapping: rel-technology-delivery",
        )

        evidence_bypass = fixture(root, "evidence-summary-bypass")
        index = evidence_bypass / "evidence_index.md"
        index.write_text(
            index.read_text(encoding="utf-8").replace(
                "- 映射关系：`rel-technology-delivery`",
                "- 摘要：正文提到 `rel-technology-delivery`，但没有映射字段。",
            ),
            encoding="utf-8",
        )
        require_failure(
            evidence_bypass,
            "evidence-summary-bypass",
            "evidence pointer not visible for relation rel-technology-delivery: S2",
        )

        duplicate_relation = fixture(root, "duplicate-relation")
        data = read_nodes(duplicate_relation)
        data["relations"].append(dict(data["relations"][0]))
        write_nodes(duplicate_relation, data)
        require_failure(
            duplicate_relation,
            "duplicate-relation",
            "duplicate relation id: rel-technology-delivery",
        )

        broken_relation_endpoint = fixture(root, "broken-relation-endpoint")
        data = read_nodes(broken_relation_endpoint)
        data["relations"][0]["to"] = "no-such-node"
        write_nodes(broken_relation_endpoint, data)
        require_failure(
            broken_relation_endpoint,
            "broken-relation-endpoint",
            "relation endpoint missing: rel-technology-delivery",
        )

        empty_relation_id = fixture(root, "empty-relation-id")
        data = read_nodes(empty_relation_id)
        data["relations"][0]["id"] = ""
        write_nodes(empty_relation_id, data)
        require_failure(
            empty_relation_id,
            "empty-relation-id",
            "relation id must be a non-empty string",
        )

        missing_node_field = fixture(root, "missing-node-field")
        data = read_nodes(missing_node_field)
        data["nodes"][1].pop("summary")
        write_nodes(missing_node_field, data)
        require_failure(
            missing_node_field,
            "missing-node-field",
            "node summary must be a non-empty string: technology",
        )

        missing_parent_field = fixture(root, "missing-parent-field")
        data = read_nodes(missing_parent_field)
        data["nodes"][1].pop("parent_id")
        write_nodes(missing_parent_field, data)
        require_failure(
            missing_parent_field,
            "missing-parent-field",
            "node parent_id must be null or a non-empty string: technology",
        )

        invalid_status = fixture(root, "invalid-status")
        data = read_nodes(invalid_status)
        data["nodes"][1]["status"] = "done"
        write_nodes(invalid_status, data)
        require_failure(
            invalid_status,
            "invalid-status",
            "invalid node status: technology",
        )

        missing_relation_field = fixture(root, "missing-relation-field")
        data = read_nodes(missing_relation_field)
        data["relations"][0].pop("claim")
        write_nodes(missing_relation_field, data)
        require_failure(
            missing_relation_field,
            "missing-relation-field",
            "relation claim must be a non-empty string: rel-technology-delivery",
        )

        endpoint_list = fixture(root, "endpoint-list")
        data = read_nodes(endpoint_list)
        data["relations"][0]["from"] = ["technology"]
        write_nodes(endpoint_list, data)
        require_failure(
            endpoint_list,
            "endpoint-list",
            "relation from/to must be non-empty strings: rel-technology-delivery",
        )

        missing_relations = fixture(root, "missing-relations")
        data = read_nodes(missing_relations)
        data.pop("relations")
        write_nodes(missing_relations, data)
        require_failure(
            missing_relations,
            "missing-relations",
            "nodes.json requires a non-empty relations array",
        )

        empty_relations = fixture(root, "empty-relations")
        data = read_nodes(empty_relations)
        data["relations"] = []
        write_nodes(empty_relations, data)
        require_failure(
            empty_relations,
            "empty-relations",
            "nodes.json requires a non-empty relations array",
        )

        frontmatter_fence = fixture(root, "frontmatter-fence")
        tree = frontmatter_fence / "knowledge_tree.md"
        text = tree.read_text(encoding="utf-8").replace("```{mermaid}", "```text")
        tree.write_text(
            text.replace("---\n", "---\n```{mermaid}\nflowchart LR\n```\n", 1),
            encoding="utf-8",
        )
        require_failure(
            frontmatter_fence,
            "frontmatter-fence",
            "knowledge_tree.md missing complete Mermaid near beginning",
        )

        yaml_scalar_fence = fixture(root, "yaml-scalar-frontmatter-fence")
        tree = yaml_scalar_fence / "knowledge_tree.md"
        text = tree.read_text(encoding="utf-8").replace("```{mermaid}", "```text")
        tree.write_text(
            text.replace(
                "---\n",
                "---\nfake_diagram: |\n  ---\n  ```{mermaid}\n  flowchart LR\n  ```\n",
                1,
            ),
            encoding="utf-8",
        )
        require_failure(
            yaml_scalar_fence,
            "yaml-scalar-frontmatter-fence",
            "knowledge_tree.md missing complete Mermaid near beginning",
        )

        unclosed_fence = fixture(root, "unclosed-fence")
        tree = unclosed_fence / "knowledge_tree.md"
        tree.write_text(
            tree.read_text(encoding="utf-8").replace(
                '  technology -. "影响" .-> delivery\n```\n',
                '  technology -. "影响" .-> delivery\n',
            ),
            encoding="utf-8",
        )
        require_failure(
            unclosed_fence,
            "unclosed-fence",
            "knowledge_tree.md Mermaid fence is not closed",
        )

        bad_tree_declaration = fixture(root, "bad-tree-declaration")
        tree = bad_tree_declaration / "knowledge_tree.md"
        tree.write_text(
            tree.read_text(encoding="utf-8").replace("flowchart LR\n", "flowchart LR garbage\n", 1),
            encoding="utf-8",
        )
        require_failure(
            bad_tree_declaration,
            "bad-tree-declaration",
            "knowledge_tree.md Mermaid block missing supported graph declaration",
        )

        bad_graph_declaration = fixture(root, "bad-graph-declaration")
        graph = bad_graph_declaration / "knowledge_graph.mmd"
        graph.write_text(
            graph.read_text(encoding="utf-8").replace("flowchart LR\n", "flowchart LR garbage\n", 1),
            encoding="utf-8",
        )
        require_failure(
            bad_graph_declaration,
            "bad-graph-declaration",
            "knowledge_graph.mmd missing supported graph declaration",
        )

        frontmatter_evidence = fixture(root, "frontmatter-evidence")
        index = frontmatter_evidence / "evidence_index.md"
        text = index.read_text(encoding="utf-8")
        s1_start = text.index("## S1")
        s2_start = text.index("## S2")
        index.write_text(
            "---\n"
            + text[s1_start:s2_start]
            + "---\n\n"
            + text[:s1_start]
            + text[s2_start:],
            encoding="utf-8",
        )
        require_failure(
            frontmatter_evidence,
            "frontmatter-evidence",
            "evidence pointer not visible for node root: S1",
        )

        extra = fixture(root, "extra")
        (extra / "extra.md").write_text("extra\n", encoding="utf-8")
        require_failure(extra, "extra", "package must contain exactly five files")

        empty = fixture(root, "empty")
        (empty / "open_questions.md").write_text("", encoding="utf-8")
        require_failure(empty, "empty", "required file is empty: open_questions.md")


def check_package_contract() -> None:
    required = [
        "SKILL.md",
        "README.md",
        "agents/interface.yaml",
        "manifest.json",
        "references/output-contract.md",
        "scripts/collect_sources.py",
        "scripts/validate_output.py",
    ]
    require(not [path for path in required if not (ROOT / path).is_file()], "missing package files")

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    require(set(manifest.get("output_contract", [])) == OUTPUTS, "manifest output contract must be exactly five files")
    require(manifest.get("maturity_tier") == "production", "manifest maturity must be production")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    contract = (ROOT / "references" / "output-contract.md").read_text(encoding="utf-8")
    for needle in ("visual-first", "landscape.md", "derived_from_claim_ids", "用户批准", "validate_output.py"):
        require(needle in skill, f"SKILL.md missing: {needle}")
    for needle in ("恰好五个文件", "parent cycle", "open-question", "claimed relation"):
        require(needle in contract, f"output contract missing: {needle}")

    profiles = REPOSITORY / "skills" / "jvc-research-core" / "profiles"
    track = json.loads((profiles / "jvc-track-research.json").read_text(encoding="utf-8"))
    knowledge = json.loads((profiles / "jvc-knowledge-tree-builder.json").read_text(encoding="utf-8"))
    require("source" in track["current_skill_record_types"], "Track Research must create current sources")
    require("source" in knowledge["required_record_types"], "Knowledge Tree requires an effective source")
    require("source" not in knowledge["current_skill_record_types"], "Knowledge Tree must not require a duplicate source")
    require("claim" in knowledge["current_skill_record_types"], "Knowledge Tree must create current claims")


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    require(header.startswith(b"\x89PNG\r\n\x1a\n"), f"not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def quarto_render(source: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], bool]:
    result = subprocess.run(
        [str(QUARTO), "render", str(source), "--to", "typst", "--output-dir", str(output)],
        text=True,
        capture_output=True,
        check=False,
    )
    error_card = any(
        png_dimensions(path) == MERMAID_ERROR_CARD_SIZE
        for path in source.parent.rglob("mermaid-figure-*.png")
    )
    return result, error_card


def render_mermaid() -> None:
    require(QUARTO is not None, "missing local Quarto renderer on PATH")
    require(PDFTOPPM is not None, "missing local Poppler pdftoppm on PATH")
    require(EXAMPLE.is_dir(), f"missing tracked example: {EXAMPLE}")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        tree_root = root / "tree"
        tree_root.mkdir()
        source = tree_root / "knowledge_tree.qmd"
        source.write_text((EXAMPLE / "knowledge_tree.md").read_text(encoding="utf-8"), encoding="utf-8")
        output = tree_root / "rendered"
        rendered, error_card = quarto_render(source, output)
        require(
            rendered.returncode == 0 and not error_card,
            f"valid knowledge_tree Mermaid render failed: {rendered.stdout}{rendered.stderr}",
        )
        pdf = output / "knowledge_tree.pdf"
        require(pdf.is_file() and pdf.stat().st_size, "valid Mermaid render produced no PDF")
        pages = subprocess.run(
            [str(PDFTOPPM), "-png", "-r", "110", str(pdf), str(tree_root / "page")],
            text=True,
            capture_output=True,
            check=False,
        )
        require(pages.returncode == 0 and list(tree_root.glob("page-*.png")), "PDF page conversion failed")

        graph_root = root / "graph"
        graph_root.mkdir()
        graph_source = graph_root / "knowledge_graph.qmd"
        graph_source.write_text(
            "# Knowledge Graph\n\n```{mermaid}\n"
            + (EXAMPLE / "knowledge_graph.mmd").read_text(encoding="utf-8")
            + "```\n",
            encoding="utf-8",
        )
        graph_rendered, graph_error = quarto_render(graph_source, graph_root / "output")
        require(
            graph_rendered.returncode == 0 and not graph_error,
            f"valid knowledge_graph.mmd render failed: {graph_rendered.stdout}{graph_rendered.stderr}",
        )

        malformed_root = root / "malformed"
        malformed_root.mkdir()
        malformed_graph = malformed_root / "knowledge_graph.mmd"
        malformed_graph.write_text("flowchart TD\n  A -->|label B\n", encoding="utf-8")
        malformed = malformed_root / "knowledge_graph.qmd"
        malformed.write_text(
            "# Malformed Knowledge Graph\n\n```{mermaid}\n"
            + malformed_graph.read_text(encoding="utf-8")
            + "```\n",
            encoding="utf-8",
        )
        rejected, error_card = quarto_render(malformed, malformed_root / "output")
        require(
            rejected.returncode != 0 or error_card,
            "malformed knowledge_graph.mmd was not rejected by local Quarto render",
        )


def main() -> int:
    check_package_contract()
    check_validator()
    tracked = run_validator(EXAMPLE)
    require(tracked.returncode == 0, f"tracked example: {tracked.stdout}{tracked.stderr}")
    render_mermaid()
    print("jvc-knowledge-tree-builder package check passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"package check failed: {error}", file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
"""End-to-end contract checks for dealflowctl.py."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("dealflowctl.py")
PACKAGE = Path(__file__).resolve().parents[1]


def check_orchestration_contract() -> None:
    skill = (PACKAGE / "SKILL.md").read_text(encoding="utf-8")
    contract = (PACKAGE / "references" / "workflow-contract.md").read_text(
        encoding="utf-8"
    )
    assert "唯一项目总控" in skill
    assert "项目身份、状态、依赖、最小调度、增量重跑和人工闸门" in skill
    assert "不解析或重算专业研究" in skill
    assert "不推进业务阶段" in skill
    assert "新增来源事件不得自动调用 Skill 或推进阶段" in contract
    for edge in (
        "`jvc-track-research` → `jvc-knowledge-tree-builder`",
        "`jvc-track-research` → `jvc-market-sizing`",
        "项目产物 → `jvc-ic-memo`",
        "赛道产物 → `jvc-research-report`",
    ):
        assert edge in contract


def run(*args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        (sys.executable, str(SCRIPT), *args),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"{' '.join(args)} returned {result.returncode}, expected {expect}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def load_json_output(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(result.stdout)


def read_state_axes(project_dir: Path) -> dict[str, str]:
    lines = (project_dir / "STATE.md").read_text(encoding="utf-8").splitlines()
    axes: dict[str, str] = {}
    for key in ("workflow_stage", "research_level", "lifecycle_status"):
        prefix = f"- {key}：`"
        line = next(item for item in lines if item.startswith(prefix))
        axes[key] = line.removeprefix(prefix).removesuffix("`")
    return axes


def check_init_and_deduplicate(root: Path) -> Path:
    first = load_json_output(
        run("init", "--library-root", str(root), "--project-name", "和光智成")
    )
    project_dir = Path(str(first["project_dir"]))
    assert first["existing"] is False
    assert project_dir.is_dir()
    assert (root / ".jvc-library.json").is_file()
    assert (project_dir / ".jvc" / "project_events.jsonl").is_file()
    assert (project_dir / "STATE.md").is_file()
    assert (project_dir / "CHANGELOG.md").is_file()
    assert (root / "PROJECTS.md").is_file()

    second = load_json_output(
        run("init", "--library-root", str(root), "--project-name", "和光智成")
    )
    assert second["existing"] is True
    assert second["project_id"] == first["project_id"]
    by_id = load_json_output(
        run(
            "init",
            "--library-root",
            str(root),
            "--project-name",
            "名称提示可忽略",
            "--project-id",
            str(first["project_id"]),
        )
    )
    assert by_id["existing"] is True
    assert by_id["project_dir"] == first["project_dir"]
    run(
        "init",
        "--library-root",
        str(root),
        "--project-name",
        "和光智成科技",
        expect=2,
    )
    events = (project_dir / ".jvc" / "project_events.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()
    assert len(events) == 1
    return project_dir


def write_event(root: Path, name: str, payload: dict[str, object]) -> Path:
    path = root / name
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path


def check_source_event_is_idempotent(root: Path, project_dir: Path) -> None:
    source = root / "source.docx"
    source.write_bytes(b"fixture")
    payload = {
        "event_id": "evt_source_1",
        "event_type": "source_registered",
        "actor": "codex",
        "trigger": "用户提供访谈",
        "reason": "登记新的只读来源",
        "input_refs": [{"path": str(source)}],
        "to": {},
    }
    event_input = write_event(root, "source-event.json", payload)
    first = load_json_output(
        run(
            "event",
            "--project-dir",
            str(project_dir),
            "--input",
            str(event_input),
        )
    )
    second = load_json_output(
        run(
            "event",
            "--project-dir",
            str(project_dir),
            "--input",
            str(event_input),
        )
    )
    assert first["appended"] is True
    assert second["appended"] is False
    duplicate_payload = dict(payload)
    duplicate_payload["event_id"] = "evt_source_same_content"
    duplicate_input = write_event(root, "source-same-content.json", duplicate_payload)
    duplicate = load_json_output(
        run(
            "event",
            "--project-dir",
            str(project_dir),
            "--input",
            str(duplicate_input),
        )
    )
    assert duplicate["appended"] is False
    assert duplicate["event_id"] == "evt_source_1"
    invalid_supersede = {
        "event_id": "evt_source_bad_supersede",
        "event_type": "source_superseded",
        "actor": "codex",
        "reason": "替代不存在的来源事件",
        "input_refs": [{"path": str(source)}],
        "supersedes": "evt_does_not_exist",
        "to": {},
    }
    invalid_supersede_input = write_event(
        root, "source-bad-supersede.json", invalid_supersede
    )
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(invalid_supersede_input),
        expect=2,
    )
    events = [
        json.loads(line)
        for line in (project_dir / ".jvc" / "project_events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(events) == 2
    assert events[-1]["input_refs"][0]["sha256"].startswith("sha256:")


def append_payload(
    root: Path,
    project_dir: Path,
    event_id: str,
    event_type: str,
    *,
    source: dict[str, object],
    target: dict[str, object],
    approval_ref: str | None = None,
    actor: str = "codex",
    expect: int = 0,
) -> subprocess.CompletedProcess[str]:
    payload: dict[str, object] = {
        "event_id": event_id,
        "event_type": event_type,
        "actor": actor,
        "reason": f"fixture {event_type}",
        "from": source,
        "to": target,
    }
    if approval_ref is not None:
        payload["approval_ref"] = approval_ref
    path = write_event(root, f"{event_id}.json", payload)
    return run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(path),
        expect=expect,
    )


def check_state_machine_and_gate(root: Path, project_dir: Path) -> None:
    event_file = project_dir / ".jvc" / "project_events.jsonl"
    before = len(event_file.read_text(encoding="utf-8").splitlines())
    append_payload(
        root,
        project_dir,
        "evt_illegal_jump",
        "workflow_transitioned",
        source={"workflow_stage": "intake"},
        target={"workflow_stage": "diligence"},
        expect=2,
    )
    assert len(event_file.read_text(encoding="utf-8").splitlines()) == before

    append_payload(
        root,
        project_dir,
        "evt_level_l1",
        "research_level_changed",
        source={"research_level": "L0"},
        target={"research_level": "L1"},
        approval_ref="user:approve:L1",
        actor="user",
    )
    for event_id, source_stage, target_stage in (
        ("evt_stage_data", "intake", "data_layer"),
        ("evt_stage_invest", "data_layer", "invest_memo"),
        ("evt_stage_pre_dd", "invest_memo", "pre_dd_review"),
    ):
        append_payload(
            root,
            project_dir,
            event_id,
            "workflow_transitioned",
            source={"workflow_stage": source_stage},
            target={"workflow_stage": target_stage},
        )
    append_payload(
        root,
        project_dir,
        "evt_gate_request",
        "gate_requested",
        source={"current_gate": None},
        target={
            "current_gate": "pre_dd_review",
            "lifecycle_status": "paused",
        },
    )
    append_payload(
        root,
        project_dir,
        "evt_gate_approve",
        "gate_decided",
        source={"current_gate": "pre_dd_review"},
        target={
            "current_gate": None,
            "lifecycle_status": "active",
            "last_approved_gate": "pre_dd_review",
            "last_gate_decision": "approve",
        },
        approval_ref="user:approve:pre_dd_review",
        actor="user",
    )
    append_payload(
        root,
        project_dir,
        "evt_level_l2",
        "research_level_changed",
        source={"research_level": "L1"},
        target={"research_level": "L2"},
        approval_ref="user:approve:L2",
        actor="user",
    )
    append_payload(
        root,
        project_dir,
        "evt_stage_dd",
        "workflow_transitioned",
        source={"workflow_stage": "pre_dd_review"},
        target={"workflow_stage": "diligence"},
        approval_ref="user:approve:pre_dd_review",
    )
    state = (project_dir / "STATE.md").read_text(encoding="utf-8")
    assert "workflow_stage：`diligence`" in state
    assert "research_level：`L2`" in state
    assert "lifecycle_status：`active`" in state
    append_payload(
        root,
        project_dir,
        "evt_early_decision",
        "decision_recorded",
        source={"decision_status": "undecided"},
        target={"decision_status": "invest"},
        approval_ref="user:decision:invest",
        actor="user",
        expect=2,
    )
    append_payload(
        root,
        project_dir,
        "evt_invalid_reconcile",
        "project_reconciled",
        source={},
        target={
            "workflow_stage": "ic_review",
            "research_level": "L0",
            "current_gate": "pre_dd_review",
            "lifecycle_status": "active",
        },
        approval_ref="user:reconcile:invalid",
        actor="user",
        expect=2,
    )


def check_artifact_staleness(root: Path, project_dir: Path) -> None:
    artifact = project_dir / "INVEST_MEMO.md"
    artifact.write_text("# Invest Memo\n", encoding="utf-8")
    outside = root / "outside.md"
    outside.write_text("# outside\n", encoding="utf-8")
    outside_event = {
        "event_id": "evt_artifact_outside",
        "event_type": "artifact_created",
        "actor": "codex",
        "reason": "不得登记项目目录外的输出",
        "output_refs": [
            {
                "path": str(outside),
                "producer": "jvc-deal-flow",
                "depends_on": [],
            }
        ],
        "to": {},
    }
    outside_input = write_event(root, "artifact-outside.json", outside_event)
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(outside_input),
        expect=2,
    )
    created = {
        "event_id": "evt_artifact_created",
        "event_type": "artifact_created",
        "actor": "codex",
        "reason": "生成尽调前工作备忘录",
        "input_refs": [{"event_id": "evt_source_1"}],
        "output_refs": [
            {
                "path": "INVEST_MEMO.md",
                "producer": "jvc-deal-flow",
                "depends_on": ["evt_source_1"],
            }
        ],
        "to": {"next_action": "等待新证据"},
    }
    created_input = write_event(root, "artifact-created.json", created)
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(created_input),
    )
    incomplete_replay = dict(created)
    incomplete_replay.pop("to")
    incomplete_replay_input = write_event(
        root, "artifact-created-incomplete-replay.json", incomplete_replay
    )
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(incomplete_replay_input),
        expect=2,
    )
    valid_audit = {
        "event_id": "evt_artifact_valid_audit",
        "event_type": "artifact_audited",
        "actor": "codex",
        "reason": "登记指纹与工件一致后记录审查",
        "output_refs": [{"path": "INVEST_MEMO.md"}],
        "to": {"research_status": "partial"},
    }
    valid_audit_input = write_event(root, "artifact-valid-audit.json", valid_audit)
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(valid_audit_input),
    )
    assert "`audited`" in (project_dir / "STATE.md").read_text(encoding="utf-8")
    duplicate_audit = dict(valid_audit)
    duplicate_audit["event_id"] = "evt_artifact_valid_audit_duplicate"
    duplicate_audit_input = write_event(
        root, "artifact-valid-audit-duplicate.json", duplicate_audit
    )
    duplicate_audit_result = load_json_output(
        run(
            "event",
            "--project-dir",
            str(project_dir),
            "--input",
            str(duplicate_audit_input),
        )
    )
    assert duplicate_audit_result["appended"] is False
    assert duplicate_audit_result["event_id"] == "evt_artifact_valid_audit"
    artifact.write_text("# manually changed\n", encoding="utf-8")
    invalid_audit = {
        "event_id": "evt_artifact_invalid_audit",
        "event_type": "artifact_audited",
        "actor": "codex",
        "reason": "漂移工件不得直接通过审查",
        "output_refs": [{"path": "INVEST_MEMO.md"}],
        "to": {"research_status": "ready"},
    }
    invalid_audit_input = write_event(
        root, "artifact-invalid-audit.json", invalid_audit
    )
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(invalid_audit_input),
        expect=2,
    )
    dedicated_old_source = root / "dedicated-old-source.pdf"
    dedicated_old_source.write_bytes(b"dedicated old fixture")
    dedicated_old_source_input = write_event(
        root,
        "dedicated-old-source-event.json",
        {
            "event_id": "evt_source_dedicated_old",
            "event_type": "source_registered",
            "actor": "codex",
            "reason": "登记目标工件的测试专用旧来源",
            "input_refs": [{"path": str(dedicated_old_source)}],
            "to": {},
        },
    )
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(dedicated_old_source_input),
    )
    affected_artifact = project_dir / "AFFECTED.md"
    affected_artifact.write_text("# Affected\n", encoding="utf-8")
    unrelated_artifact = project_dir / "UNAFFECTED.md"
    unrelated_artifact.write_text("# Unaffected\n", encoding="utf-8")
    for event_id, artifact_path, dependency in (
        ("evt_affected_created", "AFFECTED.md", "evt_source_dedicated_old"),
        ("evt_unaffected_created", "UNAFFECTED.md", "evt_source_1"),
    ):
        artifact_input = write_event(
            root,
            f"{event_id}.json",
            {
                "event_id": event_id,
                "event_type": "artifact_created",
                "actor": "codex",
                "reason": "建立显式依赖范围测试工件",
                "input_refs": [{"event_id": dependency}],
                "output_refs": [
                    {
                        "path": artifact_path,
                        "producer": "fixture-skill",
                        "depends_on": [dependency],
                    }
                ],
                "to": {},
            },
        )
        run(
            "event",
            "--project-dir",
            str(project_dir),
            "--input",
            str(artifact_input),
        )
    state_before_replacement = (project_dir / "STATE.md").read_text(encoding="utf-8")
    assert "| AFFECTED.md | `current` |" in state_before_replacement
    assert "| UNAFFECTED.md | `current` |" in state_before_replacement
    state_axes_before_incremental = read_state_axes(project_dir)
    before_incremental = [
        json.loads(line)
        for line in (project_dir / ".jvc" / "project_events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    replacement_source = root / "replacement-source.pdf"
    replacement_source.write_bytes(b"replacement fixture")
    replacement_input = write_event(
        root,
        "replacement-source-event.json",
        {
            "event_id": "evt_source_replacement",
            "event_type": "source_superseded",
            "actor": "codex",
            "reason": "替换目标工件依赖的旧来源",
            "input_refs": [{"path": str(replacement_source)}],
            "supersedes": "evt_source_dedicated_old",
            "to": {},
        },
    )
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(replacement_input),
    )
    after_source = [
        json.loads(line)
        for line in (project_dir / ".jvc" / "project_events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(after_source) == len(before_incremental) + 1
    assert after_source[-1]["event_type"] == "source_superseded"
    assert after_source[-1]["to"] == {}
    assert read_state_axes(project_dir) == state_axes_before_incremental
    state_after_source = (project_dir / "STATE.md").read_text(encoding="utf-8")
    assert "| AFFECTED.md | `current` |" in state_after_source
    assert "| UNAFFECTED.md | `current` |" in state_after_source
    stale = {
        "event_id": "evt_artifact_stale",
        "event_type": "artifact_marked_stale",
        "actor": "codex",
        "reason": "新访谈反驳 H2",
        "input_refs": [{"event_id": "evt_source_replacement"}],
        "output_refs": [{"path": "AFFECTED.md"}],
        "to": {"next_action": "用户批准后重跑 AFFECTED.md"},
    }
    stale_input = write_event(root, "artifact-stale.json", stale)
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(stale_input),
    )
    state = (project_dir / "STATE.md").read_text(encoding="utf-8")
    assert "| AFFECTED.md | `stale` |" in state
    assert "| UNAFFECTED.md | `current` |" in state
    assert "用户批准后重跑 AFFECTED.md" in state
    assert read_state_axes(project_dir) == state_axes_before_incremental
    after_stale = [
        json.loads(line)
        for line in (project_dir / ".jvc" / "project_events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert [event["event_type"] for event in after_stale[-2:]] == [
        "source_superseded",
        "artifact_marked_stale",
    ]
    assert all(
        event["event_type"]
        not in {"workflow_transitioned", "research_level_changed", "lifecycle_changed"}
        for event in after_stale[len(before_incremental) :]
    )
    restored_input = write_event(
        root,
        "affected-restored.json",
        {
            "event_id": "evt_affected_restored",
            "event_type": "artifact_updated",
            "actor": "codex",
            "reason": "完成用例后恢复工件 current 状态",
            "input_refs": [{"event_id": "evt_source_replacement"}],
            "output_refs": [
                {
                    "path": "AFFECTED.md",
                    "producer": "fixture-skill",
                    "depends_on": ["evt_source_replacement"],
                }
            ],
            "to": {},
        },
    )
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(restored_input),
        expect=2,
    )
    restored_payload = json.loads(restored_input.read_text(encoding="utf-8"))
    restored_payload["approval_ref"] = "user:approve:rerun-affected"
    restored_input = write_event(
        root,
        "affected-restored-approved.json",
        restored_payload,
    )
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(restored_input),
    )
    restored_state = (project_dir / "STATE.md").read_text(encoding="utf-8")
    assert "| AFFECTED.md | `current` |" in restored_state
    assert "| UNAFFECTED.md | `current` |" in restored_state
    run("check", "--project-dir", str(project_dir), expect=2)
    artifact.write_text("# Invest Memo\n", encoding="utf-8")
    run("check", "--project-dir", str(project_dir))


def check_view_recovery_and_drift(root: Path, project_dir: Path) -> None:
    state_path = project_dir / "STATE.md"
    state_path.unlink()
    result = load_json_output(run("check", "--project-dir", str(project_dir)))
    assert "STATE.md" in result["views_rebuilt"]
    assert state_path.is_file()

    stale_state = state_path.read_text(encoding="utf-8")
    artifact = project_dir / "INVEST_MEMO.md"
    artifact.write_text("# Invest Memo updated\n", encoding="utf-8")
    update_payload = {
        "event_id": "evt_artifact_updated",
        "event_type": "artifact_updated",
        "actor": "codex",
        "reason": "用户批准后局部重跑",
        "input_refs": [{"event_id": "evt_source_1"}],
        "output_refs": [
            {
                "path": "INVEST_MEMO.md",
                "producer": "jvc-deal-flow",
                "depends_on": ["evt_source_1"],
            }
        ],
        "to": {"next_action": "复核更新后的 Invest Memo"},
    }
    update_input = write_event(root, "artifact-updated.json", update_payload)
    run(
        "event",
        "--project-dir",
        str(project_dir),
        "--input",
        str(update_input),
    )
    duplicate_update = dict(update_payload)
    duplicate_update["event_id"] = "evt_artifact_updated_duplicate"
    duplicate_update_input = write_event(
        root, "artifact-updated-duplicate.json", duplicate_update
    )
    duplicate_result = load_json_output(
        run(
            "event",
            "--project-dir",
            str(project_dir),
            "--input",
            str(duplicate_update_input),
        )
    )
    assert duplicate_result["appended"] is False
    assert duplicate_result["event_id"] == "evt_artifact_updated"
    state_path.write_text(stale_state, encoding="utf-8")
    recovered = load_json_output(run("check", "--project-dir", str(project_dir)))
    assert "STATE.md" in recovered["views_rebuilt"]
    assert state_path.read_text(encoding="utf-8") != stale_state

    changelog = project_dir / "CHANGELOG.md"
    tampered = changelog.read_text(encoding="utf-8") + "\n手工改写\n"
    changelog.write_text(tampered, encoding="utf-8")
    run("check", "--project-dir", str(project_dir), expect=2)
    assert changelog.read_text(encoding="utf-8") == tampered
    changelog.unlink()
    repaired = load_json_output(run("check", "--project-dir", str(project_dir)))
    assert "CHANGELOG.md" in repaired["views_rebuilt"]

    listing = run("list", "--library-root", str(root)).stdout
    assert "| 和光智成 |" in listing
    assert listing == (root / "PROJECTS.md").read_text(encoding="utf-8")


def check_library_lock_prevents_duplicate_names(root: Path) -> None:
    project_dirs: list[Path] = []
    event_inputs: list[Path] = []
    for index, name in enumerate(("甲舟科技", "乙星材料"), start=1):
        initialized = load_json_output(
            run("init", "--library-root", str(root), "--project-name", name)
        )
        project_dirs.append(Path(str(initialized["project_dir"])))
        event_inputs.append(
            write_event(
                root,
                f"concurrent-rename-{index}.json",
                {
                    "event_id": f"evt_concurrent_rename_{index}",
                    "event_type": "project_renamed",
                    "actor": "user",
                    "reason": "并发改名不得破坏项目库唯一性",
                    "from": {"project_name": name},
                    "to": {"project_name": "并发同名项目"},
                    "approval_ref": f"user:rename:concurrent:{index}",
                },
            )
        )
    processes = [
        subprocess.Popen(
            (
                sys.executable,
                str(SCRIPT),
                "event",
                "--project-dir",
                str(project_dir),
                "--input",
                str(event_input),
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for project_dir, event_input in zip(project_dirs, event_inputs)
    ]
    results = [process.communicate() + (process.returncode,) for process in processes]
    return_codes = sorted(result[2] for result in results)
    assert return_codes == [0, 2], results
    listing = run("list", "--library-root", str(root)).stdout
    assert listing.count("| 并发同名项目 |") == 1


def check_reconcile_invalidates_gate_approval(root: Path) -> None:
    initialized = load_json_output(
        run("init", "--library-root", str(root), "--project-name", "闸门失效样例")
    )
    project_dir = Path(str(initialized["project_dir"]))
    for level, previous in (("L1", "L0"), ("L2", "L1")):
        append_payload(
            root,
            project_dir,
            f"evt_reconcile_level_{level.lower()}",
            "research_level_changed",
            source={"research_level": previous},
            target={"research_level": level},
            approval_ref=f"user:approve:{level}",
            actor="user",
        )
    for event_id, source_stage, target_stage in (
        ("evt_reconcile_stage_data", "intake", "data_layer"),
        ("evt_reconcile_stage_invest", "data_layer", "invest_memo"),
        ("evt_reconcile_stage_pre_dd", "invest_memo", "pre_dd_review"),
    ):
        append_payload(
            root,
            project_dir,
            event_id,
            "workflow_transitioned",
            source={"workflow_stage": source_stage},
            target={"workflow_stage": target_stage},
        )
    append_payload(
        root,
        project_dir,
        "evt_reconcile_gate_request",
        "gate_requested",
        source={"current_gate": None},
        target={
            "current_gate": "pre_dd_review",
            "lifecycle_status": "paused",
        },
    )
    append_payload(
        root,
        project_dir,
        "evt_reconcile_gate_approve",
        "gate_decided",
        source={"current_gate": "pre_dd_review"},
        target={
            "current_gate": None,
            "lifecycle_status": "active",
            "last_approved_gate": "pre_dd_review",
            "last_gate_decision": "approve",
        },
        approval_ref="user:approve:old-pre-dd",
        actor="user",
    )
    append_payload(
        root,
        project_dir,
        "evt_reconcile_back_to_data",
        "project_reconciled",
        source={"workflow_stage": "pre_dd_review"},
        target={"workflow_stage": "data_layer"},
        approval_ref="user:reconcile:back-to-data",
        actor="user",
    )
    for event_id, source_stage, target_stage in (
        ("evt_reconcile_again_invest", "data_layer", "invest_memo"),
        ("evt_reconcile_again_pre_dd", "invest_memo", "pre_dd_review"),
    ):
        append_payload(
            root,
            project_dir,
            event_id,
            "workflow_transitioned",
            source={"workflow_stage": source_stage},
            target={"workflow_stage": target_stage},
        )
    append_payload(
        root,
        project_dir,
        "evt_reconcile_reuse_old_gate",
        "workflow_transitioned",
        source={"workflow_stage": "pre_dd_review"},
        target={"workflow_stage": "diligence"},
        approval_ref="user:approve:old-pre-dd",
        expect=2,
    )


def check_legacy_attach_and_corruption(root: Path) -> None:
    legacy_dir = root / "projects" / "Legacy项目"
    legacy_dir.mkdir(parents=True)
    legacy_artifact = legacy_dir / "01-prescreen.md"
    legacy_artifact.write_text("# existing\n", encoding="utf-8")
    result = load_json_output(
        run("init", "--library-root", str(root), "--project-name", "Legacy项目")
    )
    assert Path(str(result["project_dir"])) == legacy_dir.resolve()
    assert legacy_artifact.read_text(encoding="utf-8") == "# existing\n"

    listing = run("list", "--library-root", str(root)).stdout
    assert "| Legacy项目 |" in listing
    append_payload(
        root,
        legacy_dir,
        "evt_legacy_rename",
        "project_renamed",
        source={"project_name": "Legacy项目"},
        target={
            "project_name": "Legacy重命名",
            "aliases": ["Legacy项目"],
        },
        approval_ref="user:rename:legacy",
        actor="user",
    )
    append_payload(
        root,
        legacy_dir,
        "evt_legacy_stage_data",
        "workflow_transitioned",
        source={"workflow_stage": "intake"},
        target={"workflow_stage": "data_layer"},
    )
    events_path = legacy_dir / ".jvc" / "project_events.jsonl"
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
    ]
    valid_events = json.loads(json.dumps(events))
    events[2]["to"]["workflow_stage"] = "diligence"
    unsigned = dict(events[2])
    unsigned.pop("event_hash")
    canonical = json.dumps(
        unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    events[2]["event_hash"] = (
        "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    )
    events_path.write_text(
        "\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n",
        encoding="utf-8",
    )
    state_before = (legacy_dir / "STATE.md").read_text(encoding="utf-8")
    run("check", "--project-dir", str(legacy_dir), expect=2)
    assert (legacy_dir / "STATE.md").read_text(encoding="utf-8") == state_before

    events = valid_events
    events[0]["event_hash"] = "sha256:" + ("0" * 64)
    events_path.write_text(
        "\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n",
        encoding="utf-8",
    )
    run("check", "--project-dir", str(legacy_dir), expect=2)
    assert (legacy_dir / "STATE.md").read_text(encoding="utf-8") == state_before


def main() -> int:
    check_orchestration_contract()
    with tempfile.TemporaryDirectory(prefix="jvc-deal-flow-") as temporary:
        root = Path(temporary)
        project_dir = check_init_and_deduplicate(root)
        check_source_event_is_idempotent(root, project_dir)
        check_state_machine_and_gate(root, project_dir)
        check_artifact_staleness(root, project_dir)
        check_view_recovery_and_drift(root, project_dir)
        check_library_lock_prevents_duplicate_names(root)
        check_reconcile_invalidates_gate_approval(root)
        check_legacy_attach_and_corruption(root)
    print("jvc-deal-flow package checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Deterministic local project state for jvc-deal-flow."""

from __future__ import annotations

import argparse
import contextlib
import difflib
import hashlib
import json
import os
import re
import sys
import unicodedata
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = "1.0"
PRODUCER = "jvc-deal-flow"
EVENT_FILE = Path(".jvc/project_events.jsonl")
GENERATED_NOTICE = "> 自动生成，请通过 `jvc-deal-flow` 更新。"
VIEW_MARKER_RE = re.compile(r"<!-- jvc-deal-flow:[^=]+=(.*?) -->")
EVENT_TYPES = {
    "project_initialized",
    "project_renamed",
    "source_registered",
    "source_superseded",
    "artifact_created",
    "artifact_updated",
    "artifact_marked_stale",
    "artifact_audited",
    "workflow_transitioned",
    "research_level_changed",
    "lifecycle_changed",
    "gate_requested",
    "gate_decided",
    "decision_recorded",
    "error_recorded",
    "project_reconciled",
}
WORKFLOW_TRANSITIONS = {
    "intake": {"data_layer"},
    "data_layer": {"invest_memo"},
    "invest_memo": {"data_layer", "pre_dd_review"},
    "pre_dd_review": {"data_layer", "invest_memo", "diligence"},
    "diligence": {"post_dd_review"},
    "post_dd_review": {"diligence", "insight_layer"},
    "insight_layer": {"diligence", "ic_memo"},
    "ic_memo": {"insight_layer", "ic_review"},
    "ic_review": {"insight_layer", "ic_memo", "decision_record"},
    "decision_record": set(),
}
LEVELS = ("L0", "L1", "L2", "L3")
LIFECYCLES = {"active", "paused", "closed", "archived"}
RESEARCH_STATUSES = {"not_audited", "ready", "partial", "blocked"}
DECISION_STATUSES = {"undecided", "invest", "pass", "wait"}
GATES = {"pre_dd_review", "post_dd_review", "ic_review"}
EVENT_INPUT_FIELDS = {
    "schema_version",
    "event_id",
    "occurred_at",
    "actor",
    "event_type",
    "run_id",
    "trigger",
    "reason",
    "from",
    "to",
    "input_refs",
    "output_refs",
    "approval_ref",
    "supersedes",
}


class DealFlowError(Exception):
    """Expected operator-facing failure."""


def canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def markdown_cell(value: object) -> str:
    return str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextlib.contextmanager
def exclusive_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+b")
    backend = ""
    try:
        try:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            backend = "fcntl"
        except ImportError:
            import msvcrt

            try:
                if path.stat().st_size == 0:
                    handle.write(b"\0")
                    handle.flush()
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                backend = "msvcrt"
            except OSError as exc:
                raise DealFlowError(f"another writer holds {path}") from exc
        except (BlockingIOError, OSError) as exc:
            raise DealFlowError(f"another writer holds {path}") from exc
        yield
    finally:
        try:
            if backend == "fcntl":
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            elif backend == "msvcrt":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        handle.close()


def normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"[\W_]+", "", normalized, flags=re.UNICODE)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    slug = re.sub(r"[^\w-]+", "-", normalized, flags=re.UNICODE)
    slug = re.sub(r"[-_]+", "-", slug).strip("-")
    return slug or "project"


def minimum_level_for_stage(stage: object) -> str:
    return {
        "invest_memo": "L1",
        "diligence": "L2",
        "post_dd_review": "L2",
        "insight_layer": "L2",
        "ic_memo": "L3",
        "ic_review": "L3",
        "decision_record": "L3",
    }.get(str(stage), "L0")


def marker_path(library_root: Path) -> Path:
    return library_root / ".jvc-library.json"


def ensure_library(library_root: Path) -> Path:
    library_root.mkdir(parents=True, exist_ok=True)
    marker = marker_path(library_root)
    expected = {"schema_version": SCHEMA_VERSION, "projects_dir": "projects"}
    if marker.exists():
        try:
            actual = json.loads(marker.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DealFlowError(f"invalid library marker: {marker}") from exc
        if actual != expected:
            raise DealFlowError(f"unsupported library marker: {marker}")
    else:
        atomic_write(marker, json.dumps(expected, ensure_ascii=False, indent=2) + "\n")
    projects_dir = library_root / "projects"
    projects_dir.mkdir(exist_ok=True)
    return projects_dir


def event_path(project_dir: Path) -> Path:
    return project_dir / EVENT_FILE


def load_events(project_dir: Path) -> list[dict[str, Any]]:
    path = event_path(project_dir)
    if not path.is_file():
        raise DealFlowError(f"missing project event chain: {path}")
    events: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise DealFlowError(
                f"invalid JSON at {path}:{line_number}"
            ) from exc
        if not isinstance(event, dict):
            raise DealFlowError(f"event must be an object at {path}:{line_number}")
        events.append(event)
    if not events:
        raise DealFlowError(f"empty project event chain: {path}")
    validate_chain(events, path)
    validate_history(events, path)
    return events


def validate_chain(events: list[dict[str, Any]], path: Path) -> None:
    previous_hash: str | None = None
    project_id: str | None = None
    seen_ids: set[str] = set()
    for expected_sequence, event in enumerate(events, start=1):
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise DealFlowError(f"event {expected_sequence} has no event_id: {path}")
        if event_id in seen_ids:
            raise DealFlowError(f"duplicate event_id {event_id}: {path}")
        seen_ids.add(event_id)
        if event.get("sequence") != expected_sequence:
            raise DealFlowError(f"broken event sequence at {event_id}: {path}")
        if event.get("schema_version") != SCHEMA_VERSION:
            raise DealFlowError(f"unsupported event schema at {event_id}: {path}")
        if event.get("producer") != PRODUCER:
            raise DealFlowError(f"unexpected event producer at {event_id}: {path}")
        if event.get("event_type") not in EVENT_TYPES:
            raise DealFlowError(f"unknown event type at {event_id}: {path}")
        if project_id is None:
            project_id = event.get("project_id")
        if event.get("project_id") != project_id:
            raise DealFlowError(f"project_id changed at {event_id}: {path}")
        if event.get("previous_event_hash") != previous_hash:
            raise DealFlowError(f"broken previous_event_hash at {event_id}: {path}")
        stored_hash = event.get("event_hash")
        unsigned = dict(event)
        unsigned.pop("event_hash", None)
        expected_hash = sha256_text(canonical_json(unsigned))
        if stored_hash != expected_hash:
            raise DealFlowError(f"broken event_hash at {event_id}: {path}")
        previous_hash = stored_hash


def seal_event(
    payload: dict[str, Any],
    *,
    project_id: str,
    sequence: int,
    previous_hash: str | None,
) -> dict[str, Any]:
    event = {
        "schema_version": SCHEMA_VERSION,
        "event_id": payload.get("event_id") or f"evt_{uuid.uuid4().hex}",
        "sequence": sequence,
        "occurred_at": payload.get("occurred_at") or now_iso(),
        "actor": payload.get("actor", "codex"),
        "project_id": project_id,
        "event_type": payload["event_type"],
        "run_id": payload.get("run_id") or f"run_{uuid.uuid4().hex}",
        "trigger": payload.get("trigger", ""),
        "reason": payload.get("reason", ""),
        "from": payload.get("from", {}),
        "to": payload.get("to", {}),
        "input_refs": payload.get("input_refs", []),
        "output_refs": payload.get("output_refs", []),
        "producer": PRODUCER,
        "approval_ref": payload.get("approval_ref"),
        "supersedes": payload.get("supersedes"),
        "previous_event_hash": previous_hash,
    }
    event["event_hash"] = sha256_text(canonical_json(event))
    return event


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(event) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def initial_project_state(first: dict[str, Any]) -> dict[str, Any]:
    if first.get("event_type") != "project_initialized":
        raise DealFlowError("first event must be project_initialized")
    state = dict(first.get("to", {}))
    state["artifacts"] = dict(state.get("artifacts", {}))
    state["_source_event_ids"] = set()
    state["_superseded_source_event_ids"] = set()
    state["project_id"] = first["project_id"]
    return state


def apply_event_to_state(
    state: dict[str, Any], event: dict[str, Any]
) -> dict[str, Any]:
    event_type = event["event_type"]
    target = event.get("to", {})
    previous_stage = state.get("workflow_stage")
    if event_type in {"source_registered", "source_superseded"}:
        state["_source_event_ids"].add(event["event_id"])
    if event_type == "source_superseded":
        state["_superseded_source_event_ids"].add(event["supersedes"])
    if event_type == "project_renamed":
        old_name = state.get("project_name")
        aliases = list(state.get("aliases", []))
        if old_name and old_name not in aliases:
            aliases.append(old_name)
        state["aliases"] = aliases
    for key in (
        "project_name",
        "aliases",
        "lifecycle_status",
        "workflow_stage",
        "research_level",
        "research_status",
        "decision_status",
        "current_gate",
        "blockers",
        "next_action",
        "last_approved_gate",
        "last_gate_decision",
    ):
        if key in target:
            state[key] = target[key]
    if event_type.startswith("artifact_"):
        artifact_status = {
            "artifact_created": "current",
            "artifact_updated": "current",
            "artifact_marked_stale": "stale",
            "artifact_audited": "audited",
        }[event_type]
        for ref in event.get("output_refs", []):
            if not isinstance(ref, dict) or not ref.get("path"):
                continue
            artifact_key = str(ref["path"])
            previous = dict(state["artifacts"].get(artifact_key, {}))
            previous_hash = previous.get("sha256")
            if event_type not in {"artifact_marked_stale", "artifact_audited"}:
                previous.update(ref)
            if event_type in {"artifact_marked_stale", "artifact_audited"} and previous_hash:
                previous["sha256"] = previous_hash
            previous.update(
                {
                    "path": artifact_key,
                    "status": artifact_status,
                    "last_event_id": event["event_id"],
                    "updated_at": event["occurred_at"],
                }
            )
            state["artifacts"][artifact_key] = previous
    if event_type == "workflow_transitioned" and previous_stage in GATES:
        state["last_approved_gate"] = None
        state["last_gate_decision"] = None
    if event_type == "project_reconciled" and {
        "workflow_stage",
        "current_gate",
    } & set(target):
        state["last_approved_gate"] = None
        state["last_gate_decision"] = None
    if event_type == "artifact_audited":
        state["last_audit_event_id"] = event["event_id"]
        state["last_audit_at"] = event["occurred_at"]
    if event.get("approval_ref"):
        state["last_approval_ref"] = event["approval_ref"]
        state["last_approval_event_id"] = event["event_id"]
        state["last_approval_at"] = event["occurred_at"]
    state["updated_at"] = event["occurred_at"]
    state["last_event_id"] = event["event_id"]
    return state


def project_state(events: list[dict[str, Any]]) -> dict[str, Any]:
    state = initial_project_state(events[0])
    for event in events:
        apply_event_to_state(state, event)
    return state


def render_state(state: dict[str, Any]) -> str:
    gate = state.get("current_gate") or "无"
    aliases = "、".join(markdown_cell(alias) for alias in state.get("aliases", []))
    content = (
        "# 项目状态\n\n"
        f"{GENERATED_NOTICE}\n\n"
        f"<!-- jvc-deal-flow:last-event={state['last_event_id']} -->\n\n"
        f"- 项目：{markdown_cell(state['project_name'])}\n"
        f"- 别名：{aliases or '无'}\n"
        f"- project_id：`{state['project_id']}`\n"
        f"- lifecycle_status：`{state['lifecycle_status']}`\n"
        f"- workflow_stage：`{state['workflow_stage']}`\n"
        f"- research_level：`{state['research_level']}`\n"
        f"- research_status：`{state['research_status']}`\n"
        f"- decision_status：`{state['decision_status']}`\n"
        f"- current_gate：`{gate}`\n"
        f"- 下一步：{markdown_cell(state.get('next_action', '登记来源并建立 Data Layer'))}\n"
        f"- 最近更新：{state['updated_at']}\n"
        f"- 最后事件：`{state['last_event_id']}`\n"
        f"- 最近审查：`{state.get('last_audit_event_id', '无')}`"
        f"（{state.get('last_audit_at', '无')}）\n"
        f"- 最近用户批准：`{markdown_cell(state.get('last_approval_ref', '无'))}`"
        f"（事件 `{state.get('last_approval_event_id', '无')}`，"
        f"{state.get('last_approval_at', '无')}）\n"
    )
    blockers = state.get("blockers", [])
    content += "\n## 当前阻塞\n\n"
    content += (
        "\n".join(f"- {markdown_cell(blocker)}" for blocker in blockers)
        if blockers
        else "- 无"
    )
    content += "\n\n## 工件\n\n| 路径 | 状态 | 产生者 | 最近事件 |\n"
    content += "| --- | --- | --- | --- |\n"
    artifacts = state.get("artifacts", {})
    if artifacts:
        for path, artifact in sorted(artifacts.items()):
            content += (
                f"| {markdown_cell(path)} | `{markdown_cell(artifact.get('status', 'unknown'))}` | "
                f"`{markdown_cell(artifact.get('producer', ''))}` | "
                f"`{artifact.get('last_event_id', '')}` |\n"
            )
    else:
        content += "| 无 | — | — | — |\n"
    return content


def render_changelog(events: list[dict[str, Any]]) -> str:
    rows = [
        "# 项目改动日志",
        "",
        GENERATED_NOTICE,
        "",
        f"<!-- jvc-deal-flow:last-event={events[-1]['event_id']} -->",
        "",
        "| 时间 | 类型 | 变化 | 原因 | 影响工件 | 操作者 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for event in reversed(events):
        refs = event.get("output_refs", [])
        affected = "、".join(
            str(item.get("path", "")) if isinstance(item, dict) else str(item)
            for item in refs
        )
        change = canonical_json(event.get("to", {}))
        rows.append(
            f"| {event['occurred_at']} | `{event['event_type']}` | "
            f"{markdown_cell(change)} | {markdown_cell(event.get('reason', ''))} | "
            f"{markdown_cell(affected)} | "
            f"`{event.get('actor', '')}` |"
        )
    return "\n".join(rows) + "\n"


def iter_project_dirs(library_root: Path) -> Iterator[Path]:
    projects_dir = ensure_library(library_root)
    for candidate in sorted(projects_dir.iterdir()):
        if candidate.is_dir() and event_path(candidate).is_file():
            yield candidate


def render_projects(library_root: Path) -> str:
    rows: list[tuple[int, dict[str, Any]]] = []
    marker_items: list[dict[str, str]] = []
    for project_dir in iter_project_dirs(library_root):
        events = load_events(project_dir)
        state = project_state(events)
        marker_items.append(
            {
                "project_id": state["project_id"],
                "event_hash": events[-1]["event_hash"],
            }
        )
        priority = (
            0
            if state.get("current_gate")
            else 1
            if state.get("research_status") in {"blocked", "partial"}
            else 2
            if state.get("lifecycle_status") == "active"
            else 3
            if state.get("lifecycle_status") == "paused"
            else 4
        )
        rows.append((priority, state))
    lines = [
        "# JVC 项目库",
        "",
        GENERATED_NOTICE,
        "",
        f"<!-- jvc-deal-flow:library={sha256_text(canonical_json(marker_items))} -->",
        "",
        "| 项目 | 生命周期 | 阶段 | 研究级别 | 研究状态 | 当前闸门/阻塞 | 下一步 | 最近更新 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    rows.sort(key=lambda item: item[1].get("updated_at", ""), reverse=True)
    rows.sort(key=lambda item: item[0])
    for _, state in rows:
        gate_or_blocker = state.get("current_gate")
        if not gate_or_blocker and state.get("blockers"):
            gate_or_blocker = "；".join(
                markdown_cell(blocker) for blocker in state["blockers"]
            )
        lines.append(
            f"| {markdown_cell(state['project_name'])} | `{state['lifecycle_status']}` | "
            f"`{state['workflow_stage']}` | `{state['research_level']}` | "
            f"`{state['research_status']}` | "
            f"{markdown_cell(gate_or_blocker or '无')} | "
            f"{markdown_cell(state.get('next_action', ''))} | {state['updated_at']} |"
        )
    return "\n".join(lines) + "\n"


def generated_view_marker(content: str) -> str | None:
    match = VIEW_MARKER_RE.search(content)
    return match.group(1) if match else None


def write_views(project_dir: Path, library_root: Path, events: list[dict[str, Any]]) -> None:
    state = project_state(events)
    atomic_write(project_dir / "STATE.md", render_state(state))
    atomic_write(project_dir / "CHANGELOG.md", render_changelog(events))
    atomic_write(library_root / "PROJECTS.md", render_projects(library_root))


def find_matching_project(library_root: Path, project_name: str) -> Path | None:
    wanted = normalize_name(project_name)
    matches: list[Path] = []
    for project_dir in iter_project_dirs(library_root):
        state = project_state(load_events(project_dir))
        names = [state.get("project_name", ""), *state.get("aliases", [])]
        if any(normalize_name(str(name)) == wanted for name in names):
            matches.append(project_dir)
    if len(matches) > 1:
        raise DealFlowError(
            "multiple projects match this name: "
            + ", ".join(str(path) for path in matches)
        )
    return matches[0] if matches else None


def find_project_by_id(library_root: Path, project_id: str) -> Path | None:
    matches = [
        project_dir
        for project_dir in iter_project_dirs(library_root)
        if project_state(load_events(project_dir)).get("project_id") == project_id
    ]
    if len(matches) > 1:
        raise DealFlowError(f"duplicate project_id in library: {project_id}")
    return matches[0] if matches else None


def similar_projects(library_root: Path, project_name: str) -> list[Path]:
    wanted = normalize_name(project_name)
    if len(wanted) < 3:
        return []
    candidates: list[Path] = []
    for project_dir in iter_project_dirs(library_root):
        state = project_state(load_events(project_dir))
        names = [state.get("project_name", ""), *state.get("aliases", [])]
        if any(
            difflib.SequenceMatcher(
                None, wanted, normalize_name(str(name))
            ).ratio()
            >= 0.8
            for name in names
        ):
            candidates.append(project_dir)
    return candidates


def emit_existing_project(project_dir: Path) -> int:
    state = project_state(load_events(project_dir))
    print(
        json.dumps(
            {
                "existing": True,
                "project_id": state["project_id"],
                "project_dir": str(project_dir),
                "workflow_stage": state["workflow_stage"],
            },
            ensure_ascii=False,
        )
    )
    return 0


def ensure_project_names_unique(
    library_root: Path, current_project: Path, names: list[str]
) -> None:
    wanted = {normalize_name(name) for name in names}
    for project_dir in iter_project_dirs(library_root):
        if project_dir == current_project:
            continue
        state = project_state(load_events(project_dir))
        existing = {
            normalize_name(str(name))
            for name in [state.get("project_name", ""), *state.get("aliases", [])]
        }
        if wanted & existing:
            raise DealFlowError(
                f"project name or alias conflicts with existing project: {project_dir}"
            )


def find_library_root(project_dir: Path) -> Path:
    for candidate in (project_dir, *project_dir.parents):
        if marker_path(candidate).is_file():
            ensure_library(candidate)
            return candidate
    raise DealFlowError(f"no .jvc-library.json found above {project_dir}")


def normalize_refs(
    value: object, project_dir: Path, *, project_output: bool = False
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise DealFlowError("input_refs and output_refs must be lists")
    normalized: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, str):
            ref: dict[str, Any] = {"path": item}
        elif isinstance(item, dict):
            ref = dict(item)
        else:
            raise DealFlowError("each input/output ref must be a path or object")
        raw_path = ref.get("path")
        if isinstance(raw_path, str) and raw_path:
            path = Path(raw_path).expanduser()
            if not path.is_absolute():
                path = project_dir / path
            path = path.resolve()
            if project_output:
                try:
                    relative = path.relative_to(project_dir)
                except ValueError as exc:
                    raise DealFlowError(
                        f"project artifact must stay under {project_dir}: {path}"
                    ) from exc
                ref["path"] = relative.as_posix()
            else:
                ref["path"] = str(path)
            if path.is_file():
                actual = sha256_file(path)
                supplied = ref.get("sha256")
                if supplied is not None and supplied != actual:
                    raise DealFlowError(f"fingerprint mismatch: {path}")
                ref["sha256"] = actual
        normalized.append(ref)
    return normalized


def reject_unexpected_target_keys(
    payload: dict[str, Any], allowed: set[str], *, event_type: str
) -> None:
    unexpected = set(payload.get("to", {})) - allowed
    if unexpected:
        raise DealFlowError(
            f"{event_type} cannot change state fields: {sorted(unexpected)}"
        )


def validate_artifact_ref_path(ref: object, event_type: str) -> str:
    if not isinstance(ref, dict) or not isinstance(ref.get("path"), str):
        raise DealFlowError(f"{event_type} requires artifact path objects")
    path = ref["path"]
    if not path or Path(path).is_absolute() or ".." in Path(path).parts:
        raise DealFlowError(f"{event_type} requires a project-relative artifact path")
    return path


def validate_event_payload(payload: dict[str, Any], state: dict[str, Any]) -> None:
    unknown_fields = set(payload) - EVENT_INPUT_FIELDS
    if unknown_fields:
        raise DealFlowError(f"unknown event fields: {sorted(unknown_fields)}")
    event_type = payload.get("event_type")
    if event_type not in EVENT_TYPES - {"project_initialized"}:
        raise DealFlowError(f"unsupported event_type: {event_type}")
    if payload.get("actor", "codex") not in {"user", "codex", "external"}:
        raise DealFlowError("actor must be user, codex, or external")
    for key in ("event_id", "occurred_at", "run_id"):
        if key in payload and (
            not isinstance(payload[key], str) or not payload[key].strip()
        ):
            raise DealFlowError(f"{key} must be a non-empty string")
    if not isinstance(payload.get("trigger", ""), str):
        raise DealFlowError("trigger must be a string")
    for key in ("approval_ref", "supersedes"):
        if payload.get(key) is not None and (
            not isinstance(payload[key], str) or not payload[key].strip()
        ):
            raise DealFlowError(f"{key} must be null or a non-empty string")
    for key in ("from", "to"):
        if not isinstance(payload.get(key, {}), dict):
            raise DealFlowError(f"{key} must be an object")
    for key in ("input_refs", "output_refs"):
        if not isinstance(payload.get(key, []), list):
            raise DealFlowError(f"{key} must be a list")
    if not isinstance(payload.get("reason"), str) or not payload["reason"].strip():
        raise DealFlowError("reason must be a non-empty string")
    for key, expected in payload.get("from", {}).items():
        if state.get(key) != expected:
            raise DealFlowError(
                f"stale event: {key} is {state.get(key)!r}, not {expected!r}"
            )

    target = payload.get("to", {})
    approval_ref = payload.get("approval_ref")
    if event_type in {"source_registered", "source_superseded"}:
        reject_unexpected_target_keys(payload, {"next_action"}, event_type=event_type)
        if not payload.get("input_refs"):
            raise DealFlowError(f"{event_type} requires input_refs")
        if event_type == "source_superseded":
            supersedes = payload.get("supersedes")
            if supersedes not in state.get("_source_event_ids", set()):
                raise DealFlowError(
                    "source_superseded must reference an existing source event"
                )
            if supersedes in state.get("_superseded_source_event_ids", set()):
                raise DealFlowError("source event was already superseded")
        return
    if event_type in {
        "artifact_created",
        "artifact_updated",
        "artifact_marked_stale",
    }:
        reject_unexpected_target_keys(payload, {"next_action"}, event_type=event_type)
        if not payload.get("output_refs"):
            raise DealFlowError(f"{event_type} requires output_refs")
        for ref in payload["output_refs"]:
            artifact_path = validate_artifact_ref_path(ref, event_type)
            if event_type in {"artifact_created", "artifact_updated"}:
                if not isinstance(ref.get("sha256"), str):
                    raise DealFlowError(f"{event_type} artifact must exist")
                if not isinstance(ref.get("producer"), str) or not ref[
                    "producer"
                ].strip():
                    raise DealFlowError(f"{event_type} requires artifact producer")
                depends_on = ref.get("depends_on")
                if not isinstance(depends_on, list) or not all(
                    isinstance(dependency, str) and dependency.strip()
                    for dependency in depends_on
                ):
                    raise DealFlowError(f"{event_type} requires depends_on")
            if (
                event_type in {"artifact_updated", "artifact_marked_stale"}
                and artifact_path not in state.get("artifacts", {})
            ):
                raise DealFlowError(f"unknown artifact: {artifact_path}")
        return
    if event_type == "artifact_audited":
        reject_unexpected_target_keys(
            payload, {"research_status", "next_action"}, event_type=event_type
        )
        if target.get("research_status") not in RESEARCH_STATUSES - {
            "not_audited"
        }:
            raise DealFlowError("artifact_audited requires ready, partial, or blocked")
        if not payload.get("output_refs"):
            raise DealFlowError("artifact_audited requires output_refs")
        for ref in payload["output_refs"]:
            artifact_path = validate_artifact_ref_path(ref, event_type)
            registered = state.get("artifacts", {}).get(artifact_path)
            if not isinstance(registered, dict):
                raise DealFlowError("artifact_audited requires registered artifacts")
            if registered.get("status") != "current":
                raise DealFlowError(
                    f"artifact_audited requires a current artifact: {artifact_path}"
                )
            if not isinstance(ref.get("sha256"), str) or ref["sha256"] != registered.get(
                "sha256"
            ):
                raise DealFlowError(
                    f"artifact_audited fingerprint differs from registered artifact: {artifact_path}"
                )
        return
    if event_type == "project_renamed":
        reject_unexpected_target_keys(
            payload, {"project_name", "aliases", "next_action"}, event_type=event_type
        )
        if not isinstance(target.get("project_name"), str) or not target[
            "project_name"
        ].strip():
            raise DealFlowError("project_renamed requires project_name")
        if "aliases" in target:
            expected_aliases = list(state.get("aliases", []))
            old_name = state.get("project_name")
            if old_name and old_name not in expected_aliases:
                expected_aliases.append(old_name)
            if target["aliases"] != expected_aliases:
                raise DealFlowError(
                    "project_renamed aliases must preserve existing aliases and old name"
                )
        if not approval_ref:
            raise DealFlowError("project_renamed requires user approval_ref")
        return
    if event_type == "research_level_changed":
        reject_unexpected_target_keys(
            payload, {"research_level", "next_action"}, event_type=event_type
        )
        new_level = target.get("research_level")
        old_level = state.get("research_level")
        if new_level not in LEVELS:
            raise DealFlowError("invalid research_level")
        if abs(LEVELS.index(new_level) - LEVELS.index(old_level)) != 1:
            raise DealFlowError("research level changes must be adjacent")
        if state.get("lifecycle_status") not in {"active", "paused"}:
            raise DealFlowError("reopen the project before changing research level")
        if not approval_ref:
            raise DealFlowError("research level change requires user approval_ref")
        return
    if event_type == "workflow_transitioned":
        reject_unexpected_target_keys(
            payload, {"workflow_stage", "next_action"}, event_type=event_type
        )
        old_stage = state.get("workflow_stage")
        new_stage = target.get("workflow_stage")
        if state.get("lifecycle_status") != "active":
            raise DealFlowError("resume the project before changing workflow stage")
        if new_stage not in WORKFLOW_TRANSITIONS.get(old_stage, set()):
            raise DealFlowError(f"illegal workflow transition: {old_stage} -> {new_stage}")
        minimum_level = minimum_level_for_stage(new_stage)
        if LEVELS.index(state["research_level"]) < LEVELS.index(minimum_level):
            raise DealFlowError(f"{new_stage} requires research level {minimum_level}+")
        gate_for_transition = {
            ("pre_dd_review", "diligence"): "pre_dd_review",
            ("post_dd_review", "insight_layer"): "post_dd_review",
            ("ic_review", "decision_record"): "ic_review",
        }.get((old_stage, new_stage))
        if gate_for_transition and (
            state.get("last_approved_gate") != gate_for_transition
            or state.get("last_gate_decision") != "approve"
            or not approval_ref
        ):
            raise DealFlowError(
                f"{old_stage} -> {new_stage} requires an approved {gate_for_transition} gate"
            )
        if old_stage in GATES and not gate_for_transition:
            if (
                state.get("last_gate_decision") != "revise"
                or not approval_ref
            ):
                raise DealFlowError(
                    f"{old_stage} -> {new_stage} requires a revise gate decision"
                )
        return
    if event_type == "lifecycle_changed":
        reject_unexpected_target_keys(
            payload, {"lifecycle_status", "next_action"}, event_type=event_type
        )
        new_status = target.get("lifecycle_status")
        if new_status not in LIFECYCLES or new_status == state.get(
            "lifecycle_status"
        ):
            raise DealFlowError("invalid lifecycle_status change")
        old_status = state.get("lifecycle_status")
        allowed_lifecycle_changes = {
            "active": {"paused", "closed"},
            "paused": {"active", "closed"},
            "closed": {"active", "archived"},
            "archived": {"active"},
        }
        if new_status not in allowed_lifecycle_changes.get(old_status, set()):
            raise DealFlowError(
                f"illegal lifecycle transition: {old_status} -> {new_status}"
            )
        if (old_status, new_status) != ("active", "paused") and not approval_ref:
            raise DealFlowError(
                "resume, close, archive, and reopen require user approval_ref"
            )
        return
    if event_type == "gate_requested":
        reject_unexpected_target_keys(
            payload,
            {"current_gate", "lifecycle_status", "next_action"},
            event_type=event_type,
        )
        gate = target.get("current_gate")
        if gate not in GATES or gate != state.get("workflow_stage"):
            raise DealFlowError("gate_requested must match the current review stage")
        if state.get("current_gate") is not None:
            raise DealFlowError("another gate is already open")
        if state.get("lifecycle_status") != "active":
            raise DealFlowError("gate_requested requires an active project")
        if target.get("lifecycle_status") != "paused":
            raise DealFlowError("gate_requested must pause the project")
        return
    if event_type == "gate_decided":
        reject_unexpected_target_keys(
            payload,
            {
                "current_gate",
                "lifecycle_status",
                "last_approved_gate",
                "last_gate_decision",
                "next_action",
            },
            event_type=event_type,
        )
        gate = state.get("current_gate")
        decision = target.get("last_gate_decision")
        if gate not in GATES or decision not in {"approve", "revise", "stop"}:
            raise DealFlowError("gate_decided requires an open gate and valid decision")
        if not approval_ref:
            raise DealFlowError("gate_decided requires user approval_ref")
        if decision == "approve":
            if target.get("last_approved_gate") != gate:
                raise DealFlowError("approved gate must be recorded")
            if target.get("current_gate") is not None:
                raise DealFlowError("approved gate must be cleared")
            if target.get("lifecycle_status") != "active":
                raise DealFlowError("approved gate must resume the project")
        elif decision == "revise":
            if target.get("current_gate") is not None:
                raise DealFlowError("revise must clear the current gate")
            if target.get("lifecycle_status") != "active":
                raise DealFlowError("revise must resume the project")
            if "last_approved_gate" in target:
                raise DealFlowError("revise must not record an approved gate")
        else:
            if target.get("current_gate") != gate:
                raise DealFlowError("stop must keep the current gate open")
            if target.get("lifecycle_status") != "paused":
                raise DealFlowError("stop must keep the project paused")
            if "last_approved_gate" in target:
                raise DealFlowError("stop must not record an approved gate")
        return
    if event_type == "decision_recorded":
        reject_unexpected_target_keys(
            payload, {"decision_status", "next_action"}, event_type=event_type
        )
        decision = target.get("decision_status")
        if state.get("workflow_stage") != "decision_record":
            raise DealFlowError("decision_recorded requires decision_record stage")
        if decision not in DECISION_STATUSES - {"undecided"} or not approval_ref:
            raise DealFlowError(
                "decision_recorded requires an explicit user decision and approval_ref"
            )
        return
    if event_type == "error_recorded":
        reject_unexpected_target_keys(
            payload,
            {"blockers", "research_status", "next_action"},
            event_type=event_type,
        )
        if "research_status" in target and target["research_status"] not in {
            "partial",
            "blocked",
        }:
            raise DealFlowError("error_recorded can only set partial or blocked")
        if "blockers" in target and (
            not isinstance(target["blockers"], list)
            or not all(
                isinstance(blocker, str) and blocker.strip()
                for blocker in target["blockers"]
            )
        ):
            raise DealFlowError("blockers must be non-empty strings")
        return
    if event_type == "project_reconciled":
        reject_unexpected_target_keys(
            payload,
            {
                "project_name",
                "aliases",
                "lifecycle_status",
                "workflow_stage",
                "research_level",
                "research_status",
                "decision_status",
                "current_gate",
                "blockers",
                "next_action",
            },
            event_type=event_type,
        )
        if not approval_ref:
            raise DealFlowError("project_reconciled requires user approval_ref")
        if "aliases" in target and (
            not isinstance(target["aliases"], list)
            or not all(
                isinstance(alias, str) and alias.strip()
                for alias in target["aliases"]
            )
        ):
            raise DealFlowError("project aliases must be non-empty strings")
        if "project_name" in target and (
            not isinstance(target["project_name"], str)
            or not target["project_name"].strip()
        ):
            raise DealFlowError("project_name must be a non-empty string")
        if "next_action" in target and not isinstance(target["next_action"], str):
            raise DealFlowError("next_action must be a string")
        if "blockers" in target and (
            not isinstance(target["blockers"], list)
            or not all(
                isinstance(blocker, str) and blocker.strip()
                for blocker in target["blockers"]
            )
        ):
            raise DealFlowError("blockers must be non-empty strings")
        allowed_values = {
            "lifecycle_status": LIFECYCLES,
            "workflow_stage": set(WORKFLOW_TRANSITIONS),
            "research_level": set(LEVELS),
            "research_status": RESEARCH_STATUSES,
            "decision_status": DECISION_STATUSES,
            "current_gate": GATES | {None},
        }
        for field, values in allowed_values.items():
            if field in target and target[field] not in values:
                raise DealFlowError(f"invalid reconciled {field}")
        reconciled = dict(state)
        reconciled.update(target)
        required_level = minimum_level_for_stage(reconciled["workflow_stage"])
        if LEVELS.index(reconciled["research_level"]) < LEVELS.index(required_level):
            raise DealFlowError(
                f"{reconciled['workflow_stage']} requires research level {required_level}+"
            )
        gate = reconciled.get("current_gate")
        if gate is not None and (
            gate != reconciled["workflow_stage"]
            or reconciled["lifecycle_status"] != "paused"
        ):
            raise DealFlowError(
                "an open gate must match the workflow stage and pause the project"
            )
        if (
            reconciled["decision_status"] != "undecided"
            and reconciled["workflow_stage"] != "decision_record"
        ):
            raise DealFlowError(
                "a final decision requires the decision_record workflow stage"
            )
        return
    raise DealFlowError(f"unhandled event_type: {event_type}")


def validate_initial_event(event: dict[str, Any], path: Path) -> None:
    required_fields = {
        "schema_version",
        "event_id",
        "sequence",
        "occurred_at",
        "actor",
        "project_id",
        "event_type",
        "run_id",
        "trigger",
        "reason",
        "from",
        "to",
        "input_refs",
        "output_refs",
        "producer",
        "approval_ref",
        "supersedes",
        "previous_event_hash",
        "event_hash",
    }
    if set(event) != required_fields:
        raise DealFlowError(f"invalid project_initialized fields: {path}")
    target = event.get("to")
    required_target = {
        "project_name",
        "aliases",
        "lifecycle_status",
        "workflow_stage",
        "research_level",
        "research_status",
        "decision_status",
        "current_gate",
        "blockers",
        "artifacts",
        "next_action",
    }
    if not isinstance(target, dict) or set(target) != required_target:
        raise DealFlowError(f"invalid project_initialized state: {path}")
    if not isinstance(target["project_name"], str) or not target[
        "project_name"
    ].strip():
        raise DealFlowError(f"project_initialized requires project_name: {path}")
    expected = {
        "aliases": [],
        "lifecycle_status": "active",
        "workflow_stage": "intake",
        "research_level": "L0",
        "research_status": "not_audited",
        "decision_status": "undecided",
        "current_gate": None,
        "blockers": [],
        "artifacts": {},
    }
    if any(target.get(key) != value for key, value in expected.items()):
        raise DealFlowError(f"invalid initial project state: {path}")
    if not isinstance(target["next_action"], str):
        raise DealFlowError(f"invalid initial next_action: {path}")
    if event.get("from") != {} or event.get("input_refs") or event.get("output_refs"):
        raise DealFlowError(f"project_initialized cannot reference prior state: {path}")
    if event.get("approval_ref") is not None or event.get("supersedes") is not None:
        raise DealFlowError(f"project_initialized cannot approve or supersede: {path}")
    if event.get("actor") not in {"user", "codex", "external"}:
        raise DealFlowError(f"invalid initial actor: {path}")
    for field in ("occurred_at", "run_id", "reason"):
        if not isinstance(event.get(field), str) or not event[field].strip():
            raise DealFlowError(f"invalid project_initialized {field}: {path}")
    if not isinstance(event.get("trigger"), str):
        raise DealFlowError(f"invalid project_initialized trigger: {path}")
    try:
        uuid.UUID(str(event.get("project_id")))
    except (ValueError, AttributeError) as exc:
        raise DealFlowError(f"project_id must be a UUID: {path}") from exc


def validate_history(events: list[dict[str, Any]], path: Path) -> None:
    validate_initial_event(events[0], path)
    state = initial_project_state(events[0])
    apply_event_to_state(state, events[0])
    generated_fields = {
        "sequence",
        "project_id",
        "producer",
        "previous_event_hash",
        "event_hash",
    }
    for event in events[1:]:
        payload = {
            key: value for key, value in event.items() if key not in generated_fields
        }
        try:
            validate_event_payload(payload, state)
        except DealFlowError as exc:
            raise DealFlowError(
                f"invalid historical event {event.get('event_id')}: {exc}: {path}"
            ) from exc
        apply_event_to_state(state, event)


def event_matches_input(existing: dict[str, Any], payload: dict[str, Any]) -> bool:
    if set(payload) - EVENT_INPUT_FIELDS:
        return False
    defaults = {
        "schema_version": SCHEMA_VERSION,
        "actor": "codex",
        "trigger": "",
        "reason": "",
        "from": {},
        "to": {},
        "input_refs": [],
        "output_refs": [],
        "approval_ref": None,
        "supersedes": None,
    }
    compared_fields = {
        "schema_version",
        "event_id",
        "actor",
        "event_type",
        "trigger",
        "reason",
        "from",
        "to",
        "input_refs",
        "output_refs",
        "approval_ref",
        "supersedes",
    }
    if any(
        existing.get(key) != payload.get(key, defaults.get(key))
        for key in compared_fields
    ):
        return False
    return all(
        key not in payload or existing.get(key) == payload[key]
        for key in ("occurred_at", "run_id")
    )


def ref_fingerprints(refs: object) -> frozenset[str]:
    if not isinstance(refs, list):
        return frozenset()
    return frozenset(
        ref["sha256"]
        for ref in refs
        if isinstance(ref, dict) and isinstance(ref.get("sha256"), str)
    )


def business_event_signature(event: dict[str, Any]) -> str:
    return canonical_json(
        {
            "event_type": event.get("event_type"),
            "actor": event.get("actor", "codex"),
            "from": event.get("from", {}),
            "to": event.get("to", {}),
            "input_refs": event.get("input_refs", []),
            "output_refs": event.get("output_refs", []),
            "approval_ref": event.get("approval_ref"),
            "supersedes": event.get("supersedes"),
        }
    )


def command_event(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).expanduser().resolve()
    library_root = find_library_root(project_dir)
    input_path = Path(args.input).expanduser().resolve()
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DealFlowError(f"missing event input: {input_path}") from exc
    except json.JSONDecodeError as exc:
        raise DealFlowError(f"invalid event input JSON: {input_path}") from exc
    if not isinstance(payload, dict):
        raise DealFlowError("event input must be a JSON object")
    payload["input_refs"] = normalize_refs(payload.get("input_refs", []), project_dir)
    payload["output_refs"] = normalize_refs(
        payload.get("output_refs", []), project_dir, project_output=True
    )
    if not payload.get("trigger"):
        payload["trigger"] = payload.get("reason", "")
    with exclusive_lock(project_dir / ".jvc" / "project_events.lock"):
        events = load_events(project_dir)
        event_id = payload.get("event_id")
        if event_id is not None:
            if not isinstance(event_id, str) or not event_id:
                raise DealFlowError("event_id must be a non-empty string")
            existing = next(
                (event for event in events if event["event_id"] == event_id), None
            )
            if existing is not None:
                if not event_matches_input(existing, payload):
                    raise DealFlowError(f"event_id collision: {event_id}")
                print(
                    json.dumps(
                        {
                            "appended": False,
                            "event_id": event_id,
                            "sequence": existing["sequence"],
                        },
                        ensure_ascii=False,
                    )
                )
                return 0

        state = project_state(events)
        if (
            isinstance(payload.get("event_type"), str)
            and payload["event_type"].startswith("artifact_")
            and not set(payload) - EVENT_INPUT_FIELDS
        ):
            signature = business_event_signature(payload)
            duplicate_artifact_event = next(
                (
                    event
                    for event in events
                    if event["event_type"] == payload["event_type"]
                    and business_event_signature(event) == signature
                ),
                None,
            )
            if duplicate_artifact_event is not None:
                print(
                    json.dumps(
                        {
                            "appended": False,
                            "event_id": duplicate_artifact_event["event_id"],
                            "sequence": duplicate_artifact_event["sequence"],
                            "duplicate_business_event": True,
                        },
                        ensure_ascii=False,
                    )
                )
                return 0
        validate_event_payload(payload, state)
        proposed_names: list[str] | None = None
        if payload["event_type"] in {"project_renamed", "project_reconciled"}:
            target = payload.get("to", {})
            proposed_names = [
                str(target.get("project_name", state["project_name"])),
                *[
                    str(alias)
                    for alias in target.get("aliases", state.get("aliases", []))
                ],
            ]
        if payload["event_type"] == "source_registered":
            fingerprints = ref_fingerprints(payload["input_refs"])
            if fingerprints:
                duplicate = next(
                    (
                        event
                        for event in events
                        if event["event_type"] == "source_registered"
                        and ref_fingerprints(event.get("input_refs")) == fingerprints
                    ),
                    None,
                )
                if duplicate is not None:
                    print(
                        json.dumps(
                            {
                                "appended": False,
                                "event_id": duplicate["event_id"],
                                "sequence": duplicate["sequence"],
                                "duplicate_content": True,
                            },
                            ensure_ascii=False,
                        )
                    )
                    return 0

        event = seal_event(
            payload,
            project_id=state["project_id"],
            sequence=len(events) + 1,
            previous_hash=events[-1]["event_hash"],
        )
        with exclusive_lock(library_root / ".jvc-library.lock"):
            if proposed_names is not None:
                ensure_project_names_unique(
                    library_root, project_dir, proposed_names
                )
            append_event(event_path(project_dir), event)
            events.append(event)
            write_views(project_dir, library_root, events)
        print(
            json.dumps(
                {
                    "appended": True,
                    "event_id": event["event_id"],
                    "sequence": event["sequence"],
                },
                ensure_ascii=False,
            )
        )
    return 0


def command_check(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).expanduser().resolve()
    library_root = find_library_root(project_dir)
    with exclusive_lock(
        project_dir / ".jvc" / "project_events.lock"
    ), exclusive_lock(library_root / ".jvc-library.lock"):
        events = load_events(project_dir)
        state = project_state(events)
        drift: list[str] = []
        for artifact in state.get("artifacts", {}).values():
            path_value = artifact.get("path")
            expected_hash = artifact.get("sha256")
            if not isinstance(path_value, str) or not expected_hash:
                continue
            artifact_path = project_dir / path_value
            if not artifact_path.is_file():
                drift.append(f"artifact missing: {artifact_path}")
            elif sha256_file(artifact_path) != expected_hash:
                drift.append(f"artifact fingerprint drift: {artifact_path}")

        expected_views = {
            project_dir / "STATE.md": render_state(state),
            project_dir / "CHANGELOG.md": render_changelog(events),
            library_root / "PROJECTS.md": render_projects(library_root),
        }
        rebuilt: list[str] = []
        for path, expected in expected_views.items():
            if not path.exists():
                atomic_write(path, expected)
                rebuilt.append(path.name)
            else:
                actual = path.read_text(encoding="utf-8")
                if actual == expected:
                    continue
                actual_marker = generated_view_marker(actual)
                expected_marker = generated_view_marker(expected)
                if (
                    actual_marker
                    and expected_marker
                    and actual_marker != expected_marker
                ):
                    atomic_write(path, expected)
                    rebuilt.append(path.name)
                else:
                    drift.append(f"generated view drift: {path}")
        if drift:
            raise DealFlowError("; ".join(drift))
        print(
            json.dumps(
                {
                    "status": "valid",
                    "project_id": state["project_id"],
                    "workflow_stage": state["workflow_stage"],
                    "research_status": state["research_status"],
                    "views_rebuilt": rebuilt,
                },
                ensure_ascii=False,
            )
        )
    return 0


def command_list(args: argparse.Namespace) -> int:
    library_root = Path(args.library_root).expanduser().resolve()
    if not marker_path(library_root).is_file():
        raise DealFlowError(f"not a JVC library: {library_root}")
    ensure_library(library_root)
    with exclusive_lock(library_root / ".jvc-library.lock"):
        content = render_projects(library_root)
        atomic_write(library_root / "PROJECTS.md", content)
    print(content, end="")
    return 0


def command_init(args: argparse.Namespace) -> int:
    library_root = Path(args.library_root).expanduser().resolve()
    if not args.project_name.strip():
        raise DealFlowError("project name must not be empty")
    projects_dir = ensure_library(library_root)
    with exclusive_lock(library_root / ".jvc-library.lock"):
        if args.project_id:
            try:
                normalized_project_id = str(uuid.UUID(args.project_id))
            except ValueError as exc:
                raise DealFlowError("project_id must be a UUID") from exc
            project_by_id = find_project_by_id(library_root, normalized_project_id)
            if project_by_id is None:
                raise DealFlowError(
                    f"project_id not found in this library: {normalized_project_id}"
                )
            return emit_existing_project(project_by_id)

        existing = find_matching_project(library_root, args.project_name)
        if existing is not None:
            return emit_existing_project(existing)
        similar = similar_projects(library_root, args.project_name)
        if similar and not args.confirm_new:
            raise DealFlowError(
                "similar projects require confirmation: "
                + ", ".join(str(path) for path in similar)
                + "; rerun with --confirm-new only after user confirmation"
            )

        project_id = str(uuid.uuid4())
        slug = slugify(args.project_name)
        legacy_matches = [
            candidate
            for candidate in projects_dir.iterdir()
            if candidate.is_dir()
            and not event_path(candidate).exists()
            and normalize_name(candidate.name) == normalize_name(args.project_name)
        ]
        if len(legacy_matches) > 1:
            raise DealFlowError(
                "multiple legacy project directories match: "
                + ", ".join(str(path) for path in legacy_matches)
            )
        project_dir = legacy_matches[0] if legacy_matches else projects_dir / slug
        if event_path(project_dir).exists():
            project_dir = projects_dir / f"{slug}-{project_id[:8]}"
        project_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "event_type": "project_initialized",
            "trigger": f"初始化项目：{args.project_name}",
            "reason": "用户明确选择受编排项目模式",
            "from": {},
            "to": {
                "project_name": args.project_name.strip(),
                "aliases": [],
                "lifecycle_status": "active",
                "workflow_stage": "intake",
                "research_level": "L0",
                "research_status": "not_audited",
                "decision_status": "undecided",
                "current_gate": None,
                "blockers": [],
                "artifacts": {},
                "next_action": "登记来源并建立 Data Layer",
            },
        }
        event = seal_event(
            payload, project_id=project_id, sequence=1, previous_hash=None
        )
        append_event(event_path(project_dir), event)
        write_views(project_dir, library_root, [event])
        print(
            json.dumps(
                {
                    "existing": False,
                    "project_id": project_id,
                    "project_dir": str(project_dir),
                    "workflow_stage": "intake",
                },
                ensure_ascii=False,
            )
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    init_parser = commands.add_parser("init", help="initialize or restore a project")
    init_parser.add_argument("--library-root", required=True)
    init_parser.add_argument("--project-name", required=True)
    init_parser.add_argument("--project-id")
    init_parser.add_argument("--confirm-new", action="store_true")
    init_parser.set_defaults(handler=command_init)

    event_parser = commands.add_parser("event", help="append one validated event")
    event_parser.add_argument("--project-dir", required=True)
    event_parser.add_argument("--input", required=True)
    event_parser.set_defaults(handler=command_event)

    check_parser = commands.add_parser("check", help="validate a project and its views")
    check_parser.add_argument("--project-dir", required=True)
    check_parser.set_defaults(handler=command_check)

    list_parser = commands.add_parser("list", help="rebuild and show the project index")
    list_parser.add_argument("--library-root", required=True)
    list_parser.set_defaults(handler=command_list)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except DealFlowError as exc:
        print(f"dealflowctl: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

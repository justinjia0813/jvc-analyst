from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import sys
import tempfile
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator
from xml.etree import ElementTree

SCHEMA_VERSION = 1
REGISTRY_NAME = "evidence_registry.jsonl"
CORE_ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = CORE_ROOT / "profiles"
ARTIFACT_READ_ERRORS = (
    EOFError,
    ElementTree.ParseError,
    FileNotFoundError,
    KeyError,
    OSError,
    RuntimeError,
    UnicodeError,
    ValueError,
    json.JSONDecodeError,
    zipfile.BadZipFile,
    zipfile.LargeZipFile,
)
DERIVED_FIELDS = {"sequence", "previous_fingerprint", "record_fingerprint"}
BASE_FIELDS = {
    "schema_version",
    "record_id",
    "record_type",
    "created_at",
    "actor",
    "created_by_skill",
}
REQUIRED_FIELDS = {
    "scope": {
        "subject",
        "decision",
        "inclusions",
        "exclusions",
        "geography",
        "time_range",
        "user_assumptions",
    },
    "question": {
        "question_text",
        "priority",
        "hypothesis",
        "falsifier",
        "evidence_needed",
        "state",
    },
    "query": {
        "question_id",
        "direction",
        "query_text",
        "tool_class",
        "target_source_class",
        "executed_at",
        "search_round",
        "changed_core_judgment",
        "result_count",
        "outcome",
        "result_summary",
    },
    "source": {
        "title",
        "publisher",
        "author",
        "published_at",
        "accessed_at",
        "source_class",
        "location",
        "excerpt",
        "definition",
        "geography",
        "sample",
        "statistical_scope",
        "stance",
        "independence_key",
        "content_fingerprint",
    },
    "claim": {
        "question_id",
        "claim_text",
        "claim_kind",
        "topic",
        "importance",
        "support_source_ids",
        "counter_source_ids",
        "derived_from_claim_ids",
        "scope",
        "confidence",
        "reasoning",
        "conflict_resolution",
        "state",
    },
    "waiver": {
        "rule",
        "reason",
        "scope",
        "approved_by",
        "approved_at",
        "residual_risk",
    },
}
REFERENCE_FIELDS = {
    "question_id": "question",
    "support_source_ids": "source",
    "counter_source_ids": "source",
    "derived_from_claim_ids": "claim",
    "supersedes": None,
}
LIST_FIELDS = {
    "inclusions",
    "exclusions",
    "user_assumptions",
    "evidence_needed",
    "support_source_ids",
    "counter_source_ids",
    "derived_from_claim_ids",
}
SOURCE_CLASSES = {
    "regulatory-filing",
    "government",
    "company-filing",
    "company-material",
    "technical-paper",
    "trade-association",
    "customer-interview",
    "expert-interview",
    "reputable-media",
    "market-database",
    "user-document",
    "other",
}
ENUM_FIELDS = {
    ("question", "priority"): {"high", "medium", "low"},
    ("question", "state"): {"open", "supported", "refuted", "gap"},
    ("query", "direction"): {"support", "counter", "neutral"},
    ("query", "outcome"): {"captured", "no-result", "error"},
    ("source", "source_class"): SOURCE_CLASSES,
    ("source", "stance"): {"support", "counter", "neutral", "mixed"},
    ("claim", "claim_kind"): {
        "third_party_fact",
        "company_claim",
        "user_observation",
        "model_estimate",
        "agent_inference",
        "unknown",
    },
    ("claim", "importance"): {"decision_critical", "material", "context"},
    ("claim", "confidence"): {"high", "medium", "low", "unknown"},
    ("claim", "conflict_resolution"): {"none", "reconciled", "narrowed", "unresolved"},
    ("claim", "state"): {"supported", "refuted", "narrowed", "unverified"},
}
RECORD_PREFIXES = {
    "scope": "SC",
    "question": "Q",
    "query": "QU",
    "source": "S",
    "claim": "C",
    "waiver": "W",
}
NON_EMPTY_LIST_FIELDS = {"inclusions", "evidence_needed"}
NON_WAIVABLE_RULES = {
    "required_scope",
    "high_priority_question_open",
    "artifact_missing",
    "artifact_names",
    "artifact_unreadable",
    "artifact_suffix",
    "artifact_source_reference",
    "artifact_source_coverage",
    "artifact_workbook_sheets",
    "artifact_docx",
    "partial_label_missing",
    "upstream_audit_missing",
    "upstream_audit_blocked",
    "upstream_audit_ambiguous",
    "search_stability_changed",
}
EXIT_BY_STATUS = {"ready": 0, "partial": 10, "blocked": 20}


class LedgerError(RuntimeError):
    pass


class ResearchArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise LedgerError(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    try:
        return json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise LedgerError("payload must contain canonical JSON values") from exc


def record_fingerprint(payload: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in payload.items() if key != "record_fingerprint"}
    return hashlib.sha256(canonical_bytes(unsigned)).hexdigest()


def source_content_fingerprint(record: dict[str, Any]) -> str:
    evidence_packet = {
        key: record[key]
        for key in (
            "title",
            "publisher",
            "author",
            "published_at",
            "source_class",
            "location",
            "excerpt",
            "definition",
            "geography",
            "sample",
            "statistical_scope",
        )
    }
    return hashlib.sha256(canonical_bytes(evidence_packet)).hexdigest()


def normalize_input_record(record: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise LedgerError("record must be a JSON object")
    normalized = dict(record)
    if normalized.get("record_type") == "source":
        required_without_fingerprint = REQUIRED_FIELDS["source"] - {"content_fingerprint"}
        if not (required_without_fingerprint - normalized.keys()):
            expected = source_content_fingerprint(normalized)
            supplied = normalized.get("content_fingerprint")
            if supplied not in (None, expected):
                raise LedgerError(
                    f"{normalized.get('record_id', '<unknown>')}: content_fingerprint mismatch"
                )
            normalized["content_fingerprint"] = expected
    return normalized


def validate_timestamp(value: Any, field: str, record_id: str) -> None:
    if not isinstance(value, str) or "T" not in value or not value.endswith("Z"):
        raise LedgerError(f"{record_id}: {field} must be an ISO 8601 UTC timestamp")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise LedgerError(f"{record_id}: invalid {field}") from exc


def validate_input_record(record: dict[str, Any]) -> None:
    if not isinstance(record, dict):
        raise LedgerError("record must be a JSON object")
    if DERIVED_FIELDS & record.keys():
        raise LedgerError("caller must not set derived chain fields")
    missing = BASE_FIELDS - record.keys()
    if missing:
        raise LedgerError(f"{record.get('record_id', '<unknown>')}: missing fields {sorted(missing)}")
    if "supersedes" in record and (
        not isinstance(record["supersedes"], str) or not record["supersedes"].strip()
    ):
        raise LedgerError(f"{record['record_id']}: supersedes must be a non-empty string")
    if type(record["schema_version"]) is not int or record["schema_version"] != SCHEMA_VERSION:
        raise LedgerError(f"{record['record_id']}: unsupported schema_version")
    record_type = record["record_type"]
    if not isinstance(record_type, str):
        raise LedgerError(f"{record['record_id']}: record_type must be a string")
    if record_type not in REQUIRED_FIELDS:
        raise LedgerError(f"{record['record_id']}: unknown record_type {record_type!r}")
    prefix = RECORD_PREFIXES[record_type]
    suffix = str(record["record_id"])[len(prefix) :]
    if (
        not str(record["record_id"]).startswith(prefix)
        or not suffix.isdigit()
        or suffix.startswith("0")
    ):
        raise LedgerError(f"{record['record_id']}: invalid record_id prefix")
    missing = REQUIRED_FIELDS[record_type] - record.keys()
    if missing:
        raise LedgerError(f"{record['record_id']}: missing fields {sorted(missing)}")
    record_id = str(record["record_id"])
    for field in BASE_FIELDS - {"schema_version"}:
        if not isinstance(record[field], str) or not record[field].strip():
            raise LedgerError(f"{record_id}: {field} must be a non-empty string")
    validate_timestamp(record["created_at"], "created_at", record_id)
    for field in REQUIRED_FIELDS[record_type] - LIST_FIELDS:
        if field in {"result_count", "search_round"}:
            if (
                isinstance(record[field], bool)
                or not isinstance(record[field], int)
                or record[field] < 0
            ):
                raise LedgerError(f"{record_id}: {field} must be a non-negative integer")
            if field == "search_round" and record[field] == 0:
                raise LedgerError(f"{record_id}: search_round must be positive")
        elif field == "changed_core_judgment":
            if type(record[field]) is not bool:
                raise LedgerError(f"{record_id}: changed_core_judgment must be boolean")
        elif not isinstance(record[field], str) or not record[field].strip():
            raise LedgerError(f"{record_id}: {field} must be a non-empty string")
    for field in REQUIRED_FIELDS[record_type] & LIST_FIELDS:
        if not isinstance(record[field], list) or any(
            not isinstance(item, str) or not item.strip() for item in record[field]
        ):
            raise LedgerError(f"{record_id}: {field} must be a string list")
        if len(record[field]) != len(set(record[field])):
            raise LedgerError(f"{record_id}: {field} contains duplicates")
        if field in NON_EMPTY_LIST_FIELDS and not record[field]:
            raise LedgerError(f"{record_id}: {field} must not be empty")
    for (expected_type, field), allowed in ENUM_FIELDS.items():
        if record_type == expected_type and record[field] not in allowed:
            raise LedgerError(f"{record_id}: invalid {field} {record[field]!r}")
    if record_type == "query":
        validate_timestamp(record["executed_at"], "executed_at", record_id)
        if record["target_source_class"] not in SOURCE_CLASSES:
            raise LedgerError(f"{record_id}: invalid target_source_class")
        if record["outcome"] == "no-result" and record["result_count"] != 0:
            raise LedgerError(f"{record_id}: no-result requires result_count 0")
        if record["outcome"] == "captured" and record["result_count"] == 0:
            raise LedgerError(f"{record_id}: captured requires a positive result_count")
    if record_type == "source":
        validate_timestamp(record["accessed_at"], "accessed_at", record_id)
        if record["content_fingerprint"] != source_content_fingerprint(record):
            raise LedgerError(f"{record_id}: content_fingerprint mismatch")
    if record_type == "waiver":
        validate_timestamp(record["approved_at"], "approved_at", record_id)
        if record["rule"] in NON_WAIVABLE_RULES:
            raise LedgerError(f"{record_id}: rule cannot be waived: {record['rule']}")
        if record["actor"] != record["approved_by"] or record["created_at"] != record["approved_at"]:
            raise LedgerError(f"{record_id}: waiver actor and approval time must match provenance")
    if record_type == "claim":
        has_counter = bool(record["counter_source_ids"])
        if has_counter and record["conflict_resolution"] == "none":
            raise LedgerError(f"{record_id}: counter evidence requires conflict_resolution")
        if not has_counter and record["conflict_resolution"] != "none":
            raise LedgerError(f"{record_id}: conflict_resolution requires counter evidence")
        if record["conflict_resolution"] == "narrowed" and record["state"] != "narrowed":
            raise LedgerError(f"{record_id}: narrowed conflict requires narrowed state")


def effective_records(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    effective = {record["record_id"]: record for record in records}
    for record in records:
        superseded = record.get("supersedes")
        if superseded:
            effective.pop(str(superseded), None)
    return effective


def resolve_record_id(records: list[dict[str, Any]], record_id: str) -> str:
    successors = {
        str(record["supersedes"]): str(record["record_id"])
        for record in records
        if record.get("supersedes")
    }
    resolved = str(record_id)
    while resolved in successors:
        resolved = successors[resolved]
    return resolved


def _validate_claim_lineage_cycles(records: list[dict[str, Any]]) -> None:
    claims = {
        record_id: record
        for record_id, record in effective_records(records).items()
        if record["record_type"] == "claim"
    }
    graph = {
        record_id: [
            resolve_record_id(records, parent_id)
            for parent_id in record["derived_from_claim_ids"]
        ]
        for record_id, record in claims.items()
    }
    colors: dict[str, int] = {}

    def visit(record_id: str) -> None:
        color = colors.get(record_id, 0)
        if color == 1:
            raise LedgerError(f"claim lineage cycle detected at {record_id}")
        if color == 2:
            return
        colors[record_id] = 1
        for parent_id in graph.get(record_id, []):
            visit(parent_id)
        colors[record_id] = 2

    for record_id in graph:
        visit(record_id)


def validate_references(
    new_records: list[dict[str, Any]],
    existing_records: list[dict[str, Any]],
) -> None:
    known = {record["record_id"]: record for record in existing_records}
    superseded_ids = {
        str(record["supersedes"])
        for record in existing_records
        if record.get("supersedes")
    }
    for record in new_records:
        record_id = str(record["record_id"])
        if record_id in known:
            raise LedgerError(f"duplicate record_id: {record_id}")
        for field, expected_type in REFERENCE_FIELDS.items():
            raw = record.get(field)
            values = raw if isinstance(raw, list) else ([] if raw in (None, "") else [raw])
            for value in values:
                target = known.get(str(value))
                if target is None:
                    raise LedgerError(f"{record_id}: unknown reference {value!r}")
                if expected_type and target["record_type"] != expected_type:
                    raise LedgerError(f"{record_id}: {field} must reference {expected_type}")
        superseded = record.get("supersedes")
        if superseded:
            superseded_id = str(superseded)
            if superseded_id in superseded_ids:
                raise LedgerError(f"{record_id}: record already superseded: {superseded_id}")
            superseded_record = known[superseded_id]
            if superseded_record["record_type"] != record["record_type"]:
                raise LedgerError(f"{record_id}: supersedes must keep record_type")
            if superseded_record["created_by_skill"] != record["created_by_skill"]:
                raise LedgerError(f"{record_id}: correction skill ownership must match")
            superseded_ids.add(superseded_id)
        known[record_id] = record
    _validate_claim_lineage_cycles([*existing_records, *new_records])


def chained_records(
    existing: list[dict[str, Any]],
    additions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    previous = existing[-1]["record_fingerprint"] if existing else ""
    sequence = len(existing)
    output = []
    for raw in additions:
        sequence += 1
        record = {
            **raw,
            "sequence": sequence,
            "previous_fingerprint": previous,
        }
        record["record_fingerprint"] = record_fingerprint(record)
        previous = record["record_fingerprint"]
        output.append(record)
    return output


def atomic_write(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            for record in records:
                handle.write(canonical_bytes(record).decode("utf-8") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def registry_path(run_dir: Path) -> Path:
    return Path(run_dir).resolve() / REGISTRY_NAME


@contextmanager
def registry_lock(run_dir: Path) -> Iterator[None]:
    # ponytail: fail closed on a stale lock; add PID/lease recovery only if crashes make it operationally necessary.
    path = registry_path(run_dir).with_name(f".{REGISTRY_NAME}.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise LedgerError(f"another registry writer is active: {path}") from exc
    try:
        os.write(descriptor, str(os.getpid()).encode("ascii"))
        os.close(descriptor)
        yield
    finally:
        try:
            os.close(descriptor)
        except OSError:
            pass
        path.unlink(missing_ok=True)


def load_registry(run_dir: Path) -> list[dict[str, Any]]:
    path = registry_path(run_dir)
    if not path.is_file():
        raise LedgerError(f"missing registry: {path}")
    records = []
    previous = ""
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LedgerError(f"invalid JSONL at line {line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise LedgerError(f"record at line {line_number} must be an object")
        if record.get("sequence") != line_number:
            raise LedgerError(f"sequence mismatch at line {line_number}")
        if record.get("previous_fingerprint") != previous:
            raise LedgerError(f"previous fingerprint mismatch at line {line_number}")
        expected = record_fingerprint(record)
        if record.get("record_fingerprint") != expected:
            raise LedgerError(f"record fingerprint mismatch at line {line_number}")
        previous = expected
        records.append(record)
    if not records:
        raise LedgerError(f"empty registry: {path}")
    replayed = [
        {key: value for key, value in record.items() if key not in DERIVED_FIELDS}
        for record in records
    ]
    for record in replayed:
        validate_input_record(record)
    validate_references(replayed, [])
    effective_scopes = [
        record
        for record in effective_records(replayed).values()
        if record["record_type"] == "scope"
    ]
    if len(effective_scopes) != 1:
        raise LedgerError("registry must contain exactly one effective scope")
    return records


def init_registry(run_dir: Path, skill: str, scope: dict[str, Any]) -> None:
    with registry_lock(run_dir):
        path = registry_path(run_dir)
        if path.exists():
            raise LedgerError(f"registry already exists: {path}")
        scope = normalize_input_record(scope)
        validate_input_record(scope)
        if scope["record_type"] != "scope" or scope["created_by_skill"] != skill:
            raise LedgerError("scope must be created by the initializing skill")
        validate_references([scope], [])
        atomic_write(path, chained_records([], [scope]))


def _append_records_locked(
    run_dir: Path,
    additions: list[dict[str, Any]],
    existing: list[dict[str, Any]] | None = None,
) -> None:
    existing = load_registry(run_dir) if existing is None else existing
    additions = [normalize_input_record(record) for record in additions]
    for record in additions:
        validate_input_record(record)
        if record["record_type"] == "scope" and not record.get("supersedes"):
            raise LedgerError(
                f"{record['record_id']}: additional scope must supersede the active scope"
            )
    validate_references(additions, existing)
    atomic_write(registry_path(run_dir), [*existing, *chained_records(existing, additions)])


def append_records(run_dir: Path, additions: list[dict[str, Any]]) -> None:
    if any(record.get("record_type") == "waiver" for record in additions if isinstance(record, dict)):
        raise LedgerError("waiver must be created with write_waiver")
    with registry_lock(run_dir):
        _append_records_locked(run_dir, additions)


def load_profile(skill: str) -> dict[str, Any]:
    if not isinstance(skill, str) or re.fullmatch(r"jvc-[a-z0-9-]+", skill) is None:
        raise LedgerError("invalid profile skill name")
    path = PROFILE_ROOT / f"{skill}.json"
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LedgerError(f"missing profile for {skill}") from exc
    except (json.JSONDecodeError, OSError, UnicodeError) as exc:
        raise LedgerError(f"invalid profile {skill}: {exc}") from exc
    required_keys = {
        "schema_version",
        "skill",
        "required_record_types",
        "current_skill_record_types",
        "requires_counter_query",
        "minimum_independent_sources",
        "artifact_policy",
    }
    if not isinstance(profile, dict) or set(profile) != required_keys:
        raise LedgerError(f"invalid profile {skill}: fields")
    if type(profile["schema_version"]) is not int or profile["schema_version"] != SCHEMA_VERSION:
        raise LedgerError(f"invalid profile {skill}: schema_version")
    if profile["skill"] != skill:
        raise LedgerError(f"invalid profile {skill}: skill")
    required_types = profile["required_record_types"]
    current_types = profile["current_skill_record_types"]
    if (
        not isinstance(required_types, list)
        or not required_types
        or any(not isinstance(value, str) or not value for value in required_types)
        or len(required_types) != len(set(required_types))
        or not set(required_types) <= set(REQUIRED_FIELDS)
        or not isinstance(current_types, list)
        or any(not isinstance(value, str) or not value for value in current_types)
        or len(current_types) != len(set(current_types))
        or not set(current_types) <= set(required_types)
    ):
        raise LedgerError(f"invalid profile {skill}: record types")
    if type(profile["requires_counter_query"]) is not bool:
        raise LedgerError(f"invalid profile {skill}: requires_counter_query")
    minimum = profile["minimum_independent_sources"]
    if type(minimum) is not int or minimum < 1:
        raise LedgerError(f"invalid profile {skill}: minimum_independent_sources")
    policy = profile["artifact_policy"]
    policy_keys = {"kind", "allowed_suffixes", "required_names", "required_sheets"}
    if not isinstance(policy, dict) or set(policy) != policy_keys:
        raise LedgerError(f"invalid profile {skill}: artifact_policy")
    kind = policy["kind"]
    if kind not in {"markdown", "xlsx", "docx", "multi"}:
        raise LedgerError(f"invalid profile {skill}: artifact_policy.kind")
    for field in ("allowed_suffixes", "required_names", "required_sheets"):
        values = policy[field]
        if (
            not isinstance(values, list)
            or any(not isinstance(value, str) or not value for value in values)
            or len(values) != len(set(values))
        ):
            raise LedgerError(f"invalid profile {skill}: artifact_policy.{field}")
    allowed = policy["allowed_suffixes"]
    names = policy["required_names"]
    sheets = policy["required_sheets"]
    if any(value != value.lower() or not value.startswith(".") for value in allowed):
        raise LedgerError(f"invalid profile {skill}: artifact_policy.allowed_suffixes")
    if any(Path(value).name != value for value in names):
        raise LedgerError(f"invalid profile {skill}: artifact_policy.required_names")
    expected_suffix = {"markdown": [".md"], "xlsx": [".xlsx"], "docx": [".docx"]}
    if kind == "multi":
        valid_policy = not allowed and bool(names) and not sheets
    else:
        valid_policy = (
            allowed == expected_suffix[kind]
            and not names
            and (bool(sheets) if kind == "xlsx" else not sheets)
        )
    if not valid_policy:
        raise LedgerError(f"invalid profile {skill}: artifact_policy combination")
    return profile


def file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def profile_fingerprint(profile: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(profile)).hexdigest()


def core_runtime_fingerprint() -> str:
    return file_fingerprint(Path(__file__).resolve())


MAIN_XML_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOCUMENT_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _safe_workbook_target(target: str) -> str:
    if not target or "\\" in target or "://" in target:
        raise ValueError("unsafe workbook relationship target")
    candidate = (
        target.lstrip("/")
        if target.startswith("/")
        else posixpath.join("xl", target)
    )
    normalized = posixpath.normpath(candidate)
    if normalized == ".." or normalized.startswith("../") or not normalized.startswith("xl/"):
        raise ValueError("workbook relationship escapes xl/")
    return normalized


def _workbook_sheet_targets(
    archive: zipfile.ZipFile,
) -> list[tuple[str, str]]:
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    relationships = ElementTree.fromstring(
        archive.read("xl/_rels/workbook.xml.rels")
    )
    relationship_map: dict[str, str] = {}
    relationship_ids: set[str] = set()
    for relationship in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship"):
        relationship_id = relationship.attrib.get("Id")
        relationship_type = relationship.attrib.get("Type", "")
        if not relationship_id or relationship_id in relationship_ids:
            raise ValueError("invalid workbook relationship id")
        relationship_ids.add(relationship_id)
        if not relationship_type.endswith("/worksheet"):
            continue
        if relationship.attrib.get("TargetMode") == "External":
            raise ValueError("external worksheet relationship")
        relationship_map[relationship_id] = _safe_workbook_target(
            relationship.attrib.get("Target", "")
        )
    output = []
    names: set[str] = set()
    for sheet in workbook.findall(
        f"{{{MAIN_XML_NS}}}sheets/{{{MAIN_XML_NS}}}sheet"
    ):
        name = sheet.attrib.get("name")
        relationship_id = sheet.attrib.get(f"{{{DOCUMENT_REL_NS}}}id")
        if (
            not name
            or name in names
            or relationship_id not in relationship_map
        ):
            raise ValueError("invalid workbook sheet binding")
        target = relationship_map[relationship_id]
        if target not in archive.namelist():
            raise KeyError(f"missing worksheet part: {target}")
        names.add(name)
        output.append((name, target))
    return output


def workbook_sheets(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as archive:
        sheets = _workbook_sheet_targets(archive)
        for _, target in sheets:
            ElementTree.fromstring(archive.read(target))
        return {name for name, _ in sheets}


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(item.itertext())
        for item in root.findall(f"{{{MAIN_XML_NS}}}si")
    ]


def _worksheet_text(
    archive: zipfile.ZipFile,
    target: str,
    shared: list[str] | None,
) -> tuple[str, list[str] | None]:
    root = ElementTree.fromstring(archive.read(target))
    values = []
    for cell in root.findall(f".//{{{MAIN_XML_NS}}}c"):
        cell_type = cell.attrib.get("t", "n")
        if cell_type == "inlineStr":
            inline = cell.find(f"{{{MAIN_XML_NS}}}is")
            if inline is None:
                raise ValueError("inline string cell has no value")
            values.append("".join(inline.itertext()))
            continue
        value = cell.find(f"{{{MAIN_XML_NS}}}v")
        if value is None:
            continue
        raw = value.text or ""
        if cell_type == "s":
            if not raw.isdigit():
                raise ValueError("invalid shared string index")
            if shared is None:
                shared = _shared_strings(archive)
            index = int(raw)
            if index >= len(shared):
                raise ValueError("shared string index out of range")
            values.append(shared[index])
        elif cell_type in {"n", "str", "b", "e", "d"}:
            values.append(raw)
        else:
            raise ValueError(f"unsupported worksheet cell type: {cell_type}")
    return "\n".join(values), shared


def _xlsx_text(path: Path, references_only: bool) -> str:
    with zipfile.ZipFile(path) as archive:
        sheets = _workbook_sheet_targets(archive)
        selected = [
            (name, target)
            for name, target in sheets
            if not references_only or name == "sources"
        ]
        if references_only and not selected:
            raise KeyError("sources worksheet missing")
        shared: list[str] | None = None
        text = []
        for _, target in selected:
            worksheet_text, shared = _worksheet_text(archive, target, shared)
            text.append(worksheet_text)
        return "\n".join(text)


def _docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "word/document.xml" not in names:
            raise KeyError("word/document.xml missing")
        visible_parts = [
            name
            for name in (
                "word/document.xml",
                "word/footnotes.xml",
                "word/endnotes.xml",
            )
            if name in names
        ]
        return "\n".join(
            "".join(ElementTree.fromstring(archive.read(name)).itertext())
            for name in visible_parts
        )


def artifact_text(path: Path, *, references_only: bool = False) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".mmd"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".json":
        text = path.read_text(encoding="utf-8")
        json.loads(text)
        return text
    if suffix == ".xlsx":
        return _xlsx_text(path, references_only)
    if suffix == ".docx":
        return _docx_text(path)
    return ""


def add_finding(
    findings: list[dict[str, str]],
    rule: str,
    severity: str,
    message: str,
) -> None:
    finding = {"rule": rule, "severity": severity, "message": message}
    if finding not in findings:
        findings.append(finding)


def validate_artifacts(
    profile: dict[str, Any],
    artifacts: list[Path],
    all_source_ids: set[str],
    required_source_ids: set[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    fingerprints: list[dict[str, str]] = []
    policy = profile["artifact_policy"]
    allowed = set(policy["allowed_suffixes"])
    names = {Path(path).name for path in artifacts}
    missing_names = set(policy["required_names"]) - names
    if missing_names:
        add_finding(
            findings,
            "artifact_names",
            "block",
            f"missing artifacts: {sorted(missing_names)}",
        )
    cited_source_ids: set[str] = set()
    for raw in artifacts:
        path = Path(raw).resolve()
        if not path.is_file():
            add_finding(findings, "artifact_missing", "block", str(path))
            fingerprints.append({"path": str(path), "fingerprint": "missing"})
            continue
        if allowed and path.suffix.lower() not in allowed:
            add_finding(findings, "artifact_suffix", "block", str(path))
        try:
            fingerprint = file_fingerprint(path)
        except OSError as exc:
            fingerprints.append({"path": str(path), "fingerprint": "unreadable"})
            add_finding(findings, "artifact_unreadable", "block", f"{path}: {exc}")
            continue
        fingerprints.append({"path": str(path), "fingerprint": fingerprint})
        try:
            suffix = path.suffix.lower()
            if suffix == ".xlsx":
                sheets = workbook_sheets(path)
                missing_sheets = set(policy["required_sheets"]) - sheets
                if missing_sheets:
                    add_finding(
                        findings,
                        "artifact_workbook_sheets",
                        "block",
                        f"missing sheets: {sorted(missing_sheets)}",
                    )
                text = (
                    artifact_text(path, references_only=True)
                    if "sources" in sheets
                    else ""
                )
            elif suffix == ".docx":
                with zipfile.ZipFile(path) as archive:
                    has_document = "word/document.xml" in archive.namelist()
                    if not has_document:
                        add_finding(
                            findings,
                            "artifact_docx",
                            "block",
                            "word/document.xml missing",
                        )
                text = (
                    artifact_text(path, references_only=True)
                    if has_document
                    else ""
                )
            else:
                text = artifact_text(path, references_only=True)
        except ARTIFACT_READ_ERRORS as exc:
            add_finding(findings, "artifact_unreadable", "block", f"{path}: {exc}")
            continue
        used = set(re.findall(r"\[(S[1-9]\d*)\]", text))
        cited_source_ids.update(used)
        unknown = used - all_source_ids
        if unknown:
            add_finding(
                findings,
                "artifact_source_reference",
                "block",
                f"unknown sources: {sorted(unknown)}",
            )
    missing_required = required_source_ids - cited_source_ids
    if missing_required:
        add_finding(
            findings,
            "artifact_source_coverage",
            "block",
            f"uncited current-stage sources: {sorted(missing_required)}",
        )
    fingerprints.sort(key=lambda item: item["path"])
    return findings, fingerprints


def _source_independence_dimensions(
    evidence: list[dict[str, Any]],
) -> tuple[set[str], set[str], set[str], set[str], set[str]]:
    return (
        {source["source_class"].strip().casefold() for source in evidence},
        {source["independence_key"].strip().casefold() for source in evidence},
        {source["publisher"].strip().casefold() for source in evidence},
        {source["location"].strip().casefold() for source in evidence},
        {source["content_fingerprint"] for source in evidence},
    )


def audit_records(
    records: list[dict[str, Any]],
    skill: str,
    profile: dict[str, Any],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    active = list(effective_records(records).values())
    by_type = {
        record_type: [
            record for record in active if record["record_type"] == record_type
        ]
        for record_type in REQUIRED_FIELDS
    }
    for record_type in profile["required_record_types"]:
        if not by_type[record_type]:
            add_finding(
                findings,
                f"required_{record_type}",
                "block",
                f"missing {record_type}",
            )
    for record_type in profile["current_skill_record_types"]:
        if not any(
            record["created_by_skill"] == skill
            for record in by_type[record_type]
        ):
            add_finding(
                findings,
                f"current_{record_type}",
                "block",
                f"{skill} created no {record_type}",
            )

    questions = [
        question
        for question in by_type["question"]
        if question["created_by_skill"] == skill
    ]
    queries = [
        query
        for query in by_type["query"]
        if query["created_by_skill"] == skill
    ]
    claims = [
        claim
        for claim in by_type["claim"]
        if claim["created_by_skill"] == skill
    ]
    claim_states_by_question: dict[str, set[str]] = {}
    for claim in claims:
        question_id = resolve_record_id(records, claim["question_id"])
        claim_states_by_question.setdefault(question_id, set()).add(str(claim["state"]))
    for question in questions:
        if question["priority"] != "high":
            continue
        question_id = str(question["record_id"])
        state = question["state"]
        if state == "open":
            add_finding(
                findings,
                "high_priority_question_open",
                "block",
                question_id,
            )
        elif state == "gap":
            add_finding(
                findings,
                "high_priority_question_gap",
                "partial",
                question_id,
            )
        elif state not in claim_states_by_question.get(question_id, set()):
            add_finding(
                findings,
                "resolved_question_without_claim",
                "block",
                question_id,
            )
        if profile["requires_counter_query"]:
            related_queries = [
                query
                for query in queries
                if resolve_record_id(records, query["question_id"]) == question_id
            ]
            rounds = sorted({int(query["search_round"]) for query in related_queries})
            if len(rounds) < 2:
                add_finding(
                    findings,
                    "search_stability_missing",
                    "block",
                    question_id,
                )
            else:
                latest_rounds = set(rounds[-2:])
                if any(
                    query["changed_core_judgment"]
                    for query in related_queries
                    if query["search_round"] in latest_rounds
                ):
                    add_finding(
                        findings,
                        "search_stability_changed",
                        "block",
                        question_id,
                    )

    counter_questions = {
        resolve_record_id(records, query["question_id"])
        for query in queries
        if query["direction"] == "counter"
    }
    sources = {
        record["record_id"]: record
        for record in by_type["source"]
    }
    for claim in claims:
        rule_scope = str(claim["record_id"])
        critical = claim["importance"] == "decision_critical"
        evidence_severity = "block" if critical else "partial"
        question_id = resolve_record_id(records, claim["question_id"])
        if (
            critical
            and profile["requires_counter_query"]
            and question_id not in counter_questions
        ):
            add_finding(
                findings,
                "counter_query_missing",
                "block",
                rule_scope,
            )
        support_ids = [
            resolve_record_id(records, source_id)
            for source_id in claim["support_source_ids"]
        ]
        counter_ids = [
            resolve_record_id(records, source_id)
            for source_id in claim["counter_source_ids"]
        ]
        evidence_ids = counter_ids if claim["state"] == "refuted" else support_ids
        evidence = [sources[source_id] for source_id in evidence_ids]
        for source in evidence:
            for field in (
                "published_at",
                "definition",
                "geography",
                "sample",
                "statistical_scope",
            ):
                if source[field].strip().casefold() in {"unknown", "未知"}:
                    add_finding(
                        findings,
                        "source_scope_unknown",
                        evidence_severity,
                        f"{source['record_id']}:{field}",
                    )
        if critical and claim["claim_kind"] in {"third_party_fact", "agent_inference"}:
            dimensions = _source_independence_dimensions(evidence)
            minimum = int(profile["minimum_independent_sources"])
            if any(len(values) < minimum for values in dimensions):
                add_finding(
                    findings,
                    "independent_sources",
                    "block",
                    rule_scope,
                )
        if claim["claim_kind"] == "company_claim":
            dimensions = _source_independence_dimensions(evidence)
            external_sources = [
                source
                for source in evidence
                if source["source_class"]
                not in {"company-filing", "company-material"}
            ]
            if any(len(values) < 2 for values in dimensions) or not external_sources:
                add_finding(
                    findings,
                    "company_claim_unverified",
                    evidence_severity,
                    rule_scope,
                )
        if claim["claim_kind"] == "unknown":
            add_finding(
                findings,
                "claim_kind_unknown",
                evidence_severity,
                rule_scope,
            )
        if claim["conflict_resolution"] == "unresolved":
            add_finding(
                findings,
                "conflict_unresolved",
                evidence_severity,
                rule_scope,
            )
        if not evidence_ids:
            add_finding(
                findings,
                "claim_unsupported",
                evidence_severity,
                rule_scope,
            )
        if claim["state"] == "unverified":
            add_finding(
                findings,
                "claim_unverified",
                evidence_severity,
                rule_scope,
            )
        elif claim["state"] == "narrowed":
            add_finding(
                findings,
                "claim_narrowed",
                "partial",
                rule_scope,
            )
    return findings


def apply_waivers(
    findings: list[dict[str, str]],
    records: list[dict[str, Any]],
    skill: str,
) -> list[dict[str, str]]:
    waivers = [
        record
        for record in effective_records(records).values()
        if record["record_type"] == "waiver"
        and record["created_by_skill"] == skill
    ]
    output: list[dict[str, str]] = []
    for finding in findings:
        matched = next(
            (
                waiver
                for waiver in waivers
                if waiver["rule"] == finding["rule"]
                and waiver["scope"] == finding["message"]
            ),
            None,
        )
        if (
            matched is not None
            and finding["rule"] not in NON_WAIVABLE_RULES
            and finding["severity"] == "block"
        ):
            output.append(
                {
                    **finding,
                    "severity": "partial",
                    "waiver_id": str(matched["record_id"]),
                }
            )
        else:
            output.append(finding)
    return output


def status_for(findings: list[dict[str, str]]) -> str:
    if any(finding["severity"] == "block" for finding in findings):
        return "blocked"
    if any(finding["severity"] == "partial" for finding in findings):
        return "partial"
    return "ready"


def ledger_prefix_fingerprint(records: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(canonical_bytes(record))
        digest.update(b"\n")
    return digest.hexdigest()


def stage_bytes(directory: Path, name: str, content: bytes) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{name}.",
        dir=directory,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        return temporary
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise


def audit_key(result: dict[str, Any]) -> str:
    identity = {key: value for key, value in result.items() if key != "audit_key"}
    return hashlib.sha256(canonical_bytes(identity)).hexdigest()


def _audit_entries(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeError):
        return []
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != SCHEMA_VERSION
        or not isinstance(payload.get("audits"), list)
    ):
        return []
    return [entry for entry in payload["audits"] if isinstance(entry, dict)]


def _audit_shape_is_valid(entry: dict[str, Any]) -> bool:
    required = {
        "schema_version",
        "skill",
        "ledger_sequence",
        "ledger_prefix_fingerprint",
        "artifacts",
        "dependency_audits",
        "profile_fingerprint",
        "core_runtime_fingerprint",
        "audit_path",
        "audited_at",
        "status",
        "findings",
        "audit_key",
    }
    if set(entry) != required or entry["schema_version"] != SCHEMA_VERSION:
        return False
    if (
        not isinstance(entry["skill"], str)
        or type(entry["ledger_sequence"]) is not int
        or entry["ledger_sequence"] < 1
        or not isinstance(entry["ledger_prefix_fingerprint"], str)
        or not isinstance(entry["profile_fingerprint"], str)
        or not isinstance(entry["core_runtime_fingerprint"], str)
        or not isinstance(entry["audit_path"], str)
        or not Path(entry["audit_path"]).is_absolute()
        or not isinstance(entry["audited_at"], str)
        or entry["status"] not in {"ready", "partial", "blocked"}
        or not isinstance(entry["audit_key"], str)
        or not isinstance(entry["artifacts"], list)
        or not isinstance(entry["dependency_audits"], list)
        or not isinstance(entry["findings"], list)
    ):
        return False
    for artifact in entry["artifacts"]:
        if (
            not isinstance(artifact, dict)
            or set(artifact) != {"path", "fingerprint"}
            or not isinstance(artifact["path"], str)
            or not Path(artifact["path"]).is_absolute()
            or not isinstance(artifact["fingerprint"], str)
        ):
            return False
    for finding in entry["findings"]:
        if (
            not isinstance(finding, dict)
            or not {"rule", "severity", "message"} <= set(finding)
            or set(finding) - {"rule", "severity", "message", "waiver_id"}
            or finding["severity"] not in {"block", "partial"}
            or any(
                not isinstance(finding[field], str)
                for field in ("rule", "severity", "message")
            )
            or (
                "waiver_id" in finding
                and not isinstance(finding["waiver_id"], str)
            )
        ):
            return False
    return all(isinstance(dependency, dict) for dependency in entry["dependency_audits"])


def _tail_is_relevant(
    entry: dict[str, Any],
    records: list[dict[str, Any]],
) -> bool:
    sequence = entry["ledger_sequence"]
    effective_ids = set(effective_records(records))
    for record in records[sequence:]:
        if (
            record["record_id"] in effective_ids
            and record["created_by_skill"] == entry["skill"]
            and record["record_type"] in REQUIRED_FIELDS
        ):
            return True
    return False


def _current_artifact_fingerprint(path: Path) -> str:
    if not path.is_file():
        return "missing"
    try:
        return file_fingerprint(path)
    except OSError:
        return "unreadable"


def _latest_audit_matches(
    binding: dict[str, Any],
    records: list[dict[str, Any]],
    skill_stack: tuple[str, ...],
    depth: int,
) -> bool:
    path = Path(binding["audit_path"])
    candidates = []
    for entry in _audit_entries(path):
        if entry.get("skill") != binding["skill"]:
            continue
        if _saved_audit_is_valid(entry, records, skill_stack, depth + 1):
            candidates.append(entry)
    if not candidates:
        return False
    latest_sequence = max(entry["ledger_sequence"] for entry in candidates)
    latest = [
        entry
        for entry in candidates
        if entry["ledger_sequence"] == latest_sequence
    ]
    return (
        len(latest) == 1
        and latest[0]["audit_key"] == binding["audit_key"]
    )


def _saved_audit_is_valid(
    entry: dict[str, Any],
    records: list[dict[str, Any]],
    skill_stack: tuple[str, ...],
    depth: int,
) -> bool:
    if depth > 64 or not _audit_shape_is_valid(entry):
        return False
    if entry["audit_key"] != audit_key(entry):
        return False
    profile = load_profile(entry["skill"])
    if entry["profile_fingerprint"] != profile_fingerprint(profile):
        return False
    if entry["core_runtime_fingerprint"] != core_runtime_fingerprint():
        return False
    sequence = entry["ledger_sequence"]
    if sequence > len(records):
        return False
    if entry["ledger_prefix_fingerprint"] != ledger_prefix_fingerprint(records[:sequence]):
        return False
    if _tail_is_relevant(entry, records):
        return False
    for artifact in entry["artifacts"]:
        path = Path(artifact["path"])
        if artifact["fingerprint"] != _current_artifact_fingerprint(path):
            return False
    for dependency in entry["dependency_audits"]:
        dependency_skill = dependency.get("skill")
        if not isinstance(dependency_skill, str) or dependency_skill in skill_stack:
            return False
        next_stack = (*skill_stack, dependency_skill)
        if not _saved_audit_is_valid(dependency, records, next_stack, depth + 1):
            return False
        if not _latest_audit_matches(dependency, records, next_stack, depth + 1):
            return False
    return True


def saved_audit_is_valid(
    entry: dict[str, Any],
    records: list[dict[str, Any]],
) -> bool:
    try:
        if not isinstance(entry, dict) or not isinstance(records, list):
            return False
        skill = entry.get("skill")
        if not isinstance(skill, str):
            return False
        return _saved_audit_is_valid(entry, records, (skill,), 0)
    except (
        AttributeError,
        KeyError,
        LedgerError,
        OSError,
        RecursionError,
        TypeError,
        UnicodeError,
        ValueError,
    ):
        return False


def audit_binding(entry: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(entry, ensure_ascii=False))


def dependency_findings(
    run_dir: Path,
    records: list[dict[str, Any]],
    skill: str,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    active = effective_records(records)
    sources = {
        record["record_id"]: record
        for record in active.values()
        if record["record_type"] == "source"
    }
    claims = {
        record["record_id"]: record
        for record in active.values()
        if record["record_type"] == "claim"
    }
    dependencies: set[str] = set()
    for claim in claims.values():
        if claim["created_by_skill"] != skill:
            continue
        for source_id in [
            *claim["support_source_ids"],
            *claim["counter_source_ids"],
        ]:
            source = sources[resolve_record_id(records, source_id)]
            if source["created_by_skill"] != skill:
                dependencies.add(str(source["created_by_skill"]))
        for claim_id in claim["derived_from_claim_ids"]:
            upstream_claim = claims[resolve_record_id(records, claim_id)]
            if upstream_claim["created_by_skill"] != skill:
                dependencies.add(str(upstream_claim["created_by_skill"]))
    if not dependencies:
        return [], []

    valid_entries = [
        entry
        for entry in _audit_entries(Path(run_dir).resolve() / "audit.json")
        if saved_audit_is_valid(entry, records)
    ]
    findings: list[dict[str, str]] = []
    bindings: list[dict[str, Any]] = []
    for dependency in sorted(dependencies):
        candidates = [
            entry
            for entry in valid_entries
            if entry["skill"] == dependency
        ]
        if not candidates:
            add_finding(
                findings,
                "upstream_audit_missing",
                "block",
                dependency,
            )
            continue
        latest_sequence = max(entry["ledger_sequence"] for entry in candidates)
        latest = [
            entry
            for entry in candidates
            if entry["ledger_sequence"] == latest_sequence
        ]
        if len(latest) != 1:
            add_finding(
                findings,
                "upstream_audit_ambiguous",
                "block",
                dependency,
            )
            continue
        upstream = latest[0]
        bindings.append(audit_binding(upstream))
        if upstream["status"] == "blocked":
            add_finding(
                findings,
                "upstream_audit_blocked",
                "block",
                dependency,
            )
        elif upstream["status"] == "partial":
            add_finding(
                findings,
                "upstream_audit_partial",
                "partial",
                dependency,
            )
    return findings, bindings


def paths_conflict(candidate: Path, reserved: Path) -> bool:
    candidate = Path(candidate).resolve()
    reserved = Path(reserved).resolve()
    if (
        candidate == reserved
        or str(candidate).casefold() == str(reserved).casefold()
    ):
        return True
    try:
        return candidate.samefile(reserved)
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise LedgerError(
            f"cannot compare artifact and reserved path identity: "
            f"{candidate}, {reserved}: {exc}"
        ) from exc


def audit_run(
    run_dir: Path,
    skill: str,
    artifacts: list[Path],
) -> dict[str, Any]:
    if not artifacts:
        raise LedgerError("at least one final artifact is required")
    try:
        resolved_artifacts = [Path(path).resolve() for path in artifacts]
    except (OSError, RuntimeError) as exc:
        raise LedgerError(f"invalid artifact path: {exc}") from exc
    if len(resolved_artifacts) != len(set(resolved_artifacts)):
        raise LedgerError("duplicate final artifact path")
    run_dir = Path(run_dir).resolve()
    reserved_paths = {
        run_dir / REGISTRY_NAME,
        run_dir / f".{REGISTRY_NAME}.lock",
        run_dir / "audit.json",
        run_dir / "audit.md",
    }
    for artifact in resolved_artifacts:
        for reserved in reserved_paths:
            if paths_conflict(artifact, reserved):
                raise LedgerError(
                    f"final artifact conflicts with reserved core path: {artifact}"
                )
    records = load_registry(run_dir)
    profile = load_profile(skill)
    upstream_findings, dependency_audits = dependency_findings(
        run_dir,
        records,
        skill,
    )
    active = effective_records(records)
    source_ids = {
        record["record_id"]
        for record in active.values()
        if record["record_type"] == "source"
    }
    current_claims = [
        record
        for record in active.values()
        if record["record_type"] == "claim"
        and record["created_by_skill"] == skill
    ]
    required_source_ids = {
        resolve_record_id(records, source_id)
        for claim in current_claims
        for source_id in [
            *claim["support_source_ids"],
            *claim["counter_source_ids"],
        ]
    }
    if not current_claims and "source" in profile["current_skill_record_types"]:
        required_source_ids.update(
            record["record_id"]
            for record in active.values()
            if record["record_type"] == "source"
            and record["created_by_skill"] == skill
        )
    artifact_findings, artifact_fingerprints = validate_artifacts(
        profile,
        resolved_artifacts,
        source_ids,
        required_source_ids,
    )
    findings = apply_waivers(
        [
            *audit_records(records, skill, profile),
            *upstream_findings,
            *artifact_findings,
        ],
        records,
        skill,
    )
    if status_for(findings) == "partial":
        has_label = False
        for path in resolved_artifacts:
            try:
                if "研究状态：partial" in artifact_text(path):
                    has_label = True
                    break
            except ARTIFACT_READ_ERRORS:
                continue
        if not has_label:
            add_finding(
                findings,
                "partial_label_missing",
                "block",
                "final artifact must contain 研究状态：partial",
            )
    result = {
        "schema_version": SCHEMA_VERSION,
        "skill": skill,
        "ledger_sequence": len(records),
        "ledger_prefix_fingerprint": ledger_prefix_fingerprint(records),
        "artifacts": artifact_fingerprints,
        "dependency_audits": dependency_audits,
        "profile_fingerprint": profile_fingerprint(profile),
        "core_runtime_fingerprint": core_runtime_fingerprint(),
        "audit_path": str((run_dir / "audit.json").resolve()),
        "audited_at": utc_now(),
        "status": status_for(findings),
        "findings": findings,
    }
    write_audit_outputs(run_dir, result)
    return result


def render_audit_markdown(entries: list[dict[str, Any]]) -> str:
    lines = [
        "# Research Audit",
        "",
        "| Skill | Ledger sequence | Status | Findings |",
        "| --- | ---: | --- | ---: |",
    ]
    for entry in entries:
        lines.append(
            f"| `{entry['skill']}` | {entry['ledger_sequence']} | "
            f"`{entry['status']}` | {len(entry['findings'])} |"
        )
    lines.append("")
    for entry in entries:
        lines.extend((f"## {entry['skill']} @ {entry['ledger_sequence']}", ""))
        lines.extend(
            (
                f"- Audited at: `{entry['audited_at']}`",
                f"- Ledger prefix: `{entry['ledger_prefix_fingerprint']}`",
                f"- Profile: `{entry['profile_fingerprint']}`",
                f"- Core runtime: `{entry['core_runtime_fingerprint']}`",
            )
        )
        for artifact in entry["artifacts"]:
            lines.append(
                f"- Artifact: `{artifact['path']}` `{artifact['fingerprint']}`"
            )
        for dependency in entry["dependency_audits"]:
            lines.append(
                f"- Upstream: `{dependency['skill']}` `{dependency['status']}` "
                f"`{dependency['audit_key']}`"
            )
        lines.append("")
        if not entry["findings"]:
            lines.extend(("- No findings.", ""))
            continue
        for finding in entry["findings"]:
            lines.append(
                f"- `{finding['severity']}` `{finding['rule']}`: {finding['message']}"
            )
        lines.append("")
    return "\n".join(lines)


def _has_replaced_dependency(
    entry: dict[str, Any],
    candidate: dict[str, Any],
) -> bool:
    for dependency in entry["dependency_audits"]:
        if (
            dependency["skill"] == candidate["skill"]
            and dependency["audit_key"] != candidate["audit_key"]
        ):
            return True
        if _has_replaced_dependency(dependency, candidate):
            return True
    return False


def write_audit_outputs(run_dir: Path, result: dict[str, Any]) -> None:
    run_dir = Path(run_dir).resolve()
    with registry_lock(run_dir):
        records = load_registry(run_dir)
        markdown_path = run_dir / "audit.md"
        json_path = run_dir / "audit.json"
        for output_path in (markdown_path, json_path):
            if output_path.is_symlink() or (
                output_path.exists() and not output_path.is_file()
            ):
                raise LedgerError(
                    f"audit output must be a non-symlink regular file: {output_path}"
                )
        if result.get("audit_path") != str(json_path):
            raise LedgerError("audit output path does not match the current run")
        candidate = {**result, "audit_key": audit_key(result)}
        if not saved_audit_is_valid(candidate, records):
            raise LedgerError("audit inputs changed while the audit was running")
        entries = []
        seen_keys: set[str] = set()
        for entry in _audit_entries(json_path):
            if (
                not saved_audit_is_valid(entry, records)
                or entry["audit_key"] in seen_keys
                or _has_replaced_dependency(entry, candidate)
                or (
                    entry["skill"] == candidate["skill"]
                    and entry["ledger_sequence"] == candidate["ledger_sequence"]
                )
                or entry["audit_key"] == candidate["audit_key"]
            ):
                continue
            seen_keys.add(entry["audit_key"])
            entries.append(entry)
        entries.append(candidate)
        entries.sort(
            key=lambda entry: (
                entry["ledger_sequence"],
                entry["skill"],
                entry["audit_key"],
            )
        )
        markdown_content = render_audit_markdown(entries).encode("utf-8")
        json_content = (
            json.dumps(
                {"schema_version": SCHEMA_VERSION, "audits": entries},
                allow_nan=False,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
        staged: list[Path] = []
        markdown_backup = None
        try:
            staged_markdown = stage_bytes(run_dir, "audit.md.stage", markdown_content)
            staged.append(staged_markdown)
            staged_json = stage_bytes(run_dir, "audit.json.stage", json_content)
            staged.append(staged_json)
            if markdown_path.exists():
                markdown_backup = stage_bytes(
                    run_dir,
                    "audit.md.backup",
                    markdown_path.read_bytes(),
                )
                staged.append(markdown_backup)

            markdown_published = False
            try:
                os.replace(staged_markdown, markdown_path)
                markdown_published = True
                # ponytail: two files cannot survive a crash between renames atomically;
                # audit.json is the machine-trusted commit point and a later audit rebuilds Markdown.
                os.replace(staged_json, json_path)
            except BaseException:
                if markdown_published:
                    if markdown_backup is None:
                        markdown_path.unlink()
                    else:
                        os.replace(markdown_backup, markdown_path)
                raise
        finally:
            for temporary in staged:
                if temporary.exists():
                    temporary.unlink()


def write_waiver(
    run_dir: Path,
    *,
    skill: str,
    rule: str,
    reason: str,
    scope: str,
    approved_by: str,
    approved_at: str,
    residual_risk: str,
) -> None:
    load_profile(skill)
    if rule in NON_WAIVABLE_RULES:
        raise LedgerError(f"rule cannot be waived: {rule}")
    run_dir = Path(run_dir).resolve()
    with registry_lock(run_dir):
        records = load_registry(run_dir)
        entries = [
            entry
            for entry in _audit_entries(run_dir / "audit.json")
            if entry.get("skill") == skill
            and saved_audit_is_valid(entry, records)
        ]
        if not entries:
            raise LedgerError("waiver requires a current blocked audit")
        latest_sequence = max(entry["ledger_sequence"] for entry in entries)
        latest = [
            entry
            for entry in entries
            if entry["ledger_sequence"] == latest_sequence
        ]
        matching = (
            [
                finding
                for finding in latest[0]["findings"]
                if finding.get("severity") == "block"
                and finding.get("rule") == rule
                and finding.get("message") == scope
            ]
            if len(latest) == 1 and latest[0]["status"] == "blocked"
            else []
        )
        if len(matching) != 1:
            raise LedgerError("waiver must match one current blocked finding")
        used_ids = {record["record_id"] for record in records}
        suffix = len(records) + 1
        while f"W{suffix}" in used_ids:
            suffix += 1
        waiver = {
            "schema_version": SCHEMA_VERSION,
            "record_id": f"W{suffix}",
            "record_type": "waiver",
            "created_at": approved_at,
            "actor": approved_by,
            "created_by_skill": skill,
            "rule": rule,
            "reason": reason,
            "scope": scope,
            "approved_by": approved_by,
            "approved_at": approved_at,
            "residual_risk": residual_risk,
        }
        _append_records_locked(run_dir, [waiver], records)


def read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise LedgerError(f"{path}: expected one JSON object")
    return payload


def read_jsonl_input(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise LedgerError(f"{path}:{line_number}: expected JSON object")
        records.append(payload)
    if not records:
        raise LedgerError(f"{path}: no records")
    return records


def build_parser() -> argparse.ArgumentParser:
    parser = ResearchArgumentParser(
        description="Maintain and audit a jvc evidence registry."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create or resume a research ledger.")
    init.add_argument("--skill", required=True)
    init.add_argument("--run-dir", required=True, type=Path)
    init.add_argument("--scope-file", type=Path)
    init.add_argument("--resume", action="store_true")

    record_parser = subparsers.add_parser(
        "record",
        help="Atomically append validated records.",
    )
    record_parser.add_argument("--run-dir", required=True, type=Path)
    record_parser.add_argument("--input", required=True, type=Path)

    audit = subparsers.add_parser(
        "audit",
        help="Audit one skill stage and its final artifacts.",
    )
    audit.add_argument("--run-dir", required=True, type=Path)
    audit.add_argument("--skill", required=True)
    audit.add_argument("--artifact", required=True, action="append", type=Path)

    waive = subparsers.add_parser(
        "waive",
        help="Append one human-approved business-evidence waiver.",
    )
    waive.add_argument("--run-dir", required=True, type=Path)
    waive.add_argument("--skill", required=True)
    waive.add_argument("--rule", required=True)
    waive.add_argument("--reason", required=True)
    waive.add_argument("--scope", required=True)
    waive.add_argument("--approved-by", required=True)
    waive.add_argument("--residual-risk", required=True)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        if args.command == "init":
            load_profile(args.skill)
            if args.resume:
                if args.scope_file is not None:
                    raise LedgerError("--resume cannot be combined with --scope-file")
                load_registry(args.run_dir)
                print(f"research ledger resumed: {registry_path(args.run_dir)}")
                return 0
            if args.scope_file is None:
                raise LedgerError("--scope-file is required without --resume")
            init_registry(
                args.run_dir,
                args.skill,
                read_json_object(args.scope_file),
            )
            print(f"research ledger initialized: {registry_path(args.run_dir)}")
            return 0
        if args.command == "record":
            records = read_jsonl_input(args.input)
            if any(record.get("record_type") == "waiver" for record in records):
                raise LedgerError("waiver records must use the waive command")
            for creating_skill in {
                str(record.get("created_by_skill", "")) for record in records
            }:
                load_profile(creating_skill)
            append_records(args.run_dir, records)
            print(f"research records appended: {args.input}")
            return 0
        if args.command == "waive":
            write_waiver(
                args.run_dir,
                skill=args.skill,
                rule=args.rule,
                reason=args.reason,
                scope=args.scope,
                approved_by=args.approved_by,
                approved_at=utc_now(),
                residual_risk=args.residual_risk,
            )
            print(f"research waiver appended: {args.rule}")
            return 0
        result = audit_run(args.run_dir, args.skill, args.artifact)
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "audit": str(Path(args.run_dir) / "audit.json"),
                },
                ensure_ascii=False,
            )
        )
        return EXIT_BY_STATUS[result["status"]]
    except (
        LedgerError,
        EOFError,
        ElementTree.ParseError,
        FileNotFoundError,
        KeyError,
        OSError,
        RuntimeError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        zipfile.BadZipFile,
        zipfile.LargeZipFile,
    ) as exc:
        print(f"research core error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

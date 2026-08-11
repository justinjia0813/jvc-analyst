from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape

sys.dont_write_bytecode = True
import researchctl as core
from researchctl import (
    LedgerError,
    append_records,
    audit_run,
    init_registry,
    load_profile,
    load_registry,
    resolve_record_id,
    saved_audit_is_valid,
    validate_artifacts,
    write_waiver,
)


PACKAGE = Path(__file__).resolve().parents[1]


def check_engine_contract() -> None:
    skill = (PACKAGE / "SKILL.md").read_text(encoding="utf-8")
    contract = (PACKAGE / "references" / "evidence-contract.md").read_text(
        encoding="utf-8"
    )
    assert "不可直接调用的证据引擎" in skill
    assert "证据台账、主张继承、产物审计" in skill
    assert "不推进业务阶段" in skill
    assert "ready、partial、blocked" in skill
    assert "主张继承" in contract
    assert "不得创建工作流阶段事件" in contract


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(Path(__file__).with_name("researchctl.py")), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )


def check_cli() -> None:
    help_result = run_cli("--help")
    assert help_result.returncode == 0, help_result.stderr
    for command in ("init", "record", "audit", "waive"):
        assert command in help_result.stdout

    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        missing_input = run_cli(
            "record",
            "--run-dir",
            str(root / "missing-input"),
        )
        assert missing_input.returncode == 1
        assert missing_input.stderr.startswith("research core error:")
        unknown_command = run_cli("unknown-command")
        assert unknown_command.returncode == 1
        assert unknown_command.stderr.startswith("research core error:")

        scope_file = root / "scope.json"
        scope_file.write_text(
            json.dumps(
                record(
                    "SC1",
                    "scope",
                    subject="玻璃基板",
                    decision="验证 CLI 初始化边界",
                    inclusions=["先进封装"],
                    exclusions=[],
                    geography="全球及中国",
                    time_range="2024-2029",
                    user_assumptions=[],
                ),
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        initialized = root / "initialized"
        init_result = run_cli(
            "init",
            "--skill",
            "jvc-track-research",
            "--run-dir",
            str(initialized),
            "--scope-file",
            str(scope_file),
        )
        assert init_result.returncode == 0, init_result.stderr
        assert "initialized" in init_result.stdout
        resume_result = run_cli(
            "init",
            "--skill",
            "jvc-track-research",
            "--run-dir",
            str(initialized),
            "--resume",
        )
        assert resume_result.returncode == 0, resume_result.stderr
        assert "resumed" in resume_result.stdout
        invalid_resume = run_cli(
            "init",
            "--skill",
            "jvc-track-research",
            "--run-dir",
            str(initialized),
            "--scope-file",
            str(scope_file),
            "--resume",
        )
        assert invalid_resume.returncode == 1
        assert invalid_resume.stderr.startswith(
            "research core error:"
        ), invalid_resume.stderr

        question_file = root / "question.jsonl"
        question_file.write_text(
            "\n"
            + json.dumps(
                record(
                    "Q1",
                    "question",
                    question_text="CLI 能否原子追加完整 batch？",
                    priority="low",
                    hypothesis="固定命令能够追加记录",
                    falsifier="固定命令拒绝合法记录",
                    evidence_needed=["账本记录"],
                    state="open",
                ),
                ensure_ascii=False,
            )
            + "\n\n",
            encoding="utf-8",
        )
        appended = run_cli(
            "record",
            "--run-dir",
            str(initialized),
            "--input",
            str(question_file),
        )
        assert appended.returncode == 0, appended.stderr
        assert "appended" in appended.stdout

        registry = initialized / "evidence_registry.jsonl"
        waiver_file = root / "waiver.jsonl"
        waiver_file.write_text(
            json.dumps(
                record(
                    "W1",
                    "waiver",
                    rule="company_claim_unverified",
                    reason="不得绕过 waive 命令",
                    scope="C1",
                    approved_by="test-user",
                    approved_at="2026-07-29T00:06:00Z",
                    residual_risk="公司口径仍未被第三方验证",
                ),
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        before = registry.read_bytes()
        rejected_waiver = run_cli(
            "record",
            "--run-dir",
            str(initialized),
            "--input",
            str(waiver_file),
        )
        assert rejected_waiver.returncode == 1
        assert registry.read_bytes() == before

        empty = root / "empty.jsonl"
        empty.write_text("\n\n", encoding="utf-8")
        empty_result = run_cli(
            "record",
            "--run-dir",
            str(initialized),
            "--input",
            str(empty),
        )
        assert empty_result.returncode == 1
        assert registry.read_bytes() == before

    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        run_dir, report = build_ready_fixture(root)
        audit_arguments = (
            "audit",
            "--run-dir",
            str(run_dir),
            "--skill",
            "jvc-track-research",
            "--artifact",
            str(report),
        )
        ready = run_cli(*audit_arguments)
        assert ready.returncode == 0, ready.stderr
        assert ready.stdout.count("\n") == 1
        assert json.loads(ready.stdout)["status"] == "ready"
        add_gap(run_dir)
        report.write_text(
            "研究状态：partial\n" + report.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        partial = run_cli(*audit_arguments)
        assert partial.returncode == 10, partial.stderr
        assert json.loads(partial.stdout)["status"] == "partial"
        add_blocked_company_claim(run_dir)
        blocked = run_cli(*audit_arguments)
        assert blocked.returncode == 20, blocked.stderr
        assert json.loads(blocked.stdout)["status"] == "blocked"

        waived = run_cli(
            "waive",
            "--run-dir",
            str(run_dir),
            "--skill",
            "jvc-track-research",
            "--rule",
            "company_claim_unverified",
            "--reason",
            "用户只需要保留公司口径用于下一轮访谈",
            "--scope",
            "C2",
            "--approved-by",
            "test-user",
            "--residual-risk",
            "商业化仍未被第三方验证",
        )
        assert waived.returncode == 0, waived.stderr
        assert "company_claim_unverified" in waived.stdout

        malformed = root / "malformed.jsonl"
        malformed.write_text("{\n", encoding="utf-8")
        registry = run_dir / "evidence_registry.jsonl"
        before = registry.read_bytes()
        failed = run_cli(
            "record",
            "--run-dir",
            str(run_dir),
            "--input",
            str(malformed),
        )
        assert failed.returncode == 1
        assert failed.stderr.startswith("research core error:")
        assert "Traceback" not in failed.stderr
        assert registry.read_bytes() == before


def record(record_id: str, record_type: str, **fields: object) -> dict[str, object]:
    return {
        "schema_version": 1,
        "record_id": record_id,
        "record_type": record_type,
        "created_at": "2026-07-29T00:00:00Z",
        "actor": "test-agent",
        "created_by_skill": "jvc-track-research",
        **fields,
    }


def expect_error(action, message: str) -> None:
    try:
        action()
    except LedgerError as exc:
        assert message in str(exc), exc
    else:
        raise AssertionError(f"expected LedgerError containing {message!r}")


def check_ledger() -> None:
    with TemporaryDirectory() as temporary:
        invalid_run_dir = Path(temporary) / "invalid-run"
        invalid_scope = record(
            "SC1",
            "scope",
            supersedes="SC999",
            subject="玻璃基板",
            decision="验证初始范围引用",
            inclusions=["半导体先进封装"],
            exclusions=[],
            geography="全球及中国",
            time_range="2024-2029",
            user_assumptions=[],
        )
        expect_error(
            lambda: init_registry(invalid_run_dir, "jvc-track-research", invalid_scope),
            "unknown reference",
        )
        assert not (invalid_run_dir / "evidence_registry.jsonl").exists()
        run_dir = Path(temporary) / "run"
        scope = record(
            "SC1",
            "scope",
            subject="玻璃基板",
            decision="确定下一轮尽调重点",
            inclusions=["半导体先进封装"],
            exclusions=["显示面板盖板玻璃"],
            geography="全球及中国",
            time_range="2024-2029",
            user_assumptions=[],
        )
        init_registry(run_dir, "jvc-track-research", scope)
        append_records(
            run_dir,
            [
                record(
                    "Q1",
                    "question",
                    question_text="玻璃基板量产良率是否仍限制规模交付？",
                    priority="high",
                    hypothesis="量产良率是当前商业化瓶颈",
                    falsifier="公开量产数据证明良率不再影响交付",
                    evidence_needed=["量产良率", "客户验证"],
                    state="open",
                ),
                record(
                    "QU1",
                    "query",
                    question_id="Q1",
                    direction="counter",
                    query_text="glass substrate mass production yield",
                    tool_class="web-search",
                    target_source_class="company-filing",
                    executed_at="2026-07-29T00:01:00Z",
                    search_round=1,
                    changed_core_judgment=False,
                    result_count=0,
                    outcome="no-result",
                    result_summary="未找到满足目标来源类型的反向证据",
                ),
            ],
        )
        entries = load_registry(run_dir)
        assert [entry["sequence"] for entry in entries] == [1, 2, 3]
        append_records(
            run_dir,
            [
                record(
                    "Q2",
                    "question",
                    supersedes="Q1",
                    question_text="玻璃基板量产良率是否限制未来十二个月规模交付？",
                    priority="high",
                    hypothesis="量产良率是当前商业化瓶颈",
                    falsifier="未来十二个月量产数据证明良率不影响交付",
                    evidence_needed=["量产良率", "客户验证"],
                    state="open",
                )
            ],
        )
        entries = load_registry(run_dir)
        assert resolve_record_id(entries, "Q1") == "Q2"
        before = (run_dir / "evidence_registry.jsonl").read_bytes()
        for invalid_json in (float("nan"), float("inf"), object()):
            noncanonical = record(
                "Q3",
                "question",
                question_text="非法扩展字段不得写入账本",
                priority="low",
                hypothesis="扩展字段需要规范 JSON 值",
                falsifier="规范序列化接受该值",
                evidence_needed=["规范序列化结果"],
                state="open",
                extension_value=invalid_json,
            )
            expect_error(
                lambda candidate=noncanonical: append_records(run_dir, [candidate]),
                "canonical JSON",
            )
            assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        malformed_correction = record(
            "Q3",
            "question",
            supersedes=["Q1"],
            question_text="错误修订字段不得进入引用校验",
            priority="low",
            hypothesis="修订标识必须是字符串",
            falsifier="列表修订标识被接受",
            evidence_needed=["输入校验结果"],
            state="open",
        )
        expect_error(
            lambda: append_records(run_dir, [malformed_correction]),
            "supersedes must be a non-empty string",
        )
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        foreign_correction = record(
            "Q3",
            "question",
            supersedes="Q2",
            created_by_skill="jvc-market-sizing",
            question_text="其他 skill 不得替代本 skill 问题",
            priority="low",
            hypothesis="修订所有权与原记录一致",
            falsifier="跨 skill 修订被接受",
            evidence_needed=["所有权校验结果"],
            state="open",
        )
        expect_error(
            lambda: append_records(run_dir, [foreign_correction]),
            "correction skill ownership",
        )
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        bad_source = record(
            "S1",
            "source",
            title="错误指纹来源",
            publisher="测试机构",
            author="测试作者",
            published_at="2026-07-01",
            accessed_at="2026-07-29T00:01:00Z",
            source_class="technical-paper",
            location="https://example.invalid/source",
            excerpt="测试摘录",
            definition="测试定义",
            geography="全球",
            sample="测试样本",
            statistical_scope="测试统计口径",
            stance="neutral",
            independence_key="test-source",
            content_fingerprint="0" * 64,
        )
        expect_error(lambda: append_records(run_dir, [bad_source]), "content_fingerprint mismatch")
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        valid_batch_record = record(
            "QU2",
            "query",
            question_id="Q2",
            direction="support",
            query_text="glass substrate yield evidence",
            tool_class="web-search",
            target_source_class="technical-paper",
            executed_at="2026-07-29T00:02:00Z",
            search_round=2,
            changed_core_judgment=False,
            result_count=0,
            outcome="no-result",
            result_summary="用于验证 batch 原子回滚",
        )
        bad = record(
            "C9",
            "claim",
            question_id="MISSING",
            claim_text="测试断裂引用",
            claim_kind="unknown",
            topic="technical_maturity",
            importance="decision_critical",
            support_source_ids=[],
            counter_source_ids=[],
            derived_from_claim_ids=[],
            scope="先进封装玻璃基板",
            confidence="unknown",
            reasoning="仅用于验证引用完整性",
            conflict_resolution="none",
            state="unverified",
        )
        expect_error(
            lambda: append_records(run_dir, [valid_batch_record, bad]),
            "unknown reference",
        )
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        assert "QU2" not in {entry["record_id"] for entry in load_registry(run_dir)}
        valid_claim = record(
            "C1",
            "claim",
            question_id="Q2",
            claim_text="玻璃基板量产良率仍需验证",
            claim_kind="agent_inference",
            topic="technical_maturity",
            importance="decision_critical",
            support_source_ids=[],
            counter_source_ids=[],
            derived_from_claim_ids=[],
            scope="先进封装玻璃基板",
            confidence="low",
            reasoning="仅用于验证 claim lineage",
            conflict_resolution="none",
            state="unverified",
        )
        append_records(run_dir, [valid_claim])
        before = (run_dir / "evidence_registry.jsonl").read_bytes()
        cyclic_correction = record(
            "C2",
            "claim",
            supersedes="C1",
            question_id="Q2",
            claim_text="修订后的良率判断",
            claim_kind="agent_inference",
            topic="technical_maturity",
            importance="decision_critical",
            support_source_ids=[],
            counter_source_ids=[],
            derived_from_claim_ids=["C1"],
            scope="先进封装玻璃基板",
            confidence="low",
            reasoning="修订不得在解析后派生自自身",
            conflict_resolution="none",
            state="unverified",
        )
        expect_error(
            lambda: append_records(run_dir, [cyclic_correction]),
            "claim lineage cycle",
        )
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        multi_cycle_a = {
            **valid_claim,
            "record_id": "C2",
            "claim_text": "派生判断 A",
            "derived_from_claim_ids": ["C1"],
        }
        multi_cycle_b = {
            **valid_claim,
            "record_id": "C3",
            "supersedes": "C1",
            "claim_text": "派生判断 B",
            "derived_from_claim_ids": ["C2"],
        }
        expect_error(
            lambda: append_records(run_dir, [multi_cycle_a, multi_cycle_b]),
            "claim lineage cycle",
        )
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        lock = run_dir / ".evidence_registry.jsonl.lock"
        lock.write_text("test-writer", encoding="ascii")
        expect_error(lambda: append_records(run_dir, [bad]), "another registry writer")
        assert (run_dir / "evidence_registry.jsonl").read_bytes() == before
        lock.unlink()
        lines = before.decode("utf-8").splitlines()
        changed = json.loads(lines[0])
        changed["subject"] = "被篡改"
        lines[0] = json.dumps(changed, ensure_ascii=False, sort_keys=True)
        (run_dir / "evidence_registry.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        expect_error(lambda: load_registry(run_dir), "fingerprint")


def source(source_id: str, source_class: str, independence_key: str) -> dict[str, object]:
    return record(
        source_id,
        "source",
        title=f"来源 {source_id}",
        publisher=f"机构 {independence_key}",
        author="测试作者",
        published_at="2026-07-01",
        accessed_at="2026-07-29T00:00:00Z",
        source_class=source_class,
        location=f"https://example.invalid/{source_id}",
        excerpt=f"与测试主张直接相关的最小摘录 {source_id}",
        definition="量产良率指符合客户交付规格的良品占比",
        geography="全球",
        sample="公开披露的量产项目",
        statistical_scope="截至 2026-07-01 的已披露项目",
        stance="neutral",
        independence_key=independence_key,
    )


def build_ready_fixture(root: Path) -> tuple[Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    run_dir = root / "run"
    report = root / "report.md"
    report.write_text("关键事实 [S1] [S2]\n", encoding="utf-8")
    init_registry(
        run_dir,
        "jvc-track-research",
        record(
            "SC1",
            "scope",
            subject="玻璃基板",
            decision="确定下一轮尽调重点",
            inclusions=["先进封装"],
            exclusions=["显示盖板"],
            geography="全球及中国",
            time_range="2024-2029",
            user_assumptions=[],
        ),
    )
    append_records(
        run_dir,
        [
            record(
                "Q1",
                "question",
                question_text="玻璃基板量产良率是否仍限制规模交付？",
                priority="high",
                hypothesis="良率限制规模交付",
                falsifier="量产证据证明良率不构成瓶颈",
                evidence_needed=["量产良率", "规模交付"],
                state="supported",
            ),
            record(
                "QU1",
                "query",
                question_id="Q1",
                direction="counter",
                query_text="玻璃基板 良率 不构成瓶颈",
                tool_class="web-search",
                target_source_class="company-filing",
                executed_at="2026-07-29T00:02:00Z",
                search_round=1,
                changed_core_judgment=False,
                result_count=1,
                outcome="captured",
                result_summary="找到一项满足来源类型要求的反向材料并已登记",
            ),
            record(
                "QU2",
                "query",
                question_id="Q1",
                direction="support",
                query_text="玻璃基板 量产 良率 交付",
                tool_class="web-search",
                target_source_class="technical-paper",
                executed_at="2026-07-29T00:02:30Z",
                search_round=2,
                changed_core_judgment=False,
                result_count=1,
                outcome="captured",
                result_summary="第二轮检索未改变良率仍为瓶颈的核心判断",
            ),
            source("S1", "regulatory-filing", "issuer-a"),
            source("S2", "technical-paper", "authors-b"),
            record(
                "C1",
                "claim",
                question_id="Q1",
                claim_text="现有公开证据仍指向量产良率瓶颈",
                claim_kind="third_party_fact",
                topic="technical_maturity",
                importance="decision_critical",
                support_source_ids=["S1", "S2"],
                counter_source_ids=[],
                derived_from_claim_ids=[],
                scope="先进封装玻璃基板",
                confidence="medium",
                reasoning="两类独立来源指向同一瓶颈",
                conflict_resolution="none",
                state="supported",
            ),
        ],
    )
    return run_dir, report


def add_gap(run_dir: Path) -> None:
    append_records(
        run_dir,
        [
            record(
                "Q2",
                "question",
                question_text="客户导入节奏能否在公开信息中独立验证？",
                priority="high",
                hypothesis="公开证据暂不足",
                falsifier="找到两类独立客户采用证据",
                evidence_needed=["客户采用", "量产时间"],
                state="gap",
            ),
            record(
                "QU3",
                "query",
                question_id="Q2",
                direction="support",
                query_text="玻璃基板 客户导入 量产 时间",
                tool_class="web-search",
                target_source_class="company-filing",
                executed_at="2026-07-29T00:04:00Z",
                search_round=1,
                changed_core_judgment=False,
                result_count=0,
                outcome="no-result",
                result_summary="未找到可独立验证客户导入节奏的披露",
            ),
            record(
                "QU4",
                "query",
                question_id="Q2",
                direction="counter",
                query_text="玻璃基板 客户延迟 取消 导入",
                tool_class="web-search",
                target_source_class="reputable-media",
                executed_at="2026-07-29T00:05:00Z",
                search_round=2,
                changed_core_judgment=False,
                result_count=0,
                outcome="no-result",
                result_summary="第二轮仍未找到可独立验证的采用或取消证据",
            ),
        ],
    )


def add_blocked_company_claim(run_dir: Path) -> None:
    append_records(
        run_dir,
        [
            record(
                "C2",
                "claim",
                question_id="Q1",
                claim_text="项目已经形成规模收入",
                claim_kind="company_claim",
                topic="commercialization",
                importance="decision_critical",
                support_source_ids=["S1"],
                counter_source_ids=[],
                derived_from_claim_ids=[],
                scope="规模收入",
                confidence="low",
                reasoning="仅有单一公司侧口径",
                conflict_resolution="none",
                state="supported",
            )
        ],
    )


def write_minimal_xlsx(
    path: Path,
    sheets: list[str],
    source_text: str | None,
    *,
    unreferenced_text: str | None = None,
    metadata_text: str = "",
) -> None:
    sheet_nodes = "".join(
        f'<sheet name="{name}" sheetId="{index}" r:id="rId{index}"/>'
        for index, name in enumerate(sheets, start=1)
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{sheet_nodes}</sheets></workbook>"
    )
    relationships = "".join(
        (
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
        for index, _ in enumerate(sheets, start=1)
    )
    shared_values = [
        value
        for value in (source_text, unreferenced_text)
        if value is not None
    ]
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            (
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f"{relationships}"
                + (
                    f'<Relationship Id="rId{len(sheets) + 1}" '
                    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" '
                    'Target="sharedStrings.xml"/>'
                    if shared_values
                    else ""
                )
                + "</Relationships>"
            ),
        )
        for index, name in enumerate(sheets, start=1):
            cell = (
                '<row r="1"><c r="A1" t="s"><v>0</v></c></row>'
                if name == "sources" and source_text is not None
                else ""
            )
            archive.writestr(
                f"xl/worksheets/sheet{index}.xml",
                (
                    '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                    f"<sheetData>{cell}</sheetData></worksheet>"
                ),
            )
        if shared_values:
            archive.writestr(
                "xl/sharedStrings.xml",
                (
                    '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                    + "".join(f"<si><t>{escape(value)}</t></si>" for value in shared_values)
                    + "</sst>"
                ),
            )
        archive.writestr(
            "docProps/core.xml",
            f"<coreProperties><description>{escape(metadata_text)}</description></coreProperties>",
        )


def write_minimal_docx(
    path: Path,
    text: str,
    *,
    metadata_text: str = "",
    footnote_text: str | None = None,
) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "word/document.xml",
            (
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                f"<w:body><w:p><w:r><w:t>{escape(text)}</w:t></w:r></w:p></w:body></w:document>"
            ),
        )
        if footnote_text is not None:
            archive.writestr(
                "word/footnotes.xml",
                (
                    '<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    f"<w:footnote w:id=\"1\"><w:p><w:r><w:t>{escape(footnote_text)}</w:t>"
                    "</w:r></w:p></w:footnote></w:footnotes>"
                ),
            )
        archive.writestr(
            "docProps/core.xml",
            f"<coreProperties><description>{escape(metadata_text)}</description></coreProperties>",
        )


def check_office_artifacts(root: Path) -> None:
    comps = root / "03-comps-dd.md"
    comps.write_text("# 竞品尽调\n\n[S1] [S2]\n", encoding="utf-8")
    findings, fingerprints = validate_artifacts(
        load_profile("jvc-comps-dd"),
        [comps],
        {"S1", "S2"},
        {"S1", "S2"},
    )
    assert findings == []
    assert fingerprints[0]["path"] == str(comps.resolve())

    wrong_name = root / "wrong-name.md"
    wrong_name.write_text("# 竞品尽调\n\n[S1] [S2]\n", encoding="utf-8")
    findings, _ = validate_artifacts(
        load_profile("jvc-comps-dd"),
        [wrong_name],
        {"S1", "S2"},
        {"S1", "S2"},
    )
    assert any(
        finding["rule"] == "artifact_names" for finding in findings
    ), findings

    csv_model = root / "roi-model.csv"
    csv_model.write_text("metric,value,source_id\nrevenue,100,[S1]\n", encoding="utf-8")
    findings, fingerprints = validate_artifacts(
        load_profile("jvc-roi-modeler"),
        [csv_model],
        {"S1"},
        {"S1"},
    )
    assert findings == []
    assert fingerprints[0]["path"] == str(csv_model.resolve())

    document = root / "notes.docx"
    write_minimal_docx(document, "[S1]", metadata_text="[S999]")
    findings, _ = validate_artifacts(
        load_profile("jvc-meeting-notes"),
        [document],
        {"S1"},
        {"S1"},
    )
    assert findings == []

    workbook_profile = {
        "artifact_policy": {
            "allowed_suffixes": [".xlsx"],
            "required_names": [],
            "required_sheets": ["sources"],
        }
    }
    metadata_only_workbook = root / "metadata-only.xlsx"
    write_minimal_xlsx(
        metadata_only_workbook,
        workbook_profile["artifact_policy"]["required_sheets"],
        None,
        unreferenced_text="[S1] [S2] [S999]",
        metadata_text="[S1] [S2] [S999]",
    )
    findings, _ = validate_artifacts(
        workbook_profile,
        [metadata_only_workbook],
        {"S1", "S2"},
        {"S1", "S2"},
    )
    rules = {finding["rule"] for finding in findings}
    assert "artifact_source_coverage" in rules
    assert "artifact_source_reference" not in rules

    missing_sources_workbook = root / "missing-sources.xlsx"
    write_minimal_xlsx(
        missing_sources_workbook,
        [
            sheet
            for sheet in workbook_profile["artifact_policy"]["required_sheets"]
            if sheet != "sources"
        ],
        None,
    )
    findings, _ = validate_artifacts(
        workbook_profile,
        [missing_sources_workbook],
        {"S1"},
        {"S1"},
    )
    rules = {finding["rule"] for finding in findings}
    assert "artifact_workbook_sheets" in rules
    assert "artifact_unreadable" not in rules

    metadata_only_document = root / "metadata-only.docx"
    write_minimal_docx(
        metadata_only_document,
        "正文没有来源引用",
        metadata_text="[S1] [S999]",
    )
    findings, _ = validate_artifacts(
        load_profile("jvc-meeting-notes"),
        [metadata_only_document],
        {"S1"},
        {"S1"},
    )
    rules = {finding["rule"] for finding in findings}
    assert "artifact_source_coverage" in rules
    assert "artifact_source_reference" not in rules

    missing_document = root / "missing-document.docx"
    with zipfile.ZipFile(missing_document, "w") as archive:
        archive.writestr(
            "word/styles.xml",
            '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>',
        )
    findings, _ = validate_artifacts(
        load_profile("jvc-meeting-notes"),
        [missing_document],
        {"S1"},
        {"S1"},
    )
    rules = {finding["rule"] for finding in findings}
    assert "artifact_docx" in rules
    assert "artifact_unreadable" not in rules

    footnoted_document = root / "footnoted.docx"
    write_minimal_docx(
        footnoted_document,
        "正文引用见脚注",
        metadata_text="[S999]",
        footnote_text="[S1]",
    )
    findings, _ = validate_artifacts(
        load_profile("jvc-meeting-notes"),
        [footnoted_document],
        {"S1"},
        {"S1"},
    )
    assert findings == []


def check_ready_correction_invalidates(root: Path) -> None:
    run_dir, report = build_ready_fixture(root)
    assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "ready"
    ready_entry = json.loads((run_dir / "audit.json").read_text(encoding="utf-8"))["audits"][0]
    append_records(
        run_dir,
        [
            record(
                "C2",
                "claim",
                supersedes="C1",
                question_id="Q1",
                claim_text="修订后仍认为量产良率限制规模交付",
                claim_kind="third_party_fact",
                topic="technical_maturity",
                importance="decision_critical",
                support_source_ids=["S1", "S2"],
                counter_source_ids=[],
                derived_from_claim_ids=[],
                scope="先进封装玻璃基板",
                confidence="medium",
                reasoning="两类独立来源仍指向同一瓶颈",
                conflict_resolution="none",
                state="supported",
            )
        ],
    )
    assert not saved_audit_is_valid(ready_entry, load_registry(run_dir))
    assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "ready"


def query(
    record_id: str,
    question_id: str,
    search_round: int,
    direction: str,
    *,
    created_by_skill: str,
) -> dict[str, object]:
    return record(
        record_id,
        "query",
        created_by_skill=created_by_skill,
        question_id=question_id,
        direction=direction,
        query_text=f"{question_id} 第 {search_round} 轮检索",
        tool_class="web-search",
        target_source_class="reputable-media",
        executed_at=f"2026-07-29T00:{10 + search_round:02d}:00Z",
        search_round=search_round,
        changed_core_judgment=False,
        result_count=0,
        outcome="no-result",
        result_summary="未找到改变当前判断的新证据",
    )


def check_skill_isolation(root: Path) -> None:
    run_dir, report = build_ready_fixture(root / "foreign-gap")
    append_records(
        run_dir,
        [
            record(
                "Q9",
                "question",
                created_by_skill="jvc-market-sizing",
                question_text="无关市场规模问题是否存在公开证据缺口？",
                priority="high",
                hypothesis="公开证据不足",
                falsifier="找到完整市场规模披露",
                evidence_needed=["市场规模"],
                state="gap",
            ),
            query(
                "QU9",
                "Q9",
                1,
                "support",
                created_by_skill="jvc-market-sizing",
            ),
        ],
    )
    result = audit_run(run_dir, "jvc-track-research", [report])
    assert result["status"] == "ready"
    assert not any(finding["message"] == "Q9" for finding in result["findings"])

    run_dir, report = build_ready_fixture(root / "foreign-answer")
    append_records(
        run_dir,
        [
            record(
                "Q9",
                "question",
                question_text="新增技术判断是否已由本 skill 形成主张？",
                priority="high",
                hypothesis="本 skill 已形成主张",
                falsifier="只有其他 skill 回答",
                evidence_needed=["本 skill 主张"],
                state="supported",
            ),
            query(
                "QU9",
                "Q9",
                1,
                "support",
                created_by_skill="jvc-track-research",
            ),
            query(
                "QU10",
                "Q9",
                2,
                "counter",
                created_by_skill="jvc-track-research",
            ),
            record(
                "C9",
                "claim",
                created_by_skill="jvc-market-sizing",
                question_id="Q9",
                claim_text="其他 skill 对问题作出回答",
                claim_kind="agent_inference",
                topic="technical_maturity",
                importance="decision_critical",
                support_source_ids=["S1", "S2"],
                counter_source_ids=[],
                derived_from_claim_ids=[],
                scope="其他 skill 回答",
                confidence="medium",
                reasoning="仅用于验证 skill 隔离",
                conflict_resolution="none",
                state="supported",
            ),
        ],
    )
    result = audit_run(run_dir, "jvc-track-research", [report])
    assert result["status"] == "blocked"
    assert {
        "rule": "resolved_question_without_claim",
        "severity": "block",
        "message": "Q9",
    } in result["findings"]
    assert result["dependency_audits"] == []


def company_source(
    source_id: str,
    source_class: str,
    independence_key: str,
) -> dict[str, object]:
    return record(
        source_id,
        "source",
        title="同一稿源的商业化披露",
        publisher="同一发布方",
        author="同一作者",
        published_at="2026-07-01",
        accessed_at="2026-07-29T00:00:00Z",
        source_class=source_class,
        location="https://example.invalid/same-origin",
        excerpt="同一段商业化文字",
        definition="规模收入指经审计确认的产品收入",
        geography="中国",
        sample="同一项目",
        statistical_scope="2026 年上半年",
        stance="support",
        independence_key=independence_key,
    )


def add_company_evidence(
    run_dir: Path,
    report: Path,
    sources: list[dict[str, object]],
) -> None:
    append_records(
        run_dir,
        [
            *sources,
            record(
                "C2",
                "claim",
                question_id="Q1",
                claim_text="公司已形成规模收入",
                claim_kind="company_claim",
                topic="commercialization",
                importance="decision_critical",
                support_source_ids=["S3", "S4"],
                counter_source_ids=[],
                derived_from_claim_ids=[],
                scope="规模收入",
                confidence="medium",
                reasoning="公司材料与外部报道共同支持",
                conflict_resolution="none",
                state="supported",
            ),
        ],
    )
    report.write_text("关键事实 [S1] [S2] [S3] [S4]\n", encoding="utf-8")


def check_company_independence(root: Path) -> None:
    run_dir, report = build_ready_fixture(root / "same-origin")
    add_company_evidence(
        run_dir,
        report,
        [
            company_source("S3", "company-material", "company-key"),
            company_source("S4", "reputable-media", "media-key"),
        ],
    )
    result = audit_run(run_dir, "jvc-track-research", [report])
    assert result["status"] == "blocked"
    assert any(
        finding["rule"] == "company_claim_unverified"
        and finding["message"] == "C2"
        for finding in result["findings"]
    )

    run_dir, report = build_ready_fixture(root / "independent")
    add_company_evidence(
        run_dir,
        report,
        [
            source("S3", "company-material", "company-key"),
            source("S4", "reputable-media", "media-key"),
        ],
    )
    result = audit_run(run_dir, "jvc-track-research", [report])
    assert result["status"] == "ready"
    assert not any(
        finding["rule"] == "company_claim_unverified"
        for finding in result["findings"]
    )


def check_reserved_artifact_path(root: Path) -> None:
    run_dir, report = build_ready_fixture(root)
    reserved_report = run_dir / "audit.md"
    reserved_report.write_bytes(report.read_bytes())
    before = reserved_report.read_bytes()
    failed = run_cli(
        "audit",
        "--run-dir",
        str(run_dir),
        "--skill",
        "jvc-track-research",
        "--artifact",
        str(reserved_report),
    )
    assert failed.returncode == 1
    assert failed.stderr.startswith("research core error:")
    assert reserved_report.read_bytes() == before
    assert not (run_dir / "audit.json").exists()


def check_aliased_reserved_artifact_path(root: Path) -> None:
    run_dir, report = build_ready_fixture(root)
    aliased_report = run_dir / "Audit.md"
    aliased_report.write_bytes(report.read_bytes())
    before = aliased_report.read_bytes()
    assert core.paths_conflict(aliased_report, run_dir / "audit.md")
    failed = run_cli(
        "audit",
        "--run-dir",
        str(run_dir),
        "--skill",
        "jvc-track-research",
        "--artifact",
        str(aliased_report),
    )
    assert failed.returncode == 1
    assert failed.stderr.startswith("research core error:")
    assert aliased_report.read_bytes() == before
    assert not (run_dir / "audit.json").exists()


def check_audit_output_preflight(root: Path) -> None:
    run_dir, report = build_ready_fixture(root)
    markdown = run_dir / "audit.md"
    sentinel = b"existing audit markdown\n"
    markdown.write_bytes(sentinel)
    (run_dir / "audit.json").mkdir()
    failed = run_cli(
        "audit",
        "--run-dir",
        str(run_dir),
        "--skill",
        "jvc-track-research",
        "--artifact",
        str(report),
    )
    assert failed.returncode == 1
    assert failed.stderr.startswith("research core error:")
    assert markdown.read_bytes() == sentinel


def check_trusted_audit_commit(root: Path, existing: bool) -> None:
    run_dir, report = build_ready_fixture(root)
    markdown = run_dir / "audit.md"
    json_path = run_dir / "audit.json"
    sentinel = b"existing audit markdown\n"
    old_json = None
    if existing:
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "ready"
        old_json = json_path.read_bytes()
        markdown.write_bytes(sentinel)
    original = core.os.replace

    def fail_json_publish(source: Path, target: Path) -> None:
        if Path(target).name == "audit.json":
            raise OSError("forced audit.json publish failure")
        original(source, target)

    core.os.replace = fail_json_publish
    failed = False
    try:
        audit_run(run_dir, "jvc-track-research", [report])
    except OSError as exc:
        assert "audit.json" in str(exc)
        failed = True
    finally:
        core.os.replace = original
    assert failed
    if existing:
        assert json_path.read_bytes() == old_json
        assert markdown.read_bytes() == sentinel
    else:
        assert not json_path.exists()
        assert not markdown.exists()
    assert not [
        path
        for path in run_dir.iterdir()
        if path.name.startswith(".audit.")
    ]


def check_audit() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        run_dir, report = build_ready_fixture(root)
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "ready"
        ready_entry = json.loads((run_dir / "audit.json").read_text(encoding="utf-8"))["audits"][0]
        audit_markdown = (run_dir / "audit.md").read_text(encoding="utf-8")
        assert ready_entry["skill"] in audit_markdown
        assert str(ready_entry["ledger_sequence"]) in audit_markdown
        assert ready_entry["status"] in audit_markdown
        assert not saved_audit_is_valid({}, load_registry(run_dir))
        changed_findings = {**ready_entry, "findings": [{"rule": "x", "severity": "partial", "message": "y"}]}
        changed_status = {**ready_entry, "status": "partial"}
        assert not saved_audit_is_valid(changed_findings, load_registry(run_dir))
        assert not saved_audit_is_valid(changed_status, load_registry(run_dir))

        append_records(
            run_dir,
            [
                source(
                    "S3",
                    "market-database",
                    "unrelated-market-source",
                )
                | {"created_by_skill": "jvc-market-sizing"}
            ],
        )
        assert saved_audit_is_valid(ready_entry, load_registry(run_dir))
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "ready"
        ready_entry = next(
            entry
            for entry in json.loads(
                (run_dir / "audit.json").read_text(encoding="utf-8")
            )["audits"]
            if entry["skill"] == "jvc-track-research"
            and entry["ledger_sequence"] == len(load_registry(run_dir))
        )
        append_records(
            run_dir,
            [
                source(
                    "S4",
                    "market-database",
                    "unrelated-market-source-revised",
                )
                | {
                    "created_by_skill": "jvc-market-sizing",
                    "supersedes": "S3",
                }
            ],
        )
        assert saved_audit_is_valid(ready_entry, load_registry(run_dir))

        ic_report = root / "ic.md"
        ic_report.write_text("投资结论 [S1] [S2]\n", encoding="utf-8")
        append_records(
            run_dir,
            [
                record(
                    "C3",
                    "claim",
                    created_by_skill="jvc-ic-memo",
                    question_id="Q1",
                    claim_text="良率瓶颈仍应列为投资委员会核心风险",
                    claim_kind="agent_inference",
                    topic="technical_maturity",
                    importance="decision_critical",
                    support_source_ids=["S1", "S2"],
                    counter_source_ids=[],
                    derived_from_claim_ids=["C1"],
                    scope="先进封装玻璃基板",
                    confidence="medium",
                    reasoning="继承已审研究主张并收窄为投资风险",
                    conflict_resolution="none",
                    state="supported",
                )
            ],
        )
        assert saved_audit_is_valid(ready_entry, load_registry(run_dir))
        assert audit_run(run_dir, "jvc-ic-memo", [ic_report])["status"] == "ready"
        audit_entries = json.loads((run_dir / "audit.json").read_text(encoding="utf-8"))["audits"]
        ic_entry = next(entry for entry in audit_entries if entry["skill"] == "jvc-ic-memo")
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "ready"
        assert not saved_audit_is_valid(ic_entry, load_registry(run_dir))
        assert audit_run(run_dir, "jvc-ic-memo", [ic_report])["status"] == "ready"
        audit_entries = json.loads((run_dir / "audit.json").read_text(encoding="utf-8"))["audits"]
        ic_entry = next(entry for entry in audit_entries if entry["skill"] == "jvc-ic-memo")

        original_report = report.read_text(encoding="utf-8")
        report.write_text(original_report + "变更\n", encoding="utf-8")
        records = load_registry(run_dir)
        assert not saved_audit_is_valid(ready_entry, records)
        assert not saved_audit_is_valid(ic_entry, records)
        report.write_text(original_report, encoding="utf-8")
        assert saved_audit_is_valid(ready_entry, records)
        assert saved_audit_is_valid(ic_entry, records)

        add_gap(run_dir)
        records = load_registry(run_dir)
        assert not saved_audit_is_valid(ready_entry, records)
        assert not saved_audit_is_valid(ic_entry, records)
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "blocked"
        report.write_text("研究状态：partial\n" + original_report, encoding="utf-8")
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "partial"

        add_blocked_company_claim(run_dir)
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "blocked"
        write_waiver(
            run_dir,
            skill="jvc-track-research",
            rule="company_claim_unverified",
            reason="用户只需要保留公司口径用于下一轮访谈",
            scope="C2",
            approved_by="test-user",
            approved_at="2026-07-29T00:06:00Z",
            residual_risk="商业化仍未被第三方验证",
        )
        assert audit_run(run_dir, "jvc-track-research", [report])["status"] == "partial"
        expect_error(
            lambda: write_waiver(
                run_dir,
                skill="jvc-track-research",
                rule="artifact_missing",
                reason="测试不可豁免规则",
                scope="report.md",
                approved_by="test-user",
                approved_at="2026-07-29T00:07:00Z",
                residual_risk="产物仍然缺失",
            ),
            "cannot be waived",
        )

        check_office_artifacts(root)

    with TemporaryDirectory() as temporary:
        check_ready_correction_invalidates(Path(temporary))
    with TemporaryDirectory() as temporary:
        check_skill_isolation(Path(temporary))
    with TemporaryDirectory() as temporary:
        check_company_independence(Path(temporary))
    with TemporaryDirectory() as temporary:
        check_reserved_artifact_path(Path(temporary))
    with TemporaryDirectory() as temporary:
        check_aliased_reserved_artifact_path(Path(temporary))
    with TemporaryDirectory() as temporary:
        check_audit_output_preflight(Path(temporary))
    with TemporaryDirectory() as temporary:
        check_trusted_audit_commit(Path(temporary), False)
    with TemporaryDirectory() as temporary:
        check_trusted_audit_commit(Path(temporary), True)


if __name__ == "__main__":
    check_engine_contract()
    check_cli()
    check_ledger()
    check_audit()
    print("research core ledger and audit checks passed")

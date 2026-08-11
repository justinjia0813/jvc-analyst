# Task 8 worker_done 报告 — Research Report 受审计输出组装器 + IC Memo 输入映射

> 工作区：`feature/overall-promo` 共享 worktree（未提交、未推送、未创建 PR/发布）。
> 本文件由 dispatch 生成，供 coordinator 复核；视觉复验必须由能查看图片的 agent/人完成。

## 1. 做了什么

1. **Research Report 两阶段合同**（`skills/jvc-research-report/SKILL.md` v4.0.0、`references/output-contract.md`）：
   - 阶段一 组装：从 Track Research + Knowledge Tree + Market Sizing（+ 可选 Comps/DD）组装 canonical `research-report.md`；保留来源标识、继承上游主张、展示覆盖缺口、禁止联网补研究/新增事实数字。
   - 阶段二 发布：`build_report.py` 只读渲染；渲染器未改动（不重写正文、不联网，`local_url_fetcher` 仅放行 `data:`）。
   - 直接发布模式：已有完整 canonical Markdown 直接进渲染。
2. **新增只读 stdlib 校验器** `skills/jvc-research-report/scripts/validate_assembly.py`：四类检查（来源 ID 继承、归一化数字继承、内在标签继承、覆盖缺口可见），数字归一化复用 `skills/jvc-ic-memo/scripts/validate_final.py` 的 `numbers`（import，不改 IC 语义）。
3. **TDD 扩展** `scripts/check_package.py`：真实临时上游 + 候选反例（新来源 ID、新数字、不支持标签、上游漂移、缺口未命名、必需输入缺失）全部红→绿。
4. **新增 Research Core Markdown profile** `skills/jvc-research-core/profiles/jvc-research-report.json`（`required_names: ["research-report.md"]`）+ research-core manifest 说明更新。
5. **示例**：新增 canonical 组装示例 `examples/research-report-example/research-report.md`（从 `track-research-example.md` + `knowledge-tree-example/` + `market-sizing-example.csv` + `comps-dd-example.md` 组装）；旧 `report.md` 保留为降级历史 fixture，不再被任何活跃合同引用。
6. **Skill 附属件**：`manifest.json`（output_contract 加入 `research-report.md`）、`agents/interface.yaml`、`evals/semantic_config.json`、`evals/trigger_cases.json`、`templates/industry-report.md`（含上游到章节映射与覆盖缺口章节）。
7. **IC Memo 输入映射**（`skills/jvc-ic-memo/SKILL.md`、`references/ic-memo-template.md`、`scripts/check-ic-memo-assets.sh`）：活跃输入改为 `03-comps-dd.md`、`market-sizing.csv`、`05-roi-modeler.csv`；预审 → 用户明确批准（"预审通过"）→ 干净终版闸门、`validate_final.py`、`ready` 语义全部保留，未放松。
8. **依赖视图**：`skills/jvc-deal-flow/references/workflow-contract.md` 两条依赖边更新（IC Memo 输入清单 + Research Report 两阶段组装）。
9. **一致性与治理**：`evals/output/cases.json` research-report case 更新为新合同；`check-governance.py --write-hash` 刷新 trust 哈希（我的改动全部落在 hash scope 内，属合法刷新，Task 9 会再刷一次）。

## 2. 红绿证据（TDD）

**红（初始）：** `python3 skills/jvc-research-report/scripts/check_package.py` → `AssertionError: SKILL.md missing two-stage wording: 组装`（validate_assembly.py 缺失、SKILL 无两阶段文本、示例 research-report.md 缺失）。

**绿（最终，全部 exit 0）：**

```bash
python3 skills/jvc-research-report/scripts/check_package.py        # PASS（含 TDD 反例 + 示例渲染 + 组装校验）
./scripts/check-ic-memo-assets.sh                                  # OK（新输入映射 + 闸门 + 无旧 workbook 残留）
python3 skills/jvc-ic-memo/scripts/check_package.py                # PASS
python3 skills/jvc-research-core/scripts/check_package.py          # PASS
python3 scripts/check-research-core-install.py                     # PASS
git diff --check                                                   # OK
```

**邻近检查（全部 exit 0）：** `check-skill-evals.py`（15 trigger / 16 output）、`check-governance.py`、`check-jvc-assets.sh`、`deal-flow check_package`、`comps-dd/market-sizing/track-research/prescreen/roi-modeler assets`、`knowledge-tree-builder check_package`。

**校验器反例（check_package 内自动化）：**
- 忠实组装 → exit 0；`new source ID [S9]` → exit 1 "source absent from upstream: S9"；`new number 999 万元` → exit 1 "number absent from upstream: 999万元"；`[创始人自述]`（上游无）→ exit 1 "label absent from upstream"；上游数字 420→520 后原报告 → exit 1（证明按真实上游内容比对，非静态字符串）；缺 Comps/DD 且缺口未命名 → exit 1；命名后 → exit 0；缺必需上游 → exit 2。

## 3. 渲染与视觉检查状态（重要）

- `examples/research-report-example/research-report.md` → PDF 渲染成功：14 页 A4，`structure/source/render/bookmark: pass`；仅剩预期 warning：`table has 7 columns`（来源索引 7 列表格，模板固有格式）。
- 机械验证（已做）：11 个 canonical 章节 + 覆盖缺口章节按序出现并带书签页码；关键数字（420 万元、3.2 亿元、12 亿美元、80000000000、100000000000、0.10）在 PDF 文本中；SVG 图以 `data:image/svg+xml;base64` 嵌入（HTML 含 `<figure><img>`）；FACT/INFERENCE/OPEN QUESTION callout 各 1/1/2 渲染；封面元数据完整。
- **视觉检查（未做，必须复核）：** 当前模型的图像支持不可用（`read` 图片返回 "model does not support images"），我**没有**逐页目检布局/裁切/间距/缺失/Mermaid/一致性，**不伪称已检查**。
- 视觉产物路径（交给 coordinator 复验）：
  - 页面图：`reports/task8-visual/page-01.png` … `page-14.png`（827×1170 RGB，100dpi）
  - PDF：`reports/task8-visual/report.pdf`（14 页 A4）
  - HTML 预览：`reports/task8-visual/report.html`
  - 构建日志：`reports/task8-visual/build-report.txt`

## 4. 限制与说明

- **视觉复验是未完成项**：请 coordinator 用支持图像的 agent 或人工逐页检查 `reports/task8-visual/page-*.png`（重点：第 7 页 SVG 图嵌入与图注邻接、第 13 页覆盖缺口表格、第 14 页 7 列来源索引是否横向溢出、分页/孤行、间距一致性）。
- Mermaid：canonical 报告不使用 Mermaid（渲染器不支持）；知识树上游的 `{mermaid}` 块仅存于上游五文件包，组装时以本地静态 SVG 呈现——如需 Mermaid 渲染支持，属范围外，须先 ask。
- `validate_assembly.py` 未纳入 `reports/trust_report.json` 脚本清单（Task 9 的 "更新信任清单" 步骤负责；governance 检查不因未注册而失败）。
- 新文件（`research-report.md`、`validate_assembly.py`、profile、`reports/task8-visual/`）均为 untracked；未提交是本次约束，由主代理后续统一提交。
- 未读取/未修改 `roi-modeler-template.xlsx`；未提交、推送、PR、merge、release。

## 5. 改动文件

- 修改：`skills/jvc-research-report/{SKILL.md, manifest.json, agents/interface.yaml, evals/semantic_config.json, evals/trigger_cases.json, templates/industry-report.md, references/output-contract.md, scripts/check_package.py}`
- 新增：`skills/jvc-research-report/scripts/validate_assembly.py`、`skills/jvc-research-core/profiles/jvc-research-report.json`、`examples/research-report-example/research-report.md`、`reports/task8-visual/*`
- 修改：`skills/jvc-ic-memo/SKILL.md`、`skills/jvc-ic-memo/references/ic-memo-template.md`、`skills/jvc-deal-flow/references/workflow-contract.md`、`scripts/check-ic-memo-assets.sh`、`evals/output/cases.json`、`skills/jvc-research-core/manifest.json`、`reports/trust_report.json`、`reports/trust_report.md`
- 保留（降级历史 fixture，不再被活跃合同引用）：`examples/research-report-example/report.md`

# Task8 对抗修复 worker_done 报告 — jvc-research-report 组装校验器

> 工作区：`feature/overall-promo` 共享 worktree。未提交、未推送、未 PR/merge/release；
> 未触碰 `roi-modeler-template.xlsx`（从未读取/写入）；未实现 sidecar/签名/通用 YAML/claim 框架。

## 1. 红绿证据（严格 TDD）

**红（初始）：** 先把 Task8 对抗审查 1a–1h 的复现反例加入
`skills/jvc-research-report/scripts/check_package.py`（新 `check_assembly_adversarial`，
真实临时上游 + 子进程跑 `validate_assembly.py`），运行得：
`AssertionError: 1a label accepted: [模型估算]`（随后 1b/1c/1d… 逐项红灯）。

**绿（最终，全部 exit 0）：**

```
python3 skills/jvc-research-report/scripts/check_package.py   → PASS（原 6 项 + 新增 1a-1h 反例）
./scripts/check-ic-memo-assets.sh                             → rc=0
python3 skills/jvc-ic-memo/scripts/check_package.py           → rc=0
python3 skills/jvc-research-core/scripts/check_package.py     → rc=0
python3 scripts/check-research-core-install.py                → rc=0
git diff --check                                              → rc=0
```

**邻近（全部 rc=0）：** `check-skill-evals.py`（15 trigger / 16 output）、
`check-governance.py`（--write-hash 刷新后）、`check-jvc-assets.sh`、deal-flow 与
knowledge-tree-builder `check_package.py`、comps-dd/market-sizing/track-research/
prescreen/roi-modeler/bear/bull/talk-notes assets。

**对抗反例逐项（修复后，均按审查预期）：**

| 项 | 反例 | 修复后 |
| --- | --- | --- |
| 1a | 正文引入 `[模型估算]`/`[未知/待验证]`/`[用户观察]`/`[用户假设]` | rc=1 `label absent from upstream` |
| 1a | 全角 `【模型估算】` 对校验器不可见 | rc=1（MARKER 同时扫 `【...】`，半/全角等价继承） |
| 1a | 未知关键字标签 `[自述]`/`[已核实]`/`[访谈]` | rc=1 `unknown evidence label` |
| 1a | 上游 CSV notes 写全角 `【模型估算】`、报告用半角 | rc=0（归一化后可继承） |
| 1b | 正文 `[模型估算 999]` 数字逃逸 | rc=1（`number absent from upstream: 999` + 未知标签双报） |
| 1c | 来源索引行 `\| S1 \| 来源甲（模型估算 999） \|` | rc=1 `number absent from upstream: 999` |
| 1d | frontmatter `市场规模摘要: 999 亿元` 未知键 | rc=1 `unknown frontmatter key`；`cover_image: null` 等白名单键 rc=0 |
| 1e | 直接发布换数字 999999 亿元 | build_report 未改（兼容不变，rc=0），文档显式声明信任边界 |
| 1f | 上游 CSV 年列 `2026` vs 正文 `2026 年` | rc=0（四位年份 N 与 N年 等价） |
| 1f | 上游 `420 万元` vs 正文 `0.042 亿元` | rc=1 保守拒绝，错误提示 `疑似单位表示不一致：上游为 420万元` |
| 1g | knowledge-tree 目录含 `binary.bin`（非 UTF-8） | rc=2 `cannot read knowledge-tree: binary.bin`，无 Traceback |
| 1g | 目录含 chmod 000 文件 | rc=2 `cannot read knowledge-tree: noaccess.md: Permission denied`，无 Traceback |
| 1h | CSV `sources,"S7, S8",...` 带引号逗号 | 改用 `csv.reader`，S7/S8 正常登入，报告引用 [S7] rc=0 |
| 2a | 用上游 token 拼新主张（500 家 + 420 万元） | rc=0（set-based 边界，文档化非错误） |

## 2. 最小根因修复（validate_assembly.py 重写，仅此脚本 + 测试 + 文档）

- **1a**：`INTERNAL_LABELS` 增补 `[模型估算] [未知/待验证] [用户观察] [用户假设]`；
  `MARKER` 扩展为同时匹配半角 `[...]` 与全角 `【...】`；标签比对与上游文本均做
  `【】→[]` 归一化；新增 `LABEL_KEYWORDS`（估算|未知|待验证|观察|假设|自述|推测|
  核实|访谈），含关键字但不在白名单的未知标签一律 `unknown evidence label` 报错。
- **1b**：报告侧新增 `report_numbers()`，只移除 `[S<n>]` 来源引用（不复用 IC 的
  NUMBER_METADATA 剥离标签括号），标签括号内数字参与继承；上游侧仍用
  `validate_final.numbers` 原语义（IC 语义零改动）。
- **1c**：数字继承作用到「claim 正文 + 清理后的来源索引」全文；来源索引的日期
  （YYYY-MM-DD）、URL、来源 ID 单元格视为元数据豁免（否则 tracked example 的
  虚构日期/URL 会误报），描述单元格中的其他数字照常参与继承。
- **1d**：组装路径 frontmatter 只允许
  title/subtitle/date/authors/sector/region/classification/cover_image/disclaimer
  顶层键，未知键拒绝；`build_report.py` 零改动（直接发布仍兼容接受额外键）。
- **1f**：`expand_year_tokens` 只做四位年份 `N`↔`N年` 等价；亿/万 不做换算，新增
  `scale_unit_hint` 在错误信息提示疑似单位表示不一致并给出上游单位表示。
- **1g**：knowledge-tree 目录循环逐文件 try/except（OSError/UnicodeError）→
  `AssemblyError("cannot read knowledge-tree: <文件名>")`，无 traceback。
- **1h**：sources 段改用 stdlib `csv.reader`（`io.StringIO`），row_id 单元格内全部
  `S<n>` token 登入（支持 `"S1, S4"`）。

## 3. 文档边界（1e/2a，仅文档、无代码）

- SKILL.md 阶段二 + output-contract.md「两阶段合同」：直接发布信任用户对 canonical
  的声明，`build_report.py` 只跑 renderer 内部一致性，不证明 assembly/Research Core
  继承；需证据继承必须提供上游并运行 `validate_assembly.py`。
- output-contract.md 新增「校验边界（set-based 继承）」：集合式 token 继承不能证明
  重组句子的语义等价，主张级审计仍需上游 claim 与人工复核。
- 未实现 sidecar、签名、`validated_by` 强制、通用 YAML/claim 框架（审查 1e 的
  sidecar 建议被任务边界明确排除）。

## 4. 文件

- 修改：`skills/jvc-research-report/scripts/validate_assembly.py`（重写）、
  `scripts/check_package.py`（新增 check_assembly_adversarial 1a–1h 反例）、
  `skills/jvc-research-report/SKILL.md`、`references/output-contract.md`、
  `reports/trust_report.json` + `reports/trust_report.md`（governance hash 合法刷新：
  改动全部落在 hash scope 内，刷新前基线为绿）。
- 未改：`build_report.py`、`validate_final.py`（IC）、canonical 示例正文、
  `roi-modeler-template.xlsx`（从未触碰）。

## 5. 风险与留给协调者的备注

- 视觉：renderer、canonical 示例、brand 均未变；`check_tracked_fixture` 在门禁 1
  中确定性重渲染示例 PDF 并断言产物契约，输出与 `reports/task8-visual/*` 旧产物一致，
  **无需重渲染**。
- 1d 的 frontmatter 键解析是行级正则（validator 保持 stdlib-only，不引入 yaml）：
  仅检查列 0 的 `key: value` 行；带引号键、数字键（如 `2026: x`）等异形 YAML 不报。
- 1a 关键字拒绝是保守设计：正文出现 `[估算结果](url)` 这类含关键字的 markdown 链接
  文本会被当作未知标签报错；当前 canonical 合同（链接只在来源索引）无此用法，
  tracked example 已通过，未为此放宽。
- 审查 §4 的 Task9 治理残留（validate_assembly.py 未进 trust script_inventory、
  evidence fixture 迁移）明确留给 Task9，本任务未越界处理。
- 所有改动未提交、未推送，与共享工作区其他脏改动共存；`--write-hash` 只更新
  trust_report 两文件的 hash/date 字段。

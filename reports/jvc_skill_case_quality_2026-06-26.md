# JVC Skill Case Quality Review

日期：2026-06-26

结论：12 个 `jvc-*` skill 的路由和输出契约均通过现有 deterministic eval。整体可用，强项是 Markdown 尽调类和 DOCX 纪要类；主要短板是 Excel 类示例 workbook 只有表头、`jvc-knowledge-tree-builder` 缺少完整 artifact fixture、`jvc-invoice-manager` 的脚本边界仍偏薄。

## 测试方法

本次不做联网研究和真实 OCR，不声称 model-executed quality。使用以下证据：

- `python3 scripts/check-skill-evals.py`
- `bash scripts/check-review-fixes.sh`
- `python3 scripts/check-docx-filename-rule.py`
- `python3 scripts/check-governance.py`
- 抽查 `examples/*.md`、`examples/*.xlsx`、`templates/*.md`
- 临时生成 `jvc-meeting-notes` / `jvc-talk-notes` DOCX
- 临时运行 `jvc-knowledge-tree-builder/scripts/collect_sources.py`

## 总览

| Skill | 测试案例 | 质量 | 主要判断 |
| --- | --- | --- | --- |
| `jvc-prescreen` | 虚构工业视觉项目初筛 | A- | 输出结构清楚，证据/缺口意识强，可直接进入后续 DD。 |
| `jvc-bull-case` | 同项目正向亮点提炼 | A- | 能区分亮点和待验证项，不越界到投资建议。 |
| `jvc-bear-case` | 四角色反向论证 | A | IC boss 角色有效，IP/TAM/SAM/壁垒问题足够锋利。 |
| `jvc-track-research` | 玻璃基板/工业视觉赛道图谱 fixture | B+ | 结构比早期版本好；真实质量仍依赖联网来源检索。 |
| `jvc-knowledge-tree-builder` | 临时本地资料夹 source manifest | B | source inventory 可用，缺完整知识树 artifact 样例。 |
| `jvc-comps-dd` | 竞品 workbook contract | B- | sheet 设计合理，但 `.xlsx` 示例只有表头，内容质量不可评。 |
| `jvc-market-sizing` | TAM/SAM/SOM workbook contract | B | 模型结构完整；缺公式和 populated case。 |
| `jvc-roi-modeler` | MOIC/IRR workbook contract | B | 逐轮稀释结构到位；缺公式化样例和真实输入回归。 |
| `jvc-ic-memo` | 十段式 IC memo fixture | A- | 来源标注和风险篇幅控制好，可作为 memo 初稿骨架。 |
| `jvc-meeting-notes` | 临时 DOCX 生成 | A- | 文件命名、版式、行距和 anti-expansion 设置通过。 |
| `jvc-talk-notes` | 临时 Q&A DOCX 生成 | A- | `完整回答 / 对应事实层维度 / 待验证点` 结构稳定。 |
| `jvc-invoice-manager` | 脚本/边界检查 | B- | 运营边界清楚；OCR 和汇总脚本需要更强输入校验。 |

## 逐项评价

### `jvc-prescreen`

- 案例：`prescreen-deck-quick-review`，虚构工业视觉项目。
- 证据：`examples/prescreen-example.md` 有 6 个二级章节、28 个 source/uncertainty 标签，无投资结论禁词。
- 质量判断：适合快速把材料变成事实摘要、七维判断、bear case 雏形和关键问题。
- 缺口：没有“继续/不继续深入”的优先级分层，但这符合不替用户决策的边界。

### `jvc-bull-case`

- 案例：`bull-case-positive-arguments`。
- 证据：`examples/bull-case-example.md` 覆盖标题级亮点、正文级亮点、待验证亮点和来源索引。
- 质量判断：能把正向论点压成可验证表达，不会写成营销稿。
- 缺口：证据强弱仍依赖模型执行时是否严格打标签；当前 fixture 只证明结构。

### `jvc-bear-case`

- 案例：`bear-case-adversarial-review`。
- 证据：`examples/bear-case-example.md` 覆盖挑剔 LP、竞品 CEO、怀疑论同行、IC boss；IC boss 明确打 IP 和 TAM/SAM。
- 质量判断：四角色攻击有效，可直接转成尽调取证清单。
- 缺口：如果输入材料太薄，模型可能输出过多 `[推测]`；这是合理暴露，不应补假证据。

### `jvc-track-research`

- 案例：`track-research-sector-map`。
- 证据：`examples/track-research-example.md` 有行业定义、简史、技术路线、产业链、趋势和来源痕迹。
- 质量判断：比事件列表强，能逼模型讲技术发展逻辑和路线 trade-off。
- 缺口：没有本次联网实测；真实输出质量主要取决于搜索源质量和引用纪律。

### `jvc-knowledge-tree-builder`

- 案例：临时资料夹包含 `market.md` 和 `company.txt`。
- 证据：`collect_sources.py` 生成 `source_manifest.json`，`file_count=2`、`readable_count=2`、来源 ID 为 `S1/S2`。
- 质量判断：source inventory 这一步稳，output contract 也清楚。
- 缺口：缺一套完整 `knowledge_tree.md / knowledge_graph.mmd / nodes.json / evidence_index.md / open_questions.md` 样例。

### `jvc-comps-dd`

- 案例：`comps-dd-competitor-workbook`。
- 证据：`examples/comps-dd-example.xlsx` sheet 齐全：`companies`、`segmentation`、`sources`、`coverage_notes`。
- 质量判断：字段设计能约束收入、估值、市值口径。
- 缺口：`.xlsx` 示例只有表头；Markdown 示例有内容，但 Excel 可用性还没被 populated fixture 证明。

### `jvc-market-sizing`

- 案例：`market-sizing-workbook`。
- 证据：workbook sheet 齐全：`assumptions`、`top_down`、`bottom_up`、`reconciliation`、`orthogonality_check`、`sources`。
- 质量判断：TAM/SAM/SOM、top-down/bottom-up、正交检查都被写进结构。
- 缺口：示例 workbook 没有公式和样例数字，不能验证计算质量。

### `jvc-roi-modeler`

- 案例：`roi-modeler-return-workbook`。
- 证据：workbook sheet 齐全：`investment_terms`、`financial_forecast`、`financing_dilution`、`ownership`、`exit_scenarios`、`returns`、`sensitivity`、`sources`。
- 质量判断：逐轮稀释和三情形退出结构正确。
- 缺口：示例 workbook 只有表头，IRR/MOIC 公式没有样例回归。

### `jvc-ic-memo`

- 案例：`ic-memo-full-synthesis`。
- 证据：`examples/ic-memo-example.md` 有 13 个二级章节、47 个 source/uncertainty 标签，无投资结论禁词。
- 质量判断：作为 IC memo 初稿结构够用，风险与反方观点不会被压扁。
- 缺口：缺跨文件引用完整性检查，例如 prescreen/bull/bear 中的来源编号是否一致。

### `jvc-meeting-notes`

- 案例：临时生成 `【2026年06月26日访谈】星尘工坊.docx`。
- 证据：输出使用 `Normal` style、标题居中、正文两端对齐、段前/段后 0、单倍行距、`doNotExpandShiftReturn=True`。
- 质量判断：格式问题已基本修到可用，默认模板也保持中性。
- 缺口：内容抽取质量无法由脚本自动证明，需要真实逐字稿抽查。

### `jvc-talk-notes`

- 案例：临时生成 `【2026年06月26日访谈】星尘工坊客户A.docx`。
- 证据：输出同 meeting-notes 版式；Q&A 正文使用 `完整回答 / 对应事实层维度 / 待验证点`。
- 质量判断：比旧版 `问题/回答摘要/关键原话/事实标签` 更干净，适合客户/专家访谈复盘。
- 缺口：需要一份脱敏真实访谈 fixture 来判断“完整回答”是否既完整又不冗长。

### `jvc-invoice-manager`

- 案例：`invoice-operational-boundary`。
- 证据：skill 明确人工确认、PDF 只复制、不进入投资决策流程；脚本存在 `process_invoices.py` 和 `generate_summary.py`。
- 质量判断：边界清楚，作为运营辅助可用。
- 缺口：脚本没有强 schema 校验，`generate_summary.py` 输出目录固定在 skill archive；OCR regex 简单，真实发票容错需要实测。

## 最小改进建议

1. 先补 Excel populated fixtures：`comps-dd`、`market-sizing`、`roi-modeler` 各一份带 2-3 行数据和公式的 `.xlsx`。
2. 给 `jvc-knowledge-tree-builder` 补一套最小完整 artifact 样例。
3. 给 `jvc-talk-notes` / `jvc-meeting-notes` 各留一份脱敏真实逐字稿输入和对应 DOCX 输出。
4. `invoice-manager` 加最小 JSON schema 校验即可，不需要重写 OCR。

## 当前结论

可以继续使用。若把它当 public skill suite，下一轮最值得做的是补 populated fixture，不是继续改 prompt。

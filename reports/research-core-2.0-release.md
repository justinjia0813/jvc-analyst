# jvc-analyst 2.0 Research Core Release

发布日期：2026-07-30
版本：`2.0.0`
Source contract fingerprint：`50376a35bf258272fbe62fea5035299d99e62b6b0efc1d827377b93be7a19462`

## Release Decision

发布标签保留为 `2.0.0`，但证据边界是 repository-local production governance with warnings（仓库内、带警告的生产治理），不是 governed public release（受治理的公开发布）。

material improvement（实质改进）的依据：

- 两个同输入、同日期、完整产物对照覆盖事实准确性、可追溯性、来源独立性、冲突/反证、结论校准和下一步可用性；1.0 基线 64.09%，2.0 候选 100.00%，提升 35.91 个百分点，0 regression（回退）。
- 5 个真实路径案例得到 4 `ready` 和 1 个按预期 `blocked`（exit 20）；无 waiver（例外许可），证明固定命令不仅能放行，也会在关键商业证据缺失时失败关闭。
- 玻璃基板盲审选择 2.0，置信度 0.7，理由原文：“实用性更好”。

人工证据仅为 partial support（部分支持），不得写成 2-0：

- 市场模型盲审选择 1.0，置信度 0.3，理由原文：“格式处理更胜一筹”。
- 该理由属于 presentation usability（呈现实用性）或格式偏好，不是六项 evidence-quality（证据质量）正向证据；它仍构成需要保留的可读性分歧。
- 只有 1 名审阅者、2 个案例（n=2），不能外推统计胜率或跨任务偏好。

上述 core `2.0.0` 功能证据不变。Justin 于 2026-07-30 确认本次不恢复独立 report worktree；同步远程 `main` 时，已合并的 `jvc-research-report` 功能通过远程提交 `1c54d0b` 进入主线。该 renderer 的证据单独列示，不计入 core 的五个真实案例或两项盲审。

## Acceptance Cases

DOCX：Office Open XML Word Document（Word 文档格式），用于保存可编辑的结构化访谈纪要。

| Case | Expected | Actual | Exit | Evidence |
| --- | --- | --- | ---: | --- |
| `local-interview-to-prescreen` | ready | ready | 0 | 自述/用户观察分离；DOCX 与 prescreen 审计依赖有效 |
| `glass-substrate-conflicting-public-sources` | ready | ready | 0 | 同源不重复互证，保留工程反证、检索缺口与停止条件 |
| `market-model-fact-vs-assumption` | ready | ready | 0 | 外部事实、用户假设和模型估算分离；冲突市场定义不合并 |
| `audited-chain-to-ic-memo` | ready | ready | 0 | bull→bear→memo 依赖审计与最终产物指纹有效 |
| `missing-critical-commercial-proof` | blocked | blocked | 20 | 未验证公司收入主张保留为 company claim，没有伪装成 ready |

## Blind Review

审阅者：Justin
审阅日期：2026-07-30
完整性：审阅者确认做出判断前未查看答案密钥；2 个判断均有效，无 pending 或 invalid。

| Case | Blind decision | Answer mapping | Result |
| --- | --- | --- | --- |
| 玻璃基板 | B，0.7，“实用性更好” | B=2.0 candidate | match |
| 市场模型 | B，0.3，“格式处理更胜一筹” | A=2.0 candidate；B=1.0 baseline | disagree |

实际裁决命令（exit 0）：

```bash
python3 -B /Users/justinjia/.agents/skills/yao-meta-skill/scripts/adjudicate_output_review.py \
  --blind-pack reports/output_blind_review_pack.json \
  --answer-key reports/output_blind_answer_key.json \
  --decisions reports/output_review_decisions.json \
  --output-json reports/output_review_adjudication.json \
  --output-md reports/output_review_adjudication.md
```

维护限制：生成的 `reports/output_review_adjudication.md` 中 reviewer checklist 仍展示 `scripts/yao.py` 与 `scripts/adjudicate_output_review.py` 示例命令，但本仓库没有这两个 wrapper（包装脚本）。本次没有伪造 wrapper；可复现命令是上面的外部 Yao 脚本完整路径。该生成报告的命令提示应在 Yao 上游修复。

## Source Dates and Evidence Boundary

- 公开玻璃基板与市场模型来源实际打开日期：2026-07-29。
- 来源材料发布日期范围：玻璃案例 2023-09-18 至 2026-02-05；市场案例 2023-03-31 至 2026-06-26。
- 本地脱敏案例固定研究日期：2026-07-29；最终验证与盲审裁决完成于 2026-07-30。
- 仓库只保存最小来源摘录与元数据，不镜像公开来源正文。
- 输出对照是确定性 assertion grading（断言评分）；人工盲审为 n=2；均不能替代大样本模型质量统计。

## Release Gate Results

以下命令均于 2026-07-30 在仓库根目录实际执行。

| Command | Exit | Result |
| --- | ---: | --- |
| `python3 scripts/check-governance.py` | 0 | `governance assets passed`；指纹与本报告一致 |
| `python3 skills/jvc-research-core/scripts/check_package.py` | 0 | ledger 与 audit 自检通过 |
| `python3 scripts/check-research-core-install.py` | 0 | 临时目录安装与回滚模拟通过 |
| `python3 scripts/check-skill-evals.py` | 0 | 14 trigger cases，14 output cases |
| `python3 skills/jvc-research-report/scripts/check_package.py` | 0 | 固定研报校验、事务式构建和文件渲染自检通过 |
| `python3 scripts/check-docx-filename-rule.py` | 0 | 通过 |
| `python3 scripts/check-docx-format-consistency.py` | 0 | 通过 |
| `python3 scripts/check-docx-template-customization.py` | 0 | 通过 |
| `bash scripts/check-excel-workbooks.sh` | 0 | 三类生成/示例 workbook 验证通过 |
| `bash scripts/check-jvc-assets.sh` | 0 | 通过 |
| `bash scripts/check-review-fixes.sh` | 0 | 全量本地 gate 通过 |
| `git diff --check` | 0 | 无 whitespace error（空白错误） |
| `python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/validate_skill.py skills/jvc-research-core` | 0 | 无 failure 或 warning |
| `python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/resource_boundary_check.py skills/jvc-research-core --max-initial-tokens 1000` | 0 | initial load 621 tokens，无 regression |
| `python3 /Users/justinjia/.agents/skills/yao-meta-skill/scripts/governance_check.py skills/jvc-research-core --require-manifest` | 0 | 无 failure；warning：library 声明 80/100，低于推荐 85 |

全量 gate 曾发现 `scripts/check-review-fixes.sh` 将合法仓库绝对路径误判为裸旧名称。最小根因修复把裸名称前导排除从 `j` 扩展为 `j` 或 `/`；新增的正反例自检只验证文件系统路径不匹配、裸旧包名会匹配，随后的实际 corpus scan（语料扫描）继续覆盖正文裸旧名和未加前缀的 slash command（斜杠命令）。

## Known Limitations

- 未运行 Codex 之外的平台适配器、分发包 conformance matrix（符合性矩阵）或 runtime permission probe（运行时权限探针）。
- 未运行 model-executed route holdout（模型实际路由保留集）或 adversarial holdout（对抗性保留集）。
- Yao governance gate 的 maturity warning 仍存在：skill 声明 library，当前 governance score 为 80/100，推荐最低 85。
- `jvc-research-report` 的 A4 13 页检查使用完全虚构的本地 fixture，是 renderer 自检和视觉证据，不是 core 模型执行或盲审证据。
- 人工市场模型偏好显示格式可读性尚未稳定优于 1.0；下一轮应以代表性工作簿审阅任务验证，不把证据规则降级来迎合格式。
- 既有 DOCX/发票依赖仍有未固定版本项；发票脚本仍使用手工 `sys.argv`。
- 真实光学字符识别、发票人工复核与归档没有执行，也不属于研究内核发布证据。

## Explicit Exclusions

- `jvc-invoice-manager` 保持运营辅助边界，不接入 `jvc-research-core`，不进入投资判断证据链。
- Task 0 时 `.worktrees/jvc-research-report` 路径存在且 clean；当前该路径 absent（不存在），Git 也未注册对应 worktree。本任务及已审代理命令没有删除或重建它。Justin 于 2026-07-30 确认本次不恢复。这里只排除本地 worktree 状态；远程已合并的 report skill 已通过正常主线同步纳入包。
- `.superpowers/` 与 `assets/xiaohongshu/jvc-track-research/` 是预先存在的未跟踪用户目录，不纳入 staging。
- 不包含私密逐字稿、凭据、未审阅盲审决定或公开来源全文。

## Rollback Boundary

core 回滚只需 revert 本次发布证据 commit 及其前序 2.0 实现 commits；远程 `jvc-research-report` 合并提交是独立功能边界，不随 core 回滚自动移除。研究输入、私密材料、本地自定义模板、当前未跟踪用户目录，以及若由 Justin 恢复的独立 worktree，均在 package rollback 之外，不得移动、覆盖或删除。

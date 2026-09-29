# 原子认知 Skill 的内核调用合同

本合同供新接入 skill 共用。调用前读本文件、[证据合同](evidence-contract.md) 与 `../profiles/<调用skill>.json`。从调用者 `SKILL.md` 所在目录解析同级 `jvc-research-core` 的绝对路径，不依赖工作目录。下列尖括号均需替换成已解析的输入；不得照抄为字面值。

1. 新研究准备完整 scope 后运行 `python3 "<core>/scripts/researchctl.py" init --skill "<调用skill>" --run-dir "<研究目录>" --scope-file "<scope.json>"`；已有研究用 `init --skill "<调用skill>" --run-dir "<研究目录>" --resume`。不得把本次计划的范围变更静默写入原始 scope。
2. 用 `record --run-dir "<研究目录>" --input "<records.jsonl>"` 追加问题、来源、主张及更正；更正含 supersedes。不得直接编辑证据台账 `evidence_registry.jsonl`。未执行的检索或访谈不能登记为已执行 query。
3. 完成调用者的内容自查后运行 `audit --run-dir "<研究目录>" --skill "<调用skill>" --artifact "<最终文档>"`。上述 record、audit 都使用同一 `python3 "<core>/scripts/researchctl.py"` 前缀。同时读取退出码和 `audit.json` 中 `audits` 数组内匹配当前 skill 的最新审查条目，不能只看命令成功或文档存在。需要保留首轮测评时，在修改工件或重审前复制当时的工件、审查文件和退出码；最终审查不能冒充首次审查。
4. 默认 `--mode deliver`：审查只给证据成熟度标签，不限制正文。退出码 0 就交付完整文档（含判断）；可在文末写一行 `证据成熟度：<status>`，不得写高于审查结果的级别。退出码 20 表示结构问题（产物缺失、台账残缺、引用了不存在的来源、夸大成熟度），修复后重跑。只有 `/jvc-ic-memo`、L3 或用户要求 `--rigor` 时用 `--mode gate`，此时按原纪律：`ready`/0 只能宣称本次范围内任务完成；`partial`/10 在正文开头、结论和来源限制注明“研究状态：partial”并缩小结论；`blocked`/20 只交付受影响判断的证据缺口与下一步。任何模式下错误/1 都要修复后重跑，不能退回纯提示词模式冒充审查成功。
5. gate 模式下，`partial_label_missing`、`blocked_label_missing`、`artifact_status_mismatch` 指明应呈现的状态；按 finding 修正正文标签和结论边界后重跑 audit，直到标签与最新结果一致。deliver 模式只在夸大成熟度时报 `artifact_status_mismatch`。任何文档改动后重跑终审。
6. 只有用户针对该 skill 最新仍有效的 blocked audit 明确批准具体例外，才能按证据合同运行 waive；例外最多降级为 partial。不要把对开发清单的确认当作研究证据例外。

主张类型、重要性、来源独立性按实际证据填写；scope、记录结构、引用完整性及上游审查错误均不能豁免。关键公司自述尚未核验时，deliver 模式照常交付判断，并把它写成条件式（“若公司所述 X 成立，则……”）；gate 模式下它阻断相应结论，这是有效结果，不是工具故障。

正文统一保留【第三方事实】(third_party_fact)、【公司自述】(company_claim)、【用户观察】(user_observation)、【模型估算】(model_estimate)、【分析推断】(agent_inference)、【未知/待验证】(unknown 或 question.state=gap)。来源、时间、单位与关键条件紧邻主张；英文缩写首次给英文全称、中文全称与简释。公司材料使用 company-material，公司披露使用 company-filing；上传者身份不改变原始来源类型。

一个 `[S编号]` 对应一个原始文件或页面，保留可解析路径及具体页码/单元格/段落；多个文件分别编号，不能合成一个来源后混用口径。无法确认发布日时标未知，不拿报表期末日代替发布日期。

概括句也保留原始证据身份：只有公司口述时写“公司声称已发生”，不能先写“已发生”再靠后文免责声明收回。匿名或群体陈述不得归给原文未绑定的具体客户/个人；量化成果保留统计单位、分母与归因范围。

涉及交易或经营数字时，先绑定“哪家公司、向谁买/向谁卖、哪种产品、哪个期间”。供应商的客户可能正是目标公司，其交易关系不是目标公司的下游客户证据；不同公司的相同数值或门槛分别保留，不能合并引用后移入目标公司的模型或里程碑。

gate 模式下，blocked 的缺口交付可以列出标为未核验的原始主张、出处和冲突对照，以解释需要什么证据；不能输出受影响的业务判断。未执行内核的草稿写“未执行证据内核审查”，不能自行宣称 ready、partial 或 blocked 是已取得的审查结果。

未取得材料或未找到证据意味着 gap/unknown，不意味着相反事实成立或证伪条件已满足；只有取得相反证据才可据此判为 refuted。需要管理截止时间时，区分“停止投入验证”与“业务假设已被推翻”。

可用 `python3 "<core>/scripts/researchctl.py" --help` 查询固定接口。具体字段见证据合同；结构校验报错时对照同目录运行时的字段定义修正，不猜造字段或枚举值。

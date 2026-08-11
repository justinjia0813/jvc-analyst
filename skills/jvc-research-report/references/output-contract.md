# 输出契约

## 两阶段合同

Research Report 是一个受审计的输出组装器，固定两个顺序阶段：

1. **组装**：从已审计的本地上游产物生成 canonical `research-report.md`。只重组经审查内容：
   - 保留来源标识：正文 `[S<n>]` 只能使用上游产物中已出现的编号；
   - 继承上游主张：事实、推断与开放问题沿用上游结论，证据状态标签（`[推测]`、`[未核实]`、`[模型估算]`、`[未知/待验证]`、`[用户观察]` 等）只能沿用上游已出现的标签；半角 `[...]` 与全角 `【...】` 等价，只要一种写法在上游出现过即可继承；含 `估算|未知|待验证|观察|假设|自述|推测|核实|访谈` 关键字、但不在白名单中的未知标签一律拒绝；
   - 展示覆盖缺口：在 `未核实与待补证据`（或 `覆盖缺口`）章节列出缺口，缺失的可选上游输入按规范名显式列出；
   - 禁止联网补研究或新增事实、数字、判断。
2. **发布**：校验固定章节、引用、本地图片和样式后，生成网页及固定版式结果。

已有完整 canonical `research-report.md` 时直接进入发布阶段（直接发布模式）。直接发布信任用户对 canonical 的声明：`build_report.py` 只做 renderer 内部一致性校验（章节/来源索引内自洽/本地资源），**不证明** assembly 继承或 Research Core 审计；如需证据继承校验，必须提供上游产物并运行 `validate_assembly.py`。`validate_assembly.py` 是只读校验器，不修改正文；`build_report.py` 是发布渲染器，不重写正文、不访问网络。

## 输入结构

`research-report.md` 必须是带 YAML（YAML Ain't Markup Language，YAML 不是标记语言，用于结构化元数据）frontmatter 的本地 Markdown。frontmatter 必须包含非空的 `title` 和 `date`。

正文必须按以下 11 个 canonical sections 顺序出现；标题可不带前缀，也可分别带 `0.`、`A.` 至 `I.` 前缀：

1. 研究设定与一页快照
2. 行业定义与边界
3. 行业简史与产业生命周期
4. 技术路线与商业可行性
5. 产业链图谱
6. 产业趋势、景气度与周期位置
7. 关键玩家分层
8. 监管、政策与标准
9. 投资相关问题
10. 后续工作交接包
11. 来源索引

第 8 节兼容既有标题别名 `监管 / 政策 / 标准`，后续解析器必须同时接受该别名与 canonical 标题。`缩写说明` 和 `未核实与待补证据` 可作为额外章节，但不能替代或打乱上述章节。`未核实与待补证据` 是覆盖缺口的显式载体，组装模式必须保留。内容尚未形成该结构时交回 `/jvc-track-research`。公司尽调材料合成投决文档应交给 `/jvc-ic-memo`（Investment Committee Memo，投资委员会备忘录，用于投决材料合成）。

### 上游到章节映射（组装模式）

| 报告章节 | 上游产物 | 组装要求 |
| --- | --- | --- |
| 研究设定与一页快照 | Track Research 研究设定与一页快照 | 继承口径、边界、关键事实与不确定性 |
| 行业定义与边界 | Track Research 行业定义与边界 | 继承定义、纳入/排除范围和相邻市场 |
| 行业简史与产业生命周期 | Track Research 行业简史 | 继承阶段、切换信号和当前位置 |
| 技术路线与商业可行性 | Track Research 技术路线 + Knowledge Tree 技术分支 | 继承路线、成熟度、成本和限制 |
| 产业链图谱 | Track Research 产业链图谱 + Knowledge Tree 核心关系图 | 继承环节、玩家、壁垒和价值分配 |
| 产业趋势、景气度与周期位置 | Track Research 趋势与周期矩阵 | 继承趋势、信号、反证与置信度 |
| 关键玩家 | Track Research 关键玩家 + 可选 Comps/DD 公司分层 | 可选输入缺失时在覆盖缺口列出 |
| 监管 / 政策 / 标准 | Track Research 监管、政策与标准 | 继承法规、标准、生效日期与影响 |
| 投资相关问题与反证账本 | Track Research 投资问题与反证账本 + Knowledge Tree 开放问题 | 继承支持证据、反面证据与证伪条件 |
| 市场规模数据（并入相关章节） | `market-sizing.csv`（`top_down`、`bottom_up`、`reconciliation`、`orthogonality_check` 各 section） | 数字原样继承，单位单独成列，不改写数值 |
| 后续工作交接包 | Track Research 后续工作交接 + Knowledge Tree 开放问题 | 继承交接项、优先级与完成标准 |
| 未核实与待补证据 | 上游未核实项 + 缺失的可选输入 | 逐项列出说法/数字、当前来源与所需证据 |
| 来源索引 | 上游来源并集 | 每个被引用 ID 必须已存在于上游 |

组装校验失败规则见「失败规则」；数字继承使用 IC 终版校验器同一套数字归一化（数量、单位别名、千分位），不改 IC 语义；另做最小归一化：四位年份 `N` 与 `N年` 等价（如上游 CSV 年列 `2026` 与正文 `2026 年` 不互相误报）。亿/万 量纲换算**不做**值级换算，继续保持保守拒绝，错误信息会提示疑似单位表示不一致并给出上游单位表示（如上游 `420 万元` 与正文 `0.042 亿元`）。标签括号内与来源索引描述单元格中的数字同样参与继承；来源索引中的日期（`YYYY-MM-DD`）、URL 和来源 ID 属元数据，不参与数字继承。组装路径的 frontmatter 只允许当前 canonical 已知顶层键 `title`/`subtitle`/`date`/`authors`/`sector`/`region`/`classification`/`cover_image`/`disclaimer`，未知键拒绝（build_report 直接发布兼容性不变，仍接受额外键）。

`research-report.md` 正文图片和 frontmatter 中的 `cover_image` 相对 `research-report.md` 所在目录解析；`brand.yml` 中的 `logo` 相对 `brand.yml` 所在目录解析。解析后的资源不得逃离各自根目录。绝对路径和任何带 scheme 的路径一律是 hard error。

## 品牌字段

`brand.yml` 使用 `name`、`logo`、`accent_color`、`header`、`footer`、`disclaimer`、`sans_font` 和 `serif_font`。`logo` 可为 `null` 或本地文件。`sans_font` 和 `serif_font` 接受本机 font family 名，或相对 `brand.yml` 所在目录的本地字体文件路径。字体路径与 logo 一样，解析后不得逃离 brand 根目录；用户提供的绝对路径或带 scheme 的路径一律是 hard error。本地字体文件在渲染时嵌为 `data:` `@font-face`，不得通过网络获取。来源索引中的网络链接仅作为引用元数据，不得在构建时获取。

## 卡片、图片、表格和来源

- `[!FACT]` 标记有来源支持的事实卡片。
- `[!INFERENCE]` 标记由事实推导、但不是来源原文的判断卡片。
- `[!OPEN QUESTION]` 标记尚待验证的问题卡片。
- Markdown 图片的 alt 文本作为图片 caption；排版器不生成或改写 caption。
- 表格标题使用紧邻表格的 `表：` 行。
- 来源说明使用紧邻其对象的斜体 `来源：` 行。
- 正文引用使用 `[S<n>]`。每个被引用 ID（Identifier，标识符，用于唯一指向来源条目）必须在来源索引中恰有一个条目；同一 ID 的重复来源条目和未定义引用均不允许。

## 失败规则

以下情况是 hard error，构建必须停止：缺少 `title` 或 `date`；缺少 canonical section 或顺序错误；Markdown 或 YAML 解析失败；远程资源；本地图片、cover image 或 logo 缺失、不可读或逃离各自根目录；绝对路径或带 scheme 的资源路径；字体 URL（Uniform Resource Locator，统一资源定位符，用于标识资源位置）或绝对路径；配置的系统 font family 不存在；本地字体文件缺失、不可读、路径逃逸或格式不支持；无效品牌颜色；未定义或重复的 `[S<n>]`；HTML（HyperText Markup Language，超文本标记语言，用于浏览器预览）或 PDF（Portable Document Format，可移植文档格式，用于固定版式）渲染失败。失败不得覆盖上一版成功的三个产物。

组装模式额外 hard error（`validate_assembly.py` 退出非 0）：报告引用了上游不存在的来源编号；报告正文出现上游不存在的数字（含标签括号内与来源索引描述单元格中的数字）；报告引入上游不存在的证据状态标签，或引入含证据关键字但不在白名单的未知标签；报告 frontmatter 出现未知顶层键；报告缺少覆盖缺口章节，或缺失的可选上游输入（如 Comps/DD）未在覆盖缺口章节按规范名列出；必需上游（Track Research、Knowledge Tree、Market Sizing）缺失或不可读（如 knowledge-tree 目录含非 UTF-8/不可读文件）。

## 校验边界（set-based 继承）

组装校验与 IC 终版校验器同性质：它是**集合式 token 继承**——只要数字/证据状态标签 token 在上游出现过，就能在报告中复用，包括拼进全新主张；它**不能证明**重组句子的语义等价。主张级审计仍需上游 claim 与人工复核，不把校验通过当作主张验证。直接发布模式只运行 renderer 内部一致性校验，不证明 assembly/Research Core 继承；需要证据继承时提供上游并运行 `validate_assembly.py`。

以下情况是 warning，构建可继续但必须写入 `build-report.txt`：来源索引条目从未被正文引用；图片缺少 alt caption 或位图分辨率偏低；表格缺少 `表：` 标题或列数过多；对象缺少斜体 `来源：` 行；已存在的系统 font family 或本地字体文件仅对个别字形发生 fallback；可能出现分页、孤行或横向溢出。warning 不授权改写正文。

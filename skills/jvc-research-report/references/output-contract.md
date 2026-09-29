# 输出契约

## 输入结构

`report.md` 必须是带 YAML（YAML Ain't Markup Language，YAML 不是标记语言，用于结构化元数据）frontmatter 的本地 Markdown。frontmatter 必须包含非空的 `title` 和 `date`。

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

第 8 节兼容既有标题别名 `监管 / 政策 / 标准`，后续解析器必须同时接受该别名与 canonical 标题。`缩写说明` 和 `未核实与待补证据` 可作为额外章节，但不能替代或打乱上述章节。内容尚未形成该结构时交回 `/jvc-track-research`。公司尽调材料合成投决文档应交给 `/jvc-ic-memo`（Investment Committee Memo，投资委员会备忘录，用于投决材料合成）。

`report.md` 正文图片和 frontmatter 中的 `cover_image` 相对 `report.md` 所在目录解析；`brand.yml` 中的 `logo` 相对 `brand.yml` 所在目录解析。解析后的资源不得逃离各自根目录。绝对路径和任何带 scheme 的路径一律是 hard error。

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

以下情况是 warning，构建可继续但必须写入 `build-report.txt`：来源索引条目从未被正文引用；图片缺少 alt caption 或位图分辨率偏低；表格缺少 `表：` 标题或列数过多；对象缺少斜体 `来源：` 行；已存在的系统 font family 或本地字体文件仅对个别字形发生 fallback；可能出现分页、孤行或横向溢出。warning 不授权改写正文。

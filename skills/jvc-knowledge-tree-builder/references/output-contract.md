# Knowledge Tree Output Contract

本 Skill 从 `tracks/{track-slug}/landscape.md`、Research Core（Research Core，研究证据内核：维护共享证据台账与审计状态）和用户指定本地材料生成 visual-first（visual-first，可视化优先：先展示主图和关键关系）的知识包，不承担首次完整联网赛道研究。

## 固定五文件

输出目录必须恰好五个文件且均非空，不得改名或加入第六个交付文件：

1. `knowledge_tree.md`
2. `knowledge_graph.mmd`
3. `nodes.json`
4. `evidence_index.md`
5. `open_questions.md`

`source_manifest.json` 只能作为输出目录之外的可选中间清单。

## `knowledge_tree.md`

这是主用户制品。完整且闭合的 Mermaid fence（Mermaid 代码围栏）必须在前 40 行内，图体首个非空行必须是受支持的图声明；frontmatter（文档头部元数据）中的伪 fence 不计。frontmatter 只在首行为列首精确 `---` 时成立，并且只由后续列首精确 `---` 或 `...` 结束；缩进标记仍属于 frontmatter 内容。随后给出图例、关键关系、递归问题树和开放问题概览。主图只保留影响投资理解的核心关系，细节进入问题树或子图。

````markdown
# <主题>知识树

## 核心关系图

```{mermaid}
flowchart LR
  root["根问题"] --> branch["主要分支"]
```

## 图例

- 实线：父子问题
- 虚线：有证据或明确缺口的跨分支关系
````

## `knowledge_graph.mmd`

首个非空行整行必须是受支持的 Mermaid 图声明：`graph TD`、`graph LR`、`flowchart TD`、`flowchart TB`、`flowchart BT`、`flowchart RL` 或 `flowchart LR`；声明后追加其他文本无效。该文件只保存图源，不加 Markdown fence（Markdown 代码围栏）。

## `nodes.json`

JavaScript Object Notation（JSON，JavaScript 对象表示法：保存机器可读节点与关系）文件至少包含 `nodes` 和 `relations`：

```json
{
  "topic": "string",
  "generated_at": "2026-08-09T00:00:00Z",
  "nodes": [
    {
      "id": "stable-id",
      "title": "string",
      "question": "string",
      "summary": "string",
      "parent_id": "root-or-null",
      "evidence_refs": ["S1"],
      "evidence_gap": "optional explicit gap",
      "status": "source-backed|inferred|needs-evidence|open-question"
    }
  ],
  "relations": [
    {
      "id": "stable-relation-id",
      "from": "node-id",
      "to": "node-id",
      "type": "related|depends_on|contrasts_with|affects|parent",
      "claim": "claimed relation text",
      "evidence_refs": ["S1"],
      "evidence_gap": "optional explicit gap"
    }
  ],
  "access_issues": []
}
```

结构规则：

- 每个节点的 `id`、`title`、`question`、`summary` 和 `status` 都是非空字符串；`status` 只允许合同枚举，`parent_id` 只能是 `null` 或非空字符串。
- 节点 `id` 唯一。
- 恰好一个非 `open-question` 根节点使用 `parent_id: null`。
- 非根、非明确 `open-question` 节点必须有有效 parent；缺 parent 或孤立节点均失败。
- 每个非 `open-question` 节点的 parent 链最终必须到达唯一根节点；挂在 parentless `open-question` 下不算连通。
- parent cycle（父节点循环：沿 parent 指针回到已访问节点）必须失败。
- `relations` 必须明确存在、类型为数组且非空。
- 每个 relation 的 `id`、`from`、`to`、`type` 和 `claim` 都是非空字符串；`id` 唯一，`type` 只允许合同枚举。
- relation 两端必须引用现有节点。
- `parent` 只表达结构；其他 relation 或含 `claim` 的 relation 都是 claimed relation（主张关系：表达可证伪的依赖、影响或对比）。
- claimed relation 必须有 `evidence_refs` 或非空 `evidence_gap`。

## `evidence_index.md`

每个 `[S编号]` 使用二级标题，并在该段用反引号显式列出所有使用它的节点和关系编号：

```markdown
## S1

- 来源：`tracks/example/landscape.md`
- 映射节点：`root`、`branch`
- 映射关系：`relation-id`
- 有效主张：`C1`
```

带证据的 node 或 relation 必须分别出现在对应来源段的 `映射节点：` 或 `映射关系：` 字段中；只有剥离 frontmatter 后，这些字段内的反引号编号计为映射，frontmatter 或普通摘要提及不计。无来源时必须填写非空 `evidence_gap`。下游主张在共享台账中继续用 `derived_from_claim_ids` 保留上游有效主张编号，不复制无继承关系的 Track Research 事实。

## `open_questions.md`

按分支列出问题、重要性和可解决它的证据：

```markdown
# 开放问题

## <分支>

- [ ] 问题
  - 重要性：
  - 所需证据：
```

## 校验与更新

先运行：

```bash
python3 skills/jvc-knowledge-tree-builder/scripts/validate_output.py <知识包目录>
```

validator 只使用 Python 标准库检查恰好五文件、非空、完整主图、图声明、节点与关系 schema（schema，结构约束：定义字段、类型和允许值）、祖先连通性、parent cycle、关系端点和显式证据映射。`knowledge_tree.md` 与独立 `knowledge_graph.mmd` 的 Mermaid 完整语法由本地 Quarto 真渲染验证；缺 renderer 或 malformed Mermaid（语法错误的 Mermaid 图）都是 gate failure（闸门失败：不得进入后续审计）。

validator 通过后才能运行 Research Core audit。上游变化只把受影响 nodes、relations 和 open questions 标为 stale；执行最小更新仍需用户批准。

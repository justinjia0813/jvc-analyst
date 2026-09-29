---
name: jvc-workbook
description: |
  建模工作簿：生成三类 Excel 模型——市场规模（TAM/SAM/SOM 自上而下与自下而上双路径）、可比公司表（竞品、可比、上下游、海外标杆）、投资回报（逐轮稀释、三情景退出、MOIC/IRR 与敏感性）。每个工作簿附一页文字结论。
  Use when user says '/jvc-workbook', '市场规模', 'market sizing', 'TAM', '市场有多大', '可比公司', 'comps', '竞品表', '回报测算', 'MOIC', 'IRR', '稀释', '退出回报', '回报模型', or needs an Excel model. 定性的竞争格局分析用 jvc-track-research；单位经济用 jvc-business-economics。
user_invocable: true
version: "4.0.0"
---

# 建模工作簿

交付可复算的 Excel 模型，外加一页结论。Excel 的结构和公式本身就是交付物的价值，所以本 skill 比其他 skill 更讲究口径和公式；但结论照样放在最前面，缺数据时照样给估算。

## 适用级别

最低适用级别：**L1+**（有赛道定义或项目条款就能建模，不要求先建项目档案）。

## 三种模式

| 模式 | 回答 | 合同 | 默认文件名 |
| --- | --- | --- | --- |
| **市场规模** | 市场有多大、能拿到多少 | [market-sizing.md](references/market-sizing.md) | `05-market-sizing.xlsx` |
| **可比公司** | 谁在做、做到什么程度、值多少钱 | [comps.md](references/comps.md) | `05-comps-dd.xlsx` |
| **投资回报** | 按当前条款，退出时能拿回几倍、靠什么 | [returns.md](references/returns.md) | `05-roi-modeler.xlsx` |

项目外单独导出时，文件名用 `{对象}_{模式}_{YYYYMMDD}.xlsx`。用户指定路径优先。

## 执行

1. 读对应模式的合同。
2. 从本 `SKILL.md` 的实际路径向上两级解析仓库根目录（安装为链接时解析到源码目录），用仓库里的生成器和模板建表：

   ```bash
   python3 "<仓库根>/scripts/generate-workbook.py" "<仓库根>/templates/<模板>.md" "<输出>.xlsx"
   ```

   模板：市场规模 `market-sizing-template.md`，可比公司 `comps-dd-template.md`，投资回报 `roi-modeler-template.md`。
3. 填数、写公式。业务输入只在假设表录入，其他表引用它，结果格保留真实公式。
4. 结构校验：`python3 "<仓库根>/scripts/validate-workbook.py" "<输出>.xlsx" "<仓库根>/templates/<模板>.md"`。
5. 动态检查：改一个关键输入，确认结果按预期变化，再改回来。
6. 写一页结论：同名 `.md` 文件（例如 `05-market-sizing.md`），结构见下。

## 一页结论

```
# {对象}：{模式}｜{日期}

## 结论（3–5 句）
## 关键数字（一张小表）
## 最敏感的 1–2 个假设，以及它们变到多少结论会变
## 还缺哪些数据、怎么补
```

## 文件位置

用户指定路径优先；否则写进材料所在的项目或赛道文件夹根目录（不放进原始材料子目录）；都没有时问一次放哪。中间文件（JSON、转出的文本、计算脚本、证据台账）放在同目录的 `_work/`。同名文件已存在时不覆盖，加日期后缀。

## 反合理化约束

- 缺数据时给估算并在 `sources` 表写明依据和“估算”字样；说不出依据的输入留空并在结论里列为缺口，不填 0。
- 公司给的数字标“公司自述”；上市公司市值和一级市场估值不混为同一口径。
- 两条测算路径共用输入时不算独立交叉验证，在正交检查里写明。
- 不输出“值得投 / 不值得投”，只输出区间、驱动因素和敏感项。
- 证据内核默认不启用。用户要求 `--rigor` 时按 [调用合同](../jvc-research-core/references/caller-contract.md) 审查：市场规模工作簿用 `jvc-market-sizing` 身份（含公式检查），可比公司用 `jvc-comps-dd`，投资回报用 `jvc-roi-modeler`。

## 完成

打开结论页就知道答案和最敏感的假设；打开 Excel 能看到每个数字从哪来、改一个假设整张表跟着动。

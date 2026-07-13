# 小红书 How to Use AI 活动文案：JVC Analyst

## 标题备选

1. 看项目时，别一上来就让 AI 写 memo
2. VC 尽调用 AI，顺序比 prompt 更重要
3. 一条更顺的 AI 尽调链条：赛道 → 公司 → 模型 → memo

## 正文

上一版我发现一个问题：很多 AI 投研工作流会把顺序搞乱。

遇到一个项目，最自然的链条不是直接问“这个公司能不能投”，也不是立刻生成 IC memo。

更顺的顺序应该是：

1. 先扫赛道  
   用 `/jvc-track-research` 看行业定义、技术路线、产业链和关键玩家；如果已经有本地资料，再用 `/jvc-knowledge-tree-builder` 整理成知识树和证据索引；接着用 `/jvc-comps-dd` 拉出竞品、可比公司、上下游和海外标杆。

2. 再理解公司  
   用 `/jvc-prescreen` 建立公司快照；把创始人、高管、客户、专家访谈分别用 `/jvc-meeting-notes` 或 `/jvc-talk-notes` 整理成事实层。

3. 然后做尽调攻防  
   信息够了以后，再用 `/jvc-bull-case` 提炼为什么值得认真看，用 `/jvc-bear-case` 写出最强不投理由和证伪条件。

4. 信息丰富后再建模型  
   市场规模不是凭空估，用 `/jvc-market-sizing` 吃前面的赛道定义和竞品口径；回报模型也不是孤立算，用 `/jvc-roi-modeler` 接投资条款、融资稀释和退出假设。

5. 最后整合成 IC memo  
   `/jvc-ic-memo` 应该把赛道判断、公司事实、正反观点、模型假设按链条整合，而不是孤立生成一篇“看起来很完整”的文章。

所以我理解的 AI 尽调，不是“让 AI 替你判断”。

它更像一个本地工作台：按正确顺序帮你整理证据、暴露缺口、组织问题，最后把材料变成投委会能讨论的结构。

## 结尾 CTA

收藏这条链条：

> 赛道与可比 → 公司事实 → 正反尽调 → 市场/回报模型 → IC memo

下次看项目时，先别问“能不能投”。先问：这个项目处在哪条赛道，它的证据链够不够？

## 话题标签

#HowToUseAI #AI工作流 #VC尽调 #投研 #产业研究 #创业项目分析 #AI提示词 #效率工具 #小红书创作灵感

## 每张图配文

1. 封面：先看赛道，再看公司，最后写 memo。
2. Flow：赛道 → 公司 → 尽调 → 模型 → memo。
3. 赛道：track-research / knowledge-tree / comps 先跑。
4. 公司：prescreen + meeting/talk notes 建事实层。
5. 尽调：bull case 和 bear case 必须基于前面事实。
6. 模型：market sizing 和 ROI 要吃前面的口径和假设。
7. Memo：IC memo 是整合，不是孤立生成。
8. 边界：运营辅助可以自动化，投决判断不要外包。
9. 行动：按顺序复制这些 prompts。

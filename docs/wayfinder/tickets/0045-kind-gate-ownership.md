---
id: "0045"
title: kind 门禁在索引投影中的归属
type: grilling
mode: HITL
status: closed
blocked_by: [0043, 0044]
assignee: agent
map: map-search-contract.md
created: 2026-10-22
claimed: 2026-10-22
closed: 2026-10-22
---

## Question

工单 0019 悬置、ADR-0006 决策 5 留白的问题：`index.json` 直读 `site.Data.products`，不过 `product-items.html` 的 kind 词汇门禁（未知 / 缺失 kind 即 errorf，「产品索引数据：」前缀含 id 与坏值）。本图如何定案：

- **选项 a（保持现状）**：隐式兜底——「产品页恒渲染全量 → product-items 恒被调用 → 门禁恒生效」，索引投影不重复校验。
- **选项 b（投影处重复校验）**：投影循环内对 kind 做同款 errorf，消息前缀区分（如「搜索索引数据：」）。
- **选项 c（数据源收敛）**：索引投影改走 product-items seam 或其数据准备部分，门禁只此一处。

权衡维度（决策时逐项过）：① 静默失效风险——索引与产品页不一致的真实场景（如产品页短代码被 limit 截断时门禁是否仍生效，事实以 research/0042 盘点为准）；② 单一真源原则（ADR-0006 决策 2 枪毙过「缺省回落」模式）；③ 维护成本（两处执法点的漂移风险 vs 投影形态适配成本）；④ 与 0043 seam 形状决策的联动（若 0043 定双 seam，选项 c 的成本结构变化）。

边界：首页计数条不在本范围（ADR-0004 已定案，kind 不影响 listed / price 计数语义）；产品侧 featured 契约不重开。

背景（事实）：index.json 文件头 0019 边界注释原文见 research/0042；ADR-0006 决策 5 明示「搜索索引的 kind 门禁归属候选 8」。

**0044 已决输入**：kind **不投影**（0044 决议①）——索引对 kind 零暴露，本工单的问题随之简化为：产品链的 kind 门禁（product-items）靠「产品页恒渲染全量」兜底是否可接受，索引侧无需任何 kind 相关执法。name/summary 的投影侧执法已由 0043 落定，不归本工单。

## Resolution

2026-10-22 · grilling（用户为决策者），一问定案（0044 已把本票收敛为注释处置）：

**kind 门禁归产品索引链，索引侧零执法**。门禁在 `product-items`（ADR-0006）；索引不消费 kind（0044 决议①），无需重复校验——验一个自己不消费的字段是为别人的字段执法，两处必然漂移。坏 kind 的失效由「产品页恒渲染全量 → product-items 恒被调用」触发 errorf，与索引是否存在无关；该隐式兜底的牙是 `assert_real` 的产品页全量断言（真实数据 5 条全渲染）。数据源收敛不取：product-items 返回渲染导向 dict（label/href/disabled），投影要原始字段，为门禁扭曲数据流。

**0019 边界注释改写为结论记录**（不删）：`index.json` with 块内注释从「随候选 8 定案」改为「门禁归产品索引链 / 索引零暴露 / 坏 kind 由产品页恒渲染触发 errorf / 兜底的牙是 assert_real」——删掉会让未来读者问「这里为什么不校验」。

**同场施工**（项目负责人指示）：注释已改写。本图三条线（投影字段 + fastsearch + kind 门禁）至此全部定案。

---
id: "0075"
title: 守卫模块的落点与分层：站点层还是主题层
type: grilling
mode: HITL
status: open
blocked_by: ["0073"]
assignee: ""
map: map-featured-type-guard.md
created: 2026-10-25
---

## Question

守卫模块的落点——站点层 `layouts/partials/` 还是主题层 `themes/maplemod/layouts/partials/`。已知约束：三处守卫拷贝全在站点层（post-items / product-items / _content.gotmpl）；主题层 `featured-badge.html` 是徽标唯一实现，若 0073 裁「徽标谓词收敛」，它成为模块消费方；ADR-0012 曾否决「徽标放站点层 partial」，理由之一是 theme→site 调用是全仓新先例（分层反转）；而 site→theme 调用有现成先例（`layouts/index.html` 调 `featured-badge.html`）。ADR-0008 判据：因数据结构 / 契约而变 → 站点层；守卫是契约执法，判据指向站点层。

要决策的面：

1. **落点选站点层还是主题层**；若徽标不收敛（0073 选 a），张力是否消失、答案是否随之确定。
2. **若落主题层**：契约执法放主题层是否违反 ADR-0008 判据；主题层持有站点数据契约（产品 / 注册表键名）是否可接受。
3. **若落站点层且徽标收敛**：theme→site 调用是否重开 ADR-0012 的否决（该否决的上下文是「徽标 partial 整体归站点层」，与「主题层调用站点层守卫模块」是否同型）。
4. **Hugo partial 查找序（站点层优先、主题层兜底）下，两层互调的实际约束**与既有先例清点（以 0072 事实为准）。

边界（不开票）：接口形态归 0074；消息归 0076；测试归 0077；ADR-0012 已锁部分不重开。

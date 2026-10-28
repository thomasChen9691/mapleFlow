---
id: "0080"
title: 文章卡片单模块的消费面与差异语义
type: grilling
mode: HITL
status: closed
blocked_by: ["0079"]
assignee: agent
claimed: 2026-10-27
closed: 2026-10-28
map: map-architecture-deepening.md
created: 2026-10-27
---

## Question

卡片收敛成单模块后，要覆盖哪些消费面、两处现状差异如何处置——这是「单模块」的第一个真问题：模块的**能力面**由它决定。

现状（排图日自查，待 0079 校正）：首页网格卡 `mf-post`（无 cover、无草稿标记、无 `hideMeta` 守卫、摘要不过 `Truncated` 判断）与 section/term 列表卡 `post-entry`（有 cover、草稿 SVG、`hideMeta` 守卫、`first-entry` / `tag-entry` 变体）已经**语义发散**——同一篇文在首页与列表页长得不一样，且没有任何断言记录这是有意为之。

要决策的面：

1. **消费面清单**：单模块服务哪些面——首页「最近更新」网格、section 列表、term 列表（`tag-entry` 变体）、`first-entry` 首篇大卡；哪些面**不收**（若有不收的，理由与守门方式）。
2. **三处差异的处置**：cover / 草稿标记 / `hideMeta` 守卫——统一语义（两处一致）、参数化保留（调用方开关）、还是按面固定（首页永不显示 cover 等）。逐项定。
3. **`first-entry` 的归属**：「首篇大卡」是卡片模块的变体参数，还是列表模板自己的编排决定；它与分页器位置耦合（仅第 1 页第 0 篇），归谁判。
4. **等价性口径**：收敛后允许首页视觉发生什么程度的变化（结构等价 / 允许字段增减 / 需逐像素回归）；这决定 0082 要什么强度的断言。

边界（不开票）：数据准备（`post-items.html` 的 featured 判定与截断）不动，归 ADR-0009；`featured-badge` 与 `post_meta` 的实现不动；视觉重设计属 Out of scope。

## Resolution（决议已定，施工未开始）

2026-10-27 · grilling（HITL，项目负责人四问定案；本轮为「0079 五轴质询」的一支，四票同场 grill——例外已记入地图 Notes）。

**Q1 等价性 = 一套类名、视觉零 diff**：卡片只输出一套类名，视觉不变——依据是两套 CSS 本就成对等价（`custom.css` 已有 9 组 `.post-entry, .mf-post` 双写：880/904/908/918/924/926/1083/1487/1526 行附近）。类名族随层归属定（→ [0081](0081-card-module-layer-naming-interface.md)）。代价：列表页或首页的类名会变，需一次产物对比确认零 diff。

**Q2 消费面 = 三面同卡**：首页「最近更新」网格 + section 列表 + term 列表；term 页的 `tag-entry` 类随统一消失（它唯一的 CSS 规则 `.tag-entry .entry-cover` 挂在从不存在的 cover 上）。

**Q3 `first-entry` = 删除**：不可达——首页走 `layouts/index.html`，`list.html` 的 `$.IsHome` 分支永不成立；`.first-entry` 五块 CSS（`post-entry.css:1-31`）随之进死面清单（→ [0085](0085-dead-surface-criteria-and-scope.md)）。

**Q4 三处差异 = 不参数化**：cover / 草稿标记 / `hideMeta` 统一为「**总是执行、条件自守**」——cover 恒调（空则不出）、草稿标记恒判、`hideMeta` 恒守。依据：三处差异当前**全不可观测**（全站无 content/data 设过 cover → `entry-cover` 从不渲染；草稿不进生产构建；`hideMeta` 只有模板在读）。将来某文设了 cover，首页也会显示 = 语义统一，不是回归。

**施工（2026-10-28，PR①）**：`themes/maplemod/layouts/partials/post-card.html` 落地（零参数、四段骨架、cover/draft/hideMeta 恒执行条件自守）；`layouts/index.html` 与 `themes/maplemod/layouts/_default/list.html` 改为调它；`list.html` 的 `first-entry` / `tag-entry` 分支与 `$term` 变量删除；`custom.css` 九组成对选择器合并为单选择器，`post-entry.css` 基础卡规则改名 `.post-card`。

**视觉零 diff 的两处实现细节（诚实入档）**：① 主题 `.post-card` 带 `margin-bottom: var(--gap)`（列表页历史遗留），类名统一后首页卡第一次吃到它 → 加 `.mf-posts > .post-card { margin-bottom: 0 }` 保住首页原样；② `.first-entry` / `.tag-entry .entry-cover` 等死块**未删**（归 0085 / PR②）。**未做像素级产物对比**——零 diff 由「类名 1:1 改名 + 结构断言」间接证明，非逐像素。

**验证**：site 185/185 · npm 9+28+41 · sop 105/105 · 生产构建 0 WARN · 无 localhost 泄漏。

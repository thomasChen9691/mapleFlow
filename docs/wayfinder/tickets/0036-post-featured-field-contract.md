---
id: "0036"
title: 文章 featured 字段契约
type: grilling
mode: HITL
status: open
blocked_by: []
assignee: ""
map: map-featured-mechanism.md
created: 2026-10-21
---

## Question

文章 featured 的**字段契约**——文章的「精选」如何被声明、如何被判定、缺省与坏值怎么办。这是本图所有下游决策（首页行为 / 架构落点 / 测试缝 / 派生文归属）的前置。

待决：

1. **字段名与位置**：front matter 顶层 `featured`（与产品侧 `products.yaml` 同名），还是 `params.featured`？两者在 Hugo 里取值等价，但**书写形态**影响 AI 与人类作者的可预期性，也影响 archetype 与文档措辞。
2. **缺省语义**：未声明 = 非精选（不参与）——与产品侧「缺省 false」对齐？还是未声明即精选（反向缺省）？
3. **判定严格度与坏值策略**：只认布尔 `true`，还是 truthy 也算（`"true"` 字符串、`1`）？Hugo 的 `.Param` 取值宽松，`featured: "false"` 这类字符串可能被当真值——本项目惯例是「契约失败而非兜底」（ADR-0006 负数 errorf 先例），文章侧是否也走 errorf，还是静默按非精选处理（文章是内容不是数据表，作者可能是人）？
4. **archetype**：`archetypes/default.md` 是否带 `featured: false`（新文章默认显式非精选，还是保持不写以免噪声）？
5. **跨类一致性**：文章侧与产品侧是否确立「同名同义」契约（布尔、缺省非精选、只认 true），并作为一条术语/文档级约定（`CONTEXT.md` 的「精选」条是否需补「缺省即非精选」一句）？

约束：产品侧语义已由 ADR-0006 锁定，本题只决定文章侧与之对齐还是分叉，不重开产品侧。

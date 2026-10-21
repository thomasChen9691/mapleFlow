---
id: "0036"
title: 文章 featured 字段契约
type: grilling
mode: HITL
status: closed
blocked_by: []
assignee: agent
map: map-featured-mechanism.md
created: 2026-10-21
claimed: 2026-10-21
closed: 2026-10-21
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

## Resolution

2026-10-21 · grilling（HITL，用户为决策者；五问全决）：

1. **字段**：front matter 顶层 `featured`。Hugo 中顶层未知键自动进 `.Params`，与 `params.featured` 取值等价，但书写更短、且与 `data/products.yaml` 的 `featured` 同名——**同名同义**是本题要买的东西。
2. **缺省**：未声明 = 非精选（不参与）。与产品侧缺省语义对齐。
3. **判定严格度 = 只认布尔 `true`**。实测（Hugo 0.167 临时探针，`where ... "Params.featured" true`）：bool true 入选；字符串 `"true"`、字符串 `"false"`、`yes`（YAML 解析为字符串）、整数 `1` **全部不匹配**。**`if .Params.featured` 写法禁用**——实测 `"false"` 字符串为真值，会把非精选文章放进精选区（真值陷阱）。
4. **坏值策略 = 显式 errorf**：字段存在但类型非 bool 即构建失败（用 `isset` 区分「未声明」与「写了但写错」）。理由：`where` 严格匹配的副作用是**静默排除**，作者写了 `featured: "true"` 却看不到文章上首页——属本项目明确枪毙的静默失效类（ADR-0006 负数 errorf 先例）。
5. **archetype**：`archetypes/default.md` **不加字段**，加一行注释写明字段名与语义（缺省即非精选已足够；避免 `featured: false` 与「不写」两种等价写法共存）。
6. **跨类一致性**：产品侧 `product-items.html` 一并补同款类型校验（见 0038 Resolution 第 3 条）；两侧统一为「布尔、缺省非精选、只认 true、坏值 errorf」。`CONTEXT.md` 的「精选」条补一句「缺省即非精选；坏值构建失败」。

**下游影响**：0037/0038 的入参校验与 0039 的坏值断言以此为准。

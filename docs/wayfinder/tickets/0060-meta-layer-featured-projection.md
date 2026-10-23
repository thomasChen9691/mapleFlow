id: "0060"
title: 结构化数据与社交元数据是否投影精选状态
type: grilling
mode: HITL
status: open
blocked_by: []
assignee: 
map: map-featured-fog-zones.md
created: 2026-10-23
---

## Question

文章页的精选语义是否向 meta 层投影？本票由 0056 决议一（精选标识进入文章页）触发毕业——徽标是 DOM 层信号，本票问的是投影层（`themes/maplemod/layouts/partials/templates/schema_json.html` 的 JSON-LD 与 `opengraph.html` / `twitter_cards.html` 的社交卡片）要不要同步反映精选状态。

要决策的面：

1. **做不做**：meta 层是否投影精选？若不做，负向定案并记录理由。
2. **投影什么**（若做）：形态是什么——schema.org Article 无标准 featured 字段，候选形态只有自定义属性 / keywords 追加 / 自定义 meta 标签；og/twitter 侧同理。先证明存在消费方再谈形态。
3. **契约与断言**（若做）：定义处落哪个 docstring、断言怎么锚（meta 层产物目前无任何精选相关断言）。

事实前提：`research/0055` 第 3 项（single/meta 渲染链现状）；ADR-0010 决策 4 的负向先例——「无消费方不投影」（index.json 不投影 featured，0044 同款纪律：投影字段六字段冻结）；当前无任何消费方消费精选状态（搜索引擎排序/社交 unfurl 均不识别）；徽标与 meta 之间无强制同步关系（两层服务不同消费者）。

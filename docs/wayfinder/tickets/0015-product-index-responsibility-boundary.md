---
id: 0015
title: product-index 职责边界与数据注入方向
type: grilling
mode: HITL
status: open
blocked_by: []
assignee:
map: map-product-index-narrowing.md
---

## Question

收窄后的 product-index 是「纯渲染 partial：调用方准备数据（筛选 / 限额）、传入条目列表」，还是「保持自读 `data/products.yaml`、收窄仅限入参」？即数据准备职责留在模板内还是移到调用方（shortcode / 首页 / fixture）？

背景（事实，已核）：当前 `layouts/partials/product-index.html` 自读 `hugo.Data.products`，内部按 `featured` 过滤、按 `limit` 取前 N 条；调用方共 3 处（短代码 `layouts/shortcodes/product-index.html` 传四参 dict、`layouts/index.html:110` 传 featured/limit=3/filters=false、测试 fixture 覆盖 dataDir）。「可测试」要求行为可随输入观察，「AI 可导航」要求无隐式全局依赖——两条约束如何权衡，取决于本题方向。

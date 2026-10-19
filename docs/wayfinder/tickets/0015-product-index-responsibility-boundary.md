---
id: 0015
title: product-index 职责边界与数据注入方向
type: grilling
mode: HITL
status: closed
blocked_by: []
assignee: agent
map: map-product-index-narrowing.md
claimed: 2026-10-19
closed: 2026-10-19
---

## Question

收窄后的 product-index 是「纯渲染 partial：调用方准备数据（筛选 / 限额）、传入条目列表」，还是「保持自读 `data/products.yaml`、收窄仅限入参」？即数据准备职责留在模板内还是移到调用方（shortcode / 首页 / fixture）？

背景（事实，已核）：当前 `layouts/partials/product-index.html` 自读 `hugo.Data.products`，内部按 `featured` 过滤、按 `limit` 取前 N 条；调用方共 3 处（短代码 `layouts/shortcodes/product-index.html` 传四参 dict、`layouts/index.html:110` 传 featured/limit=3/filters=false、测试 fixture 覆盖 dataDir）。「可测试」要求行为可随输入观察，「AI 可导航」要求无隐式全局依赖——两条约束如何权衡，取决于本题方向。

## Resolution

2026-10-19 · grilling（用户为决策者），三问落定：

1. **方向 = 双 seam 拆分**：`product-items`（数据准备 seam）+ `product-index`（渲染 seam）。
   - `product-items`：索引渲染链中**唯一读 `hugo.Data.products` 的宿主**，负责 featured 过滤 + limit 截断，返回 slice，不渲染。
   - `product-index`：**纯渲染**——渲染传入 items + 筛选 UI + uid，零全局读；空态文案（「暂无资源」）留渲染 seam。
   - 排除「外移到调用方」（准备逻辑三处拷贝）；排除「保持内驻」（接口泄漏原样保留）。
2. **数据准备 seam 入参契约**：`featured`（bool，缺省 false）+ `limit`（int，缺省或 0 = 全量；**负数即 errorf**——现状负数走 `gt (int .) 0` 分支外静默全量，属静默失效类，本项目做法是契约失败而非兜底）。**不留 `source` 注入位**：ADR-0004 精神（不留死参数/无缺省回落）；用户重启后端时的数据源替换届时再开新 seam，不现在预留。
3. **范围边界 = 只收窄索引渲染链**（短代码 → product-items → product-index → 产物）。首页计数条（`index.html:56`，ADR-0004 已定案、14/14 测试钉住）与搜索索引（`index.json:28`，候选 8 边界）保持各自迭代，记入雾区「调用点适配范围」。首页精选区调用点（`index.html:110`）施工时从单 seam 改走新双 seam（它本来就是渲染调用方）。

**下游影响**：0017（uid 契约）解锁——uid 随筛选 UI 归渲染 seam，形状只受本决议约束；0019（测试缝，0018 已闭）解锁——渲染 seam 零全局读后，输入组合全分支可由 fixture 数据 + 入参二维钉住。雾区「调用点适配范围」保留至施工期，条目不变。


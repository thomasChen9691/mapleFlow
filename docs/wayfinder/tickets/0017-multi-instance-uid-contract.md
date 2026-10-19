---
id: 0017
title: 同页多实例契约 uid
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

接口收窄后，同页多次调用（首页精选 + 产品页全文）的 DOM id 契约怎么走：保留显式 `uid` 入参（调用方保证唯一）、改为 partial 自动派生（如按同页调用序号）、还是随筛选 UI 移出而消失？

背景（事实，已核）：`uid` 入参存在的唯一理由是筛选脚本 `getElementById` 需要唯一根节点 id；三处调用值分别为 `mf-idx-<Ordinal>`（短代码）、`mf-idx-home`（首页字面量）、fixture（未传，走 `default "mf-idx"`）。需定：契约是否执法（同页重名即 errorf？）、自动派生的确定性来源、以及 uid 缺省值的去留。

## Resolution

2026-10-19 · grilling（用户为决策者），两问落定：

1. **uid = 显式必填**：删掉 `| default "mf-idx"` 死缺省（两个现有调用方本来就都传值，零迁移成本）。同页两实例撞 id 时第二个的 script 会静默挂到第一个上——正是本项目一直在消灭的静默失效类，必填让「忘记传」直接构建失败。短代码路径的页内唯一性由 `.Ordinal` 免费保证；模板调用方传字面量（uid 同时是深链锚，字面量有意义）。排除「保留缺省」（静默通道）与「按 filters 分支」（seam 加分支、home 深链锚消失、行为面变大）。
2. **契约强度 = 纯文档约定，不执法**：docstring 写明「同页多次调用必须不同（短代码由 .Ordinal 保证；模板调用方人工保唯一）」。不建检测机制——partial 默认无页级视野，重名检测要所有调用方多传 page 键 + `.Page.Store` 记账（成本与收益悬殊）；自动唯一（内部计数器）同样要页级状态且丢失稳定深链锚。

**下游影响**：0019（测试缝）无新约束——uid 必填属「调用方[items 缺失]」同族的调用方契约，测试手法已建立（layoutsDir 直调 partial 可再复制一格「uid 缺失」）；0020 收口无新阻塞。施工动作：product-index.html 删 `| default "mf-idx"` + docstring 补契约句 + 补「uid 缺失」坏用例一格（施工期事项，随下一批 verify-then-commit）。


---
id: 0017
title: 同页多实例契约 uid
type: grilling
mode: HITL
status: open
blocked_by: [0015]
assignee:
map: map-product-index-narrowing.md
---

## Question

接口收窄后，同页多次调用（首页精选 + 产品页全文）的 DOM id 契约怎么走：保留显式 `uid` 入参（调用方保证唯一）、改为 partial 自动派生（如按同页调用序号）、还是随筛选 UI 移出而消失？

背景（事实，已核）：`uid` 入参存在的唯一理由是筛选脚本 `getElementById` 需要唯一根节点 id；三处调用值分别为 `mf-idx-<Ordinal>`（短代码）、`mf-idx-home`（首页字面量）、fixture（未传，走 `default "mf-idx"`）。需定：契约是否执法（同页重名即 errorf？）、自动派生的确定性来源、以及 uid 缺省值的去留。

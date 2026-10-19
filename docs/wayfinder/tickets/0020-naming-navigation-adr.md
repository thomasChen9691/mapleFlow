---
id: 0020
title: 命名、导航契约与 ADR 耐久化
type: grilling
mode: HITL
status: open
blocked_by: [0015, 0016, 0017, 0019]
assignee:
map: map-product-index-narrowing.md
---

## Question

收窄定案后：模块定名（是否仍称 product-index、若拆分则各部分名字）、`CONTEXT.md` 是否新增 / 修订术语条、决策耐久化落点（修订 ADR-0004 还是新开 ADR-0006）、以及施工前必须留下的导航痕迹（AGENTS.md 坑点 / 速查表更新哪些）。

背景（事实，已核）：纪律①——阅读路由（CONTEXT.md + docs/adr/）不含 wayfinder 目录，决策必须活在 `docs/adr/`；候选 1 收口时同类决策落在 ADR-0004。**本题关闭 = 目的地到达，地图标记 closed。**

## 施工期注记（2026-10-19，待本工单追认）

按项目负责人指示，0015/0016 决议的施工已提前开工（地图未关闭）。需本题追认的施工期新增：① 渲染 seam 的「items 必填」守卫（errorf 前缀「产品索引：」）——两个工单均未要求，按「无缺省」宗教补的防御；② 两条 errorf 消息的具体措辞（limit「（got %d）」、kind 缺失时 `"<缺失>"`）；③ 两个 seam 的临时命名（product-items / product-index）是否即定名，CONTEXT.md 是否补「交付形态封闭词表 + 构建期执法」注记。

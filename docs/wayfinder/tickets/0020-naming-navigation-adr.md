---
id: 0020
title: 命名、导航契约与 ADR 耐久化
type: grilling
mode: HITL
status: closed
blocked_by: [0015, 0016, 0017, 0019]
assignee: agent
map: map-product-index-narrowing.md
claimed: 2026-10-19
closed: 2026-10-19
---

## Question

收窄定案后：模块定名（是否仍称 product-index、若拆分则各部分名字）、`CONTEXT.md` 是否新增 / 修订术语条、决策耐久化落点（修订 ADR-0004 还是新开 ADR-0006）、以及施工前必须留下的导航痕迹（AGENTS.md 坑点 / 速查表更新哪些）。

背景（事实，已核）：纪律①——阅读路由（CONTEXT.md + docs/adr/）不含 wayfinder 目录，决策必须活在 `docs/adr/`；候选 1 收口时同类决策落在 ADR-0004。**本题关闭 = 目的地到达，地图标记 closed。**

## 施工期注记（2026-10-19，待本工单追认）

按项目负责人指示，0015/0016 决议的施工已提前开工（地图未关闭）。需本题追认的施工期新增：① 渲染 seam 的「items 必填」守卫（errorf 前缀「产品索引：」）——两个工单均未要求，按「无缺省」宗教补的防御；② 两条 errorf 消息的具体措辞（limit「（got %d）」、kind 缺失时 `"<缺失>"`）；③ 两个 seam 的临时命名（product-items / product-index）是否即定名，CONTEXT.md 是否补「交付形态封闭词表 + 构建期执法」注记。

## Resolution

2026-10-19 · grilling（用户为决策者），三问落定：

1. **命名 = 文件名保留，CONTEXT.md 新增「产品索引」一条术语**：`product-items.html` / `product-index.html` 临时名即定名，不折腾；术语表只载领域概念——「产品索引」= 产品列表渲染物（产品页全量 + 首页精选分栏两个消费点，由数据准备 seam 与纯渲染 seam 协作产出）；seam 分工是文件级细节，进 AGENTS.md 速查表，不进术语表。施工期注记①②（items 守卫、errorf 措辞）随本题追认。
2. **ADR 耐久化 = 新开 ADR-0006**：候选 4 决策集（双 seam 拆分 / kind 契约化写死 / limit 与 uid 契约 / 测试缝合流）主题是 product-index 接口，与 ADR-0004（产品状态模块）主体不同——独立成篇，ADR-0004 只加一行指针（「产品索引接口收窄见 ADR-0006」）。先例：ADR-0005 每候选一 ADR。
3. **导航痕迹 = 三处齐落**：① AGENTS.md §7 速查表 +2 行（`layouts/partials/product-items.html` = 数据准备 seam：渲染链唯一读 `hugo.Data.products` 处，kind 词汇契约 + featured/limit；`layouts/partials/product-index.html` = 纯渲染 seam：items/uid 必填、零全局读）；② 坑点节 +1 条「产品索引接口纪律」（数据准备只此一处 / 渲染 seam 不收裸数据 / 同页多实例 uid 唯一——短代码 .Ordinal 保唯一、模板调用方人工）；③ CONTEXT.md「交付形态」条补注「封闭词表由 product-items 在构建期执法」（0016 遗留事项）。

**本题关闭 = 目的地到达，地图标记 closed。** 剩余施工（文档写入，不涉新决策）：写 ADR-0006 + ADR-0004 指针行、CONTEXT.md 术语条与交付形态注记、AGENTS.md 速查两行与坑点一条、地图 closed。测试与代码已全部就位（产品 29/29、SOP 100/100）。


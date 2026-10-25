---
id: "0076"
title: 守卫的错误消息与命名契约：三前缀统一还是参数化
type: grilling
mode: HITL
status: open
blocked_by: ["0074"]
assignee: ""
map: map-featured-type-guard.md
created: 2026-10-25
---

## Question

守卫模块的错误消息与命名契约。现状三前缀：「文章精选数据：」（post-items）、「产品索引数据：」（product-items）、「SOP 发布管线：」（_content.gotmpl）；测试期望子串钉前缀（`assert_site_contracts.py` 的 `POSTS_BAD_FEATURED_EXPECT` 与 `BAD_CASE_EXPECT["featured-not-bool"]`、`assert_sop_pipeline.py` 的 `BAD_CASE_EXPECT`）。单模块后消息必须单一来源，但三前缀各携定位信息（哪条链的坏值）。

要决策的面：

1. **消息形态**：统一前缀（如「精选类型守卫：」）+ origin 参数（调用方传「文章精选数据」/「产品索引数据」/「SOP 发布管线」），还是保留三前缀由模块外调用方拼装？origin 参数化与 0074 接口形态的衔接。
2. **消息即测试锚**：三套件期望子串随消息形态的迁移成本与迁移时机（随施工批，不随本图）。
3. **模块文件命名**（候选：`featured-guard.html` / `mf-featured-guard.html` / `featured-type-guard.html`）——与既有两个 featured partial（`post-items.html` / `featured-badge.html`）的命名族一致。
4. **「守卫」一词是否入 CONTEXT.md「精选 (Featured)」条**（ADR-0014 决策 9 先例：harness 不入术语表——「类型守卫」是对外领域语言还是实现细节）。

边界（不开票）：接口归 0074；测试期望字面量的独立值不动（三层文档契约，字面量留套件）。

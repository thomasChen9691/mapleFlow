---
id: "0076"
title: 守卫的错误消息与命名契约：三前缀统一还是参数化
type: grilling
mode: HITL
status: closed
blocked_by: ["0074"]
assignee: agent
map: map-featured-type-guard.md
created: 2026-10-25
claimed: 2026-10-26
closed: 2026-10-26
---

## Question

守卫模块的错误消息与命名契约。现状三前缀：「文章精选数据：」（post-items）、「产品索引数据：」（product-items）、「SOP 发布管线：」（_content.gotmpl）；测试期望子串钉前缀（`assert_site_contracts.py` 的 `POSTS_BAD_FEATURED_EXPECT` 与 `BAD_CASE_EXPECT["featured-not-bool"]`、`assert_sop_pipeline.py` 的 `BAD_CASE_EXPECT`）。单模块后消息必须单一来源，但三前缀各携定位信息（哪条链的坏值）。

要决策的面：

1. **消息形态**：统一前缀（如「精选类型守卫：」）+ origin 参数（调用方传「文章精选数据」/「产品索引数据」/「SOP 发布管线」），还是保留三前缀由模块外调用方拼装？origin 参数化与 0074 接口形态的衔接。
2. **消息即测试锚**：三套件期望子串随消息形态的迁移成本与迁移时机（随施工批，不随本图）。
3. **模块文件命名**（候选：`featured-guard.html` / `mf-featured-guard.html` / `featured-type-guard.html`）——与既有两个 featured partial（`post-items.html` / `featured-badge.html`）的命名族一致。
4. **「守卫」一词是否入 CONTEXT.md「精选 (Featured)」条**（ADR-0014 决策 9 先例：harness 不入术语表——「类型守卫」是对外领域语言还是实现细节）。

边界（不开票）：接口归 0074；测试期望字面量的独立值不动（三层文档契约，字面量留套件）。

## Resolution

2026-10-26 · grilling（HITL，项目负责人三问定案）：

**Q1 消息形态 = 保留 origin 三前缀**：三前缀逐字（「文章精选数据：」「产品索引数据：」「SOP 发布管线：」），由调用方经 origin 传入——测试期望子串零改写；链身份（哪条链坏了）不丢；模块只持 errorf 骨架、不持措辞（0073 Q3 边界）。统一前缀的收益（单一 grep 词）不抵「三套件期望子串全改 + 消息变长」。

**Q2 label = 调用方格式化**：label 是**定位值**不是措辞——调用方最懂自己的定位形态（permalink / `%q` 引号 id / 「条目 %s」）；「条目」二字留在它所属的 SOP 链，不污染通用模块；模块只做字符串拼接。

**Q3 命名与术语**：文件名 **`featured-guard.html`** 定案（与 `featured-badge` / `post-items` 同族）；术语表**不新增**「守卫」词条（实现机制不是对外领域语言，ADR-0014 决策 9 先例）；`CONTEXT.md`「精选」条加一句 guard 指针（与 badge 指针并列，ADR-0012 同款体例）。

**施工**：CONTEXT.md 指针已落；消息与命名与已落地实现一致——**零代码改动**。

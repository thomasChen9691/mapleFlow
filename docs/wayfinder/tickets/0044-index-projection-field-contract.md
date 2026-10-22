---
id: "0044"
title: 索引投影字段契约
type: grilling
mode: HITL
status: open
blocked_by: [0042, 0043]
map: map-search-contract.md
created: 2026-10-22
---

## Question

index.json 每条投影记录的字段契约是什么？具体待决：

1. **字段集取舍**：现状六字段（title / permalink / summary / content / tags / categories）哪些保留；是否新增——`featured` 投影与否（ADR-0009 遗留边界：投影后 fastsearch 的 keys 是否消费、UI 是否区分；若无人消费，投影是否为「死字段」——参数纪律的投影版）；`kind` 是否投影（与 0045 门禁决策联动）。
2. **字段语义与变换是否契约化**：`summary = .Summary | plainify | htmlUnescape | chomp` 后 `truncate 200`；`content` 与 `summary` **同源**（现状即取同一 `$summary` 截断到 320，并非正文——搜索的 content 字段实际不含文章正文，此事实须向用户显式确认是否有意设计）；产品条目 `content = name + summary + scale` 拼接、`tags`/`categories` 硬编码 `["产品"]`。
3. **排除规则是否契约化**：searchHidden、Layout archives / search 三类排除的语义与执法方式（契约注释 / 测试断言 / errorf）。
4. **坏输入是否 errorf**：产品缺 name / summary、页面 Summary 为空等——「无缺省」宗教（ADR-0004 / 0006 先例：契约失败而非兜底）是否适用于投影层，还是投影层宽容缺失、由前端消费方容错（fastsearch 渲染时字段缺失的行为）。

背景（事实）：现状投影无任何 errorf，坏数据静默进索引；fastsearch 默认 keys = title / permalink / summary / content，tags / categories 是「供扩展检索」的既存字段（index.json 头注）。

**0043 已决输入**：投影守自消费字段，name/summary 缺失即 errorf（前缀「搜索索引数据：」，本条定字段级细节）；summary/content 同源是否有意设计仍是本条的待决面；truncate 200/320 取值是否入契约归本条（原雾区「索引体积治理」并入）；SOP 注册表缺 intro 的 %!s() 污染归发布管线契约（ADR-0005 地盘），本条只记边界、不做投影层执法。

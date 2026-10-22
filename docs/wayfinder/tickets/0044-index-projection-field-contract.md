---
id: "0044"
title: 索引投影字段契约
type: grilling
mode: HITL
status: closed
blocked_by: [0042, 0043]
assignee: agent
map: map-search-contract.md
created: 2026-10-22
claimed: 2026-10-22
closed: 2026-10-22
---

## Question

index.json 每条投影记录的字段契约是什么？具体待决：

1. **字段集取舍**：现状六字段（title / permalink / summary / content / tags / categories）哪些保留；是否新增——`featured` 投影与否（ADR-0009 遗留边界：投影后 fastsearch 的 keys 是否消费、UI 是否区分；若无人消费，投影是否为「死字段」——参数纪律的投影版）；`kind` 是否投影（与 0045 门禁决策联动）。
2. **字段语义与变换是否契约化**：`summary = .Summary | plainify | htmlUnescape | chomp` 后 `truncate 200`；`content` 与 `summary` **同源**（现状即取同一 `$summary` 截断到 320，并非正文——搜索的 content 字段实际不含文章正文，此事实须向用户显式确认是否有意设计）；产品条目 `content = name + summary + scale` 拼接、`tags`/`categories` 硬编码 `["产品"]`。
3. **排除规则是否契约化**：searchHidden、Layout archives / search 三类排除的语义与执法方式（契约注释 / 测试断言 / errorf）。
4. **坏输入是否 errorf**：产品缺 name / summary、页面 Summary 为空等——「无缺省」宗教（ADR-0004 / 0006 先例：契约失败而非兜底）是否适用于投影层，还是投影层宽容缺失、由前端消费方容错（fastsearch 渲染时字段缺失的行为）。

背景（事实）：现状投影无任何 errorf，坏数据静默进索引；fastsearch 默认 keys = title / permalink / summary / content，tags / categories 是「供扩展检索」的既存字段（index.json 头注）。

**0043 已决输入**：投影守自消费字段，name/summary 缺失即 errorf（前缀「搜索索引数据：」，本条定字段级细节）；summary/content 同源是否有意设计仍是本条的待决面；truncate 200/320 取值是否入契约归本条（原雾区「索引体积治理」并入）；SOP 注册表缺 intro 的 %!s() 污染归发布管线契约（ADR-0005 地盘），本条只记边界、不做投影层执法。

## Resolution

2026-10-22 · grilling（用户为决策者），四问落定：

1. **字段集冻结为六字段**：**不投影 featured**（ADR-0009 遗留边界——无消费方：fastsearch keys 不含、结果 UI 只渲染标题+链接；投影即死字段且会打破 0043 立的差集断言；精选归首页编排语义）。**不投影 kind**（页面侧无此字段、搜索 UI 无 kind 筛选器；索引对 kind 零暴露，0045 的门禁归属问题随之简化为「隐式兜底是否可接受」）。
2. **summary/content 同源确认为有意设计**（原始 P2-6 头注「瘦身：content 不再塞整篇正文」是明证），写入契约；**truncate 200/320 为调值**——仅文档不断言（与 fuse 参数同属「调值不属契约」边界；精确截断断言会被 Hugo truncate 省略号行为搞得脆弱）。
3. **产品条目形态全加断言**：title=name、permalink=`products.html#<id>`、content=`name + summary + scale` 拼接，期望值取 fixture 五条产品的独立字面量，落既有 dataDir fixture 构建（零新增构建）。

**同场施工**（项目负责人指示，TDD）：产品条目三组断言先表征绿、后变异红（permalink 格式 / content 拼接 / title 各红一次再还原）；docstring ① 补记字段集冻结与同源确认；index.json 逻辑零变更（字段集不动）。

**下游**：0045 因 kind 不投影而简化；0047 拿到产品条目牙口（仍挂既有 fixture 构建）；负向决策（不投影什么）随 docstring ① 落位，防未来「为什么没有 featured」的重复讨论。

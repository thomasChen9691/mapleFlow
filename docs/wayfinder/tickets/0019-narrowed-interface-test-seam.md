---
id: 0019
title: 接口收窄后的测试缝形状
type: grilling
mode: HITL
status: open
blocked_by: [0015, 0018]
assignee:
map: map-product-index-narrowing.md
---

## Question

接口收窄后，「可测试」落在哪个缝上：哪些 fixture 构建 × 哪些产物断言，才能覆盖输入组合全分支（含空态、限额、筛选开关、多实例）？缝与 `tests/assert_product_states.py` 合流为一个套件还是独立脚本？CI 守门策略（权威 / advisory）如何安排？

背景（事实，已核）：ADR-0004 已定测试总原则——Hugo 生态无模板单测机制，只能 build-then-assert；契约执法在模块内 `errorf`、构建即门禁；CI 权威 + 本地 advisory；双构建（fixture 全分支 + 真实数据线上回归）。定案须遵守这些闭卷原则，只回答「针对收窄后接口的具体缝形状」。

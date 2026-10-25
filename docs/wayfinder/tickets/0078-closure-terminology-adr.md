---
id: "0078"
title: 收口：守卫单模块的术语、导航与 ADR 耐久化
type: grilling
mode: HITL
status: open
blocked_by: ["0073", "0074", "0075", "0076", "0077"]
assignee: ""
map: map-featured-type-guard.md
created: 2026-10-25
---

## Question

目的地到达后的收口三产出——术语、导航与 ADR 耐久化。本票在 0073-0077 全部闭环后开。

要决策的面：

1. **术语**：`CONTEXT.md`「精选 (Featured)」条如何扩写指向守卫模块（措辞含「类型守卫」概念与模块指针；「守卫」一词是否入术语表若 0076 未决则由本票决）。
2. **导航**：`AGENTS.md` 坑点 11 与 §7 速查表如何改——新增守卫模块行；三处拷贝的 docstring 守卫段落改为指针（落地随施工批的尺度归本票定）。
3. **ADR 形态**：新开 ADR-0015 承载守卫单模块决策集，还是 ADR-0009 加指针行（先例：ADR-0012 新开、ADR-0009 加指针）。
4. **handoff 与 backlog**：收口 handoff 落 `docs/handoffs/`；本图出处（架构评审候选②）是否需要在 `docs/backlog.md` 记一笔。

边界（不开票）：施工批次本身（partial + 三处改写 + fixture + 断言）——待项目负责人指示后展开，不随收口批。

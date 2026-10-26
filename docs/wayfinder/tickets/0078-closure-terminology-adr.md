---
id: "0078"
title: 收口：守卫单模块的术语、导航与 ADR 耐久化
type: grilling
mode: HITL
status: closed
blocked_by: ["0073", "0074", "0075", "0076", "0077"]
assignee: agent
map: map-featured-type-guard.md
created: 2026-10-25
claimed: 2026-10-26
closed: 2026-10-26
---

## Question

目的地到达后的收口三产出——术语、导航与 ADR 耐久化。本票在 0073-0077 全部闭环后开。

要决策的面：

1. **术语**：`CONTEXT.md`「精选 (Featured)」条如何扩写指向守卫模块（措辞含「类型守卫」概念与模块指针；「守卫」一词是否入术语表若 0076 未决则由本票决）。
2. **导航**：`AGENTS.md` 坑点 11 与 §7 速查表如何改——新增守卫模块行；三处拷贝的 docstring 守卫段落改为指针（落地随施工批的尺度归本票定）。
3. **ADR 形态**：新开 ADR-0015 承载守卫单模块决策集，还是 ADR-0009 加指针行（先例：ADR-0012 新开、ADR-0009 加指针）。
4. **handoff 与 backlog**：收口 handoff 落 `docs/handoffs/`；本图出处（架构评审候选②）是否需要在 `docs/backlog.md` 记一笔。

边界（不开票）：施工批次本身（partial + 三处改写 + fixture + 断言）——待项目负责人指示后展开，不随收口批。

## Resolution

2026-10-26 · grilling（HITL，项目负责人六问定案）：

**Q1 ADR 形态 = 新开 ADR-0015 + 双指针**：15 条决策（0073–0077）各注工单号；ADR-0009（Consequences「改精选 = 改 post-items + index.html」）与 ADR-0012（决策 2「坏值执法继承 post-items.html:32-38」）各加一行指针，正文不改（历史记录）。只加指针会让 15 条决策散落工单、违反 ADR-0004；只新开会让旧 ADR 的过期归属无指针可循。

**Q2 三层分工 = 各司其职**：ADR = 决策集耐久化；工单 Resolution = 推理链；docstring = 执行契约。三层互不重述（ADR-0007 / ADR-0014 既有分工）。

**Q3 地图形态 = gist + ADR 指针**：保留现有 gist 行（一眼判断相关性），每行追加「→ ADR-0015 决策 N」；不收成裸题目索引（丢 gist 违背「一行足够判断相关性」的地图体例）。

**Q4 backlog = 不记**：候选②非 backlog 来源（与候选①/harness 先例一致）；出处已在 ADR-0015 背景段与收口 handoff 留痕。

**Q5 改动面 = 纯文档**：ADR + 双指针 + 地图 closed + handoff + README 计数修正；**不动代码、不动断言**——site 159 / sop 105 / npm 8+23+41 原样存活。

**Q6 handoff = 单份收口**：`docs/handoffs/2026-10-26-featured-guard-closure.md`（收口态 / 15 条决策一句话 / 未推状态与基数注意 / 下一步 / 环境坑）。

**收口产出核对**：ADR-0015 落盘（15 条决策）；ADR-0009 / ADR-0012 指针行落盘；地图 status closed + 五条 ADR 决策号 + 例外记录（四票同场）；handoff 落盘；README 计数（ADR 15 篇、交接 18 份、wayfinder 11/78/11）。**frontier 空 = 目的地到达**。

**事实修正（声明先对树验证后写入的产物）**：决策条数 11→**15**（此前口头的 11 只含 0074–0077，ADR 须含 0073 四问；4+3+2+3+3=15）；交接份数 11→**17**（此前只看了 `ls -t | head -10`，实际 17 份，收口后 18 份）。

id: "0059"
title: 收口：术语、导航与 ADR 耐久化
type: grilling
mode: HITL
status: open
blocked_by: ["0056", "0057", "0058"]
assignee: 
map: map-featured-fog-zones.md
created: 2026-10-23
---

## Question

三面决策（0056 / 0057 / 0058）定案后，本图如何收口——**本题关闭 = 目的地到达（决策面）**。

要决策的面：

1. **ADR 形态**：决策集耐久化到哪——新开 ADR-0012（三条雾区是 ADR-0009 的延续但决策面独立：徽标契约 / 数据条口径 / 分类页消费），还是 ADR-0009 加指针行（其正文不改、指针行是先例）？判据：难逆决策才写 ADR（工程纪律 3）+ 决策必须活在 `docs/adr/`（ADR-0004 立过的规矩，AGENTS §8.1 阅读路由不含 wayfinder）。
2. **术语**：`CONTEXT.md`「精选 (Featured)」条是否扩写（内容层呈现 / 数据条 / 分类页消费的新语义）；要不要新增术语条（排图期不预设用词，此刻已有三面决议才可精确措辞）。
3. **导航**：`AGENTS.md` 坑点 11（文章精选纪律）是否补三条雾区的纪律；§7 速查表要不要加行（如徽标契约的定义处文件）。
4. **收口动作**：`docs/backlog.md` 第 13 项标记完成；写 handoff（`docs/handoffs/`）；本地图 `status: closed`；地图 Decisions so far 补齐三面 gist；雾区三条按既定方式处理（毕业为新工单 / 随 closed 地图挂起 / 消解——逐条定）。

边界（不开票）：施工批次划分与 CI 验证节奏归项目负责人（本图只到可施工状态）；内容填充不随图。

---
id: 0014
title: SOP 管线的命名与导航契约
type: grilling
mode: HITL
status: open
blocked_by: [0013]
assignee:
map: map-sop-source-sync
---

## Question

管线定名、术语落点、决策耐久化——本图收口工单。

- **模块命名**：候选如「SOP 发布管线」/「SOP 派生模块」/「源笔记管线」。命名须与 `CONTEXT.md` 现词汇（SOP 文、源笔记、文章）自洽——是收敛不是新增同义词。
- **术语更新**：`CONTEXT.md` 的「源笔记」条目（现声称「是 SOP 文的上游」）随机制落地变为机械真实，还是需要改写（若 0008 裁 content/posts 赢则必须改写）。当场更新，不攒批。
- **决策耐久化**：本图决策是否落 ADR-0005——按三问检验（难逆转 + 无上下文会惊讶 + 源于真实权衡）。参照 ADR-0004 的先例：决策必须活在 `docs/adr/`，因为 AGENTS.md §9.1 的阅读路由不含 wayfinder 目录。
- **AI 导航路由**：AGENTS.md §9.1 的既有阅读路径（CONTEXT.md + docs/adr/）是否足够让未来会话发现本管线，还是需要在 `docs/sop/README.md` 或 AGENTS.md 关键文件速查表加指针。

本题关闭 = 目的地到达，地图标记 closed。

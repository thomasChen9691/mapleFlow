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

## 预裁记录（工单 0008 质询，2026-10-15）

命名候选已向「**SOP 发布管线**」收敛（seam = `_content.gotmpl` + `data/sop.yaml` + `docs/sop/`；「管线」准确表达「笔记→注册表→构建期生成」的流向，且不与 CONTEXT.md 现词汇冲突）。`CONTEXT.md`「源笔记」条目预计**无需改写**——目录契约（0009 决议第 1 条）让其定义「尚未发布的 SOP 稿件」原生为真。进入 frontier 后正式落档并裁 ADR-0005 是否记录。

**实施期注记（2026-10-15，code-review 发现）**：AGENTS.md 坑点 10 + 关键文件速查表三行已于实现期提前落地——评审判定此举越权（本题第 4 问「AGENTS.md 是否加指针」未决），但方向无害且服务目的地「AI 可导航」。本题进入 frontier 时，对该文档同步做 **ratify/adjust**（保留、修正或回撤），不从零重决。

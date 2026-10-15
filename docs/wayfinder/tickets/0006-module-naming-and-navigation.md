---
id: 0006
title: 模块命名与导航契约
type: grilling
mode: HITL
status: closed
blocked_by: []
assignee: agent
map: map-product-state-convergence
claimed: 2026-10-15
closed: 2026-10-15
---

## Question

「AI 可导航」的落点：模块叫什么（定稿后进入 `CONTEXT.md` 成为标准术语）、放在哪个文件（单一入口）、文档如何指向它（`AGENTS.md` 关键文件速查表是否加一行）。

命名候选：产品状态模块 / 上架状态模块 / 领取入口模块。命名须与 `CONTEXT.md` 现词汇（领取入口、已上架、即将上架、可下载产品）自洽 —— 是收敛不是新增同义词。

## Resolution

2026-10-15 · grilling（用户为决策者），两问落定：

1. **定名「产品状态模块」**：`layouts/partials/product-state.html`。三件职责（上架判定 + 免费判定 + 控件语义）都在「状态」伞下，与 CONTEXT.md 现词汇（即将上架/已上架为状态词）同族。否决「上架状态」（免费判定在名字里无住所，制造 F2 式困惑）与「领取入口」（数据字段名装不下模块职责）。CONTEXT.md 术语条已按纪律④当场写入。
2. **耐久性 = ADR-0004 一份**：《产品状态模块：seam、形状与测试策略》。核心理由：纪律①规定新会话只读 CONTEXT.md + docs/adr/——决策若只活在地图里，未来会话按纪律不可见。ADR 内放指针回本地图与工单，不复制全文。

**地图状态**：本题关闭后 6 张工单全部 closed、雾区已空——目的地到达，地图标记 closed。执行期 backlog（不在地图内，见下方移交清单）。

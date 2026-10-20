---
id: 0026
title: 术语、seam 命名与 ADR 收口
type: grilling
mode: HITL
status: closed
blocked_by: [0023, 0024, 0025]
assignee: agent
map: map-reveal-protocol.md
claimed: 2026-10-20
closed: 2026-10-20
---

## Question

收口三件套（参照工单 0014 / 0020 先例）：

1. **CONTEXT.md 术语**：新增「reveal 协议」主条目；值得单独命名的子概念有哪些（is-in 终态？筛选语义？no-js 基线在 ADR-0002 已用自然语言描述，是否收编为术语）？纪律：术语表不载文件布局，seam 分工进 AGENTS.md 速查表。
2. **命名与导航**：seam 文件/资源命名、AGENTS.md 导航痕迹（速查表行、坑点条）。
3. **ADR 耐久化**：新开 ADR-0007 承载候选 5 决策集；处理与 ADR-0002（基线）、ADR-0006（产品索引双 seam，filters/uid 的归属）的指针关系。本题关闭 = 目的地到达，地图标记 closed。

## Resolution

2026-10-20 · grilling（用户为决策者），四问落定：

1. **术语范围 = 只加主术语**：CONTEXT.md 新增「reveal 协议」一条——概念级定义（no-js 渐进增强基线之上、由 `assets/js/mf-reveal` 引擎实现的客户端动效交互契约；契约定义处 = 引擎 docstring）+ _Avoid_（动效系统 / 动画库 / reveal 组件）；`is-in`、`mf-rise`、筛选语义等实现级词汇**不进**术语表。理由：0020 先例——术语表不载文件布局/实现细节，只放领域概念；`is-in` 是 DOM class 名，收进术语表会把它钉成领域概念。
2. **`motion.js` → `reduced-motion.js`**：名直述内容（唯一降级判定）；改两处 import + docstring。0025 决议明留命名给本题，评审的 Mysterious Name 由此消解。
3. **AGENTS 导航 = 行 + 坑点 + 命令**：速查表加一行目录级（`assets/js/mf-reveal/`：reveal 协议契约定义处；行为 `npm test`、产物 `tests/assert_product_states.py`）；坑点加一条（改契约先跑两套件；契约定义处在引擎 docstring 而非 CONTEXT.md）；§3 核心命令加 `npm test`（0023 决议明留）。
4. **ADR-0007 + 指针**：新开 ADR-0007 承载候选 5 六工单决策集（分层提取 / 三层文档契约 / 命名权归协议层 / 测试缝（CI 权威、两套件、手写样本）/ 交互语义 / 一次性终态 + 降级统一）；ADR-0002、ADR-0006 各加一行指针（**不改正文**——ADR 是历史记录；0006 给 0004 加指针行是先例）。

**本题关闭 = 目的地到达，地图标记 closed。** 施工动作（待用户指示）：CONTEXT.md 术语条、`motion.js` 改名、AGENTS 三处、ADR-0007 + 两处指针、地图状态改 closed 并写收口注记。

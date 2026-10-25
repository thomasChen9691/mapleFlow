id: "0067"
title: harness 的文档 seam 与导航入口
type: grilling
mode: HITL
status: open
blocked_by: ["0062"]
map: map-test-harness-convergence.md
created: 2026-10-25
---

## Question

Destination 要求 harness **AI 可导航**。项目既有模式是三层文档契约：CONTEXT.md 只放概念、引擎 / seam 文件头 docstring 是契约唯一定义处、测试承载期望值字面量；AGENTS.md 速查表是目录级导航。harness 是内部基建（不是对外概念），它适用哪几层、以什么形态落，需单独定。

要决策的面：

1. **契约定义处的形态**：harness 模块采用文件头 docstring 为唯一定义处（复刻 mf-reveal / fastsearch / index.json 引擎模式）——docstring 写什么（消费者契约：每个入口的入参 / 产物 / 失败行为；写什么不算契约——视觉与内部实现细节）；「harness 无 DOM 契约」是否让它比引擎契约薄，薄到什么程度仍需 docstring。
2. **术语层**：「harness」是否进 CONTEXT.md——CONTEXT.md 是对外领域术语表（内容形态 / 发布管线 / 产品 / 搜索 / 交互 / 站点架构），测试基建是内部事，初步判断不入；若入，措辞与 _Avoid_ 对立词由本票定。定名权：模块叫什么（harness / testkit / runner……）与术语是否入表，是同一决策还是分开。
3. **导航入口**：AGENTS.md 落点——§3 命令区（harness 相关命令怎么呈现）、§7 速查表（目录级一行）、坑点区（哪些既有坑点因 harness 收敛而改写，如「串行约束」坑点若被分根消解）；新会话（人或 AI）从 AGENTS.md 到 harness 文档的路径不超过几步。
4. **与收口的关系**：本图收口时 harness 的导航落点是否必须同批落地（对照历史先例：候选 12/13 收口批含 AGENTS.md 与术语同步）——还是允许「决策已决、文档随施工批落」；若允许，地图需记录这个未落地项防丢。

边界（不开票）：模块物理形态归形态工单；测试入口（npm test / CI）归可测性工单——本票只决「契约写在哪、术语入不入表、导航怎么走」。

事实前提：ADR-0007 三层文档契约（概念 / docstring / 字面量）；AGENTS.md §3 / §7 / 坑点区现状；CONTEXT.md 现有分区（无测试基建区）。

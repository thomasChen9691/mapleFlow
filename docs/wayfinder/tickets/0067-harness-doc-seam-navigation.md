id: "0067"
title: harness 的文档 seam 与导航入口
type: grilling
mode: HITL
status: closed
assignee: agent
blocked_by: ["0062"]
map: map-test-harness-convergence.md
created: 2026-10-25
claimed: 2026-10-25
closed: 2026-10-25
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

## Resolution

2026-10-25 · grilling（HITL，项目负责人三问定案；六票同场例外见地图 Notes）：

**契约定义处（Q1）**：**批准现行两份文件头 docstring 为唯一定义处**——harness.py（seam 五承诺三禁止 + 待接缝 + 残留清点 + sop_golden 互防）与 dom.mjs（导出契约 + 两种装配模式）。这是 ADR-0007 三层文档契约的 harness 侧落地：概念层（不入术语表，见 Q2）+ docstring 唯一定义处 + 自测承载期望字面量（0066）。拒绝：docstring 内写示例（示例会漂移，行为规格归自测）；拆 spec seam（ADR-0007 决策 3 已拒，harness 无 DOM 契约、比引擎更薄）。

**术语层（Q2）**：**「harness」不入 CONTEXT.md**——术语表是对外领域语言（内容形态 / 发布管线 / 产品 / 搜索 / 交互 / 站点架构），测试基建是内部实现细节。一词的定型场所 = harness.py docstring 首段（「一个概念，两个文件」已写）+ AGENTS.md §7 速查行。拒绝：新开「测试基建」分区（术语表开始承载实现细节）；一行指针骑墙（对不上现有词条的完整规格）。

**导航落点（Q3）**：AGENTS.md 三处**随施工批同步落地**（不等本图收口——导航先于实体存在会写将来的形状，形态若有变则二次改）：§7 速查表加两行（tests/harness.py / tests/dom.mjs，注明契约定义处与消费方）；§3 命令区随 0066 自测落地同步（npm test 扩链在 package.json，AGENTS.md 只述不变性）；§4 坑点区补一条（坏用例 fixture 按模块子根、tmp 按套件分根、无串行约束）。本图收口时记录未落地项防丢。

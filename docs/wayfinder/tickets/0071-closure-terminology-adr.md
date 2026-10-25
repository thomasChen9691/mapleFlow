id: "0071"
title: 收口：harness 收敛的耐久化与地图关闭
type: grilling
mode: HITL
status: open
blocked_by: ["0069"]
map: map-test-harness-convergence.md
created: 2026-10-25
---

## Question

0061–0070 十票的决策面走完后，本图如何收口：harness 收敛的已决决策如何耐久化、地图关闭条件是什么、哪些未落地项如何记录防丢。

要决策的面：

1. **ADR 形态**：harness 收敛的决策集（边界判据 / 模块形态 / seam 五承诺三禁止 / tmp 分根 / dest 归 harness / 旗标档位 / 配置写入入口 / 自测缝 / 文档 seam / 预检归属 / golden 并列）是否值得一份新 ADR 耐久化，还是只留在工单 Resolution 里（wayfinder 是过程、决策耐久化进 ADR 的既有规矩——docs/README.md 明言「决策只活在 docs/adr/」）？若立 ADR，边界怎么划（一份总纲 vs 按主题拆）。
2. **未落地项的登记**：施工批尚未执行的已决项（0063 旗标档位、0064 配置入口、0066 自测双文件、0067 AGENTS.md 三处、0068 glob 修正、0070 对称互防）随 0069 迁移批落地——收口时这些「已决未建」项记在哪（地图 Notes？handoff？），防它们在地图关闭后丢失。
3. **与旧批的关系**：本图之前已施工的两批（bad/ 拆子根、harness 模块收敛）未推未过 CI（GitHub auth-required）——收口是否等待 CI 证据（历图收口批含 CI 复跑全绿的先例），还是接受「本地全绿 + 待推」状态。
4. **handoff 形态**：是否随收口写 handoff（docs/handoffs/ 惯例：状态、决策、下一步、环境坑点——本图的环境坑至少有一条：safe-delete 每轮删除预算 5000 会拦套件 rmtree）。

边界（不开票）：具体施工动作不归本票（已各有其票或随 0069）；候选⑤其余死面不随本图；术语入不入 CONTEXT.md 已由 0067 定案（不入）。

事实前提：0061–0070 的 Resolution 全文；docs/README.md 的「决策只活在 docs/adr/」规矩；docs/handoffs/ 的历史形态。

id: "0071"
title: 收口：harness 收敛的耐久化与地图关闭
type: grilling
mode: HITL
status: closed
assignee: agent
blocked_by: ["0069"]
map: map-test-harness-convergence.md
created: 2026-10-25
claimed: 2026-10-25
closed: 2026-10-25
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

## Resolution

2026-10-25 · grilling（HITL，项目负责人四问定案；与 0069 同场，经指示的第三次「一会话多票」例外，地图 Notes 已记）：

**耐久化形态（Q1）**：**一份总纲 ADR-0014「测试基建 harness 收敛」**——背景（四套件重复分布与架构评审结论）+ 决策集十一条（各注工单号可溯源：边界判据 0061 / 模块形态 0062 / tmp 所有权 0065 / 旗标档位 0063 / 配置写入入口 0064 / 自测缝 0066 / 文档 seam 0067 / 预检归属 0068 / golden 并列 0070）+ 后果（seam 纪律、纳入双门槛、未决接缝指针）。工单 Resolution 保留为过程记录——决策进 ADR、推理链留工单，两不混。拆多份拒：四条决策互相咬合（seam 禁止项是纳入判据的前提），拆开割裂推理链。不立 ADR 拒：违反 docs/README.md「决策只活在 docs/adr/」。

**待建登记面（Q2）**：**登记为「空集」，面溶解**——开票时列的六项已决未建（0063 档位 / 0064 入口 / 0066 自测 / 0067 文档 / 0068 glob / 0070 互防）已于 `cd531ea` 全部落地，提交信息逐项对应；收口清单无未落地项，ADR「后果」节直接指向已建成形态。仍建对照表拒：第三份索引违反「地图是索引不是仓库」同款纪律。

**CI 证据（Q3）**：**不等 CI**——分支模型（AGENTS.md §2 规则集 Require status checks）已把 verify job 设为 PR 合入硬门禁，CI 证据在开 PR 时自然产生且不绿合不进去；地图关闭条件 = 决策面走完 + 本地全绿 + 提交就绪。「分支 5 笔 + 基点 4 笔共 9 笔未推、PR 未开、GitHub auth-required」在 handoff 与地图 Notes **显著记录**——不记录将重演候选⑤「资产完备性」式烂尾。

**handoff（Q4）**：**写完整 handoff**（`docs/handoffs/2026-10-25-harness-convergence-closure.md`）：状态（图闭、9 笔未推、PR 未开）/ 决策（ADR-0014 指针 + 十一条一句话）/ 下一步（恢复 GitHub 授权 → 推分支 → 开 PR → 门禁绿 → squash 合并）/ 环境坑（safe-delete 每轮删除预算 5000 拦套件 rmtree、单命令进程数上限、execFileSync 嵌套 spawn 偶发 kill、CI 钉版 0.164 纪律）。

**收口施工范围**（本票决议的产出，待负责人指示后展开）：ADR-0014 撰写、handoff 撰写、地图状态置 closed、Decisions 索引的 gist 并入 ADR 指针。

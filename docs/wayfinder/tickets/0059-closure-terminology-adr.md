id: "0059"
title: 收口：术语、导航与 ADR 耐久化
type: grilling
mode: HITL
status: closed
blocked_by: ["0056", "0057", "0058"]
assignee: agent
map: map-featured-fog-zones.md
created: 2026-10-23
claimed: 2026-10-23
closed: 2026-10-23
---

## Question

三面决策（0056 / 0057 / 0058）定案后，本图如何收口——**本题关闭 = 目的地到达（决策面）**。

要决策的面：

1. **ADR 形态**：决策集耐久化到哪——新开 ADR-0012（三条雾区是 ADR-0009 的延续但决策面独立：徽标契约 / 数据条口径 / 分类页消费），还是 ADR-0009 加指针行（其正文不改、指针行是先例）？判据：难逆决策才写 ADR（工程纪律 3）+ 决策必须活在 `docs/adr/`（ADR-0004 立过的规矩，AGENTS §8.1 阅读路由不含 wayfinder）。
2. **术语**：`CONTEXT.md`「精选 (Featured)」条是否扩写（内容层呈现 / 数据条 / 分类页消费的新语义）；要不要新增术语条（排图期不预设用词，此刻已有三面决议才可精确措辞）。
3. **导航**：`AGENTS.md` 坑点 11（文章精选纪律）是否补三条雾区的纪律；§7 速查表要不要加行（如徽标契约的定义处文件）。
4. **收口动作**：`docs/backlog.md` 第 13 项标记完成；写 handoff（`docs/handoffs/`）；本地图 `status: closed`；地图 Decisions so far 补齐三面 gist；雾区三条按既定方式处理（毕业为新工单 / 随 closed 地图挂起 / 消解——逐条定）。
5. **0058 转入动作**：`post-items.html` docstring 硬边界措辞收紧（「只服务首页精选链；其他页面消费 featured 须先过新决策」）——0058 决议二指定与本票③同批落地。

边界（不开票）：施工批次划分与 CI 验证节奏归项目负责人（本图只到可施工状态）；内容填充不随图。

## Resolution

2026-10-23 · grilling（HITL，项目负责人两问定案）+ 收口批执行：

**决议一（ADR 形态）**：**新开 ADR-0012**（`docs/adr/0012-featured-content-surfaces.md`，五组：语义边界 / 徽标三面 / 数据条负向 / 分类页负向 + seam 收紧 / meta 负向），**ADR-0009 加指针行**（三条雾区定案留痕，正文不改——历史记录纪律）。否掉：只加指针（正向架构决策在 §8.1 路由内无耐久 home）、改写 0009 正文（违反历史记录纪律）。

**决议二（术语扩写范围）**：CONTEXT.md「精选 (Featured)」条**只扩徽标面一句**（三面呈现 + `featured-badge.html` 契约定义处指针）；**负向边界不进术语表**——术语表承载概念与导航，决策记录归 ADR-0012 与 AGENTS 坑点 11。

**收口批执行清单（全部落地）**：ADR-0012 新写 + ADR-0009 指针行；CONTEXT.md 精选条扩写；AGENTS.md 坑点 11 补四条纪律（seam 只服务首页 / 坏值执法全局托管 / 徽标唯一实现处 / 数据条与 meta 两条负向）+ §7 速查表加 `featured-badge.html` 行；**0058 转入动作**——`post-items.html` docstring 硬边界收紧已落地；`docs/backlog.md` 第 13 项标记完成；handoff `docs/handoffs/2026-10-23-featured-fog-zones-closure.md`；本地图 `status: closed`；Decisions so far 补齐 0059/0060 gist；雾区三条处理完毕（0060 毕业并已决、另两条随负向消解，见地图注记）。

**验证**：`python3 tests/assert_site_contracts.py` **87/87 GREEN**（收口批含 post-items.html docstring 注释改动，零逻辑；套件头 Hugo 版本 WARN 为 0.167/0.164 skew 提醒，非失败）。

**本题关闭 = 地图 closed，frontier 空 = 目的地到达（决策面）。施工批（featured-badge.html partial + 三处调用 + fixture 三面断言 + 变异检验）待项目负责人指示后展开；视觉值归视觉层。**

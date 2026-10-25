---
id: "0064"
title: fixture 配置写入的统一面
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

fixture TOML 配置的写入在全仓手写了约六处：SOP 套件两处（fixture_config :218-236、assert_featured_passthrough :397-405，同型不同参）、站点套件四处（assert_bad_cases :1332-1335、assert_bad_caller_limit :1361-1363、assert_bad_caller_direct :1387-1388、assert_empty_state :1310-1311）。收敛为一个写入入口时，核心风险是它自身变成浅模块——为覆盖所有变体而把接口撑得和实现等宽。

要决策的面：

1. **变体轴心的识别**：六处写入实际变化的轴有哪些（dataDir / sopNotesDir / contentDir / refLinksErrorLevel / 空数据覆盖……）——先盘点再设计，轴心清单即参数面的上限。
2. **参数面的窄化判据**：入口收什么、每轴的消费方有几处（leverage：一个轴只有一处消费就不该进接口——留调用点）；「坏用例配置」与「行为 fixture 配置」是同一入口的两种调用还是两个入口；ADR-0006 决策 2「不留 source 注入位」的先例如何复用（不为臆想变体预留参数）。
3. **既有坑的内聚**：Windows 上 `relative_to` 产反斜杠嵌进 TOML 会被当转义序列（fixture_config 的 as_posix 处理与注释）、dataDir 下混入 .md 会 unmarshal 崩溃的约束——这些知识随入口内聚为一处文档，还是分散在各调用点。
4. **浅模块自查**：收敛后对入口做 deletion test——删掉它，复杂度是集中回六处（证明该收）还是 merely 搬家（证明设计错了）；接口宽度是否有可陈述的上限（如「参数不超过 N 个，超过即拆分」）。

边界（不开票）：配置写入的产物（tmp 下 .toml 文件）归 tmp 工单管；写入内容消费的构建旗标归构建工单。

事实前提：六处行号锚点见边界工单正文（同一盘点）；SOP 套件 fixture_config 的 docstring（:218-236 上方）记录了 dataDir/notes 隔离与 refLinksErrorLevel=WARNING 的理由，是「理由随实现走」的现成范例。

## Resolution

2026-10-25 · grilling（HITL，项目负责人三问定案；六票同场例外见地图 Notes）：

**轴心盘点（质询前的事实核查）**：六处手写写入的实际变化轴 = **dataDir / contentDir / sopNotesDir / refLinksErrorLevel 四轴**；SOP 两处是 root→{data,notes,content} 派生，站点四处是平铺路径；真实构建不走写入器（`REAL_CONFIG` 常量）——写入器消费者全是 fixture 构建。

**root 映射归属（Q1）**：**留 SOP 套件**。`root → root/data + root/notes` 是 SOP fixture 布局约定（套件知识）；harness 入口只收四个平铺轴——harness 不懂内容布局，与 0061「seam 后只有机制」一致；站点侧消费方不用 root 形态，入口不为一半消费方撑宽。

**入口形态（Q2）**：**一个入口、四轴、全显式无缺省**（ADR-0006 决策 2：不留缺省回落）。「坏用例配置 / 行为 fixture 配置」不是两种入口，是同四轴的不同取值——站点坏用例只设 dataDir 就是最小调用；`refLinksErrorLevel` 由 SOP 调用方显式给 WARNING（站点四处不设，即 Hugo 默认 ERROR 级）。

**宽度上限与坑内聚（Q3）**：宽度上限 = 四个 inventoried 轴；新轴须带新消费者并过 deletion test。两条既有坑随入口内聚为一处文档、全仓写入者共享：① 路径必须 `relative_to(REPO).as_posix()`（Windows 反斜杠嵌 TOML 会被当转义序列 → 假红）；② dataDir 只含数据文件，.md 混入即 unmarshal 崩溃（notes 平级隔离的原因）。入口落成后做 deletion test 自查：删掉它，复杂度应集中回六处（证明该收）而非搬家。

**对下游的输入**：入口随 0069 迁移批落地；SOP 的 `fixture_config` 退化为 root→四轴的适配器（保留其布局约定与坑注释的套件侧引用）。

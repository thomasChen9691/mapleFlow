id: "0064"
title: fixture 配置写入的统一面
type: grilling
mode: HITL
status: open
blocked_by: ["0062"]
map: map-test-harness-convergence.md
created: 2026-10-25
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

---
id: map-test-harness-convergence
title: 测试基建收敛图（harness 模块）
labels: [wayfinder:map]
status: closed
created: 2026-10-25
closed: 2026-10-25
---

# 测试基建收敛图（harness 模块）

## Destination

把测试基建从现状（四个套件各持一份 harness 副本）深化为**一个 harness 模块**：运行基建（Report / 构建入口 / fixture 配置写入 / jsdom 装配 / tmp 管理）收敛一处，契约字面量按三层文档契约保持独立；harness 自身**可测试、AI 可导航**。到「way 清晰、无待决策项」即收口；本图只产决策，施工经项目负责人指示后展开。

## Notes

- **出处**：架构评审候选①（improve-codebase-architecture，2026-10-25；报告在 OS 临时目录，属 epoch 性资产——关键行号锚点已抄写进各工单正文，不依赖该文件存活）。
- **工单纪律（项目负责人开图时明确）**：每张工单是**待决策问题**、不是施工任务；一次会话最多解决一张（research 除外）；地图是索引不是仓库，决策只存在于工单。
- **推送状态（2026-10-25，显著记录）**：本图全部施工与决议在本地分支 `refactor/harness-convergence` **全部未推、PR 未开**（GitHub auth-required；共 8 笔，以 `git log` 为准）：`6620eb0` chart → `42ba094` bad/ 拆子根 → `90a46e4` 两票决议 → `e08eb06` harness 模块 → `4adc239` 六票决议 → `cd531ea` 六票施工 → `e78930a` 0069/0071 决议 → 收口批（本提交）。收口不等 CI——分支规则集已把 verify 设为 PR 硬门禁，开 PR 时自然产生证据；恢复授权后推分支开 PR 即下一步（0071 决议）。基点的可视批 4 笔已在 `origin/style/css-modern-batch`（另一远程分支，未并 main）。
- **例外记录（2026-10-25）**：经项目负责人明确指示，0062 与 0065 同场 grill 并同场闭环；同日更进一步，0063 / 0064 / 0066 / 0067 / 0068 / 0070 六票同场 grill 并同场闭环；第三场，0069 与 0071 同场闭环（「一会话一票」纪律的三次例外，均由负责人指示）；各票 Resolution 均已记明。同场不降质：每票仍一次一问、推荐答案先行、事实自查后问决策。
- **入口不变是约束不是决策**：`npm test`、`python3 tests/assert_site_contracts.py`、`python3 tests/assert_sop_pipeline.py`、CI `.github/workflows/ci-cd.yml` verify job 的**调用方式**不因本图改变；harness 收敛的是套件内部，不是入口面。npm test 的**链内容**经 0066 决议扩展（assert_harness.mjs 先行）——命令面不变、链内容变，属已记录的显式变更。
- **闭卷 ADR**：0006（Considered Options 已枪毙「拆独立脚本」——fixture 基建复制即第二实现；本图是该原则的完成式：基建单份、套件多数）、0007（三层文档契约：CONTEXT.md 概念 / 引擎 docstring / 测试期望字面量**互相独立**——字面量重复是承重设计，不是本图合并对象）、0009（变异检验纪律：每条断言以「破坏实现→断言红→还原」证实有牙；迁移不得削掉牙）、0010（投影契约与测试期望独立字面量）、0013（parity 断言纪律：两处配置同改，防静默分叉）。
- **测试总原则**：Hugo 无模板单测，静态产物只能 build-then-assert；fixture 基建单份；fixture 日期一律过去日（未来内容不发布 → 假绿）；Hugo 0.164 语义编写（CI 钉版，0.166+ 条件多 return 本地过、CI 红）。
- **现成榜样**：`tests/sop_golden.py` 是项目中唯一做对的模块共享——capture 与 assert 都 import 它；harness 设计参照此例的反面教材成本（其余四处各写一份）。
- **术语**：「harness」是否进 CONTEXT.md 由 0067 裁决——已决：**不入**（术语表是对外领域语言；一词定型于 harness.py docstring 首段 + AGENTS.md §7 速查行）。
- 用户是项目负责人：HITL 工单必须实时对话解决，agent 不得自答；事实自己查，决策问用户；一次一问，先给推荐答案。
- 环境注意（历图传承）：本 shell 的 grep 对 `\|` 交替失效，内容搜索用 Grep 工具。

## Decisions so far

<!-- 本图 11 票已全部闭环（2026-10-25）。决策集耐久化于 ADR-0014
     （docs/adr/0014-test-harness-convergence.md）——十一条决策各注工单号；
     工单 Resolution 保留推理链。以下仅存题目索引，不重述决策。 -->

- [harness 边界：现存重复哪些判为基建、哪些判为契约](tickets/0061-harness-boundary-infra-vs-contract.md) → ADR-0014 决策 1 / 5
- [harness 模块形态：Python 侧与 Node 侧各是什么、落在哪](tickets/0062-harness-module-shape.md) → ADR-0014 决策 2 / 3
- [构建入口的旗标分歧归谁](tickets/0063-build-flags-divergence-ownership.md) → ADR-0014 决策 6
- [fixture 配置写入的统一面](tickets/0064-fixture-config-writer-interface.md) → ADR-0014 决策 7
- [共享 tmp 的所有权：分根还是共用](tickets/0065-tmp-ownership-structure.md) → ADR-0014 决策 4
- [harness 自身如何被测试](tickets/0066-harness-self-testability.md) → ADR-0014 决策 8
- [harness 的文档 seam 与导航入口](tickets/0067-harness-doc-seam-navigation.md) → ADR-0014 决策 9
- [版本预检是否进 harness](tickets/0068-version-preflight-ownership.md) → ADR-0014 决策 10
- [golden seam 与 harness 的关系](tickets/0070-golden-seam-relation.md) → ADR-0014 决策 11
- [迁移顺序与风险](tickets/0069-migration-order-risk.md) → ADR-0014 Consequences（迁移记录）
- [收口：harness 收敛的耐久化与地图关闭](tickets/0071-closure-terminology-adr.md) → 本图关闭（收口三产出：ADR-0014 + handoff + 本地图 closed）

## Not yet specified

<!-- 雾区：在目的地内、但还无法精确表述的问题。随 frontier 推进毕业为工单。 -->

- **已消解**（[0061](tickets/0061-harness-boundary-infra-vs-contract.md) 决议）：「跨套件契约执法点的归属」——BAD_CASE_EXPECT 判契约（各套件独立，循环因两侧真实差异留各套件）、fuse pair 判互补维持现状（源对源比对与硬编码字面量覆盖不同漂移方向），均无 harness 可收部分。
- **已消解（负向）**（[0065](tickets/0065-tmp-ownership-structure.md) 决议）：「并行执行的代价面」——并行定为目标 = **否**（分根结构已备好、CI 暂不并行；无真实时长需求）。若将来并行成为目标，本雾区复活并连同 CI 改造一并评估。
- **已消解（负向）**（[0069](tickets/0069-migration-order-risk.md) 决议）：「既有断言随 harness 落地的重组粒度」——实测答案：**无重组**。断言原样搬家、期望字面量独立不动、计数三批持平（site 159 · sop 104 · npm 23+41）、变异等价逐批证实；不存在「哪些动哪些不动」的选择面。

## Out of scope

- **架构评审候选⑤的其余死面**（hugo.toml socialIcons 死配置 / list.html IsHome 死分支 / 四条无产出方 CSS）：属另一候选的目的地；本图只处理测试基建内的死面（CI_WORKFLOW 失效指针归版本预检工单裁决）。
- **架构评审候选②③④⑥**（featured 类型守卫 / 文章卡片单模块 / 注册缝下沉 / CSS 影子契约 parity）：各自独立目的地，不随本图合并或顺带。
- **契约语义本身**（精选词表、SOP 管线五类契约、投影六字段、fuse 参数值、各 errorf 消息前缀）：本图只动承载它们的基建，不改契约；改契约是新目的地。
- **CI 流水线结构**（verify/deploy 双 job、分支规则集、门禁清单）：入口调用方式不变即足；重划 CI 是新需求。
- **引擎与模板行为**（mf-reveal / mf-search-* / fastsearch / Hugo 模板的任何改动）：非测试基建。
- **施工批次与 CI 验证节奏**：本图只到「way 清晰」，施工经项目负责人指示后展开（候选 7/12/13 先例）。

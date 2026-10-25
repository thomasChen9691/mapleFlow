---
id: map-test-harness-convergence
title: 测试基建收敛图（harness 模块）
labels: [wayfinder:map]
status: open
created: 2026-10-25
---

# 测试基建收敛图（harness 模块）

## Destination

把测试基建从现状（四个套件各持一份 harness 副本）深化为**一个 harness 模块**：运行基建（Report / 构建入口 / fixture 配置写入 / jsdom 装配 / tmp 管理）收敛一处，契约字面量按三层文档契约保持独立；harness 自身**可测试、AI 可导航**。到「way 清晰、无待决策项」即收口；本图只产决策，施工经项目负责人指示后展开。

## Notes

- **出处**：架构评审候选①（improve-codebase-architecture，2026-10-25；报告在 OS 临时目录，属 epoch 性资产——关键行号锚点已抄写进各工单正文，不依赖该文件存活）。
- **工单纪律（项目负责人开图时明确）**：每张工单是**待决策问题**、不是施工任务；一次会话最多解决一张（research 除外）；地图是索引不是仓库，决策只存在于工单。
- **入口不变是约束不是决策**：`npm test`（assert_reveal.mjs + assert_search.mjs）、`python3 tests/assert_site_contracts.py`、`python3 tests/assert_sop_pipeline.py`、CI `.github/workflows/ci-cd.yml` verify job 的调用方式不因本图改变；harness 收敛的是套件内部，不是入口面。
- **闭卷 ADR**：0006（Considered Options 已枪毙「拆独立脚本」——fixture 基建复制即第二实现；本图是该原则的完成式：基建单份、套件多数）、0007（三层文档契约：CONTEXT.md 概念 / 引擎 docstring / 测试期望字面量**互相独立**——字面量重复是承重设计，不是本图合并对象）、0009（变异检验纪律：每条断言以「破坏实现→断言红→还原」证实有牙；迁移不得削掉牙）、0010（投影契约与测试期望独立字面量）、0013（parity 断言纪律：两处配置同改，防静默分叉）。
- **测试总原则**：Hugo 无模板单测，静态产物只能 build-then-assert；fixture 基建单份；fixture 日期一律过去日（未来内容不发布 → 假绿）；Hugo 0.164 语义编写（CI 钉版，0.166+ 条件多 return 本地过、CI 红）。
- **现成榜样**：`tests/sop_golden.py` 是项目中唯一做对的模块共享——capture 与 assert 都 import 它；harness 设计参照此例的反面教材成本（其余四处各写一份）。
- **术语**：「harness」是否进 CONTEXT.md、由谁定名，归导航工单裁决，排图期不预设用词。
- 用户是项目负责人：HITL 工单必须实时对话解决，agent 不得自答；事实自己查，决策问用户；一次一问，先给推荐答案。
- 环境注意（历图传承）：本 shell 的 grep 对 `\|` 交替失效，内容搜索用 Grep 工具。

## Decisions so far

<!-- 索引：每个已决工单一行 gist + 链接；决策详情只存在于工单，此处不重述。 -->

- [harness 边界：现存重复哪些判为基建、哪些判为契约](tickets/0061-harness-boundary-infra-vs-contract.md) — 判据 = **所有权测试**（唯一所有者→基建；各有其主→契约），平分 tiebreak 判契约（合并意义制造隐形跨套件耦合、代价无界无报警；重复机制有界可见）；「必须同改」标准废除。六类裁定：BAD_CASE_EXPECT 表与循环→契约留各套件（两侧循环有真实差异：默认回落 vs 完整性自检）；fuse 双执法→互补 pair 维持现状（Python 源对源零硬编码 + mjs 字面量，覆盖不同漂移方向，ADR-0013 决策 5 本体）；fixture 镜像→基建侧留原地（事实核查消灭「跨套件借用」前提——站点套件自持 dataDir，harness 不收数据文件）；bad/ 共享坏用例→契约，**拆子根 bad/products/ + bad/sop/ + 每根本根卫生断言**（所有权从约定变为结构，与 tmp 分根同款哲学）；sop-golden→契约归 SOP 套件（工具关系归 0070）。seam 禁止项：harness 之后只有机制、零契约知识；现存断言全存活，净新增仅本根卫生一类；三条下游约束（禁字面量 / 拆子根与断言同批 / 测试不减每条有牙）移交 0062·0066·0069。产物存 Resolution，判据耐久化建议归 0067。frontier = 0062 + 0065。

## Not yet specified

<!-- 雾区：在目的地内、但还无法精确表述的问题。随 frontier 推进毕业为工单。 -->

- **已消解**（[0061](tickets/0061-harness-boundary-infra-vs-contract.md) 决议）：「跨套件契约执法点的归属」——BAD_CASE_EXPECT 判契约（各套件独立，循环因两侧真实差异留各套件）、fuse pair 判互补维持现状（源对源比对与硬编码字面量覆盖不同漂移方向），均无 harness 可收部分。
- **既有断言随 harness 落地的重组粒度**：横切迁移时哪些断言随基建移动、哪些原样不动、移动后期望字面量与 fixture 的对应关系如何维持——取决于迁移顺序工单选定的迁移策略。
- **并行执行的代价面**：若 tmp 所有权工单把「并行」定为目标，CI 时长收益、runner 资源与失败可读性的变化需重新评估——取决于该工单决议。

## Out of scope

- **架构评审候选⑤的其余死面**（hugo.toml socialIcons 死配置 / list.html IsHome 死分支 / 四条无产出方 CSS）：属另一候选的目的地；本图只处理测试基建内的死面（CI_WORKFLOW 失效指针归版本预检工单裁决）。
- **架构评审候选②③④⑥**（featured 类型守卫 / 文章卡片单模块 / 注册缝下沉 / CSS 影子契约 parity）：各自独立目的地，不随本图合并或顺带。
- **契约语义本身**（精选词表、SOP 管线五类契约、投影六字段、fuse 参数值、各 errorf 消息前缀）：本图只动承载它们的基建，不改契约；改契约是新目的地。
- **CI 流水线结构**（verify/deploy 双 job、分支规则集、门禁清单）：入口调用方式不变即足；重划 CI 是新需求。
- **引擎与模板行为**（mf-reveal / mf-search-* / fastsearch / Hugo 模板的任何改动）：非测试基建。
- **施工批次与 CI 验证节奏**：本图只到「way 清晰」，施工经项目负责人指示后展开（候选 7/12/13 先例）。

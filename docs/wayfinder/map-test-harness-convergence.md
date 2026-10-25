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
- **例外记录（2026-10-25）**：经项目负责人明确指示，0062 与 0065 同场 grill 并同场闭环；同日更进一步，0063 / 0064 / 0066 / 0067 / 0068 / 0070 六票同场 grill 并同场闭环（「一会话一票」纪律的两次例外，均由负责人指示）；各票 Resolution 均已记明。同场不降质：每票仍一次一问、推荐答案先行、事实自查后问决策。
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
- [harness 模块形态：Python 侧与 Node 侧各是什么、落在哪](tickets/0062-harness-module-shape.md) — 「一个 harness 模块」作为**概念**覆盖语言强制的两个文件：**tests/harness.py**（Report + 打印/汇总/退出码 + hugo 检查 + tmp 重置 + build + 配置写入）+ **tests/dom.mjs**（check + 计数/汇总 + installDom/loadFresh），按职责命名；同干命名与 Node 不立模块均拒。**入口只剩「参数 + 有序断言清单」**——入口仪式（含两套件逐字重复的打印块，第三处副本）全进 harness，排序注释留调用点；声明式注册表拒（seam 变配置）。纳入双门槛：≥2 消费者 + deletion test，无预期消费者不留（ADR-0006 决策 2）；预检（0068）/golden 工具链（0070，sop_golden.build_real 是内容语义）/字面量/fixture 数据明确在外。seam 五承诺（构建/报告/配置/DOM/tmp 根）三禁止（词表/期望值/fixture 数据）；「harness」词范围 = 测试运行基建，sop_golden 并列第三模块且 docstring 须提其存在；现存断言全存活。
- [共享 tmp 的所有权：分根还是共用](tickets/0065-tmp-ownership-structure.md) — **按套件分根** tmp/site/ + tmp/sop/ + tmp/capture/（capture 从约定升级为真所有权）——与 bad/ 拆子根同款「所有权从约定变为结构」，串行约束自然消解；共用+锁与维持文档约束均拒。**并行定为目标 = 否**（分根备好、CI 暂不并行，意图入雾区）。**dest 由 harness 统一生成**（套件传用途名，拼 tmp/<suite>/<purpose>；「real」魔法字符串消失）。残留清点：__pycache__ 与 resources/_gen 记录在案不加锁（缓存语义 / 跟着模块文件走）；SOP :36-37 串行文档随施工废除。
- [构建入口的旗标分歧归谁](tickets/0063-build-flags-divergence-ownership.md) — **命名档位 + 显式 extras**：harness.build(config, dest, profile, flags)。site-contracts 档 = --cleanDestinationDir（无 minify，断言解析带引号属性）；sop-pipeline 档 = --gc --minify --cleanDestinationDir（与 CI 生产命令逐字一致，golden 按 minify 产物捕获）；drafts 糖拆成 flags=["-D"]。档位 docstring 必须载旗标理由；新档位过 0062 双门槛；站点 real 构建「生产配置、故意不 minify、minify 归 CI 零 WARN 守门」的不对称在 site 档显式声明。
- [fixture 配置写入的统一面](tickets/0064-fixture-config-writer-interface.md) — 六处写入实测四轴（dataDir / contentDir / sopNotesDir / refLinksErrorLevel）。**一个入口、四轴、全显式无缺省**（ADR-0006 决策 2）；坏用例与行为 fixture 是同四轴的不同取值（坏用例 = 只设 dataDir 的最小调用）。**root→data/notes 映射留 SOP 套件**（fixture 布局约定是套件知识，harness 不懂内容布局）。宽度上限 = 四轴，新轴带新消费者 + deletion test；as_posix 与 dataDir 禁 .md 两坑随入口内聚为一处文档。
- [harness 自身如何被测试](tickets/0066-harness-self-testability.md) — **只测牙临界行为**（check 的 verdict 记录 / finish 退出码 / dest 拼装 / reset_tmp 隔离）；间接覆盖判据 = 破坏时现有套件是否可定位地红（check 不达标已实证：if(true) 静默假绿）。**独立双文件** tests/assert_harness.{py,mjs}；npm test 扩链 + CI verify 加一步。自测断言行为、期望值独立字面量、不重算 harness 逻辑、每条变异证牙；自测文件禁存被测模块契约字面量。
- [harness 的文档 seam 与导航入口](tickets/0067-harness-doc-seam-navigation.md) — **批准现行两份文件头 docstring 为契约唯一定义处**（ADR-0007 三层模式的 harness 侧落地）。**「harness」不入 CONTEXT.md**（术语表对外；定型于 harness.py docstring 首段 + AGENTS.md §7）。AGENTS.md 三处**随施工批同步落地**：§7 两行（两模块）+ §3 随 0066 自测同步 + §4 坑点补一条（坏用例子根 / tmp 分根 / 无串行约束）；收口记录未落地项防丢。
- [版本预检是否进 harness](tickets/0068-version-preflight-ownership.md) — **修：workflow 发现改 glob，预检复活**（CI_WORKFLOW 钉已改名的 deploy.yml → 静默失效，已死；照 assert_ci_wiring glob 先例）。**留站点套件**（SOP 断言与 Hugo 版本无关，WARN 对它无信息量；harness 收它违双门槛）。**维持 advisory WARN**（skew ≠ 产物错，硬失败误伤新版 hugo 用户）。
- [golden seam 与 harness 的关系](tickets/0070-golden-seam-relation.md) — **追认并列三模块**（harness.py / dom.mjs / sop_golden.py）；接缝 = docstring 互指 + capture 只走 tmp_root；build_real 留 sop_golden（生产配置直捕是内容工具关注点）。**--check 不接 CI**：覆盖与 SOP 套件 golden 比对重叠、独特覆盖对共享模块 bug 双盲，记录为已知限制（ADR-0010 先例）。三票一致闭环；sop_golden docstring 补对称互防一行。

## Not yet specified

<!-- 雾区：在目的地内、但还无法精确表述的问题。随 frontier 推进毕业为工单。 -->

- **已消解**（[0061](tickets/0061-harness-boundary-infra-vs-contract.md) 决议）：「跨套件契约执法点的归属」——BAD_CASE_EXPECT 判契约（各套件独立，循环因两侧真实差异留各套件）、fuse pair 判互补维持现状（源对源比对与硬编码字面量覆盖不同漂移方向），均无 harness 可收部分。
- **已消解（负向）**（[0065](tickets/0065-tmp-ownership-structure.md) 决议）：「并行执行的代价面」——并行定为目标 = **否**（分根结构已备好、CI 暂不并行；无真实时长需求）。若将来并行成为目标，本雾区复活并连同 CI 改造一并评估。
- **既有断言随 harness 落地的重组粒度**：横切迁移时哪些断言随基建移动、哪些原样不动、移动后期望字面量与 fixture 的对应关系如何维持——取决于迁移顺序工单选定的迁移策略。

## Out of scope

- **架构评审候选⑤的其余死面**（hugo.toml socialIcons 死配置 / list.html IsHome 死分支 / 四条无产出方 CSS）：属另一候选的目的地；本图只处理测试基建内的死面（CI_WORKFLOW 失效指针归版本预检工单裁决）。
- **架构评审候选②③④⑥**（featured 类型守卫 / 文章卡片单模块 / 注册缝下沉 / CSS 影子契约 parity）：各自独立目的地，不随本图合并或顺带。
- **契约语义本身**（精选词表、SOP 管线五类契约、投影六字段、fuse 参数值、各 errorf 消息前缀）：本图只动承载它们的基建，不改契约；改契约是新目的地。
- **CI 流水线结构**（verify/deploy 双 job、分支规则集、门禁清单）：入口调用方式不变即足；重划 CI 是新需求。
- **引擎与模板行为**（mf-reveal / mf-search-* / fastsearch / Hugo 模板的任何改动）：非测试基建。
- **施工批次与 CI 验证节奏**：本图只到「way 清晰」，施工经项目负责人指示后展开（候选 7/12/13 先例）。

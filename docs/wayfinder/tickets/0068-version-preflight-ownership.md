id: "0068"
title: 版本预检是否进 harness
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

`preflight_hugo_version`（assert_site_contracts.py:81-106，约 25 行）是本机 Hugo 版本与 CI 钉版（0.164）skew 的 advisory 检查——零断言效果、一个调用点，且它引用的 `CI_WORKFLOW`（:75）指向已改名的 `deploy.yml`（现为 `ci-cd.yml`），file 读取走 OSError 分支静默跳过，整个预检实际已死。它是测试基建内的死面，归本图裁决（候选⑤的其余死面 out of scope）。

要决策的面：

1. **接管、修正还是留撤**：harness 接管预检并修正 workflow 发现（SOP 套件 :457 已有 glob workflows 的先例，照做即活）；还是判定预检价值不足、撤掉（版本 skew 的牙由 CI 本身提供——CI 用钉版跑，本地 skew 只影响「本地过、CI 红」的可预期性）；留待候选⑤随死面批处理是否可接受（注意：它在测试基建内，与本图目的地相邻）。
2. **效果定位**：若保留——advisory WARN（现状定位：只提示不失败）还是升级为硬失败（本地 hugo 版本 ≠ CI 钉版即红）；硬失败的误伤面（开发者用新版 hugo 本地跑测试被挡）与 advisory 的无效面（WARN 无人看）。判据：这个检查真正防的事故是什么（CI 红而非本地绿？还是 0.166+ 语义差异导致的行为分叉）。
3. **与 0.164 语义纪律的关系**：项目已有「Hugo 0.164 语义编写（CI 钉版）」的纪律注记（历图 Notes 传承）——预检是这条纪律的执行机制还是重复表达；若预检撤掉，纪律注记是否需要在别处有牙。
4. **harness 化的代价**：预检进 harness 后，它的输入（workflow 文件位置、版本号来源）成为 harness 的依赖——workflow 改名再次发生时，harness 的 glob 发现是否足够健壮；这是否又是「为小功能撑宽接口」的案例（对照形态工单的浅模块判据）。

边界（不开票）：候选⑤其余死面（socialIcons / IsHome 分支 / 死 CSS）不随本票；CI 流水线本身的结构不动。

事实前提：`assert_site_contracts.py:75`（CI_WORKFLOW 常量指向 deploy.yml）、:81-106（preflight_hugo_version 全文）、:90-91（OSError 静默分支）；`assert_sop_pipeline.py:457`（glob workflows 先例）；架构评审候选①与候选⑤对该点的记录。

## Resolution

2026-10-25 · grilling（HITL，项目负责人三问定案；六票同场例外见地图 Notes）：

**修撤留（Q1）**：**修——workflow 发现改 glob，预检复活**。事实底座：`CI_WORKFLOW` 常量指向已改名的 `deploy.yml`（现为 `ci-cd.yml`），read_text 走 OSError 分支静默返回——预检**已死**。修法照 `assert_sop_pipeline.py` 的 `assert_ci_wiring` 先例（glob 全部工作流；钉文件名曾是隐性耦合：流水线改名就红且红因与 SOP 无关）。不撤（失去「提交前提醒 0.166+ 写法陷阱」的软牙——ADR-0004 的本地过 CI 红正是它防的）；不推候选⑤（它在测试基建内，与候选⑤其余死面不同域、不同动作）。

**落点（Q2）**：**留站点套件**（main 里 harness.run 之前的现状位置），只修 glob——SOP 套件断言只消费构建产物、与 Hugo 版本无关（其头部自证），WARN 对它无信息量；harness 收它等于给零信息量消费方加宽接口，违 0062 双门槛。拒绝：进 harness 全套件、进 harness 加按套件开关（预留病）。

**效果（Q3）**：**维持 advisory WARN**（不进断言计数、不影响退出码）——ADR-0004 原逻辑：skew 不等于产物错，断言仍有效、只是证明不了 CI 会绿；硬失败误伤用新版 hugo 的开发者，且挡不住真正的问题（CI 自己用钉版跑）。

**施工形态**：`CI_WORKFLOW` 常量删除，改 glob `.github/workflows/*.yml` 抽 `hugo-version`；docstring 的「钉版真源」表述随改。

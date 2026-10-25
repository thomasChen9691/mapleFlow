---
id: "0070"
title: golden seam 与 harness 的关系
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

`sop_golden.py` 是全仓唯一做对的模块共享：capture（capture_sop_golden.py）与 assert（assert_sop_pipeline.py）都 import 它，verify/regenerate 分离有文档、有 `--check` 只读 staleness 检测。harness 落地后，这个现成榜样与 harness 是什么关系——它算 harness 的一部分（测试基建），还是独立的内容 fixture 工具链（与 harness 并列的第二个共享模块）。

要决策的面：

1. **归类**：golden 的抽取 / 规范化 / 比对，与 harness 的 Report / 构建 / 配置写入，是同一关注点（「让测试可跑」）还是两个（「跑测试」vs「内容样本的正确性」）——判据：golden 的消费者是否只有测试套件（若是，它与 harness 同命运）；它变化的原因（SOP 正文变换规则变）与 harness 变化的原因（测试运行方式变）是否同源。
2. **若并列，接缝在哪**：harness 不吸收 sop_golden.py——两者之间的调用关系（assert_sop_pipeline.py 同时 import 两者？）；命名与落点上如何让读者一眼看出「两个共享模块、职责不同」；harness docstring 是否提及 golden 的存在（防未来的合并冲动）。
3. **--check 未接 CI 的现状**：capture_sop_golden.py --check 目前不在 CI 门禁里（golden 漂移只被管线比对顺带抓）——这个缺口是否随本图补（harness 化后接入成本变化？），还是显式记录为已知限制留待（对照 ADR-0010「已知限制记录在案、不承诺修复」的先例）。
4. **对边界工单的反馈**：若本票判定 golden 属契约侧（内容样本）而非基建侧——边界工单的灰色地带第四类（golden 文件与 capture/assert 分工）随之定案；两票结论必须一致，若冲突回边界工单重裁。

边界（不开票）：golden 文件内容本身的更新（SOP 正文变换规则演化）不是本图的事；本票只决 golden 工具链与 harness 的结构关系。

事实前提：`tests/sop_golden.py`（144 行，共享核心）、`tests/capture_sop_golden.py`（81 行，写侧）、`tests/fixtures/sop-golden/README.md`（verify/regenerate 分离的文档）；架构评审候选①对该 seam 的评价（「全仓唯一做对的模块共享」）。

## Resolution

2026-10-25 · grilling（HITL，项目负责人三问定案；六票同场例外见地图 Notes）：

**结构关系（Q1）**：**追认并列三模块**——harness.py / dom.mjs（测试运行基建，一个概念两个文件）+ sop_golden.py（内容 fixture 工具：golden 抽取 / 规范化 / 生产构建捕获）。接缝 = docstring 互指 + capture 只走 `tmp_root` 不碰 harness 其余能力。`build_real` 留 sop_golden：生产配置直捕是内容工具的关注点，harness 的 build 归 0063 档位（两种构建风味各有其主，拆半只会制造两个构建入口）。吸收进 harness 拒（0061 裁定五的前提就是并列；且 harness 收内容抽取逻辑即懂内容语义，违 seam 三禁止）。

**--check 接 CI（Q2）**：**不接，记录为已知限制**（ADR-0010 先例）。覆盖分析：golden 漂移已被 SOP 套件的 golden 比对从管线侧覆盖（真实注册表 + 源笔记的构建产物 vs golden，内容变了套件即红）；--check 的独特只剩「捕获路径自身」，而它与 assert 共用同一个 sop_golden.py——同模块的 bug 两边同盲。接 CI 是第三份执法 + 一次全量生产构建的耗时，收益近零。撤 --check 拒：它与 regenerate 是 README 载明的一体两面，是人工维护 golden 时的只读探针。

**一致性闭环（Q3）**：三票结论一致无需回 0061 重裁——0061 判「golden 文件归契约侧（SOP 套件）」、0062 判「并列第三模块 + harness docstring 互防」、本票判「并列追认 + CI 不接」，层面各不相同。**补对称互防一行**：sop_golden.py docstring 加指向 harness 的互指（harness→sop_golden 的方向已在施工批落地）。

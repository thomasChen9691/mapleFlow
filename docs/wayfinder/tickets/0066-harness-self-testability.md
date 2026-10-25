id: "0066"
title: harness 自身如何被测试
type: grilling
mode: HITL
status: open
blocked_by: ["0062"]
map: map-test-harness-convergence.md
created: 2026-10-25
---

## Question

Destination 要求 harness 模块**可测试**。现状里 harness 的各个副本恰恰是不可测的：Report 的汇总逻辑、build 的旗标拼接、TOML 写入的产物，全部只在「套件整体跑绿」里被间接证明——它们坏了，表现是某个契约断言诡异地红，定位要穿越整个套件。本票定 harness 自身被测试的形态。

要决策的面：

1. **测什么**：harness 行为的清单与优先级——Report（check 记录 / failed 判定 / 汇总输出）、构建入口（命令拼接、旗标档位、失败传播）、配置写入（产物 TOML 的内容与路径）、tmp 管理（分根 / 清场）；哪些行为值得直接断言，哪些继续由「套件跑绿」间接覆盖足够（间接覆盖的判据：坏了是否会被现有断言以可定位的方式抓到）。
2. **自测套件的形态与入口**：独立脚本（如 `tests/assert_harness.py` / `.mjs`）还是并入既有套件的引导段；入口是否进 `npm test` 与 CI verify job——进门的代价（CI 时长）与收益（harness 坏了在契约断言之前先红，失败定位前移）。
3. **「谁测试测试者」的边界**：自测断言与被测 harness 的关系——自测的期望值是否构成「第二实现」（ADR-0004 枪毙过的模式：独立契约检查器是第二实现必然漂移）；用真实小 fixture 跑端到端 vs 单元式断言各覆盖什么；变异检验纪律（ADR-0009）是否适用于 harness 自测（每条自测也以「破坏 harness→红→还原」证实有牙）。
4. **与文档 seam 的关系**：harness 契约定义处（docstring）与自测期望字面量的关系——自测字面量是否算三层契约的第三层（若是，它独立于 harness 实现即是承重设计，不是重复）。

边界（不开票）：harness 的模块形态归形态工单（本票以其决议为输入）；具体测试内容随形态定，本票只定「测不测、测什么形态、入口在哪、边界何在」。

事实前提：架构评审候选①（harness 副本全部未经直接测试的现状）；sop_golden.py 先例（共享模块被两个消费方间接覆盖——这是「间接覆盖足够」的现存论点，需评估是否适用于 harness 全部行为）。

---
id: 0013
title: SOP 管线的测试缝形状
type: grilling
mode: HITL
status: open
blocked_by: [0012]
assignee:
map: map-sop-source-sync
---

## Question

管线落地后，断言什么、放哪、CI 怎么跑？

候选（可组合）：

- 每条源笔记都有对应渲染产物（防漏生成）；
- 渲染正文与源笔记归一化后相等（防漂移——这是「零同步」痛点的守门转化）；
- 无孤儿文章（有产物无真源，或反向）；
- 日期非零值回归（工单 0007 的 `dates` 陷阱：照抄文档示例会静默全零）；
- `--printPathWarnings` 守门（adapter 页与残留 .md 撞路径）；
- 双构建（fixture + 真实数据）是否必要——参照 ADR-0004「fixture 双构建覆盖全部分支 + 真实数据守线上回归」的既有范式是否需要照搬。

决策依据：ADR-0004 的测试哲学——契约执法在模块内（`errorf`，构建即门禁）+ 存活测试只以构建产物断言；Hugo 生态无模板单测（工单 0001 已证），一切断言只能是 build-then-assert；CI 权威 + 本地 advisory 的运行策略是否沿用。

## 预裁记录（工单 0008/0009 质询，2026-10-15）

测试集已裁（0008 决议第 4 条 + 0009 决议连带裁定）：构建期契约 4 类（死条目 / 无 H1 / 缺 date / 缺 slug）+ 产物断言 6 条（6 篇存在[URL 冻结回归]、标题==H1、日期非零、正文归一化比对、ref 解析、6 slug 无手写残留）+ README↔注册表双向一致 + fixture 双构建。进入 frontier 后只剩正式落档：脚本命名（`tests/assert_sop_pipeline.py`）、fixture 站点组织（临时目录 + dataDir 覆盖，对 ADR-0001 只做加法）、CI 断言步插入点。

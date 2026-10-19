---
id: 0016
title: 筛选词汇来源：写死还是数据派生
type: grilling
mode: HITL
status: open
blocked_by: []
assignee:
map: map-product-index-narrowing.md
---

## Question

kind 与 price 两组筛选值（筛选按钮 + 行上 `data-kind` / `data-price` 属性）继续写死三种交付形态 + 免费/付费，还是改为从条目数据派生（按数据中出现的 kind 去重生成按钮）？

背景（事实，已核）：按钮当前硬编码 workflow / document / question-bank 三枚 + 价格组免费/付费两枚；`data-price` 已由产品状态模块的 `dataPrice` 供给（ADR-0004），kind 侧仍是模板写死。工单 0005 曾评估「未知交付形态不纳入产品状态契约」（kind 是事实而非状态派生项），并将筛选词汇问题划归本图。需定：派生时出现数据中没有的 kind、或 kind 集合变化时，按钮与契约如何行为；以及词汇是否属于 CONTEXT.md「交付形态」术语条的执行区。

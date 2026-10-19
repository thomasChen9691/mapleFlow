---
id: 0016
title: 筛选词汇来源：写死还是数据派生
type: grilling
mode: HITL
status: closed
blocked_by: []
assignee: agent
map: map-product-index-narrowing.md
claimed: 2026-10-19
closed: 2026-10-19
---

## Question

kind 与 price 两组筛选值（筛选按钮 + 行上 `data-kind` / `data-price` 属性）继续写死三种交付形态 + 免费/付费，还是改为从条目数据派生（按数据中出现的 kind 去重生成按钮）？

背景（事实，已核）：按钮当前硬编码 workflow / document / question-bank 三枚 + 价格组免费/付费两枚；`data-price` 已由产品状态模块的 `dataPrice` 供给（ADR-0004），kind 侧仍是模板写死。工单 0005 曾评估「未知交付形态不纳入产品状态契约」（kind 是事实而非状态派生项），并将筛选词汇问题划归本图。需定：派生时出现数据中没有的 kind、或 kind 集合变化时，按钮与契约如何行为；以及词汇是否属于 CONTEXT.md「交付形态」术语条的执行区。

## Resolution

2026-10-19 · grilling（用户为决策者），两问落定：

1. **kind 词汇 = 契约化写死**：按钮维持写死 workflow / document / question-bank 三枚——即 CONTEXT.md「交付形态」封闭词表的执行区；新增数据契约：`data/products.yaml` 出现词表外 kind 即 `errorf` 构建失败。排除「按数据派生」（词表失控：加形态 = 改数据即改导航 UI，无审批点）与「维持现状」（未知 kind 静默穿透：data-kind 写异常值、无按钮可筛、仍计入总数——0005 划归本图的缺口就此补上）。
2. **契约落点 = product-items 数据门禁**（0015 新设的数据准备 seam）：prepare 遍历 items 时逐条校验 kind ∈ 三值封闭集；消息前缀与产品状态模块的「产品状态：」并列，定为「产品索引数据：」，内容含产品 id 与坏值（测试断言的子串锚）。产品状态模块不碰——0005 裁决（kind 是事实非状态派生、不进状态契约）不变，升级的只是「不检查」→「在渲染链数据入口检查」。

**下游影响**：0017（uid 契约）与 0019（测试缝）解锁；0019 的坏用例集须新增「未知 kind」一格（施工期事项，不新开工单）。CONTEXT.md「交付形态」术语条是否补注「封闭集 + 构建期执法」留给 0020 导航契约一并在收口时处理。


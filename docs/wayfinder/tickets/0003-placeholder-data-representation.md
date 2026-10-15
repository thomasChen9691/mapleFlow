---
id: 0003
title: 占位例外的数据表示
type: grilling
mode: HITL
status: open
blocked_by: []
assignee: agent
map: map-product-state-convergence
claimed: 2026-10-15
---

## Question

「占位链接（测试商品页）不计入可下载产品」这条 `CONTEXT.md` 规则，如何获得数据表示？候选：

- (a) `products.yaml` 增加显式上架状态字段 —— 人写、可信，但依赖填写纪律；
- (b) 由 `buy_url` 形态推导（如 `mbd.pub/o/test-` 前缀）—— 零填写成本，但是启发式，可能被真实链接误伤或漏判；
- (c) 占位条目移出主数据文件（独立 fixture，默认不计入）。

附带决策：免费判定（`price = 0` 或缺省）是否同案统一表示。

注意：项目负责人已裁定当前 5 条均为开发中占位、不提供真实下载链接 —— 本工单决定的是**表示形式**，不是是否清空。

---
id: 0005
title: 测试缝的形状
type: grilling
mode: HITL
status: open
blocked_by: [0002, 0003]
assignee:
map: map-product-state-convergence
---

## Question

深化后的产品状态模块，测试断言什么？候选（可组合）：

- (a) 派生规则单测 —— fixture yaml → 期望状态表；
- (b) 构建产物断言 —— `hugo` 构建后解析 `public/products.html`，核对按钮态与首页数字；
- (c) 数据契约检查 —— `products.yaml` 每条状态字段合法、无未知交付形态、占位标记不冲突。

决策依据：工单 0002 的 seam 形状决定测试能穿过哪条缝；「接口即测试面」—— 测试必须与调用方走同一道缝，不得为可测性另造入口。

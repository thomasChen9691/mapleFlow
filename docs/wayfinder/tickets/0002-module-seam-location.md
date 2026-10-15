---
id: 0002
title: 产品状态模块的驻留位置
type: grilling
mode: HITL
status: open
blocked_by: [0001]
assignee:
map: map-product-state-convergence
---

## Question

产品状态推导（已上架 / 即将上架 / 免费 / 可下载产品，含占位例外）应驻留在哪？候选形态：

- (a) 单一 template partial 单源 + 构建产物级测试；
- (b) 构建期派生脚本（Python / Node）读 `products.yaml` 产出派生数据 + 单测；
- (c) 混合：partial 单源 + 独立校验脚本。

决策依据：工单 0001 的事实、ADR-0001 固定构建命令约束、本地 dev 与 CI 双流程成本、「接口即测试面」原则。

本工单同时划定模块职责边界：模块是只拥有状态判定，还是连同 CTA 文案 / 价格展示映射一起拥有。

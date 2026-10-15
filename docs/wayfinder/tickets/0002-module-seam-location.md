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

## 背景约束（来自工单 0001 决议，2026-10-15）

- Hugo 无模板单测机制，测试只能「build 后对产物断言」—— seam 形状直接决定测试能否单点覆盖。
- return 型 partial 在 0.164 限「单变量 + 根级单条 return」；0.166 起才支持条件多 return。
- **版本 skew 已核实**：本机 hugo 0.167.0，CI 锁定 0.164.0 —— 同一写法两端行为可能分叉，深化方案必须按 0.164 语义编写。
- data/ 纯静态，无构建期计算；构建期派生只能靠 partial/store（构建内）或预构建脚本（构建外）。

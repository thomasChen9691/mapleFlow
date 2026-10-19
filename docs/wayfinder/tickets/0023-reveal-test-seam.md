---
id: 0023
title: 可测试的缝：JS 行为测试与产物断言的分工
type: grilling
mode: HITL
status: open
blocked_by: [0022]
assignee:
map: map-reveal-protocol.md
---

## Question

目的地要求「可测试」——测试缝落在哪、怎么分：

1. **分工**：哪些行为进 Node DOM harness（真实点击、aria-pressed、计数、空态、减弱动效、同页多实例），哪些只配 build-then-assert 产物断言（class / data-* / aria / 脚本挂点存在性、no-js 降级规则的存在）？判据是什么？
2. **套件与守门**（若引 harness）：测试落点（并入 `tests/assert_product_states.py` 还是新脚本如 `tests/assert_reveal.py`）、样本 HTML 来源、CI 守门（权威 / advisory）、与 Hugo 版本 skew 的关系（harness 消费产物，预期与 Hugo 版本无关——需确认）。
3. **既有缺口**：no-js 基线（html class、head swap 脚本、`.no-js .reveal` CSS 降级）当前零断言，缺口补在哪个缝？

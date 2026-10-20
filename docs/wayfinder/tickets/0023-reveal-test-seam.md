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

## 施工期注记（2026-10-20，待本工单追认）

0022 决议④的 A/B 分流已按用户指示提前施工（候选 4 先例：施工先于工单，本段登记待追认事实）：

- **A 类行为 harness**：落点 `tests/assert_reveal.mjs`（Node ESM + jsdom），样本 HTML 手写于 harness 内（镜像渲染 seam 的 DOM 契约），未用构建产物；A 类 9 项已全落（RGR-1..8，含 RGR-7c 减弱动效分支）。A6 的 remove→reflow→add 中 reflow 不可观测（jsdom 无布局），断言只锁终态与 timer 行为——评审确认为可观测极限，不测实现细节。
- **B 类产物断言**：并入 `tests/assert_product_states.py`（`assert_reveal_artifacts`，B1–B6），B5 为精确集合比对。
- **依赖供给**：jsdom 经仓外 symlink（`node_modules → managed workspace`）解析，`package.json` 未入仓、CI 无 node 步——harness 目前只在开发机可跑。**这是本题待决的核心**：套件形态已事实定为「独立 .mjs（行为）+ 并入 .py（产物）」，但依赖入仓方式（package.json + npm ci 步 / vendored / CI 不跑仅本地 advisory）与 CI 守门策略未定。
- **C 类逐出已执行**：视觉参数数值未断言（评审曾抓出 520ms 数值被打钉，已删）；搜索 JS 未碰。

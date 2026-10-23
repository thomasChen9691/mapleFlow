---
id: "0053"
title: 入口与呈现层的测试缝
type: grilling
mode: HITL
status: open
blocked_by: [0052]
assignee:
map: map-search-entry.md
created: 2026-10-23
---

## Question

新入口 / 呈现层的测试缝（前提：0052 已决，契约定义处已落位）：

1. **行为测试**：入口交互（唤起 / 聚焦 / 键盘 / 浮层 / no-js 降级）与呈现层加深的 jsdom 套件——并入 `tests/assert_reveal.mjs` 还是新建 `tests/assert_search.mjs`；`package.json` 的 test 入口是否调整；样本 DOM 手写镜像契约（ADR-0007 先例：不用构建产物，fingerprint / minify 会使 harness 脆弱）；断言范围与 0052 契约定死范围一致。
2. **产物断言**：入口在首页 / 全站的渲染挂哪个 fixture 构建（现有三套：dataDir fixture / contentDir fixture / 真实数据——第四套 config 键的成本，fixture 基建单份原则）；fastsearch 构件引用面断言（哪些页面必须引用 `search.*.js`——交付面守门，参照 0047 先例）；加载条件改动的回归（search 页仍加载、新页面也加载、其余页面不加载）。
3. **坏用例缝**：若 0052 新增 errorf——进 `tests/fixtures/bad/` + `BAD_CASE_EXPECT` 逐用例钉子串（参照产品索引门禁先例）。
4. **CI 守门**：deploy.yml 的 `Assert site contracts` 步与新断言的关系；`npm test` 入口是否仍单条。

纪律沿用：每条断言变异检验（破坏实现 → 红 → 还原）；期望值独立字面量（非同义反复）；真实内容不锚（字段契约与结构必须锚）。

**已决输入**：ADR-0010 决策 5（不立 jsdom 行为套件的理由与「重写时测试与新契约一起 TDD」的既定路径——本图不是重写，入口交互的测试缝要回答「为什么这次值得立」或按产物断言覆盖）、0047 测试缝先例、0052 契约落位。

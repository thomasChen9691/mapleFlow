---
id: "0047"
title: 搜索契约的测试缝
type: grilling
mode: HITL
status: open
blocked_by: [0043, 0044, 0046]
map: map-search-contract.md
created: 2026-10-22
---

## Question

「可测试」落在哪个缝上（前提：0043 / 0044 / 0046 已决）：

1. **行为断言**：fastsearch 的 jsdom 套件——并入 `tests/assert_reveal.mjs`（连同改名？）还是新建 `tests/assert_search.mjs`；`package.json` 的 test 入口如何调整；样本 DOM 手写镜像契约（ADR-0007 先例：不用构建产物，fingerprint / minify 会使 harness 脆弱）；断言范围（渲染结果 / 键盘导航 / 容错降级）与 0046 契约定死范围一致。
2. **产物断言**：index.json 投影契约——挂现有 dataDir fixture 构建（`tests/hugo.test.toml`）还是新建 fixture 配置（第四套构建的成本：fixture 基建单份原则下只加 config 键还是整轮复制）；断言清单（字段集 / 排除规则 / 产品条目 / featured 投影与否）；与既有两条真实数据断言（产品 tag = ["产品"]、SOP 派生在场）的归并关系（谁迁进 fixture、谁留真实数据守线上回归）。
3. **坏用例缝**：若 0044 定 errorf——契约坏用例进 `tests/fixtures/bad/` + `BAD_CASE_EXPECT` 逐用例钉子串（「搜索索引数据：」前缀？含 id 与坏值？参照产品索引门禁先例）。
4. **CI 守门**：deploy.yml 的 `Assert site contracts` 步与新断言的关系；`npm test` 步骤已在（候选 5 时加入）——行为套件若新建，入口是否仍是单条 `npm test`。

纪律沿用：每条断言变异检验（破坏实现 → 红 → 还原）；期望值独立字面量（非同义反复）；真实精选 / 产品清单类内容不锚（内容由项目负责人掌控——但字段契约与结构必须锚）。

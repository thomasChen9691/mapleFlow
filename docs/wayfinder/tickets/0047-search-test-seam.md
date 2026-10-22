---
id: "0047"
title: 搜索契约的测试缝
type: grilling
mode: HITL
status: closed
blocked_by: [0043, 0044, 0046]
assignee: agent
map: map-search-contract.md
created: 2026-10-22
claimed: 2026-10-22
closed: 2026-10-22
---

## Question

「可测试」落在哪个缝上（前提：0043 / 0044 / 0046 已决）：

1. **行为断言**：fastsearch 的 jsdom 套件——并入 `tests/assert_reveal.mjs`（连同改名？）还是新建 `tests/assert_search.mjs`；`package.json` 的 test 入口如何调整；样本 DOM 手写镜像契约（ADR-0007 先例：不用构建产物，fingerprint / minify 会使 harness 脆弱）；断言范围（渲染结果 / 键盘导航 / 容错降级）与 0046 契约定死范围一致。
2. **产物断言**：index.json 投影契约——挂现有 dataDir fixture 构建（`tests/hugo.test.toml`）还是新建 fixture 配置（第四套构建的成本：fixture 基建单份原则下只加 config 键还是整轮复制）；断言清单（字段集 / 排除规则 / 产品条目 / featured 投影与否）；与既有两条真实数据断言（产品 tag = ["产品"]、SOP 派生在场）的归并关系（谁迁进 fixture、谁留真实数据守线上回归）。
3. **坏用例缝**：若 0044 定 errorf——契约坏用例进 `tests/fixtures/bad/` + `BAD_CASE_EXPECT` 逐用例钉子串（「搜索索引数据：」前缀？含 id 与坏值？参照产品索引门禁先例）。
4. **CI 守门**：deploy.yml 的 `Assert site contracts` 步与新断言的关系；`npm test` 步骤已在（候选 5 时加入）——行为套件若新建，入口是否仍是单条 `npm test`。

纪律沿用：每条断言变异检验（破坏实现 → 红 → 还原）；期望值独立字面量（非同义反复）；真实精选 / 产品清单类内容不锚（内容由项目负责人掌控——但字段契约与结构必须锚）。

**0044/0046 已决输入**（已随同场施工落地的部分，本工单只定剩余形状）：① 产品条目形态断言（title/permalink/content）已加在 `assert_search_projection`，挂既有 dataDir fixture 构建；② fastsearch 的契约定义处已就位（`fastsearch.js` 文件头 docstring，现状快照含键盘语义与 XHR 容错）；③ jsdom 行为测试（是否新建 `assert_search.mjs`、`npm test` 入口调整、样本 DOM 手写镜像）仍是本工单的待决面；④ 套件合流 / 命名（`assert_site_contracts.py` 是否因职责再扩张而改名）亦归本工单。

## Resolution

2026-10-22 · grilling（用户为决策者），两问落定：

1. **不立 jsdom 行为套件，改补产物级断言**。事实依据：fastsearch.js 是无导出经典脚本（顶层 DOM 捕获 + `window.onload` + 事件绑定全是加载时副作用），reveal 那套「ESM import + cache-bust」harness 用不了——要 JSDOM `runScripts` 注入源码 + stub XHR + 加载 fuse UMD + 手动触发 onload，约 100 行一次性成本，测的是上游遗留行为的快照。重写时新引擎按 mf-reveal 模式抽 ESM 可测模块，测试与新契约一起 TDD 出生。**补的产物断言**（0043 docstring ④ 交付面条款的牙）：search 页引用 `search.*.js` 且构件落盘（对位 B2 接线断言）、构件 fetch 路径为同目录 `"index.json"`；锚 fixture 构建（`--quick` 也跑；构件经 `resources.Minify`，路径用容忍引号的正则匹配）。
2. **套件不改名**：`assert_site_contracts.py` 头注释「五类职责」更新为七类（+ 搜索索引投影 / 搜索交付面与 fastsearch 守门）；CI 与 `npm test` 入口零改动——新断言全在 python 套件，deploy.yml 的 Assert site contracts 守门步自候选 7 起已在。

**同场施工**（项目负责人指示）：`assert_search_artifacts` 已落位（fixture 构建锚定）；头注释已更新。

**下游**：0048 收口无新阻塞——ADR-0010 测试缝组的输入即本两条。

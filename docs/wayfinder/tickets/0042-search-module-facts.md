---
id: "0042"
title: 搜索模块现状事实底座（盘点）
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-search-contract.md
created: 2026-10-22
claimed: 2026-10-22
closed: 2026-10-22
---

## Question

搜索模块的现状盘点——本图后续所有决策的事实前提，只查事实、不做决策。要盘清六项：

1. **index.json 投影面**：`layouts/_default/index.json` 的全量投影字段与变换（含 `summary` / `content` 是否同源截断）、三类排除规则（searchHidden / archives / search layouts）、产品条目的拼接方式与硬编码字段、0019 边界注释原文、投影层有无任何契约执法（errorf）。
2. **fastsearch 接线面**：`themes/maplemod/layouts/partials/head.html` 的加载条件（`.Layout == search`）、`js.Build` 的 params 传递（`site.Params.fuseOpts` 在 hugo.toml 未配置时的实际行为）、与 `fuse.basic.min.js` / `license.js` 的 concat + fingerprint 管线；`fastsearch.js` 的默认 keys、Fuse options、DOM 挂点（searchbox / searchInput / searchResults、focus class、结果 `li` 结构）、键盘导航语义、XHR 失败时的容错。
3. **search 页面**：`content/search.md` front matter、主题 `_default/search.html` 的三挂点与 aria 属性、`assets/css/common/search.css` 的存在与覆盖范围。
4. **现有断言覆盖与缺口**：`assert_site_contracts.py` 的 `assert_search_index`（产品 tag）与 B11（三挂点）各自锚在哪种构建（fixture / 真实数据）；`assert_sop_pipeline.py` 的「索引含全部派生条目」；`npm test`（assert_reveal.mjs）是否覆盖搜索；逐项列出缺口：fixture 覆盖、行为测试、坏值契约、契约定义处。
5. **各 ADR / 工单留给本图的边界注记原文汇编**：ADR-0006 决策 5、ADR-0007 Consequences、ADR-0008 Consequences 与 B11、ADR-0009 边界、工单 0019 Resolution 第 3 条、0026（若涉及搜索）——逐条摘录原文与出处（文件:行号）。
6. **hugo.toml 搜索相关参数现状**：`[outputs] home`、menu search 项、`fuseOpts` 缺失；按参数纪律（每个参数须有读取点）核对搜索相关参数的读取点存在性。

产物：`docs/wayfinder/research/0042-search-contract-facts.md`，逐条带文件:行号证据；结尾给「缺口清单」（现有断言未覆盖、且候选 8 需要决策的问题面）。

## Resolution

2026-10-22 · research（AFK，agent 独立完成；事实经二次核实）：事实落 `docs/wayfinder/research/0042-search-contract-facts.md`。

六项结论摘要：

1. **投影面**：index.json 六字段（title/permalink/summary/content/tags/categories）；**summary 与 content 同源**（都是 .Summary 的 plainify 截断，200 vs 320，content 不含正文——产物抽样 12/12 坐实）；三类排除（searchHidden/archives/search layout）；产品条目直读 `site.Data.products`（不过 kind 门禁，0019 注释在 index.json:28-30）；**投影层零 errorf**；无 featured 投影。
2. **fastsearch 接线**：head.html:77-90 仅 `.Layout == search` 时经 js.Build params 传 fuseOpts + concat fuse/license + fingerprint；hugo.toml **未配置 fuseOpts**，实测 nil params 构建 exit=0 且产物指纹与线上一致（整段 fuseOpts 分支:29-43 是潜伏死路径）；默认 keys 四字段、threshold 0.4；XHR 取 ../index.json，**失败仅 console.log、JSON.parse 无 try/catch——静默失效**；键盘导航（Escape/↑↓/→）语义已梳理；header.html:88-91 搜索项有 accesskey=/。
3. **search 页面**：content/search.md 仅 title/layout/summary 三键；search.html 三挂点在 :18-21（另 maxlength=64、aria-label）；search.css 45 行且经 resources.Match **全站加载**。
4. **断言覆盖**：产品 tag 断言锚 **fixture 构建**（:389），B11 三挂点锚 **真实构建**（assert_theme_contract 内，--quick 即跳过），SOP 派生在场锚真实构建（assert_sop_pipeline.py:436）；**fastsearch 行为测试零**（assert_reveal.mjs grep 计数 0，npm test 只跑它）；缺口 10 条已列（投影无契约定义处、文章侧投影零断言、content/summary 同源无文档、坏值无门禁、行为无测试、li/focus DOM 契约无定义处、fuseOpts 死路径无处置、featured 投影未决、kind 门禁未决、测试入口扩展未决）。
5. **边界注记**：0006 决策 5、0007 Consequences、0008 Consequences、0009 边界、0019 Resolution 3、handoff 下一步 2 原文均已摘录——本图的三条线（投影字段 + fastsearch + kind 门禁）正是这些注记 deferred 的问题。0026 不涉及搜索（已核）。
6. **hugo.toml 参数**：outputs home JSON（:215-218）与 menu search 项（:183-188）均有读取点、无死配置；fuseOpts「有读取点、无配置」，存废归 0046。

**活例证（0044 坏值决策的直接输入）**：SOP 管线 fixture（tests/fixtures/featured/data/sop.yaml）两条条目无 intro，`_content.gotmpl:61` 的 printf 把 nil 渲染成 `%!s()`，静默污染派生页摘要并进 tests/tmp/featured/index.json——投影层无校验的实例；真实 data/sop.yaml 6 条均有 intro，生产不受影响。

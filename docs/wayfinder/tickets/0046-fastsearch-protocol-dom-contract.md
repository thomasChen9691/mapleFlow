---
id: "0046"
title: fastsearch 的协议归属与 DOM 契约
type: grilling
mode: HITL
status: open
blocked_by: [0042]
map: map-search-contract.md
created: 2026-10-22
---

## Question

fastsearch.js（主题层 vendored 上游 PaperMod 代码：无 docstring、无行为测试、`fuseOpts` 参数位存在但 hugo.toml 未配置）的治理形态：

1. **协议归属三选一**：a) 纳入 ADR-0007 reveal 协议（三层文档契约扩展——须评估语义相容性：reveal 的既定语义是「动效交互：滚动进场 / 筛选 / hero」，搜索是检索交互，是扩容还是混淆）；b) 独立为新的命名协议模块（docstring 落 `assets/js/fastsearch.js` 文件头？与 mf-reveal 的「引擎 docstring 即契约定义处」先例对齐）；c) 保持上游原样，只守 B11 产物断言（可测试性下限，AI 导航靠 ADR / 注释）。
2. **DOM 契约的定义处与范围**：三挂点（searchbox / searchInput / searchResults）、结果 `li` 结构（post-entry / entry-header）、focus class、键盘导航（↑ ↓ / Escape / → / 同值再点）——哪些必须契约定死、定义落在哪（docstring vs 测试字面量）、与 B11 断言的关系（B11 保留 / 并入 / 改写指向新契约）。
3. **fuseOpts 参数化**：`site.Params.fuseOpts` 有读取点（head.html js.Build params）但 hugo.toml 未配置，fastsearch.js 全默认运行——按参数纪律是「补配置 + 文档化默认值」还是「删参数位、默认值写进 docstring」？默认 keys（title / permalink / summary / content）与 0044 投影字段的联动：投影加字段而 keys 不消费 = 死字段，两边如何对齐。
4. **降级与容错是否入契约**：JS 加载失败 / index.json XHR 失败时的现状行为（console.log）、no-js 下搜索页可用性、reduced-motion 与搜索的关系（ADR-0007 的 reduced-motion 引擎是否覆盖搜索交互）。

背景（事实）：ADR-0007 Consequences 明示「搜索 JS（fastsearch）与 index.json 投影不属本 ADR，归候选 8」；head.html 的 search 区块（条件加载 + concat + fingerprint）与 fastsearch.js 全文见 research/0042。

**0043 已决输入**：投影 docstring 含 fastsearch 接口条款（默认 keys = [title, permalink, summary, content] 与 ../index.json fetch 路径），且 keys 与投影字段的对齐由 `assert_site_contracts.py` 的静态断言执法——本工单若重写 fastsearch 或改 keys，接口条款锚点随移，docstring 与断言两处须同步。

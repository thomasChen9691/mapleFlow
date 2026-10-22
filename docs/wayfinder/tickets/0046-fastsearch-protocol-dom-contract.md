---
id: "0046"
title: fastsearch 的协议归属与 DOM 契约
type: grilling
mode: HITL
status: closed
blocked_by: [0042]
assignee: agent
map: map-search-contract.md
created: 2026-10-22
claimed: 2026-10-22
closed: 2026-10-22
---

## Question

fastsearch.js（主题层 vendored 上游 PaperMod 代码：无 docstring、无行为测试、`fuseOpts` 参数位存在但 hugo.toml 未配置）的治理形态：

1. **协议归属三选一**：a) 纳入 ADR-0007 reveal 协议（三层文档契约扩展——须评估语义相容性：reveal 的既定语义是「动效交互：滚动进场 / 筛选 / hero」，搜索是检索交互，是扩容还是混淆）；b) 独立为新的命名协议模块（docstring 落 `assets/js/fastsearch.js` 文件头？与 mf-reveal 的「引擎 docstring 即契约定义处」先例对齐）；c) 保持上游原样，只守 B11 产物断言（可测试性下限，AI 导航靠 ADR / 注释）。
2. **DOM 契约的定义处与范围**：三挂点（searchbox / searchInput / searchResults）、结果 `li` 结构（post-entry / entry-header）、focus class、键盘导航（↑ ↓ / Escape / → / 同值再点）——哪些必须契约定死、定义落在哪（docstring vs 测试字面量）、与 B11 断言的关系（B11 保留 / 并入 / 改写指向新契约）。
3. **fuseOpts 参数化**：`site.Params.fuseOpts` 有读取点（head.html js.Build params）但 hugo.toml 未配置，fastsearch.js 全默认运行——按参数纪律是「补配置 + 文档化默认值」还是「删参数位、默认值写进 docstring」？默认 keys（title / permalink / summary / content）与 0044 投影字段的联动：投影加字段而 keys 不消费 = 死字段，两边如何对齐。
4. **降级与容错是否入契约**：JS 加载失败 / index.json XHR 失败时的现状行为（console.log）、no-js 下搜索页可用性、reduced-motion 与搜索的关系（ADR-0007 的 reduced-motion 引擎是否覆盖搜索交互）。

背景（事实）：ADR-0007 Consequences 明示「搜索 JS（fastsearch）与 index.json 投影不属本 ADR，归候选 8」；head.html 的 search 区块（条件加载 + concat + fingerprint）与 fastsearch.js 全文见 research/0042。

**0043 已决输入**：投影 docstring 含 fastsearch 接口条款（默认 keys = [title, permalink, summary, content] 与 ../index.json fetch 路径），且 keys 与投影字段的对齐由 `assert_site_contracts.py` 的静态断言执法——本工单若重写 fastsearch 或改 keys，接口条款锚点随移，docstring 与断言两处须同步。

## Resolution

2026-10-22 · grilling（用户为决策者），四问落定：

1. **协议归属：独立「搜索协议」模块，现状快照式契约**——docstring 落 `themes/maplemod/assets/js/fastsearch.js` 文件头，与 ADR-0007 三层模式同构；**不并入 reveal**（reveal 语义是动效交互，搜索是检索交互，并入即重开 0007 的模块定义）、**不与投影合并命名**（0043 已决跨层不合并；CONTEXT.md 侧一词条两指针互指——0048 决议①对决议①「并列互指」表述的勘误落于此）。
2. **快照全量收录**：三挂点（searchbox/searchInput/searchResults）、`.focus` 类（search.css `#searchResults .focus` 消费）、`li > header + a` 覆盖结构（`#searchResults a` 绝对定位点击热区）、键盘语义（Escape 重置 / ↑↓ 导航 / → 点击）、XHR 路径与失败行为。后两块显式标注「vendored 上游快照」与「已知限制」。B11 保留为挂点的唯一机械断言（注释改指向 docstring）；jsdom 行为测试归 0047。
3. **删 fuseOpts 参数位**：head.html 去 `js.Build` 的 params 传递；fastsearch.js 删 `@params` import 与 fuseOpts 分支（含 search 的 limit 分支）；默认值（threshold 0.4 / distance 100 / ignoreLocation true / keys 四字段）升格为 docstring 契约。调参 = 改代码 + 改契约 + 评审，不再留无人执行的配置分支。
4. **容错行为记录不动代码**：XHR / JSON.parse 失败 = 静默失效类**已知限制**（待重写或加容错时处理）；no-js = 客户端搜索固有不可用（ADR-0002 基线只保证内容可读）；reduced-motion = 无运动面（唯一动效是 `li:active` 0.1s 按压反馈，非进场动画）。

**同场施工**（项目负责人指示）：fuseOpts 删除为行为保持型重构——安全网 = 既有全套 + 生产构建绿，验收 = 产物 search.js 不再含 fuseOpts 字样；docstring 快照落位；B11 注释改指向新定义处。

**下游**：0047 若立 jsdom 行为测试，契约定义处已就位；CONTEXT.md 协议层术语（「搜索索引」条是否扩展出检索协议表述）归 0048；雾区新增「索引加载失败的容错 UX」。

**施工期补记（2026-10-22，TDD 循环 B-E 的发现，重要）**：research/0042 读的是主题层 `themes/maplemod/assets/js/fastsearch.js`，**漏掉了站点级覆盖** `assets/js/fastsearch.js`（commit 59a93f4，子模块时代为修子路径部署 XHR 404 而建）——Hugo 的 `resources.Get` 项目级优先，**活的是一直是站点级那份**，主题层是死文件。连带三处修正：① 0043 施工期的 B3 断言一度读的是死文件（keys 凑巧一致所以绿着）、0043 docstring ④ 的 fetch 路径记的是死文件行为（`../index.json`）——本轮已改记活行为（同目录 `index.json`，附子路径 rationale）；② 覆盖的存在理由（不动主题子模块）随 ADR-0008 fork 消亡，本轮把 XHR 修正**合并进主题层并删除站点级覆盖**，恢复单副本（`git rm`），并加「单副本守门」断言防覆盖复活；③ 顺带修了 head.html preload 的 `../index.json` → `index.json`（同一子路径 bug 的另一半，此前只修了 JS fetch；preload 指错域根无害但让交付面条款不真）。fuseOpts 删除后产物 search.js 已无 `fuseOpts`/`@params` 字样（grep 实证）。**教训入账：事实盘点也要查「项目级覆盖/同名文件」——本次两处「我以为的事实」（死文件当活文件）都是 diff 两份同名文件才翻的盘。**

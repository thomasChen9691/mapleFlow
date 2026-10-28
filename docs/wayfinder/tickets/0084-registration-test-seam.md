---
id: "0084"
title: 注册缝改造后的测试加载面与降级语义
type: grilling
mode: HITL
status: closed
blocked_by: ["0083"]
assignee: agent
claimed: 2026-10-27
closed: 2026-10-28
map: map-architecture-deepening.md
created: 2026-10-27
---

## Question

注册缝下沉后，行为断言怎么加载被测代码——**这是本图最容易产生假绿的一票**。

现状：`tests/assert_reveal.mjs`（23 条）与 `tests/assert_search.mjs`（41 条）用 `dom.loadFresh()` **直接加载引擎源文件**，注册完全依赖 import 副作用；`tests/assert_harness.mjs`（8 条）也直载 `reduced-motion.js`。若引擎改成「导出 `mount` 不自执行」，这些断言会**加载成功但什么都没挂载**——断言若只查「无异常」就静默变绿。

要决策的面：

1. **测试加载面**：改载 `app.js` 入口（贴近生产）还是继续按引擎单文件加载（贴近单元）；两者对「注册表写错」的覆盖差异。
2. **双写风险**：若测试需自己调 `mount`，测试里就出现一份「注册清单」，与 `app.js` 的注册表**双写**——用哪个机制消除（从 `app.js` 导出注册表供测试复用 / 测试只测入口 / 断言注册表与目录文件一一对应）。
3. **假绿防线**：加一条「挂载生效」的哨兵断言（如挂载后必有一个可观测副作用：`is-in` 出现、`--mf-progress` 被写），确保「加载但未注册」会红。
4. **降级语义**：no-js 基线（ADR-0002）与「引擎缺失 / 注册失败」时的行为是否变化；`extend_footer` 的 `errorf`（入口缺失）是否要新增「注册表引用了不存在的引擎」的构建期检查。
5. **断言计数与套件归属**：新增断言放 `assert_reveal.mjs` 还是 `assert_harness.mjs`（后者是 Node 侧自测，ADR-0014 决策 8 的先例）；计数变化如何记录（CI 权威）。

边界（不开票）：搜索检索行为断言（27 条浮层 + 14 条入口）的语义不改，只改加载方式；Hugo 构建期不可读 JS 源码，故不做构建期注册检查（除非 0087 证明可行）。

## Resolution（决议已定，施工未开始）

2026-10-27 · grilling（HITL，三问定案）。

**加载方式 = helper + 显式挂载**：`dom.mjs` 加一个 mount helper（只做机制、不持期望值，符合 harness seam 纪律：`dom.mjs` docstring「seam 之后只有机制」）。`assert_reveal.mjs` 的 **13 处 `loadFresh`**（filter 7 / scroll-in 3 / reading-progress 3）全部补显式挂载。事实：`loadFresh(rel)` 只 `import(url + '?t=N')`，**只 bust 自己、不 bust 依赖**——引擎纯化后加载 app.js 不会重求值其依赖，但 app.js 的调用会以新 document 再跑一遍，故「测 app.js」技术上可行。

**假绿防线 = 注册完整性断言**：一条断言比对 `assets/js/mf-reveal/*.js` 与 `app.js` 的 import 清单，白名单**仅** `reduced-motion.js`（共享判定、非引擎）。防的是「app.js 漏挂一个引擎 → 测试全绿、线上少一个功能」。

**为什么不改测 app.js**：一个用例会同时挂三个引擎、互相干扰（filter 扫 `.mf-index` 会污染 scroll 用例），失败定位变差；且 [0083](0083-registration-seam-shape.md) 的 try/catch 隔离会吞错，测 app.js 必须额外加 `console.error` spy 才不假绿。

**降级语义 = 引擎自兜底**：`initScrollIn` 内部 try/catch，失败即走与「无 IntersectionObserver」**同一条**降级路径（全量直写 `is-in`，内容可见）；`app.js` 的 catch 只上报、不兜内容。理由：兜底逻辑必须留在拥有 DOM 契约的引擎里（ADR-0007）；放到 `app.js` 等于让装配层知道 `.reveal` 这个选择器。这也是 [0083](0083-registration-seam-shape.md) 的 try/catch 没盖住的那个洞——隔离只保其余引擎，不保「自己炸了内容还在」。

**套件归属 = 机制归 harness、契约归 reveal**：mount helper 是 `dom.mjs` 的机制 → 自测进 `assert_harness.mjs`（ADR-0014 决策 8「自测先于契约红」）；「`app.js` 注册完整性」是产品契约（漏挂一个引擎 = 功能缺失）→ 进 `assert_reveal.mjs`。计数预期 **8 + 23 + 41 → 9 + 24 + 41**。

**施工（2026-10-28，PR①）**：`dom.mjs` 新增 `loadMounted(rel, mount)`（加载 + 挂载 + 返回模块），`assert_reveal.mjs` 的 11 处直载点改用它、2 处保留显式调用（RGR-0 测「import 无副作用」必须直载；RGR-11 显式调 `initReadingProgress`）；`scroll-in` 加 fail-open（内部 try/catch，异常走与「无 IO」同一条直落终态路径）。

**RGR-13 评审后重写**：初版是源码扫描（`appSrc.includes('./x.js')`），评审指出「只 import 不挂载」也能通过——正是它要防的假绿。改为**行为断言**：装一个含三类挂点的 DOM，加载生产入口 `app.js`，断言点亮 / 筛选计数 / 进度变量三个副作用都出现。装配表漏一行即红。

**计数实际值**：8+23+41 → **9+28+41**（比决议预估多 4 条：RGR-0a/0b、12a/12b）。

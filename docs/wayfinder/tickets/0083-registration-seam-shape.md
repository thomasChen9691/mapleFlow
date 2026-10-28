---
id: "0083"
title: 注册缝的形态与 API：自注册改成 app.js 显式注册
type: grilling
mode: HITL
status: closed
blocked_by: ["0079"]
assignee: agent
claimed: 2026-10-27
closed: 2026-10-28
map: map-architecture-deepening.md
created: 2026-10-27
---

## Question

「注册缝下沉到 app.js」具体长什么样——本图最容易被做成「搬家」的一票，因此先定边界再定形状。

现状：三个引擎在模块底部各自 `autoInit()`，**import 即副作用**（`scroll-in` 直接 `initScrollIn(document)`、`filter` 扫 `.mf-index` 后逐个 `initFilter`、`reading-progress` 直接挂 `scroll` / `resize` 监听）；`app.js` 只有三行 import、零注册逻辑；搜索浮层另有装配入口 `mf-search-overlay.js`（`@params` 注入 URL + 两引擎），与 reveal 是**两套形态**。

要决策的面：

1. **注册形态**：(a) 引擎导出 `mount(doc, win)`，`app.js` 逐个显式调用；(b) `app.js` 持一张注册表（`name → mount` 数组 / Map）遍历挂载；(c) 保留 `autoInit`，仅把「扫 DOM 找挂点」的逻辑上提到 `app.js`。三者的差别在「谁拥有挂点发现权」。
2. **副作用去留**：引擎是否彻底无 import 副作用（可测试性收益 vs 测试与既有加载面的改造量）；若保留 `autoInit` 作为兼容出口，注册缝算不算真的下沉了。
3. **挂点发现权的归属**：`.reveal` / `.mf-index` / `[data-mf-progress]` 的选择器由引擎自持（现状）还是 `app.js` 传元素进去——这决定引擎能否被单测成纯函数。
4. **顺序与依赖语义**：现状声明「互不依赖、import 顺序无关」；显式注册后是否引入顺序契约（例如 `reduced-motion` 判定必须先于 scroll-in），以及这个顺序写在哪里（注册表顺序 / 显式调用顺序）。
5. **失败隔离**：单引擎 throw 是否影响其余引擎挂载（现状 import 期 throw 会中断整个 bundle）。
6. **搜索浮层是否同构**：`mf-search-overlay.js` 也是装配入口——本票是把它一并收敛成同一注册骨架，还是明确承认两者形态不同（`@params` 注入是构建期关注点，与 DOM 挂载是两件事）。

边界（不开票）：DOM 契约本身（class / data-* / aria 的语义）不动，归各引擎 docstring 与 ADR-0007；搜索检索链路不动。

## Resolution（决议已定，施工未开始）

2026-10-27 · grilling（HITL，项目负责人三问定案；与 0080/0081/0084 同场 grill）。

**Q1 注册形态 = 对齐搜索入口**（不是发明新形态）：`assets/js/mf-search-overlay.js` 早就是装配式——引擎纯导出（`initSearchOverlay(document, window, {...})`）、入口显式调用，docstring 还写明「入口/引擎裂为两文件」的理由是「引擎零 Hugo 依赖、可被 Node 直接导入」。**只有 reveal 这一套是自注册的**。决议：`app.js` 变装配入口（三行显式调用），引擎去 `autoInit`、只导出 `initX(doc)`。

**Q2 挂点发现权 = 留在引擎**：引擎仍自扫自己的选择器（`.reveal` / `.mf-index` / `.mf-progress`），`app.js` 只调用不扫描。理由：选择器与契约 docstring 同文件（ADR-0007「契约定义处唯一」）；`app.js` 的三行调用清单本身就是可导航索引，无需把选择器搬出来另立一张表。

**Q3 顺序 = 顺序无关**（维持现状声明）：不引入「scroll-in 必须先于 filter」的显式契约——该依赖未经证实，不为未验证的依赖写契约。

**Q4 失败隔离 = 逐个 try/catch + `console.error` 上报**：单引擎失败不连带其余。理由 ADR-0002：`scroll-in` 不跑时 `.reveal` 停在 `opacity:0` = **内容消失**，不能让一个筛选 bug 连带阅读进度条与进场动效一起死。已知代价：bundle 路径上的异常不再显眼（测试直载引擎仍会红，→ [0084](0084-registration-test-seam.md)）。

**Q5 搜索浮层 = 不同构、不动它**：`@params` 是构建期注入，与 DOM 挂载是两件事；本票只把 reveal 对齐它，不反向改搜索入口。

**施工（2026-10-28，PR①）**：三引擎删除 `autoInit` 与 import 期调用（`scroll-in` / `filter` / `reading-progress`）；`app.js` 改为装配入口——`ENGINES` 表 + `for` 循环 + 逐个 `try/catch` + `console.error`；引擎文件头补「注册缝在 app.js」指针。

**一处命名偏差（诚实入档）**：本票原文写「只导出 `initX(doc)`」，实际 `filter` 导出的是 `mountFilter(doc)`——因为它的单元是 `initFilter(el)`（收元素），若让 app.js 扫 `.mf-index` 就违反 Q2「选择器留引擎」。故新增 `mountFilter` 作为引擎侧的挂载入口，选择器仍在引擎内。

**验证**：`npm test` 9+28+41 全绿；RGR-0 守「import 无副作用」、RGR-13 守「app.js 真的挂了三个引擎」（行为面，见 0084）。

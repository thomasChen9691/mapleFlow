# 0013 - 搜索浮层：ADR-0010 重评、全站就地检索与入口契约升级

**状态**：已批准（2026-10-24，项目负责人指示展开）。本 ADR 是 ADR-0010「不重写 fastsearch」结论的**正式重评**记录，也是浮层形态的设计决策耐久化。基线：ADR-0010（搜索契约：投影 + 检索快照 + 测试缝）、ADR-0011（搜索入口：快捷键 / 摘要渲染 / 三协议并列）、ADR-0002（no-js 基线）、ADR-0007（reveal 边界）、ADR-0008（分层）。施工批次：C 批浮层形态（2026-10-24）。

## 背景

ADR-0010 的 2026-10-23 指针（一）给「不重写 fastsearch」挂了两个触发条件：「引擎 ESM 化 + 容错 UX」长期挂起，**触发条件是真被 XHR 静默失败咬到、或出现第二个消费方**；届时按决策 5 既定路径——「新引擎按 mf-reveal 模式抽 ESM 可测模块，测试与新契约一起 TDD 出生，本 ADR 的快照契约作为输入」。ADR-0011 的边界条同款约定：「若将来重开浮层 / 首页框形态（**第二个加载面出现**），按 ADR-0010 决策 5 既定路径重评，届时以本 ADR 与 ADR-0010 的快照契约为输入」。

2026-10-24 项目负责人决定完成 C 批「浮层搜索框」形态——一次同时 materialize 两个触发条件：浮层是 index.json 投影的**第二个消费方**，也是 fastsearch 之外的**第二个搜索 JS 加载面**（全站）。重评因此不是可选项而是既定流程；本 ADR 记录重评过程与结论。

## 决策

1. **重评结论：原「不重写」在浮层形态下正式重开，采纳「新引擎」路径，不动 fastsearch**。备选的「改 fastsearch 支持注入 indexUrl」被拒：它的 fetch 是同目录相对（`index.json`）的硬假设，全站化要改检索契约的加载面前提；而 ADR-0010 决策 4 已明确快照契约「重写时接口条款随移」——与其把 legacy 脚本改造成第二形态，不如按决策 5 让新引擎与新契约 TDD 出生，快照契约降为输入。fastsearch 维持 search 页唯一检索落点，本 ADR 不碰它的任何条款。
2. **形态：全站浮层（模态面板），两个入口并列**。图标点击（`.mf-search-link`，C 批已落地）与 `/` 快捷键（ADR-0011 决策 1 原为跳转 search 页）都打开浮层；**search 页角色不变**——仍是完整检索落点（fastsearch 领地、原生 autofocus、完整键盘导航），浮层是「就地快查」面。浮层不做首页常驻框（ADR-0011 已拒：解决的是排序在后的 P2，且不覆盖文章页成本）。
3. **模块边界：站点层引擎 + 主题层骨架，装配入口改名**。`assets/js/mf-search-overlay-engine.js`（纯引擎、零 Hugo 依赖、**契约定义处 = 文件头 docstring**，复刻 mf-reveal / 入口引擎的 ESM 可测模式）；bundle 入口 `assets/js/mf-search-overlay.js`（原 `mf-search-entry.js` 改名——它装配的不再只是快捷键入口；`import * as params from '@params'` 注入 searchUrl + indexUrl）；主题层 `partials/search-overlay.html`（DOM 骨架，挂 baseof 全站在场）+ header 的 `.mf-search-link` 作触发器。站点层落位复刻 ADR-0011 决策 3 理由：零 `resources.Get` 项目级遮蔽风险（0046 翻车教训）。
4. **入口契约升级（supersede ADR-0011 决策 1 的「轻形态只跳转」）**：`/` 的动作为「开浮层」。实现为 entry 引擎的 `env.openSearch` 钩子——有钩子（浮层装配成功）则开浮层，无钩子回落 `searchUrl` 跳转（**原轻形态降级为兜底**，params 缺失时菜单 / 图标链接照常工作，ADR-0002 基线不破）。entry 引擎的键位 / 修饰键 / 焦点门控与 search 页分支（聚焦 `#searchInput`）原样保留——变的只有「非 search 页按下 / 之后发生什么」。
5. **检索契约镜像 + parity 断言**：浮层的 fuse 配置与快照逐字一致——`distance 100 / threshold 0.4 / ignoreLocation true / keys = [title, permalink, summary, content]`（与投影六字段差集 {tags, categories} 不变）。两处配置由 **parity 断言**执法（从 fastsearch.js 与浮层引擎抽同名配置比对）：改一处不改另一处即红——「调参 = 改代码 + 改契约 + 评审」（ADR-0010 决策 4）的纪律跨模块延续。
6. **容错 UX 随新引擎一并出生**（ADR-0010 触发条件的另一半）：索引拉取失败 → 浮层内可见错误态（「索引加载失败」+ 引导去 search 页），不再继承快照的「XHR 失败仅 console.log」静默失效；空结果有空态文案。**索引损坏（JSON.parse）容错**同批处理。
7. **投影契约不变**：index.json 六字段冻结（ADR-0010 决策 2）——浮层消费同一投影（summary 200 已在字段内），**不新增字段**；第二个消费方不触发「改投影字段 = 三处同步」（那说的是改字段，不是加消费方）。
8. **a11y 与动效归属**：浮层 `role="dialog" aria-modal="true"`；打开入焦输入框、关闭还焦触发器、Tab 在面板内困排、打开时锁 body 滚动；Esc / backdrop / 选中结果 / 关闭按钮四路可关。面板过场是**搜索协议**的动效（归本 ADR），不归 reveal（ADR-0007 边界：reveal 是滚动 / 筛选 / 进场）；包在 `prefers-reduced-motion: no-preference` 内，减弱偏好下不过场。
9. **测试缝**：jsdom 行为测试扩建 `tests/assert_search.mjs`（引擎纯函数 + 手写样本镜像 docstring DOM 契约：开关四路 / 焦点管理 / 困排 / 检索渲染 / 空态 / 错误态 / Enter 首条 / params 降级）；产物断言挂既有三套构建（全站加载面 / indexUrl 子路径 / DOM 契约与默认 hidden / parity / no-js）；**无第四套 config**（ADR-0011 决策 4 同款）。
10. **no-js 基线（ADR-0002）**：浮层 DOM 默认 `hidden`——无 JS 时整块不可见，图标是普通链接跳 search 页；无内容被隐藏，只是增强。

## Considered Options

- **改 fastsearch 支持注入 indexUrl 后全站加载**（决策 1，拒绝）：动检索契约的加载面前提与 fetch 假设，把 legacy 脚本推上它没被设计过的形态；且浮层需要的可测 seam 与容错 UX 在经典脚本里都要新造。
- **iframe 嵌 search 页**（拒绝）：焦点管理 / 滚动 / 样式隔离全是坑，移动端尤糟；为 17 条索引付架构税。
- **无 fuse 的轻量子符检索**（拒绝）：结果与搜索页分叉（同一查询两处答案），违背「快照契约为输入」的重评前提。
- **`/` 维持跳转、浮层只走图标**（决策 4，否决）：同一意图两个落点（键盘进检索页、指针进浮层），结果 UI 不一致；且快捷键的 1 步优势（ADR-0011 P1）被削掉一半。
- **浮层并进 mf-reveal  bundle**（拒绝）：语义污染——reveal 边界是动效交互（ADR-0007），浮层是检索交互；ADR-0011 决策 3 已为入口立过同款边界。
- **结果列表复用 fastsearch 的 li 结构与 search.css**（拒绝）：浮层自有 DOM 契约（整行可点、无绝对定位热区），硬套 legacy 结构会把快照的耦合类（`.post-entry` / `.focus`）带进新契约；视觉语言在 custom.css 复用即可。

## Consequences

- 搜索前端从「快捷键跳转」升级为「快捷键 + 图标 → 全站浮层」；search 页 / fastsearch / index.json 投影 / search.css 零改动。
- **指针（本 ADR 收口时落）**：ADR-0010 加一笔（第二个消费方 materialize + 重评结论：不重写快照、新引擎路径采纳）；ADR-0011 加一笔（决策 1 的「只跳转」形态被本 ADR 决策 4 supersede，入口引擎契约以新 docstring 为准）；ADR-0007 加轻笔（浮层过场不归 reveal 的边界闭合）；先前 ADR 正文不改（历史记录，指针行是先例）。
- 术语：CONTEXT.md「搜索入口」条更新（两条路由 + 动作改为开浮层）、新增「搜索浮层」条；AGENTS.md 落 §3 注释 / §7 速查行 / 坑点 14 修订（「第二个消费方」从「守门观测牙」变为「已实现的第二加载面」——加载面双向断言的语义改为：fastsearch 仍仅 search 页、新 bundle 全站）。
- 已知限制（诚实入档）：浮层键盘导航（ArrowUp/Down 选择结果）v1 不做——Tab / Enter / Esc 覆盖基本路径，完整方向键导航留在 search 页（fastsearch 已有）；命中高亮不做（ADR-0011 决策 2 同款理由：不动 fuse matches）。
- **已知限制（fastsearch 冻结的代价）**：`fastsearch.js` docstring 的指针段仍写着「入口只负责跳转 / 聚焦」——该文件按本 ADR 决策 1 **一字不改**（快照契约冻结），故这句已过时；入口的真实行为以 `mf-search-entry-engine.js` 新 docstring 与本 ADR 为准。检索契约条款不受影响。

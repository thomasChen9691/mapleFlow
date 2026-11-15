---
id: "0089"
title: 搜索浮层 v2 现状事实底座（盘点）
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-search-overlay-v2.md
created: 2026-11-15
claimed: 2026-11-15
closed: 2026-11-15
---

## Question

本图所有决策票的共同事实前提。**只查事实、不做决策、不给推荐**；每项带 `文件:行号` 证据，结尾给「缺口清单」（本图需要决策、而现有断言 / 文档未覆盖的问题面）。要盘清六项：

1. **契约定义处与消费面**：`assets/js/mf-search-overlay-engine.js` 文件头 docstring 的条款清单、`assets/js/mf-search-overlay.js` 装配入口（`@params` 注入 searchUrl / indexUrl）、`themes/maplemod/layouts/partials/search-overlay.html` DOM 骨架、`header.html` 的 `.mf-search-link` 触发面；以及 `mf-search-entry-engine.js`、`fastsearch.js` docstring、`index.json` docstring 三处契约之间的互指指针现状（哪句已过时、哪句仍准确）。
2. **现有测试覆盖**：`tests/assert_search.mjs` 中浮层相关条目的编号与覆盖面（开关四路 / 焦点管理 / 困排与 inert 分支 / 检索渲染 / 空态 / 三种索引失败态 / Enter 首条 / params 降级 / iOS 双机制滚锁）、`tests/assert_site_contracts.py` 的产物断言（全站加载面 / indexUrl 子路径 / DOM 契约与默认 hidden / fuse parity / no-js）、`npm test` 三段计数；标出哪些面**只有弱断言或一次性验证**、哪些完全没被覆盖。
3. **ADR-0013 两条已知限制**：方向键导航（ArrowUp/Down）与命中高亮 v1 不做的原文措辞与理由、parity 断言抽取两侧配置的方式、`fastsearch.js` docstring 里那句已过时的「入口只负责跳转 / 聚焦」指针为何冻结（决策 1）。
4. **候选 12 挂起雾区的兑现情况**：`docs/wayfinder/map-search-entry.md` 收口注记三条（移动端 / 小屏入口形态、aria 契约细节、浮层首屏空间关系）逐条比对现状，标注「已兑现 / 部分兑现 / 仍未触及」并给证据；注明触发条件「将来出现浮层形态」由哪笔落地兑现。
5. **2026-10-24 视觉批 E/F 已落的面**：触屏搜索入口、iOS 双机制滚锁（overflow + position:fixed）、inert 背景钉住与手写 Tab 困排兜底、`@starting-style` 统一进出场、`prefers-reduced-motion` 包裹范围、`content-visibility: auto` 未采纳的判据；逐项给文件与断言锚点。
6. **search 页侧的静默失效面**：`fastsearch.js` 的 XHR / `JSON.parse` 失败路径、`index.json` 交付面断言、浮层错误态「引导去 search 页」之后的实际体验落差。

边界（不开票）：不评估「该不该做」，不给方案推荐；**不得运行 Hugo 构建**（以读源码与既有 `public/` 产物为准，避免污染），除研究产物外不修改任何仓库文件，不执行 git 写操作。
研究产物落 `docs/wayfinder/research/0089-search-overlay-v2-facts.md`。

## Resolution

2026-11-15 · AFK research，由研究子代理逐条查证后落盘（「一会话一票」的 research 例外）。

**答案**：事实底座 = [`research/0089-search-overlay-v2-facts.md`](../research/0089-search-overlay-v2-facts.md)，六项盘点逐条带 `文件:行号`，零引用类结论经 Grep 双向复核。要点：

- 契约唯一定义处 = `assets/js/mf-search-overlay-engine.js` 文件头 docstring；装配入口 `assets/js/mf-search-overlay.js`（`@params` 注入 searchUrl / indexUrl）；DOM 骨架与触发面在主题层。三处互指指针里 `themes/maplemod/assets/js/fastsearch.js:14-15` 两句过时（旧文件名 `mf-search-entry.js` + 「入口只负责跳转 / 聚焦」），因 ADR-0013 决策 1 冻结快照而保留；`layouts/_default/index.json` 的 docstring 未记「第二消费方」。
- 现有覆盖：`tests/assert_search.mjs` 的浮层 MFO-1..19（开关 / 焦点 / 困排 / 三种索引失败态 / Enter 首条 / inert / iOS 双机制滚锁 / parity 字面量）+ `tests/assert_site_contracts.py` 的产物断言（全站加载面 / 子路径 URL / 默认 hidden / fuse parity / no-js）；`item.summary` 渲染只有弱断言，「渲染结果正确」靠记录在案的一次性验证。
- ADR-0013 两条 v1 不做（方向键、命中高亮）在浮层引擎零实现，只有 Consequences 一句、无重开触发条件；候选 12 三条挂起雾区的「将来出现浮层形态」触发条件已由 ADR-0013 兑现，其中① 触屏 / ② aria **部分兑现**、③ 首屏空间关系**未触及**；10-24 视觉批 E/F 六面已落。
- 两面容错不对称：浮层有可见错误态并引导去 search 页，而 search 页 fastsearch 的 XHR / `JSON.parse` 仍静默失效且无可见错误态；由 ADR-0010 决策 5 与 ADR-0013 决策 1 固化。
- 盘出文档-实现不一致：docstring 与测试头写返回 `{ open, close, isOpen }`，实现只返回 `{ open, close }`，`isOpen` 全仓零消费、零断言（本图不施工，交「可测试性的判据与测试缝归属」作输入）。

**缺口清单 13 条**（可测试判据 / 所有权分层 / 一次性验证 / parity 边界 / 负向边界形态 / aria 定义处 / 小屏空间 / 失败语义一致 / 重试·i18n·阈值 / reduced-motion 叠加 / 测试计数口径 / `isOpen` 返回形状 / 可施工判据）见研究产物末节，逐条带证据位置，供后续五张决策票认领时取用。

**边界**：未运行 Hugo 构建、未执行 git 写操作、除该研究产物外未改任何仓库文件；研究产物中的地图行号以 2026-11-15 排图时版本为准。本票只给事实，不做决策、不给推荐。

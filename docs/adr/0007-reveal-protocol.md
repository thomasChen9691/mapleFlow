# 0007 - reveal 协议：分层提取、三层文档契约与测试缝

**状态**：已批准（2026-10-20）。决策过程见 wayfinder 地图「reveal 协议图（候选 5）」（docs/wayfinder/map-reveal-protocol.md，六工单 0021~0026 全 closed）；本 ADR 是决策的耐久化记录——AGENTS.md §8.1 的阅读路由（CONTEXT.md + docs/adr/）不含 wayfinder 目录，决策必须活在 docs/adr/。基线本身见 ADR-0002（no-js 渐进增强），产品索引接口见 ADR-0006（filters/uid 的归属）。

## 决策

1. **模块边界**：no-js 基线之上的三块客户端动效交互——产品索引筛选、页脚滚动进场、首页 hero 进场——归一个模块：**reveal 协议**。基线（ADR-0002）不重开，本协议只在其上契约化交互。
2. **分层提取**：`extend_head` 的 class swap 保持内联（ADR-0002 的升级同步件，内容越薄升级面越小）；滚动进场与筛选引擎提取为 `assets/js/mf-reveal/` 模块（`app.js` 入口 / `filter.js` 筛选 / `scroll-in.js` 进场 / `reduced-motion.js` 降级判定），经 `extend_footer` 的 `js.Build | Minify | fingerprint` 引用——与 PaperMod 自家 `head.html` 的 fastsearch 同款管线，Hugo 0.164 可用（js.Build 自 v0.74.0 引入）。模板不再内联 script，只产出 DOM 挂点。
3. **协议形态 = 三层文档契约**：① CONTEXT.md 只放「reveal 协议」主术语（概念层）；② 引擎文件头 docstring 是 DOM 契约的**唯一定义处**（读写的 class / data-* / aria / CSS 变量及其语义）；③ 测试期望值字面量。**不建 spec seam**——ADR-0006 已把词汇 seam 明挂「词表真要扩展时再评估」，现在不是扩展时。
4. **命名权归协议层**：DOM 契约词汇由协议层定义，`product-index.html` 渲染 seam 是消费者。与 ADR-0006 的接口关系：uid 仍 DOM id 必填兼深链锚（短代码 `.Ordinal` 保唯一），引擎遍历 `.mf-index` roots 自动注册，**uid 不再是注册键**；`filters` 收窄为「是否输出筛选控件」（脚本由 `extend_footer` 恒加载）。0006 正文不改，差异记录在本 ADR。
5. **测试缝**：行为断言（A 类 9 项）在 `tests/assert_reveal.mjs`（Node + jsdom，手写样本镜像 DOM 契约，**CI 权威**：`npm ci` + `npm test`，构建前守门）；产物断言（B 类 6 项）并入 `tests/assert_product_states.py`（fixture 基建单份）；视觉参数数值不测（C 类逐出）。依赖入仓（`package.json` + lock，jsdom 唯一 devDependency）。
6. **交互语义**（0024 四问确认现状）：同值再点回「全部」、组内互斥、计数与空态随筛选更新、uid 不扩 hash/URL、reduced-motion 下过滤照常但不播放 morph/bump。**字面契约**（class / aria / 文案 / CSS 变量）以 `filter.js` 的 docstring 为准，本 ADR 只记决策。
7. **is-in 一次性终态**：IO 点亮即 unobserve；筛选交互后可见行直写终态；不重放。`--mf-i` 的变量名与「第 9 条起截断」语义归协议，22ms 延迟值归 CSS 调值。降级判定抽单一 `reduced-motion.js`（两引擎共用），CSS 媒体查询保留为独立兜底层（JS 加载失败时仍定格终态）。
8. **命名与导航**：`motion.js` 定名 `reduced-motion.js`；AGENTS.md 落三处（速查表目录级一行、坑点、§3 `npm test` 命令）；本 ADR 与 ADR-0002 / 0006 互加指针（**0002/0006 正文不改**——ADR 是历史记录，0006 给 0004 加指针行是先例）。

## Considered Options

- **全量内联（不提取）**：拒绝——契约散在三个模板/主题文件，行为无法单测，AI 导航差。
- **spec seam 单一真源**：拒绝——提前实施 ADR-0006 挂起的词汇 seam，测试缝被绑死在 spec 格式上。
- **单一测试入口 / 全搬 node**：拒绝——多一层间接、失败定位变差；复制 python fixture 基建是第二实现（ADR-0004 枪毙的模式）。
- **样本改用构建产物**：拒绝——fingerprint/minify 使 harness 脆弱，样本随 fixture 数据变化。
- **hash 记录筛选状态**：拒绝——静态博客无分享刚需，引入 history 管理与首屏回放复杂度。
- **is-in 可重放**：拒绝——已读内容重新动画分散注意，且需与滚动位置重新协调。

## Consequences

- 改契约 = 改引擎 docstring + 同步断言；两个套件是唯一守门（`npm test` 行为、`assert_product_states.py` 产物）。
- 新增动效/筛选行为只改 `assets/js/mf-reveal/`，模板保持纯渲染。
- jsdom 成为仓库唯一 npm 依赖，锁文件固定版本；CI 增加 Node 步骤（约 +15–25s），失败即阻断部署。
- 主题升级时 `extend_head` 仍是同步件；`extend_footer` 已改为引擎引用，升级面缩小。
- 搜索 JS（fastsearch）与 `index.json` 投影不属本 ADR，归候选 8（搜索契约）。

**2026-10-22 指针**：本 ADR Consequences 末条「搜索 JS（fastsearch）与 index.json 投影归候选 8」已由 **ADR-0010** 定案——fastsearch 独立为「搜索协议」现状快照契约（docstring 落 `themes/maplemod/assets/js/fastsearch.js` 文件头），**不并入本协议**；投影侧契约见同一 ADR。本 ADR 正文不改（历史记录）。

**2026-10-23 指针（二）（候选 12 收口）**：本 ADR 的模块边界（动效交互三块）被候选 12 显式问过并闭合——搜索入口（全站 `/` 快捷键）是**纯功能交互、零动效面**，不归 reveal 协议、不并入本 ADR 的任何引擎；作为第三个并列模块落站点层 `assets/js/mf-search-entry-engine.js`，自有 docstring、与 fastsearch.js 快照契约并列互指（ADR-0011 决策 3 / 工单 0052 决议③）。本 ADR 正文不改（历史记录）。

**2026-10-24 指针（三）（D1 阅读进度条）**：本协议的动效交互从三块扩到四块——新增引擎 `assets/js/mf-reveal/reading-progress.js`（阅读进度条，写 `--mf-progress`，量 `.post-content`，仅 posts 文章页渲染）。性质上它属本协议（滚动驱动的界面状态，非纯功能交互），故并入 mf-reveal 而非另立模块；契约定义处 = 该引擎文件头 docstring，行为测试 RGR-9/10/11 入 `tests/assert_reveal.mjs`，产物断言 B15 入 `tests/assert_site_contracts.py`。**不进本 ADR 正文**（历史记录）；若将来出现第二个「非滚动驱动的纯功能」搜索类入口，仍按 2026-10-23 指针（二）的判据另立模块。

**指针（2026-10-24，ADR-0013）**：浮层的开 / 关过场（opacity + transform，120ms）
**不归 reveal**——它属搜索协议的动效（检索交互），与「搜索交互不并入 reveal」
（本 ADR 决策 4 同款理由）一致；包在 prefers-reduced-motion: no-preference 内。
浮层是站点层独立 bundle（mf-search-overlay*），不经本协议的 js.Build。

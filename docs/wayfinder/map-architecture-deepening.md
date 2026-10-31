---
id: map-architecture-deepening
title: 架构深化图（候选 ③④⑤⑥）
labels: [wayfinder:map]
status: closed
created: 2026-10-27
closed: 2026-10-31
---

# 架构深化图（候选 ③④⑤⑥）

## Destination

把架构从现状深化到四件落地状态，使相关模块**可测试、AI 可导航**：① **文章卡片单模块**（一处实现、多消费面，不再两处各写一份）；② **注册缝下沉到 app.js**（引擎无 import 副作用，注册点唯一）；③ **删除死面**（配置 + CSS 的零读取点面）；④ **CSS 影子契约加 parity 门**（JS 写入的 class / 自定义属性与 CSS 消费侧不得静默漂移）。**含施工与收口**：施工随票推进，收口票统一产出 ADR、术语与导航同步、handoff。

## Notes

- **出处**：架构评审候选 ③④⑤⑥（improve-codebase-architecture，2026-10-25；报告属 epoch 性资产，关键锚点已抄写进本图与工单，不依赖该文件存活）。前图 `map-featured-type-guard.md` 的 Out of scope 曾把四条记为「各自独立目的地，不随本图合并或顺带」——本图经项目负责人 2026-10-27 指令把这四条**合并为一个目的地**，理由：四条共享同一批文件与同一套断言，分图会让同一处代码被四张图反复触碰。
- **终点含施工**（项目负责人 2026-10-27 拍板）：与 wayfinder 默认「只产决策」不同，本图**把施工纳入**——决策票决议落定即施工（同票或紧随批次，Resolution 里记施工与验证），收口票负责 ADR / 术语 / 导航 / handoff。目的：目的地写的是架构状态本身（「深化到 X，使该模块可测试」），这种状态只能由落地产物证明。
- **工单纪律**（项目负责人开图时明确，2026-10-27）：每张工单是**待决策问题**、不是施工任务；一次会话最多解决一张（research 除外）；地图是索引不是仓库，决策只存在于工单。
- **死面范围已定**（项目负责人 2026-10-27）：**配置 + CSS** 两类。模板可达性与 fork 形态不重开（0027/0029 已裁）、静态资产与 i18n 键不纳入、悬空 `google_analytics.html` 调用不处理。
- **例外记录（2026-10-27）**：经项目负责人指示，本轮对「0079 五轴」（约束 / 依赖 / 模块形状 / seam 藏什么 / 测试存活）做了一次**跨票质询**，同场锁定 0080 / 0081 / 0083 全部决策 + 0082 / 0084 部分决策——「一会话一票」纪律的例外，同 `map-featured-type-guard` 0074–0077 先例。
- **决议与施工分离（本图约定）**：本图含施工，故**决议已定但未施工的票保持 `open` + `assignee: agent`**（不是 frontier、不算完成），Resolution 段首行标明「决议已定，施工未开始」；施工完成并验证后才 `status: closed` 并进 Decisions so far。
- **收口（2026-10-31）**：**10/10 票 closed**（0079–0088），frontier 空 = 目的地到达；决策集耐久化于 **ADR-0016**（四章 20 条，各注工单号），ADR-0007 / 0008 各加指针；收口 handoff 见 `docs/handoffs/2026-10-31-architecture-deepening-closure.md`。
- **PR① 已施工（2026-10-28）**：0080–0084 五票 closed，施工与验证见各自 Resolution；验证基线 = site **185/185** · npm **9+28+41** · sop **105/105** · 生产构建 **0 WARN** · 无 localhost 泄漏。
- **PR② 已施工（2026-10-31）**：0085–0088 四票 closed——死面删除（−196 行、零断言改动）+ parity 门（RGR-14 三节）+ ADR-0016 收口。验证 = site 185/185 · npm 13+31+41 · sop 105/105 · 构建 0 WARN。
- **已锁定并施工的决策（PR② + 收口，详情见各票 Resolution）**：
  - [0085](tickets/0085-dead-surface-criteria-and-scope.md) — 判据 = 四面零引用 + 三类白名单（构建期生成 / 运行时拼接 / 渲染器产出）；配置侧删零读取点与注释遗留键、**恒等默认保留**（`defaultTheme` 留，`socialIcons` 删）；粒度 = 文件 + 块级、**不加死面守门**；删块连带查 `var(--x)` 链；**先删死面、再上 parity 门**。
  - [0086](tickets/0086-css-shadow-contract-token-set.md) — 清单 = **源码双向抽取 + 白名单**（不手写 registry：会成为第二契约定义处）；方向 = 双向、范围 = **只 class 与 CSS 变量**（`aria-*` / `inert` / `hidden` 不进）；已知限制 = 只守存在性、不守语义漂移。
  - [0087](tickets/0087-parity-gate-placement-strength.md) — 落点 = `assert_reveal.mjs` 新节、强度 = 测试红（构建期 `errorf` 要在模板里正则解析 JS，不可维护）；失败消息按方向两种、带四处定位；新引擎零登记（抽取自动覆盖）。
  - [0088](tickets/0088-closure-adr-terminology-navigation.md) — 一份 **ADR-0016**（18–22 条，各注工单号）；0007/0008 加指针；术语只收「文章卡片」；AGENTS 三行 + 两坑点；施工 = **两个 PR**（① 呈现层收敛 ② CSS 契约治理，顺序即依赖）；回滚点：类名与 `:has()` 同进同退、PR② 逐块删每块跑一次 site 套件。
- **现状事实锚点（排图日自查，待 0079 确认并补全）**：
  - **卡片**：`layouts/index.html:126-143`（`article.mf-post`：无 cover、无草稿标记、无 hideMeta 守卫、摘要不过 `Truncated` 判断）vs `themes/maplemod/layouts/_default/list.html:57-85`（`post-entry` / `first-entry` / `tag-entry` 三变体：有 cover、草稿 SVG、hideMeta 守卫、`featured-badge`）；两处都调 `post_meta.html`（compact）与 `featured-badge.html`。**测试锚点（2026-10-27 更正）**：`assert_site_contracts.py` 有 **8 条断言直接锚类名**（`parse_card_badges` 三面 × 2 + 首页 × 2），另 `assert_post_grid_empty` 锚 `mf-posts` 容器、`assert_theme_transition` 用正则锚 `.post-entry { --card-motion }`；`entry-link` 锚点可存活。**三处字段差异当前全不可观测**（全站无 cover、草稿不进生产、无人设 `hideMeta`）。
  - **注册**：三个引擎在模块底部各自 `autoInit()`（`scroll-in.js` / `filter.js` / `reading-progress.js` 尾部），import 即产生副作用；`assets/js/mf-reveal/app.js` 仅 3 行 import、零注册逻辑；搜索浮层另有装配入口 `assets/js/mf-search-overlay.js`（`import '@params'` + 两引擎）；测试以 `dom.loadFresh()` 直载引擎文件（`assert_reveal.mjs` / `assert_search.mjs`），依赖 import 副作用完成注册。
  - **死面**：`themes/maplemod/assets/css/common/archive.css`（44 行）与 `profile-mode.css`（43 行）零 markup 引用；custom.css + 主题 CSS 共 251 个类名，粗扫 **42 个零引用**，其中 chroma / highlight 类（`c1` `cm` `kc` `lnt` `linenodiv` 等）是构建期生成、属**假阳性**——判据必须排除构建期生成类与运行时拼接类。
  - **影子契约**：JS 写入 `is-in`（scroll-in / filter）、`is-hidden` + `--mf-i`（filter）、`--mf-progress`（reading-progress）、`aria-pressed`、`inert`、`hidden`（overlay）；CSS 侧消费 `.reveal` / `.is-in` / `.is-hidden` / `--mf-progress` / `--mf-i` / `.mf-index` / `.mf-search-overlay`。契约的**定义处是引擎文件头 docstring**，CSS 只是一份**无门的影子拷贝**。
- **闭卷 ADR**：0002（no-js 渐进增强基线）、0007（reveal 协议：DOM 契约定义处=引擎 docstring、js.Build 加载、`extend_footer` 单入口）、0008（分层判据：视觉/骨架→主题层，内容策略/数据结构→站点层；两层不得同相对路径）、0009/0015（精选链：卡片含 `featured-badge` 时不得绕过徽标契约）、0012（徽标三面、谓词同源契约独立）、0014（自测先于契约红的先例与已知差异）。
- **测试总原则**：Hugo 无模板单测 → build-then-assert；fixture 基建单份（不新开第四套构建）；fixture 日期一律过去日；Hugo 0.164 语义编写（CI 钉版）。
- **环境注意（历图传承）**：本 shell 的 grep 对 `\|` 交替失效——内容搜索一律用 Grep 工具；safe-delete 每轮删除预算 5000；单命令约第 6 个 node 进程会被 kill（137），变异测试分批跑。
- 用户是项目负责人：HITL 工单必须实时对话解决，agent 不得自答；事实自己查，决策问用户；一次一问，先给推荐答案。
- 术语以根目录 `CONTEXT.md` 为准；本图可能新增「文章卡片」「注册缝」「死面」「影子契约」等词条（收口票 0088 裁定）。

## Decisions so far

<!-- 索引：每个已决工单一行 gist + 链接；决策详情只存在于工单，此处不重述。 -->

- [文章卡片单模块的消费面与差异语义](tickets/0080-card-module-surfaces-and-divergence.md) — 一套类名·视觉零 diff（两套 CSS 本就成对等价，9 组双写合并）；首页/section/term 三面同卡；`first-entry` 删（不可达）；三处差异**不参数化**，统一「总是执行、条件自守」。施工补：主题卡 `margin-bottom` 在首页清零以保原样。
- [卡片单模块的层归属、命名与入参契约](tickets/0081-card-module-layer-naming-interface.md) — 主题层 `post-card.html`、零参数（只收 page）；**父容器契约载重**：`main:has(> .post-card)` 靠「卡片是否 main 直接子元素」区分面，类名统一后旧判别器消失，故改直接子选择器 + 三条深度断言。
- [卡片单模块的测试缝与产物守门](tickets/0082-card-module-test-seam.md) — 新增 `assert_post_card`（第十六类，22 条）+ `content-card` fixture 四篇；解析唯一实现 `parse_cards`；类名只走一个常量；**跨面等价是「单模块」唯一直接证据**；五条变异全部可定位地红。附带抓到「反向断言在解析为空时假绿」并补前置。
- [注册缝的形态与 API](tickets/0083-registration-seam-shape.md) — 对齐搜索入口的装配式：引擎去 `autoInit`、`app.js` 持 `ENGINES` 表显式挂载、逐个 `try/catch`；选择器留引擎（`filter` 因此导出 `mountFilter` 而非 `initX`）；顺序无关。
- [注册缝改造后的测试加载面与降级语义](tickets/0084-registration-test-seam.md) — `loadMounted` helper + 11 处改造；**RGR-13 从源码扫描改为行为断言**（装三类挂点、载 `app.js`、验三个副作用）；`scroll-in` 内部 fail-open（异常走「无 IO」同一条路）；计数 9+28+41。

- [死面的判据与删除边界](tickets/0085-dead-surface-criteria-and-scope.md) — 四面零引用 + 三类白名单（构建期生成 / 运行时拼接 / 渲染器产出）；删整文件 2 个 + 选择器块 23 处（−196 行），chroma/highlight 18 类走白名单；**删除笔零断言改动**（删完仍全绿 = 没删到活的）；不加死面守门。
- [CSS 影子契约的 token 清单与 parity 方向](tickets/0086-css-shadow-contract-token-set.md) — 源码双向抽取、不写 registry；**反向收窄到 `is-*` 六类、白名单为空**（mf-* 视觉类不进反向，否则等于死面守门）；抽取器独立 `tests/tokens.mjs`、带 file:line；首跑抓到「模板条件类写在动作外」的抽取 bug。
- [parity 门的落点与强度](tickets/0087-parity-gate-placement-strength.md) — `assert_reveal.mjs` 的 RGR-14 三节（空集前置 / 正向 / 反向），强度 = 测试红，消息带四处定位；变异：抹 CSS 消费点 → 正向红，删模板生产者 → 反向红。
- [收口：ADR 切分、术语、导航与施工节奏](tickets/0088-closure-adr-terminology-navigation.md) — 一份 ADR-0016（四章 20 条）；0007/0008 指针；术语只收「文章卡片」；AGENTS 三行 + 坑点 17/18；PR② 两笔（先删后门）。

- [架构深化四区现状事实底座（盘点）](tickets/0079-architecture-deepening-facts.md) — 未单独成文：五项事实在施工中逐条查实，以「指针表 + token 矩阵」收口；矩阵由 `tests/tokens.mjs` 现算，8 行即全部（正向 0 违规、反向 0 孤儿）。

## Not yet specified

<!-- 雾区：在目的地内、但还无法精确表述的问题。随 frontier 推进毕业为工单。 -->

- **已消解**（[0080](tickets/0080-card-module-surfaces-and-divergence.md) 决议）：「卡片收敛后的视觉等价性要求」——一套类名、视觉零 diff（两套 CSS 本就成对等价），守门靠「类名一处常量 + 类名↔CSS 落地牙」，不引入像素回归。
- **已消解**（[0083](tickets/0083-registration-seam-shape.md) 决议）：「两套装配形态的统一度」——reveal 对齐搜索入口的装配式，搜索侧不动（`@params` 是构建期注入，与 DOM 挂载是两件事）。
- **已消解**（[0085](tickets/0085-dead-surface-criteria-and-scope.md) 决议）：「CSS 变量链的连带断裂」——删块必须连带查 `var(--x)` 引用链：只被死块引用则一并删、仍被活块引用则保留。
- **已消解**（[0086](tickets/0086-css-shadow-contract-token-set.md) 决议）：「token registry 会不会变成第二个契约定义处」——不手写 registry，改源码双向抽取，docstring 仍是唯一定义处（ADR-0007）。
- **已消解**（[0088](tickets/0088-closure-adr-terminology-navigation.md) 决议）：「四区的施工与 PR 节奏」——两个 PR（呈现层收敛 / CSS 契约治理），顺序即依赖，回滚点已登记。

## Out of scope

- **重开已锁 ADR**（0002 no-js 基线 / 0007 reveal 协议与 docstring 定义处 / 0008 分层判据 / 0009·0015 精选链 / 0012 徽标 / 0014 自测模式）：认为错了先提重审（工程纪律 2），不随本图默认推翻。
- **模板 partial 可达性与 fork 形态**（0027/0029 已裁）：含悬空 `google_analytics.html` 调用（主题 README 明确「保留」）、未用 partial、`themes/maplemod/images/*`——本图不重开。
- **静态资产与 i18n 键清理**：2026-10-27 拍板，死面范围 = 配置 + CSS 两类，不含 `static/` 与 `i18n/zh-cn.yaml` 的零消费键。
- **视觉重设计**（卡片改版、配色、排版重构）：本图只做**等价收敛**，不借机改版。
- **新消费面**（新增卡片形态、新增搜索面、新增 reveal 引擎）：新需求，新目的地。
- **内容与 SOP 管线**（0005/0008 已锁）、**搜索检索链路**（0010/0011/0013 已锁）：本图只碰卡片的呈现面、注册缝与 CSS/配置，不碰检索与内容派生。

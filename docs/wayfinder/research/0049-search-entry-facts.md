# 0049 研究：搜索入口现状事实底座

2026-10-23 · research（AFK）· 工单 [0049 搜索入口现状事实底座](../tickets/0049-search-entry-facts.md)

本图后续所有决策的事实前提。只查事实、不做决策。八项结论，逐条带文件:行号证据；外部惯例与项目事实分开标注。候选 8（搜索契约，ADR-0010）已锁定部分（index.json 六字段投影冻结、fastsearch.js docstring 为检索协议现状快照契约、fastsearch 不重写）不在此重新推导，本文只盘「入口 / 加载面 / 呈现层」相关事实。

---

## 1. search 页面

- `content/search.md:1-5`：front matter 仅三键——`title = "搜索"`（:2）/ `layout = "search"`（:3）/ `summary = "搜索站内文章"`（:4）。**无 `draft` 键**（默认 false，即发布态）；无 description；无 searchHidden；**front matter 无 outputs 覆盖**——JSON 输出只在站点级 `hugo.toml:189-190`（`[outputs] home = ["HTML","RSS","JSON"]`）作用于首页；search 页自身为默认 HTML 单输出，uglyURLs 下落盘 `/search.html`。
- `themes/maplemod/layouts/_default/search.html:18-22`：三挂点——`<div id="searchbox">`（:18）、`<input id="searchInput" autofocus placeholder="{{ .Params.placeholder | default (printf "%s ↵" .Title) }}" aria-label="search" type="search" autocomplete="off" maxlength="64">`（:19-20）、`<ul id="searchResults" aria-label="search results"></ul>`（:21）。search.md 未配 placeholder，实际渲染「搜索 ↵」。页头有标题 + 放大镜 SVG（:3-16）；description 为条件渲染（:11-15），search.md 无值故不出现。
- `themes/maplemod/assets/css/common/search.css:1-45`：46 行。覆盖 `#searchbox input`（:1-8）、`input:focus`（:10-12）、`#searchResults li`（:14-21）、`#searchResults`（:23-26）、`li:active` 按压反馈（:28-31）、`#searchResults a` 绝对定位铺满 li（:33-40）、`#searchResults .focus`（:42-45）。**覆盖范围：全站**——`head.html:56` 的 `resources.Match "css/common/*.css"` 无条件并入全站样式表，不限 search 页。

## 2. fastsearch 加载面

**加载条件**：`themes/maplemod/layouts/partials/head.html:77-90`——`{{- if (eq .Layout `search`) -}}`（:78）。即仅 `.Layout == "search"` 的页面；本站点即唯一 search 页（uglyURLs 下 `/search.html`）。**fastsearch 现仅在该单页加载。**

**preload 路径**：`head.html:79`——`<link crossorigin="anonymous" rel="preload" as="fetch" href="index.json">`。同目录相对（0046 施工期由上游 `../index.json` 修正，子路径部署下 `../` 会逃逸域名根 404）。

**js.Build 管线**：`head.html:80-89`——`resources.Get "js/fastsearch.js" | js.Build | resources.Minify`（:80，**无 params**：fuseOpts 参数位已删，见 fastsearch.js:10「js.Build 无 params——fuseOpts 参数位已删（0046 决议③）」；注意 0042 文档记的 `js.Build (dict "params" ...)` 已过时）；与 `fuse.basic.min.js`（:81）、`license.js`（:82）concat 为 `assets/js/search.js` 后 fingerprint（:84）。指纹分支 concat 序为 fuse → license → fastsearch（:84）；**非指纹分支（:87）序为 fuse → fastsearch——license.js 在 disableFingerprinting 时被丢弃**（现状未配置 disableFingerprinting，走 :84 分支，license 在内）。

**现状文件的加载面约束（事实）**：fastsearch.js 模块级 `document.getElementById` 无守卫（fastsearch.js:53-54）+ `sInput.onkeyup = ...` 直接赋值（:111）——若把本文件原样加载到没有 `#searchInput` 的页面，:111 抛 TypeError，后续全部绑定丢失。即 **fastsearch.js 现状不可原样搬到全站加载面**，任何「全站入口」设想都需先面对此点。

**全站 JS 恒加载面（现有机制）**：`themes/maplemod/layouts/partials/extend_footer.html:12-17`——`resources.Get "js/mf-reveal/app.js"`（:12；解析到站点层 `assets/js/mf-reveal/`，含 app.js / scroll-in.js / filter.js / reduced-motion.js 四文件，app.js:10-11 import scroll-in + filter，二者再各 import reduced-motion）→ `js.Build (dict "format" "iife") | resources.Minify | fingerprint`（:16）→ `<script ... integrity ... defer>`（:17）；入口缺失有 errorf 守卫（:13-15）。调用链：`baseof.html:39` partialCached footer.html → `footer.html:33` partial extend_footer.html；footer.html:1 条件为 `if not (.Param "hideFooter")`，content 目录无任何页面设 hideFooter（grep 零命中）→ **实际全站每页恒加载**。search 页自身也走 baseof（baseof.html:30-31 还特判 search layout 的 `body class="list"`），故 search 页同时挂 search.js 与 reveal 引擎两个脚本。这是「全站入口脚本」可复用的现有机制（与 fastsearch 的 head.html 管线同款，ADR-0007）。

## 3. 入口现状

**菜单项**：`hugo.toml:155-160`——`identifier = "search"` / `name = "搜索"` / `url = "/search.html"` / `weight = 6`。menu.main 共 9 个顶层项（:125-179，weight 1-10 无 8）。

**导航渲染面**：`themes/maplemod/layouts/partials/header.html:84-108`——`range site.Menus.main`（:85）渲染全部顶层项，无子菜单机制（Hugo 的 site.Menus.main 本就不含子项）；对 search 项特判：title 后缀 `" (Alt + /)"` + `accesskey=/`（:88-91，经 `(site.GetPage .KeyName).Layout == "search"` 识别）。渲染 9 项及顺序由 B9 钉死（`tests/assert_site_contracts.py:194-197` MENU_RENDERED_KEYS，含 `/search.html`）。

**键盘绑定**：`themes/maplemod/assets/js/fastsearch.js:142`——`document.onkeydown`，**挂在 document 的全局监听**；因脚本仅在 search 页加载，有效作用范围仅 search 页。键位：`Escape` 恒可重置（:155-156：清空输入与结果、焦点回输入框——位于结果门之前，无结果 / 焦点在框外时也响应）；`ArrowDown`/`ArrowUp` 受「结果可用且焦点在搜索框内」门控（:157-158、:159-178）在输入框与结果项间移动 focus；`ArrowRight` 点击当前项（:179-181）。逐字符检索在 `sInput.onkeyup`（:111）；type=search 的清除 x 走 `search` 事件 → reset（:136-139）。**「Alt + /」不在 fastsearch.js 里**——它是 HTML `accesskey` 属性（header.html:91），由浏览器实现（macOS 上 accesskey 实际组合为 Ctrl+Option+/），fastsearch 侧零参与、零测试。

**window.onload 的 focus 行为**：`fastsearch.js:59-88` 的 `window.onload` **只做 XHR 取 index.json**（:60-87），不做任何 focus。打开 search 页自动聚焦输入框来自 `search.html:19` 的原生 `autofocus` 属性（docstring 记 "autofocus"，fastsearch.js:14）。

## 4. 首页结构

`layouts/index.html` 区块编排（按文件实际顺序）：

1. **HERO**（`mf-hero`，:21-43：eyebrow「SRE · DevOps · AIOps」/ 主标题 / lede / 双按钮「浏览文章」「查看资源」/ 分类标签云）——仅第 1 页（:18 门控）；
2. **数据条**（`mf-spec`，:46-72：文章数 / 分类数 / 可下载产品数 / 最近更新月份，全部真实数据计算）——仅第 1 页；
3. **精选文章**（`mf-section` + `mf-rows` 索引行，:75-104；0 篇 featured 整块不渲染）——仅第 1 页；
4. **精选资源**（`mf-section` + `product-index.html` partial，:107-116；与产品页同数据同渲染）——仅第 1 页；
5. **最近更新 / 文章网格**（`mf-posts` 卡片，:121-145；补集为空整块不渲染）——每页都显示；
6. **分页**（`page-footer`，:147-158）；
7. **结尾 CTA**（`mf-cta-band`，:161-178）——仅第 1 页。

**无任何搜索相关区块或预留位**（hero 的双按钮是「浏览文章 / 查看资源」，无搜索入口）。

**`homeInfoParams`：hugo.toml 无此配置**（grep 零命中；`[params]` 下有 description（:48）、socialIcons（:69-75）等）。首页由站点层 `layouts/index.html` 全量覆盖（文件头 :1-5 注明「覆盖 PaperMod 的 _default/list.html」），主题 homeInfo 路径不参与渲染。

## 5. 契约现状

**fastsearch.js 文件头 docstring（:1-50）收录的入口相关条款，逐条**：

- **加载条件在契约里**（:8-10）：「加载（themes/maplemod/layouts/partials/head.html，仅 .Layout == "search" 时）：与 fuse.basic.min.js、license.js concat 为 assets/js/search.js 后 fingerprint；js.Build 无 params——fuseOpts 参数位已删（0046 决议③：无消费方的预留位不留）。」
- **DOM 契约**（现状快照定性，:12-13「快照式记录当前行为、非设计目标」）：读 `#searchbox > #searchInput`（autofocus / maxlength=64 / aria-label=search）（:14）与 `#searchResults`（aria-label=search results）（:15）；写 `#searchResults.innerHTML` 的 li 结构——「只渲染标题+链接，不显摘要、不显精选（与 0044「UI 无消费方」同理）」（:16-19）；`.focus` 类语义（结果项导航时加在 li 上，search.css 消费；焦点回输入框时加在 #searchbox 上，无 CSS 消费方）（:20-22）。
- **键盘语义**（:23-26）：「键盘（document.onkeydown 全局监听）：Escape 恒可重置（清空输入与结果、焦点回输入框——位于结果门之前，无结果 / 焦点在框外时也响应）；输入框获焦时先清理既有 .focus；ArrowDown/ArrowUp/ArrowRight 受「结果可用且焦点在搜索框内」门控（ArrowRight = 点击当前项）。」
- **点击热区**（:27-28）：`#searchResults a` 绝对定位铺满 li（search.css 消费）；li 的 post-entry / entry-header 类名无外部消费方。
- **XHR 路径**（:36-37）：「索引来源：XHR GET "index.json"（同目录相对——站点在子路径 /mapleFlow/ 下，上游的 ../index.json 会逃逸到域名根而 404，已实测；head.html 的 preload 同步同目录）。」
- **已知限制**（:40-44）：XHR 失败仅 console.log、JSON.parse 无 try/catch（索引损坏时静默失效）；no-js 下搜索页只剩空壳；reduced-motion 无运动面可降级。
- **测试归属**（:46-47）：「B11 三挂点产物断言（tests/assert_site_contracts.py）；jsdom 行为测试归工单 0047（未立）。」

**ADR-0010 原文摘录**（`docs/adr/0010-search-contract.md`，入口 / 加载条件 / 呈现层 / 第二个消费方相关）：

- 决策 1（:11）：「search 页面留 B11 守挂点；交付面（outputs JSON / preload / XHR 路径）写进投影 docstring。」
- 决策 2（:12）：「**featured 与 kind 不投影**——无消费方（fastsearch keys 不含、结果 UI 只渲染标题+链接）……truncate 200/320 为调值，仅文档不断言。」
- 决策 4（:14）：「fastsearch 治理为**独立「搜索协议」，现状快照式契约**——docstring 落 themes/maplemod/assets/js/fastsearch.js 文件头，收录挂点、.focus、li 结构、键盘语义、XHR 路径与失败行为……**fuseOpts 参数位删除**——无消费方的预留位不留……容错行为（XHR / JSON.parse 静默失效等）记录为已知限制，不承诺修复。」
- 决策 5（:15）：「**不立 jsdom 行为套件**……重写时新引擎按 mf-reveal 模式抽 ESM 可测模块，测试与新契约一起 TDD 出生。**产物断言盖上交付面**：search 页引用 search.*.js + 构件落盘 + fetch 同目录 index.json（锚 fixture 构建）。」
- Consequences 边界（:33）：「边界：重写 fastsearch 时才有的面（结果呈现深化 / 引擎形态 / 容错 UX）与**搜索入口新功能**，均不属本 ADR（见地图 Out of scope）。」——即入口形态是候选 12 的决策面，ADR-0010 显式让渡。
- 文件末尾 2026-10-23 指针段（:35）原文：「**2026-10-23 指针（重写与否的结论）**：**不重写 fastsearch**。理由是投入产出比：索引仅 17 条记录、引擎单文件、测试依赖只有 jsdom……若「结果可读性」成为真实需求，只改渲染层（摘要 / 标签），不动引擎；「引擎 ESM 化 + 容错 UX」长期挂起，触发条件是真被 XHR 静默失败咬到、**或出现第二个消费方**。届时按决策 5 的既定路径：新引擎与新契约一起 TDD 出生，本 ADR 的快照契约作为输入。」

## 6. 投影与呈现的字段面

- **投影六字段现状**（`layouts/_default/index.json:59-66`；docstring 字段表 :10-21）：`title`(.Title) / `permalink`(.Permalink) / `summary`(.Summary | plainify | htmlUnescape | chomp 后 truncate 200) / `content`（**同一 $summary** 再 truncate 320，与 summary 同源、不含正文） / `tags`(.Params.tags | default slice) / `categories`(.Params.categories | default slice)。产品条目同六字段（:82-89：title=name、permalink=产品页#id、content=三字段拼接、tags/categories 硬编码 ["产品"]）。字段集冻结为六项，featured / kind 不投影（0044 决议）。
- **Fuse keys 四字段**（`fastsearch.js:71-76`）：`['title','permalink','summary','content']`——与投影六字段的差集恰为 `{tags, categories}`（测试钉死：`tests/assert_site_contracts.py:172-174` 常量、:363-365 关系断言）。
- **结果 li 现渲染字段**（`fastsearch.js:120-123`）：每条结果仅 `${item.title}`（置于 `<header class="entry-header">` 内，带 `&nbsp;»`）+ `<a href="${item.permalink}" aria-label="${item.title}">`（CSS 绝对定位铺满 li）。**summary / tags / categories 均不渲染**——docstring 记为「只渲染标题+链接」快照（:16-19）。

## 7. 现有断言覆盖

`tests/assert_site_contracts.py` 中搜索相关断言全清单：

| 断言 | 位置 | 锚定构建 | 内容一句话 |
|---|---|---|---|
| `assert_search_index` | :329-338（调用点 :491，在 `assert_fixture` 内；dest=TMP/"fixture"，FIXTURE_CONFIG=hugo.toml,tests/hugo.test.toml，真实 content + fixture data） | **fixture 构建** | index.json 中 products.html# 锚点条目 `tags == ["产品"]`；无产品条目则红 |
| `assert_search_projection` | :341-385（调用点 :492） | **fixture 构建**（同上） | 每条记录恰为投影六字段；fastsearch.js 默认 keys 为四字段字面量（读主题层源码）；差集 == {tags, categories}；产品条目形态（title=name / permalink 锚点 / content 拼接）fixture 字面量；fastsearch.js 单副本守门（项目级 assets/js/fastsearch.js 不得存在） |
| `assert_search_artifacts` | :607-634（调用点 :493） | **fixture 构建**（同上；fixture 恒跑，`--quick` 也跑） | 0047 交付面三查：search.html 引用 `search.*.js` 构件 + 构件落盘 + 构件内 XHR 为同目录 `"index.json"` 且无 `"../index.json"` |
| `assert_search_fixture` | :568-604（dest=TMP/"search-fixture"，:580-581，POSTS_FIXTURE_CONFIG + `--contentDir tests/fixtures/content-search`） | **独立 fixture 构建** | 文章侧投影形态与三类排除：索引恰 2 条（fx-hidden / fx-archives / fx-search-page 均排除）；alpha summary==content 直写字面量；beta plainify 字面量；tags/categories 原样投影 |
| B11 三挂点 | :812-819（在 `assert_theme_contract` 内） | **真实数据构建**（`assert_real` :746 → :763；REAL_CONFIG=hugo.toml,config.production.toml；`--quick` 跳过真实构建即跳过本条） | search.html 含 searchbox / searchInput / searchResults 三个 id |
| 坏用例 search-missing-name / search-missing-summary | BAD_CASE_EXPECT :153-154；`assert_bad_cases` :659-677 | **坏 fixture 构建**（dataDir 覆盖，逐用例独立构建） | 产品数据缺 name / summary 时构建必须失败且错误含「搜索索引数据：… 缺少 name / summary」 |

**行为测试：零。** `tests/assert_reveal.mjs` 无任何 search 内容（grep 计数 0）；`package.json` 的 `test` 脚本只跑 `node tests/assert_reveal.mjs`（jsdom ^30.1.3 是唯一 devDependency，只服务 reveal）。

## 8. 外部惯例（轻量；外部常识，非本项目事实）

1. **GitHub 全站 `/` 或 `s` 聚焦搜索栏**——来源：GitHub Docs 官方键盘快捷键页（https://help.github.com/en/github/getting-started-with-github/keyboard-shortcuts，"Site wide shortcuts: S or / — Focus the search bar"）。同页 ⌘K 在 GitHub 是「编辑器内插入 Markdown 链接」而非搜索；GitHub 另有 Command Palette 提供快速操作入口。
2. **Cmd+K 命令菜单是文档站 / 工具站的常见模式**——来源：社区文章（SegmentFault 2022-09-29 https://segmentfault.com/a/1190000042559544：「Vercel GitHub Raycast Linear Framer……你敲一下 ⌘ + K 就能唤起」；CSDN cmdk 插件盘点 2025-10 https://blog.csdn.net/gitblog_00505/article/details/153304860）。属社区共识性描述，非任一站点的官方规范原文。
3. **Vercel 文档站的搜索快捷键**：未在公开页面查到官方明文（vercel.com/docs 为 JS 渲染，抓取未见快捷键说明）——**未查到（官方明示）**。其命令菜单风格被 cmdk 类库复刻（同来源 2）。
4. **Stripe**：docs.stripe.com 未查到官方明示的 docs 站搜索快捷键；其 Dashboard 页明示「press the question mark key (?) for a list of available keyboard shortcuts」（https://docs.stripe.com/dashboard/basics）——dashboard 非 docs 站本体，仅佐证「? 唤出快捷键面板」惯例。
5. **Chrome**：官方快捷键表（Windows/Linux 段）地址栏快捷键含 "Search from anywhere on the page — Ctrl + k or Ctrl + e" 与 "Jump to the address bar — Ctrl + l / Alt + d / F6"（来源：Google Chrome 帮助页 https://support.google.com/chrome/answer/157179 的转录 https://zhuanlan.zhihu.com/p/372891250；Google 原页折叠区未能直接展开，Mac 段未在转录中出现——**Mac 段待确认**）。即站点绑 Ctrl+K（Windows）会与浏览器「从页面任意处搜索」冲突。
6. **Safari**：Apple 官方快捷键页（https://support.apple.com/zh-cn/guide/safari/cpsh003/18.0/mac/15.0）全文**无 Command-K**；智能搜索栏（地址栏）= Command-L，页内查找 = Command-F。即 Safari 不默认占用 ⌘K（macOS 层 Spotlight 为 ⌘Space）——站点绑 ⌘K 在 Safari 无浏览器层冲突。
7. **`/` 键的常见用途**：除 GitHub 外，大量站点用 `/` 聚焦站内搜索（社区常识，无单一权威源，未逐站考证）。其代价：输入框聚焦时 `/` 是正常字符输入——需在 keydown 里门控「焦点不在输入元素」才可安全拦截。

---

## 缺口清单

（现有断言未覆盖、且候选 12 需要决策的问题面——给排图用，非给施工用。）

1. **入口形态无契约定义处**：菜单项 / accesskey / autofocus 的存在均无 docstring 或断言锚定——B11 只守三个 DOM id（:812-819），不守入口面；header.html:90-91 的 accesskey 与 title 后缀零测试。
2. **fastsearch.js 不可原样全站加载**：模块级 getElementById 无守卫（:53-54）+ sInput.onkeyup 直接赋值（:111），加载到无 #searchInput 的页面即抛 TypeError——「全站入口脚本」复用 fastsearch 的先决改造（守卫或 ESM 化）无决策、无测试缝。
3. **加载条件无守门**：`.Layout == "search"` 除 fastsearch.js docstring（:8-10）外无第二处记录，且无断言守「仅 search 页加载」——改加载面无牙。
4. **快捷键冲突面无盘点**：accesskey=Alt+/ 的浏览器实际组合（macOS 为 Ctrl+Option+/）无测试或文档记录；与候选新快捷键（Cmd+K 等）的冲突（对照第 8 项 Chrome Ctrl+K 事实）无本项目侧盘点。
5. **首页无搜索区块 / 预留位**：若考虑首页常驻框，layouts/index.html 无 seam、无断言、无 CSS 预设——search.css 只覆盖 #searchbox/#searchResults 且现状全站加载（head.html:56），复用是否需拆分无决策。
6. **呈现层字段面**：li 只渲染 title+permalink 是 docstring 快照（:16-19）无断言；若改渲染（摘要 / 标签），「改投影 = 三处同步」（投影 docstring / fastsearch keys / 差集断言）纪律是否触发、标签进 keys 后差集断言如何改，无决策。
7. **「第二个消费方」触发条件无观测面**：ADR-0010:35 指针把「出现第二个消费方」列为重写触发条件，但入口改造若引入第二个加载 fastsearch / 消费 index.json 的面，无任何断言或文档会提示「重写条件已触发」。
8. **no-js 基线**：搜索页 no-js 下只剩空壳（docstring:42 记录为已知限制）；入口若前移（如首页常驻框），no-js 下的呈现面无决策。
9. **行为测试为零对入口决策的影响**：任何入口 / 键盘新行为都没有可挂断言的家（jsdom 套件 0047 决议不立；npm test 只跑 reveal）——候选 12 若改入口行为，测试缝方案无决策。

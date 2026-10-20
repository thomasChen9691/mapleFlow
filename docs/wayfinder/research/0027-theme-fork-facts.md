# research/0027 —— 主题 fork 事实底座（本地盘点）

> 工单：[tickets/0027-theme-fork-facts.md](../tickets/0027-theme-fork-facts.md)（地图：map-theme-fork.md，候选 6 主题 fork 图）
> 产出：2026-10-20，research 子代理只读盘点（`git status/log/diff/show`、`git add --dry-run`、`grep`、`file`），未改动任何文件与 git 状态。
> 用途：候选 6 各决策工单的事实底坐。本文只产事实，不产决策；未核实处以「未验证」标注。

## 1. 子模块状态

**结论**：子模块 gitlink 干净、工作区 116 个文件 dirty 且**已坐实为纯 CRLF 行尾差异**（非内容改动）；`.git` 是 gitlink 文件；LICENSE/README/go.mod/theme.toml 均在位。

| 事实 | 证据 |
|---|---|
| gitlink = 6c5a8f6b055cf6cfd9fb9f763a18f23d1044b6ab，与 HEAD 一致 | `git submodule status` → `6c5a8f6… themes/PaperMod (v8.0-55-g6c5a8f6)`（无 `+`/`-` 前缀）；`git ls-tree HEAD themes/` → `160000 commit 6c5a8f6b… themes/PaperMod` |
| 外仓 `git status` 标 ` m themes/PaperMod`（小写 m = 子模块内容 modified，gitlink 未动） | `git status --short themes/PaperMod` |
| `git diff themes/PaperMod` 显示 `1 file changed, 0 insertions(+), 0 deletions(-)`；numstat `0 0` | 上述命令 |
| 子模块内部 116 个文件 M，6025 insertions / 6025 deletions（行数对称 = 全行替换的典型特征） | `git -C themes/PaperMod diff --stat`（末行：`116 files changed, 6025 insertions(+), 6025 deletions(-)`）；完整名单含 `.github/*`、`LICENSE`、`README.md`、`assets/css/**`、`i18n/*.yaml`、`layouts/**`、`theme.toml` 等 |
| **纯行尾实锤**：`git -C themes/PaperMod diff --ignore-cr-at-eol` 输出为空（0 个文件）；工作区文件 `file` 全部报 CRLF，而 `git show HEAD:theme.toml` 为 LF | `file themes/PaperMod/theme.toml` → `ASCII text, with CRLF line terminators`；对 `LICENSE`、`README.md`、`layouts/_default/single.html` 同样成立 |
| `.git` 形式：**文件**（gitlink），内容 `gitdir: ../../.git/modules/themes/PaperMod` | `file themes/PaperMod/.git` → `ASCII text`；`cat themes/PaperMod/.git` |
| LICENSE 存在：MIT，版权行 `Copyright (c) 2020 nanxiaobei and adityatelange` / `Copyright (c) 2021-2026 adityatelange` | themes/PaperMod/LICENSE:3-4 |
| README.md 存在（4901 字节） | ls themes/PaperMod |
| go.mod：`module github.com/adityatelange/hugo-PaperMod` / `go 1.12` | themes/PaperMod/go.mod |
| theme.toml：`name = "PaperMod"`、`license = "MIT"`、`min_version = "0.146.0"`；**无 version 字段**（版本语义来自 git tag：v8.0 之后第 55 个提交 = v8.0-55-g6c5a8f6） | themes/PaperMod/theme.toml:5,6,44 |
| 子模块 HEAD commit = `6c5a8f6 Update LICENSE`（父 `7d061d5`、`1cf5327`） | `git -C themes/PaperMod log --oneline -3` |

**遗留疑点（未验证）**：dirty 的 CRLF 从何而来（疑某次 Windows 侧 checkout 或编辑器写入）；交接文档所述「gitlink 未变」已复核属实。

## 2. 主题面可达性盘点

**结论**：首页/文章/list/taxonomy/search/404 均可达且由主题（或站点覆盖）实际渲染；**archives 页不可达**（无 content 页声明 `layout: archives`、菜单无入口、`public/` 无产物）；**6 个主题短代码在 content 中零引用**。

| 面 | 模板链 | 可达性 | 证据 |
|---|---|---|---|
| 首页 HTML | 站点 `layouts/index.html`（net-new，覆盖 Hugo home 查找顺位的主题 `_default/list.html`）+ 站点 `baseof.html` → 主题 `head/header/footer.html` | 可达 | hugo.toml:178-182; `find layouts -type f` 无主题同名 index.html；public/index.html 存在 |
| 首页 RSS / JSON | 站点 `layouts/_default/rss.xml`、`layouts/_default/index.json`（同名覆盖主题同名文件） | 可达 | hugo.toml:270-271 `[outputs] home = ["HTML","RSS","JSON"]`；public/index.xml、public/index.json 存在 |
| 文章 single | 主题 `_default/single.html` + 站点 `_default/baseof.html` + 站点 `partials/post_meta.html`（partial 查找链站点优先） | 可达 | 5 篇手写文章 + 6 篇派生（_content.gotmpl）；public/posts/*.html |
| 分区 list（/posts/） | 主题 `_default/list.html`（站点无同名覆盖） | 可达 | public/posts/ |
| taxonomy 列表（/categories/ /tags/） | 主题 `_default/terms.html` | 可达 | hugo.toml:190-229 菜单；public/categories/index.html、public/tags/index.html |
| taxonomy 词表页（/categories/运维/ 等） | 主题 `_default/list.html` | 可达 | public/categories/运维.html 等；菜单 ops/k8s/docker/aiops 子项指向它们 |
| **archives** | 主题 `_default/archives.html` | **不可达** | `grep -rniE 'archive' content/` 仅命中 layouts 注释与 index.json 过滤行，**无任何 content 页设 `layout: archives`**；菜单无 archives 项（hugo.toml:178-260 全清单核对）；`ls public/` 无 archives.html |
| search | 主题 `_default/search.html` + 站点 baseof | 可达 | content/search.md:3 `layout = "search"`；public/search.html；菜单 url=/search.html（hugo.toml:237-241） |
| 404 | 主题 `404.html`（`{{ define "main" }}` 由 baseof 兜底，站点 baseof 加 no-js） | 可达 | public/404.html |
| robots.txt | **static/robots.txt 遮蔽主题 layouts/robots.txt** | 站点版生效 | static/robots.txt 内容 = public/robots.txt（`Allow: /` + 写死的生产 sitemap URL）；主题模板生产分支输出的是 `Disallow:`（空值），与产物不符即被遮蔽的证据 |

**主题短代码引用统计**（`grep -rnoE '\{\{[<%][ ]*[a-zA-Z_"]+' content/` 全文短代码调用只有两个名字）：

| 短代码 | content/ 引用次数 |
|---|---|
| collapse | 0 |
| figure | 0 |
| inTextImg | 0 |
| ltr | 0 |
| rawhtml | 0 |
| rtl | 0 |
| product-index（站点自有） | 1（content/products.md:50 `{{< product-index >}}`） |
| ref（Hugo 内建，非主题） | 6 |

## 3. 主题 partial 触达盘点

**结论**：25 个主题自有 partial 中 **9 个可达**（其中 opengraph/schema_json/twitter_cards/get-page-images 仅生产构建可达），**16 个不可达**；另有 1 个**悬空引用**（google_analytics.html 在主题中不存在但被 head.html 调用）。

可达栏：

| partial | 调用链（主题内引用点） | 备注 |
|---|---|---|
| head.html | 主题 baseof.html:16 / 站点 baseof.html:28 | 站点 baseof 复用主题 head |
| header.html | 主题 baseof.html:24 / 站点 baseof.html:36（partialCached） | 渲染 site.Menus.main 全树（header.html:85） |
| footer.html | 主题 baseof.html:28 / 站点 baseof.html:40（partialCached） | 读 site.Copyright（footer.html:4） |
| extend_head.html | head.html:197 | **站点覆盖生效**（no-js→js 内联脚本，layouts/partials/extend_head.html:9-15）；主题原版是注释占位 |
| extend_footer.html | footer.html:33 | **站点覆盖生效**（js.Build 加载 mf-reveal 引擎，layouts/partials/extend_footer.html）；主题原版是注释占位 |
| post_meta.html | 主题 list.html:89 / single.html:24、archives.html:70；站点 index.html:133 | **站点覆盖生效**（时区显式格式化，layouts/partials/post_meta.html:18） |
| author.html | head.html:24、post_meta.html:16 | site.Params.author="thomasChen"（hugo.toml:48）使其激活 |
| anchored_headings.html | list.html:36 / single.html:40（守卫仅 `disableAnchoredHeadings`，站点未设） | 产物实证：public/posts/*.html 有 `<a hidden class=anchor…>` |
| cover.html | list.html:68 / single.html:32 | 可达但渲染空：全站无页设 cover.image，[params.cover].image=""（hugo.toml:126-127） |
| templates/opengraph.html | head.html:202（生产守卫内） | **站点覆盖生效**（ogImage 兜底，见 §4） |
| templates/twitter_cards.html | head.html:203（生产守卫内） | 站点无覆盖，用主题版 |
| templates/schema_json.html | head.html:204（生产守卫内） | 站点无覆盖 |
| templates/_funcs/get-page-images.html | opengraph.html:47、schema_json.html、twitter_cards.html:9 | 经生产守卫链可达 |

不可达栏：

| partial | 引用点 | 不可达原因（证据） |
|---|---|---|
| breadcrumbs.html | list.html:9 / single.html:5 | 内部守卫 `.Param "ShowBreadCrumbs"`（breadcrumbs.html:1），站点与全部页面均未设 |
| comments.html | single.html:61 | `.Param "comments"` 未设；且模板本体只有两行注释、零输出 |
| edit_post.html | single.html:26 | `editPost.URL` 未设（edit_post.html:1） |
| post_canonical.html | single.html:27 | `.Params.canonicalURL`/`ShowCanonicalLink` 未设（post_canonical.html:1） |
| post_nav_links.html | single.html:53 | `.Param "ShowPostNavLinks"` 全站未设；双重死：即使调用，`mainSections` 也未设（post_nav_links.html:1）→ 空 |
| share_icons.html | single.html:56 | 调用点守卫 `site.Params.ShowShareButtons` 未设（single.html:55）；`reorderShares = []`（hugo.toml:144）主题零引用 |
| toc.html | single.html:34 | `.Param "ShowToc"` 未设；`showTableOfContents = true`（hugo.toml:132）**不是**该键名（见 §5） |
| translation_list.html | single.html:25 / search.html:18 | 守卫 `.IsTranslated`（translation_list.html:1）；单语言站（defaultContentLanguage=zh-cn，无译文） |
| home_info.html | list.html:51 | 双杀：`site.Params.homeInfoParams` 整块注释（hugo.toml:81-88）+ 首页由站点 index.html 接管不再走主题 list.html |
| index_profile.html | list.html:4 | 双杀：`profileMode.enabled` 未设（list.html:3）+ 首页自定义 |
| social_icons.html | home_info.html:10 / index_profile.html:35 | 两个父 partial 均不可达 |
| svg.html | social_icons.html:5 | 父不可达 |

**悬空引用（重要）**：head.html:201 调用 `partial "google_analytics.html"`，但主题 `git ls-files layouts/partials/` 与全仓 find 均**无此文件**。经验证（Hugo v0.167.0，/tmp 最小复现沙箱）：生产构建**不报错**，缺失 partial 静默渲染为空、无 ERROR/WARN。既有 public/ 产物（含 og: 标签，证明生产分支执行过）与 CI 绿色记录与此一致。**在 Hugo 0.164.0（CI 钉版）上的行为未验证**——若 0.164 对缺失 partial 报错，则须复查；本地 0.167 实证不报错。

## 4. 覆盖面对应表

| 站点 layouts/ 文件 | 主题同名文件？ | 关系与差异要点 |
|---|---|---|
| `_default/baseof.html` | 有 | **近逐字覆盖 + 同步义务（ADR-0002 点名）**：唯一实质差异是 3 处 `<html …>` 标签加 `class="no-js"`（站点版 :20/:22/:24，主题版 :8/:10/:12 无）；头部加了大段注释。版本守卫句（`lt hugo.Version "0.146.0"`）两版相同 |
| `_default/index.json` | 有 | **语义重写（P2-6/P2-7，非逐字）**：content 字段由整篇正文改为截断摘要（truncate 200/320）；新增 tags/categories 字段；过滤语义保留（跳过 searchHidden/archives/search）；新增产品段（site.Data.products → `/products.html#<id>` 锚点） |
| `_default/rss.xml` | 有 | **语义重写（P2-8，非逐字）**：首页订阅源限定 `Type=posts`（站点版 :11），不再混入 about/products 等独立页；删除主题的 site.Author 弃用分支与 warnf；`$authorName := site.Title`（站点版 :21，主题版按 author map/name 推导）；删除 `<image>` 块（site.Params.images 未用）与逐条 item 的 search/archives 过滤 |
| `index.html` | **无**（主题只有 `_default/list.html`） | **net-new**：首页完整自定义（HERO/数据条/精选/CTA/分页），调用站点自有 product-* partial 与 post_meta 覆盖 |
| `partials/extend_head.html` | 有（主题版 = 4 行注释占位） | **net-new 内容**：no-js→js 内联交换脚本（:9-15） |
| `partials/extend_footer.html` | 有（主题版 = 3 行注释占位） | **net-new 内容**：`resources.Get "js/mf-reveal/app.js"` → js.Build(iife) → Minify → fingerprint，缺文件即 errorf |
| `partials/post_meta.html` | 有 | **近逐字覆盖 + 同步义务（AGENTS.md:133 点名，但 ADR-0002 文本漏列）**：唯一实质差异是 title 属性由裸 `.Date` 改为 `.Date.Format "2006-01-02 15:04:05 -0700"`（站点版 :18 vs 主题版 :4），消除「构建机时区决定输出字节」 |
| `partials/product-state.html` | 无 | net-new（ADR-0004 产品状态模块，纯计算 + 契约 errorf） |
| `partials/product-items.html` | 无 | net-new（数据准备 seam，唯一读 hugo.Data.products 处 + kind 封闭词表门禁） |
| `partials/product-index.html` | 无 | net-new（纯渲染 seam，items/uid 必填） |
| `partials/templates/opengraph.html` | 有 | **近逐字覆盖**：唯一实质差异是 og:image 兜底链——主题无页内图时直接不输出 og:image；站点版在 `partial "_funcs/get-page-images"` 为空时回退 `site.Params.ogImage`（站点版 :47-52 的 `{{- else }}{{- with site.Params.ogImage }}` 分支）。注：该 partial 仅生产构建被 head.html:202 调用，dev 构建整块不执行 |
| `shortcodes/product-index.html` | 无 | **net-new**：主题 shortcodes/ 仅有 collapse/figure/inTextImg/ltr/rawhtml/rtl 六个；站点短代码是 product-items/product-index 两 seam 的包装 |

站点**未**覆盖的主题面（fork 时原样继承）：head/header/footer/single/list/terms/search/404/archives/render-image/robots.txt/index.json 之外的其余 `_default` 模板、6 个主题短代码、i18n/zh.yaml、assets/**。

## 5. 站点配置消费面

逐一 grep themes/PaperMod/layouts 的结果（读取点均为主题文件:行号）：

| hugo.toml 参数 | 主题是否读取 | 读取点 / 说明 |
|---|---|---|
| `theme = "PaperMod"` (:23) | — | Hugo 核心机制 |
| `defaultTheme = "auto"` (:42) | ✅ | baseof.html:6；head.html:117/155/163/186 |
| `author = "thomasChen"` (:48) | ✅ | author.html:1；post_meta.html:15/16；rss.xml:3,18（主题版） |
| `description` (:49) | ✅ | head.html:21-23；schema_json.html:6；twitter_cards.html:15 |
| `avatar = "img/avatar.svg"` (:50) | ❌ **零读取**（主题 layouts 全目录 0 命中；AGENTS.md:134 表格外的死配置，about.md 用内联 SVG） |
| `socialIcons` (:91-99) | ⚠️ 仅 social_icons.html:2，而 social_icons **不可达**（§3）→ 实际死配置；email/github 实际经 menu.main 生效 |
| `[params.assets].favicon` (:102-103) | ✅ | head.html:93-98（逐个 favicon 变体，其余走默认名） |
| `customSyntaxHighlighting = false` (:106) | ❌ **零读取**（高亮实际由 Hugo `[markup.highlight]` 核心接管，hugo.toml:160-168） |
| `stickyNav = true` (:110) | ❌ **零读取**（主题 layouts 与 assets/css 均无 sticky 相关命中；导航吸顶由 CSS/media 行为决定） |
| `reorderNavItems` (:115) | ❌ **零读取**——**已复核确认为真**：`grep -rn reorderNavItems themes/PaperMod/layouts` 0 命中，AGENTS.md:66 亦记载「已 grep 主题全目录 0 命中」 |
| `collapseNavItems` (:118) | ❌ **零读取**（layouts/assets/css/js 全目录仅 `border-collapse` 一处 CSS 属性命中；移动端折叠为 CSS 实现） |
| `rss = true` (:64) | ❌ **零读取**（RSS 链接由 head.html:102 `.AlternativeOutputFormats` 经 `[outputs]` 配置产出，与 params.rss 无关） |
| `siteStartYear = 2019` (:78) | ❌ **零读取**（footer.html:4-8：有 site.Copyright 用之，否则 only now.Year） |
| `copyright` (:27) | ✅ | footer.html:4-5（优先级高于默认 © now.Year，hugo.toml:25-26 注释属实） |
| `ogImage` (:56) | ⚠️ **仅经站点覆盖**被读取（layouts/partials/templates/opengraph.html 的兜底分支）；主题原版 opengraph 不读 ogImage |
| `sopNotesDir` (:53) | 站点自有消费：content/posts/_content.gotmpl:31（`site.Params.sopNotesDir \| default "docs/sop"`） |
| `pagination.pagerSize = 6` (:265-266) | Hugo 核心（主题 list.html:48 `.Paginate`） |
| `[outputs] home = HTML,RSS,JSON` (:270-271) | Hugo 核心（决定 index.xml/index.json 生成） |
| `timeZone` (:10) / `uglyURLs` (:17) / `relativeURLs` (:4) / `locale` (:21) | Hugo 核心（注意：timeZone 管不到 post_meta 的 `.Date` 裸字符串化路径，layouts/partials/post_meta.html:10-13 注释属实） |
| 死配置（主题零读取）：avatar、customSyntaxHighlighting、stickyNav、reorderNavItems、collapseNavItems、rss、siteStartYear、`showTableOfContents`(:132)、`showSummaryCoverInPost`(:135)、`imageZoomableInPost`(:138)、`showPrevNextPost`(:141)、`reorderShares`(:144)、`noDefaultSummaryCover`(:121)、`[params.homeInfoParams]`(已注释) | ❌ | 关键错配：TOC 主题只认 `.Param "ShowToc"`（single.html:33）≠ showTableOfContents；上下篇只认 `.Param "ShowPostNavLinks"`（single.html:52）≠ showPrevNextPost。附：hugo.toml:50 的 avatar 注释自述「原 img/tn.png 不存在」——static/img/ 下现状未逐项核（**未验证**），但配置本身死 |
| `email`(:76) / menu.main 全清单(:178-260) | ✅（Hugo 菜单核心 + header.html:85 range site.Menus.main） | 菜单 13 项含 4 个 categories 子项；无 archives 项 |

## 6. 测试缺口

**hugo.test.toml 作用**：仅 `dataDir = "tests/fixtures/data"`（tests/hugo.test.toml:4），配合 `hugo --config hugo.toml,tests/hugo.test.toml -d tests/tmp/fixture` 做 fixture 数据构建；uglyURLs/timeZone/menu 等继承 hugo.toml（该文件头注释自述）；是对 ADR-0001「生产构建命令零改动」的加法。

| 套件 | 与主题渲染产物相关的断言面 |
|---|---|
| tests/assert_product_states.py | 构建 fixture（含 hugo.test.toml）+ 真实数据生产构建；解析首页/产品页产物：mf-row 行、spec 计数（:172 parse_spec_count）；**B1 no-js 基线**：`<html class=no-js>` 与 head 内联 swap 脚本（'classList.remove(\'no-js\')'）在产品页（:224-232）；**B2** 产品页引用 mf-reveal 引擎脚本且落盘（:234-241）；**B3** `.reveal`/`mf-rise d1/d2/d3` 挂点（:243-249）；**B4** data-group/value/kind/price 挂点（:251-255）；**B5** 筛选按钮词汇精确集合（:257-262）；**B6** 产物 CSS 含 `.no-js .reveal` / `.no-js .mf-rise` 降级规则（:264-269）；index.json 产品条 tags==["产品"]（:203-213）；契约坏用例（kind 门禁/listed/price/buy_url errorf 子串）；调用方级 items/uid 必填。**不经 Hugo 的部分（engine 行为）不在本文件** |
| tests/assert_sop_pipeline.py | 派生文章产物：posts 页面集合 vs 注册表 slug 集、URL 冻结（`<slug>.html` 在役）、`<title> == "H1 \| MapleFlow"`、meta description、导语/章节标题/末行内容在场、**golden 三字段**（title/meta description/`<article>` inner HTML，规范化 token 比对，见 tests/sop_golden.py:117-144；比对器**刻意容忍**时间戳时区标记两种形态，sop_golden.py:23-39）、draft 语义、README↔注册表双向一致、ref 链接解析、**index.json 含全部派生 slug**（:392-404 搜索投影）、CI 接线（deploy.yml 含本脚本）。golden 用与 CI 逐字相同的生产命令构建（sop_golden.py:105-112） |
| tests/assert_reveal.mjs | jsdom + 引擎 ESM 源码（scroll-in/filter/reduced-motion），**不消费 Hugo 产物**；样本 HTML 手写镜像 DOM 契约；覆盖筛选/aria/计数/空态/减弱动效/IO 降级/多实例（文件头 :1-20 自述） |

**当前零断言的主题行为面（fork 决策直接相关）**：

1. **no-js/js swap 的全站面**：仅在 products.html 与（B3 的）index.html 上断言类名与脚本存在；**about/search/404/taxonomy/list 等页的 no-js 基线零断言**；js swap 的「执行后语义」只由 assert_reveal.mjs 在合成 DOM 上测，不经真实产物。
2. **post_meta 时区格式无回归保护**：golden 规范化器显式容忍 `+0800 CST` 与 `+0800` 两种写法（sop_golden.py:21-39 注释自述为容错），即 layouts/partials/post_meta.html:18 的修复**被回退也不会红**；仅派生文章的 post-meta 落在 `<article>` golden 范围内，非派生手写文章连 golden 都没有。
3. **菜单与 URL 形态**：header 渲染（13 项菜单、active 态、外链图标、accesskey=/）零断言；菜单 URL 与 uglyURLs 产物的一致性只间接覆盖到 posts/*.html 冻结 URL（assert_sop_pipeline.py:255-262）与 ref 链接。
4. **RSS**：public/index.xml 与各 taxonomy index.xml 的内容、home feed 只含 posts 的语义（layouts/_default/rss.xml 的核心改动）**零断言**。
5. **404 页**：零断言（主题 404.html + 站点 baseof 的 no-js 均无检查）。
6. **list/taxonomy 渲染**：主题 list.html/terms.html 的输出（分页器、tag-entry 类、terms-tags 列表）零断言；assert_product_states 解析的首页行来自**站点自定义 index.html**，不构成对主题 list 的保护。
7. **归档页**：零断言（且不可达，§2）。
8. **search 页渲染**：index.json 投影有断言，但 search.html 本身（searchbox DOM、fastsearch 预加载）零断言。
9. **head/footer 的生产守卫差异**：og/twitter/schema/robots 的 dev-vs-prod 分支行为零断言（本地 public/ 是生产构建产物，测试套件未固定构建环境差异）。

## 7. 构建链触点 →「移除子模块后必须同步修改的清单」

| 触点 | 现状（证据） | 移除子模块后必须处理 |
|---|---|---|
| `.github/workflows/deploy.yml:28` | `submodules: true  # 新增：如果用了 PaperMod 主题（子模块），必须加这个` | 删除该行（否则无害但留死注释）；checkout@v4 默认 recursive=false 也不影响 |
| deploy.yml:60 | 构建命令 `hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml` | hugo.toml `theme = "PaperMod"`（:23）须改：fork 后主题 layouts/assets/i18n 需合并进站点自身目录，或改 Hugo Modules 指向 fork 仓库 |
| deploy.yml:45-53 | `npm ci --ignore-scripts` + `npm test`（reveal 行为断言） | 不受影响（与主题无关） |
| deploy.yml:66,73 | assert_product_states.py / assert_sop_pipeline.py | 两者均以 `theme = "PaperMod"` 的 hugo.toml 构建；fork 后若 layouts 合并路径变化，fixture/tmp 构建仍走 hugo.toml+生产配置，**需重跑确认三套件全绿** |
| AGENTS.md:9 | 「themes/PaperMod 是 Git 子模块（.gitmodules 指向 …）」 | 改写为 fork/合并后形态 |
| AGENTS.md:20 | 「检出（含子模块）→ hugo …」 | 去掉「含子模块」 |
| AGENTS.md:31-32 | 「首次初始化主题子模块（关键！否则 hugo 报 found no layout file）」+ `git submodule update --init themes/PaperMod` | 删除整段 |
| AGENTS.md:76-79 | 坑点 6：`git checkout main` 触发子模块递归联网卡死；正确做法 `git -c submodule.recurse=false checkout -f main` | **删除整条坑点**（该坑随子模块消失） |
| AGENTS.md:65-66 | 坑点 3：「reorderNavItems 在当前 PaperMod 版本同样不被读取（已 grep 主题全目录 0 命中）」 | fork 后可自行决定是否实现该参数；文档须同步 |
| AGENTS.md:133 | 表格行：post_meta.html「升级 PaperMod 子模块时必须回来同步」 | 改为 fork 内文件 |
| AGENTS.md:5,7 | 「项目结构」表（未逐行核，含主题行——**未验证具体行号**） | 结构描述更新 |
| `.gitmodules` | 存在（path/url 两条） | 删除文件（fork 方案）或改 url |
| auto_push.py:26,31,36 | `git add .` → `git commit -m "update: <时间戳>"` → `git push origin main` | 代码零 PaperMod 耦合；**但已实证**：`git add --dry-run .` 只列出 `.workbuddy-ai/memory/*.md`，**不暂存子模块内部 CRLF dirty**（gitlink 未变则 `git add .` 对子模块无可暂存内容）；反之若子模块 gitlink 移动，`git add .` 会把 gitlink 变更一并入库。fork 后此行为消失，无改动必要 |
| docs/adr/0002 | 「layouts/_default/baseof.html 与 layouts/partials/extend_head.html 两个主题覆盖文件需在 PaperMod 子模块升级时手动同步」 | fork 后同步义务消失；另注意该 ADR **漏列**了两个同样有同步义务的近逐字覆盖：post_meta.html（其文件头 :3-4 自述）与 templates/opengraph.html |
| README.md:20,26,34-38,66 | 「补执行子模块」「主题目录空的排查」「手动 clone 主题到 themes/PaperMod」「检出代码（包含 PaperMod 子模块）」 | 涉及子模块初始化的指引整段删除/改写 |
| CLAUDE.md | **零** submodule/PaperMod 引用（grep 实证） | 无需改 |

## 附：对决策图有直接影响的边缘事实

- 主题 v8 的**可删面很大**：16/25 partial 不可达、6/6 短代码零引用、archives 模板不可达、robots.txt 被 static/ 遮蔽、悬空的 google_analytics.html；但同时 **9 个 partial 可达且被站点行为依赖**（head/header/footer/baseof 链 + extend_head/extend_footer/post_meta/author/anchored_headings/opengraph 链）。
- **两条不同的「生产守卫」语义**：head.html:200 的 `hugo.IsProduction | or (eq site.Params.env "production")` 控制 OG/schema/analytics；cover.html:6/header.html:14/index_profile.html:14 的 `$prod` 控制图片处理。dev 与 prod 产物差异巨大（og 标签、robots Disallow、图片 srcset），任何 golden/断言机制固定到单一环境都有盲区。
- 站点 4 个「近逐字覆盖」文件（baseof/extend_head/post_meta/opengraph）+ 2 个语义重写（index.json/rss.xml）+ index.html（net-new）构成对上游的全部耦合面；ADR-0002 只点名 2 个，实际是 4 个。

# 0042 研究：搜索模块现状事实底座

2026-10-22 · research（AFK）· 工单 [0042 搜索模块现状事实底座](../tickets/0042-search-module-facts.md)

本图后续所有决策的事实前提。只查事实、不做决策。六项结论，逐条带文件:行号证据；事实与推断分开标注。

---

## 1. index.json 投影面

投影文件：`layouts/_default/index.json`（站点层，覆盖主题同名模板）。

**文章投影**（:12-25）：`range site.RegularPages`，三类排除——`.Params.searchHidden` 为真、`.Layout "archives"`、`.Layout "search"`（:14）。每条投影六字段（:16-23）：

| 字段 | 表达式 |
|---|---|
| `title` | `.Title` |
| `permalink` | `.Permalink` |
| `summary` | `.Summary \| plainify \| htmlUnescape \| chomp` 后 `truncate 200` |
| `content` | **同一 `$summary`** 截断到 320（:15、:20） |
| `tags` | `.Params.tags \| default slice` |
| `categories` | `.Params.categories \| default slice` |

**关键事实：`summary` 与 `content` 同源**——两者都是 `.Summary`（Hugo 的自动摘要）的 plainify 截断，仅长度不同（200 vs 320）。`content` 字段**不含文章正文**。产物抽样佐证：`tests/tmp/real/index.json` 中 12/12 条文章记录的 `content` 均以 `summary` 同串开头。

**产品投影**（:26-41）：`with site.GetPage "page" "products"` 内 `range site.Data.products` **直读数据文件**，不过 `product-items.html`。每条四字段 + 两硬编码：`title = .name`；`permalink = <产品页 RelPermalink>#<id>`；`summary = .summary`；`content = printf "%s %s %s" .name .summary (.scale | default "")`；`tags = ["产品"]`、`categories = ["产品"]` 硬编码（:37-38）。

**契约执法：零。** 投影层无任何 `errorf`，坏数据（缺 name/summary、类型错误）静默进索引。0019 边界注释原文在 :28-30：「覆盖边界（0019 决议）：此处直读 site.Data.products，不经 product-items 的 kind 词汇门禁。门禁的实际覆盖靠『产品页恒渲染全量 → product-items 恒被调用』这一隐式依赖兜底；索引投影是否重复校验/如何校验，随候选 8『搜索契约』定案。」

**无 featured 投影**（ADR-0009 边界确认）。

## 2. fastsearch 接线面

**加载条件**：`themes/maplemod/layouts/partials/head.html:77-90`，仅当 `(eq .Layout "search")` 时输出 `<link rel="preload" as="fetch" href="../index.json">` 并打包脚本。管线（:80-89）：`fastsearch.js` 经 `js.Build (dict "params" (dict "fuseOpts" site.Params.fuseOpts))` → 与 `fuse.basic.min.js`、`license.js` concat 为 `assets/js/search.js` → fingerprint（未disableFingerprinting 时）。**与 mf-reveal 的 `extend_footer` js.Build 管线同款**（ADR-0007）。

**fuseOpts 未配置**：hugo.toml 全文无 `fuseOpts`（grep 仅命中注释）。`site.Params.fuseOpts` 为 nil 时 js.Build **构建仍成功**——本地 hugo v0.167.0 实测 exit=0，产物 `search.js` 指纹 `b0579257...` 与 `public/`、`tests/tmp/real/` 中一致，即线上跑的就是 nil params 的构建；`fastsearch.js:29` 的 `if (params.fuseOpts)` 走 false 分支，全部用默认 options。**`fastsearch.js:29-43` 整段 fuseOpts 分支是潜伏死路径**（无任何 hugo.toml 配置可触达，但参数位有读取点，不违反参数纪律）。

**检索行为**（`themes/maplemod/assets/js/fastsearch.js`）：默认 Fuse options（:18-28）——`distance 100 / threshold 0.4 / ignoreLocation true`，keys = `['title','permalink','summary','content']`。检索入口 `sInput.onkeyup`（:76），逐字符触发；`fuse.search` 结果渲染为 `<li class="post-entry"><header class="entry-header">…</header><a href=…>`（:91-92）；`resultsAvailable` 标志 + `first/last` 指针驱动键盘导航（:112-152）：Escape 清空重置、ArrowDown/ArrowUp 在输入框与结果间移动 focus（`activeToggle` 操纵 `.focus` class，:55-67）、ArrowRight 点击当前项。XHR 取 `"../index.json"`（:51，相对 search.html → 站根 index.json）；**失败容错仅 `console.log`**（:47），`JSON.parse` 无 try/catch——index.json 缺失或损坏时搜索静默失效（无结果、无报错）。

**键盘入口**：`themes/maplemod/layouts/partials/header.html:88-91` 给搜索菜单项加 `accesskey=/` 与 title 后缀 `(Alt + /)`——既有事实，搜索入口有快捷键。

## 3. search 页面

- `content/search.md`：front matter 仅三键——`title = "搜索"` / `layout = "search"` / `summary = "搜索站内文章"`。无 description、无 searchHidden。
- `themes/maplemod/layouts/_default/search.html`：三挂点在 :18-21——`<div id="searchbox">`、`<input id="searchInput" … aria-label="search" maxlength="64">`、`<ul id="searchResults" aria-label="search results">`；placeholder 取 `.Params.placeholder | default (printf "%s ↵" .Title)`。
- `themes/maplemod/assets/css/common/search.css`：45 行，经 `head.html:56` 的 `resources.Match "css/common/*.css"` **全站加载**（不限 search 页）。
- uglyURLs 下页面为 `/search.html`（hugo.toml menu 项 :183-188）。

## 4. 现有断言覆盖与缺口

| 断言 | 位置 | 锚定构建 | 内容 |
|---|---|---|---|
| 产品 tag 检查 | `tests/assert_site_contracts.py:274-283`（`assert_search_index`） | **fixture 构建**（调用点 :389；dest=TMP/"fixture"，FIXTURE_CONFIG=hugo.toml,tests/hugo.test.toml；真实 content + fixture data） | index.json 中 products.html# 锚点条目的 `tags == ["产品"]`；无产品条目则红 |
| B11 三挂点 | `tests/assert_site_contracts.py:639-645` | **真实数据构建**（在 `assert_theme_contract` 内，:590 由 `assert_real` 调用；`--quick` 跳过真实构建即跳过本条） | search.html 含 searchbox/searchInput/searchResults 三个 id |
| SOP 派生在场 | `tests/assert_sop_pipeline.py:436-446`（`assert_search_index`） | 真实构建（TMP/"real"） | 注册表 6 条 slug 全部出现在 index.json permalink |
| RSS 只收 posts（B10） | `tests/assert_site_contracts.py:632-637` | 真实构建 | 顺带事实：搜索类内容不在 RSS，与索引排除规则各自为政 |

**行为测试：零。** `tests/assert_reveal.mjs` 无任何 search 相关内容（grep 计数 0）；`package.json` 的 `test` 脚本只跑 `node tests/assert_reveal.mjs`（jsdom ^30.1.3 是唯一 devDependency）。

**fixture 矩阵现状**（四套构建，`tests/assert_site_contracts.py:257` `build()`）：
- `tests/hugo.test.toml`（只覆盖 dataDir）→ TMP/"fixture"：产品状态/索引/精选/reveal 产物 + 上述产品 tag 断言；
- `tests/hugo.test.posts.toml`（只覆盖 contentDir → tests/fixtures/content-posts）→ TMP/"posts-fixture"：文章精选两片断言；
- 若干坏用例构建（TMP/"bad-*"、caller-*、empty-state）；
- 真实数据构建（hugo.toml,config.production.toml）→ TMP/"real"：B7-B13 主题契约 + 真实数据回归。
- **SOP 管线另有自有 fixture**：`tests/fixtures/featured/`（data + content[含适配器副本] + notes），`assert_sop_pipeline.py:381+` 生成 `tests/tmp/featured.toml` 构建 → TMP/"featured"，消费方是首页精选区透传断言（0040）。

**投影层无校验的活例证（推断已坐实为事实）**：`tests/fixtures/featured/data/sop.yaml` 两条派生条目**均无 `intro` 字段**，而 `content/posts/_content.gotmpl:61` 的 `printf "%s\n\n---\n\n%s" $entry.intro $body` 对 nil intro 渲染出字面量 `%!s()`——该构建的 `tests/tmp/featured/index.json` 两条记录 `summary`/`content` 均以 `"%!s()"` 开头。即：**注册表缺字段 → 派生页摘要污染 → 静默进搜索索引，全链路无任何 errorf**。真实 `data/sop.yaml` 6 条均有 intro，生产不受影响；该 artifact 只活在 fixture 构建，但 CI 每次跑 assert_sop_pipeline 都在生产它。

**缺口清单**（现有断言未覆盖、且候选 8 需要决策的问题面）：
1. 投影字段契约无定义处（无 docstring / 术语 / 测试锚定六字段语义）；
2. 文章侧投影零断言（排除规则、字段形态、截断行为均无 fixture 覆盖——现有两条 index.json 断言一条只看产品 tag、一条只看 SOP 在场）；
3. `content` 与 `summary` 同源这一设计无任何文档或断言，改其一可能静默改变两者；
4. 坏值契约缺失（缺 name/summary、%!s() 类污染无门禁）；
5. fastsearch 行为零测试（渲染、键盘导航、容错降级）；
6. fastsearch 无 docstring，DOM 契约（三挂点之外的 li 结构 / focus class）无定义处，B11 只守三个 id；
7. fuseOpts 死路径无文档化处置；
8. featured 投影与否无决策（ADR-0009 遗留）；
9. kind 门禁在投影中的归属无决策（0019 遗留）；
10. 测试入口若要扩搜索行为套件，`package.json` test 脚本与 CI 的 `npm test` 步如何调整无决策。

## 5. 各 ADR / 工单留给本图的边界注记原文

- **ADR-0006 决策 5**（docs/adr/0006-product-index-narrowing.md）：「搜索索引（`index.json`，属候选 8 搜索契约）保持各自迭代，`index.json` 留边界注释（kind 门禁靠『产品页恒渲染全量 → 数据门禁恒生效』兜底）。」
- **工单 0019 Resolution 3**（docs/wayfinder/tickets/0019-narrowed-interface-test-seam.md）：「搜索索引 kind 门禁 = 归候选 8 + 本图留边界注释……索引投影不重复校验；门禁去留随候选 8 的投影契约定案。」
- **ADR-0007 Consequences**（docs/adr/0007-reveal-protocol.md）：「搜索 JS（fastsearch）与 `index.json` 投影不属本 ADR，归候选 8（搜索契约）。」
- **ADR-0008 Consequences**（docs/adr/0008-theme-fork.md）：「搜索 JS（fastsearch）与 index.json 投影契约归候选 8；本图未动，代码里的 0019 边界注释继续有效。」（B11 三挂点由 0032 并入 assert_site_contracts.py。）
- **ADR-0009 Consequences 边界**（docs/adr/0009-featured-mechanism.md）：「搜索索引（`index.json`）是否投影 featured 归候选 8。」
- **工单 0026**（docs/wayfinder/tickets/0026-terminology-naming-adr.md）：不涉及搜索（已核，无相关注记）。
- **handoff 2026-10-22 下一步 2**（docs/handoffs/2026-10-22-candidate-7-closure.md）：「选下一张图：候选 8『搜索契约』（`index.json` 投影字段 + fastsearch + kind 门禁归属）。」

## 6. hugo.toml 搜索相关参数

| 参数 | 位置 | 读取点 | 状态 |
|---|---|---|---|
| `[outputs] home = ["HTML","RSS","JSON"]` | hugo.toml:215-218 | Hugo 内置（产出 index.json） | 已配置，有读取点 |
| menu search 项（url=/search.html, weight=6） | hugo.toml:183-188 | `themes/maplemod/layouts/partials/header.html:85-91`（含 accesskey=/ 特判） | 已配置，有读取点 |
| `fuseOpts` | **不存在** | `head.html:80` js.Build params + `fastsearch.js:29-43` 分支 | 未配置；读取点存在但 nil 走默认（见第 2 项） |

按参数纪律（每个参数须有读取点，无读取点即死配置）：现状无死配置；`fuseOpts` 是「有读取点、无配置」的潜伏参数位，其存废是候选 8 的决策面（归工单 0046）。

---

## 周边事实

- `public/index.json` 存在（09:10 新构建，含 JSON 输出）——本地 public/ 不是陈旧产物。
- `tests/tmp/` 现有子目录：`real`（17 条索引）、`featured`（2 条，SOP 管线 fixture 构建）、若干 bad-*/draft-*/caller-*；**无 `fixture`、无 `posts-fixture`**——即 tests/tmp 不是最近一次完整 `assert_site_contracts.py` 全套的产物（部分被清或部分运行），引用其中产物时需注意新鲜度。

# 0055 三条雾区现状事实底座（盘点）

> 工单 0055 研究产物 · 2026-10-23 · 只查事实不做决策 · 证据以 `文件:行号` 为准

## 1. 首页数据条

`layouts/index.html:46-72`（`section.mf-spec`，仅第 1 页渲染，`index.html:18` 门控）四项：

| 项 | 算法与数据来源 | 行号 | 现状值（public/ 产物实测） |
|---|---|---|---|
| 篇技术文章 | `len $pages`，`$pages = $postSets.all`，即 post-items.html 的 **all 片** | `index.html:10,48` | 10（4 手写 + 6 SOP 派生） |
| 个分类 | `len site.Taxonomies.categories` | `index.html:52` | 4 |
| 份可下载产品 | `range hugo.Data.products`，逐条 `partial "product-state.html" .` 取 `.listed` 计数 | `index.html:57-63` | 0 |
| 最近更新 | `index (site.RegularPages.ByLastmod.Reverse) 0` 的 `.Lastmod` 格式化为 `2006-01` | `index.html:67-68` | 2026-01 |

关键事实：
- 「篇技术文章」取数口径 = post-items.html 的 all 片 = `where site.RegularPages "Type" "posts"`（空则回落全量），按日期倒序（`layouts/partials/post-items.html:28-30,51`）；**含 SOP 派生文**。
- 「最近更新」口径 = `site.RegularPages` 全站（非 posts-only），与上一项口径不同；当前站内恰同集（所有 regular pages 均属 posts 区），无断言守此一致性。
- ADR-0004 决议原文（`docs/adr/0004-product-state-module.md:3`）：「产品的上架/免费判定与控件语义收敛在 `layouts/partials/product-state.html` 一个 return 型 partial，`product-index.html`、首页数据条与测试共用同一 seam」；Consequences（`docs/adr/0004-product-state-module.md:7`）：「模板与首页不得自行推导产品状态，发现第二处推导即违本 ADR」。即数据条可下载产品计数**不随产品索引链**（不走 product-items.html），直调 product-state.html。
- CONTEXT.md 佐证：「模板与首页数据条消费它，不自行推导」（`CONTEXT.md:48`）；「只有已上架产品计入站点数据中的『可下载产品』」（`CONTEXT.md:60`）。
- 锚定数据条的断言（`tests/assert_site_contracts.py`）：
  - `parse_spec_count`（`:300-307`，按 label 文本定位 mf-spec-num 取整数）；
  - `assert_fixture`（`:444`）内「fixture 首页计数 = 已上架条数（2）」（`:480-481`，锚 fixture 构建 `hugo.toml,tests/hugo.test.toml`）；
  - `assert_real`（`:810`）内「真实数据可下载产品计数 = 0」（`:822-823`，锚真实/生产构建）。
  - **只有「可下载产品」一项被断言**；「篇技术文章 / 个分类 / 最近更新」三项无任何断言引用（grep `篇技术文章` 在 tests/ 零命中）。

## 2. 分类/标签页渲染链

- 主题 `_default/list.html` 取页与排序：`$pages := union .RegularPages .Sections`（`themes/maplemod/layouts/_default/list.html:36`）→ `.Paginate $pages`（`:43`）。模板内**无任何显式排序**。
- Hugo 对 `.Paginate` 输入的默认排序（Hugo 官方文档语义，Page collections 默认排序，0.164 系列未变）：**weight 升序（weight=0/未设置视为无权重，排在任何有权重页之后）→ date 倒序 → LinkTitle 升序 → filepath**；`.Paginate` 不重排输入，保留给定顺序。本项目 `content/` 与 `archetypes/` 无任何 `weight` 字段（已 grep 确认），故实际顺序 = **日期倒序**。产物佐证：`public/posts/index.html` 页 1 前三篇为 sop-ops-tools-index（01-28 20:30）→ Prometheus（20:25）→ Grafana（20:20）。分页大小 `pagerSize = 6`（`hugo.toml:184-185`）。
- `themes/maplemod/layouts/_default/terms.html` 角色：taxonomy 词条索引页（`/categories/`、`/tags/`）——渲染 `ul.terms-tags`，按 `.Data.Terms.Alphabetical` 列词条 + Count（`terms.html:14-25`）；**不分页、不列文章、不消费 featured**。term 页（如 `/categories/aiops.html`）不走它，走 list.html。
- 站点层覆盖确认：`layouts/` 下**无 list.html / terms.html / single.html 覆盖**（`ls -R layouts/` 仅 `index.html`、`partials/`、`shortcodes/`、`_default/index.json`、`_default/rss.xml`）。分类页、标签页、`/posts/` section 列表全部走主题层模板。
- `/posts/` 文章列表页与分类/标签 term 页**同链**（同为 `_default/list.html`，同为 `union .RegularPages .Sections` → `.Paginate`）；唯一差别是 term 页命中 `$term` 分支加 `tag-entry` class（`list.html:53-54`）。产物佐证：`public/posts/index.html` 6×`post-entry`；`public/categories/aiops.html` 为 `post-entry tag-entry`；`public/categories/index.html` 含 `terms-tags`。
- 死代码事实：`list.html:38-41` 的 `.IsHome` 分支（mainSections 过滤）在本站不可达——home kind 被站点层 `layouts/index.html` 覆盖，永不进入主题 list.html。
- 主题层全部模板无 featured 消费点（grep `featured` 在 `themes/maplemod/layouts` 仅命中 get-page-images.html 的「featured image」资源匹配，与精选语义无关）。
- 锚定 list/term 页产物的断言：**无专属断言**。B7-B14 中只有全站面断言覆盖到它们：
  - B7 全站 no-js 基线 + 内联交换脚本（`assert_site_contracts.py:868-882`，遍历 dest 全部页面，含 `/posts/index.html`、term 页）；
  - 搜索入口全站恒加载 / fastsearch 不泄漏（`:664-675`、`:849-863`）；
  - B13 站点/主题单副本不变量（`assert_single_copy`，`:946-956`）。
  - B8/B9/B14 只锚单页 `posts/aiops-state-and-tools.html`（`:886-920`）；B10 锚 `index.xml`（`:922-927`）；B11 锚 `search.html`（`:929-936`）；B12 锚 `about.html`（`:938-943`）。**列表页排序、分页、条目内容、卡片 DOM 均无断言**。

## 3. 文章页与列表卡片的徽标现状

- 文章页 `themes/maplemod/layouts/_default/single.html`：**无精选/hint 机制**；唯一徽标是 Draft 先例——`h1.post-title.entry-hint-parent` 内 `{{- if .Draft }}<span class="entry-hint" title="Draft"><svg …/></span>{{- end }}`（`single.html:5,7-14`）。
- 列表卡片 Draft 先例（`list.html`）：`h2.entry-hint-parent` 内同款 `span.entry-hint`（`list.html:61,63-70`），触发条件 = `.Draft`（front matter `draft = true`）。CSS 先例存在：`.entry-hint` / `.entry-hint-parent`（`themes/maplemod/assets/css/common/post-entry.css:83,87`）。先例的固有限制：draft 页不进生产构建，徽标只在 `-D` 构建可见（精选无此问题，featured 文章照常发布）。
- 站点层首页网格卡片 `index.html:130` 只有 `h2.entry-hint-parent`，无 `entry-hint` span（首页消费可发布文章，draft 本就不在集合内）。
- 首页精选行 DOM 契约（`index.html:83-102`）：`ol.mf-rows > li.mf-row.reveal > div.mf-row-num`（`86`）+ `div.mf-row-main`（`h3.mf-row-title` `88`、`p.mf-row-sum` `89`、`ul.mf-row-meta` `90`）+ `div.mf-row-side > a.mf-cta.mf-cta-ghost`（`98`）。
- 首页网格 DOM 契约（`index.html:126-141`）：`div.mf-posts > article.mf-post > header.entry-header > h2.entry-hint-parent` + `div.entry-content` + `footer.entry-footer`（post_meta）+ `a.entry-link`。
- 断言锚定情况（`tests/assert_site_contracts.py`）：
  - 已锚：`mf-rows` + `mf-row-title`（`parse_home_featured_slugs`，`:289,292`；注意首页有 2 个 mf-rows——文章精选区与产品精选区同用该 class，函数靠「精选文章」标题锚定，`:283-287`）；`mf-posts` + `entry-link`（`parse_home_grid_slugs` `:297`；`assert_post_grid_empty` `:567`）；`mf-spec-item/num/label`（`parse_spec_count` `:302-304`）。
  - 未锚：`mf-row-num`、`mf-row-sum`、`mf-row-meta`、`mf-row-side`、`mf-post`、`entry-hint`、`entry-hint-parent`（grep 全 tests 零命中）；首页精选行的 `mf-row reveal`（B3 只锚 `products.html` 的 `'mf-row reveal'`，`:417`）。
- `themes/maplemod/layouts/partials/post_meta.html` 渲染元信息（`:16-38`）：日期 span（title 为显式时区格式 `2006-01-02 15:04:05 -0700`，`:19`，0030 对上游的修正）、阅读时长（`ShowReadingTime`，`:22-24`）、字数（`ShowWordCount`，`:26-28`）、作者（非 `hideAuthor`，`:30-34`），`·` 分隔。**无分类/标签/featured 元信息**。

## 4. ADR-0009 已锁部分的接口面

- `layouts/partials/post-items.html` 文件头 docstring 契约条款现状（`:1-26`）：
  - 「本 partial 是首页精选渲染链中**唯一**读 site.RegularPages 并做 featured 判定/截断/补集的地方；渲染形态（编号行 vs 卡片网格）不归本文件」（`:4-6`）；
  - 入参「只收 `limit`（缺省或 0 = 全部；负数 → errorf）」（`:9`）；
  - 三片语义：`featured`「已标精选的文章，按日期倒序，limit 截断后」（`:12`）；`rest`「其余文章，按日期倒序；与 featured 互斥、并集为全量」（`:13-14`）；`all`「全量可发布文章，按日期倒序（计数用，不参与分页）」（`:15`）；
  - 「featured 只认布尔 true。字段存在但类型非 bool → errorf」（`:18-21`）；「limit 为负数 → errorf」（`:22`）；
  - 边界表述（即「只服务首页」条款）：「调用方（不自行 where/first 推导）：· layouts/index.html（首页精选文章区 + 最近更新网格）」（`:24-26`）——docstring 无「禁止其他调用方」的硬禁令措辞，仅此一条调用方登记。
- `CONTEXT.md`「精选 (Featured)」条原文（`:89-91`）：「由 featured 标记驱动的内容挑选机制，适用于文章与产品两类内容；未被标记的内容不参与精选。**未声明即非精选；标记必须是布尔 `true`（坏值即构建失败）**。文章侧首页『精选文章』区与『最近更新』网格互斥：入选文章从网格剔除，被条数截断的精选回落到网格。」`_Avoid_`: 推荐、置顶、热门。
- `data/sop.yaml` featured 现状：**6 个条目全部未标 featured**（`:9-51`）；文件头注释声明契约：「featured 存在但非布尔（2026-10 精选机制，工单 0040；featured 可选，缺省即非精选）→ 构建失败」（`:7-8`）。SOP 侧条件传键实现：`content/posts/_content.gotmpl:62-71`（`isset` 守卫 + `merge` 条件传键，非 bool errorf 在 `:68`）。
- 真实文章侧 featured 分布：3 篇手写标了 `featured = true`（`content/posts/aiops-state-and-tools.md:5`、`k8s-common-commands.md:5`、`sop-ops-tools-index.md:5`），`docker-common-commands.md` 未标。
- ADR-0009 对三条雾区的边界原文（`docs/adr/0009-featured-mechanism.md:34`）：「**边界**：搜索索引（`index.json`）是否投影 featured 归候选 8；『精选』徽标在内容层的呈现、首页数据条是否区分精选、分类页是否消费精选留在地图雾区，未决。」同文件 `:37`：搜索索引不投影已由 ADR-0010 定案（`layouts/_default/index.json:18` docstring 亦记「featured / kind 不投影——无消费方」）。

## 5. 精选相关断言全清单

`tests/assert_site_contracts.py`（文章侧 fixture 构建配置 = `tests/hugo.test.posts.toml:6`，只覆盖 `contentDir = "tests/fixtures/content-posts"`；featured fixture 文章 6 篇，位于 `tests/fixtures/content-posts/posts/`：fx-post-feat-a/b/c/d 标 `featured=true`（02-01～02-04）、fx-post-false 显式 `false`（02-05）、fx-post-newest 未声明（02-10，用于区分「按日期取前 3」旧行为）——分布：4 featured（limit=3 截断 1）+ 1 false + 1 未声明；坏例 fixture：`content-posts-bad/posts/bad-featured.md`（字符串 `'true'`）、`content-posts-bad-int/posts/bad-featured-int.md`（整数 `1`）；另有无 featured 的 `content-posts-none` 与全 featured 的 `content-posts-all`）：

| 函数（行号） | 锚定构建 | 内容 |
|---|---|---|
| `assert_post_featured`（:499） | `hugo.toml,tests/hugo.test.posts.toml` | 5 条：精选区 = 3 条 featured 日期倒序（d/c/b）；第 4 条 feat-a 截断不上；网格 = rest 三篇；两片互斥；并集 = 全量 6 篇 |
| `assert_post_featured_empty`（:526） | 同上 + `--contentDir tests/fixtures/content-posts-none`（两篇均未标） | 0 篇 featured → 精选区整块不渲染（锚「精选文章」文案缺席 + slug 列表空） |
| `assert_post_featured_bad`（:540） | 同上 + `content-posts-bad`（featured 为字符串） | 构建失败且错误含「文章精选数据：」 |
| `assert_post_featured_bad_int`（:547） | 同上 + `content-posts-bad-int`（featured 为整数） | 同上，整数单开一例 |
| `assert_post_grid_empty`（:554） | 同上 + `content-posts-all`（两篇全 featured） | 精选区 2 行 + 网格整块不渲染（判定锚 `mf-posts` / `entry-link`，不用「最近更新」文案，:563-567） |
| `assert_fixture`（:444）内首页条目（:465-479） | `hugo.toml,tests/hugo.test.toml`（dataDir=fixtures/data） | 产品侧：首页精选分栏 = 前 3 条 featured 产品；非 featured 产品不上首页；截断产品不上首页但仍在产品页 |
| `assert_real`（:810）内（:824-826） | 生产配置真实构建 | 真实首页精选 = 3 条 featured 产品（yaml 序，`REAL_HOME_FEATURED_IDS`） |

`tests/assert_sop_pipeline.py`：
- `assert_featured_passthrough`（:381）：fixture `tests/fixtures/featured`（dataDir/contentDir/sopNotesDir 三覆盖，`hugo.toml` + 临时 toml，按 CI 生产命令 `--gc --minify` 构建）；fixture 注册表 2 条——`sop-featured-entry`（`featured: true`，2026-04-01）/ `sop-plain-entry`（未标，2026-04-02）（`tests/fixtures/featured/data/sop.yaml:3-11`）。三条断言：fixture 适配器副本与真实 seam 逐字节一致（:394-396）；「注册表 featured: true → 派生文进首页精选区」（:416-417）；「未标 featured 的派生文不进精选区」（:418-419）。
- SOP 侧 featured 非布尔 errorf 存在于 seam（`_content.gotmpl:68`），但 **`tests/fixtures/bad/` 无 sop-featured-not-bool 用例**、`assert_sop_pipeline.py` 的 `BAD_CASE_EXPECT`（:77-84）无对应条目——该契约无坏用例断言（文章侧有 bad/bad-int 两条）。
- ADR-0009 明示「真实精选清单**不锚**断言（内容由项目负责人掌控）」（`docs/adr/0009-featured-mechanism.md:13`）——fixture 只保护契约行为。

## 6. 外部惯例（外部常识，非本项目事实）

以下为博客/文档站生态通行做法，非本仓事实，供决策参考：

- **徽标/标识（badge）**：卡片与文章页标题旁加「精选」角标。通行成本：每处渲染面（single + list + 可能的卡片组件）各加条件分支，测试面随之扩大；本站已有 Draft 徽标先例（`entry-hint`，DOM + CSS 齐备）可直接复形。
- **排序优先（sticky/pinned）**：置顶集合排于日期流之前。通行成本：与「最新在前」的心智冲突；置顶集合内部序需再定（社区常见 `weight` 手工序或日期倒序）；本站 ADR-0009 已为 3 条规模显式拒绝 `weight`（`docs/adr/0009-featured-mechanism.md:22`）。
- **专属区块（featured section）**：首页 hero 下单独成区。通行成本：与主列表重复展示（本站已用补集 seam 解决）；空态与全入选时的降级需定义（本站已定义：整块不渲染）。
- **Hugo 主题侧**：Hugo 核心无 featured/sticky 内置概念；PaperMod 无原生 featured 排序，社区通行做法即 front matter 自定义字段 + 列表模板 `where`/`first` 过滤（与本站 `post-items.html` 同构），或在卡片模板渲染 `if .Params.featured` 徽标；少数主题借 `weight` 实现置顶。代价同上：徽标要改多处模板、排序要与默认 weight→date 链交互。

## 缺口清单

现有断言未覆盖、且三条雾区决策需要正视的问题面：

1. **数据条三项无牙**：「篇技术文章 / 个分类 / 最近更新」无任何断言（只有「可下载产品」被 fixture=2 / real=0 锚定）。雾区②若改数据条口径，数字语义变化无守门。
2. **列表/term 页无专属断言**：`/posts/`、分类页、标签页的排序、分页、条目内容、卡片 DOM 均无断言，仅被全站面断言（B7、search-entry 加载/泄漏）incidental 覆盖。雾区③若让 term 页 featured 优先，需要新建断言面（含 Hugo 默认排序链被改写后的期望值）。
3. **徽标 DOM 契约无牙**：`entry-hint` / `entry-hint-parent` 及其 CSS 无任何测试引用；Draft 徽标先例的渲染本身不被守。雾区①若加精选徽标，先例可用但无保护，需同步补断言。
4. **首页精选行细部 class 未锚**：`mf-row-num / mf-row-sum / mf-row-meta / mf-post` 未被断言引用（`mf-rows / mf-row-title / mf-posts / entry-link` 已锚）；文章精选区与产品精选区共用 `mf-rows / mf-row-title`，现有解析函数靠标题文本锚定（`assert_site_contracts.py:283-292`），区块结构变化时解析有脆性。
5. **SOP 侧 featured 坏值无 fixture**：`_content.gotmpl:68` 有 errorf，但无 sop-featured-not-bool 坏用例、无登记子串（文章侧有 bad/bad-int 两例）——SOP 注册表写坏值只有真实构建能暴露。
6. **真实 SOP 条目零精选**：`data/sop.yaml` 6 条均未标 featured；真实首页精选区当前只有 3 篇手写文章（日期倒序：sop-ops-tools-index / aiops-state-and-tools / k8s-common-commands）。派生文精选占比现状为 0。
7. **两处取数口径不一致且无守门**：数据条「篇技术文章」= all 片（Type=posts），「最近更新」= `site.RegularPages` 全站；当前站内恰同集，无断言保证。
8. **post-items.html 无「只服务首页」硬边界**：docstring 仅登记唯一调用方（`:24-26`），无 errorf 级或断言级守卫；list/term 页若未来复用该 seam，无任何机制提示越界。

id: "0055"
title: 三条雾区现状事实底座（盘点）
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-featured-fog-zones.md
created: 2026-10-23
claimed: 2026-10-23
closed: 2026-10-23
---

## Question

三条雾区对应面的现状盘点——本图后续所有决策的事实前提，只查事实、不做决策、不给推荐。要盘清六项：

1. **首页数据条**：`layouts/index.html` 的 `mf-spec` 区块（约 46-72 行）四个计数项各自的算法与数据来源（「篇技术文章」是否取自 `post-items.html` 的 `all` 片、分类数、可下载产品数、最近更新）；ADR-0004 中关于「首页计数条不随产品索引链」的决议原文摘录；`tests/assert_site_contracts.py` 中哪些断言锚定首页数据条（函数名 + 锚定构建 + 断言内容一句话）。
2. **分类 / 标签页渲染链**：`themes/maplemod/layouts/_default/list.html` 的取页与排序（`union .RegularPages .Sections` → `.Paginate`；**Hugo 默认排序规则是什么、实测确认**——weight/date/linktitle 的优先级）；`terms.html` 的角色；站点层有无 `list.html` 覆盖（确认无）；`/posts/` 文章列表页（section list）走哪套渲染、与分类/标签页是否同链；现有主题契约断言（B7-B14）中哪些锚定 list/term 页。
3. **文章页与列表卡片的徽标现状**：`themes/maplemod/layouts/_default/single.html` 有无徽标 / hint 机制；`list.html` 的 Draft `entry-hint` 徽标先例（class 名 / DOM 结构 / 触发条件）；首页精选行（`mf-rows`/`mf-row-num`）与网格卡片（`mf-posts`/`mf-post`/`entry-link`）的 DOM 契约——哪些 class 已被断言锚定、哪些没有；`post_meta.html` 渲染哪些元信息。
4. **ADR-0009 已锁部分的接口面**：`layouts/partials/post-items.html` 的 docstring 契约现状（`{featured, rest, all}` 三片语义、`limit` 语义、有无「只服务首页」类边界条款）；`CONTEXT.md`「精选 (Featured)」条现状原文；`data/sop.yaml` 的 `featured` 字段现状。
5. **精选相关断言全清单**：`tests/assert_site_contracts.py` 中精选类断言逐条（函数名 + 锚定构建 + 内容一句话）；contentDir fixture 的构建配置在哪、featured fixture 文章放在哪、篇数与 featured 分布；`assert_sop_pipeline.py` 中 featured 相关断言。
6. **外部惯例（轻量）**：主流博客 / 文档站对「精选 / 推荐 / 置顶」在内容层的呈现惯例（徽标 / 排序优先 / 专属区块）各有什么代价；Hugo 主题（PaperMod 等）对 featured 排序的常见做法。标注为外部常识，非本项目事实。

产物：`docs/wayfinder/research/0055-featured-fog-facts.md`，前 5 项逐条带 `文件:行号` 证据；第 6 项标注来源；结尾给「缺口清单」（现有断言未覆盖、且本图需要决策的问题面）。只查事实，不做决策，不给推荐。

环境注意：本 shell 的 grep 对 `\|` 交替失效，内容搜索用 Grep 工具；除研究产物文件外不得修改任何仓库文件；不得执行 git 写操作；不得运行 hugo 构建（以读源码与既有 `public/` 产物为准）。

## Resolution

2026-10-23 · research（AFK）：研究子代理完成六项盘点（本 shell 的 Write 工具对长 content 偶发丢参数，子代理改以正文返回、主代理 heredoc 分段落盘，环境注意已历图在案）；主代理抽查核实六处关键证据：`post-items.html` docstring 三片语义与唯一调用方登记（:1-26）、`assert_site_contracts.py` 十个相关函数行号逐一吻合、`data/sop.yaml` 6 条均未标 featured、3 篇手写文章 `featured = true`、`single.html:5,7-14` Draft 徽标先例、fixture 6 篇分布 + bad/bad-int 坏例 + 日期（02-01～02-10）。事实全文落 `docs/wayfinder/research/0055-featured-fog-facts.md`（六项分节 + 缺口清单 8 条），本工单不重述。

对后续工单最关键的五个事实：① 数据条四项**只有「可下载产品」有断言**——「篇技术文章」= post-items 的 all 片（含派生文）、分类数、最近更新三项无牙；② `/posts/`、分类页、标签页**同走主题层 `list.html`**（`union .RegularPages .Sections` → `.Paginate`，无显式排序，站内无 weight 字段故实际 = 日期倒序），列表/term 页**零专属断言**；③ 徽标先例现成：文章页 `single.html` 与列表卡片 `list.html` 均有 Draft `entry-hint` 徽标（DOM + CSS 齐备），但**无任何测试引用**；④ `post-items.html` docstring 只登记唯一调用方（index.html），**无「禁止其他调用方」的硬边界**——雾区③若复用该 seam 无守门；⑤ fixture 基建齐备（4 featured + false + newest + 两坏例），但 SOP 侧 featured 坏值无 fixture、真实 SOP 条目零精选。缺口 8 条中与 0056-0058 直接相关的：数据条三项无牙（0057）、列表页无断言（0058）、徽标 DOM 无牙（0056）。

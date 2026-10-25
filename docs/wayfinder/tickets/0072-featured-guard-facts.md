---
id: "0072"
title: featured 类型守卫现状事实底座（盘点）
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-featured-type-guard.md
created: 2026-10-25
claimed: 2026-10-25
closed: 2026-10-25
---

## Question

featured 类型守卫单模块化的事实底座——三处守卫拷贝 + 三种谓词形态 + 测试覆盖的盘点。本图后续所有决策的事实前提，只查事实、不做决策、不给推荐。要盘清七项：

1. **三处守卫拷贝逐行比对**：`layouts/partials/post-items.html`（约 :38-44）、`layouts/partials/product-items.html`（约 :36-42）、`content/posts/_content.gotmpl`（约 :62-71）——各自的 `isset` 判据、类型检查写法（`printf "%T"` + `ne "bool"`）、`errorf` 消息前缀与参数、遍历模式（全量 vs 条件）、数据访问方式（`.Params.featured` / `$p.featured` / `$entry.featured`）。逐字重复的部分 vs 真实差异的部分，逐类标出。
2. **三种谓词形态**：`where $pages "Params.featured" true` / `where $items "featured" true` / `eq .Params.featured true`——各自所在文件行号、消费方、语义；`featured-badge.html` docstring 自称谓词与守卫「同源」的原文摘录。
3. **坏值测试覆盖全清单**：`tests/assert_site_contracts.py` 中文章侧两例（`content-posts-bad` / `content-posts-bad-int`，期望子串「文章精选数据：」）与产品侧一例（`bad/products/featured-not-bool`）的断言函数名 + 锚定构建 + fixture 内容；`tests/assert_sop_pipeline.py` 中 featured 相关断言（`assert_featured_passthrough` 等）——**SOP 侧是否有 featured 坏值 fixture**（排图日自查：`bad/sop/` 下六个用例无 featured 坏例，待确认）。
4. **三种数据形态的键访问行为**：`.Params`（Page）与 `hugo.Data.products` / `hugo.Data.sop`（map）在 `isset` / `index` / 键大小写规范化上的行为差异——Hugo 官方文档或官方集成测试佐证；`where "Params.featured" true` 对 bool true 的匹配语义（是否只匹配 bool true、对字符串/整数的行为）。
5. **errorf 消息前缀与测试期望的对应关系**：三前缀各自被哪些测试钉住（函数名 + 期望字面量）；消息改动会影响哪些断言。
6. **三处拷贝的调用方与渲染链位置**：post-items（首页精选链唯一数据准备）、product-items（索引链唯一读 products）、_content.gotmpl（SOP 派生）——各自 docstring 中与 featured / 守卫相关的契约原文摘录。
7. **Hugo partial 的可用机制事实**：partial 能否 `return` 值、能否 `errorf`、能否被 `_content.gotmpl`（站点层 content 适配器）与主题层模板双向调用（查找序：站点层优先、主题层兜底）——官方文档佐证；站点层调用主题层 partial 的仓内现成先例（如 `layouts/index.html` 调 `featured-badge.html`）。

产物：`docs/wayfinder/research/0072-featured-guard-facts.md`，前 6 项逐条带 `文件:行号` 证据；第 7 项标注来源；结尾给「缺口清单」（现有断言未覆盖、且本图需要决策的问题面）。只查事实，不做决策，不给推荐。

环境注意：本 shell 的 grep 对 `\|` 交替失效，内容搜索用 Grep 工具；除研究产物文件外不得修改任何仓库文件；不得执行 git 写操作；不得运行 hugo 构建（以读源码与既有 `public/` 产物为准）。

## Resolution

2026-10-25 · research（AFK）：研究子代理完成七项盘点，事实全文落 `docs/wayfinder/research/0072-featured-guard-facts.md`（173 行，七节 + 缺口清单 8 条；Write 长内容丢参数，子代理分 4 段写入并复读自查完整）。主代理抽查核实五处关键证据：三处守卫拷贝行号与逐字同构（post-items.html:38-44 / product-items.html:36-42 / _content.gotmpl:62-71）、`bad/sop/` 六用例无 featured 坏例、fixture 适配器与真实 seam 逐字节一致（diff IDENTICAL）、主题层零调用站点层 partial（grep 无命中）、研究产物指向本地图的行号指针（:36 雾区条）准确。本工单不重述事实，以研究产物为准。

对后续工单最关键的五个事实：① 守卫四件套（`isset` + `printf "%T"` + `ne "bool"` + errorf）三处**逐字同构**，差异仅在数据访问路径、遍历模式（文章侧独立循环 / 产品侧与 kind 门禁合循环 / SOP 侧与五类检查合循环）、消息前缀与定位参数；② 谓词三形态各有真实差异——文章侧无条件 `where`、产品侧**条件** `where`（入参开关）、徽标单页 `eq`（docstring 自称与守卫「同源」但分开实现）；③ 坏值覆盖文章 2 例 + 产品 1 例，**SOP 侧零 fixture、零钉子串**（`_content.gotmpl:68` 的 errorf 无任何测试钉住）；④ `.Params` 键小写化有官方 isset 页显式声明、数据 map 键原样——本仓三源全小写书写故当前不可观测，跨源统一接口时成为问题面（归 0074）；⑤ Hugo partial 可 return / 可 errorf、查找序站点层优先，站点层调主题层 partial 有现成先例（index.html 调 featured-badge/post_meta/pagination 三处），**theme→site 调用零先例**（ADR-0012 否决过）。缺口 8 条中与 0073-0077 直接相关的：SOP 坏例与消息钉子（0077/0076）、徽标跨层归属（0073/0075）、键大小写（0074）、where 行为差异无守门（0073/0077）。

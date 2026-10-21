---
id: "0035"
title: 精选机制事实底座（现状盘点）
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-featured-mechanism.md
created: 2026-10-21
claimed: 2026-10-21
closed: 2026-10-21
---

## Question

精选机制的现状盘点——本图后续所有决策的事实前提，只查事实、不做决策。要盘清六项：

1. **文章侧 featured 的现状**：`hugo.toml` 参数、`archetypes/default.md`、站点层 `layouts/`、主题层 `themes/maplemod/layouts/`、`content/posts/*.md` front matter 中是否存在任何 featured 读取或声明（含易混淆项：主题 `get-page-images.html` 的 `$resources.GetMatch "*feature*"` 是 og 图资源匹配，与精选机制无关，须显式区分）。
2. **首页「精选文章」区的真实选文规则**：`layouts/index.html` 的取数表达式、与分页集合的关系、同页「最近更新」网格是否同源（去重问题的存在性证据）。
3. **产品侧已锁契约的清单化**（供文章侧对齐时引用，不重新推导）：`product-items.html` 入参语义、短代码接口、首页调用点、`data/products.yaml` 现状、`assert_product_states.py` 里与 featured 相关的断言清单。
4. **测试 fixture 机制对文章侧的可扩展性**：`tests/hugo.test.toml` 的覆盖范围（只 dataDir？）、fixture 构建时 `content/` 用的是真实目录还是 fixture、由此带来的连带效应（`hugo.Data.sop` 是否为空、派生文是否消失）、若新增 contentDir 覆盖会与 SOP 管线产生什么冲突面。
5. **SOP 派生文 front matter 的生成点与可扩展字段位**：`_content.gotmpl` 的 `AddPage` dict 结构，featured 若要进入派生文需落在哪一层（params vs 顶层），以及现有四类契约 errorf 的位置。
6. **内容盘点与断言覆盖缺口**：现有手写文章数（含脚手架）、注册表条目数与 slug、首页当前「精选」3 篇分别是谁；文章侧精选相关断言的有无；`layouts/_default/index.json` 是否含 featured（候选 8 边界确认，不决策）。

产物：`docs/wayfinder/research/0035-featured-mechanism-facts.md`，逐条带文件:行号证据。

## Resolution

2026-10-21 · research（AFK，agent 独立完成）：事实落 `docs/wayfinder/research/0035-featured-mechanism-facts.md`。

六项结论摘要：

1. **文章侧 featured 零实现**——`hugo.toml` 无参数、`archetypes/default.md` 无字段、站点层与主题层模板无读取点、5 个手写 `.md` 无声明。唯一 grep 命中是主题 `get-page-images.html` 的 og 图资源匹配（`*feature*`），**与精选机制无关**，后续工单勿误引。
2. **首页「精选文章」= 最新 3 篇**：`layouts/index.html:81` 的 `first 3 ($pages.ByDate.Reverse)`，`$pages` 即 `where site.RegularPages "Type" "posts"`（:9-10）；同页「最近更新」网格用 `$paginator.Pages`（:122），**同一个 `$pages` 分页而来**——当前精选 3 篇必然与网格前 3 篇重复，去重是真实问题而非假设。
3. **产品侧契约齐备**：`product-items.html` 的 `featured` 缺省 false + `where featured true` + `limit`（缺省/0=全量，负数 errorf）；短代码透传 `featured/limit/filters`；首页 `:110-111` 调 `featured true, limit 3`；`data/products.yaml` 5 条（3 true / 2 false）；断言 4 条（fixture 前 3 featured、第 4 条被 limit 截断、非 featured 不上首页、真实数据 yaml 序）。
4. **fixture 只覆盖 dataDir**：`tests/hugo.test.toml` 单键 `dataDir = "tests/fixtures/data"`，注释明示「只覆盖 dataDir」；`content/` 用真实目录，因此 fixture 构建里 `hugo.Data.sop` 为空 → **派生文 0 篇**，手写文章仍在。文章 fixture 必须新增 `contentDir` 覆盖（与 dataDir 覆盖可叠加），并接受「fixture 内无派生文」这一既有事实——除非同时造 SOP 注册表 fixture（会牵动 0005 契约，须在 0039 决策）。
5. **派生文 front matter 唯一生成点** `_content.gotmpl:61-69` 的 `AddPage` dict：`path/title/description/draft/dates/content/params(categories,tags)`。featured 若入派生文，**必须落 `params` 内**（顶层非官方 page map 契约字段），四类契约 errorf 在 :34-55。
6. **内容与缺口**：手写 5 个 `.md`（`docker-common-commands`、`aiops-state-and-tools`、`k8s-common-commands`、`sop-ops-tools-index`、`my-first-post1` 脚手架 `draft: true`）；注册表 6 条（ansible / gitlab / jenkins / prometheus / sonarqube / grafana）；**首页当前「精选」3 篇 = 生产构建实测的按日期最新 3 篇：`sop-ops-tools-index`（手写）+ `sop-prometheus`（派生）+ `sop-grafana`（派生）——手写与派生混排**，即派生文今天就占着精选位；**文章侧精选零断言**；`index.json` 投影字段无 featured（候选 8 边界确认，不决策）。

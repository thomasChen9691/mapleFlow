---
id: map-featured-mechanism
title: 精选机制图（候选 7）
labels: [wayfinder:map]
status: open
created: 2026-10-21
---

# 精选机制图（候选 7）

## Destination

候选 7「精选机制」的决策集定稿：文章侧 featured 契约（字段语义、派生文归属）、首页精选文章区的选择与呈现行为、模块的架构落点（seam 划分）、测试缝与导航契约——达到「可测试、AI 可导航」的可施工状态即收口。产品侧 featured 契约已由 ADR-0006 锁定，本图不重开，只在跨类语义一致性上做确认。本图只产决策；施工按候选 5/6 先例，经项目负责人指示后展开。

## Notes

- **边界（开图时与项目负责人钉死，2026-10-21）**：候选 7 = 精选机制**整体治理**（文章 + 产品两类内容）；产品侧已锁契约不重开；不改搜索索引投影（候选 8）；不调视觉/CSS 参数；不动内容填充（about.md、products.yaml 的 buy_url 等卡用户材料）。
- 术语以根目录 `CONTEXT.md` 为准；「精选 (Featured)」条已存在（声明覆盖文章与产品两类），本图只确认/微调，不另造同义词。
- 闭卷 ADR：0001（生产构建命令）、0002（no-js 渐进增强基线）、0004（产品状态模块）、0005（SOP 发布管线）、0006（产品索引双 seam，**含产品侧 featured 语义：缺省 false、where true、limit 截断、负数 errorf**）、0007（reveal 协议）、0008（主题 fork 与分层契约）。
- 方向已 ratified（2026-10-15 起多份 handoff，及候选 4/5/6 地图 Out of scope 记录）：给文章加 featured 字段，首页「精选文章」区块改真精选。本图不重开方向，只把落地面的决策钉死。
- Hugo 0.164 语义编写（CI 钉版）：0.166+ 的条件多 return 写法本地过、CI 红，禁止。
- 测试总原则：Hugo 无模板单测，静态产物只能 build-then-assert；fixture 基建单份（ADR-0004/0006 枪毙第二实现）；变异检验 + 独立字面量期望值（ADR-0007 先例）。
- 分层判据（ADR-0008）：因视觉 / 骨架 / 交互而变 → 主题层；因内容策略 / 数据结构而变 → 站点层；两层不得存在同相对路径文件。
- 用户是项目负责人：HITL 工单必须实时对话解决，agent 不得自答；事实自己查，决策问用户；一次一问，先给推荐答案。
- 事实底座：`research/0035`（文章侧零实现、首页选文实为「最新 3 篇」、产品侧契约与断言清单、fixture 只覆盖 dataDir 对文章侧的扩展缺口）。后续工单的事实争辩以该份为准，不重新推导。
- 排图日 2026-10-21：研究工单 0035 当日解决，事实落 `research/`，本图只留 gist。

## Decisions so far

- [精选机制事实底座（现状盘点）](tickets/0035-featured-mechanism-facts.md) — 文章侧 featured **零实现**（hugo.toml / archetype / 模板 / 内容全无），首页「精选文章」实为 `first 3 ($pages.ByDate.Reverse)` 即最新 3 篇，且与同页「最近更新」网格同源必然重复；**当前精选位实测为手写 1 篇 + 派生 2 篇混排**（派生文今天就占精选位）；产品侧契约与 4 条断言齐备（featured 缺省 false / limit 截断 / 非 featured 不上首页 / 真实数据 yaml 序）；测试 fixture **只覆盖 dataDir**（hugo.test.toml 单键），文章 fixture 需新增 contentDir 覆盖且会连带清空 `hugo.Data.sop`（派生文 0 篇）；SOP 派生 front matter 唯一生成点 `_content.gotmpl:61-69`（params 仅 categories/tags）；搜索索引不含 featured（候选 8 边界确认）；现有内容 5 手写（含 1 脚手架 draft）+ 6 派生。

## Not yet specified

<!-- 雾区：在目的地内、但还无法精确表述的问题。随 frontier 推进毕业为工单。 -->

- **「精选」标识在内容层的呈现**：文章页 / 列表页是否显示精选徽标、卡片是否有视觉区分——语义未决，且紧邻视觉层边界（视觉调值本身 out of scope）。
- **首页数据条与精选的关系**：「篇技术文章」计数是否区分精选、是否新增「精选 N 篇」类数字。
- **分类页 / 标签页是否消费精选**：文章列表排序是否 featured 优先，还是精选只作用于首页。
- **精选条数的可配置性**：固定字面量 3 vs `hugo.toml` 参数（受 AGENTS 参数纪律约束：无读取点即死配置）——待 0037 定行为后判断是否独立成题。

## Out of scope

- **搜索契约**（`index.json` 投影字段 + fastsearch + kind 门禁）：候选 8（0019/0026/0008 边界注记）。
- **视觉 / CSS 参数调值**（精选卡片样式、动效时长、降级阈值）：视觉层（候选 5 地图先例）。
- **产品侧 featured 契约重开**（缺省语义 / limit / 负数 errorf）：ADR-0006 已锁，本图只引用不重开。
- **内容填充**（`data/products.yaml` 的 buy_url/listed、`content/about.md` 真实简历、socialIcons 真实邮箱、删脚手架文章）：卡用户材料，不随图（候选 5/6 先例）。
- **后端重启时的产品数据源替换**：ADR-0006 已定，届时只动 `product-items.html` 一处。
- **菜单 `parent` 子项渲染**（4 个 categories 子项配置了不渲染）：独立新需求，不属精选机制。

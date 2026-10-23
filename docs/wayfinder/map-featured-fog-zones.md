---
id: map-featured-fog-zones
title: 精选雾区图（候选 13）
labels: [wayfinder:map]
status: closed
created: 2026-10-23
closed: 2026-10-23
---

# 精选雾区图（候选 13）

## Destination

把精选机制从 ADR-0009 已锁的「首页精选块」深化到内容层其余三面——**精选标识的呈现 / 首页数据条 / 分类·标签页的消费**：逐面定案「做不做、落点、契约定义处、测试缝」，使精选模块整体达到可测试、AI 可导航的可施工状态即收口。从现状深化，不重开 ADR-0009 已锁决策；本图只产决策，施工经项目负责人指示后展开。

## Notes

- **边界（开图时与项目负责人钉死，2026-10-23）**：本图 = `docs/backlog.md` 第 13 项 = ADR-0009 Consequences 边界条留的三条雾区（① 徽标内容层呈现 ② 首页数据条区分精选 ③ 分类/标签页消费精选）；**不重开 ADR-0009 已锁五组决策**（字段契约 / 首页精选行为 / seam 形状 / 测试缝 / 派生文归属——那是本图的输入，不是重开对象）；产品侧 featured 契约不重开（ADR-0006 已锁）；搜索索引不投影 featured 已由 ADR-0010 定案（不属本图）；不替换/不改精选实现本身；**视觉 / CSS 调值 out of scope**（本图只定语义契约与 DOM 契约，样式值归视觉层）；不随图做内容填充（buy_url/listed、about.md、socialIcons）。
- **工单纪律（项目负责人开图时明确）**：每张工单是**待决策问题**、不是施工任务；一次会话最多解决一张（research 除外）；地图是索引不是仓库，决策只存在于工单。
- **0060（meta 投影）的范围说明**：0056 定案（精选标识进文章页）后毕业的新观察点——meta 层投影问由「不可表述」变为可精确表述，属本图范围内（destination 三面的直接后果，非范围外新需求）；已随收口批解决（负向：无消费方不投影，ADR-0012 决策 5）。
- 闭卷 ADR：0002（no-js 渐进增强基线）、0004（**首页数据条独立于产品索引链**的先例——计数口径归站点层 index.html，模板不自行推导产品状态）、0005（SOP 发布管线——精选池含派生文）、0006（产品侧 featured 已锁）、0008（**分层判据：分类/标签页与文章页渲染在主题层 `list.html`/`single.html`——站点层覆盖还是主题层直改，是 0058/0056 的真问题；两层不得存在同相对路径文件**）、0009（本图主输入）、0010（投影六字段冻结、featured 不投影已定）。
- Hugo 0.164 语义编写（CI 钉版）：0.166+ 的条件多 return 写法本地过、CI 红，禁止。
- 测试总原则：Hugo 无模板单测，静态产物只能 build-then-assert；fixture 基建单份（三套构建：dataDir fixture / contentDir fixture / 真实数据——**ADR-0009 决策 4 为精选新增的 contentDir fixture 是现成基础，不新开第四套**）；变异检验 + 独立字面量期望值；fixture 日期一律过去日（Hugo 不发布未来内容 → 假绿，坑点 12）。
- 分层判据（ADR-0008）：因视觉 / 骨架 / 交互而变 → 主题层；因内容策略 / 数据结构而变 → 站点层。三条雾区的落点都可能触发此判据，逐票落定。
- 用户是项目负责人：HITL 工单必须实时对话解决，agent 不得自答；事实自己查，决策问用户；一次一问，先给推荐答案。
- 术语以根目录 `CONTEXT.md` 为准；本图可能扩写「精选 (Featured)」条（措辞归收口工单 0059，排图期不预设用词）。
- 事实底座：`research/0055`（排图日由研究子代理落盘）。后续工单的事实争辩以该份为准，不重新推导。
- 环境注意（历图传承）：本 shell 的 grep 对 `\|` 交替失效，内容搜索用 Grep 工具。

## Decisions so far

<!-- 索引：每个已决工单一行 gist + 链接；决策详情只存在于工单，此处不重述。 -->

- [三条雾区现状事实底座（盘点）](tickets/0055-featured-fog-facts.md) — 数据条四项**只有「可下载产品」有断言**（「篇技术文章」= post-items 的 all 片含派生文、分类数、最近更新三项无牙）；`/posts/`、分类页、标签页**同走主题层 `list.html`**（union→Paginate，无显式排序、站内无 weight 字段故实际=日期倒序），列表/term 页**零专属断言**；徽标先例现成——`single.html` 与 `list.html` 均有 Draft `entry-hint` 徽标（DOM+CSS 齐备但无测试引用）；`post-items.html` docstring 只登记唯一调用方（index.html）、**无硬边界守卫**；fixture 齐备（4 featured + false + newest + bad/bad-int 两坏例）但 SOP 侧坏值无 fixture、真实 SOP 条目零精选。缺口 8 条（详见工单 Resolution）。
- [精选标识进入内容层：三面 + 主题层 partial + fixture 三面锚定](tickets/0056-content-layer-badge.md) — **做，三面**：文章页（single）+ 列表卡片（分类/标签/posts）+ 首页网格卡片；**精选行不加**（区块标题已表达）。契约 = **主题层新 partial `featured-badge.html`**（docstring 定义处，复刻 post_meta 调用先例、零新分层先例），三处调用、单一标记实现；坏值执法继承 `post-items.html:32-38` 全局 errorf（非布尔 featured 首页构建即炸），徽标谓词 `eq .Params.featured true` 无需新执法点；测试 = **fixture 三面全锚**（single / term+posts 列表 / 首页网格——截断回落的 feat-a 是天然样本），真实不锚（ADR-0009 原则），变异检验强制。视觉值 out of scope。**本票毕业新工单 0060**（meta 投影问）。frontier = 0057。
- [首页数据条不区分精选（负向）](tickets/0057-home-databar-featured.md) — **不做**：数据条维持站点总量口径。抽象层不分层（总量 vs 编排）、信息冗余（all 片已含精选且精选区就在下方）、断言经济学（三项已无牙，不给第四个冗余数字纳税）。重开触发 = featured 规模远超 3 条且网格无法完整表达。frontier = 0058。
- [分类/标签页不消费精选（负向）+ seam 边界收紧](tickets/0058-taxonomy-featured-consumption.md) — **不做，三页统一**：分类/标签/posts 维持日期倒序——term 页意图是「找新文章」、置顶挤压曝光、断言面从零建且期望值耦合 Hugo 默认排序链。边界守门 = **post-items docstring 收紧硬边界措辞**（落地归 0059，与坑点 11 同步句同批）+ 否掉产物断言（锁 Hugo 排序链现状、误红风险）。
- [收口：术语、导航与 ADR 耐久化](tickets/0059-closure-terminology-adr.md) — **本题关闭 = 地图 closed，frontier 空 = 目的地到达（决策面）**。ADR 形态 = **新开 ADR-0012**（五组决策耐久化）+ ADR-0009 指针行（正文不改）；术语 = CONTEXT.md「精选」条只扩徽标面一句（三面呈现 + featured-badge.html 指针，负向边界不进术语表）；导航 = AGENTS 坑点 11 补四条纪律 + §7 加 featured-badge.html 行；收口批同落：post-items docstring 收紧（0058 转入）+ backlog 第 13 项完成 + handoff（`docs/handoffs/2026-10-23-featured-fog-zones-closure.md`）+ 0059/0060 Resolution + assert_site_contracts 87/87 复跑全绿。**施工批（partial + 三处调用 + fixture 断言）待项目负责人指示。**
- [meta 层不投影精选（负向）](tickets/0060-meta-layer-featured-projection.md) — **不做**：schema_json（BlogPosting）/ opengraph / twitter_cards 不投影精选状态。ADR-0010 决策 4 同款纪律——无消费方不投影；schema.org 无 featured 概念、og 无 article:featured 类标准属性，自造字段没有第二个读者；徽标服务页面内的眼睛、meta 服务抓取与分享的机器，两层无强制同步。

## Not yet specified

<!-- 雾区：在目的地内、但还无法精确表述的问题。随 frontier 推进毕业为工单。 -->

（排图时的三条雾区观察点已全部处理：一条毕业为工单，两条随负向决议消解。）

- **已毕业为工单并已决（负向）**：「结构化数据 / 社交元数据是否反映精选状态」（`schema_json.html` / `opengraph.html`）——0056 决议一（文章页出现精选语义）触发毕业为 [0060](tickets/0060-meta-layer-featured-projection.md)，质询定案**不做**（无消费方不投影，ADR-0010 决策 4 同款；ADR-0012 决策 5）。
- **已消解**（0058 决议一负向）：「RSS 输出是否受分类页排序决议影响」——term 页不 featured 优先，RSS 无跟随对象；订阅流维持现状。
- **已消解**（0057 负向）：「数据条计数的语义从属关系」——数据条口径不动，「篇技术文章」维持全集口径，无从属问题存在。

## Out of scope

- **重开 ADR-0009 已锁决策**（字段契约 / 首页精选行为 / seam 形状 / 测试缝 / 派生文归属）：本图只在其上加面，不改已锁部分；认为 ADR-0009 错了先提重审（工程纪律 2）。
- **产品侧 featured 契约**（缺省语义 / limit / 负数 errorf / 坏值校验）：ADR-0006 + ADR-0009 指针已锁。
- **搜索索引投影 featured**：ADR-0010 决策 4 负向已定（无消费方），候选 8 闭环。
- **视觉 / CSS 调值**（徽标样式与图标、数据条排版数值、列表卡片视觉区分）：视觉层（候选 5/6/7 先例）；本图只定「有没有、在哪、DOM 契约是什么」。
- **精选文章手工排序**（`weight` 字段）：ADR-0009 Considered Options 已否。
- **数据条其他计数项的口径改造**（分类数 / 产品数 / 最近更新）：不属精选雾区，动它们是新需求。
- **内容填充**（`data/products.yaml` 的 buy_url/listed、`content/about.md` 真实简历、socialIcons 真实邮箱）：卡用户材料，不随图。
- **施工批次与 CI 验证节奏**：本图只到「可施工状态」，施工经项目负责人指示后展开（候选 7/12 先例）。

id: "0056"
title: 精选标识是否进入内容层（雾区一）
type: grilling
mode: HITL
status: closed
blocked_by: ["0055"]
assignee: agent
map: map-featured-fog-zones.md
created: 2026-10-23
claimed: 2026-10-23
closed: 2026-10-23
---

## Question

「精选」标识是否在内容层呈现（文章页 / 列表页 / 卡片）？这是 ADR-0009 边界条留悬的第一条雾区，本票把它定到可施工精度。

要决策的面：

1. **做不做**：精选标识是否进入内容层（文章页 `single.html` / 分类·标签·posts 列表页 `list.html` / 首页网格卡片 / 精选行自身）？若不做，记录负向决策与理由（精选只以「首页精选区」这一种形态存在是否自洽）。
2. **哪些面**：若做，上述四个面各自呈现与否——可以只做文章页、也可以全做，逐面定。
3. **契约落点**：呈现的语义契约定义处落哪——徽标是主题层模板行为（`single.html`/`list.html` 直改，参考 Draft `entry-hint` 先例）还是站点层 partial？DOM 契约（class / data-* / aria）写进哪个 docstring？分层判据（ADR-0008）怎么用？
4. **测试缝**：断言怎么锚（哪些构建、锚哪些 DOM 契约、坏值/缺省要不要覆盖——注意 featured 字段契约已由 ADR-0009 锁死，本票不重开）。

边界（不开票）：徽标的视觉样式（颜色 / 字号 / 图标长相 / 动效）归视觉层，本票只定「有没有、在哪、契约是什么」；结构化数据 / 社交元数据是否同步反映精选状态已入地图雾区（取决于本票决议形状），本票不决。

事实前提以 `research/0055` 为准（第 3 项：徽标现状与 DOM 契约；第 4 项：seam 接口面）。

## Resolution

2026-10-23 · grilling（HITL，项目负责人四问全决）：

**决议一（做不做 / 哪些面）**：**做，三面**——文章页（`single.html`）+ 列表卡片（分类/标签/`/posts/`，即 `list.html`）+ 首页网格卡片（站点 `index.html`）；**首页精选行不加**（区块标题「精选文章」已表达，行内徽标冗余）。理由：① 信号缺口真实——访客从文章页/列表页落地时无任何精选信号；② 成本低——Draft 徽标证明 DOM+CSS 先例齐备；③ 首页网格**可能**合法含 featured（被 limit 截断的精选回落到网格，ADR-0009 硬约束），徽标区分它们；④ **坏值执法已被全局托管**——`post-items.html:32-38` 的 errorf 循环遍历全部文章，非布尔 featured 在首页构建时即失败，徽标谓词 `eq .Params.featured true` 继承该守卫，无需新执法点。

**决议二（契约落点 / 模块形状）**：**主题层新 partial** `themes/maplemod/layouts/partials/featured-badge.html`，**docstring = 契约定义处**（class / title 文案 / 谓词语义 / 调用面清单），由 `single.html`、`list.html`、站点 `index.html` 网格三处调用。理由：① 单一标记实现，杜绝三处拷贝漂移（第二实现风险，本项目纪律明确过敏）；② 复刻 `post_meta.html` 先例——theme partial 被站点层调用已有先例（`index.html:138`），零新分层先例；③ 徽标归呈现行为，按 ADR-0008 判据属主题层。否决项：三处内联（Draft 式拷贝）、站点层 partial（theme→site 调用是全仓新先例且分层反转）。

**决议三（测试缝 / 哪些测试能存活）**：**fixture 三面全锚**——挂 contentDir fixture 构建：① featured 文章 single 产物有徽标、false/未声明文章无；② term 与 `/posts/` 列表产物同理；③ 首页网格产物（截断回落的 feat-a 是天然样本）。**真实构建不锚**（ADR-0009「真实精选清单不锚」原则——真实 featured 由项目负责人掌控）；**变异检验强制**。Draft 徽标零测试的现状不碰（草稿不进生产构建，补测需 `-D` 构建，属另一件事）。

**边界（随票挂起）**：视觉值（颜色/字号/图标）归视觉层 out of scope，本票只定 DOM 契约；结构化数据/社交元数据是否同步反映精选状态——由本票决议一（文章页出现精选语义）触发毕业为新工单 **0060**，不在本票范围。

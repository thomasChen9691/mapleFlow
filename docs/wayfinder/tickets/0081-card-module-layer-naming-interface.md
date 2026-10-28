---
id: "0081"
title: 卡片单模块的层归属、命名与入参契约
type: grilling
mode: HITL
status: closed
blocked_by: ["0080"]
assignee: agent
claimed: 2026-10-27
closed: 2026-10-28
map: map-architecture-deepening.md
created: 2026-10-27
---

## Question

卡片单模块落在哪一层、叫什么、入参怎么定——「单模块」的**形状**问题。0080 定了能力面，本票定它的物理位置与接口。

现状：两处卡片分别住在站点层（`layouts/index.html`）与主题层（`themes/maplemod/layouts/_default/list.html`）；卡片内部已经调用两个主题 partial（`featured-badge.html` / `post_meta.html`）与一个主题 partial（`cover.html`，仅列表侧）。ADR-0008 判据「因视觉 / 骨架 / 交互而变 → 主题层；因内容策略 / 数据结构而变 → 站点层」，且两层**不得存在同相对路径文件**；站点层调主题层 partial 有现成先例，**主题层调站点层零先例**（ADR-0012 曾否决）。

要决策的面：

1. **层归属**：主题层（视觉骨架的归位，站点层首页调用它）还是站点层（与 `post-items` / `product-index` 同族，主题层列表调用它）。选后者要正面回答 theme→site 先例问题。
2. **命名**：`post-card.html` / `post-entry.html` / `post-item.html`——与既有 `post-items`（数据准备）、`featured-badge`、`post_meta`、`post-nav` 的命名族如何对齐；术语表是否新增「文章卡片」词条（对照「守卫」不收的先例，ADR-0015 决策 12）。
3. **入参形态**：单页 `Page` + 变体 dict（`class` / `cover` / `draft` / `meta` 开关），还是调用方算好 `class` 字符串传入；必填项与缺省值；是否自校验（对照 `product-index` 的自校验先例与 `featured-guard` 的不自校验先例）。
4. **边界声明**：卡片只渲染**单页**，不做选择 / 截断 / featured 判定 / 补集（这些归 `post-items`）；`first-entry` 变体若保留，是入参还是调用方包一层。
5. **与 `post_meta` / `featured-badge` / `cover` 的关系**：直接调用（现状）还是由卡片转交参数；`compact` 之类的入参是否要上提到卡片接口。

边界（不开票）：数据准备与精选语义归 ADR-0009；`featured-guard` 的执法不动；视觉重设计属 Out of scope。

## Resolution（决议已定，施工未开始）

2026-10-27 · grilling（HITL，项目负责人三问定案；与 0080/0083/0084 同场 grill）。

**Q1 层归属 = 主题层**：`themes/maplemod/layouts/partials/post-card.html`。判据 ADR-0008（卡片是视觉骨架）；两个消费方都能调（site→theme 有现成先例）；内部三个 partial（`cover` / `featured-badge` / `post_meta`）同层自洽。**未选站点层，故不重开 ADR-0012 的 theme→site 否决**。

**Q2 命名 = `post-card.html`**：与 `post-items` / `product-index` / `featured-badge` / `post_meta` 同族。术语表是否新增「文章卡片」词条留 [0088](0088-closure-adr-terminology-navigation.md)。

**Q3 入参 = 零参数**：只收 page（传 Page 还是 `dict "page" .` 属施工细节，倾向直接传 Page，与 `featured-badge.html` 同风格）。三个分支不暴露开关——为不存在的输入参数化属投机泛化（ADR-0015 决策 6 同款判据）。

**Q4 父容器契约显式化**（本图最硬的一条隐式契约）：`custom.css:850` 的 `main:has(.post-entry)` 把 main 变网格，835 行注释明说「首页…类名不同，不会命中这里」——**类名不同是载重的，它在当「面」的判别器**。一套类名后该规则会在首页也命中，布局塌。决议：docstring 声明「卡片不自带布局；卡片必须是网格容器的**直接子元素**」，`:has()` 改直接子选择器（`main:has(> .post-card)` / `.mf-posts:has(> .post-card)`）——首页卡在 `.mf-posts` 内、不是 main 直接子项，自然不命中。断言钉「首页卡在 `.mf-posts` 内、列表卡是 main 直接子项」（→ [0082](0082-card-module-test-seam.md)）。

**Q5 与三个 partial 的关系 = 卡片内直接调用**：`cover` 恒调、`featured-badge` 恒调、`post_meta` 以 `compact` 恒调；不向调用方转交参数。

**施工（2026-10-28，PR①）**：`post-card.html` 落主题层（`themes/maplemod/layouts/partials/`），docstring 即父容器契约定义处；类名统一为 `.post-card`；`custom.css:850` 的 `main:has(.post-entry)` 改 `main:has(> .post-card)`（三条 `.home-info/.page-header/.page-footer` 同改），单条与相邻兄弟两条 `:has()` 同步改直接子选择器；注释里「类名不同不会命中」的旧说明改写成「判别器是 DOM 位置」并加警告。

**新增断言（评审后补）**：`container_depth()` + 三条位置断言（首页卡深度 2 = 在 `.mf-posts` 内、列表/term 卡深度 0 = main 直接子项）——父容器契约此前只靠注释，无产物牙。

**验证**：site 185/185（含新增 3 条位置断言）。

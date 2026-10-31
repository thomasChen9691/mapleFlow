---
id: "0085"
title: 死面的判据与删除边界（配置 + CSS）
type: grilling
mode: HITL
status: closed
blocked_by: ["0079"]
assignee: agent
claimed: 2026-10-27
closed: 2026-10-31
map: map-architecture-deepening.md
created: 2026-10-27
---

## Question

「死面」用什么判据认定、这批删到哪一条线——范围已定（配置 + CSS，2026-10-27），本票定**判据与粒度**。

现状（排图日粗扫，待 0079 补全）：`archive.css`（44 行）与 `profile-mode.css`（43 行）零 markup 引用（无 archives / profile 布局，故整文件无主）；custom.css + 主题 CSS 共 251 个类名、**42 个零引用**，但其中 chroma（`c1` `cm` `kc` `kn`…）与 highlight 行号表（`lnt` `lntable` `linenodiv`…）是**构建期生成**、属假阳性；`hugo.toml` 有多段注释掉的 PaperMod 遗留键与少量可能零读取点的参数。

要决策的面：

1. **判据**：`零引用` 怎么定义——markup + JS + data + i18n 全无引用即为死？还是要连带看 CSS 变量链、`@media` 分支、伪类选择器、被其他选择器组合引用（`.a .b`）的情况。
2. **假阳性排除规则**：构建期生成类（chroma / highlight 表）、运行时拼接类（`'is-' + x`）、Hugo 结构类（`.highlight` / `.highlighttable`）、以及「当前无内容触发但属于合法内容形态」的类（如 `cover` 相关）——各自怎么排除，要不要维护一份白名单及其归属。
3. **删除粒度**：整文件 / 选择器块 / 单条声明；`archive.css` 这类整文件死面直接删文件，还是留空文件维持 `resources.Match` 装配（装配是通配，删文件即自动不并入）。
4. **配置侧判据**：参数「有读取点」但值恒等于 Hugo / 主题默认（如 `defaultTheme = "auto"`）算不算死面；注释掉的遗留键（PaperMod 的 disqus / utterances / waline 等）删不删；`[params.cover]` 这类「留空字典防模板解析错误」的必须保留项如何登记。
5. **守门**：是否新增「死面守门」断言（新加零引用选择器即红），还是只做一次性清理并把判据写进 AGENTS.md 坑点。这决定本票是否要连带开一条施工外的断言。
6. **与 0086/0087 的顺序**：parity 门要守的 token 集合依赖删除结果（先删再上门 vs 先上门再删）——本票给出顺序约束即可，不越界定 parity 的实现。

边界（不开票）：模板 partial 可达性与 fork 形态（0027/0029 已裁）、静态资产、i18n 键——均已判 Out of scope。

## Resolution（决议已定，施工未开始）

2026-10-27 · grilling（HITL，三问定案）。

**判据 = 四面零引用 + 三类白名单**：类名/变量在 **markup + JS + data + i18n** 四处均无字面出现即为死。白名单必须登记理由与归属文件，覆盖三类假阳性：① **构建期生成**（chroma token 如 `c1` `cm` `kc`、highlight 行号表 `lnt` `lntable` `linenodiv`、`.highlight` 结构类）；② **运行时拼接**（本仓当前无，规则先留位）；③ **渲染器产出类**。

> 判据的动机是排图日两次假阴性：一次是 shell 里带 `\|` 的 grep 静默失效，把 `is-morphing` / `is-bump` 误判成「有写无读」（实际 `custom.css:216/226` 有规则）；一次是把「只扫了两个词」当成「零处引用类名」。**工具假阴性是死面判据的头号风险**，扫描必须用 Grep 工具且双向复核。

**配置侧 = 零读取点必删 + 注释遗留键一并删 + 值恒等默认保留**：`[[params.socialIcons]]`（email/github 两条）全仓零读取点，删；注释掉的 PaperMod 遗留键（disqus / utterances / waline / backgroundImage / footerBottomText / zenMode …）按 AGENTS 坑点 3「不留文档价值」删；`defaultTheme = "auto"` 这类**有读取点但值等于默认**的保留（活配置的显式声明，Hugo 改默认时会变）。`[params.cover]` 空字典是**活配置**（`cover.html:2` 无条件访问 `.params.cover.image`，删了会模板解析错误），登记为「必须保留」而非死面。

**粒度 = 文件级 + 选择器块级；不新增死面守门**：整文件删（`archive.css` 44 行 / `profile-mode.css` 43 行——装配是 `resources.Match "css/common/*.css"` 通配，删文件自动不并入）；选择器块删（`.first-entry` 五块、`.tag-entry .entry-cover`、成对规则里死的那半）。**删块必须连带检查 `var(--x)` 引用链**：变量只被死块引用 → 一并删；仍被活块引用 → 保留（这条同时关掉了地图雾区「CSS 变量链连带断裂」那条）。**不加守门断言**：死面判定是启发式（chroma / highlight / 运行时类都要白名单），守门会误红且白名单要长期维护；防回流靠 review + parity 门覆盖 token 面。

**顺序约束 = 先删死面、再上 parity 门**（→ [0086](0086-css-shadow-contract-token-set.md) / [0087](0087-parity-gate-placement-strength.md)）：门的 token 集合必须在清理后的基线上算，否则门会先红在一批即将被删的 token 上。

**施工（2026-10-31，PR② 第一笔 `8e7b785`）**：整文件删 `archive.css`（44 行）/ `profile-mode.css`（43 行）；选择器块删 **23 处**（`breadcrumbs` / `i18n_list` / `paginav` / `share-buttons` / `in-text` / `align-center` / `home-info` / `social-icons` / `archive-*` / `button-inner`，含嵌在 `@media` 内的三条）；chroma/highlight 18 个类走白名单未删。共 **−196 行**。

**零断言改动已兑现**：`git diff --stat -- tests/` 为空，删完 site 185/185 · npm 13+31+41 · sop 105/105 全绿。**未删** `hugo.toml` 的注释遗留键——复核后判定它们已带「已删除」标注、不构成误读风险，且删注释会掩盖「这里曾经有过什么」的历史；本条与决议第 13 条的差异已记入 ADR-0016 Consequences（配置侧只执行了「零读取点」一半）。

**实施细化（2026-10-31 grilling，PR② 开工前）**
- **实测清单（PR① 后重扫）**：零引用类名 **35 个**，其中 **18 个**是 chroma/highlight 构建期类（`c1 cp cpf fm kc kp kr mh s1 s2 sb vm highlighttable linenodiv lnlinks lnt lntable lntd`）→ 白名单；文件级死面 = `archive.css`（44 行，含 9 个 `archive-*` 类）与 `profile-mode.css`（43 行，含 `profile_inner`）；选择器级死面 = `breadcrumbs` / `button-inner` / `home-info` / `i18n_list` / `in-text` / `paginav` / `share-buttons` / `align-center` / `social-icons`。
- **删除笔的验收纪律 = 零断言改动**：删完跑 site 185/185 + npm 9+28+41 + sop 105/105，**断言文件一个字符都不改**；动了断言 = 删到了活的东西，回退重判。
- **提交粒度 = 两笔**：第一笔纯删除、第二笔只加 parity 门。门其实不依赖删除（正向现状 0 违规、反向只守 6 个 `is-*` 且全有生产者），所以「先删后门」是**证据顺序**而非硬依赖——删完仍绿本身就是「没删到活的」的证据。

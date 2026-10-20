---
id: 0030
title: 分层契约：覆盖文件归并与站点层剩余
type: grilling
mode: HITL
status: closed
blocked_by: [0029]
assignee: agent
map: map-theme-fork.md
created: 2026-10-20
claimed: 2026-10-20
closed: 2026-10-20
---

## Question

fork 后「主题层 vs 站点层」的文件归属与分层契约。事实底坐：0027 覆盖表（4 个近逐字覆盖 + 2 个语义重写 + 3 个 net-new）、ADR-0002 同步义务实际范围（漏列 post_meta/opengraph，实为 4 个）。

待决问题（一次会话内按序过，先给推荐答案）：

1. **四个「近逐字覆盖」的归属**：`layouts/_default/baseof.html`（仅差 `class="no-js"`×3）、`layouts/partials/post_meta.html`（仅差时区格式）、`layouts/partials/extend_head.html` / `extend_footer.html`（主题版是注释占位）——并入 fork 内部（消除覆盖层、ADR-0002 同步义务自然关闭）还是保留站点层覆盖（保留「站点改动 vs 主题基线」的可视分界）？
2. **两个语义重写的归属**：`layouts/_default/rss.xml`（首页订阅限 Type=posts）、`layouts/_default/index.json`（截断摘要+产品段，属候选 8 边界）——哪些算「站点语义」必须留站点层，哪些可进 fork？
3. **站点 layouts/ 最终剩余面**：product-state/items/index 三 seam、shortcodes/product-index、index.html（首页自定义）确定留站点层；是否还有别的应留（如未来候选 7 精选区块）？最终站点层清单是什么——这决定 AGENTS.md/README 里「站点层」的定义。
4. **ADR-0002 同步义务的关闭方式**：ADR 是历史记录不改正文（0006→0004 加指针行先例）——ADR-0002 加指针行注明「义务已由候选 6 关闭」，还是等 0034 在新 ADR-0008 统一记载？注意 no-js 基线本身（类名 swap 机制）不重开，只处理其「文件归属与同步义务」的变迁。

决策记录：本题 Resolution 落逐文件归属表（主题层/站点层两栏）+ ADR-0002 指针方案，作为 0031（触点清单）与 0032（测试锚点）的输入。

## Resolution

2026-10-20 · grilling（五问全决，用户为决策者；施工待项目负责人指示）：

1. **分层形态 = A 合并入主题层**：站点版内容搬进 maplemod（站点版是修好过的那份），删站点覆盖。B（保留双份）否定本图存在的理由；C（解散主题层）抹掉「呈现基线 vs 内容数据」的概念边界、且红笔画掉本图前提——均排除。
2. **逐文件归属（判据=「因什么而变」：视觉/骨架/交互→主题；内容策略/数据结构→站点）**：5 进主题——`_default/baseof.html`（no-js 骨架）、`partials/extend_head.html`（class swap）、`partials/extend_footer.html`（js.Build 引擎）、`partials/post_meta.html`（时区格式）、`partials/templates/opengraph.html`（ogImage 兜底）；2 留站点——`_default/rss.xml`（首页 feed 只含 posts = 内容策略）、`_default/index.json`（搜索投影 + 读 site.Data.products = 站点数据；契约归候选 8）。**两个主题死副本删除**（主题版 rss.xml/index.json 永不执行）。
3. **站点层最终 7 文件**：`index.html`（首页内容编排）、`_default/rss.xml`、`_default/index.json`、product-state / product-items / product-index 三 seam、`shortcodes/product-index.html`；其余全部主题。覆盖机制从此只保留「站点页面模板 vs 主题默认」（如 index.html），**不再有「站点 partial 覆盖主题 partial」**。
4. **验证方案 A（合并的守门）**：合并前生产构建 → `public/` 快照 → 合并 → 重建 → `diff -r` **零差异**（事实：rss 的 lastBuildDate 用 .Lastmod、sitemap lastmod 来自内容，构建确定性成立）；三套件照跑（16/39/100，零改动存活）；不变量「站点与主题不得存在同相对路径文件」；无 localhost 残留。只跑三套件（方案 B）被拒：三套件不覆盖 baseof/head/footer/opengraph 字节，搬错文件可能全绿而线上行为已变。
5. **ADR-0002 关闭落点 = B（0034 统一落）**：0034 写 ADR-0008 + 0002 指针行；本题只记录两件事——① 同步义务随合并消失（文件唯一，无「升级时同步」可言）；② **实际范围是 5 个文件**（baseof/extend_head/extend_footer/post_meta/opengraph），ADR-0002 原文记 2 个为漏记，正文不改。

**连带事实**：`extend_head`/`extend_footer` 的「上游用户钩子」语义随合并消失——站点即主题主人，钩子退化为普通 partial，文档不得再称扩展点（0033 导航文档注意）；no-js 基线机制（ADR-0002 正文）不重开，只是随骨架移入主题。

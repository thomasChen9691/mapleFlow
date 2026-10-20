---
id: 0030
title: 分层契约：覆盖文件归并与站点层剩余
type: grilling
mode: HITL
status: open
blocked_by: [0029]
assignee:
map: map-theme-fork.md
created: 2026-10-20
---

## Question

fork 后「主题层 vs 站点层」的文件归属与分层契约。事实底坐：0027 覆盖表（4 个近逐字覆盖 + 2 个语义重写 + 3 个 net-new）、ADR-0002 同步义务实际范围（漏列 post_meta/opengraph，实为 4 个）。

待决问题（一次会话内按序过，先给推荐答案）：

1. **四个「近逐字覆盖」的归属**：`layouts/_default/baseof.html`（仅差 `class="no-js"`×3）、`layouts/partials/post_meta.html`（仅差时区格式）、`layouts/partials/extend_head.html` / `extend_footer.html`（主题版是注释占位）——并入 fork 内部（消除覆盖层、ADR-0002 同步义务自然关闭）还是保留站点层覆盖（保留「站点改动 vs 主题基线」的可视分界）？
2. **两个语义重写的归属**：`layouts/_default/rss.xml`（首页订阅限 Type=posts）、`layouts/_default/index.json`（截断摘要+产品段，属候选 8 边界）——哪些算「站点语义」必须留站点层，哪些可进 fork？
3. **站点 layouts/ 最终剩余面**：product-state/items/index 三 seam、shortcodes/product-index、index.html（首页自定义）确定留站点层；是否还有别的应留（如未来候选 7 精选区块）？最终站点层清单是什么——这决定 AGENTS.md/README 里「站点层」的定义。
4. **ADR-0002 同步义务的关闭方式**：ADR 是历史记录不改正文（0006→0004 加指针行先例）——ADR-0002 加指针行注明「义务已由候选 6 关闭」，还是等 0034 在新 ADR-0008 统一记载？注意 no-js 基线本身（类名 swap 机制）不重开，只处理其「文件归属与同步义务」的变迁。

决策记录：本题 Resolution 落逐文件归属表（主题层/站点层两栏）+ ADR-0002 指针方案，作为 0031（触点清单）与 0032（测试锚点）的输入。

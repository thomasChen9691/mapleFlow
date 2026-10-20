---
id: 0027
title: 主题 fork 事实底座（本地盘点）
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-theme-fork.md
created: 2026-10-20
claimed: 2026-10-20
closed: 2026-10-20
---

## Question

候选 6 开图前的本地事实底座（本工单只产事实、不产决策）：

1. **子模块状态**：gitlink 与 dirty 工作区的真实构成（交接文档称「纯行尾、gitlink 未变」——须复核）、LICENSE/README/theme.toml 的在位性与版本语义来源。
2. **面内盘点**：站点内容实际经过哪些主题布局/partial（首页自定义、single/list/terms/search/404、archives 是否可达）、主题短代码在 content/ 的引用统计、主题 25 个 partial 的触达两栏（可达/不可达）。
3. **覆盖面对应表**：layouts/ 下每个文件覆盖 themes/PaperMod 哪个同名文件还是 net-new；ADR-0002 所称「两个覆盖文件同步义务」是否漏列。
4. **测试缺口**：tests/ 三套件当前对「主题渲染产物」的断言面；主题行为中零断言的清单（no-js/js swap、post_meta 时区、菜单与 URL 形态、RSS、404、list/taxonomy、search 页）。
5. **构建链触点**：移除子模块后必须同步修改的文档/脚本清单（CI deploy.yml、AGENTS.md、README、auto_push.py、.gitmodules）。

## Resolution

2026-10-20 · research（agent 驱动，结论落 [research/0027-theme-fork-facts.md](../research/0027-theme-fork-facts.md)，只读盘点，未改动任何文件与 git 状态）：

1. **子模块**：gitlink 6c5a8f6 干净（`git submodule status` 无 `+`/`-` 前缀）；116 文件 dirty **实锤为纯 CRLF**（`--ignore-cr-at-eol` 归零、numstat 6025/6025 对称、`file` 报 CRLF vs `git show` 为 LF）；LICENSE MIT 双版权行在位；theme.toml 无 version 字段（版本语义=git tag：v8.0-55）；`.git` 为 gitlink 文件。
2. **可达性两栏**：**9/25 partial 可达**（head/header/footer + baseof 链，extend_head/extend_footer/post_meta/author/anchored_headings/opengraph 链）；**16/25 不可达**（comments/share_icons/toc/breadcrumbs/post_nav_links/translation_list/home_info/index_profile…各有守卫不满足或父 partial 不可达）；**archives 模板不可达**（无 content 页设 `layout: archives`、菜单无入口、public/ 无产物）；**6 个主题短代码零引用**；robots.txt 被 static/ 遮蔽；head.html:201 悬空引用 google_analytics.html（0.167 实证不报错，CI 钉的 0.164 行为未验证）。
3. **覆盖表**：站点 4 个「近逐字覆盖」——baseof（仅差 `<html class="no-js">`×3）、post_meta（仅差时区格式）、extend_head/extend_footer（主题版是注释占位）、opengraph（仅差 ogImage 兜底）；2 个语义重写——index.json（截断摘要+tags/categories）、rss.xml（限 Type=posts）；3 个 net-new——index.html、product-* 三 seam、shortcodes/product-index。**ADR-0002 漏列 post_meta 与 opengraph 两个同步义务文件（实际 4 个）**。
4. **主题行为零断言 9 处**：no-js swap 全站面（仅 products/home 断言）、post_meta 时区回退不红（golden 容错 `+0800 CST`/`+0800` 两形态）、菜单 13 项与 URL 形态、RSS home-only-posts 语义、404 页、list/taxonomy 渲染、search.html 渲染、归档页、dev-vs-prod 双守卫差异（og/schema/robots/图片 srcset）。
5. **死配置 8+**：avatar、socialIcons（唯一读取点不可达）、customSyntaxHighlighting、stickyNav、reorderNavItems（复核确认真不读）、collapseNavItems、rss、siteStartYear、showTableOfContents/showPrevNextPost（键名错配≠ShowToc/ShowPostNavLinks）等主题零读取。
6. **构建触点清单**：deploy.yml:28 `submodules: true`；AGENTS.md 5 处（含坑点 6 checkout 卡死整条随子模块消失）；README 5 处子模块指引；.gitmodules 删除；auto_push.py 代码零耦合（`git add --dry-run` 实证不碰子模块内部 dirty，无需改）。

**下游影响**：0029 的修剪范围有可达性两栏做边界；0030 的分层契约有覆盖表（含 ADR-0002 漏列事实）；0031 有构建触点清单；0032 有 9 处零断言清单做锚点候选。

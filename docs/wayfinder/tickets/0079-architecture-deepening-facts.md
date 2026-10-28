---
id: "0079"
title: 架构深化四区现状事实底座（盘点）
type: research
mode: AFK
status: open
blocked_by: []
assignee:
map: map-architecture-deepening.md
created: 2026-10-27
---

## Question

本图四区（卡片 / 注册缝 / 死面 / 影子契约）的事实底座——后续每张决策票的共同前提。只查事实、不做决策、不给推荐。要盘清五项：

1. **文章卡片的全部渲染面与逐字段差异**：`layouts/index.html:126-143`（`mf-post`）与 `themes/maplemod/layouts/_default/list.html:57-85`（`post-entry` / `first-entry` / `tag-entry`）逐行比对——cover、草稿 SVG、`hideMeta`、摘要 `Truncated` 处理、`post_meta` 入参、`featured-badge`、`entry-link`、aria-label 的异同；并确认是否还有第三/第四种卡片形态（`terms.html`、`search.html`、`404.html`、`_content.gotmpl` 派生文是否有独立 markup）。附各自的调用链与分页器关系（`first-entry` 由谁判定）。
2. **引擎注册面**：`assets/js/mf-reveal/` 四文件的 import 图（`reduced-motion.js` 被谁 import）、三个引擎尾部 `autoInit()` 的具体副作用（挂载点、监听器、是否幂等）、`app.js` 现状、`mf-search-overlay.js` 的装配形态（`@params` 注入、两引擎如何被调起）、以及 `extend_footer.html` 的 js.Build 入口事实。
3. **测试加载面**：`tests/assert_reveal.mjs` / `assert_search.mjs` / `assert_harness.mjs` 各自如何加载被测代码（`dom.loadFresh()` 的语义、是否直接加载引擎文件、是否依赖 import 副作用、断言条目数与文件对应关系）；若引擎不再自注册，哪些断言会因「未调用注册」而静默空跑（**假绿风险清单**）。
4. **死面清单（范围 = 配置 + CSS）**：① `hugo.toml` 每个参数与配置块是否有读取点（`grep` 读取点，标注「有读取点 / 零读取点 / 有读取点但值恒等于 Hugo 默认」；含注释掉的 PaperMod 遗留键）；② `themes/maplemod/assets/css/` 与 `assets/css/extended/` 每个文件的可达性（被 `head.html` 装配？`resources.Match` 通配？）与选择器消费面；③ 零引用类名逐条归类：**真死** / **构建期生成**（chroma、highlight line-number 表）/ **运行时拼接**（JS 里 `'is-' + x` 之类）/ **markup 由 Hugo 生成**（如 `.highlight` 结构）；④ CSS 变量链（`--theme` / `--entry` / `--border` 等）的定义处与消费处，标出「只被死块引用」的变量。
5. **JS→CSS token 矩阵**：JS 写入的全部 class / 自定义属性 / `aria-*` / `data-*` / `inert` / `hidden`，与 CSS 消费点做一一对应表，标出三类：**有写无读**（JS 写了 CSS 不消费）、**有读无写**（CSS 消费但无 JS 或 markup 生产者）、**两侧同名**（含语义是否一致）。同时记录每个 token 的契约定义处（哪个引擎 docstring 的哪一段）。

产物：`docs/wayfinder/research/0079-architecture-deepening-facts.md`，第 1–5 项逐条带 `文件:行号` 证据；结尾给「缺口清单」（本图需要决策、而现有断言/文档未覆盖的问题面）。只查事实，不做决策，不给推荐。

环境注意：本 shell 的 grep 对 `\|` 交替失效，内容搜索用 Grep 工具；除研究产物文件外不得修改任何仓库文件；不得执行 git 写操作；**不得运行 hugo 构建**（以读源码与既有 `public/` 产物为准，避免污染 `public/`）。

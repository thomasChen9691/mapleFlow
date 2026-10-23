---
id: "0049"
title: 搜索入口现状事实底座（盘点）
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-search-entry.md
created: 2026-10-23
claimed: 2026-10-23
closed: 2026-10-23
---

## Question

搜索入口相关面的现状盘点——本图后续所有决策的事实前提，只查事实、不做决策。要盘清八项：

1. **search 页面**：`content/search.md` 的 front matter（draft / layout / outputs）；主题 `themes/maplemod/layouts/_default/search.html` 的三挂点（searchbox / searchInput / searchResults）与 aria 属性；`assets/css/common/search.css` 的存在与覆盖范围。
2. **fastsearch 加载面**：`themes/maplemod/layouts/partials/head.html` 的加载条件（`.Layout == search`？）、`js.Build` 管线（concat fuse / license / fastsearch、params 传递）、preload 路径；fastsearch 现仅在哪类页面加载；全站唯一 JS 恒加载面是什么（`extend_footer` 的 reveal 引擎——确认其加载条件与落点，这是「全站入口脚本」的现有基础）。
3. **入口现状**：`hugo.toml` 的 `[[menu.main]]` search 项（weight / url）与导航 9 项渲染面；`themes/maplemod/assets/js/fastsearch.js` 的键盘绑定（Alt+/ 还是其他、keydown 挂在哪个元素、作用范围是否仅 search 页）、`window.onload` 的 focus 行为。
4. **首页结构**：`layouts/index.html` 的区块编排（hero / 精选文章 / 最近更新 / 产品分栏 / 数据条）、有无搜索相关区块或预留位；`homeInfoParams` 内容。
5. **契约现状**：`fastsearch.js` 文件头 docstring 快照收录了哪些入口相关条款（挂点 / .focus / 键盘语义 / XHR 路径 / **加载条件是否在契约里**）；ADR-0010 中与「入口 / 加载条件 / 呈现层」相关的原文摘录（含 2026-10-23 指针）。
6. **投影与呈现的字段面**：`layouts/_default/index.json` 六字段现状；fastsearch 的 keys 是哪四个字段（决定「显示标签 / 摘要」是否需要改投影——三处同步纪律）；结果 `li` 现渲染哪些字段（标题 + 链接？）。
7. **现有断言覆盖**：`tests/assert_site_contracts.py` 中 B11（search 页三挂点）锚哪种构建；0047 落地的交付面断言（search.*.js 引用 / 构件落盘 / fetch 同目录 index.json）锚哪种构建；搜索相关断言全清单（函数名 + 锚定构建 + 断言内容一句话）。
8. **外部惯例（轻量）**：主流文档站 / 博客的搜索入口惯例（Cmd+K / Ctrl+K / `/` 唤起、首页常驻框）各有什么代价；浏览器默认快捷键冲突（Cmd+K 在 Safari / Chrome 的行为、`/` 在部分输入场景的行为）。标注为外部常识，非本项目事实。

产物：`docs/wayfinder/research/0049-search-entry-facts.md`，前 7 项逐条带 `文件:行号` 证据；第 8 项标注来源；结尾给「缺口清单」（现有断言未覆盖、且本图需要决策的问题面）。只查事实，不做决策，不给推荐。

环境注意：本 shell 的 grep 对 `\|` 交替失效，内容搜索用 Grep 工具；不要修改本文件以外的任何仓库文件；不要执行 git 写操作。

## Resolution

2026-10-23 · research（AFK）：研究子代理完成八项盘点，主代理抽查核实四项关键证据（header.html:90-91 accesskey 与 title 后缀、head.html:78 加载条件、fastsearch.js:53-54 无守卫模块级挂载、:142 document.onkeydown），与文档一致。事实全文落 `docs/wayfinder/research/0049-search-entry-facts.md`（八项分节 + 缺口清单 9 条），本工单不重述。

对后续工单最关键的五个事实：① fastsearch 现仅 search 页加载，且**现状文件不可原样搬到全站加载面**（无 #searchInput 的页面会抛 TypeError）；② 「Alt + /」不在 fastsearch.js 里，是 header.html 的 accesskey 属性，浏览器实现、零测试；③ search 页 focus 靠原生 autofocus，window.onload 只做 XHR；④ 首页无任何搜索区块或预留位；⑤ 结果 li 只渲染标题+链接，keys 四字段与投影六字段差集恰为 {tags, categories}——摘要/标签均在投影内，加深渲染不触发三处同步。缺口 9 条中与 0050-0052 直接相关的：入口无契约定义处、加载条件无守门、「第二个消费方」触发条件无观测面、行为测试为零。

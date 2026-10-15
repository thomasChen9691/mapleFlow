---
id: 0009
title: 无配对副本的范围裁定
type: grilling
mode: HITL
status: open
blocked_by: []
assignee: agent
claimed: 2026-10-15
map: map-sop-source-sync
---

## Question

三个「无配对」文件是否进入本图的管线范围？

- `docs/sop/MAPLEFLOW_BLOG_SOP.md`（157 行，博客自身的维护 SOP，无对应文章）；
- `content/posts/sop-ops-tools-index.md`（30 行，运维工具索引文章，无对应笔记）；
- `docs/sop/README.md`（21 行，docs/sop 的索引笔记）。

候选（逐个文件裁）：纳入派生管线 / 保持手写 / 明确排除出本图。

决策依据：

- 目的地边界：「候选 2 的 SOP 模块」到底指 6 对工具 SOP，还是 docs/sop 全目录——这决定管线的输入面。
- 索引的双源问题：README 列 6 篇、index 文章链 6 篇，改一处忘另一处就是**新的零同步点**；若索引不进管线，漂移守门要不要覆盖它。
- MAPLEFLOW_BLOG_SOP 是元内容（讲怎么维护博客），其更新频率与读者面都异于工具 SOP——「同管线产出」可能反而是错配。

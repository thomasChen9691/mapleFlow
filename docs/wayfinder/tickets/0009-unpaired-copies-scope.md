---
id: 0009
title: 无配对副本的范围裁定
type: grilling
mode: HITL
status: closed
blocked_by: []
assignee: agent
map: map-sop-source-sync
claimed: 2026-10-15
closed: 2026-10-15
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

## Resolution

2026-10-15 · grilling（用户为决策者），门闩 + 三文件全落：

1. **门闩 · 目录契约**：注册表驱动，孤儿笔记 tolerated——docs/sop 里无注册条目的笔记 = 「尚未发布的稿件」，允许自然存在（`CONTEXT.md` 源笔记定义原生为真，术语零改写）；「注册但未发布」= 条目 `draft: true`。此契约即 0008 机制的枚举语义（并录于 0008 决议第 5 条）。
2. **MAPLEFLOW_BLOG_SOP.md**：留在 docs/sop，README 标注「不发布的人类向维护文档」，注册表不收。它与 AGENTS.md 的陈旧重复（约 95% 同域；构建命令缺 `--gc --cleanDestinationDir`；引用已被证伪的 `reorderNavItems`；about.md TODO 占位早已替换）原样移交架构评审 F10「小手抄集群」候选——本图目的地是发布管线，不做文档治理，删除/合并留待 F10 一次性裁。
3. **sop-ops-tools-index.md**：保留手写。索引是站点编辑层资产（学习顺序、使用说明、表格），不是 SOP 稿件，与 aiops/docker/k8s 手写文章同级；它是 content/posts 里唯一非派生的 sop-* 文章，合法。连带两个裁定：① 产物断言「无残留」精确化为「6 个派生 slug 不得存在手写 .md」，不误伤 index；② index 内 6 个 ref 短码对生成页的解析由产物断言守——这是实施期第一个验证点（工单 0007 遗留的不确定项）。
4. **docs/sop/README.md**：保留手写 + 双向漂移断言——README 表格列出的笔记集合 == 注册表条目集合；加一篇 SOP 忘更 README 则 CI 红。docs/sop 的人类入口（使用说明 + 学习顺序）有独立价值，最后一个手抄索引从此变成受守资产。

**下游影响**：0013 的产物断言集增加/精确化两条（README ↔ 注册表双向一致；残留断言的 6-slug 精确表述）。无新工单——三个文件处置全部有主，雾区无增生。

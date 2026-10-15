---
id: 0010
title: SOP 文的派生机制
type: grilling
mode: HITL
status: open
blocked_by: [0008]
assignee:
map: map-sop-source-sync
---

## Question

承接「真源归属」的裁决：SOP 文（或反向的源笔记）以什么机制派生？

候选（若 0008 裁 docs/sop 赢）：

- (a) **content adapters**——`_content.gotmpl` 读 docs/sop + `AddPage`：磁盘单份、front matter 全可控、真页面；代价 = 内存态（backend 断供、grep/AI 导航看不到文章）、`dates` 嵌套写法陷阱、`--printPathWarnings` 守门；
- (b) **module mounts**——虚拟视图：docs/sop 需补 front matter（8 个文件现在全无），slug 按文件名小写化、与现有 `/posts/sop-*.html` 冲突，需逐篇加 `slug`；
- (c) **构建外脚本**——CI/Makefile 从 docs/sop 生成 content/posts/*.md：磁盘两份但自动同步，backend/grep/AI 导航全部不受影响；代价 = 生成物入库后的 review 面与「漏跑即腐化」风险（ADR-0004 已拒过同款风险，需评估本次是否同构——脚本写 content/ 是 git 可见的，与派生数据静默渲染不同）。

若 0008 裁 content/posts 赢：本题反向——docs/sop 是退役、归档还是反向生成。

本工单同时确认两个硬约束：

1. 既有 6 篇线上 URL `/posts/sop-*.html` 是否**冻结**（改 URL = 外链 404 + gh-pages 残留，除非 `--cleanDestinationDir` 清掉）；
2. 导语 / description / tags 等已分叉差异的**承载位置**（细则归工单「已分叉差异的消长裁定」，本题只定承载位置的候选空间）。

决策依据：工单 0007 的机制事实与代价结构；ADR-0001（构建命令只做加法）；ADR-0004 的「接口即测试面」原则。

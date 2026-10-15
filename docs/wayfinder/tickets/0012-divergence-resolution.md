---
id: 0012
title: 已分叉差异的消长裁定
type: grilling
mode: HITL
status: open
blocked_by: [0008, 0010]
assignee:
map: map-sop-source-sync
---

## Question

6 对副本已分叉（文章多一段 web 导语、标题在 front matter、多 description/tags/date；笔记侧有 H1 标题行）。收敛时哪些差异是合法的、承载在哪？

逐个裁：

- **导语段**（文章有、笔记无）：进源笔记 / 由派生机制统一注入 / 丢弃；
- **front matter**（title/date/categories/tags/description）：逐篇写在源文件 / 集中一份数据文件（如 `data/sop-meta.yaml`）/ 派生模板统一注入；
- **H1 标题行**：保留在正文 / 删除（标题已由 front matter 承载，PaperMod 文章页不渲染正文 H1 会与页面标题重复）。

决策依据：工单 0007 的 adapter page map 字段能力（categories/tags 只能进 params，是「集中数据文件」选项的技术前提）；「真源归属」与「派生机制」的方向与形态结论——差异策略是它们的直接下游。

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

## 预裁记录（工单 0008/0009 质询，2026-10-15）

承载位置已裁（0008 决议第 3 条）：front matter 住 `data/sop.yaml` 注册表；标题从笔记 H1 提取（seam 剥离）；导语为注册表字段。剩余进入 frontier 后确认的只是数据填充与机制细节：逐篇导语/description/tags 的具体值（从现有 6 篇 posts 回填，非决策）；categories 缺省 `['运维']`、tags 可缺省；H1 剥离与导语前置的正文变换顺序。

**实施期订正（2026-10-15，golden 比对发现）**：正文变换实为**三条规则**——剥 H1、**剥紧随首个章节标题后的定位段（单行）**、前置导语。第三规则是历史事实（6 篇线上文章都把笔记首段并入了导语），非新决策；预裁记录的「两条规则」表述因此不准，以此订正为准。该规则为启发式：定位段仅单行才剥（多行段不剥，页面可见重复、不静默丢失内容），依赖笔记结构约定（H1 → 章节标题 → 单行定位段）。

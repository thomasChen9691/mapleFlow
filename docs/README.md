# 文档目录

> 本目录是 MapleFlow 的文档、决策与追踪归档。**阅读路由**：术语 → 决策 → 最近状态 → 在办事项。
> 站点的构建命令、必知坑点、契约纪律不在本目录，在仓库根的 **`AGENTS.md`**。

## 目录一览

| 路径 | 是什么 | 什么时候看 |
|---|---|---|
| [`../CONTEXT.md`](../CONTEXT.md) | 唯一标准术语表（代码 / 文档 / UI 文案统一用词） | 写代码、写文案前对齐词 |
| [`adr/`](adr/) | **10 篇架构决策记录**（0001-0010） | 问「为什么这样设计」 |
| [`handoffs/`](handoffs/) | **10 份交接**：每次会话 / 每张图的终态（状态、决策、下一步、环境坑点） | 接手工作前先读最新一份 |
| [`wayfinder/`](wayfinder/) | **追踪器**：9 张地图 + 53 张工单 + 9 份研究 | 开新工作前看 frontier |
| [`sop/`](sop/) | SOP 源笔记（7 篇，其中 6 篇已由注册表发布）+ 笔记结构约定 | 改 SOP 正文 |
| [`CHANGELOG.md`](CHANGELOG.md) | **已冻结**（最后条目 2026-10-16） | 查 2026-10 之前的历史 |
| [`backlog.md`](backlog.md) | 剩余待办清单（17 项，含证据与验收） | 决定下一步做什么 |

## 阅读路由（给 AI 与新人）

1. **术语** → `CONTEXT.md`（唯一术语表，代码与文案统一用它）
2. **决策** → `docs/adr/`（0001-0010；ADR 是历史记录，正文不改，后续变化以指针行追加）
3. **最近发生了什么** → `docs/handoffs/` 最新一份
4. **接下来做什么** → `docs/backlog.md`
5. **怎么改、怎么验** → `AGENTS.md`（命令、坑点、契约纪律、测试缝）

## 约定

- **决策只活在 `docs/adr/`**：wayfinder 地图与工单是过程，收口时必须耐久化进 ADR（ADR-0004 立的规矩）。
- **变更记录不再写 CHANGELOG**：新变更记在 handoff（状态与去向）与 ADR（耐久决策）。CHANGELOG 已冻结，历史条目原样保留。
- **追踪器用本地 markdown**：地图 / 工单 / frontier 的操作方式见 [`wayfinder/README.md`](wayfinder/README.md)。

## 历史指针（已退役的东西，避免照着旧文档走）

- **OpenSpec 已退役（2026-10-23）**：`openspec/` 与 `OPENSPEC_GUIDE.md` 已删除。项目追踪由 `docs/wayfinder/` 承担；旧提交或旧文档里出现的 `/opsx:` 命令、「OpenSpec 变更」字样均属历史。
- **`页面改版落地说明.md` 已删除（2026-10-23）**：那是 2026-10 视觉改版的落地记录，其中「精选文章 = 最新 3 篇」「资源数 = `len site.Data.products`」等描述已被 ADR-0004 / ADR-0009 取代，设计理由现存于 `assets/css/extended/custom.css` 的注释。
- **`backend/` 已退役（ADR-0003，2026-10-16）**：FastAPI 内容 API 全套删除，代码留 git 历史。产品数据源替换届时只动 `layouts/partials/product-items.html`（ADR-0006）。

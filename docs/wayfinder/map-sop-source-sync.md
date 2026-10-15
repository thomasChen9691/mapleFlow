---
id: map-sop-source-sync
title: SOP 真源与发布管线图（候选 2）
labels: [wayfinder:map]
status: open
created: 2026-10-15
---

# SOP 真源与发布管线图（候选 2）

## Destination

把 6 对「源笔记 / SOP 文」手抄副本（docs/sop 6 个工具 SOP 共 1243 行 vs content/posts 6 篇 sop-*.md 共 1327 行，逐对 difflib 实测 98.5% 相同、零同步机制）收敛为单一真源的发布管线，达到「可测试、AI 可导航」的可施工状态。本图只产决策，不落地代码；施工留待地图关闭后按 verify-then-commit 展开。

## Notes

- 术语以根目录 `CONTEXT.md` 为准：SOP 文、源笔记、草稿。新术语当场进 `CONTEXT.md`，不攒批（AGENTS.md §9.4）。
- ADR-0001~0004 闭卷不得重开。最相关先例：ADR-0003「Hugo 是真源，消费方对齐 Hugo」——本图的核心张力是 `CONTEXT.md` 已声称「源笔记是 SOP 文的上游」，但该上游关系没有任何机制承载（grep 全库：docs/sop 被代码/配置引用 0 处）。
- 已核实事实（2026-10-15 本会话一手复测，非引用旧报告）：6 对副本 901 非空行中 888 行一致（98.5%）；分叉仅在于文章多一段 web 导语、标题进 front matter、多 description/tags/date。另有三个无配对文件：`docs/sop/MAPLEFLOW_BLOG_SOP.md`（157 行，博客自身维护 SOP）、`content/posts/sop-ops-tools-index.md`（30 行，索引文章）、`docs/sop/README.md`（21 行，索引笔记）。
- 原架构评审的候选 2~6、8 明细只存在于已清理的临时 HTML（`architecture-review-20261015-1736.html`），本图事实为一手复测；其余候选的勘察未恢复，将来选做时重跑 improve-codebase-architecture 或接受重新勘察。
- Hugo CI 钉 0.164.0、本机 0.167.0；一切 URL/模板行为按 0.164 编写（0.148.0 uglyURLs 修复后语义，见工单 0007）。
- **URL 冻结已确认为硬约束**（工单 0008 决议）：既有 6 个线上 URL `/posts/sop-*.html` 不得变更（改 URL = 外链 404 + gh-pages 残留；slug 由 `data/sop.yaml` 显式控制）。
- backend（FastAPI）是文章的第二个磁盘消费者：`blog_parser.py` glob `content/posts/*.md`（ADR-0003 只读镜像）。**已坐实（工单 0008 附带事实）：backend 零消费者，两份历史审计报告均结论「全量死代码、建议删除」**——内存态机制打断 `/api/posts` 的实际代价接近零，正式处置归工单 0011。
- 用户是项目负责人：术语敲定与 ADR 是否记录由用户拍板。质询一次一问，先给推荐答案；**事实自己查**（文件 / 子代理），只有**决策**问用户。
- 节奏：一次会话最多解决一张工单（research 除外）；HITL 工单必须与用户实时对话解决，agent 不得自答。

## Decisions so far

- [Hugo 构建期内容生成机制事实清单](tickets/0007-hugo-build-time-content-generation.md) — 0.164 源码+实证：只有 content adapters 同时满足「磁盘单份 .md + front matter 全可控 + 真页面」；mounts 是虚拟视图且不能注入 front matter（docs/sop 8 个文件全无 front matter，挂载后 title 空/date 零值，slug 按文件名小写化与现 URL 冲突）；git symlink 因 v0.163.1 安全修复出局；adapter 页仅内存存在且 Hugo 无落盘选项 ⇒ backend 的 `glob("*.md")` 会空、`/api/posts` 断供，seam 决策必须同时裁决 backend 取数路由；adapter page map 顶层 `date` 静默失效，必须 `"dates" (dict "date" ...)`。
- [SOP 文与源笔记的真源归属](tickets/0008-sop-source-of-truth.md) — docs/sop 为唯一真源（意图立为机制）；派生机制 = content adapters（排除预构建脚本：ADR-0004 枪毙过的「漏跑即陈旧」失效模式）；**6 个线上 URL `/posts/sop-*.html` 冻结为硬约束**；元数据住 `data/sop.yaml` 注册表，标题由 seam 从笔记 H1 提取并剥除；测试 = 构建期 errorf 契约 + 产物断言（含「渲染正文 == 剥 H1 笔记正文 + 导语」归一化比对——零同步痛点的守门转化）+ fixture 双构建；目录契约 = 注册表驱动、无条目笔记即「尚未发布的稿件」（CONTEXT.md 定义原生为真）。
- [无配对副本的范围裁定](tickets/0009-unpaired-copies-scope.md) — MAPLEFLOW_BLOG_SOP.md 留下 + README 标注「不发布」（陈旧重复移交 F10 候选）；sop-ops-tools-index.md 保留手写（编辑层资产非 SOP 稿件；残留断言精确化为 6 个派生 slug）；docs/sop/README.md 保留 + README↔注册表双向漂移断言。

## Not yet specified

- **/api/posts 改道后的新鲜度语义**：若 backend 改读构建产物（工单 0011 的路由候选之一），API 的缓存与失效语义——等 0011 裁路由。

## Out of scope

- **候选 3~6、8**：后端解析器诚实化、product-index 接口收窄、reveal 协议、主题 fork、搜索契约——各自独立成图。
- **候选 7「精选机制落地」**：方向已由项目负责人决议（给文章加 featured 字段），另行开工，不并进本图。
- **上一图遗留**：commit message 重写、push 35 个 commit、products.yaml 真上架——与本地图无关。
- **backend 产品 API**：ADR-0003 边界内后端只镜像文章，产品域不进入后端。

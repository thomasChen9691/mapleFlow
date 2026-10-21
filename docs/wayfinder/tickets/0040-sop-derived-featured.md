---
id: "0040"
title: SOP 派生文是否参与精选
type: grilling
mode: HITL
status: open
blocked_by: ["0036"]
assignee: ""
map: map-featured-mechanism.md
created: 2026-10-21
---

## Question

SOP 派生文（6 篇，由 `data/sop.yaml` 注册表 + `docs/sop/` 源笔记构建期生成）**能否被标为精选**，以及若能，声明载体与契约怎么走。事实底座：派生文 front matter 的唯一生成点是 `_content.gotmpl:61-69` 的 `AddPage` dict，params 仅 `categories/tags`（research/0035 §5）。

待决：

1. **是否参与**：派生文一律不参与精选（首页精选只收手写文章——理由是 SOP 文是速查体、精选位应留给叙事性文章），还是参与？
2. **若参与，声明载体**：`data/sop.yaml` 加 `featured` 字段（可缺省 false）→ `_content.gotmpl` 在 `params` 里透传。随之而来的：注册表契约是否从四类扩到五类（featured 非布尔即 errorf），还是保持「可选字段不校验」（与 `tags` 可缺省的宽松先例一致）。
3. **若参与，现有 6 篇谁标**：SOP 文是站点主体内容（6/11），若精选只标 1-2 篇手写文章，首页精选区会显得单薄——这是内容策略问题，需项目负责人定。
4. **对 SOP 管线测试的影响面**：`tests/assert_sop_pipeline.py`（100 项）是否需新增字段透传断言；契约从四类扩五类会不会与「契约四类」的既有表述冲突（AGENTS 坑点 8、ADR-0005、`_content.gotmpl` docstring 三处同步）。

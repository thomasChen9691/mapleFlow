---
id: "0040"
title: SOP 派生文是否参与精选
type: grilling
mode: HITL
status: closed
blocked_by: ["0036"]
assignee: agent
map: map-featured-mechanism.md
created: 2026-10-21
claimed: 2026-10-21
closed: 2026-10-21
---

## Question

SOP 派生文（6 篇，由 `data/sop.yaml` 注册表 + `docs/sop/` 源笔记构建期生成）**能否被标为精选**，以及若能，声明载体与契约怎么走。事实底座：派生文 front matter 的唯一生成点是 `_content.gotmpl:61-69` 的 `AddPage` dict，params 仅 `categories/tags`（research/0035 §5）。

待决：

1. **是否参与**：派生文一律不参与精选（首页精选只收手写文章——理由是 SOP 文是速查体、精选位应留给叙事性文章），还是参与？
2. **若参与，声明载体**：`data/sop.yaml` 加 `featured` 字段（可缺省 false）→ `_content.gotmpl` 在 `params` 里透传。随之而来的：注册表契约是否从四类扩到五类（featured 非布尔即 errorf），还是保持「可选字段不校验」（与 `tags` 可缺省的宽松先例一致）。
3. **若参与，现有 6 篇谁标**：SOP 文是站点主体内容（6/11），若精选只标 1-2 篇手写文章，首页精选区会显得单薄——这是内容策略问题，需项目负责人定。
4. **对 SOP 管线测试的影响面**：`tests/assert_sop_pipeline.py`（100 项）是否需新增字段透传断言；契约从四类扩五类会不会与「契约四类」的既有表述冲突（AGENTS 坑点 8、ADR-0005、`_content.gotmpl` docstring 三处同步）。

## Resolution

2026-10-21 · grilling（HITL，用户为决策者）：

1. **派生文参与精选**。理由：不参与则精选池只剩 4 篇手写（3 篇速查 + 1 篇索引），标 3 篇 ≈ 「手写文章全集」，精选退化为分类而非挑选；且今天占着 2/3 精选位的派生文会突然消失，变更面反而更大。参与后池 10 篇，挑选成立，且行为连续。
2. **载体 = 注册表可选字段 + 条件传键**：`data/sop.yaml` 加可选 `featured`；`_content.gotmpl` 在 `AddPage` 的 `params` 里**仅当字段存在时写入**。实测依据（Hugo 0.167 探针）：`dict "featured" .featured` 在缺字段时产出 `isset=true` + 类型 `nil`，若盲传，0036 定的「非 bool 即 errorf」会对每条未标条目误报——**必须条件传键**。
3. **契约四类 → 五类**：新增「featured 存在但非 bool → errorf」。同步三处：`_content.gotmpl` 头注（契约清单）、`AGENTS.md` 坑点 8、`ADR-0005`（按「ADR 是历史记录」惯例加指针行而非改正文）。
4. **首次标注 3 篇（均手写）**：`sop-ops-tools-index`（站点入口/索引）、`k8s-common-commands`（最常用）、`aiops-state-and-tools`（唯一叙事性文章）。派生文初始不标。
5. **补覆盖（防止「能力预留但零使用零测试」）**：注册表路径在 `tests/assert_sop_pipeline.py` 加一条 fixture 透传断言——fixture 条目带 `featured: true` → 派生页 `params.featured` 为 bool `true`；不靠改真实内容去凑测试。
6. **golden 不受影响**（已核 `assert_sop_pipeline.py:310-320`）：golden 只比对 `<article>` HTML、title、description、date，`params.featured` 不进这些产物。
7. **下游**：0039 的 fixture 不需要造派生文；0041 收口时 ADR-0009 须记「SOP 契约四类 → 五类」。

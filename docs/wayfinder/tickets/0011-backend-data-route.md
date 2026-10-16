---
id: 0011
title: backend 取数路由
type: grilling
mode: HITL
status: closed
blocked_by: [0010]
assignee: agent
claimed: 2026-10-16
closed: 2026-10-16
map: map-sop-source-sync
---

## Question

若「SOP 文的派生机制」选出内存态机制（content adapters 或 mounts，磁盘上 content/posts 无 .md），`backend/blog_parser.py` 的输入改道哪里？

候选：

- (a) **改读构建产物**——backend 解析 `public/` 的渲染 HTML（反解析脆，且 ADR-0003 的「解析语义独立」优势丧失）；
- (b) **Hugo custom output format 产出 JSON**——index.json 同款机制产一份内容 API 页，backend 退役或改为纯转发；
- (c) **接受 /api/posts 对 SOP 文缺供**——接口收缩为「只覆盖手写文章」，消费方知情；
- (d) **backend 改读 docs/sop 自行推导元数据**——重演 front matter 缺失问题（工单 0007 已证伪此路的可行性）。

决策依据：ADR-0003「后端是 Hugo 的只读镜像，分歧时后端对齐 Hugo」——本工单是该 ADR 在「内容不再落盘」新事实下的适用，不是重卷；若裁 (b)，等于镜像的输入从磁盘换成构建产物，需同时裁断 `/api/posts` 的契约是否对外（有无真实消费方）。

前置事实（工单 0007 已坐实）：adapter 化后 `glob("*.md")` 返回空、`/api/posts` 空列表；Hugo 无「生成页落盘」选项。

## 预裁记录（工单 0008 质询，2026-10-15）

本题前提已坐实：机制 = content adapters（0008 决议第 2 条）⇒ backend 的 `glob("*.md")` 确定返回空。另坐实：backend 零消费者，两份历史审计（`功能盘点与冗余分析报告` R1 / `代码与文档审核报告-2026-10-10` P2-2）均结论「全量死代码、建议删除」——选项 (c)「接受缺供」的实际代价接近零。四个路由候选本身仍未裁，进入 frontier 后正式质询。

## Resolution

2026-10-16 · grilling（用户为决策者）。**路由问题溶解为存亡问题，裁决：退役。**

**前提订正（质询中查出）**：本题原文「glob 返回空」不准确——只有 6 篇 SOP 被派生，4 篇手写文章（aiops/docker/k8s/ops-tools-index）仍在磁盘上。backend 现状不是空列表，而是**静默从 10 篇缩到 4 篇**：`/api/posts` 看起来健康地返回 4 篇，60% 内容无声缺席。这比空列表更坏——空列表会立刻被发现，静默缺供不会。选项 (c)「接受缺供」的代价因此不是「接近零」，而是引入一个本项目一直在消灭的失效类别（对照：5-vs-0 指标事故、draft 分歧、SOP 零同步）。

**裁决与执行**：退役，不改道。删除范围（commit `e2de031`）：`backend/`、`run_backend.py`、`test_api.py`、`verify_encoding.py`、`docs/BACKEND_DOCS.md`、`pyproject.toml`（该文件整个就是 backend 的包配置）。AGENTS.md / CLAUDE.md 的后端章节同步删除并重编号（无活文档引用旧章节号）。代码留 git 历史。

**理由**：① 零消费者——三条改道候选都是「为无人维护新机制」；② 两份独立审计早已结论删除，未执行只是因为决策从未被强制，适配器迁移强制了它；③ 「未来小程序/APP 数据源」的保留理由不成立——真有消费方那天，正确做法是为该消费方现建 Hugo custom output，而不是Speculative 维护一个镜像；④ 原样不动 = 静默缺供，见前提订正。

**ADR-0003 状态（明示，非重开）**：0003 裁的是「后端若存在，则是 Hugo 只读镜像、分歧时后端对齐 Hugo」。退役取消其适用对象，不改其语义——已在 ADR-0003 文件头加状态标注（语义裁决对今后的任何磁盘镜像仍然有效）。用户质询中未异议；若认为构成重开，走重审流程。

**四个路由候选的归宿**：(a) 读 public/、(b) custom output JSON、(c) 接受缺供、(d) 改读 docs/sop——全部随存亡裁决而消解（moot），不另行评估。(d) 早已被工单 0007 证伪（笔记无 front matter）。

**遗留地雷（移交 F10，本图不越界）**：`docs/sop/MAPLEFLOW_BLOG_SOP.md` 的「常用命令」仍教人启动已删除的后端——该文件按 0009 决议标注「不发布」且陈旧重复问题整体移交 F10，本次不碰。

**下游影响**：0012 不受影响（差异消长纯表示层）；地图雾区「/api/posts 改道后的新鲜度语义」随之消解（无 API 可改道）；架构评审「候选 3 后端解析器诚实化」随后端消失而消解——无后端则无解析器。

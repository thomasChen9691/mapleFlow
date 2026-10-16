---
id: 0011
title: backend 取数路由
type: grilling
mode: HITL
status: open
blocked_by: [0010]
assignee: agent
claimed: 2026-10-16
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

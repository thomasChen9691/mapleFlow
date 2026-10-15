---
id: 0011
title: backend 取数路由
type: grilling
mode: HITL
status: open
blocked_by: [0010]
assignee:
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

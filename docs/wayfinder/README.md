# Wayfinder 追踪器（本地 markdown 约定）

本目录是 mapleFlow 的 wayfinding 追踪器。无外部 issue tracker 时的本地约定，操作方式如下。

## 地图（map）

- 位置：`docs/wayfinder/map-*.md`，frontmatter 打 `labels: [wayfinder:map]`。
- 地图是**索引不是仓库**：只列 Destination / Notes / Decisions so far / Not yet specified / Out of scope。决策详情只存在于工单；地图对每个已决工单只留一行 gist + 链接，绝不重述全文。

## 工单（ticket）

- 位置：`docs/wayfinder/tickets/NNNN-<slug>.md`，是地图的子工单。
- frontmatter 字段：`id` / `title` / `type`（research | prototype | grilling | task）/ `mode`（HITL | AFK）/ `status`（open | closed）/ `blocked_by`（工单 id 列表）/ `assignee`（认领人）/ `map`（父地图文件名）。
- 工单正文只有一个 `## Question` 段：待决策的问题，粒度控制在一次会话能解决。
- **无原生依赖关系，用 body 约定**：`blocked_by` 列出阻塞工单。frontier = status 为 open、`blocked_by` 全部已 closed、且无 assignee 的工单。

## 操作规则

- **认领**：开工前先把工单 `assignee` 改成自己；open + 无 assignee = 未认领。
- **解决**：工单内追加 `## Resolution` 段（答案 + 理由 + 资产链接），`status: closed`；地图 Decisions so far 追加一行 gist + 链接。
- **节奏**：一次会话最多解决一张工单（research 工单除外）。HITL 工单必须与用户实时对话解决，agent 不得自答。
- **研究产物**：存 `docs/wayfinder/research/NNNN-*.md`，工单 Resolution 里放指针。
- ** fog 迁移**：工单答案使某条 Not yet specified 可精确表述时，落成新工单并从地图雾区删掉该条——它只以工单形态存在。
- **越界定性**：若答案揭示某工单已越过目的地，关闭它并在地图 Out of scope 留一行（gist + 原因 + 链接），不进 Decisions so far。

---
id: 0008
title: SOP 文与源笔记的真源归属
type: grilling
mode: HITL
status: closed
blocked_by: []
assignee: agent
map: map-sop-source-sync
claimed: 2026-10-15
closed: 2026-10-15
---

## Question

6 对副本（docs/sop/<TOOL>_SOP.md 与 content/posts/sop-<tool>-*.md，98.5% 相同、零同步）中，哪一侧是唯一真源？

候选：

- (a) **docs/sop 为真源**——`CONTEXT.md` 现术语已如此声称（「源笔记是 SOP 文的上游」），SOP 文由构建期机制派生，声称变为机械真实；
- (b) **content/posts 为真源**——发布物即真源，docs/sop 退出发布链（归档 / 删除 / 反向生成，细节另议）；
- (c) **维持双副本**——不做机制收敛，只加漂移检测守门（测试兜底）。

决策依据：

- ADR-0003 先例：Hugo 是真源、消费方对齐 Hugo。本次是它的同构问题——「声称的上游无机制」，要么补机制要么改声称。
- 工单 0007 的机制事实：三选项的代价结构完全不同（(a) 的代价是 backend 断供 + 内存态，(b) 的代价是丢掉 docs/ 内的可 grep 真源，(c) 的代价是漂移风险不归零）。
- 目的地「AI 可导航」：磁盘上可 grep 的真源位置本身就是导航资产——哪一侧赢，直接决定未来会话的第一落点。
- 用户偏好背景：项目一贯立场是「机制承载声称，不留口头契约」（ADR-0004 拒预构建脚本的同款逻辑）。

## Resolution

2026-10-15 · grilling（用户为决策者），五裁全落：

1. **真源归属**：docs/sop 为唯一真源。`CONTEXT.md`「源笔记是 SOP 文的上游」从口头声称变为机械真实；写作流 = 先落笔 docs/sop，发布动作发生在注册表。分叉背景（质询中查出的事实）：6 对副本同日生（`c1353fa`），出生后唯一实质编辑（`37363f7`）只动 posts 侧（补 description），docs/sop 零改动——用户裁意图派而非事实派，核心理由：「单一真源」是候选 2 题设，且这次分叉的根因是「内容」与「web 表示」混在同一份文件里，docs/sop 为真源顺势把两层分开。
2. **派生机制**：content adapters（`content/posts/_content.gotmpl` 读 docs/sop + `AddPage`）。排除预构建脚本：「漏跑一步即静默渲染陈旧派生数据」正是 ADR-0004 枪毙过的失效模式；adapters 不存在「忘记跑」状态，生成发生在每次构建里，本地与 CI 同一机制。**硬约束确认：既有 6 个线上 URL `/posts/sop-*.html` 冻结**（改 URL = 外链 404 + gh-pages 残留；slug 由注册表显式控制，零成本满足）。
3. **元数据承载**：`data/sop.yaml` 注册表，每篇一条（slug/date/categories/tags/description/导语）。标题不进注册表——由 seam 从笔记首行 H1 提取并剥除，消灭标题双源，笔记 H1 成为唯一标题源。与 `products.yaml` 的数据驱动架构同构；「条目在、笔记无」由 errorf 构建期执法。
4. **存活测试集**（继承 ADR-0004 范式，两层防线）：① 构建期契约（errorf 门禁）：死条目（条目在、笔记无）/ 笔记无 H1 / 缺 date / 缺 slug → 构建失败；② 产物断言（`tests/assert_sop_pipeline.py`，CI 权威 + 本地 advisory）：6 个 `/posts/sop-*.html` 全部存在（URL 冻结回归）、渲染标题 == 笔记 H1、日期非零且 == 注册表 date（`dates` 嵌套陷阱回归）、渲染正文 == 剥 H1 后笔记正文 + 前置导语（归一化比对——「1250 行零同步」痛点的守门转化，从此内容漂移不可能静默）、ops-tools-index 的 6 个 ref 全部解析、6 个派生 slug 无手写 .md 残留。fixture 双构建照搬：4 类坏输入必须构建失败 + 真实数据守线上回归。
5. **目录契约**：注册表驱动——适配器只遍历 `data/sop.yaml` 条目；docs/sop 里无条目的笔记 = 「尚未发布的稿件」，允许自然存在（`CONTEXT.md` 源笔记定义不经改写即为机械真实）；「注册但未发布」用条目 `draft: true` 表达；在役发布篇目由产物断言守。

**模块定形**（下游施工的接口）：seam = `content/posts/_content.gotmpl` 一个模板 + `data/sop.yaml` 一份注册表 + `docs/sop/*.md` 纯净正文；模板外无生成物、无第二份 .md；ADR-0001 构建命令零改动；`deploy.yml` 仅在 build 后追加断言步（加法，与产品状态模块同款）。

**附带事实**（质询中查出，非本工单决策）：① backend 零消费者，两份历史审计（`功能盘点与冗余分析报告` R1 / `代码与文档审核报告-2026-10-10` P2-2）均结论「全量死代码、建议删除」——内存态机制「/api/posts 断供」的实际代价接近零，正式处置归工单 0011；② 6 个既有 `content/posts/sop-*.md` 必须在迁移时删除——adapter 生成页与同路径 .md 共存结果不确定（工单 0007 Q1.8），由残留断言守；③ 搜索索引（`layouts/index.json`）预计无需调整——生成页是真页面，自动进 `.Site.RegularPages` 投影，实施期验证即可。

**下游影响**：0010 的机制题本题已裁（进 frontier 后正式落档，已在其 body 留预裁记录）；0011 前提坐实（adapters ⇒ backend `glob("*.md")` 返回空）；0012 的承载题本题已裁为「注册表 + H1 提取」，余下导语/description 逐篇值是数据填充非决策；0013 测试集本题已裁（预裁记录已留）；0014 命名候选向「SOP 发布管线」收敛。地图雾区清除两条：「败者副本的去处」（= 删除 6 个 .md，见附带事实②）、「搜索索引投影」（见附带事实③）；「/api/posts 改道后的新鲜度语义」保留——等 0011 裁路由。

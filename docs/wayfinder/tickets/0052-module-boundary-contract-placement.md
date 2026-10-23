---
id: "0052"
title: 模块边界与契约落位
type: grilling
mode: HITL
status: closed
blocked_by: [0050, 0051]
assignee: agent
map: map-search-entry.md
created: 2026-10-23
claimed: 2026-10-23
closed: 2026-10-23
---

## Question

新入口 / 呈现层的模块边界与契约落位（前提：0050、0051 已决）：

1. **seam 归属与加载机制**：新入口代码落站点层还是主题层（ADR-0008 判据：视觉 / 骨架 / 交互 → 主题；内容 / 数据 → 站点）。fastsearch 在主题层（head.html 条件加载）；reveal 引擎在站点层 `assets/js/mf-reveal/`（extend_footer 恒加载）——本项目第一个跨层契约组合的两半各有先例。快捷键 / 首页框的入口脚本落哪、用什么机制加载（head.html 条件扩展 / extend_footer js.Build / 并入 mf-reveal）；两层不得存在同相对路径文件（B13 断言）。
2. **契约定义处**：新交互的 DOM 契约（class / data-* / aria / CSS 变量）落哪个 docstring——扩写 `fastsearch.js` 文件头快照 / 新文件 docstring / reveal 引擎 docstring（ADR-0007 纪律：docstring 是唯一定义处，CONTEXT.md 只放概念）；CONTEXT.md 术语条措辞归 0054，本工单只定「契约住哪」。
3. **交互归属**：入口的进场 / 聚焦 / 浮层展开动效归 reveal 协议还是搜索协议（ADR-0007 模块边界三块：产品索引筛选 / 页脚滚动进场 / 首页 hero 进场；ADR-0010 决议：搜索交互不并入 reveal）——新入口是 reveal 的第四块、搜索快照的扩展、还是两者都不归（纯 CSS / 无动效）？
4. **加载条件的契约化**：head.html 的加载条件（现 `.Layout == search`，见 0049 事实）改动后是否写进 fastsearch docstring 快照（0049 确认现状是否已在契约里）；B11 三挂点断言与交付面断言如何跟随（断言落点归 0053，本工单只定契约措辞）。
5. **search 页角色**：若 0050 使 search 页不再是唯一落点——其角色（保留为完整检索页 / 退场）在本工单确认，或显式移交雾区（地图 Not yet specified 已有此条）。

**已决输入**：ADR-0008 分层判据、ADR-0007 三层文档契约、ADR-0010 搜索协议快照与「不并入 reveal」决议、0050 形态结论、0051 呈现层结论。

## Resolution

2026-10-23 · grilling（HITL，用户为决策者；两问落定，五条记录经用户最终确认共识）。前提：0050 决议 + 施工实证已回答了本工单五个子问题中的三个。答案五条：

1. **seam 归属与加载机制**：无新决策——站点层 + extend_footer 双 js.Build + params 注入已由 0050 施工落地，构件交付面/加载面有断言守住（assert_search_entry_artifacts / assert_search_entry_real）。记录为既定事实，不重开。
2. **契约定义处与互指（本工单唯一新决策，b 案）**：fastsearch.js docstring 增加互指指针行——全站 `/` 快捷键入口是并列模块（assets/js/mf-search-entry-engine.js，全站恒加载，契约定义处在其文件头 docstring）；入口只负责跳转/聚焦到 search 页，检索仍归本协议；本协议仅 .Layout == "search" 页加载（head.html 条件）vs 入口构件全站每页在——两个搜索相关 JS 面、加载条件不同，勿混。引擎 docstring 指针行同步加强为双向对句。**不合并命名、不并入条款**（ADR-0010 决策 4 同款纪律）。该指针同时是 0049 缺口 3「加载条件无守门」的文档侧补偿（断言侧牙已由 0050 加载面双向断言提供）。
3. **交互归属**：入口是纯功能交互（keydown → 跳转/聚焦，零动效面）——reveal 模块边界是动效交互（ADR-0007），无对象可归；记录为「第三个并列模块，自有 docstring」，此问不成立。
4. **加载条件契约化**：fastsearch 加载条件未变（其 docstring 已收录「仅 .Layout == search」）；新全站加载面由引擎 docstring + fastsearch 指针行双处记录；文档与断言两侧齐备。
5. **search 页角色**：维持现状——全站唯一完整检索落点，角色不变（轻形态下它退场即推翻 0050 决议③，自相矛盾）；**地图雾区第一条「search 页角色重定义」消解**（无变化，不毕业新工单）。搭车两条否：页内提示 `/（P2 可发现性，0050 已排序在后、另开工单）；改面板形态（重浮层，0050 已否决）。

**机械后果**：fastsearch.js docstring 落两笔——互指指针行（本条）+ li 结构条款改写（0051 决议③）；引擎 docstring 指针行加强；地图雾区删第一条，其余三条保留。施工待项目负责人指示展开。

**施工期补记（2026-10-23，项目负责人指示施工；双轴 code-review 后回写）**：

- **落地**：fastsearch.js docstring 落三笔——互指指针行（决议② b 案原文）+ li 条款改写（0051 决议③）+ 文件头新增「呈现层摘要加深与入口互指分别见候选 12 工单 0051/0052 决议」指引行。第三笔为 Spec 轴评审点名的「机械后果清单外」改动：该行沿用文件头既有式样（原头即注「工单 0046 决议①②」），属导航指引而非契约条款，评审后判断保留、在此备案。
- 引擎 docstring 指针加强为双向对句（决议②）；地图雾区第一条删除并留消解注记（决议⑤）；fastsearch 测试行在「jsdom 行为测试未立（ADR-0010 决策 5）」后补回 0047 决议引用（Spec 轴评审点名的误删，已恢复）。
- **节奏说明**：本会话一次解决两张 HITL 工单（0051 三问 → 确认 → 0052 两问 → 确认），由项目负责人指令显式要求（「对工单0051/0052跑 grilling」）——属负责人对 wayfinder README「一次会话一工单」节奏的显式覆盖；分次 grilling 顺序如实记录在两票 Resolution 中。
- 全套复验：assert_site_contracts 87 断言 GREEN、npm test 29 GREEN、assert_sop_pipeline 104 GREEN、生产构建零 WARN、无 localhost:1313、生产构件含 entry-summary。

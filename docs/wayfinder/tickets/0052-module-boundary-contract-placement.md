---
id: "0052"
title: 模块边界与契约落位
type: grilling
mode: HITL
status: open
blocked_by: [0050, 0051]
assignee:
map: map-search-entry.md
created: 2026-10-23
---

## Question

新入口 / 呈现层的模块边界与契约落位（前提：0050、0051 已决）：

1. **seam 归属与加载机制**：新入口代码落站点层还是主题层（ADR-0008 判据：视觉 / 骨架 / 交互 → 主题；内容 / 数据 → 站点）。fastsearch 在主题层（head.html 条件加载）；reveal 引擎在站点层 `assets/js/mf-reveal/`（extend_footer 恒加载）——本项目第一个跨层契约组合的两半各有先例。快捷键 / 首页框的入口脚本落哪、用什么机制加载（head.html 条件扩展 / extend_footer js.Build / 并入 mf-reveal）；两层不得存在同相对路径文件（B13 断言）。
2. **契约定义处**：新交互的 DOM 契约（class / data-* / aria / CSS 变量）落哪个 docstring——扩写 `fastsearch.js` 文件头快照 / 新文件 docstring / reveal 引擎 docstring（ADR-0007 纪律：docstring 是唯一定义处，CONTEXT.md 只放概念）；CONTEXT.md 术语条措辞归 0054，本工单只定「契约住哪」。
3. **交互归属**：入口的进场 / 聚焦 / 浮层展开动效归 reveal 协议还是搜索协议（ADR-0007 模块边界三块：产品索引筛选 / 页脚滚动进场 / 首页 hero 进场；ADR-0010 决议：搜索交互不并入 reveal）——新入口是 reveal 的第四块、搜索快照的扩展、还是两者都不归（纯 CSS / 无动效）？
4. **加载条件的契约化**：head.html 的加载条件（现 `.Layout == search`，见 0049 事实）改动后是否写进 fastsearch docstring 快照（0049 确认现状是否已在契约里）；B11 三挂点断言与交付面断言如何跟随（断言落点归 0053，本工单只定契约措辞）。
5. **search 页角色**：若 0050 使 search 页不再是唯一落点——其角色（保留为完整检索页 / 退场）在本工单确认，或显式移交雾区（地图 Not yet specified 已有此条）。

**已决输入**：ADR-0008 分层判据、ADR-0007 三层文档契约、ADR-0010 搜索协议快照与「不并入 reveal」决议、0050 形态结论、0051 呈现层结论。

---
id: 0024
title: 筛选交互语义定案
type: grilling
mode: HITL
status: closed
blocked_by: [0022]
assignee: agent
map: map-reveal-protocol.md
claimed: 2026-10-20
closed: 2026-10-20
---

## Question

语义即契约——逐条给出推荐答案并标出与现状的差异（定案后每条就是行为断言与文档契约的字面期望值）：

1. 同一筛选值再次点击：回到「全部」（现状 toggle-off）还是保持选中？
2. aria-pressed 的组内互斥规则与初始态（「全部」默认 pressed=true）；
3. 计数文案格式（现状「显示 X / Y」）与 aria-live="polite" 的更新时机；
4. 空态「没有符合筛选条件的资源」的 hidden 切换规则；
5. uid 深链锚是否扩展 hash / URL 行为（当前仅 DOM id，无 pushState）；
6. 减弱动效（prefers-reduced-motion）下筛选是否仍播放 morph 动画（现状不播）。

## 施工期注记（2026-10-20，待本工单追认）

引擎提取施工已把**现状语义**固化为代码与行为断言（`assets/js/mf-reveal/filter.js` + `tests/assert_reveal.mjs`），本题质询将以这些为基线确认或修改——每条决议一旦定案，就是行为断言与引擎 docstring 的字面期望值：

- 同值再点 → 回 all（toggle-off）；
- aria-pressed 组内互斥（当前值 true，同组其余 false）；
- 计数文案「显示 X / Y」，无动画时机差异；
- 空态 `.mf-empty` hidden = (X > 0)；
- uid 仅 DOM id/深链锚，无 hash/URL 行为；
- reduced-motion：过滤与 is-in 照常，morph/bump 不播放。

## Resolution

2026-10-20 · grilling（用户为决策者），四问落定——**全部确认为现状**，施工期固化的语义即契约：

1. **toggle-off 保持**：同值再点回「全部」；aria-pressed 组内互斥，初始「全部」=true。理由：筛选 chip 的标准交互，误点可一键清除；取消 toggle-off 会让选中态按钮点击无反应，与 toggle button 的可访问性语义相悖。
2. **计数与空态保持**：计数「显示 X / Y」；空态双文案分工（无数据「暂无资源」归渲染 seam / 筛空「没有符合筛选条件的资源」由 hidden 切换）；aria-live="polite" 更新。
3. **uid 不扩 hash/URL**：仅 DOM id 锚，筛选状态不写 location。静态博客无分享筛选视图刚需；hash 状态会引入 popstate、首屏回放、与 id 锚共存的复杂度，属范围蔓延。
4. **reduced-motion 不播动画**：过滤与 is-in 终态照常，morph/bump 不播放；与 CSS 媒体查询「定格最终画面」一致。

**下游影响**：无施工动作（引擎与断言已是字面期望值）。第 4 条的判定目前仍三处分布（CSS 媒体查询 + 两引擎各自检查），统一与否交 0025 定。

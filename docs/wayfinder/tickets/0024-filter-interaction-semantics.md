---
id: 0024
title: 筛选交互语义定案
type: grilling
mode: HITL
status: open
blocked_by: [0022]
assignee:
map: map-reveal-protocol.md
---

## Question

语义即契约——逐条给出推荐答案并标出与现状的差异（定案后每条就是行为断言与文档契约的字面期望值）：

1. 同一筛选值再次点击：回到「全部」（现状 toggle-off）还是保持选中？
2. aria-pressed 的组内互斥规则与初始态（「全部」默认 pressed=true）；
3. 计数文案格式（现状「显示 X / Y」）与 aria-live="polite" 的更新时机；
4. 空态「没有符合筛选条件的资源」的 hidden 切换规则；
5. uid 深链锚是否扩展 hash / URL 行为（当前仅 DOM id，无 pushState）；
6. 减弱动效（prefers-reduced-motion）下筛选是否仍播放 morph 动画（现状不播）。

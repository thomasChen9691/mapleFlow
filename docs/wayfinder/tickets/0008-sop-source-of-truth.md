---
id: 0008
title: SOP 文与源笔记的真源归属
type: grilling
mode: HITL
status: open
blocked_by: []
assignee:
map: map-sop-source-sync
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

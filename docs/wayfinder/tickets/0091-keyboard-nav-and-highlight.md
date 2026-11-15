---
id: "0091"
title: 方向键导航与命中高亮的取舍
type: grilling
mode: HITL
status: closed
blocked_by: ["0089"]
assignee: agent
map: map-search-overlay-v2.md
created: 2026-11-15
claimed: 2026-11-15
closed: 2026-11-15
---

## Question

ADR-0013 把两条明确记为「v1 不做」——ArrowUp/Down 选择结果、命中高亮。v2 做不做、做的话契约放哪：

1. **方向键导航**：要不要在浮层内补 ArrowUp/Down 选择结果？若做，选中态的 DOM 契约（class / aria-activedescendant / aria-selected）、与现有「Tab 困排 + Enter 首条 + Esc 关闭」的关系、以及 Enter 在「有选中项」与「无选中项」两种情形下的语义如何定？若不做的理由是否仍是「完整方向键导航留在 search 页」？
2. **命中高亮**：ADR-0011 决策 2 以「需消费 fuse matches、违背只改渲染层边界」否掉过高亮。v2 若要做，是重开该负向决策（须先提重审，AGENTS §8.2），还是把它限定在浮层自有引擎内、不计入 fastsearch 快照？做的话 parity 断言要不要覆盖高亮相关配置。
3. **负向边界的形态**：任何「不做」的结论，是作为负向边界耐久化进 ADR（写明重开触发条件），还是随图挂起进 Not yet specified？参照候选 13 的三条负向与候选 12 的三条挂起各自的判据。
4. **与 search 页的一致性**：浮层与 search 页在同一查询下若键盘行为不同，是否可接受？可接受的话，边界写在哪个契约定义处，避免后来者误以为漏实现。

边界（不开票）：不重写 fastsearch（Out of scope）；具体断言条数归「可测试性的判据与测试缝归属」；视觉高亮样式归视觉层。事实以「搜索浮层 v2 现状事实底座（盘点）」为准。

## Resolution

2026-11-15 · HITL grilling（项目负责人实时对话定案）。

**决策 = 只补方向键，命中高亮不做。**

1. **方向键**：浮层内补 ArrowUp/Down 选择结果；选中态的 DOM 契约（class / `aria-activedescendant` / `aria-selected`）归 `mf-search-overlay-engine.js` 头 docstring（唯一定义处），配新 jsdom 行为断言；MFO-15 Enter 首条 / MFO-16·16b 困排 / MFO-18·19 inert 可存续。与「移动端与小屏的 a11y 契约」的 aria 扩写联动（同一处 docstring 承载）。
2. **命中高亮**：维持 ADR-0013 的 v1 不做，作为**负向边界耐久化**写进 ADR-0017；理由沿用 ADR-0011 决策 2（需消费 fuse matches、违背「只改渲染层」）；**重开触发条件** = 结果可读性成为真实且高强度的需求，且须先按 AGENTS §8.2 提重审。
3. **fuse parity 四元组**（distance / threshold / ignoreLocation / keys）不动；不做「只补高亮」（与 ADR-0013「完整方向键导航留在 search 页」的现状理由相冲）。
4. 浮层与 search 页键盘行为允许不同，这条边界写进引擎 docstring，避免后来者当作漏实现补上。

依赖：0090 分层判据（新增契约条款必须有可定位地红的断言）、0092 的 aria 归属裁定。未选「两条都不补」（丢掉已 materialize 的触发条件）与「两条都补」（须重开 ADR-0011 决策 2 负向）。

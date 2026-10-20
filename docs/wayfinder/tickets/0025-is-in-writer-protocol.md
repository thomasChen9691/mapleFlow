---
id: 0025
title: is-in 写入方协议与动效降级统一
type: grilling
mode: HITL
status: open
blocked_by: [0022]
assignee:
map: map-reveal-protocol.md
---

## Question

`.reveal`/`is-in` 有两位写入方（extend_footer 的 IntersectionObserver 与 product-index 筛选脚本的终态直写），协议如何收口：

1. **is-in 语义**：一次性终态（IO 当前 unobserve）vs 可重放；筛选后可见条目被脚本直写 is-in 的规则（现状有注释解释，需升格为契约条款）。
2. **--mf-i stagger 变量**：由 JS 写入 CSS 自定义属性（第 9 条起截断不累加）——算协议面还是纯视觉细节？
3. **降级分布**：reduced-motion 与无 IntersectionObserver 的降级散在三处（CSS 媒体查询 + 两个脚本的 matchMedia 检查）——统一为单一降级规则，还是接受分布、在文档契约中各写各的？
4. **mf-rise 契约深度**：hero 进场的 d1/d2/d3 delay 类与 `.no-js .mf-rise` 降级，契约化到什么程度（仅断言存在性，还是语义条款）。

## 施工期注记（2026-10-20，待本工单追认）

引擎提取后的现状（0022 决议的施工产物，本题以此为基线）：

- **两个 is-in 写入方**：`scroll-in.js`（IntersectionObserver，进入视口加 is-in 并 unobserve，一次性）；`filter.js` 的 `apply`（用户交互后对可见行直写 is-in 终态）。
- **降级仍三处分布**：CSS 媒体查询（custom.css:228-247）+ `scroll-in.js` 的 reduce 分支 + `filter.js` 的 `prefersReducedMotion` 守卫。评审建议抽共享判定模块，**未执行**——统一与否正是本题待决，不提前实施。
- `--mf-i` 由 filter.js 写 CSS 自定义属性（第 9 条起截断为 8）；`replay` 用单槽 `morphTimer`。
- mf-rise 的契约深度已在 0022 映射中暂定为「存在性断言」（B3 含 d1/d2/d3），语义条款是否升格由本题定。

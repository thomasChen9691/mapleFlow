---
id: 0025
title: is-in 写入方协议与动效降级统一
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

## Resolution

2026-10-20 · grilling（用户为决策者），四问落定：

1. **is-in = 一次性终态**：IO 点亮即 unobserve；筛选交互后对可见行直写 is-in（跳过动画直达终态）；不重放、不因筛选回退为透明。「终态」即协议语义——元素要么未亮、要么永久亮。
2. **`--mf-i` 归属 = 语义归协议、数值归 CSS**：变量名与「第 9 条起截断」的语义写进引擎 docstring 并断言；22ms 延迟值属 CSS 调值不测（C 类逐出）。`replay` 单槽 `morphTimer` 保留——当前仅 morph 一用，出现第二种带 timer 的重播时再泛化。
3. **降级统一 = JS 共享判定 + CSS 兜底**：抽单一 `prefersReducedMotion(win)` 供两引擎共用（落 `assets/js/mf-reveal/motion.js`，命名随 0026 定）；CSS 媒体查询保留为独立兜底层（JS 加载失败时仍定格终态，ADR-0002 基线不破）。层次分工，不是重复实现。
4. **mf-rise 契约深度 = 存在性 + 降级**：B3 断 d1/d2/d3 存在、B6 断 `.no-js .mf-rise`；延迟数值不测。

**下游影响（施工动作，待用户指示）**：抽 `motion.js` 共享判定并改两引擎 import（行为不变，回归跑两套件）；filter.js / scroll-in.js docstring 指向共享判定；0026 收口时把「契约定义处 = 引擎 docstring」写进 AGENTS.md 导航。评审曾标记的两引擎判定重复，由此决议转为正式施工项。

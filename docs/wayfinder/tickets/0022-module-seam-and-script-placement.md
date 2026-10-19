---
id: 0022
title: 模块边界内的 seam 划分与脚本落点
type: grilling
mode: HITL
status: closed
blocked_by: [0021]
assignee: agent
map: map-reveal-protocol.md
claimed: 2026-10-19
closed: 2026-10-19
---

## Question

模块边界已钉（三块全含：筛选脚本 + 滚动进场 IO + hero mf-rise，共享 no-js 基线），本工单定**边界之内**的结构：

1. **seam 划分**：契约 spec（单一真源）→ HTML/CSS 产出 → JS 行为，各自由哪个文件承载？「协议」以什么形态存在——CONTEXT.md 术语 + 各文件 docstring 契约注释（文档形态），还是提炼为可执行常量 / 执法点（代码形态）？
2. **脚本落点**：三段脚本（extend_head 的 class swap、extend_footer 的 IO、product-index 内联筛选）保持内联，还是提取为 assets/js 下的共享文件经 js.Build 引用（若 0021 证实 0.164 可行）？判据：可测试性、AI 可导航性、PaperMod 覆盖文件升级同步负担（ADR-0002 已知义务）的权衡。
3. **与 ADR-0006 的接口关系**：product-index.html 的筛选 UI 归产品索引渲染 seam（filters 开关、uid 挂点已定），本模块接管 UI 之下的行为层——uid 挂点、data-* 属性、filters 开关是否即协议面的组成部分，在文档契约里如何归属？

## Resolution

2026-10-19 · grilling（用户为决策者），四问落定：

1. **脚本落点 = 分层提取**：`extend_head` 的 class swap 保持 inline（ADR-0002 两个升级同步文件之一，内容越薄升级面越小）；`extend_footer` 的 IO 滚动进场与 `product-index` 的筛选引擎提取为 `assets/js` 下的模块、经 js.Build 引用（先例：PaperMod 自家 `head.html:80` 正用 `js.Build | Minify | Concat | fingerprint` 管线，本 Hugo 版本生产验证）。template 不再内联 script，只产出 DOM 契约挂点。
2. **协议形态 = 三层文档契约**：① CONTEXT.md 术语（概念层）② 引擎文件头 docstring 为 DOM 契约**唯一定义处** ③ 测试期望值字面量。不新建 spec seam——ADR-0006 Consequences 明挂词汇 seam「待词表真要扩展时再评估」，现在不是扩展时，闭卷决策不提前撬。
3. **DOM 契约命名权归协议层**：class / data-* / aria 词汇由协议层定义（引擎 docstring），product-index 渲染 seam 是消费者。ADR-0006 接口语义不动：uid 仍 DOM id 必填兼深链锚（短代码 `.Ordinal` 页内保唯一不变），引擎改为遍历 `.mf-index` roots 自动注册（uid 不再是注册键、仍是锚）。`.reveal/is-in` 的定义处问题由此解决（写入方 extend_footer 不在产品索引链路）。
4. **测试存活映射**（12+ 契约点分流，作 0023 缺口清单）：
   - **A 行为 harness（9 项）**：筛选 state 切换 / 同值回 all + 组内互斥 aria-pressed / is-hidden + 计数 + 空态 / is-in 终态直写 / `--mf-i` 赋值与截断 / morph + bump 重播（含 520ms 移除）/ reduced-motion 不播放 / IO 三态（无 IO 全量直写、视口点亮、unobserve 一次性）/ 同页多实例 roots 独立。
   - **B 产物断言（6 项）**：`<html class="no-js">` + swap inline 脚本在 / js.Build 产出的 script src 入 built HTML / `.reveal` + mf-rise d1-d3 存在 / data-* 挂点存在 / mf-filter 按钮集（已有，0019）/ 产物 CSS 含 `.no-js .reveal` 降级规则。
   - **C 逐出（2 项）**：视觉参数数值（delay 22ms、520ms、rootMargin/threshold 等纯审美）不测；搜索 JS 归候选 8。

**下游影响**：0023 的缝（harness 落点、与 assert_product_states.py 合流或新脚本、样本来源）已有 A/B 分流底坐；0024 语义清单不变；0025 的 is-in 写入方协议以「协议层拥命名权」为前提收口；0026 收口时 CONTEXT.md 术语条 + AGENTS.md「契约定义处 = 引擎 docstring」一行。地图雾区两条随本题消解（多实例共享化取舍 → 单一外部引擎遍历 roots；mf-rise 契约深度 → 定在存在性断言 B12）。

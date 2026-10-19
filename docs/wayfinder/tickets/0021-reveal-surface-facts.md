---
id: 0021
title: reveal 面事实底座与 JS 可测试性事实
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-reveal-protocol.md
claimed: 2026-10-19
closed: 2026-10-19
---

## Question

开图前的两块事实底座（本工单只产事实、不产决策）：

1. **面内盘点**：「reveal 面」的完整清单——哪些文件、哪些行为、写与读哪些契约（html 的 no-js/js 基线类、`.reveal` → `is-in`、`.mf-rise`/d1-d3、筛选脚本的 data-* / aria-pressed / is-hidden / is-morphing / is-bump / --mf-i、CSS 的 no-js 降级与 prefers-reduced-motion 分支），以及每一块当前的测试覆盖（预期：现有产物断言只碰到 `mf-filter` 控件有无，其余为零——若有不符，以实际为准）。

2. **外部事实**（对照 Hugo 0.164 官方文档核实，CI 钉 0.164.0 extended）：
   - 自定义 JS 的加载机制选项：内联 partial（现状：extend_head / extend_footer / product-index 内 script 块）vs Hugo Pipes 的 js.Build（0.164 是否可用、能力边界：bundling / minify / 指纹、如何从 assets/js 产出并在页面引用、源码文件是否保持可单测形态）；
   - `--minify` 对 JS 产物的影响（生产构建是否改写 JS，影响「以产物断言」的哪些面）；
   - Node 端 DOM 行为测试可行性：jsdom / happy-dom（能否加载构建产物 HTML 并执行内联脚本）、CI（GitHub Actions ubuntu-latest）上的增量成本。**不实际安装任何包**，只做可行性结论。

## Resolution

2026-10-19 · research（agent 驱动，结论落 [research/0021-reveal-surface-facts.md](../research/0021-reveal-surface-facts.md)）：

1. **面内盘点 = 12+ 契约点表**（A1）：no-js 基线类与 head swap、mf-rise/d1-d3、`.reveal→is-in`（两个写入方：extend_footer IO 与筛选脚本直写）、筛选按钮 data-group/value 与 aria-pressed、is-hidden、--mf-i、is-morphing/is-bump、计数文案、空态双态、reduced-motion 三处分布、data-kind/price 筛选依据。每点标注产生者/消费者/行号。
2. **测试覆盖近乎零**（A2）：两个断言脚本对 `reveal/is-in/mf-rise/no-js/mf-count/is-hidden/aria-pressed` 零命中；唯一相邻断言是 `mf-filter` 控件有无（0019 的 filters 开关差异）。该表即 0023 的缺口清单。
3. **外部事实三连**：① js.Build **v0.74.0 引入**（2022-07-13 release notes 实证「native JavaScript bundling (and minifier)」；早期假设的 0.98/0.101/0.103 均被实证否定），0.164 可用，`assets/js/*.js` 源文件不被构建改写、保持可单测形态；② `--minify` 默认改 JS（tdewolff，`disableJS=false`）——产物断言不得匹配脚本文本，但语义不变、可执行；③ jsdom 30.1.3 / happy-dom 21.0.3 均可达（未安装），jsdom `runScripts:"dangerously"` 可执行 inline script，matchMedia/IntersectionObserver 需 stub，而脚本对两者的守卫路径恰好成为可断言对象；CI（ubuntu-latest）加 node 步为行数级增量，harness 消费产物 → 与 Hugo 版本 skew 解耦。

**下游影响**：0022 的脚本落点二选一（inline / js.Build）两侧事实齐备；0023 的双层测试缝（行为 harness + 产物契约）有可行性底坐；0024/0025 的语义清单可直接引用 A1 表的现状差异。

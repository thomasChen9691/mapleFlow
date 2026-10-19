---
id: 0022
title: 模块边界内的 seam 划分与脚本落点
type: grilling
mode: HITL
status: open
blocked_by: [0021]
assignee:
map: map-reveal-protocol.md
---

## Question

模块边界已钉（三块全含：筛选脚本 + 滚动进场 IO + hero mf-rise，共享 no-js 基线），本工单定**边界之内**的结构：

1. **seam 划分**：契约 spec（单一真源）→ HTML/CSS 产出 → JS 行为，各自由哪个文件承载？「协议」以什么形态存在——CONTEXT.md 术语 + 各文件 docstring 契约注释（文档形态），还是提炼为可执行常量 / 执法点（代码形态）？
2. **脚本落点**：三段脚本（extend_head 的 class swap、extend_footer 的 IO、product-index 内联筛选）保持内联，还是提取为 assets/js 下的共享文件经 js.Build 引用（若 0021 证实 0.164 可行）？判据：可测试性、AI 可导航性、PaperMod 覆盖文件升级同步负担（ADR-0002 已知义务）的权衡。
3. **与 ADR-0006 的接口关系**：product-index.html 的筛选 UI 归产品索引渲染 seam（filters 开关、uid 挂点已定），本模块接管 UI 之下的行为层——uid 挂点、data-* 属性、filters 开关是否即协议面的组成部分，在文档契约里如何归属？

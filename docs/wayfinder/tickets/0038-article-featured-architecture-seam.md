---
id: "0038"
title: 文章精选的架构落点与 seam 划分
type: grilling
mode: HITL
status: open
blocked_by: ["0036"]
assignee: ""
map: map-featured-mechanism.md
created: 2026-10-21
---

## Question

文章精选的**代码落点**——是否复用 ADR-0006 的双 seam 模式，还是维持首页内联；以及由此决定的站点层/主题层归属与 AI 导航形态。这是「使该模块可测试、AI 可导航」里「可导航」的主战场。

待决：

1. **是否拆 seam**：现状选文逻辑内联在 `layouts/index.html:81`（一行 `first 3 (...)`）。产品侧的先例是「数据准备 partial（唯一读数据源 + 过滤/截断）+ 纯渲染 partial（零全局读）」。文章侧的 `$pages` 来自 `site.RegularPages` 而非 `hugo.Data`，是否仍值得拆？判据应是「未来谁会改它、改的时候会不会漏改另一处」，而非机械对称。
2. **若拆**：命名与位置（`layouts/partials/post-items.html` 对称于 `product-items.html`？）；入参是否与产品侧同名同义（`featured`/`limit`）；负数/坏值是否同样 errorf；是否与产品侧共享一个**跨数据源的通用挑选 partial**（抽象成本 vs 两份近似实现）。
3. **层级归属**：首页编排属站点层（ADR-0008 判据「内容策略」）。但若「精选文章」也被文章列表页/分类页复用（见地图雾区），挑选逻辑的归属是否要上移；两层不得同相对路径的约束如何满足。
4. **AI 可导航要求**：新 seam 若建立，docstring 契约（入参/返回值/失败语义）、`AGENTS.md` §7 速查行、断言入口三处是否齐落——参照 ADR-0006/0007 的「定义处唯一」纪律；若维持内联，则须说明为何此处不需要 seam（避免「没拆也没记录」的第三种状态）。
5. **与 reveal 协议的边界**：区块的 `reveal` class 与滚动进场属 reveal 协议（ADR-0007），本题不重开，只确认拆分后 class 契约不破。

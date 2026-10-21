---
id: "0038"
title: 文章精选的架构落点与 seam 划分
type: grilling
mode: HITL
status: closed
blocked_by: ["0036"]
assignee: agent
map: map-featured-mechanism.md
created: 2026-10-21
claimed: 2026-10-21
closed: 2026-10-21
---

## Question

文章精选的**代码落点**——是否复用 ADR-0006 的双 seam 模式，还是维持首页内联；以及由此决定的站点层/主题层归属与 AI 导航形态。这是「使该模块可测试、AI 可导航」里「可导航」的主战场。

待决：

1. **是否拆 seam**：现状选文逻辑内联在 `layouts/index.html:81`（一行 `first 3 (...)`）。产品侧的先例是「数据准备 partial（唯一读数据源 + 过滤/截断）+ 纯渲染 partial（零全局读）」。文章侧的 `$pages` 来自 `site.RegularPages` 而非 `hugo.Data`，是否仍值得拆？判据应是「未来谁会改它、改的时候会不会漏改另一处」，而非机械对称。
2. **若拆**：命名与位置（`layouts/partials/post-items.html` 对称于 `product-items.html`？）；入参是否与产品侧同名同义（`featured`/`limit`）；负数/坏值是否同样 errorf；是否与产品侧共享一个**跨数据源的通用挑选 partial**（抽象成本 vs 两份近似实现）。
3. **层级归属**：首页编排属站点层（ADR-0008 判据「内容策略」）。但若「精选文章」也被文章列表页/分类页复用（见地图雾区），挑选逻辑的归属是否要上移；两层不得同相对路径的约束如何满足。
4. **AI 可导航要求**：新 seam 若建立，docstring 契约（入参/返回值/失败语义）、`AGENTS.md` §7 速查行、断言入口三处是否齐落——参照 ADR-0006/0007 的「定义处唯一」纪律；若维持内联，则须说明为何此处不需要 seam（避免「没拆也没记录」的第三种状态）。
5. **与 reveal 协议的边界**：区块的 `reveal` class 与滚动进场属 reveal 协议（ADR-0007），本题不重开，只确认拆分后 class 契约不破。

## Resolution

2026-10-21 · grilling（HITL，用户为决策者）：

1. **形状 = 单 seam 返回两片，渲染不抽**：新增一个数据准备 partial（站点层 `layouts/partials/`），**一次调用返回 `{featured, rest}`**——两片由**同一个谓词**算出，杜绝「精选与网格之间漏文章/重文章」。渲染不抽：精选继续用编号行 `mf-rows`、网格继续用卡片 `mf-posts`，两套形态强行统一会引入模式参数，正是 ADR-0006 收敛掉的那类病。**不照搬产品侧双 seam**（纯渲染 seam 在这里没有第二个消费点）。
2. **入参 = 只收 `limit`**：数据源固定 `site.RegularPages`；featured 数量由调用点传字面量 `3`；**不留 `source` 注入位、不留 `featured` 开关**（两片同出，开关无意义）——ADR-0006 决策 2「不留死参数/注入位」直接适用。
3. **谓词与校验只此一处**：featured 判定（严格布尔）、坏值 errorf（`isset` 区分未声明与写错）都归 seam。**产品侧对称校验**放在 `product-items.html` 内（其数据源不同，不能共用 seam），两侧错误消息前缀沿用各自模块惯例（「产品索引数据：」）。
4. **层级归属 = 站点层**：首页编排属内容策略（ADR-0008 判据），文件落 `layouts/partials/`，不进主题层；满足「两层不得同相对路径」不变量。
5. **AI 可导航**：seam 文件头 docstring 是契约定义处（入参、返回值两片、失败语义），`AGENTS.md` §7 速查表加一行（0041 落账）；不新建第二个术语（CONTEXT 的「精选」条已覆盖概念）。
6. **真实数据不锚**：生产构建只保留既有冒烟（exit=0、无 localhost 残留），**不对真实精选清单做断言**——内容由项目负责人掌控，锚死会让每次标 featured 都变红。

**施工提示（供后续会话）**：分页必须建立在 `rest` 上而非全集，否则剔除失效；`.Paginate` 只调一次（同一模板重复调用不同集合会报错）。

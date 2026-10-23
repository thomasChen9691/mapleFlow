id: "0058"
title: 分类页 / 标签页是否消费精选（雾区三）
type: grilling
mode: HITL
status: closed
blocked_by: ["0055"]
assignee: agent
map: map-featured-fog-zones.md
created: 2026-10-23
claimed: 2026-10-23
closed: 2026-10-23
---

## Question

分类页 / 标签页是否消费精选——文章列表排序是否 featured 优先，还是精选只作用于首页？这是 ADR-0009 边界条留悬的第三条雾区，本票把它定到可施工精度。

要决策的面：

1. **做不做**：分类页 / 标签页（Hugo `term` kind，走主题层 `list.html`）的文章列表是否 featured 优先排序？`/posts/` 文章列表页（section list，同走 `list.html`）是否同样处理？若不做，记录负向决策与理由（精选是首页编排概念，外溢到分类页是否稀释「精选」语义、是否与「集内日期倒序」的首页规则冲突）。
2. **落点与分层**：若做，排序逻辑落哪——`post-items.html` seam 扩展（它当前只收 `limit`、返回三片，语义是「首页精选链」）/ 新 partial / 主题层 `list.html` 直改？分层判据（ADR-0008）：`list.html` 是主题层文件，站点层覆盖（两层不得同相对路径——覆盖即站点层新建 `layouts/_default/list.html`）还是主题层直改（改行为基线）？排序与分页（`.Paginate`）的交互怎么处理。
3. **契约与断言**：排序契约的定义处落哪个 docstring；断言怎么锚（term 页产物构建里 featured 文章的位次、fixture 已具备否）；与「补集对实际显示的精选求」等 ADR-0009 硬约束的一致性。

边界（不开票）：RSS 输出是否跟随已入地图雾区（取决于本票决议）；排序的稳定性（同日文章的次级排序）若成为问题随施工期处理；视觉归视觉层。

事实前提以 `research/0055` 为准（第 2 项：list.html 取页与默认排序、posts 列表页渲染链；第 5 项：现有断言清单）。

## Resolution

2026-10-23 · grilling（HITL，项目负责人两问定案）：

**决议一（做不做）**：**不做，三页统一负向**——分类页 / 标签页 / `/posts/` 文章列表页（三者同走主题层 `list.html`，`union .RegularPages .Sections` → `.Paginate`）**维持日期倒序**，不 featured 优先。理由：① term 页访问意图是「找这个分类下的**新**文章」，置顶 3 篇精选直接打破「最新在前」心智；② 池子只有 3 篇 featured，置顶挤压新文章曝光，个人博客内容消费路径里收益不抵成本；③ 断言面从零建（缺口 2：列表/term 页零专属断言），且期望值要耦合 Hugo 默认排序链（weight→date→LinkTitle→filepath）被改写后的行为；④ 外部惯例（research 第 6 项）显示 sticky 与「最新在前」的冲突是通行代价，ADR-0009 已为 3 条规模显式拒绝过 `weight` 手工序。精选是首页编排概念（Q1 分层默认），term 页是完整内容流。

**决议二（边界守门）**：**docstring 收紧，不上产物断言**。`post-items.html` docstring 补硬边界措辞（「只服务首页精选链；其他页面消费 featured 须先过新决策——本图 0058 已决 term 页不做」），AGENTS.md 坑点 11 同步一句。否掉产物断言守牙：断言「fixture term 页首卡 = 日期最新」等于把 Hugo 默认排序链的现状锁进测试，主题未来正当改排序会误红，且该失败模式（有人给 list.html 加 featured 排序）不可能无意发生——它必须过决策。**落地归 0059 收口批**（与坑点 11 同步句同批执行）。

**重开触发条件（将来）**：精选池显著增大（如 10+ 篇）且访客在分类页的「找好文」需求被真实反馈——届时连排序稳定性（同日文次级序）与断言面一并决。

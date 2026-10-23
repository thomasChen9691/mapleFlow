id: "0058"
title: 分类页 / 标签页是否消费精选（雾区三）
type: grilling
mode: HITL
status: open
blocked_by: ["0055"]
assignee: 
map: map-featured-fog-zones.md
created: 2026-10-23
---

## Question

分类页 / 标签页是否消费精选——文章列表排序是否 featured 优先，还是精选只作用于首页？这是 ADR-0009 边界条留悬的第三条雾区，本票把它定到可施工精度。

要决策的面：

1. **做不做**：分类页 / 标签页（Hugo `term` kind，走主题层 `list.html`）的文章列表是否 featured 优先排序？`/posts/` 文章列表页（section list，同走 `list.html`）是否同样处理？若不做，记录负向决策与理由（精选是首页编排概念，外溢到分类页是否稀释「精选」语义、是否与「集内日期倒序」的首页规则冲突）。
2. **落点与分层**：若做，排序逻辑落哪——`post-items.html` seam 扩展（它当前只收 `limit`、返回三片，语义是「首页精选链」）/ 新 partial / 主题层 `list.html` 直改？分层判据（ADR-0008）：`list.html` 是主题层文件，站点层覆盖（两层不得同相对路径——覆盖即站点层新建 `layouts/_default/list.html`）还是主题层直改（改行为基线）？排序与分页（`.Paginate`）的交互怎么处理。
3. **契约与断言**：排序契约的定义处落哪个 docstring；断言怎么锚（term 页产物构建里 featured 文章的位次、fixture 已具备否）；与「补集对实际显示的精选求」等 ADR-0009 硬约束的一致性。

边界（不开票）：RSS 输出是否跟随已入地图雾区（取决于本票决议）；排序的稳定性（同日文章的次级排序）若成为问题随施工期处理；视觉归视觉层。

事实前提以 `research/0055` 为准（第 2 项：list.html 取页与默认排序、posts 列表页渲染链；第 5 项：现有断言清单）。

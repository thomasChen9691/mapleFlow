---
id: "0043"
title: 搜索契约的模块边界与 seam 形状
type: grilling
mode: HITL
status: closed
blocked_by: [0042]
assignee: agent
map: map-search-contract.md
created: 2026-10-22
claimed: 2026-10-22
closed: 2026-10-22
---

## Question

「搜索契约」作为可测试、AI 可导航的模块，边界与架构落点是什么？具体待决：

1. **index.json 投影的 seam 形状**：收窄为「数据准备 seam + 消费方」双 seam 形态（对照 ADR-0006 product-items / product-index 先例：数据准备唯一读数据源并执法契约，消费方零全局依赖），还是保持单文件投影 + 文件头 docstring 契约（对照 ADR-0005 `_content.gotmpl` 先例）？判据维度：投影的消费点数量（fastsearch 一个？）、契约复杂度、坏值执法需求（0044 的输入）。
2. **契约定义处的分层**：是否沿用 ADR-0007 的三层文档契约模式——CONTEXT.md 术语条（概念层）/ 投影文件头 docstring（契约定义处）/ 测试期望值字面量？若建独立 docstring seam，文件落站点层哪一目录。
3. **跨层模块的相容性**：投影（站点层）与 fastsearch（主题层 vendored 上游）是否同属一个被命名的协议模块；模块命名（「搜索契约」/「搜索协议」/ 其他）与 ADR-0008 分层判据如何相容（**2026-10-22 勘误**：排图期此处写的「跨层先例：reveal 引擎在主题层 `assets/js/mf-reveal/`、消费方在站点层 `product-index.html`」不成立——reveal 引擎实际在站点层 `assets/js/mf-reveal/`，并非跨层模块；本题是本项目第一个跨层契约组合，结论「不合并命名」不受影响）。
4. **搜索页（`search.md` + `search.html`）是否入模块**：它今天归主题层呈现 + 站点层内容各一半，B11 断言已守挂点；模块边界是否含页面本身，还是只含「投影 + 检索协议」。

背景（事实）：ADR-0006 双 seam 先例与其 Considered Options（数据准备外移 / 内驻只正语义均被拒）；ADR-0007 三层文档契约；ADR-0008 分层判据与「两层不得有同相对路径文件」；工单 0019 Resolution 3 的边界注释（投影直读 products 不过 kind 门禁）是本图的直接输入。

## Resolution

2026-10-22 · grilling（用户为决策者），五问落定：

1. **执法约束**：投影守自己消费的字段——产品 name/summary 必填、缺失即 errorf（前缀「搜索索引数据：」）；页面/派生侧不加投影层执法（%!s() 归 SOP 管线契约，0044 记边界）；listed/price/buy_url/kind 不重验（产品链已有门禁，重复验证即两处执法必然漂移）。此决定独立于 0045——无论 kind 门禁怎么定，name/summary 都无人守。
2. **seam 形状**：index.json **单文件自足**（投影 + jsonify + errorf 同住一个文件，对照 `_content.gotmpl` 先例）；不拆双 seam——薄渲染 seam 在产品侧的存在意义是两种渲染形态，JSON 只有一种；坏用例测试走 `bad/` fixture 机制，不依赖拆 seam。
3. **契约分层**：**三层文档契约**（与 ADR-0007 reveal 同构）——CONTEXT.md 概念术语条（措辞归 0048）/ index.json 文件头 docstring 为投影契约唯一定义处，五块内容（字段表[含 summary/content 同源事实]、三类排除规则、产品投影、fastsearch 接口条款、errorf 清单）/ 测试期望值字面量。不建 spec seam（0006/0007 已拒）。
4. **模块边界**：**只圈站点层投影**（模块即「搜索索引投影」）；fastsearch 治理归 0046（若其协议化，两模块在 CONTEXT.md 并列互指、不合并命名——合并要先赌 0046 结论且让「因什么而变」的分层判据失灵）；search 页面不入边界（B11 继续守挂点），但交付面（outputs JSON / head.html preload / XHR 路径）写进 docstring 条款——交付面坏掉搜索静默失效，正是契约该记的。
5. **断言取舍**：**keys 对齐静态断言**（fastsearch 默认 keys 与投影字段精确对齐，差集恰为 tags/categories——跨层接口条款唯一的牙）+ **文章侧字段与三类排除规则**挂 fixture 构建（新建 `tests/fixtures/content-search` 内容目录，复用 `hugo.test.posts.toml` + `--contentDir` 既有机制即 0039 的 none/all/bad 变体同款，不新增构建配置）；现有三条 index.json/挂点断言全部存活；docstring 与实现漂移靠纪律（全项目如此，靠变异检验 + review）。

**同场施工**（项目负责人指示，TDD 红绿一次一行为）：errorf 两个坏用例先红后绿；docstring 五块 + CONTEXT.md「搜索索引」术语条落位；keys 对齐与文章侧断言落 `tests/assert_site_contracts.py`（套件合流/命名的最终形态归 0047）；每条断言变异检验（破坏实现→红→还原）。

**下游**：0044 随之可开工（输入：errorf 前缀、docstring 五块、truncate 取值是否入契约、SOP intro 边界）；0046 须与接口条款保持一致（重写 fastsearch 则条款锚点随移）；0047 拿到三处新断言的落面；雾区「索引体积治理」并入 0044 字段契约问题（已是活工单的子问题，按规则移出雾区），「fastsearch 引擎形态」加注不合并前提。

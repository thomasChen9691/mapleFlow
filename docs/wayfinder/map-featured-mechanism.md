---
id: map-featured-mechanism
title: 精选机制图（候选 7）
labels: [wayfinder:map]
status: closed
created: 2026-10-21
closed: 2026-10-22
---

# 精选机制图（候选 7）

## Destination

候选 7「精选机制」的决策集定稿：文章侧 featured 契约（字段语义、派生文归属）、首页精选文章区的选择与呈现行为、模块的架构落点（seam 划分）、测试缝与导航契约——达到「可测试、AI 可导航」的可施工状态即收口。产品侧 featured 契约已由 ADR-0006 锁定，本图不重开，只在跨类语义一致性上做确认。本图只产决策；施工按候选 5/6 先例，经项目负责人指示后展开。

## Notes

- **边界（开图时与项目负责人钉死，2026-10-21）**：候选 7 = 精选机制**整体治理**（文章 + 产品两类内容）；产品侧已锁契约不重开；不改搜索索引投影（候选 8）；不调视觉/CSS 参数；不动内容填充（about.md、products.yaml 的 buy_url 等卡用户材料）。
- 术语以根目录 `CONTEXT.md` 为准；「精选 (Featured)」条已存在（声明覆盖文章与产品两类），本图只确认/微调，不另造同义词。
- 闭卷 ADR：0001（生产构建命令）、0002（no-js 渐进增强基线）、0004（产品状态模块）、0005（SOP 发布管线）、0006（产品索引双 seam，**含产品侧 featured 语义：缺省 false、where true、limit 截断、负数 errorf**）、0007（reveal 协议）、0008（主题 fork 与分层契约）。
- 方向已 ratified（2026-10-15 起多份 handoff，及候选 4/5/6 地图 Out of scope 记录）：给文章加 featured 字段，首页「精选文章」区块改真精选。本图不重开方向，只把落地面的决策钉死。
- Hugo 0.164 语义编写（CI 钉版）：0.166+ 的条件多 return 写法本地过、CI 红，禁止。
- 测试总原则：Hugo 无模板单测，静态产物只能 build-then-assert；fixture 基建单份（ADR-0004/0006 枪毙第二实现）；变异检验 + 独立字面量期望值（ADR-0007 先例）。
- 分层判据（ADR-0008）：因视觉 / 骨架 / 交互而变 → 主题层；因内容策略 / 数据结构而变 → 站点层；两层不得存在同相对路径文件。
- 用户是项目负责人：HITL 工单必须实时对话解决，agent 不得自答；事实自己查，决策问用户；一次一问，先给推荐答案。
- 事实底座：`research/0035`（文章侧零实现、首页选文实为「最新 3 篇」、产品侧契约与断言清单、fixture 只覆盖 dataDir 对文章侧的扩展缺口）。后续工单的事实争辩以该份为准，不重新推导。
- 排图日 2026-10-21：研究工单 0035 当日解决，事实落 `research/`，本图只留 gist。

## Decisions so far

- [精选机制事实底座（现状盘点）](tickets/0035-featured-mechanism-facts.md) — 文章侧 featured **零实现**；首页「精选文章」实为 `first 3 ($pages.ByDate.Reverse)` 即最新 3 篇，与同页「最近更新」网格同源必然重复；**当前精选位实测为手写 1 篇 + 派生 2 篇混排**；产品侧契约与 4 条断言齐备；fixture **只覆盖 dataDir**（文章 fixture 需 contentDir 覆盖，且 fixture 内派生文为 0）；SOP 派生 front matter 唯一生成点 `_content.gotmpl:61-69`（params 仅 categories/tags）；搜索索引不含 featured（候选 8 边界）；内容 5 手写（含 1 脚手架 draft）+ 6 派生。
- [文章 featured 字段契约](tickets/0036-post-featured-field-contract.md) — 顶层 `featured`（与 products.yaml 同名同义）；未声明 = 非精选；**只认布尔 true**（实测 `where "Params.featured" true` 对 `"true"`/`"false"`/`yes`/`1` 全不匹配；`if .Params.featured` 因 `"false"` 为真值而禁用）；坏值 **errorf**（isset 区分未声明与写错）；archetype 不加字段只加注释；**产品侧一并补同款校验**，跨类统一为「布尔/缺省非精选/只认 true/坏值 errorf」。
- [首页精选文章区的选择与呈现行为](tickets/0037-home-featured-posts-behavior.md) — 精选 3 篇**从「最近更新」网格剔除**（剔除后为空则整块不渲染）；featured 不足按实显示、**0 篇隐藏不写空态文案**；集内**日期倒序**（不引入 weight）；**固定 3 条**（调用点字面量，不加 hugo.toml 参数）；标题与入口保持。
- [文章精选的架构落点与 seam 划分](tickets/0038-article-featured-architecture-seam.md) — **单 seam 一次返回 `{featured, rest}` 两片**（同一谓词算补集，杜绝漏/重），**渲染不抽**（编号行 vs 卡片两套形态）；入参**只收 limit**（数据源固定、不留 source 注入位/featured 开关）；谓词与坏值校验只此一处、产品侧对称校验在 product-items；落站点层；docstring 为契约定义处；真实精选清单不锚。
- [精选机制的测试缝与断言集](tickets/0039-featured-test-seam.md) — **新增独立 fixture 构建**（第三配置文件只设 contentDir，不动现有 48 条的构建环境；接受派生文在 fixture 内为 0）；**必锚四条**：过滤+缺省 / 截断（第 4 篇不上）/ **两片互斥无遗漏** / 空态+坏值 errorf；落点**并入并改名** `assert_site_contracts.py`（0032 命名债触发）；改名成本实测 **12 处活引用 + 约 25 处历史引用**（历史不改，AGENTS 加旧名指针），**搭施工批次的车**不单独提交；真实清单不锚；变异检验 + 独立字面量沿用。
- [SOP 派生文是否参与精选](tickets/0040-sop-derived-featured.md) — **参与**（否则精选池只剩 4 篇手写、退化为「手写全集」）；注册表加可选 `featured` + `_content.gotmpl` **条件传键**（实测盲传 nil 会让 `isset` 为真、触发 0036 的坏值 errorf 误报）；**契约四类 → 五类**（三处同步）；首标 3 篇手写：`sop-ops-tools-index` / `k8s-common-commands` / `aiops-state-and-tools`；派生文路径由 `assert_sop_pipeline.py` 的 fixture 透传断言覆盖（不靠改内容凑测试）；golden 不受影响（已核）。

- [收口：术语、导航与 ADR 耐久化](tickets/0041-closure-terminology-adr.md) — **新开 ADR-0009** 承载五组决策（字段契约 / 首页行为 / seam 形状 / 测试缝 / 派生文归属）；**ADR-0006 加指针行**（其 featured 语义被跨类统一扩展）；ADR-0005 指针已在施工期以补记落；**新增 AGENTS 坑点 11（文章精选纪律）+ 坑点 12（fixture 时间陷阱）**；术语不新增「精选池」类概念（既有「精选」条已在施工期补齐语义）；同场写 handoff + 地图 closed。**本题关闭 = 目的地到达。**

## Not yet specified

<!-- 雾区：在目的地内、但还无法精确表述的问题。随 frontier 推进毕业为工单。 -->

- **「精选」标识在内容层的呈现**：文章页 / 列表页是否显示精选徽标、卡片是否有视觉区分——语义未决，且紧邻视觉层边界（视觉调值本身 out of scope）。
- **首页数据条与精选的关系**：「篇技术文章」计数是否区分精选、是否新增「精选 N 篇」类数字。
- **分类页 / 标签页是否消费精选**：文章列表排序是否 featured 优先，还是精选只作用于首页。

## Out of scope

- **搜索契约**（`index.json` 投影字段 + fastsearch + kind 门禁）：候选 8（0019/0026/0008 边界注记）。
- **视觉 / CSS 参数调值**（精选卡片样式、动效时长、降级阈值）：视觉层（候选 5 地图先例）。
- **产品侧 featured 契约重开**（缺省语义 / limit / 负数 errorf）：ADR-0006 已锁，本图只引用不重开。**例外**：产品侧坏值类型校验是 0006 从未定义的空白，由 0036/0038 决议补齐（补空白 ≠ 重开）。
- **内容填充**（`data/products.yaml` 的 buy_url/listed、`content/about.md` 真实简历、socialIcons 真实邮箱、删脚手架文章）：卡用户材料，不随图（候选 5/6 先例）。
- **后端重启时的产品数据源替换**：ADR-0006 已定，届时只动 `product-items.html` 一处。
- **菜单 `parent` 子项渲染**（4 个 categories 子项配置了不渲染）：独立新需求，不属精选机制。

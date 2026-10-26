---
id: map-featured-type-guard
title: 精选类型守卫图（候选 2）
labels: [wayfinder:map]
status: closed
created: 2026-10-25
closed: 2026-10-26
---

# 精选类型守卫图（候选 2）

## Destination

把 featured 类型守卫从现状深化为**单一模块**，使该模块可测试、AI 可导航。现状 = 三处拷贝各持一份「`isset` + 非 bool → `errorf`」（`layouts/partials/post-items.html` / `layouts/partials/product-items.html` / `content/posts/_content.gotmpl`）+ 谓词三种形态（`where`×2 + `eq`×1）。目的地 = 契约定义处唯一、测试缝唯一、导航入口唯一。到「way 清晰、无待决策项」即收口；不重开已锁 ADR；本图只产决策，施工经项目负责人指示后展开。

## Notes

- **出处**：架构评审候选②（improve-codebase-architecture，2026-10-25；报告在 OS 临时目录属 epoch 性资产——关键锚点已抄写进本图与工单正文，不依赖该文件存活）。harness 图（`map-test-harness-convergence.md`）Out of scope 条已把「featured 类型守卫」记为独立目的地——本图是其展开；候选①（harness）已由 ADR-0014 收口。
- **工单纪律（项目负责人开图时明确，2026-10-25）**：每张工单是**待决策问题**、不是施工任务；一次会话最多解决一张（research 除外）；地图是索引不是仓库，决策只存在于工单。
- **例外记录（2026-10-26）**：经项目负责人指示，0074 / 0075 / 0076 / 0077 四票同场 grill 并同场闭环（「一会话一票」纪律的例外）；每票仍一次一问、推荐先行、事实自查后问决策。0073 亦为「决议先落、同场进入施工」。
- **收口（2026-10-26）**：**7/7 票 closed（0072–0078；含 1 张 research 事实票）**，frontier 空 = 目的地到达；决策集耐久化于 **ADR-0015**（15 条决策各注工单号），ADR-0009 / ADR-0012 各加指针行；收口 handoff 见 `docs/handoffs/2026-10-26-featured-guard-closure.md`；backlog 不追加条目（候选②非 backlog 来源，与候选①先例一致）。
- **现状事实锚点（排图日自查，已由 0072 研究工单确认）**：守卫三份拷贝——`layouts/partials/post-items.html:38-44`（前缀「文章精选数据：」，遍历全部文章）、`layouts/partials/product-items.html:36-42`（前缀「产品索引数据：」，遍历产品）、`content/posts/_content.gotmpl:62-71`（前缀「SOP 发布管线：」，注册条目，条件传键避 dict nil 陷阱）；谓词三形态——`where $pages "Params.featured" true`（post-items）、`where $items "featured" true`（product-items）、`eq .Params.featured true`（主题层 `featured-badge.html`，docstring 自称与守卫「同源」）；坏值测试覆盖——文章两例（`content-posts-bad` 字符串 / `content-posts-bad-int` 整数，期望子串「文章精选数据：」）、产品一例（`bad/products/featured-not-bool`）、**SOP 侧零 fixture**（排图日自查：`bad/sop/` 下六个用例无 featured 坏例）。
- **闭卷 ADR**：0009（字段契约：未声明 = 非精选、只认布尔 `true`、非 bool 即 errorf；产品侧补同款校验是「执行已声明类型」非重开；真实精选清单不锚）、0012（徽标三面 + `featured-badge.html` 单一实现；谓词与守卫同源但分开实现；坏值执法继承 post-items 全局循环、徽标面无需新执法点；theme→site 调用曾被否决）、0006（产品侧 featured 过滤语义与缺省值）、0010（搜索索引不投影 featured）、0008（分层判据）、0007（三层文档契约模式）、0014（harness 自测先于契约红的先例）。
- **纳入判据先例**（0061 所有权测试）：机制在全部消费方中应只有一个所有者 → 基建收敛；各有其主 → 契约独立；平分判契约。本图对象（守卫执法机制）倾向收敛，但最终边界归 0073 质询，排图期不预设。
- **测试总原则**：Hugo 无模板单测，静态产物只能 build-then-assert；fixture 基建单份（不新开第四套构建）；fixture 日期一律过去日（未来内容不发布 → 假绿）；Hugo 0.164 语义编写（CI 钉版，0.166+ 条件多 return 本地过、CI 红）。
- 用户是项目负责人：HITL 工单必须实时对话解决，agent 不得自答；事实自己查，决策问用户；一次一问，先给推荐答案。
- 术语以根目录 `CONTEXT.md` 为准；「精选 (Featured)」条已两轮扩写（0009/0012），本图可能再扩（措辞归收口工单 0078）。
- 环境注意（历图传承）：本 shell 的 grep 对 `\|` 交替失效，内容搜索用 Grep 工具；safe-delete 每轮删除预算 5000。

## Decisions so far

<!-- 索引：每个已决工单一行 gist + 链接；决策详情只存在于工单，此处不重述。 -->

- [featured 类型守卫现状事实底座（盘点）](tickets/0072-featured-guard-facts.md) — 守卫四件套（isset + %T + ne bool + errorf）三处**逐字同构**，差异仅在数据访问路径、遍历模式与消息前缀；谓词三形态各有真实差异（无条件 where / 条件 where / 单页 eq）；坏值覆盖文章 2 例 + 产品 1 例，**SOP 侧零 fixture 零钉子串**；`.Params` 键小写化（官方声明）vs 数据 map 键原样，本仓三源全小写故当前不可观测；partial 可 return / 可 errorf、查找序站点层优先，站点→主题调用有先例、**theme→site 零先例**。缺口 8 条（SOP 坏例 / SOP 消息钉子 / 徽标坏值无直接断言 / where 行为差异无守门 / 键大小写 / 遍历形态 / dict nil 陷阱 / 徽标跨层归属）。
- [守卫单模块的职责边界：只做类型校验，还是校验与谓词合一](tickets/0073-guard-module-scope-boundary.md) — **谓词判契约（各有其主：ADR-0009 精选链 / ADR-0006 条件过滤 / ADR-0012 渲染判定）、边界 (a) 只做类型校验**（合并 = 为三种真实差异参数化，0061 枪毙的「搬家」）；文档 = **双向互指**（模块 docstring 为执行契约唯一定义处，badge 与两处数据准备各留指针）；边界文本 = **校验器不是选择器/取数器**（不拥有取数/选择/渲染/消息措辞；遍历归 0074）；测试 = **零增减零改写**（三断言原样存活、模块无专属断言、SOP 缺口留 0077；验收含变异等价）。连锁：0075 张力消解（降级确认票）、雾区「谓词合一开销」负向了结、0074 收窄。→ **ADR-0015 决策 1–4**。
- [守卫模块的形态与接口：入参形态、未声明归属、返回语义](tickets/0074-guard-module-interface-form.md) — **条目语义**（调用方传容器、四件套全收敛、遍历留调用方）；**不自校验**（内部模板接口、三处字面量，docstring 声明必填）；**无返回**（纯执法）。与已落地实现一致，零代码改动。→ **ADR-0015 决策 5–7**。
- [守卫模块的落点与分层：站点层还是主题层](tickets/0075-guard-module-layer-placement.md) — **站点层**（ADR-0008 判据；三消费方全站点层；徽标不消费 → 零 theme→site 新先例，主题层保持自洽）；**记重开触发**（徽标谓词收敛或主题层消费方 → 重开分层决策；ADR-0012 的否决是上下文特定的）。docstring 已落。→ **ADR-0015 决策 8–9**。
- [守卫的错误消息与命名契约：三前缀统一还是参数化](tickets/0076-guard-message-and-naming-contract.md) — **保留 origin 三前缀**（逐字、测试零 churn、链身份不丢）；**label 归调用方格式化**（定位值不是措辞，「条目」留在 SOP 链）；**`featured-guard.html`** 定案、术语表不收「守卫」词条、CONTEXT.md 精选条加 guard 指针。零代码改动（指针已落）。→ **ADR-0015 决策 10–12**。
- [守卫模块的测试缝：单模块如何被 build-then-assert](tickets/0077-guard-test-seam.md) — **各消费链**（测公开行为，不建模块探针）；**补 SOP 坏值 fixture**（`bad/sop/sop-featured-not-bool` + BAD_CASE_EXPECT 钉 origin+label+契约，套件 104→105）；**ADR-0014 自测模式不适用**（模板侧无等价 seam，记已知差异）。红绿：fixture 先红（缺期望）→ 期望转绿；变异 → 四条坏值断言同红（site 156/159 + sop 104/105）。→ **ADR-0015 决策 13–15**。

## Not yet specified

<!-- 雾区：在目的地内、但还无法精确表述的问题。随 frontier 推进毕业为工单。 -->

- **已消解（负向）**（[0073](tickets/0073-guard-module-scope-boundary.md) 决议）：「谓词与守卫合一后的构建期开销面」——谓词判契约、不合并，开销面不存在。
- **已消解**（[0074](tickets/0074-guard-module-interface-form.md) 决议）：「Page.Params 键小写化 vs 数据 map 键原样的接口影响」——接口取 item 容器 + 键名固定 `"featured"`，三源全小写书写 → 差异不构成问题面；未来出现大写键源按新数据源重评。
- **已消解**（[0074](tickets/0074-guard-module-interface-form.md) 决议）：「第四类 featured 数据源出现时的接口扩展性」——条目语义对第四源天然开放（传容器即可），无需预留扩展位。

## Out of scope

- **重开已锁 ADR**（0009 字段契约 / 首页行为 / seam 形状 / 测试缝 / 派生文归属；0012 徽标三面 / 数据条负向 / 分类·标签页负向 / meta 负向；0006 产品侧语义；0010 搜索不投影）：认为错了先提重审（工程纪律 2），不随本图默认推翻。
- **精选的选择 / 截断 / 补集等首页编排语义**：归 `post-items.html` seam 本身（ADR-0009 锁），本图只动守卫执法，不动编排。
- **徽标视觉值**（CSS 调值）：视觉层先例；本图只定语义契约与 DOM 契约。
- **架构评审候选③④⑤⑥**（文章卡片单模块 / 注册缝下沉 / 配置·CSS 死面批处理 / CSS 影子契约 parity）：各自独立目的地，不随本图合并或顺带。
- **新消费面**（数据条 / term 页 / meta 已负向；任何新增 featured 消费面）：新需求，新目的地。
- **施工批次与 CI 验证节奏**：本图只到「可施工状态」，施工经项目负责人指示后展开（候选 7/12/13 先例）。

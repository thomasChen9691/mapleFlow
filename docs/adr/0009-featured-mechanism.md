# 0009 - 精选机制：文章侧 featured、首页真精选与跨类契约统一

**状态**：已批准（2026-10-22）。决策过程见 wayfinder 地图「精选机制图（候选 7）」（docs/wayfinder/map-featured-mechanism.md，工单 0035-0041 全 closed，其中 0035 为事实盘点）；本 ADR 是决策的耐久化记录——AGENTS.md §8.1 的阅读路由（CONTEXT.md + docs/adr/）不含 wayfinder 目录，决策必须活在 docs/adr/。基线见 ADR-0006（产品索引双 seam）、ADR-0005（SOP 发布管线）、ADR-0008（主题 fork 与分层契约）。

## 背景

精选机制原为产品侧独有（`data/products.yaml` 的 `featured` 字段 + ADR-0006 的过滤语义）；文章侧首页「精选文章」区实为 `first 3 ($pages.ByDate.Reverse)`——按日期取最新，与 featured 无关，且与同页「最近更新」网格同源，前 3 篇必然重复展示。候选 7 的目的地：把精选机制做成可测试、AI 可导航的模块（工单 0035 事实底座）。

## 决策

1. **字段契约（0036）**：文章 front matter 顶层 `featured`（与 `data/products.yaml` 同名同义）。**未声明 = 非精选；只认布尔 `true`**——实测 `where "Params.featured" true` 对字符串 `"true"`/`"false"`、`yes`、整数 `1` 全部不匹配（静默排除），而 `if .Params.featured` 会把字符串 `"false"` 当真值（错误入选），故 `if` 写法禁用。**字段存在但非布尔 → errorf 构建失败**（项目惯例：契约失败而非兜底；ADR-0006 负数 errorf 先例）。`archetypes/default.md` 不加字段，只加注释。**产品侧补同款类型校验**——ADR-0006 锁定了过滤语义与缺省值，从未定义坏值行为，补校验是执行已声明的类型，非重开。
2. **首页行为（0037）**：精选区**固定 3 条**（调用点字面量，不新增 `hugo.toml` 参数——AGENTS 参数纪律），集内**日期倒序**（不引入 `weight` 手工序）。**精选从「最近更新」网格剔除**（现状同页重复是真实缺陷）；精选区与网格在各自集合为空时**整块不渲染**（0 篇 featured 不写空态文案；全部入选则网格隐藏）。标题保持「精选文章」。
3. **架构落点（0038）**：**单 seam 返回 `{featured, rest, all}` 三片，渲染不抽**。数据准备 partial 是首页精选链**唯一**读 `site.RegularPages` 并做 featured 判定/截断/补集处；入参**只收 `limit`**（数据源固定，不留 `source` 注入位、不留 `featured` 开关——ADR-0006 决策 2 适用）；落**站点层**（首页编排属内容策略）。`all` 片供首页数据条计数，避免首页为计数再写一遍 `where`。**补集必须对「实际显示的精选」求**（`complement $featured $pages`），不是对全部 featured 求——后者会把被 limit 截断的文章从首页彻底抹掉（静默丢内容）。真实精选清单**不锚**断言（内容由项目负责人掌控）。
4. **测试缝（0039）**：**新增独立 fixture 构建**（第三个配置只覆盖 `contentDir`），不动既有 fixture 的构建环境；必锚四条：过滤+缺省、截断（第 4 篇不上）、**两片互斥且并集全量**、空态+坏值 errorf（字符串与整数各一例）；另锚「全部入选 → 网格隐藏」。落点**并入并改名** `tests/assert_site_contracts.py`（0032 记账的命名债触发：产品状态/产品索引/主题契约/reveal 产物/精选五类职责），**改名搭施工批次的车**（活引用 12 处 + 历史引用约 25 处，后者按「ADR 是历史记录」不改，AGENTS 留旧名指针）。每条断言变异检验。
5. **派生文归属（0040）**：**SOP 派生文参与精选**（不参与则池只剩 4 篇手写，精选退化为「手写全集」）。`data/sop.yaml` 加可选 `featured`；`_content.gotmpl` **条件传键**——实测 `dict "featured" .featured` 在字段缺失时产出 `isset=true` + 类型 `nil`，盲传会让第 1 条的非布尔 errorf 对每条未标条目误报。**SOP 契约四类 → 五类**。首标 3 篇手写文章（`sop-ops-tools-index` / `k8s-common-commands` / `aiops-state-and-tools`）；派生文路径由 fixture 透传断言覆盖，不靠改真实内容凑测试。

## Considered Options

- **首页内联不拆 seam**：谓词与补集分散在模板，未来列表页复用即第二处实现；且无 docstring 契约可导航——排除。
- **照搬产品侧双 seam（post-items + post-index）**：文章区只有一种渲染形态，纯渲染 seam 无第二消费点，且要处理「编号行 vs 卡片」两种模式——排除（0030/0006 收敛过的病）。
- **补集用 `where "Params.featured" "!=" true`**：被截断的 featured 文章在首页彻底消失，无任何报错——施工期被「两片互斥无遗漏」断言当场抓住，排除。
- **精选用手工序（`weight` 字段）**：3 条规模的收益不抵第二个字段的组合语义成本——排除。
- **条数可配（`hugo.toml` 参数）**：无真实需求，且违反参数纪律——排除。
- **派生文不参与精选**：池太小、精选退化为分类，且今天占着 2/3 精选位的派生文会突然消失——排除。
- **不动产品侧坏值校验**：同一字段名在两类内容里行为不同，未来必踩——排除。

## Consequences

- 改精选 = 改 `layouts/partials/post-items.html`（谓词/截断/补集）+ `layouts/index.html` 调用点；改 SOP 精选 = 改 `data/sop.yaml`。契约定义处：seam 文件头 docstring（0038）+ `_content.gotmpl` 头注（0040）+ `CONTEXT.md`「精选」条（概念级）。
- **ADR-0006 加指针行**：其 featured 语义已被本 ADR 扩展（非布尔即 errorf、跨类同名同义）。
- **ADR-0005 的指针已在施工期以补记形式落**（契约四类 → 五类），本 ADR 不加第二处。
- 命名债已还：`tests/assert_site_contracts.py` 管五类站点契约；历史文档中的旧名由 AGENTS.md §3 指针解释。
- 施工期踩坑（已入工单 Resolution 与 AGENTS 坑点 11）：Hugo 默认**不发布未来日期的内容**，fixture 写未来日期会让文章整篇消失并表现为「区块不渲染」的假绿；判定网格隐藏须锚 `class=mf-posts`/`entry-link`，不能用「最近更新」文案子串（首页数据条有同名标签）。
- **边界**：搜索索引（`index.json`）是否投影 featured 归候选 8；「精选」徽标在内容层的呈现、首页数据条是否区分精选、分类页是否消费精选留在地图雾区，未决。
- 本图只到「可施工状态」+ 同场施工完成；push 与 CI 验证由项目负责人决定节奏。

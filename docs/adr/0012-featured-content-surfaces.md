# 0012 - 精选机制的内容层外溢：徽标三面、两条负向边界与 seam 收紧

**状态**：已批准（2026-10-23）。决策过程见 wayfinder 地图「精选雾区图（候选 13）」（docs/wayfinder/map-featured-fog-zones.md，工单 0055-0060 全 closed，其中 0055 为事实盘点）；本 ADR 是决策的耐久化记录——AGENTS.md §8.1 的阅读路由（CONTEXT.md + docs/adr/）不含 wayfinder 目录，决策必须活在 docs/adr/（ADR-0004 立过的规矩）。基线见 ADR-0009（精选机制——本 ADR 的所有输入）、ADR-0006（产品索引）、ADR-0008（主题 fork 分层判据）、ADR-0010（搜索契约——「无消费方不投影」先例）。

## 背景

ADR-0009 把文章侧 featured 做成首页精选块后，在 Consequences 边界条留了三条雾区未决：①「精选」徽标在内容层的呈现；② 首页数据条是否区分精选；③ 分类页 / 标签页是否消费精选。候选 13 的目的地：把精选机制从现状深化到这三面，使该模块可测试、AI 可导航。排图 2026-10-23：事实底座工单 0055（research/0055，缺口 8 条）+ 项目负责人质询七问全决。

## 决策

1. **语义边界（质询 Q1）**：精选 = **分层默认**——首页编排概念为主（ADR-0009 语义不外溢自动生效），外溢面逐面举证、默认不做，举证责任在「做」方。
2. **精选标识进入内容层（0056，正向）**：**做，三面**——文章页（主题层 `single.html`）+ 列表卡片（分类 / 标签 / `/posts/`，主题层 `list.html`）+ 首页网格卡片（站点层 `index.html`）；**首页精选行不加**（区块标题「精选文章」已表达，行内徽标冗余）。契约落点 = **主题层新 partial `themes/maplemod/layouts/partials/featured-badge.html`**，文件头 docstring 为契约定义处（class / title 文案 / 谓词语义 / 调用面清单），三处调用、**单一标记实现**（否决三处内联拷贝——第二实现风险）。谓词 `eq .Params.featured true`（只认布尔 true）；**坏值执法继承 `post-items.html:32-38` 的全局 errorf 循环**（该循环遍历全部文章，非布尔 featured 在首页构建时即失败——徽标面无需新执法点）。测试 = **fixture 三面全锚**（挂 contentDir fixture 构建：single 产物 / term+posts 列表产物 / 首页网格产物——被 limit 截断回落到网格的 feat-a 是天然样本），**真实构建不锚**（ADR-0009「真实精选清单不锚」原则），**变异检验强制**。
3. **首页数据条不区分精选（0057，负向）**：数据条（站点层 `index.html` 的 `mf-spec`）维持站点总量口径，不加「精选 N 篇」、不改造合并口径。理由：抽象层不分层（总量 vs 编排）、信息冗余（all 片已含精选且精选文章区就在数据条下方）、断言经济学（现有三项已无断言，不给第四个冗余数字纳税）。重开触发 = featured 规模远超首页展示的 3 条且网格因分页无法完整表达。
4. **分类 / 标签页不消费精选（0058，负向）+ seam 边界收紧**：分类页 / 标签页 / `/posts/`（同走主题层 `list.html`）**维持日期倒序**，不 featured 优先——term 页访问意图是「找该分类下的新文章」、置顶 3 篇挤压新文章曝光、断言面从零建且期望值要耦合 Hugo 默认排序链（weight→date→LinkTitle→filepath）。边界守门 = **`post-items.html` docstring 收紧硬边界措辞**（只服务首页精选链；其他页面 / 模板不得调用本 partial 做 featured 判定或取数）+ AGENTS.md 坑点 11 同步；**否掉产物断言守牙**（断言 term 页日期序 = 把 Hugo 默认排序链现状锁进测试，主题未来正当改排序会误红；且该失败模式必须过决策，不可能无意发生）。
5. **meta 层不投影精选（0060，负向）**：`schema_json.html`（BlogPosting JSON-LD）/ `opengraph.html` / `twitter_cards.html` 不投影精选状态。ADR-0010 决策 4 同款纪律——**无消费方不投影**；schema.org 无 featured 概念、og 协议无 `article:featured` 类标准属性，自造非标准字段没有第二个读者；徽标服务「落在页面上的眼睛」、meta 服务「抓取与分享的机器」，两层无强制同步。

## Considered Options

- **全站内容属性（Q1 否）**：featured 外溢到所有面——与 ADR-0009 已锁的首页锚定语义冲突，且每个新面都要重新决定消费形态，决策面失控。
- **严格首页-only（Q1 否）**：三面一刀切锁死——把徽标面的真实信号缺口（访客从文章页 / 列表页落地时无任何精选信号）一起牺牲。
- **徽标三处内联（0056 否）**：复刻 Draft `entry-hint` 先例——class / 谓词三处拷贝，任一处漂移无断言可捕（第二实现风险；本项目对重复实现的过敏有 ADR-0004 先例）。
- **徽标放站点层 partial（0056 否）**：theme→site 调用是全仓新先例（分层反转，主题基线不再自洽），且徽标归呈现行为、按 ADR-0008 判据属主题层。
- **首页精选行加徽标（0056 否）**：区块标题「精选文章」已表达，行内徽标冗余。
- **真实构建锚徽标断言（0056 否）**：违反 ADR-0009「真实精选清单不锚」原则（真实 featured 由项目负责人掌控，改标记即测试红）。
- **数据条加「精选 N 篇」独立项 / 合并口径（0057 否）**：见决策 3 三项理由；合并口径还要动 `parse_spec_count` 的 label 定位。
- **term 页 featured 优先 / term+posts 全做（0058 否）**：见决策 4；外部惯例（research 第 6 项：sticky 与「最新在前」心智冲突）与 ADR-0009 拒绝 `weight` 手工序的先例同向。
- **产物断言守 term 页负向边界（0058 否）**：把 Hugo 默认排序链的现状锁进测试，主题正当改排序误红；docstring 硬边界是 proportionate 的守门（契约定义处记事）。
- **meta 投影精选：schema 自定义属性 / og 自定义标签（0060 否）**：均无消费方、无标准字段，ADR-0010 决策 4 同款负向。

## Consequences

- 改徽标 = 改 `themes/maplemod/layouts/partials/featured-badge.html`（契约 docstring）+ 三处调用点（主题层 `single.html` / `list.html` / 站点层 `index.html` 网格）；徽标谓词 `eq .Params.featured true`，不得在各模板内联拷贝。
- **ADR-0009 加指针行**（其 Consequences 边界条的三条雾区由本 ADR 定案；正文不改，历史记录）。
- 术语：`CONTEXT.md`「精选 (Featured)」条扩一句（三面呈现 + `featured-badge.html` 指针）；导航：`AGENTS.md` 坑点 11 补四条纪律（seam 只服务首页 / 坏值执法全局托管 / 徽标唯一实现处 / 两条负向边界）+ §7 速查表加 `featured-badge.html` 行。
- **施工批（待项目负责人指示）**：`featured-badge.html` partial + 三处调用 + fixture 三面断言（挂 `tests/assert_site_contracts.py` 文章精选类）+ 变异检验；**视觉值（颜色 / 字号 / 图标）归视觉层，不在本 ADR**。`post-items.html` docstring 收紧随本 ADR 收口批已落地。
- 边界：数据条 / 分类·标签页 / meta 层三条负向随本 ADR 耐久化，重开触发条件见各决策条；精选的跨类契约（文章 + 产品同名同义）不变（ADR-0009）。

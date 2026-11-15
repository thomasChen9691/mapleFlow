---
id: map-search-overlay-v2
title: 搜索浮层 v2 图
labels: [wayfinder:map]
status: closed
created: 2026-11-15
closed: 2026-11-15
---

# 搜索浮层 v2 图

## Destination

把架构从现状深化到**搜索浮层 v2**，使该模块**可测试、AI 可导航**：决策集完备、契约定义处唯一、测试缝可执行、导航可读。到达判据 = frontier 空、决策耐久化于 ADR、地图 closed 且达到「可施工状态」。**施工本身不属本图**——按 wayfinder 默认「只产决策」，工单一律是待决策问题、不是施工任务。

## Notes

- **出处与触发条件（2026-11-15 开图）**：项目负责人给定 Destination 后开图。继承三处：① `map-search-entry.md` 收口时挂起的三条雾区（移动端 / 小屏入口形态、aria 契约细节、浮层首屏空间关系），其触发条件「将来出现浮层形态」已由 **ADR-0013** 兑现；② ADR-0013 诚实入档的两条 v1 不做（ArrowUp/Down 选结果、命中高亮）与 fastsearch docstring 过时指针；③ 2026-10-24 CI/CD 重建 + 视觉批 E/F 已落的触屏入口、iOS 双机制滚锁、inert 分支与进出场过场。挂起雾区**由本图从注记继承，勿从 closed 地图直接复工单**。
- **边界（开图时与项目负责人钉死）**：本图只深化搜索浮层模块本身。不重写 fastsearch、不替换检索实现、不改投影六字段、不做视觉 / CSS 调值、不做内容填充、不重开已锁 ADR、不往任何已 closed 地图加票。
- **工单纪律（项目负责人开图时明确）**：每张工单是**待决策问题**、不是施工任务，粒度控制在一次会话能解决；一次会话最多解决一张（research 除外）；**地图是索引不是仓库，决策只存在于工单**；HITL 工单必须实时对话解决，agent 不得自答；事实自己查，决策问用户，一次一问、先给推荐答案。
- **不含施工**：决策收口后经项目负责人指示另开施工批；施工序列、验证基线、ADR / 术语 / 导航同步的交接安排归「收口」票，不在本图执行。
- **闭卷 ADR**：0002（no-js 渐进增强基线）、0007（reveal 边界、DOM 契约定义处 = 引擎 docstring）、0008（主题层 / 站点层分层判据）、0010（搜索契约：六字段冻结、fastsearch 现状快照、不重写与两个重评触发条件、改投影字段三处同步）、0011（搜索入口：三协议并列、所有权分层原则、无第四套 config）、0013（搜索浮层：形态、模块边界、fuse parity、容错 UX、a11y、no-js、两条已知限制）、0014（harness 自测与 fixture 基建单份）、0016（注册缝唯一与 CSS parity 门边界）。
- **术语**：以根目录 `CONTEXT.md` 为准（「搜索入口」「搜索浮层」「搜索索引」已有词条）；是否新增 / 扩写词条归收口票，排图期不预设用词。
- **测试总原则**：Hugo 无模板单测 → build-then-assert；行为断言走 `npm test`（jsdom，手写样本镜像 docstring DOM 契约、不用构建产物）；fixture 基建单份、不新开第四套 config；每条断言以变异检验证牙；CI 钉 Hugo 0.164 语义，本机 0.167 的 skew 只有 advisory WARN（不是失败）。
- **环境注意（历图传承）**：shell 的 grep 对 `\|` 交替静默失效 → 内容搜索一律用 Grep 工具并双向复核；`gh` 未安装，查 CI 用 curl + GitHub API（runs / jobs 匿名可读，logs 需管理员 token）；safe-delete 每轮预算 5000；单命令约第 6 个 node 进程会被 kill。
- **建议 skill**：realeng-grilling（HITL 决策，一次一问）、realeng-domain-modeling（术语对齐）、realeng-tdd（新契约与新测试同时出生）、realeng-code-review（收口双轴评审）、realeng-handoff（会话收尾压缩交接）。
- **改动纪律**：`AGENTS.md` §2 单人直推（改 → 本地四道门 → commit → push origin main）；ADR 是历史记录、正文不改只加指针行；已被 ADR 记录的决策禁止重新推导（§8.2），认为错先提重审。
- **闭图判据（收口票决议 6，2026-11-15）**：决策完备即 closed —— frontier 空 + 六票 Resolution 落档 + 本索引六行 = 目的地到达；ADR-0017 / 指针行 / CONTEXT / AGENTS / handoff 属**收口批施工**，经项目负责人指示后另开一笔，**不进闭图条件**。本图始终不含施工。

## Decisions so far

<!-- 索引：每个已决工单一行 gist + 链接；决策详情只存在于工单，此处不重述。 -->

- [搜索浮层 v2 现状事实底座（盘点）](tickets/0089-search-overlay-v2-facts.md) — 契约定义处 = 浮层引擎 docstring；fastsearch docstring 两句指针过时（ADR-0013 决策 1 冻结）、index.json 未记第二消费方；MFO-1..19 + 产物断言覆盖主要面，渲染正确性只有弱断言与一次性验证；ADR-0013 两条 v1 不做、候选 12 三条挂起雾区中①②部分兑现③未触及；E/F 六面已落；浮层与 search 页容错不对称；`isOpen` 返回形状文档-实现不一致且零断言。**缺口 13 条**见 [研究产物](research/0089-search-overlay-v2-facts.md)。

- [可测试性的判据与测试缝归属](tickets/0090-testability-criteria-and-seam.md) — **分层判据**：引擎条款级可定位地红 / 主题骨架只走产物断言 / legacy 弱断言 + 一次性验证；不新增第四套 config、parity 边界不变；`isOpen` 删文档对齐实现 + 补返回形状断言。
- [方向键导航与命中高亮的取舍](tickets/0091-keyboard-nav-and-highlight.md) — **只补方向键**（ArrowUp/Down + 选中态 aria，配新行为断言）；命中高亮不做、负向边界 + 重开触发条件；fuse parity 四元组不动；浮层与 search 页键盘行为允许不同。
- [移动端与小屏的 a11y 契约](tickets/0092-mobile-a11y-contract.md) — 三雾区毕业：① 触屏已兑现只补断言、② aria 扩写进引擎 docstring（引擎写触发器 `aria-expanded`、不加主题层脚本）、③ 小屏空间判视觉层 Out of scope。
- [索引失败态与 search 页的关系](tickets/0093-index-failure-and-search-page.md) — **不统一**，不对称固化为负向边界 + 0010/0013 指针行；不自动重试、失败不缓存；错误文案去掉「前往搜索页」、继续硬编码中文；fastsearch 一字不改。
- [收口：ADR 切分、术语、导航与交接](tickets/0094-closure-adr-terminology-navigation.md) — 一份 **ADR-0017** + 0010/0011/0013 三笔指针 + CONTEXT 只扩写既有词条 + AGENTS §7 / 坑点 14·18；**决策完备即 closed**，资产落档属收口批施工；README 计数归清理批。本题关闭 = 目的地到达。

## Not yet specified

<!-- 雾区：在目的地内、但还无法精确表述的问题。随 frontier 推进毕业为工单；不预切成票。 -->

**收口挂起注记（2026-11-15，[收口：ADR 切分、术语、导航与交接](tickets/0094-closure-adr-terminology-navigation.md) 决议 7）**：本图收口时前沿已空（六票全 closed、目的地到达）。「AI 可导航」判据已由 [可测试性的判据与测试缝归属](tickets/0090-testability-criteria-and-seam.md) 消解并从本段删除；以下三条随 closed 地图**诚实保存、不进 backlog、不宣布 Out of scope**（触发条件可能出现），将来触发时由新图从本注记继承，**勿从 closed 地图直接复工单**。

- **动效语义的叠加边界**：浮层过场、阅读进度条、滚动进场三者在 `prefers-reduced-motion` 下是否要统一判定；ADR-0007 与 ADR-0013 各自只写了自己的边界，交界处模糊。触发条件 = 出现实际冲突或用户反馈。
- **结果规模增长后的形态**：索引当前 17 条，浮层是否需要分组 / 排序 / 截断 / 空态细分；阈值与触发条件都不明，待事实底座给出规模与渲染成本后再看。
- **第三个搜索面出现时的共享 seam**：首页常驻框 / 命令面板之类若将来重开，浮层与它的共享装配形态；目前没有对象可精确提问。

## Out of scope

- **重开已锁 ADR**（0002 / 0007 / 0008 / 0010 / 0011 / 0013 / 0014 / 0016）：认为错了先提重审，不随本图默认推翻（工程纪律 §8.2）。
- **重写 fastsearch 引擎 / 替换检索实现**（pagefind、Algolia 等）：ADR-0010 已定不重写，ADR-0013 决策 1 明确 fastsearch 一字不改。本图只审视「两个加载面的容错语义要不要统一」这一**决策**，不在图内施工改写该文件。
- **改投影字段 / 新增字段**：ADR-0010 决策 2 六字段冻结；改字段 = 三处同步，属另一目的地。
- **视觉 / CSS 调值**（配色、断点数值、过场时长、空间像素值）：视觉层，历图先例均排除。
- **施工本身与验证执行**：本图只产决策；施工批次经项目负责人指示后另开，验证基线写进交接。
- **内容填充**（`data/products.yaml` 的 buy_url / listed、`content/about.md` 真实简历、`hugo.toml` 的 socialIcons 邮箱）：卡用户材料，不随图、不排期。
- **清理批与无关议题**：`hugo.toml` 注释遗留键、文档计数失实、`style/css-modern-batch` 遗留分支、Hugo 版本 skew 收敛——均属另一目的地。

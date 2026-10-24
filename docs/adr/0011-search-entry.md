# 0011 - 搜索入口：全站快捷键、摘要渲染与三协议并列

**状态**：已批准（2026-10-23）。决策过程见 wayfinder 地图「搜索入口图（候选 12）」（docs/wayfinder/map-search-entry.md；工单 0049-0054 全 closed，0049 为事实底座 research/0049-search-entry-facts.md）；本 ADR 是决策的耐久化记录——AGENTS.md §8.1 的阅读路由（CONTEXT.md + docs/adr/）不含 wayfinder 目录，决策必须活在 docs/adr/（ADR-0004 立过的规矩）。基线见 ADR-0002（no-js 渐进增强）、ADR-0007（reveal 协议）、ADR-0008（主题 fork 分层）、ADR-0010（搜索契约）。

## 背景

候选 8（ADR-0010）把站内搜索治理到「投影 + 检索 + 测试缝」契约完备，其 Consequences 边界条显式让渡一个面：「搜索入口新功能，不属本 ADR」。backlog 第 12 项承接该面；交接文档指出它只剩两个子问题——入口形态 + 渲染层要不要加摘要/标签。开图事实底座 research/0049 盘清八项，最关键的五条：fastsearch 仅 search 页加载且**现状文件不可原样搬全站**（无 `#searchInput` 的页面抛 TypeError）；「Alt + /」不在 fastsearch.js 里、是 header.html 的 accesskey 属性（浏览器实现、零测试）；search 页 focus 靠原生 autofocus；结果 li 只渲染标题+链接；fuse keys 四字段与投影六字段的差集恰为 {tags, categories}（摘要/标签均在投影内，加深渲染不触发三处同步）。

## 决策

1. **入口形态（工单 0050，grilling 九问）**：需求定为 P1——从任意页面发起搜索的步骤成本（现状 2 步：菜单 → search 页）。形态为**全站快捷键单独成立**：键位 `/`（单键、零修饰键歧义、GitHub 式肌肉记忆；焦点在 input/textarea/select/contenteditable 或按着 Ctrl/Meta/Alt 时不拦截）；**轻形态**——按键跳转 `/search.html`（search 页打开即 autofocus，检索体验完整），当前页即 search 页时只聚焦不刷新；`params.searchUrl` 缺失/非字符串时静默不注册，菜单链接兜底（ADR-0002 基线：无内容被隐藏，只是增强）。**重评结论：入口只做跳转/聚焦，与 fastsearch、index.json 零耦合 ⇒ 不构成 ADR-0010 的「第二个消费方」，不触发其「不重写」结论的重评。**
2. **呈现层（工单 0051，grilling 三问）**：场景乙（fuse 命中发生在正文而非标题时，纯标题结果无法区分哪篇真含所求）是真实缺陷、强度中等——本站核心场景（查具体命令/配置片段）正落在此。按低成本半解处理：**只加摘要**（渲染 `item.summary`，200 截断字段，标题行下方一行）；**不加标签**（categories 全站同值、tags 信息与 summary 重叠，区分价值被抵消）；**不做命中高亮**（需消费 fuse matches 区间，违背 ADR-0010「只改渲染层」边界，明确出局）。fastsearch.js docstring 的 li 结构条款由「只渲染标题+链接，不显摘要」改写为「标题+链接+摘要」。
3. **模块边界与契约落位（工单 0052，grilling 两问）**：入口落**站点层**——`assets/js/mf-search-entry.js`（js.Build 入口，`import * as params from '@params'`）+ `assets/js/mf-search-entry-engine.js`（纯引擎，零 Hugo 依赖，行为契约定义处），经 extend_footer 第二个 js.Build（iife + minify + fingerprint + defer）**全站恒加载**——复刻 mf-reveal 模式、零 resources.Get 项目级遮蔽风险（0046 翻车教训）；URL 走构建期注入（search 页 RelPermalink，自动带 /mapleFlow/ 生产子路径）。**三协议并列互指、不合并命名**（ADR-0010 决策 4 同款纪律）：index.json 投影契约 ↔ fastsearch.js 检索契约 ↔ 引擎入口契约，docstring 双向指针；fastsearch.js docstring 明确「入口只路由、检索归本协议；两个搜索相关 JS 面加载条件不同，勿混」。**交互归属问题不成立**：入口是纯功能交互（零动效面），reveal 边界是动效交互（ADR-0007），无对象可归——记录为第三个并列模块。**search 页角色维持现状**：全站唯一完整检索落点。
4. **测试缝（工单 0053，grilling 一问）**：入口行为测试立 `tests/assert_search.mjs`（jsdom、手写样本镜像引擎 docstring、13 条：跳转 / 焦点门控 / 修饰键门控 / 页内聚焦 / params 降级），npm test 双套件串联，node 套件「只测源码不经构建」不变式保住；产物断言挂既有三套构建（入口构件交付面 / 生产子路径 URL / 加载面双向 / 菜单文案），无第四套 config（fixture 基建单份）；0052 零 errorf 故无坏用例。**呈现层只加弱产物断言**（构件含 `item.summary` 渲染引用，正则覆盖点/括号两写法，守契约-代码不漂移），「渲染结果正确」记为已知限制、由记录在案的一次性 jsdom 验证覆盖（驱真实构件 + 真实索引跑完整 fuse 链路，5/5，脚本不提交）。**所有权分层原则**：我们新写的代码（入口引擎）→ 常驻行为测试；我们承诺不重写的遗留引擎（fastsearch，ADR-0010）→ 弱断言 + 一次性验证——不为 legacy 内部机制（XHR 模式 / onload / 模块级捕获）给 CI 征税。

## Considered Options

- **首页常驻框**（0050，拒绝）：解决的是已被排序在后的 P2 不可发现性，且不覆盖文章页的步骤成本——与 P1 不严格对齐。
- **快捷键重形态浮层**（0050，拒绝）：fastsearch 多一个加载页面 = 第二个消费方触发重评 + 引擎改造 + 新交互契约，对 17 条索引买贵了；且 0049 已证现状文件不可原样搬全站。
- **维持现状**（0050，否决）：P1 是真实痛点，菜单 2 步成本在命令检索场景可感知。
- **`Cmd+K` / `Ctrl+K` 键位**（0050，否决）：跨平台双映射 + Chrome（Win/Linux）Ctrl+K 冲突；⌘K 是文档站 / 工具站的产品惯例，非内容站刚需。
- **沿用 accesskey**（0050，否决）：浏览器中介实现、macOS 实为 Ctrl+Option+/、零测试；`/` 的 Firefox quick-find 遮蔽取舍已知并接受（GitHub 同款取舍）。
- **并入 mf-reveal**（0052，否决）：语义污染——reveal 模块边界是动效交互（ADR-0007），入口是纯功能交互。
- **主题层挨着 fastsearch**（0052，否决）：extend_footer 取主题层资产是无先例模式，且未来同名项目级文件即静默遮蔽（0046 翻车教训）；站点层新文件复刻 reveal 模式、根除遮蔽风险（采纳）。
- **body data 属性传 URL**（0050，否决）：动主题层 baseof + 扩全站 DOM 契约面，为传一个值不值。
- **脚本读菜单链接 href**（0050，否决）：行为耦合导航结构，搜索入口搬家即静默失灵且无断言会红；js.Build params 注入（采纳）：构建期配置走构建机制，指纹 bundle 内联使子路径正确性可断言。
- **加标签渲染**（0051，否决）：categories 全站同值（实测 17 条全「运维」）+ tags 信息与 summary 重叠，区分价值被抵消。
- **加命中高亮**（0051，否决）：需消费 fuse matches 区间，违背 ADR-0010「只改渲染层」边界。
- **摘要取 content 320**（0051，否决）：多出的 120 字符在命中点靠后时是噪声，且把结果列表往小预览卡形态推；`summary` 200（采纳）：区分足够、形态克制。
- **为 fastsearch 立 jsdom 行为套件**（0053，否决）：ADR-0010 决策 5 的 harness 成本与 legacy 耦合理由对渲染加深丝毫未变；且 CI 中 npm test 先于 hugo 构建，常驻渲染测试须保持 hugo 无关。
- **渲染逻辑提纯函数再嵌回**（0051，否决）：动引擎结构即滑向重写面；弱产物断言 + 记录在案的一次性验证（采纳）：守最常见漂移、覆盖不到的面诚实入档。

## Consequences

- 从任意页面按 `/` 一步到检索页；菜单「搜索」项 title 提示改 `/`，accesskey 退役。fastsearch.js / index.json / search 页 / search.css / mf-reveal / 首页 layouts 零改动（入口批）；fastsearch.js 仅渲染行与 docstring 改动（呈现批）。
- **指针**：本 ADR 给 ADR-0010 加两笔（重评结论留痕 + 快照扩写说明）、给 ADR-0007 加一笔（入口交互不归 reveal 的边界闭合）、给 ADR-0008 加轻笔（站点层交互引擎实践两例备注）；先前 ADR 正文不改（历史记录，指针行是先例）。
- 术语：CONTEXT.md 新增「搜索入口」条（与「搜索索引」条并列，先路由后索引）；AGENTS.md 落 §3 注释 / §7 速查行 / 坑点 14「搜索入口纪律」（两个 JS 面加载条件不同勿混、params 是 `@params` ESM import 不是全局——旧 fastsearch 裸 `params` 写法是死路径、入口只路由、第二个消费方由加载面双向断言守门、测试所有权分层）。
- 施工期实证（排图时未知）：Hugo `js.Build` params 的注入形态是 **ESM import（`@params`）而非裸全局**（本机 0.167 实证；0.162-0.168 发布日志无 params 相关变更，CI 钉版 0.164 同款）——单文件 seam 因此裂为入口 + 纯引擎两文件（决议意图不变）；`typeof params` 守卫落地为 searchUrl 值守卫（模块恒为对象，语义等价）。
- 施工分两批 + 收口批，均经项目负责人指示展开，每批 TDD 红绿 + 变异检验 + 双轴 code-review 后单独提交（261b17b 入口批 / 3f1aee3 呈现批 / 本收口批）。三套测试（assert_site_contracts.py 87 / npm test 29 / assert_sop_pipeline.py 104）全绿；新断言 10/10 变异捕获。
- **边界**：搜索入口的「第二个消费方」守门是断言级的（加载面双向）；若将来重开浮层/首页框形态（第二个加载面出现），按 ADR-0010 决策 5 既定路径重评，届时以本 ADR 与 ADR-0010 的快照契约为输入。移动端形态 / aria 细节 / 浮层空间关系三条雾区随地图收口挂起（docs/wayfinder/map-search-entry.md），触发条件 = 将来重开对应形态。

---

**2026-10-24 指针（ADR-0013 supersede 决策 1 的形态）**：本 ADR 决策 1 的「轻形态——
按键跳转 /search.html」已被 **ADR-0013 决策 4 supersede**：`/` 的动作为「开浮层」
（env.openSearch 钩子），无浮层时才回落 searchUrl 跳转——原轻形态降级为兜底。
入口引擎的键位 / 修饰键 / 焦点门控与 search 页分支原样保留，契约以该引擎**新 docstring**
为准；决策 2（摘要渲染）/ 3（模块边界：站点层 + 三协议并列）/ 4（测试缝）不受影响，
其中决策 4 的「第二个消费方守门」语义已更新（见 AGENTS 坑点 14）。本 ADR 正文不改。

# 0010 - 搜索契约：投影字段、kind 门禁、检索协议与测试缝

**状态**：已批准（2026-10-22）。决策过程见 wayfinder 地图「搜索契约图（候选 8）」（docs/wayfinder/map-search-contract.md，工单 0042-0048 全 closed，其中 0042 为事实盘点）；本 ADR 是决策的耐久化记录——AGENTS.md §8.1 的阅读路由（CONTEXT.md + docs/adr/）不含 wayfinder 目录，决策必须活在 docs/adr/。基线见 ADR-0006（产品索引双 seam）、ADR-0007（reveal 三层文档契约）、ADR-0008（主题 fork 分层）、ADR-0009（精选机制）。

## 背景

站内搜索在候选 8 开图前由三块互不担保的部分组成：`layouts/_default/index.json` 投影（六字段、三类排除、产品条目直读 `site.Data.products`）、主题层 vendored 的 fastsearch.js（无 docstring、无行为测试、fuseOpts 潜伏死路径）、零散断言（产品 tag、三挂点）。0019 / 0026 / 0008 / 0009 的边界注记把「投影字段 + fastsearch + kind 门禁」deferred 到本图。开图事实底座见 `docs/wayfinder/research/0042-search-contract-facts.md`（十项缺口：summary/content 同源、XHR 失败静默、投影零 errorf、行为测试为零等）。

## 决策

1. **模块边界与 seam 形状（0043）**：投影侧**单文件自足**——index.json 一个文件承载投影逻辑 + jsonify + 契约执法，对照 SOP 管线 `_content.gotmpl` 先例，不拆数据准备 / 薄渲染双 seam（JSON 单一形态下渲染 seam 是空壳）。契约分层沿用 ADR-0007 三层模式：CONTEXT.md 概念术语条 / 文件头 docstring 为唯一定义处 / 测试期望值字面量，不建 spec seam。模块边界**只圈站点层投影**；fastsearch 的治理独立成「搜索协议」（决策 4）；search 页面留 B11 守挂点；交付面（outputs JSON / preload / XHR 路径）写进投影 docstring。**投影守自己消费的字段**：产品 name/summary 必填、缺失即 errorf（前缀「搜索索引数据：」）；listed/price/buy_url/kind 不重验（产品链已有门禁）；页面 / 派生侧不加投影层执法（SOP intro 污染归 ADR-0005）。
2. **字段契约（0044）**：字段集**冻结为六项**（title / permalink / summary / content / tags / categories）；**featured 与 kind 不投影**——无消费方（fastsearch keys 不含、结果 UI 只渲染标题+链接），投影即死字段；精选归首页编排（ADR-0009），kind 门禁归产品索引链。summary/content **同源确认为有意设计**（P2-6「瘦身」初衷：content 是 .Summary 的 320 字符截断而非正文）；truncate 200/320 为调值，仅文档不断言。产品条目形态（title=name / permalink 锚点 / content 三字段拼接）有独立字面量断言。
3. **kind 门禁归属（0045）**：**门禁归产品索引链，索引侧零执法**——索引不消费 kind（决策 2），坏 kind 由「产品页恒渲染全量 → product-items 恒被调用」触发 errorf，与索引是否存在无关；该隐式兜底的牙是 `assert_real` 的产品页全量断言。0019 边界注释改写为结论记录。
4. **协议归属（0046）**：fastsearch 治理为**独立「搜索协议」，现状快照式契约**——docstring 落 `themes/maplemod/assets/js/fastsearch.js` 文件头，收录挂点、`.focus`、li 结构、键盘语义、XHR 路径与失败行为；**不并入 reveal**（reveal 语义是动效交互，搜索是检索交互）、**不与投影合并命名**（CONTEXT.md 一词条两指针互指）。**fuseOpts 参数位删除**——无消费方的预留位不留；默认值（threshold 0.4 / distance 100 / ignoreLocation true / keys 四字段）升格为契约，调参 = 改代码 + 改契约 + 评审。容错行为（XHR / JSON.parse 静默失效等）记录为已知限制，不承诺修复。**施工期定案**：项目级 `assets/js/fastsearch.js` 覆盖（子模块时代遗产；Hugo `resources.Get` 项目级优先，故其为活文件、主题层副本是死的）的 XHR 修正合并入主题层后删除，单副本由守门断言执法；head.html preload 路径同批修正。
5. **测试缝（0047）**：**不立 jsdom 行为套件**——fastsearch 是无导出经典脚本（顶层 DOM 捕获 + window.onload），harness 要 stub XHR + 加载 fuse UMD + 手动触发 onload（约 100 行一次性成本），测的是遗留行为快照；重写时新引擎按 mf-reveal 模式抽 ESM 可测模块，测试与新契约一起 TDD 出生。**产物断言盖上交付面**：search 页引用 `search.*.js` + 构件落盘 + fetch 同目录 `index.json`（锚 fixture 构建）。套件合流 `tests/assert_site_contracts.py`（头注释七类职责），不改名；CI 守门经 deploy.yml 既有步骤，`npm test` 入口不变。

## Considered Options

- **投影拆双 seam**（0043，拒绝）：薄渲染 seam 在 JSON 单一形态下是空壳；坏用例走 `bad/` fixture 机制，不依赖拆 seam。
- **投影 featured / kind**（0044，拒绝）：无消费方即死字段，且打破 keys 差集断言；精选归首页编排（ADR-0009），kind 门禁归产品索引链。
- **索引重复验 kind / 数据源收敛**（0045，拒绝）：验自己不消费的字段是两处执法必然漂移；product-items 返回渲染导向 dict（label/href/disabled），收敛扭曲数据流。
- **搜索交互并入 reveal**（0046，拒绝）：reveal 语义是动效交互；并入即重开 0007 的模块定义。
- **补配置激活 fuseOpts**（0046，拒绝）：为无人要调的面新增配置 surface，且配置与 docstring 两处记录默认值。
- **立 jsdom 行为套件**（0047，拒绝）：为遗留快照陪葬 harness；重写时测试与新契约一起出生。
- **给快照立「搜索协议」术语名**（0048，拒绝）：把现状升格为设计，与「非设计目标」定性冲突；重写发生时新引擎配新词。

## Consequences

- 搜索模块的两个契约定义处：`layouts/_default/index.json` 文件头 docstring（投影）与 `themes/maplemod/assets/js/fastsearch.js` 文件头 docstring（检索）；CONTEXT.md「搜索索引」条一词两指针。**改投影字段 = 三处同步**（投影 docstring / fastsearch keys / 差集断言）；重写 fastsearch 时接口条款锚点随移。
- 搜索的静默失效面全部有牙或已记录：坏产品字段 errorf、keys 对齐断言、交付面产物断言、单副本守门；XHR 静默失效记录为已知限制（重写时处理）。
- 指针：ADR-0006（0019 边界定案）、ADR-0007（搜索 JS 归属闭环）、ADR-0009（索引不投影 featured）各加指针行；三份正文不改（ADR 是历史记录）。
- 施工期踩坑（已入工单 0046 施工期补记）：Hugo `resources.Get` **项目级 assets 优先于主题层**——事实盘点必须查同名覆盖文件；本次「死文件当活文件」翻车即此（B3 断言一度读的是死文件）。
- 边界：重写 fastsearch 时才有的面（结果呈现深化 / 引擎形态 / 容错 UX）与搜索入口新功能，均不属本 ADR（见地图 Out of scope）。

**2026-10-23 指针（重写与否的结论）**：**不重写 fastsearch**。理由是投入产出比：索引仅 17 条记录、引擎单文件、测试依赖只有 jsdom——本 ADR 已把行为快照成契约、把静默失效面记录在案，维护成本本来就低，重写降低的是一个不高的成本。若「结果可读性」成为真实需求，只改渲染层（摘要 / 标签），不动引擎；「引擎 ESM 化 + 容错 UX」长期挂起，触发条件是真被 XHR 静默失败咬到、或出现第二个消费方。届时按决策 5 的既定路径：新引擎与新契约一起 TDD 出生，本 ADR 的快照契约作为输入。本 ADR 正文不改（历史记录）。

**2026-10-23 指针（二）（候选 12 收口）**：本 ADR Consequences 边界条让渡的「搜索入口新功能」已由**候选 12**（ADR-0011）定案并施工。两笔留痕：① 本文件末段指针所列「第二个消费方」触发条件已被正式评估——入口只做跳转 / 聚焦、与 fastsearch 及 index.json 零耦合，**不构成第二个消费方、不触发重评**，「不重写」结论原样成立；② 本 ADR 治理的快照契约（fastsearch.js docstring）已扩写——li 结构条款加摘要渲染（`item.summary`，ADR-0011 决策 2 / 工单 0051），扩写位置与入口互指指针见该文件头。本 ADR 正文不改（历史记录）。

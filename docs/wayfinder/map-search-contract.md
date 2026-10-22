---
id: map-search-contract
title: 搜索契约图（候选 8）
labels: [wayfinder:map]
status: closed
created: 2026-10-22
closed: 2026-10-22
---

# 搜索契约图（候选 8）

## Destination

把站内搜索从「上游遗留代码 + 零散断言」的现状，深化为一个可测试、AI 可导航的契约模块：`index.json` 投影字段契约、kind 门禁归属、fastsearch 的协议归属与 DOM 契约、测试缝与导航收口——达到「可施工状态」即收口。从现状深化，不替换搜索实现。本图只产决策；施工经项目负责人指示后展开。

## Notes

- **边界（开图时与项目负责人钉死，2026-10-22）**：候选 8 = 搜索契约整体治理，三条线即 handoff 2026-10-22 所列：`index.json` 投影字段 + fastsearch + kind 门禁归属；产品侧 featured 契约不重开（ADR-0006/0009 已锁）；不替换搜索实现（pagefind / Algolia 等第三方方案不做）；不动视觉 / CSS；不随图做内容填充（buy_url/listed、about.md、socialIcons、脚手架文章）。
- 术语以根目录 `CONTEXT.md` 为准；本图可能新增「搜索契约」「搜索索引」类术语条（措辞归 0048 决策，排图期不预设用词）。
- 闭卷 ADR：0001（双配置构建）、0002（no-js 渐进增强基线）、0004（产品状态模块）、0005（SOP 管线——派生文自动进索引，`assert_sop_pipeline.py` 已有「索引含全部派生条目」断言）、0006（产品索引双 seam + **0019 边界注释：index.json 直读 `site.Data.products` 不过 kind 门禁，归属本图**）、0007（reveal 协议——**搜索 JS 与 index.json 投影明确不属该图，归本图**）、0008（主题 fork 分层 + B11 search 页三挂点断言）、0009（精选——**索引是否投影 featured 归本图**）。
- 本图的任务是回答上述边界注记 deferred 到本图的问题，不重开已锁契约。
- Hugo 0.164 语义编写（CI 钉版）：0.166+ 条件多 return 写法本地过、CI 红，禁止。
- 测试总原则：Hugo 无模板单测，静态产物只能 build-then-assert；fixture 基建单份（现有三套构建：dataDir fixture / contentDir fixture / 真实数据）；行为断言先例 = `npm test`（jsdom，`assert_reveal.mjs` 16 条，样本手写镜像 DOM 契约、不用构建产物）；变异检验 + 独立字面量期望值。
- 分层判据（ADR-0008）：`index.json` 属站点层（内容 / 数据），fastsearch / fuse 属主题层（行为）；两层不得存在同相对路径文件。**2026-10-22 勘误**：本图排图期曾记「跨层先例：reveal 引擎在主题层」——不成立，reveal 引擎实际在**站点层** `assets/js/mf-reveal/`（消费方亦在站点层，经主题 extend_footer 加载），reveal 并非跨层模块；搜索的两半（站点层投影 × 主题层检索）是本项目第一个跨层契约组合，0043 的「不合并命名」即据此。
- 用户是项目负责人：HITL 工单必须实时对话解决，agent 不得自答；事实自己查，决策问用户；一次一问，先给推荐答案。
- 事实底座：`research/0042`（排图日由研究子代理落盘）。后续工单的事实争辩以该份为准，不重新推导。

## Decisions so far

<!-- 索引：每个已决工单一行 gist + 链接；决策详情只存在于工单，此处不重述。 -->

- [搜索模块现状事实底座（盘点）](tickets/0042-search-module-facts.md) — index.json 六字段且 **summary/content 同源**（content 不含正文）、三类排除、产品条目直读 products 不过 kind 门禁、投影层零 errorf；fastsearch 仅 search 页加载、**fuseOpts 未配置**（nil 走默认，:29-43 为潜伏死路径）、XHR 失败仅 console.log 属静默失效；现有断言只覆盖产品 tag（fixture）与三挂点（真实构建），**fastsearch 行为测试为零**；缺口 10 条；SOP fixture 缺 intro 致 `%!s()` 静默进索引（投影无校验活例证）。
- [搜索契约的模块边界与 seam 形状](tickets/0043-search-module-boundary-seam.md) — **单文件自足**（index.json 一文件承载投影 + jsonify + errorf，对照 `_content.gotmpl` 先例，不拆双 seam——薄渲染 seam 在 JSON 单一形态下是空壳）；**三层文档契约**（CONTEXT.md 术语条 / index.json 文件头 docstring 五块为唯一定义处 / 测试字面量，不建 spec seam）；**模块只圈站点层投影**，fastsearch 归 0046（协议化则并列互指不合并命名）、search 页面留 B11，交付面与 fastsearch 接口条款写进 docstring；**投影守自消费字段**（产品 name/summary 缺失即 errorf，前缀「搜索索引数据：」，不重验产品链已有门禁）；keys 对齐与文章侧投影/排除规则断言落 `assert_site_contracts.py`（套件最终形态归 0047）。同场施工已完成（TDD 红绿 + 变异检验）。
- [索引投影字段契约](tickets/0044-index-projection-field-contract.md) — **字段集冻结六项：featured / kind 均不投影**（无消费方；kind 顺带简化 0045——索引对 kind 零暴露）；**summary/content 同源确认为有意设计**（P2-6 瘦身初衷），truncate 200/320 为调值仅文档不断言；**产品条目形态全加断言**（title=name / permalink 锚点 / content 拼接），落既有 fixture 构建。同场施工已完成（表征绿 + 三处变异红）。
- [fastsearch 的协议归属与 DOM 契约](tickets/0046-fastsearch-protocol-dom-contract.md) — **独立「搜索协议」现状快照契约**（docstring 落 fastsearch.js 文件头，与 reveal 三层同构；不并入 reveal、不跨层合并）；**快照全量收录**（挂点/.focus/li 结构/键盘语义/XHR 容错，静默失效标注已知限制）；**删 fuseOpts 参数位**（默认值升格为契约，调参走代码+契约+评审）；**容错只记录不修**。同场施工已完成（行为保持型重构 + docstring 落位 + 施工期翻出项目级覆盖层：合并入主题层、删副本、加单副本守门断言）。
- [kind 门禁在索引投影中的归属](tickets/0045-kind-gate-ownership.md) — **隐式兜底定案**：门禁归产品索引链，索引不消费 kind（0044）故零暴露、零执法；坏 kind 由产品页恒渲染触发 errorf，兜底的牙是 assert_real 产品页全量断言；0019 边界注释改写为结论记录。
- [搜索契约的测试缝](tickets/0047-search-test-seam.md) — **不立 jsdom 行为套件**（fastsearch 是无导出经典脚本，harness 成本 ~100 行且测的是遗留快照；重写时新引擎抽 ESM、测试与新契约一起 TDD）；**改补产物断言**（search 页引用 search.*.js + 构件落盘 + fetch 同目录 index.json，锚 fixture 构建）；**套件不改名**（头注释五类→七类，CI 与 npm test 零改动）。
- [收口：术语、导航与 ADR 耐久化](tickets/0048-closure-terminology-adr.md) — **一词条两指针**（不新立「搜索协议」术语；0046「并列互指」表述勘误）；**单份 ADR-0010 五组决策** + 给 0006/0007/0009 加指针；**AGENTS.md** §7 两行 + 坑点 13「搜索契约纪律」；handoff 同场落。**本题关闭 = 候选 8 目的地到达。**

## Not yet specified

<!-- 雾区：在目的地内、但还无法精确表述的问题。随 frontier 推进毕业为工单。 -->

（本图收口时雾区清空——四条雾区均挂在「重写 fastsearch」或「新功能」上，超出「现状治理」的目的地，已移入 Out of scope。）

## Out of scope

- **替换搜索实现**（pagefind / Algolia / 其他本地引擎）：目的地是「从现状深化」，换实现是新方向、新地图，不属本图。
- **视觉 / CSS 调值**（`search.css`、结果列表样式、动效时长）：视觉层（候选 5/6/7 先例）。
- **fuse 检索参数数值调优**（threshold / distance / limit 的具体取值）：属调值不属契约；fuseOpts 参数位已删（0046 决议③），默认值写在 fastsearch.js docstring 契约里，调参 = 改代码 + 改契约 + 评审。
- **内容填充**（`data/products.yaml` 的 buy_url/listed、`content/about.md` 真实简历、socialIcons 真实邮箱、删脚手架文章）：卡用户材料，不随图。
- **菜单 `parent` 子项渲染**（4 个 categories 子项配置了不渲染）：独立新需求。
- **后端重启时的产品数据源替换**：ADR-0006 已定，届时只动 `product-items.html` 一处。
- **重写 fastsearch 时才有的面**（结果列表深化：摘要/标签/命中高亮；引擎形态：ESM 模块化与 fuse/license 依存；索引加载失败的容错 UX）：本图目的是现状治理，这三条雾区随收口移出——重写若发生，是下一张图的事，届时以本图的快照契约为输入。
- **搜索入口形态**（快捷键唤起 / 首页常驻搜索框）：新功能方向，用户未提出，不属本图。

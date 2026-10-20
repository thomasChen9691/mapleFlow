---
id: map-reveal-protocol
title: reveal 协议图（候选 5）
labels: [wayfinder:map]
status: closed
created: 2026-10-19
closed: 2026-10-20
---

# reveal 协议图（候选 5）

## Destination

候选 5「reveal 协议」的决策集定稿：no-js 基线之上的三块客户端动效交互（产品索引筛选、页脚滚动进场、首页 hero mf-rise 进场）统一为一个模块——边界内的 seam 划分与脚本落点、「可测试」的缝（JS 行为测试与产物断言的分工与落点）、筛选交互语义与 is-in 写入方协议、术语/seam 命名/ADR 耐久化。达到「可测试、AI 可导航」的可施工状态即收口。本图只产决策；施工按候选 4 先例，经项目负责人指示后展开。

**状态：已收口（2026-10-20）。** 目的地到达——六张工单全 closed（0021 事实底座、0022 边界与落点、0023 测试缝、0024 语义、0025 协议、0026 收口），无剩余决策。代码与测试已按决议施工（行为 16/16、产品 39/39、SOP 100/100、CI 接线完成）；文档写入（CONTEXT.md 术语、AGENTS 导航、ADR-0007）按 0026 决议执行中。

## Notes

- **边界（2026-10-19 起图时与项目负责人钉死）：三块全含**——`layouts/partials/product-index.html` 内联筛选脚本、`layouts/partials/extend_footer.html` 滚动进场 IO 脚本、`layouts/index.html` 的 mf-rise hero 进场，共享 `layouts/_default/baseof.html` + `layouts/partials/extend_head.html` 的 no-js/js 基线（ADR-0002）。
- 领域词汇以根目录 `CONTEXT.md` 为准；讨论敲定的新术语当场写入 `CONTEXT.md`，不攒批。
- 闭卷 ADR：0001（生产构建固定命令）、0002（no-js 渐进增强基线——本图只在其上契约化交互，基线本身不重开）、0004（产品状态模块）、0005（SOP 发布管线）、0006（产品索引双 seam：filters 开关与 uid 挂点已归渲染 seam，本图接管 UI 之下的行为层）。
- Hugo 0.164 语义编写（CI 钉版）：本机 0.167 与 CI 之间存在不对称 skew，0.166+ 的条件多 return 写法本地过、CI 红，禁止。
- 测试总原则（research 0001 已立）：Hugo 生态无模板单测机制，静态产物只能 build-then-assert；但 JS 行为发生在 Hugo 构建之外——本图能否/如何引入 JS 行为测试是核心待决。
- 用户是项目负责人：术语敲定与 ADR 是否记录由用户拍板。质询一次一问，先给推荐答案。能查到的**事实**自己查（文件 / 子代理），只有**决策**问用户。HITL 工单必须与用户实时对话解决，agent 不得自答。
- 背景证据：候选 4 地图雾区「客户端筛选脚本的重写边界」随本图开图毕业（原注：脚本内含 `.reveal` / `is-in` 交互，与候选 5 交界未定）；该地图 Out of scope 已注明「reveal 协议（候选 5）各自独立成图」。

## Decisions so far

- [reveal 面事实底座与 JS 可测试性事实](tickets/0021-reveal-surface-facts.md) — 12+ 契约点盘点（含两个 is-in 写入方）+ 测试覆盖近乎零（唯一相邻断言是 mf-filter 有无）；js.Build 自 v0.74.0 引入、0.164 可用且源码保持可单测形态；--minify 改 JS 不改语义；jsdom/happy-dom 可行（未安装，CI 增量为行数级）；harness 与 Hugo 版本 skew 解耦。
- [模块边界内的 seam 划分与脚本落点](tickets/0022-module-seam-and-script-placement.md) — 分层提取（swap 留 inline、IO+筛选引擎提取 assets/js 走 js.Build，PaperMod 同款管线先例）；三层文档契约（术语/docstring 唯一定义处/测试字面量），不提前建 ADR-0006 挂起的词汇 seam；DOM 契约命名权归协议层，ADR-0006 接口语义不动（uid 仍必填兼锚，引擎遍历 .mf-index roots 注册）；测试分流定案：行为 harness 9 项 / 产物断言 6 项 / 逐出 2 项。
- [可测试的缝：JS 行为测试与产物断言的分工](tickets/0023-reveal-test-seam.md) — 依赖入仓 + CI 权威（package.json/lock + npm ci + node harness 两步）；套件两脚本两 step；行为用手写样本、契约合规由 B 类产物断言守；no-js 基线缺口落 B 类。
- [筛选交互语义定案](tickets/0024-filter-interaction-semantics.md) — 全部确认现状：同值回 all、aria-pressed 组内互斥、计数「显示 X / Y」、空态双文案、uid 不扩 hash、reduced-motion 不播动画。
- [is-in 写入方协议与动效降级统一](tickets/0025-is-in-writer-protocol.md) — is-in 一次性终态（IO unobserve + 筛选直写）；--mf-i 语义归协议、数值归 CSS；降级 JS 共享单一判定 + CSS 兜底保留；mf-rise 契约到存在性+降级。
- [术语、seam 命名与 ADR 收口](tickets/0026-terminology-naming-adr.md) — CONTEXT.md 只加「reveal 协议」主术语（实现词汇不进表）；motion.js 改名 reduced-motion.js；AGENTS 行+坑点+命令三处；ADR-0007 承载决策集，0002/0006 加指针不改正文。**本题关闭 = 目的地到达，地图 closed。**

## Not yet specified

<!-- 空：0023 已定样本来源与 CI 供给；目的地前仅剩 0026 收口（术语/命名/ADR） -->

## Out of scope

- **站内搜索 JS 与 index.json 投影契约**：候选 8（搜索契约），候选 4 已划定。
- **主题 fork / PaperMod 子模块升级**：ADR-0002 的两个覆盖文件同步义务不随本图重开。
- **CSS 动效参数调值**（时长、曲线、降级阈值）：视觉层，本图只定契约语义。
- **data/products.yaml 内容填充**：卡用户材料，不随图。

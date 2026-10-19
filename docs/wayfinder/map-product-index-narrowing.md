---
id: map-product-index-narrowing
title: product-index 接口收窄图（候选 4）
labels: [wayfinder:map]
status: closed
created: 2026-10-19
closed: 2026-10-19
---

# product-index 接口收窄图（候选 4）

## Destination

候选 4「product-index 接口收窄」的决策集定稿：`layouts/partials/product-index.html` 的接口形状（入参 / 数据来源 / 多实例契约）、筛选词汇来源、测试缝形状、命名与导航契约——达到「可测试、AI 可导航」的可施工状态。本图只产决策，不落地代码；施工留待地图关闭后按 verify-then-commit 展开。

**状态：已收口（2026-10-19）。** 目的地到达——六张工单全 closed，无剩余 frontend 决策。代码与测试已按决议施工完毕（产品 29/29、SOP 100/100、生产构建干净）；文档写入（ADR-0006、CONTEXT.md 术语、AGENTS.md 导航痕迹）按 0020 决议执行中，不涉新决策。

## Notes

- **施工进行中（2026-10-19，按项目负责人指示提前开工，早于地图关闭）**：0015/0016 已决部分已落地（双 seam + kind 契约 + limit 契约，测试 21/21 + SOP 100/100）；0017/0019 已决（uid 必填 / 测试缝合流 + 收口三格）待施工；两项工单的「施工期注记」段登记了待 0020 追认事项。剩余 open 工单：0020（命名/ADR 收口）。
- 领域词汇以根目录 `CONTEXT.md` 为准：产品、交付形态（工作流 / 文档 / 题库）、产品状态、领取入口、即将上架、已上架、可下载产品。讨论敲定的新术语当场写入 `CONTEXT.md`，不攒批。
- 闭卷 ADR：0001（生产构建固定命令）、0003（后端只镜像、分歧对齐 Hugo；产品域不进后端）、0004（产品状态模块：模板与首页不得自行推导状态，`errorf` 契约执法）、0005（SOP 发布管线，本图不碰）。0004 已裁决事项（位置 / 输入契约 / 双构建测试）不得重开。
- Hugo 0.164 语义编写（CI 钉版）：本机 0.167 与 CI 之间存在不对称 skew，0.166+ 的条件多 return 写法本地过、CI 红，禁止。
- 用户是项目负责人：术语敲定与 ADR 是否记录由用户拍板。质询一次一问，先给推荐答案。能查到的**事实**自己查（文件 / 子代理），只有**决策**问用户。HITL 工单必须与用户实时对话解决，agent 不得自答。
- 用户 2026-10-19 计划重启后端开发：本图不改 ADR-0003 边界（产品域仍不进后端）；`docs/sop/MAPLEFLOW_BLOG_SOP.md` 的 backend 历史指令已作退役标注、保留参考。
- 背景证据：摩擦定位 product-index dict 接口泄漏——partial 自读 `hugo.Data.products` 全局数据 + `featured`/`limit`/`filters`/`uid` 四入参，且一个模板内混装「列表渲染 / 筛选 UI / 客户端脚本」三责；筛选词汇问题由工单 0005 划归本图。原架构评审 HTML（temp 目录）已被清理，本图事实底座以代码现状重立（调用方共 3 处：短代码、`layouts/index.html:110`、测试 fixture）。

## Decisions so far

- [fixture 与测试缝的事实底座](tickets/0018-fixture-test-seam-facts.md) — 三种构建原语已存在（fixture 双 config 覆盖 dataDir / 坏用例动态 TOML 直指 bad/<case>、判定=非零退出+「产品状态」前缀 / 真实数据生产构建）；现有 fixture 只覆盖产品状态 2×2，product-index 输入组合仅默认路径一格被断言，缺口 11 项；契约断言语义偏弱（只匹配统一前缀，SOP 的逐用例子串手法可复用）；Hugo 版本 skew 无脚本级适配，CI 守门点在两个断言步。
- [product-index 职责边界与数据注入方向](tickets/0015-product-index-responsibility-boundary.md) — 双 seam 拆分：product-items（唯一读 hugo.Data.products，featured 缺省 false + limit 缺省/0=全量、负数 errorf，无 source 注入位）+ product-index（纯渲染 items + 筛选 UI + uid，零全局读，空态留渲染 seam）；范围只收窄索引渲染链，首页计数条与搜索索引不动。
- [筛选词汇来源：写死还是数据派生](tickets/0016-filter-vocabulary-source.md) — 契约化写死：三枚 kind 按钮 = CONTEXT.md 交付形态封闭词表的执行区；kind ∈ 三值封闭集由 product-items 数据门禁逐条校验，未知 kind 即 errorf（前缀「产品索引数据：」，含产品 id + 坏值）；产品状态模块不碰，0005 裁决不变。
- [同页多实例契约 uid](tickets/0017-multi-instance-uid-contract.md) — uid 显式必填（删 default "mf-idx" 死缺省）；短代码由 .Ordinal 页内保唯一、模板调用方写字面量（兼深链锚）；重名纯文档约定不执法（partial 无页级视野，检测成本与收益悬殊）。
- [接口收窄后的测试缝形状](tickets/0019-narrowed-interface-test-seam.md) — 合流追认（测试留在 assert_product_states.py，5 条缝）；收口三格全补：limit 截断（fixture 4 featured 逼真截断 + 第 4 条不上首页断言）、filters 开关差异、uid 必填坏用例；搜索索引 kind 门禁归候选 8，index.json 留边界注释。
- [命名、导航契约与 ADR 耐久化](tickets/0020-naming-navigation-adr.md) — 文件名保留，CONTEXT.md 新增「产品索引」术语条（seam 分工进 AGENTS.md 不进术语表）；新开 ADR-0006 承载候选 4 决策集，ADR-0004 加指针行；导航痕迹三处齐落（AGENTS 速查 2 行 + 坑点 1 条 + 交付形态封闭集执法注记）。**本题关闭 = 目的地到达，地图标记 closed。**

## Not yet specified

- **调用点适配范围**：短代码 `layouts/shortcodes/product-index.html` 与首页 `layouts/index.html:110` 两处调用随接口收窄的改造量（取决于 0015 的方向）。
- **客户端筛选脚本的重写边界**：脚本内含 `.reveal` / `is-in` 交互，与候选 5「reveal 协议」图的交界未定。
- **fixture 数据与真实数据的同步节奏**：fixture 是否需要跟随 `data/products.yaml` 演进（取决于 0019 的测试缝定案）。
- **空态文案归属**：「暂无资源」「没有符合筛选条件」两处空态由模板写死还是随接口收窄上移（取决于 0015）。

## Out of scope

- **reveal 协议（候选 5）、主题 fork、搜索契约**：各自独立成图，不并进本图。其中**搜索索引的 kind 门禁**经 0019 决议明确归候选 8（搜索契约）——`index.json` 已留边界注释。
- **backend 产品 API**：ADR-0003 边界内后端只镜像文章，产品域不进后端；用户重启后端计划不改变此边界。
- **`data/products.yaml` 占位产品填充**（`buy_url` 填空 + `listed` 翻 true）：施工动作，且卡在用户提供真实商品页地址，不随本图。
- **视觉 / CSS 改动**：本图只收窄接口、契约与测试缝，不动样式。

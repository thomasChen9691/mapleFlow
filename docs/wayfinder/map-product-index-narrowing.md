---
id: map-product-index-narrowing
title: product-index 接口收窄图（候选 4）
labels: [wayfinder:map]
status: open
created: 2026-10-19
closed:
---

# product-index 接口收窄图（候选 4）

## Destination

候选 4「product-index 接口收窄」的决策集定稿：`layouts/partials/product-index.html` 的接口形状（入参 / 数据来源 / 多实例契约）、筛选词汇来源、测试缝形状、命名与导航契约——达到「可测试、AI 可导航」的可施工状态。本图只产决策，不落地代码；施工留待地图关闭后按 verify-then-commit 展开。

## Notes

- 领域词汇以根目录 `CONTEXT.md` 为准：产品、交付形态（工作流 / 文档 / 题库）、产品状态、领取入口、即将上架、已上架、可下载产品。讨论敲定的新术语当场写入 `CONTEXT.md`，不攒批。
- 闭卷 ADR：0001（生产构建固定命令）、0003（后端只镜像、分歧对齐 Hugo；产品域不进后端）、0004（产品状态模块：模板与首页不得自行推导状态，`errorf` 契约执法）、0005（SOP 发布管线，本图不碰）。0004 已裁决事项（位置 / 输入契约 / 双构建测试）不得重开。
- Hugo 0.164 语义编写（CI 钉版）：本机 0.167 与 CI 之间存在不对称 skew，0.166+ 的条件多 return 写法本地过、CI 红，禁止。
- 用户是项目负责人：术语敲定与 ADR 是否记录由用户拍板。质询一次一问，先给推荐答案。能查到的**事实**自己查（文件 / 子代理），只有**决策**问用户。HITL 工单必须与用户实时对话解决，agent 不得自答。
- 用户 2026-10-19 计划重启后端开发：本图不改 ADR-0003 边界（产品域仍不进后端）；`docs/sop/MAPLEFLOW_BLOG_SOP.md` 的 backend 历史指令已作退役标注、保留参考。
- 背景证据：摩擦定位 product-index dict 接口泄漏——partial 自读 `hugo.Data.products` 全局数据 + `featured`/`limit`/`filters`/`uid` 四入参，且一个模板内混装「列表渲染 / 筛选 UI / 客户端脚本」三责；筛选词汇问题由工单 0005 划归本图。原架构评审 HTML（temp 目录）已被清理，本图事实底座以代码现状重立（调用方共 3 处：短代码、`layouts/index.html:110`、测试 fixture）。

## Decisions so far

- [fixture 与测试缝的事实底座](tickets/0018-fixture-test-seam-facts.md) — 三种构建原语已存在（fixture 双 config 覆盖 dataDir / 坏用例动态 TOML 直指 bad/<case>、判定=非零退出+「产品状态」前缀 / 真实数据生产构建）；现有 fixture 只覆盖产品状态 2×2，product-index 输入组合仅默认路径一格被断言，缺口 11 项；契约断言语义偏弱（只匹配统一前缀，SOP 的逐用例子串手法可复用）；Hugo 版本 skew 无脚本级适配，CI 守门点在两个断言步。

## Not yet specified

- **调用点适配范围**：短代码 `layouts/shortcodes/product-index.html` 与首页 `layouts/index.html:110` 两处调用随接口收窄的改造量（取决于 0015 的方向）。
- **客户端筛选脚本的重写边界**：脚本内含 `.reveal` / `is-in` 交互，与候选 5「reveal 协议」图的交界未定。
- **fixture 数据与真实数据的同步节奏**：fixture 是否需要跟随 `data/products.yaml` 演进（取决于 0019 的测试缝定案）。
- **空态文案归属**：「暂无资源」「没有符合筛选条件」两处空态由模板写死还是随接口收窄上移（取决于 0015）。

## Out of scope

- **reveal 协议（候选 5）、主题 fork、搜索契约**：各自独立成图，不并进本图。
- **backend 产品 API**：ADR-0003 边界内后端只镜像文章，产品域不进后端；用户重启后端计划不改变此边界。
- **`data/products.yaml` 占位产品填充**（`buy_url` 填空 + `listed` 翻 true）：施工动作，且卡在用户提供真实商品页地址，不随本图。
- **视觉 / CSS 改动**：本图只收窄接口、契约与测试缝，不动样式。

---
id: map-product-state-convergence
title: 产品状态模块深化图（候选 1）
labels: [wayfinder:map]
status: closed
created: 2026-10-15
closed: 2026-10-15
---

# 产品状态模块深化图（候选 1）

## Destination

候选 1「产品状态推导收敛」的决策集定稿：模块驻留位置（seam）、占位例外的数据表示、可下载产品指标口径、测试缝形状、命名与导航契约——达到「可测试、AI 可导航」的可施工状态。本图只产决策，不落地代码；施工留待地图关闭后按 verify-then-commit 展开。

## Notes

- 领域词汇以根目录 `CONTEXT.md` 为准：产品、交付形态、领取入口、即将上架、已上架、可下载产品。不得另造同义词。
- ADR-0001~0003 闭卷不得重开。本图唯一交互点：若 seam 落在构建期脚本，须遵守 ADR-0001 的固定构建命令（集成而非修改）。
- 工程纪律见 `AGENTS.md` 第 9 节：每批次单独 commit；讨论敲定的术语当场更新 `CONTEXT.md`，不攒批。
- 用户是项目负责人：术语敲定与 ADR 是否记录由用户拍板。质询一次一问，先给推荐答案。
- 能查到的**事实**自己查（文件 / 子代理），只有**决策**问用户。
- 背景证据：架构评审报告候选 1（摩擦定位 `layouts/index.html:54-55` 与 `layouts/partials/product-index.html:46,63-70` 两处重推 + 占位例外无代码表示；首页对外显示 5、术语口径 0）。

## Decisions so far

- [查清 Hugo 模板可测性事实](tickets/0001-hugo-template-testability.md) — Hugo 无模板单测机制，测试只能 build 后断言产物；派生数据靠 return 型 partial（0.164 限根级单条 return）+ site.Store；data/ 纯静态；本机 0.167 与 CI 0.164 的 return 语义分叉已坐实，深化方案按 0.164 编写。
- [产品状态模块的驻留位置](tickets/0002-module-seam-location.md) — seam = 单一 return 型 partial（排除预构建脚本：漏跑即静默腐化）；形状 B：模块拥有状态判定 + 控件/文案语义；规则全集 5 条（搜索投影不外扩）；存活测试 = products.html 控件态 + index.html 计数两条产物断言，覆盖 100%。
- [占位例外的数据表示](tickets/0003-placeholder-data-representation.md) — 显式上架状态字段，必填无缺省、缺失即 errorf 构建失败；price 同案严格（免费显式写 0）；模块输入契约成形（已上架⇒buy_url 真实、未上架⇒buy_url 空）；CONTEXT.md 可下载产品定义随机制 sharpen。
- [可下载产品指标口径](tickets/0004-downloadable-metric-display.md) — 显示 0：指标含义不因数字重定义；迁移后当前值 0 属预期；数据条该格改消费模块的已上架判定。
- [测试缝的形状](tickets/0005-test-seam-shape.md) — 契约执法在模块内（errorf，构建即门禁）；双构建覆盖（fixture 全分支 + 真实数据线上回归）；CI 权威 + 本地 advisory；脚本落 tests/assert_product_states.py；ADR-0001 只做加法。
- [模块命名与导航契约](tickets/0006-module-naming-and-navigation.md) — 定名「产品状态模块」（layouts/partials/product-state.html），CONTEXT.md 术语条当场写入；决策耐久性落 ADR-0004（纪律①的阅读路由不含 wayfinder 目录，决策必须活在 docs/adr/）。**本题关闭 = 目的地到达，地图标记 closed。**

## Not yet specified

（空——雾区已清空；剩余决策仅在 frontier 工单 0006）

## Out of scope

- **候选 7「精选机制落地」**：方向已由项目负责人决议（给文章加 featured 字段），另行开工，不并进本图。
- **候选 2~6、8**：SOP 真源、后端解析器诚实化、product-index 接口收窄、reveal 协议、主题 fork、搜索契约 —— 各自独立成图。
- **backend 产品 API**：ADR-0003 边界内后端只镜像文章，产品域不进入后端。
- **products.yaml 占位数据迁移改写**：施工动作，地图关闭后执行。

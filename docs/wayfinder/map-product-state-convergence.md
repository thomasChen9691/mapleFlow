---
id: map-product-state-convergence
title: 产品状态模块深化图（候选 1）
labels: [wayfinder:map]
status: open
created: 2026-10-15
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

（空）

## Not yet specified

- **构建集成方式**：若 seam 选定构建期脚本，CI（`.github/workflows/deploy.yml`）与本地 dev 如何获得派生数据 —— 依赖工单「产品状态模块的驻留位置」。
- **数据迁移与上线时序**：`products.yaml` 5 条 TEST buy_url 改写成新表示的时点与顺序 —— 依赖工单「占位例外的数据表示」。
- **测试运行阶段**：若测试缝选定构建产物断言，测试挂在 CI 哪一步、本地如何跑 —— 依赖工单「测试缝的形状」。

## Out of scope

- **候选 7「精选机制落地」**：方向已由项目负责人决议（给文章加 featured 字段），另行开工，不并进本图。
- **候选 2~6、8**：SOP 真源、后端解析器诚实化、product-index 接口收窄、reveal 协议、主题 fork、搜索契约 —— 各自独立成图。
- **backend 产品 API**：ADR-0003 边界内后端只镜像文章，产品域不进入后端。
- **products.yaml 占位数据迁移改写**：施工动作，地图关闭后执行。

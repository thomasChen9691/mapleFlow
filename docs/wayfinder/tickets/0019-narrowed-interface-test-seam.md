---
id: 0019
title: 接口收窄后的测试缝形状
type: grilling
mode: HITL
status: closed
blocked_by: [0015, 0018]
assignee: agent
map: map-product-index-narrowing.md
claimed: 2026-10-19
closed: 2026-10-19
---

## Question

接口收窄后，「可测试」落在哪个缝上：哪些 fixture 构建 × 哪些产物断言，才能覆盖输入组合全分支（含空态、限额、筛选开关、多实例）？缝与 `tests/assert_product_states.py` 合流为一个套件还是独立脚本？CI 守门策略（权威 / advisory）如何安排？

背景（事实，已核）：ADR-0004 已定测试总原则——Hugo 生态无模板单测机制，只能 build-then-assert；契约执法在模块内 `errorf`、构建即门禁；CI 权威 + 本地 advisory；双构建（fixture 全分支 + 真实数据线上回归）。定案须遵守这些闭卷原则，只回答「针对收窄后接口的具体缝形状」。

## 施工期注记（2026-10-19，待本工单追认）

按项目负责人指示，0015/0016 决议的施工已提前开工（地图未关闭）。与本题相关的施工事实：测试**并入** `tests/assert_product_states.py`（未新建独立脚本）；新增逐用例子串表 `BAD_CASE_EXPECT`、调用方级坏用例两个（limit 负数经短代码链、items 缺失经 layoutsDir 直调）、首页 featured 分栏断言、空态断言。评审 additionally 提出一个待决问题：搜索索引（`index.json`）直读 `site.Data.products` 且不经 kind 门禁——覆盖率隐含依赖「产品页短代码必渲染全量」；该问题属本题还是候选 8（搜索契约），未定。

## Resolution

2026-10-19 · grilling（用户为决策者），三问落定：

1. **套件形状 = 合流追认**：产品索引接口的测试留在 `tests/assert_product_states.py`（施工期假设追认），头注释已扩写为 5 条缝。fixture 基建（dataDir 双 config / bad 扫描 / 坏用例判定 / 双报告）单份——拆脚本即复制基建，第二实现必然漂移（ADR-0004 枪毙过的模式）。脚本名稍窄的问题留 0020 处理。
2. **覆盖收口 = 三格全补**（施工期事项）：
   - **limit 截断**：fixture 改 4 条 featured → 首页 `limit=3` 真正截断，断言前 3 上首页、第 4 条不上首页（此前 fixture 仅 1 条 featured、真实数据恰好 3 条，截断路径零覆盖——首页少显示产品无任何报错，属数据静默消失类）；
   - **filters 开关差异**：products.html 有 `mf-filter` 按钮、首页精选区无（渲染 seam 自身分支）；
   - **uid 必填**（0017 新契约）： layoutsDir 直调 partial 不传 uid → 构建失败，无绿色证据不放行。
3. **搜索索引 kind 门禁 = 归候选 8 + 本图留边界注释**：`layouts/_default/index.json` 加一行注释——kind 契约由产品页渲染链执法（产品页恒渲染全量 → 门禁恒生效），索引投影不重复校验；门禁去留随候选 8 的投影契约定案。计数条（`index.html:56`）无此需求（kind 不影响 listed/price 计数语义，ADR-0004 已定案）。

**下游影响**：0020 收口无新阻塞。雾区「fixture 数据与真实数据的同步节奏」随本题部分溶解——fixture 明确跟随接口分支演进（非跟随真实数据），剩余「调用点适配范围」「脚本重写边界」两条留待施工期/候选 5。施工动作四项（fixture 4 featured + 截断断言 / filters 断言 / uid 坏用例 / index.json 注释），随下一批 verify-then-commit。


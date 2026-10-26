---
id: "0077"
title: 守卫模块的测试缝：单模块如何被 build-then-assert
type: grilling
mode: HITL
status: closed
blocked_by: ["0073", "0074"]
assignee: agent
map: map-featured-type-guard.md
created: 2026-10-25
claimed: 2026-10-26
closed: 2026-10-26
---

## Question

守卫模块的测试缝——Hugo 无模板单测，「可测试」对单模块意味着什么。现状：文章侧两例（字符串 / 整数，contentDir fixture）+ 产品侧一例（dataDir fixture）锚「构建失败 + 消息子串」；SOP 侧零 fixture（_content.gotmpl 的守卫无坏例——待 0072 确认）。候选测试缝：

- **(a) 各消费方链路各留坏用例**——模块的正确性由三个调用方的构建失败间接证明；SOP 侧补一例；
- **(b) 模块直接探针**——一个最小 fixture 构建直接驱动 partial 传各类值（未声明 / bool true / bool false / 字符串 / 整数），断言构建成功或失败；
- **(c) (a) + (b)**。

要决策的面：

1. **测试缝选 a / b / c**；「可测试」的判定标准（单模块的每个分支是否有至少一条断言可定位地红）。
2. **SOP 侧坏值缺口补不补**（补则 `bad/sop/` 新增一例 + `BAD_CASE_EXPECT` 登记；不补则记录为已知限制）。
3. **ADR-0014 决策 8 的「自测先于契约红」模式**（harness 自测独立双文件、只测牙临界）能否适用于 Hugo partial 守卫——Hugo 侧无 Node/Python seam，probe 构建是否等价物。
4. **变异检验口径**：破坏模块的哪个行为 → 哪条断言红（模块三分支：unset skip / bool 放行 / 非 bool errorf）。

边界（不开票）：消息文案归 0076；fixture 基建单份不变（不新开第四套构建）。

## Resolution

2026-10-26 · grilling（HITL，项目负责人三问定案）：

**Q1 测试缝 = 各消费链**：测公开行为（三条链的构建失败），**不建模块探针**——探针测 partial 内部 API（实现细节），改模块签名即误红；模块分支（未声明跳过 / bool 放行 / 非 bool errorf）经正路 + 坏值 fixture 全触达。

**Q2 SOP 缺口 = 补**：新增 `tests/fixtures/bad/sop/sop-featured-not-bool/`（`data/sop.yaml` + `notes/FEAT_BAD.md`，`featured: "true"` 字符串）+ `BAD_CASE_EXPECT` 登记（钉 origin + label + 契约三要素，防「因别的原因失败也绿灯」）；SOP 套件 **104→105**。

**Q3 自测模式 = 不适用**：Hugo 模板侧无可独立执行的 seam（不像 harness 的 Node/Python 文件），「自测先于契约红」的定位优势不存在；记录为与 ADR-0014 决策 8 的**已知差异**——模板侧模块的可测试性由套件级消费链断言承担。

**施工（红绿）**：先加 fixture（红：表完整性自检报「BAD_CASE_EXPECT 缺该用例」104/105）→ 补期望（105/105 绿）；变异 = 禁用模块类型检查 → **四条坏值断言同时红**（site 156/159 + sop 104/105）。

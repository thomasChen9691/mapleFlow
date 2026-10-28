---
id: "0087"
title: parity 门的落点与强度
type: grilling
mode: HITL
status: open
blocked_by: ["0086"]
assignee: agent
claimed: 2026-10-27
map: map-architecture-deepening.md
created: 2026-10-27
---

## Question

parity 门放在哪、失败时是红还是构建失败——「门装在哪面墙」的问题。0086 定了 token 集合与方向，本票定**执行面与失败语义**。

现状：可用的执行面有三处——`npm test` 链（`assert_harness.mjs` → `assert_reveal.mjs` → `assert_search.mjs`，Node + jsdom）、`tests/assert_site_contracts.py`（构建产物套件，CI 权威）、以及 Hugo 构建期（`errorf`，只能读 `assets/` 与 `layouts/`，**读不到 JS 源码的运行时行为**）。CI 门禁已含三者（verify job）。

要决策的面：

1. **落点**：(a) `assert_reveal.mjs` 内新增一节（与行为断言同套件，但它读的是源码文本而非 DOM）；(b) `assert_site_contracts.py` 新增一类（与产物断言同套件，读源码 + 产物 CSS）；(c) 独立脚本挂进 `npm test` 链（第四段）。三者在「失败时人往哪看」上不同。
2. **强度**：测试断言（红，可继续跑其余套件）还是构建期 `errorf`（构建失败）。构建期方案的可行性边界——CSS 在 `assets/css/extended/` 与主题 `assets/css/`，模板侧可 `resources.Get` 读文本，但 JS 侧模板不可读；若 token 清单是手写 registry，构建期才可行。
3. **失败消息形态**：缺哪个 token、谁写的（哪个引擎）、该谁消费（哪个 CSS 文件）、契约定义处指向（docstring 路径）；消息要不要按方向分两种（有写无读 / 有读无写）。
4. **与死面清理的顺序**：先删死面再上门（门只守活 token）还是先上门再删（门会先红一片）；这条顺序约束要写进收口票的施工序列。
5. **新引擎的引导**：新增 reveal 引擎时，parity 门如何要求它声明 token（docstring 固定格式？registry 条目？），以及「忘了声明」时是静默通过还是红。
6. **已知限制的登记**：语义漂移不可检、白名单可被滥用、构建期方案覆盖不到 JS——哪些接受并写进 ADR。

边界（不开票）：token 集合与方向归 0086；ADR-0007 的契约定义处不重开。

## Resolution（决议已定，施工未开始）

2026-10-27 · grilling（HITL，一问定案 + 两项按先例推定）。

**落点 = `assert_reveal.mjs` 新增一节**：Node 天然读源码（Hugo 模板侧只能 `os.ReadFile` + `findRE` 硬解析 JS，不可维护）；与 [0084](0084-registration-test-seam.md) 的「契约归 reveal」一致。**强度 = 测试红**（不阻塞构建）：CI 门禁已把「测试红」等同「合不进去」，构建期 errorf 的额外收益抵不上模板里写正则的成本。

**失败消息形态**（按方向分两种，均带四处定位）：
- 有写无读：`token X 被 <引擎文件:行> 写入，但无 CSS 消费`；
- 有读无写：`token X 被 <CSS 文件:行> 消费，但无 JS / markup 生产者（若非白名单，补生产者或登记白名单）`。

**新引擎引导 = 零登记**：抽取规则自动覆盖新增引擎的写入面，白名单是**例外清单**，新增引擎默认不需动它（这也否掉了「docstring 固定格式声明」与「registry 登记」两条路，与 0086 的清单来源决议一致）。

**已知限制**：只守存在性、不守语义漂移（0086 已记）；白名单为断言内常量（带理由注释），不设独立数据文件。

**施工状态**：**未开始**。本票保持 open + 已认领。

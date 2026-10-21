---
id: "0039"
title: 精选机制的测试缝与断言集
type: grilling
mode: HITL
status: open
blocked_by: ["0035", "0037", "0038"]
assignee: ""
map: map-featured-mechanism.md
created: 2026-10-21
---

## Question

精选机制的**测试缝**——文章侧精选用什么夹具造、断言落在哪个脚本、必锚哪些行为。事实底座：`tests/hugo.test.toml` 只覆盖 `dataDir`（research/0035 §4），文章 fixture 需新增 `contentDir` 覆盖，且 fixture 构建里 `hugo.Data.sop` 为空、派生文 0 篇。

待决：

1. **落点**：并入 `tests/assert_product_states.py`（fixture 基建单份纪律，ADR-0004/0006 枪毙第二实现），还是新脚本？该脚本名已偏离实际职责（0032 记过「命名债」），文章精选并入会让偏离更远——是**改名**、**继续记账**、还是**按职责新开脚本但共用 fixture 构建函数**（需论证不构成第二实现）。
2. **文章 fixture 的造法**：`contentDir` 覆盖到 `tests/fixtures/content`（真实 `content/` 不再参与 fixture 构建，SOP 派生文本就为 0，但需确认 fixture 里要不要复制 `_content.gotmpl` 与最小 `posts`）；或维持真实 `content/` 而在断言里硬编码真实文章的 featured 期望（**与真实内容耦合，内容一变断言就红**——须明确排除或接受）。两条路的取舍是本题核心。
3. **必锚断言清单**（参照 0032「必锚 6 条」的体例，逐条要能用变异检验证明有牙）：① featured 文章进首页、非 featured 不进；② 条数上限与截断（第 N+1 条 featured 不上首页）；③ 与「最近更新」网格的去重（若 0037 定为剔除）；④ 0 篇时的空态/隐藏行为；⑤ 缺省未声明 = 非精选；⑥ 坏值（若 0036 定为 errorf，则断言构建失败并钉错误子串；若定为静默，则断言按非精选渲染）。
4. **真实数据回归**：现有 5 篇手写 + 6 篇派生文里**谁标 featured**——这既是内容决策也是断言期望值的来源（独立字面量要求），须与项目负责人当场定，否则断言无处落地。
5. **跨类一致性断言**：是否给产品侧既有断言补一条「文章与产品同名同义」的守门（防止未来两侧语义漂移），还是仅在文档层约定。

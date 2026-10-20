---
id: 0032
title: 主题层可测试的缝
type: grilling
mode: HITL
status: closed
blocked_by: [0027, 0030]
assignee: agent
map: map-theme-fork.md
created: 2026-10-20
claimed: 2026-10-20
closed: 2026-10-20
---

## Question

fork 使主题代码成为仓内第一方代码后，「可测试」如何落地。事实底坐：0027 §6 主题行为零断言 9 处 + 三套件现状（fixture 基建单份、build-then-assert、变异检验纪律）。

待决问题（一次会话内按序过，先给推荐答案）：

1. **锚点清单**：从 9 处零断言面中选「必锚」子集。候选：no-js/js swap 全站面（当前仅 products/home 断言）、post_meta 时区格式回归（当前 golden 容错两形态、回退不红）、菜单 13 项与 uglyURLs 形态、RSS home-only-posts 语义、404 页、list/taxonomy 渲染、search.html 渲染、dev-vs-prod 双守卫差异。哪些进必锚、哪些明确不锚（如 search.html 渲染归候选 8 边界）？
2. **测试落点**：并入既有 `tests/assert_product_states.py` / `assert_sop_pipeline.py`（fixture 基建单份原则，ADR-0004/0006 先例：拆脚本=第二实现必然漂移）vs 新建主题契约脚本（命名/归属/CI step 位置）——注意 SOP 的 URL 冻结等既有断言已在 assert_sop_pipeline.py 中间覆盖主题产物面。
3. **golden 收严**：post_meta 时区两形态容错（sop_golden.py:23-39）是否随本次收严为单一形态（`.Date.Format "2006-01-02 15:04:05 -0700"`）——收严即让「时区修复被回退」变红，属本图的「可测试」核心收益之一。
4. **fork 完整性断言**：主题目录清单快照（防误删/漂移：如 0031 施工误删文件、未来编辑误伤）要不要、以何形态（golden 文件清单 vs 断言「9 个可达 partial 链存在」的可达性契约）？
5. **纪律沿用**：变异检验（每条断言破坏实现→红→还原）与测试期望值独立字面量两条纪律（ADR-0007 先例）是否明文写进本题 Resolution 作为主题断言的施工纪律。

决策记录：本题 Resolution 落「必锚清单 + 落点脚本 + golden 收严方案 + 完整性断言形态」，作为施工期测试扩展的执行依据。

## Resolution

2026-10-20 · grilling（五问全决，用户为决策者；施工待项目负责人指示）：

1. **必锚清单 = 6 条**（判据：坏了会静默且构建不会红）：
   - B7 no-js/js swap 全站面：扫描 `public/**/*.html`，每页含 `class=no-js` 与内联 swap 片段（404 页由此天然覆盖）；
   - B8 post_meta 时区格式：取已知文章页，title 属性匹配 `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}$`（独立字面量）；
   - B9 菜单契约：header 内链数量 == 13，内部 href 以 `.html` 或 `/` 结尾（uglyURLs 契约）；
   - B10 RSS 内容策略：`public/index.xml` 的 `<item><link>` 全部落在 `/posts/` 下；
   - B11 search 页 DOM：`#searchbox` / `#searchInput` / `#searchResults` 三挂点存在；
   - B12 og:image 兜底：无封面图页面仍输出 `og:image`（ogImage 参数生效）。
   **明确不锚**：list/taxonomy 渲染（构建兜底 + 视觉层）、归档页（模板已删）、dev-vs-prod 双守卫的 dev 侧（不跑 dev 构建，成本翻倍）。
2. **落点 = `tests/assert_product_states.py`**（不新建脚本——复制 fixture 基建即第二实现，ADR-0004/0006 枪毙模式）；**保持文件名，命名债记账**（脚本已装「产品状态 + 站点/主题产物契约」两类职责；等长出第三类职责时一次性改名 `assert_site_contract.py`，届时同步 CI step 名与 AGENTS/ADR 引用）。断言编号续 B7-B12；同脚本混 build-then-assert 与纯文件系统检查（同路径不变量）可接受。
3. **golden 不收严**：`sop_golden` 的时区双形态容错保留（CI 0.164 vs 本机 0.167 渲染差异 + 迁移期捕获）；post_meta 的回归牙口由 B8 独立断言提供，不靠收紧 golden 制造误红。
4. **fork 完整性 = 只加同路径不变量**（永久断言）：站点 `layouts/` 与主题 `layouts/` 不得存在同相对路径文件——把 0030 的「文件唯一」决策变成可执行断言，防覆盖层复活。**不建主题目录清单快照**：有意增删都要改快照、维护面大，且漏文件时构建会响亮失败。
5. **纪律 = 逐条变异检验**：六条断言各破坏一次实现（删 no-js 类 / 改 post_meta 格式 / 删菜单项 / rss 塞非 posts 项 / 改 searchbox id / 站点层重建同名文件），确认变红后还原；期望值一律独立字面量（非同义反复）。

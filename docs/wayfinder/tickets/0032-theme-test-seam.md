---
id: 0032
title: 主题层可测试的缝
type: grilling
mode: HITL
status: open
blocked_by: [0027, 0030]
assignee:
map: map-theme-fork.md
created: 2026-10-20
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

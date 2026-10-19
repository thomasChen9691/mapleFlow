---
id: 0018
title: fixture 与测试缝的事实底座
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-product-index-narrowing.md
claimed: 2026-10-19
closed: 2026-10-19
---

## Question

现有测试基建（`tests/fixtures/` 的 bad / data / draft 组织、`tests/assert_product_states.py` 的双构建与 fixture 机制、`tests/assert_sop_pipeline.py` 的 fixture 手法）具体长什么样？要支撑 0019「测试缝形状」的决策，必须先查清：fixture 如何覆盖 Hugo 的 `data/` 与布局、契约用例（构建必须失败）如何构造、真实数据 seam 如何构建，以及——对照 product-index 的输入组合（featured × limit × filters × uid × 空态）——现有机制的能力缺口在哪？

本工单只产事实报告（存 `docs/wayfinder/research/0018-*.md`），不作任何决策。

## Resolution

2026-10-19 · research（AFK，子代理完成）。研究报告：[`docs/wayfinder/research/0018-fixture-test-seam-facts.md`](../research/0018-fixture-test-seam-facts.md)（187 行，全部结论附 文件:行号 证据）。

要点（供 0019 决策直接引用，不替代报告）：

1. **三种构建原语已存在**：fixture 构建 = `hugo.toml,tests/hugo.test.toml` 双 config 叠加、后者仅一行 `dataDir = "tests/fixtures/data"`（tests/hugo.test.toml:5）；坏用例构建 = 运行时动态写 TOML、`dataDir` 直指 `tests/fixtures/bad/<case>`、判定 = 非零退出且输出含「产品状态」（tests/assert_product_states.py:209-213）；真实数据构建 = 生产双 config（:36）。`--quick` 只跳真实数据构建。
2. **现有 fixture 覆盖的是产品状态 2×2**（listed×price 四行、featured 全 false，:41-62）；对照 product-index 输入组合，**只有默认路径一格被逐行断言**，featured 过滤、limit 截断、filters 开/关、uid 多实例、空态、nil 路径均无覆盖（报告 Q4/缺口清单 11 项）。
3. **契约断言语义偏弱**：只匹配 errorf 统一前缀「产品状态」，不钉逐用例子串——强度缺口，SOP 脚本有可复用的 BAD_CASE_EXPECT 手法（对照 docs/wayfinder/research/0001 与 tests/assert_sop_pipeline.py）。
4. **版本 skew 无脚本级适配**：时区钉 hugo.toml:10（Asia/Shanghai），脚本与 CI 均无 TZ 处理；CI 顺序 = Build(--gc --minify) → assert_product_states → assert_sop_pipeline → Deploy，断言步即守门点（.github/workflows/deploy.yml）。
5. **两处需 0019 留意的事实**：产品脚本 build() 不带 `--gc --minify`（与 SOP 脚本、CI 生产命令不同，原因未查实——报告显式标注）；bad/ 目录为产品与 SOP 共享的坏用例空间，按 products.yaml 文件形态归属过滤（:197-204）——新增用例须守此约定。

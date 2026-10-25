id: "0065"
title: 共享 tmp 的所有权：分根还是共用
type: grilling
mode: HITL
status: open
blocked_by: []
map: map-test-harness-convergence.md
created: 2026-10-25
---

## Question

两个 Python 套件都 `rmtree` 同一个 `tests/tmp` 再构建到同名目标目录（`real`）——「必须串行」的约束只有文档（assert_sop_pipeline.py:36-37 的说明），无任何执法；并行跑会互相清目录，且失败模式是令人困惑的半成品断言。本票只决 tmp / scratch 的所有权结构（fixture 数据归属归边界工单，不重叠）。

要决策的面：

1. **分根还是共用**：按套件分根（如 `tmp/site`、`tmp/sop`，capture 的 `tmp/capture` 同规则）还是维持共用 + 某种锁。判据：分根后串行约束是否自然消解（结构消灭约束 vs 文档维持约束）；目录数量增长的可导航性代价。
2. **并行是否定为目标**：并行执行的收益（CI 时长）与代价（runner 资源、失败输出交错后的可读性、Hugo 并发构建的已知行为）——即使本票不实现并行，「分根」是否按可并行设计（为将来留结构）还是严格按当前串行设计（YAGNI）。
3. **dest 命名的归属**：两套件共用 `real` 这个目标名——分根后目标名由 harness 统一生成（套件不再自选）还是各套件自定；同一套件内多构建（站点套件有 fixture 构建 + 真实构建等多次）的 dest 如何编目。
4. **执法**：串行约束若保留，从文档升级为执法的成本（锁文件 / 目录探测报错）值不值；若分根消除约束，是否就没有任何残留的共享状态需要清点（如 `__pycache__`、capture 的 tmp）。

边界（不开票）：fixture 数据（bad/ 目录、fixtures/ 数据文件）的所有权归边界工单；本票只决 tmp 与构建产物目录。

事实前提：`assert_site_contracts.py:1616` 与 `assert_sop_pipeline.py:476`（各自 rmtree TMP）；`:1408` 与 `:247`（构建到同名 dest）；`assert_sop_pipeline.py:36-37`（串行约束文档）；`tests/capture_sop_golden.py` 用 `tests/tmp/capture`。架构评审候选①（共享 tmp 无主权的论断）。

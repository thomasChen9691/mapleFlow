id: "0065"
title: 共享 tmp 的所有权：分根还是共用
type: grilling
mode: HITL
status: closed
blocked_by: []
assignee: agent
map: map-test-harness-convergence.md
created: 2026-10-25
claimed: 2026-10-25
closed: 2026-10-25
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

## Resolution

2026-10-25 · grilling（HITL，项目负责人四问定案；与 0062 同场——经负责人指示的一次会话两票例外，例外已记入地图 Notes）：

**所有权结构（Q1）**：**按套件分根**——`tmp/site/` + `tmp/sop/` + `tmp/capture/`。capture 从「共享空间里的命名约定」升级为真所有权（今日两套件的整树 rmtree 会连 `tmp/capture` 一起端掉）。与 bad/ 拆子根（0061 裁定四）同款哲学：**所有权从约定变为结构**；串行约束自然消解——两套件不再碰彼此的目录。拒绝：共用 + 文件锁（锁残留需清理逻辑、进程被杀后要能恢复，复杂度是搬家不是消灭）；维持文档约束（架构评审已判 load-bearing but unenforced，并行即半成品假红）。

**并行目标（Q2）**：**否——分根备好但 CI 暂不并行**。当前无真实时长需求（两套件各 30–60s、Hugo 构建占大头）；并行留给将来有真实需求时，只差 CI 配置一步。意图记入地图雾区「并行执行的代价面」防未来重复讨论。

**dest 命名（Q3）**：**harness 统一生成**——套件传用途名，harness 拼 `tmp/<suite>/<purpose>`。套件不再自选路径；同用途跨套件不可能相撞；「real」魔法字符串（站点 :914/:1041/:1416、SOP :246）从调用点消失；第三套件零协调成本。拒绝：套件自定（保留魔法字符串，将来再撞名再决策）；不可读唯一名（排障时无法从 dest 名定位用途与套件）。

**残留与执法（Q4）**：**串行约束废除**——SOP 套件 :36-37 的「tests/tmp 独占 / 须顺序运行」文档随分根施工删除。残留清点记录在案、不加锁不分家：`tests/__pycache__` 无害（路径跟着被导入模块的文件位置走、按 mtime 自失效、无法按套件分——逆 Python 机制分行不通）；`resources/_gen`（Hugo 资源缓存）今日已被两套件共享、缓存幂等，分根不改变它。拒绝：保留 capture 文档约束（capture 已有自己的根，约束指向的共享已不存在；capture 写 `fixtures/sop-golden/` 与 tmp 无关）。

**对下游的输入**：0062（tmp 重置归 harness 的入口仪式，本票已定其形状）；0069（迁移时 dest 引用点与串行文档的处置属确定工作项）。

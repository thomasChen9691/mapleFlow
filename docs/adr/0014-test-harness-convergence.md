# 0014 - 测试基建 harness 收敛

**状态**：已批准（2026-10-25，项目负责人经 wayfinder 地图 `map-test-harness-convergence` 工单 0061–0071 逐票 grill 定案）。基线：ADR-0007（三层文档契约模式——本 ADR 是其 harness 侧落地）、ADR-0004（Hugo 0.164 钉版纪律）、ADR-0006（决策 2：不留缺省回落）。过程记录存各工单 Resolution（决策进本 ADR、推理链留工单，两不混）。

## 背景

四个测试套件（`assert_site_contracts.py` 159 条 / `assert_sop_pipeline.py` 104 条 / `assert_reveal.mjs` 23 条 / `assert_search.mjs` 41 条）在扩张中各自长出了同款基建：Report 类与打印汇总退出码、hugo 检查与 tmp 重置、build 包装、fixture 配置手写、jsdom 页面装配、check 与计数器。架构评审（候选①）确认六类重复，其中三类是逐字拷贝（打印块、run 包装、Node 侧 check），三类是形状相同参数不同（build 旗标分歧、配置写入六处、DOM 装配两种模式）。重复的代价不是行数，是**改一处漏一处**与**理由住在拷贝里**。收敛目标：测试运行基建归一个 harness，契约字面量原样独立（independent 是承重设计）。

## 决策

1. **边界判据 = 所有权测试（工单 0061）**：一段重复代码，若其唯一所有者是「测试运行」本身 → 基建，收 harness；若各有其主（两个套件各自持有不同期望） → 契约，留各套件。平分时判**契约**——合并意义会制造隐形跨套件耦合，代价无界无报警；重复机制有界可见。据此裁定六类：BAD_CASE_EXPECT 表与循环、fuse 双执法（源对源 + 字面量互补 pair）、bad/ 坏用例内容判契约；fixture 镜像（无跨套件借用前提）、golden 文件判契约归 SOP 套件。
2. **模块形态 = 一个概念、两个文件（工单 0062）**：语言边界（Python ×2 + Node ×2）强制至少两个文件，「一个 harness 模块」作为概念覆盖——`tests/harness.py`（Report / 入口仪式 / tmp 管理 / build 档位 / 配置写入）+ `tests/dom.mjs`（check / jsdom 页面装配 / 汇总退出），按职责命名。四个入口文件收敛后**只剩「取参数 + 有序断言清单」**；入口仪式（argparse、hugo 检查、tmp 重置、Report 构造、打印块、汇总退出码）全进 harness；排序依赖注释留调用点（清单顺序是套件知识不是基建）。
3. **seam 契约 = 五承诺三禁止（工单 0061/0062）**：harness 承诺——跑构建 / 收报告 / 写 fixture 配置 / 装 DOM 页面 / 管 tmp 根；禁止——知道任何被测模块的词表 / 持有任何契约期望值 / 持有 fixture 数据。契约定义处 = 两份文件头 docstring（唯一定义处）；「harness」词范围 = 测试运行基建；`sop_golden.py` 是并列第三个模块，docstring 双向互指防合并冲动。
4. **tmp 所有权 = 按套件分根（工单 0065）**：`tests/tmp/site/` + `tmp/sop/` + `tmp/capture/`——所有权从约定变为结构，串行约束自然消解（SOP 套件「独占 / 须顺序运行」文档废除）。**dest 归 harness 生成**：套件传用途名，拼 `tmp/<suite>/<purpose>`，「real」魔法字符串不进调用点、跨套件不相撞。**并行执行定为目标 = 否**：分根结构已备好、CI 暂不并行（无真实时长需求），意图记录在案防未来重复讨论。残留清点：`__pycache__`（跟着模块文件走）与 `resources/_gen`（Hugo 缓存）记录在案、不加锁不分家。
5. **坏用例 fixture 按模块拆子根（工单 0061）**：`tests/fixtures/bad/products/` + `bad/sop/`，每根本根卫生断言（错放即红）——与 tmp 分根同款「所有权从约定变为结构」。
6. **构建旗标分歧 = 命名档位 + 显式 extras（工单 0063）**：`harness.build(config, dest, profile, flags)`——`site-contracts` 档 = `--cleanDestinationDir`（故意不 minify，断言要解析带引号属性）；`sop-pipeline` 档 = `--gc --minify --cleanDestinationDir`（与 CI 生产命令逐字一致，golden 按 minify 产物捕获）。档位是套件的属性，经套件级薄适配器绑定（不在约 20 个调用点重复）；逐调用差异（`--contentDir` / `--layoutDir` / `-D`）走 flags。档位 docstring 必须载「为什么是这组旗标」；新档位过双门槛。站点 real 构建的承重不对称（生产配置、故意不 minify、minify 形态归 CI 零 WARN 守门）在 site 档显式声明。
7. **fixture 配置写入 = 一个入口、四轴、全显式无缺省（工单 0064）**：`harness.write_config(name, dataDir, *, contentDir, sopNotesDir, refLinksErrorLevel)`——六处手写写入全迁；「坏用例 / 行为 fixture」是同四轴的不同取值（坏用例 = 只设 dataDir 的最小调用），不拆入口。`root → data/notes` 映射留 SOP 套件（fixture 布局约定是套件知识，harness 不懂内容布局）。宽度上限 = 四轴，新轴须带新消费者并过 deletion test。两条既有坑（路径必须 as_posix 相对化 / dataDir 禁混 .md）随入口内聚为一处文档。
8. **harness 自测 = 独立双文件、只测牙临界（工单 0066）**：`tests/assert_harness.py`（19 条）+ `tests/assert_harness.mjs`（8 条）；间接覆盖判据 = 破坏该行为时现有套件是否可定位地红（check 的 verdict 记录不达标——已实证静默假绿，故必测）。自测**独立记账**（不复用被测的 Report/check——复用即同义反复）；期望值独立字面量；每条以变异检验证牙；自测文件禁存被测模块契约字面量。入口：`npm test` 扩链（mjs 自测先跑）+ CI verify 加一步（harness 红先于契约红，失败定位前移）。
9. **文档 seam = docstring 唯一定义处 + 导航随施工批落地（工单 0067）**：批准两份文件头 docstring 为契约唯一定义处（ADR-0007 三层模式的 harness 侧落地：概念层不入术语表 + docstring 唯一定义 + 自测承载期望字面量）。「harness」**不入 CONTEXT.md**（术语表是对外领域语言）。AGENTS.md 三处落点：§7 速查两行（契约定义处 + 消费方）、§3 命令区述不变性（npm test 扩链在 package.json）、§4 坑点 16（harness 五条硬约束）。
10. **版本预检 = 留站点套件 + glob 修正 + advisory（工单 0068）**：预检曾因 `CI_WORKFLOW` 常量钉死已改名的 `deploy.yml` 而静默失效（read_text 走 OSError 静默返回——预检已死一轮）；复活方式 = glob 全部工作流并收集钉版集合（多工作流钉不同版本不静默取第一）。留站点套件（SOP 套件断言与 Hugo 版本无关，WARN 对它无信息量；harness 收它违双门槛）。维持 advisory WARN（不进断言计数、不影响退出码——skew ≠ 产物错，硬失败误伤新版 hugo 用户）。
11. **golden 工具链 = 并列第三模块，--check 不接 CI（工单 0070）**：`sop_golden.py`（golden 抽取 / 规范化 / 生产构建捕获）与 harness 并列，接缝 = docstring 互指 + capture 只走 `tmp_root`；`build_real` 留 sop_golden（生产配置直捕是内容工具关注点）。`capture_sop_golden.py --check` **不接 CI**：其覆盖与 SOP 套件的 golden 比对重叠（漂移侧有牙），独特覆盖（捕获路径自身）与 assert 共用同一模块、对共享 bug 双盲——记录为已知限制（ADR-0010 先例）。

## Considered Options

- **两文件同干命名（harness.py + harness.mjs）**（决策 2，拒绝）：暗示两侧契约对称，实际不对称（Python 侧吸收入口仪式六件、Node 侧只有 check/计数/装配）。
- **tmp 共用 + 文件锁**（决策 4，拒绝）：锁残留需清理逻辑、进程被杀后要能恢复——复杂度是搬家不是消灭；维持文档约束亦拒（评审已判 load-bearing but unenforced）。
- **build 档位按套件隐式推断**（决策 6，拒绝）：隐式推断让 capture 等非 run 消费者不可用，档位知识藏进推断逻辑。
- **root→轴映射进 harness**（决策 7，拒绝）：harness 开始懂 SOP fixture 目录布局（内容语义），正是 seam 三禁止禁的浑浊；且站点侧消费方不用 root 形态。
- **harness 自测并入现有套件首组**（决策 8，拒绝）：harness 测试与契约断言混报，定位优势减半；只本地不挂 CI 亦拒（advisory 化重蹈预检覆辙）。
- **版本预检进 harness / 撤掉 / 推给候选⑤**（决策 10，均拒）：进 harness 给零信息量消费方加宽接口；撤掉失去「提交前提醒 0.166+ 陷阱」的软牙；候选⑤是配置/CSS 死面批处理，与预检需要的 glob 修正不同域不同动作。
- **golden 吸收进 harness / 拆半**（决策 11，均拒）：吸收违 seam 三禁止；拆半（build_real 进 harness）制造两个构建入口。
- **决策集拆多份 ADR**（拒绝）：四条决策互相咬合（seam 禁止项是纳入判据的前提），拆开割裂推理链；ADR 库一主题一篇的形态也支持总纲。

## Consequences

- 测试运行基建收敛为一个 harness 概念（`tests/harness.py` + `tests/dom.mjs`）；四个入口文件读起来像规格清单；六类重复清零（含三处逐字副本：打印块、run 包装、Node 侧 check）。
- **纳入判据耐久化**：任何新基建能力进 harness 须过双门槛——≥2 消费者 + deletion test（删掉它复杂度是集中不是搬家）；无消费者预期的入口不留（ADR-0006 决策 2 同款）。
- **迁移记录（工单 0069）**：实际切法 = 按基建能力分层横切，三批施工（`e08eb06` harness 模块 / `42ba094` bad/ 拆子根 / `cd531ea` 档位+入口+自测+预检+文档），批批全绿中间态；断言计数三批持平（site 159 · sop 104 · npm 23+41，净新增仅 bad/ 两条卫生断言），变异等价逐批证实。
- **已知限制（诚实入档）**：① `--check` 不接 CI（决策 11 的覆盖分析）；② 并行执行非目标（决策 4）；③ 预检是软牙（决策 10，by design）；④ 本图全部提交（本地分支 `refactor/harness-convergence`：`6620eb0` chart → `42ba094` bad/ 拆子根 → `90a46e4` 两票决议 → `e08eb06` harness 模块 → `4adc239` 六票决议 → `cd531ea` 六票施工 → `e78930a` 0069/0071 决议 → 收口批（本提交））**未推、PR 未开**（GitHub auth-required；笔数以 `git log --oneline refactor/harness-convergence` 为准）；收口不等 CI（分支规则集即 PR 硬门禁），状态与下一步见 handoff `2026-10-25-harness-convergence-closure.md`。基点的可视批 4 笔已在 `origin/style/css-modern-batch`（另一远程分支，未并 main）。
- **指针（本 ADR 收口时落）**：AGENTS.md 坑点 16 补引本 ADR 编号；CONTEXT.md 不碰（决策 9）；先前文档不改（历史记录，指针行是先例）。

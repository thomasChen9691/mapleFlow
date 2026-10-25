# 交接：测试基建 harness 收敛收口（2026-10-25）

> 决策与契约不在此重述，按需取：**ADR-0014**（harness 收敛决策集，十一条各注工单号）· wayfinder 地图 `docs/wayfinder/map-test-harness-convergence.md`（已 closed，11 票 Resolution 留推理链）· **AGENTS.md** §3/§4 坑点 16/§7（命令、harness 五条硬约束、两模块速查行）· `tests/harness.py` 与 `tests/dom.mjs` 文件头 docstring（seam 契约唯一定义处）。本文只记当前状态、下一步、环境坑与建议 skill。

## 当前状态

- **地图已收口**：`map-test-harness-convergence` 11/11 票全部 closed，frontier 空，决策面走完；收口三产出齐备——ADR-0014（`docs/adr/0014-test-harness-convergence.md`）、本 handoff、地图状态置 closed 且 Decisions 索引并拢 ADR 指针。
- **分支与 PR**：`refactor/harness-convergence` **全部提交未推、PR 未开**（GitHub 连接器 auth-required；共 8 笔，以 `git log` 为准）：`6620eb0` chart → `42ba094` bad/ 拆子根 → `90a46e4` 0062/0065 决议 → `e08eb06` harness 模块（0062/0065 施工）→ `4adc239` 六票决议 → `cd531ea` 六票施工（0063/0064/0066/0067/0068/0070）→ `e78930a` 0069/0071 决议 → 收口批（本提交）。**收口不等 CI**（0071 决议：分支规则集把 verify 设为 PR 硬门禁，开 PR 时自然产生证据）。基点的可视批 4 笔已在 `origin/style/css-modern-batch`（另一远程分支，未并 main——其 PR 亦未开，见该批 handoff）。
- **验证基线（收口文书核对，非重跑）**：site 159/159 · sop 104/104 · harness 自测 py 19 + mjs 8 · npm test 8+23+41 · capture --check 6 same · 预检 WARN 正常（本机 0.167 vs CI 钉 0.164，advisory）。断言计数与迁移前基线持平，净新增仅 bad/ 两条卫生断言；变异等价逐批证实（各施工批提交信息有录）。
- **形态一句话**：harness = 一个概念两个文件（`tests/harness.py` Report/入口仪式/tmp 分根/build 档位/配置写入四轴 + `tests/dom.mjs` check/finish/installDom/installPage/loadFresh）；四个入口只剩「参数 + 有序断言清单」；自测独立双文件先于契约断言红。
- **决策速览（十一条一句话，全文以 ADR-0014 为准）**：① 边界判据 = 所有权测试，平分判契约；② 一个概念两个文件（harness.py + dom.mjs），入口只剩参数 + 断言清单；③ seam 五承诺三禁止，docstring 唯一定义处；④ tmp 按套件分根、dest 归 harness、串行约束废、并行非目标；⑤ bad/ 按模块拆子根 + 每根卫生断言；⑥ build 命名档位 + 显式 extras，档位是套件属性；⑦ 配置写入一入口四轴全显式，root 映射留套件；⑧ 自测独立双文件只测牙临界，npm test 扩链 + CI 一步；⑨ 「harness」不入 CONTEXT.md，AGENTS.md 三落点随施工批；⑩ 预检留站点套件 + glob 修正 + advisory；⑪ golden 并列第三模块，--check 不接 CI。

## 下一步

1. **唯一待办（用户侧）**：恢复 GitHub 授权 → `git push -u origin refactor/harness-convergence` → 开 PR → 门禁绿 → squash 合并 → 删远端分支、本地 `git pull`。PR 描述可引 ADR-0014；门禁含新增的 `Assert harness self-test` 步（0066 决议）。
2. **合并后预期**：gh-pages 会推进（本批改的是 tests/ 与文档，站点产物本身无 diff——与 docs-only PR #1 同类，但 verify 全链会跑）。
3. **可选后续（非紧急）**：`style/css-modern-batch` 的 PR 亦未开（可视批 handoff 有述）；两分支的 PR 顺序无依赖，可并行开。

## 环境坑（本会话新增，历图传承之外）

- **safe-delete 每轮删除预算 5000**：一轮 bash 会话内累计删除超限后，套件的 `rmtree(tmp)` 被 broker 拦截（SOP 全量末跑被拦过一次）——不是代码故障，新开命令即恢复。
- **单命令进程数上限**：一条命令里约第 6 个 node 进程会被 kill（137）——变异测试分批跑，别把十次运行串一条命令。
- **execFileSync 嵌套 spawn 偶发被 kill**：node 父进程 spawn node 子进程在本沙箱不稳定（曾致自测假红）——harness mjs 自测因此改为**零子进程**的进程内观测（ExitSignal 抛掷桩 + loadFresh 自加载）；新写测试优先进程内。
- **shell grep 对 `\|` 交替失效**：内容搜索一律用 Grep 工具（历图传承，本会话又踩三次）。
- **Hugo skew WARN 是正常态**：本机 0.167 vs CI 钉 0.164，套件启动打 WARN 不影响退出码（0068 决议的 advisory 定位）。

## 建议 skill

- **realeng-grilling**：本图全程用它把 11 张工单逼到非黑即白（一次一问、推荐先行、事实自查后问决策）——下张地图开图照例。
- **realeng-code-review**：每批施工收尾的双轴评审（Standards/Spec）——本图三批施工各抓出真问题（docstring 漂移、死导入、路径字面量），照例。
- **realeng-tdd**：施工批的红绿循环 + 变异检验——文档批的变体是「声明先对树验证后写入」（本批 ADR 11 条决策逐条验树，抓出 package.json 描述漂移）。

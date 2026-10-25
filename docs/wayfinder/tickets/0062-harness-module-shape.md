id: "0062"
title: harness 模块形态：Python 侧与 Node 侧各是什么、落在哪
type: grilling
mode: HITL
status: closed
blocked_by: ["0061"]
assignee: agent
map: map-test-harness-convergence.md
created: 2026-10-25
claimed: 2026-10-25
closed: 2026-10-25
---

## Question

边界判定的产出（哪些重复是基建）之后，定 harness 的模块形态：两侧各自的模块是什么、落在哪、四个入口文件因此变成什么形状。

要决策的面：

1. **模块数量与落点**：语言边界强制至少两个模块（Python 侧 / Node 侧）。Python 侧一个（如 `tests/harness.py`）吸收 Report / 构建 / fixture 配置写入 / 预检；Node 侧一个（如 `tests/dom.mjs`）吸收 check / 页面装配——这个二拆是否成立；两侧是否同名同责（对照分层纪律：站点层与主题层不得同相对路径的先例，测试目录内同名是否造成导航混淆）。
2. **入口文件的剩余形状**：四个套件（assert_site_contracts.py / assert_sop_pipeline.py / assert_reveal.mjs / assert_search.mjs）收敛后各自剩什么——只剩契约字面量与用例编排，还是仍保留套件级 setup；判断「薄得恰当」的标准（不是越薄越好：编排逻辑留套件还是进 harness）。
3. **harness 自身的浅模块风险**：harness 是基建的集中地，最可能犯的病是接口≈实现。宽度判据是什么——deletion test（删掉 harness 是集中复杂度还是转移复杂度）、每个入口的消费者数（leverage：一个入口几处消费才值得）；哪些能力明确不进 harness（避免为「以后可能用」撑宽接口，对照 ADR-0006 决策 2「不留注入位」先例）。
4. **与 sop_golden 先例的关系**：sop_golden.py 是现成的共享模块（capture 与 assert 都 import）——harness 与它是并列两个模块还是吸收关系；「harness」这个词覆盖的范围（仅测试运行基建，还是含内容 fixture 工具链）。

边界（不开票）：构建旗标分歧的表达归构建工单；配置写入的参数面归写入工单；harness 文档 seam 归导航工单——本票只定「有几个模块、各在哪、入口变什么形」。

事实前提：以边界工单决议为准（未决时本票阻塞）；架构评审候选①的重复盘点（行号锚点见边界工单）。

## Resolution

2026-10-25 · grilling（HITL，项目负责人四问定案；与 0065 同场——经负责人指示的一次会话两票例外，例外已记入地图 Notes）：

**模块数量、落点与命名（Q1）**：语言边界（Python ×2 + Node ×2）强制至少两个文件，「一个 harness 模块」作为**概念**覆盖，不为单文件幻觉拆队。落点与命名 = **`tests/harness.py` + `tests/dom.mjs`，按职责命名**：

- `tests/harness.py`（Python 侧）：Report 类 + 打印 / 汇总 / 退出码 + hugo PATH 检查 + tmp 重置 + build（旗标档位归 0063）+ fixture 配置写入（参数面归 0064）
- `tests/dom.mjs`（Node 侧）：check + 计数 / 汇总 / 退出 + installDom / loadFresh

拒绝：同干命名 `harness.py` + `harness.mjs`（暗示两侧契约对称，实际不对称——Python 侧吸收入口仪式六件、Node 侧只有 check / 计数 / 装配）；Node 侧不立模块（违背目的地；第三个 jsdom 套件出现即复制第三份）。

**入口剩余形状（Q2）**：四个入口文件收敛后**只剩「取参数 + 有序断言清单」**。入口仪式——argparse `--quick` / hugo 检查 / rmtree+mkdir / Report 构造 / **打印块（当前两套件逐字重复，评审未点名的第三处副本）** / 汇总与退出码——全进 harness。排序依赖注释留调用点（站点 main :1639-1644 的注释证明顺序承重：清单顺序是套件知识，不是基建）。拒绝：入口自拼装（拼装代码仍是两份逐字重复，收敛只做一半）；声明式断言注册表（清单是编排逻辑，把 seam 变成配置 = ADR-0006 决策 2 枪毙的模式）。

**纳入判据与宽度防护（Q3）**：双门槛——每个纳入物须同时满足 **≥2 个消费者（leverage）+ deletion test（删掉它，复杂度是集中而不是搬家）**；无消费者预期的入口不留（ADR-0006 决策 2 同款）。明确在外：契约字面量与 fixture 数据（0061）、预检（归 0068 未决）、golden 工具链（归 0070 未决——`sop_golden.py` 自带 `build_real` 是 golden 捕获用的生产配置构建风味，进 harness 等于让 harness 懂内容语义，正是 0061 禁过的浑浊）。

**seam 契约与测试存活（Q4，全部确认）**：

- **seam 之后只有机制**：harness 对四个消费方承诺五件事——跑构建 / 收报告 / 写 fixture 配置 / 装 DOM 页面 / 管 tmp 根；禁止三件事——知道任何模块的词表、存任何期望值、存任何 fixture 数据（0061 约束① 在本票形状下的具体化）。四套件的契约字面量原样独立。
- **「harness」词范围 = 测试运行基建**；sop_golden 为并列第三模块（工具关系归 0070）；harness docstring 须提及 sop_golden 的存在（防未来合并冲动）。
- **测试存活**：本票不合任何行为，现存断言全存活、无搬家；harness 自身如何被测归 0066。

**对下游的输入**：0063（旗标档位落在 harness 的 build 内）、0064（配置写入的参数面）、0065（tmp 分根后重置归 harness）、0066（自测对象 = 本票五承诺）、0067（导航两行 + docstring 提及 golden）、0068（预检若接管则进 harness.py）。

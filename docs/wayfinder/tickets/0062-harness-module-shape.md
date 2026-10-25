id: "0062"
title: harness 模块形态：Python 侧与 Node 侧各是什么、落在哪
type: grilling
mode: HITL
status: open
blocked_by: ["0061"]
map: map-test-harness-convergence.md
created: 2026-10-25
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

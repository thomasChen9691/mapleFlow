# 交接：候选 12「搜索入口」闭环（六票全 closed，ADR-0011，施工三批，未推）

> 本文只记本批终态、决策落点与去向，不重述 `CONTEXT.md` / `docs/adr/` / 工单已有内容。
> 工单体（含每票的完整 Resolution 与施工期补记）在 `docs/wayfinder/tickets/0049-0054*.md`；事实底座在 `docs/wayfinder/research/0049-search-entry-facts.md`。

## 当前状态

- **候选 12 全闭环**：地图 `docs/wayfinder/map-search-entry.md` 已 closed；工单 0049（事实底座 research）-0054 全 closed；决策耐久化于 **ADR-0011**（四组：入口形态含重评结论 / 呈现层 / 模块边界 / 测试缝含所有权分层原则）。指针三笔已落：ADR-0010 两笔（第二个消费方重评结论留痕 + 快照扩写说明）、ADR-0007 一笔（入口交互不归 reveal 的边界闭合）、ADR-0008 轻笔（站点层交互引擎两例备注）。
- **施工三批，均 TDD + 变异检验 + 双轴 code-review 后单独提交**：`261b17b` 入口批（`assets/js/mf-search-entry*.js` 站点层双文件、extend_footer 双 js.Build + `@params` 注入、header accesskey 退役、`tests/assert_search.mjs` 13 行为 + 产物断言 5 条、npm test 双串联）；`3f1aee3` 呈现与契约批（fastsearch.js 渲染 `item.summary` + docstring 三笔 + 互指指针 + 弱产物断言）；本收口批（ADR-0011 + CONTEXT.md「搜索入口」条 + AGENTS.md 三笔含坑点 14 + deploy.yml 三处注释修正 + handoff + backlog 第 12 项完成 + 地图 closed）。
- **验证**：三套测试全绿（assert_site_contracts 87 / npm test 29 / assert_sop_pipeline 104）；新断言 10/10 变异捕获；呈现层「渲染结果正确」由一次性 jsdom 验证覆盖（驱真实构件 + 真实索引跑完整 fuse 链路 5/5，脚本未提交、结论在 0051 施工期补记）；生产构建零 WARN、无 localhost:1313。
- **未推**：三批提交（`261b17b` / `3f1aee3` / 收口批）均在本地 main。GitHub 连接器 auth-required——**推送与 CI 验证待项目负责人恢复连接后执行**；推后预期 CI 十步全绿（npm test 与 assert 步骤的内容本批只改注释，无逻辑变动）。
- **工作区干净**（`.workbuddy-ai/` 已被 .gitignore 挡住，backlog 第 1 项的防线仍在）。

## 下一步

1. **推送三批提交**（负责人恢复 GitHub 连接后）：CI 应全绿；若有红，优先怀疑 Hugo 0.164 上 `@params` import 的兼容性（本机 0.167 实证可用、0.162-0.168 发布日志无相关变更，但 CI 是权威）。
2. **backlog 第 13 项**（精选三条雾区）：唯一挂起的决策项，需先排地图再动工——其性质与候选 12 相同（目的地未定），可复用本次「research 工单开路 → grilling 分票 → 施工分批」的节奏。
3. **视觉批**（不在本图范围）：摘要行 `.entry-summary` 目前走默认文档流（可用但无样式）；字号 / 行数 / 截断归视觉层调值。search.css 的 `#searchResults li` 既有规则仍兼容（点击热区随 li 增高自动覆盖，已验证）。
4. **三条雾区随地图挂起**（移动端形态 / aria 细节 / 浮层空间关系）：触发条件写在 closed 地图的 Not yet specified——触屏流量出现或重开浮层形态时，由新图继承，勿从 closed 地图直接复工单。
5. **若将来重开「首页常驻框 / 浮层」形态**：那将引入 fastsearch 的第二个加载页面 = ADR-0010 第二个消费方，须先过该 ADR 决策 5 的重评路径；本次的加载面双向断言（fixture + real）就是那条路的守门。

## 建议 skill

- **realeng-wayfinder** — 第 13 项开图前先排地图（目的地先行、工单是待决策问题）。
- **realeng-grilling** — 决策项访谈（一次一问、先给推荐答案；本次六票的「场景乙」「所有权分层」等判断均是该模式产出）。
- **realeng-tdd** — 施工批次（红先绿后、一次一行为；本图两批施工 + 收口批均走此循环）。
- **realeng-code-review** — 收口前双轴评审；本图三批各抓 2-3 处（枚举漂移 / frontier 过期 / 单文件偏离未回写 / 括号写法绕逃 / 人工验证缺记录），全部落地修复。
- **环境注意**：① 本 shell 的 grep 对 `\|` 交替失效，用 Grep 工具；② `gh` 未安装，查 CI 用 `curl` + GitHub API（logs 需 admin）；③ Hugo `js.Build` params 是 **ESM import（`@params`）不是全局**——排图期曾按旧 fastsearch 的裸 `params` 写法误判，施工期实证推翻；④ CI 中 `npm test` 先于 hugo 构建——常驻行为测试必须保持 hugo 无关（只测源码）；⑤ 今日沙箱中 Write 工具对长 content 偶发丢参数——子代理与研究产物曾因此改道（子代理只输出正文、主代理 Bash heredoc 分段落盘）；若复现，优先怀疑参数序列化而非提示词。

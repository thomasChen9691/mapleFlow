# 交接：精选类型守卫单模块收口（2026-10-26）

> 决策与契约不在此重述，按需取：**ADR-0015**（`docs/adr/0015-featured-type-guard.md`，15 条决策各注工单号）· 地图 `docs/wayfinder/map-featured-type-guard.md`（已 closed，7 票 Resolution 留推理链）· **AGENTS.md** §7 速查行 / 坑点 9·11 · `layouts/partials/featured-guard.html` 文件头 docstring（执行契约唯一定义处）· `docs/wayfinder/research/0072-featured-guard-facts.md`（事实底座）。本文只记当前状态、下一步、环境坑与建议 skill。

## 当前状态

- **地图已收口**：`map-featured-type-guard` **7/7 票 closed**（0072 事实底座 / 0073 边界 / 0074 接口 / 0075 落点 / 0076 消息命名 / 0077 测试缝 / 0078 收口），frontier 空，目的地到达。决策集耐久化于 **ADR-0015**；ADR-0009 / ADR-0012 各加指针行（正文不改）。
- **分支与 PR**：`refactor/featured-guard-module` 基于 `refactor/harness-convergence` 尖（含其未推提交），共 4 笔、**全部未推**（GitHub auth-required；笔数以 `git log` 为准）：`a1202e8` docs（图 + 0072/0073 + 24 张工单围栏修复）→ `c8725e8` refactor（守卫模块 + 三处迁移 + 四处指针 + AGENTS 同步）→ `7a01618` docs（0074–0077 Resolution + 地图）→ `2cf3d2a` test（SOP 缺口 + docstring/术语同步）。**PR 时注意基数**：harness 分支（`refactor/harness-convergence`，自 main 起 13 笔——含基点可视批 4 笔）的 PR 亦未开。
- **验证基线**：site **159/159** · sop **105/105** · npm test **8+23+41**（harness 自测 + reveal + search）· 生产构建**零 WARN** · **无 localhost 泄漏**。变异：禁用守卫类型检查 → 四条坏值断言同红（site 156/159 + sop 104/105）。
- **形态一句话**：featured 类型守卫 = 一个站点层 partial（`layouts/partials/featured-guard.html`），条目语义（`item` 容器进、四件套全收敛、遍历留调用方），只做类型校验（不选择/不取数/不渲染/不持措辞），消息三前缀由调用方经 `origin`/`label` 逐字传入。

## 决策速览（十五条一句话，全文以 ADR-0015 为准）

- **0073**：① 边界 = 只做类型校验（谓词判契约，各有其主）；② 文档双向互指（模块 docstring = 执行契约唯一定义处）；③ 边界文本 = 校验器不是选择器/取数器；④ 测试零增减零改写（SOP 缺口留 0077）。
- **0074**：⑤ 条目语义（四件套全收敛、遍历留调用方）；⑥ 不自校验（内部模板接口）；⑦ 无返回（纯执法）。
- **0075**：⑧ 站点层（ADR-0008；徽标不消费 → 零 theme→site 新先例）；⑨ 记重开触发（徽标谓词收敛或主题层消费方 → 重开分层决策）。
- **0076**：⑩ 保留 origin 三前缀（逐字、零 churn、链身份不丢）；⑪ label 归调用方格式化（定位值不是措辞）；⑫ `featured-guard.html` 定案 + 术语表不收「守卫」+ CONTEXT.md 加指针。
- **0077**：⑬ 各消费链测试缝（测公开行为，不建探针）；⑭ 补 SOP 坏值 fixture（104→105）；⑮ ADR-0014 自测模式不适用（模板侧无等价 seam，已知差异）。

## 下一步

1. **恢复 GitHub 授权** → `git push -u origin refactor/featured-guard-module` → 开 PR（描述可引 ADR-0015）→ 门禁绿 → **squash 合并**（规则集仅允许 squash）→ 删远端分支、本地 `git pull`。
2. **基数注意**：本分支基于 `refactor/harness-convergence` 尖——该分支自 main 起 13 笔（含基点可视批 4 笔）亦未推、PR 未开。建议先合 harness 分支的 PR，再让本分支 rebase 到 main 后开 PR（避免 PR 里混入 harness 提交）。
3. 合并后预期：本批只改 `layouts/partials/`、`content/posts/_content.gotmpl`、`tests/`、`docs/`——站点产物本身有精选守卫的行为等价，gh-pages 推进但页面 diff 应仅限注释/无。

## 环境坑（本图新增，历图传承之外）

- **shell grep 对 `\|` 交替失效**：内容搜索一律用 Grep 工具（本图又踩两次）。
- **safe-delete 每轮删除预算 5000**：一轮内多次跑套件可能被 broker 拦 `rmtree(tmp)`——不是代码故障，新开命令即恢复。
- **单命令进程数上限**：一条命令里约第 6 个 node 进程会被 kill（137）——变异测试分批跑。
- **Hugo skew WARN 是正常态**：本机 0.167 vs CI 钉 0.164，套件启动 WARN 不影响退出码（advisory）。
- **npm test 链**：`assert_harness.mjs` → `assert_reveal.mjs` → `assert_search.mjs`（8 + 23 + 41）。

## 建议 skill

- **realeng-tdd**：纯重构的 TDD 变体 = 现有断言为 oracle、逐切片变异证「切片确经模块」；文档批的变体 = 「声明先对树验证后写入」（本图两次抓出事实漂移：决策条数 11→14、交接份数 11→17）。
- **realeng-code-review**：每批收尾双轴评审（Standards/Spec）——本图三批施工各抓出真问题（docstring 测试段过期、期望子串偏弱、CONTEXT.md 同句重复）。
- **realeng-grilling**：下张地图开图照例（一次一问、推荐先行、事实自查后问决策）。
- 无需 wayfinder 操作：本地图已 closed；开新工作先开新地图，勿往已闭图里加票。

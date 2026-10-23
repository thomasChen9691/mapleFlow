# 交接：候选 13「精选雾区」闭环（六票全 closed，ADR-0012，决策面收口，未推）

> 本文只记本批终态、决策落点与去向，不重述 `CONTEXT.md` / `docs/adr/` / 工单已有内容。
> 工单体（含每票完整 Resolution）在 `docs/wayfinder/tickets/0055-0060*.md`；事实底座在 `docs/wayfinder/research/0055-featured-fog-facts.md`。

## 当前状态

- **候选 13 全闭环（决策面）**：地图 `docs/wayfinder/map-featured-fog-zones.md` 已 closed；工单 0055（research 事实底座）-0060 全 closed；决策耐久化于 **ADR-0012**（五组：语义边界 / 徽标三面 / 数据条负向 / 分类页负向 + seam 收紧 / meta 负向）；**ADR-0009 加指针行**（三条雾区定案留痕，正文不改）。
- **三批落地**：`29f9304` 开图批（地图 + 工单 0055-0059 + research/0055 + backlog/README 指针）；`ba5e696` 质询批（0056/0057/0058 Resolution + 0060 毕业 + 索引更新）；**本收口批**（ADR-0012 + 0009 指针 + CONTEXT 术语 + AGENTS 坑点 11/§7 + post-items docstring 收紧 + backlog 完成 + 本 handoff + 地图 closed + 0059/0060 Resolution）。
- **质询七问**（项目负责人，grilling 一次一问全决）：Q1 语义边界 = 分层默认；0056 = 做三面 + 主题层 partial + fixture 三面锚；0057 = 不做；0058 = 不做 + docstring 收紧；0060 = 不做；0059 = ADR-0012 + 术语只扩徽标面。
- **验证**：`python3 tests/assert_site_contracts.py` 全绿（收口批含 post-items.html docstring 注释改动，零逻辑；套件头版本 WARN 为 Hugo 0.167/0.164 skew 提醒，非失败）。生产构建未跑（纯文档 + 注释改动，不影响产物）。
- **未推**：三批提交均在本地 main（GitHub 连接器 auth-required）——连同候选 12 三批，待负责人恢复后一并推送过 CI。

## 下一步

1. **推送并过 CI**（负责人恢复 GitHub 连接后）：预期全绿；docstring 注释级改动若红，优先怀疑环境而非逻辑。
2. **施工批（待指示）**：ADR-0012 Consequences 已列——`themes/maplemod/layouts/partials/featured-badge.html` partial + `single.html`/`list.html`/站点 `index.html` 三处调用 + fixture 三面断言（挂 `tests/assert_site_contracts.py` 文章精选类）+ 变异检验；**视觉值（颜色/字号/图标）归视觉层**。施工前先跑 `python3 tests/assert_site_contracts.py`。
3. **backlog 剩余**：第 11 项（fastsearch 重写）长期挂起（触发条件见 ADR-0010）；内容填充三项（buy_url/listed、about.md、socialIcons）卡用户材料。
4. **候选 12 遗留**：三条雾区（移动端 / aria / 浮层空间）随 closed 地图挂起，触发条件见 `map-search-entry.md` 注记，勿从 closed 地图直接复工单。

## 建议 skill

- **realeng-tdd** — 施工批次（红先绿后、一次一行为；徽标断言建议一次一面：single → list → 首页网格）。
- **realeng-code-review** — 收口前双轴评审；重点预判：三处调用点的谓词一致性、fixture 期望值独立字面量。
- 环境注意：① 本 shell 的 Write 工具对长 content 偶发丢参数（本日复现）——子代理只输出正文、主代理 bash heredoc 分段落盘；② grep 对 `\|` 交替失效，内容搜索用 Grep 工具；③ Hugo 默认不发布未来日期内容，fixture 日期一律过去日（坑点 12）；④ CI 中 `npm test` 先于 hugo 构建，常驻行为测试须保持 hugo 无关。

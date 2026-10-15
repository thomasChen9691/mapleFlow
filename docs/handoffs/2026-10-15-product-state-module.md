# 交接：产品状态模块深化（2026-10-15）

## 当前状态

- 候选 1「产品状态推导收敛」全链路闭环：wayfinder 地图 6 工单全 closed（`docs/wayfinder/map-product-state-convergence.md`）、决策定案于 `docs/adr/0004-product-state-module.md`、术语在 `CONTEXT.md`（产品状态）。
- 实现共 6 个 commit 在本地 `main`（`fe27508` → `39f4c9b`，TDD 5 循环 + 评审修复 1），**全部未 push**（ahead of `origin/main` 35 个 commit）。`python3 tests/assert_product_states.py` 14/14 绿；生产构建命令未动（ADR-0001 只做加法）；首页显示「0 份可下载产品」符合工单 0004 裁决。
- **唯一未决事项**：`fe27508`/`0e5de50`/`0178481`/`f0e1cf6` 四条 commit message 含中文，违反 AGENTS.md §6 纯 ASCII 规范。重写方案已备（backup 分支 + cherry-pick replay + 逐条 amend message，树哈希前后可验证一致、内容零变更），**等项目负责人批准后执行**——项目规则要求历史重写前须确认。批准并执行后才谈 push。
- 工作区既有噪音，勿动：`CLAUDE.md` 行尾 diff、`themes/PaperMod` 子模块标记、根目录一批未跟踪的历史中文名 md 文档。

## 下一步

1. **用户裁决 commit message 重写**：获批则执行 replay，用 `git log --oneline` + 提交前后树哈希双验（本环境 Bash 工具链式命令的显示层会出幽灵「no changes added」——提交后必须独立验证，不信回显）。
2. **push**：重写完成且用户放行后执行（35 个 commit，触发 CI 的部署 + 新增的断言步）。
3. **架构深化若继续**：候选 2~6、8 的勘察结论目前只存在于临时目录的评审 HTML（`architecture-review-20261015-1736.html`，会被清理）——继续前先把它拷进仓库或重跑 improve-codebase-architecture。优先级建议：候选 2（SOP 文与源笔记 1250 行手抄副本零同步）> 候选 3（后端四层静默失败）> 候选 4（product-index dict 接口泄漏）。
4. **已 ratified 未实施**：候选 7 文章 featured 字段（方向用户已裁决：给文章加 featured，首页「精选文章」区块改真精选）；UI 文案术语收尾（`content/products.md` 6 处「资源」、首页 hero 标签）——后者是把 CONTEXT.md 术语纪律贯彻到表示层，随时可做。
5. **产品真上架时**：`data/products.yaml` 逐条填真实 `buy_url` 且同时 `listed: true`（契约执法两者必须同步）；首页计数自动转真，无需改模板。

## 建议 skill

- **realeng-tdd** — 任何新行为继续红绿循环：一次一个行为、先红后绿、每轮单独 commit。
- **realeng-code-review** — 每批结束跑双轴评审（固定点取上一批首个 commit；spec 源在 `docs/wayfinder/` 与 ADR）。
- **realeng-improve-codebase-architecture** — 选下一个候选前重跑（旧报告在临时目录，不持久）。
- **realeng-grilling** — 遇决策点一次一问，先给推荐答案；事实自己查，决策问用户。
- **realeng-domain-modeling** — 新术语当场进 `CONTEXT.md`（AGENTS.md §9.4 纪律），不攒批。

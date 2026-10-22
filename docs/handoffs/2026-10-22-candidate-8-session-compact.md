# 交接：候选 8「搜索契约」会话压缩（排图 → 七票闭环 → push/CI 全绿，2026-10-22 终态）

> 地图关闭时的决策/施工明细见同日的 `2026-10-22-candidate-8-closure.md`；本文只记会话终态与去向，不重述 CONTEXT.md / ADR / 工单已有内容。

## 当前状态

- **候选 8 全程闭环并已上线**：地图 `docs/wayfinder/map-search-contract.md` closed，工单 0042-0048 全 closed，决策耐久化在 `docs/adr/0010-search-contract.md`（两个契约定义处、字段冻结、kind 门禁、测试缝的完整形态见该 ADR 与两份 docstring，此处不重述）。
- **提交与推送**：三笔已 push——`943e41b`（0043 决议 + 投影契约施工）→ `49ec9ac`（0044/0046 决议 + 同场施工，含项目级 fastsearch 覆盖层合并删除）→ `29cfa0a`（0045/0047/0048 收口 + ADR-0010 + AGENTS 导航）。origin/main 与本地一致（`530f375..29cfa0a`）。
- **CI 全绿**：Deploy run **39807946562**（run 24，head=29cfa0a）十步全 success（npm test / hugo build / assert_site_contracts / assert_sop_pipeline / 部署 gh-pages）；后续 pages build and deployment 亦 success。注意 CI 单套断言仅 ~2 秒——本站 hugo 全构 ~65ms，非异常。
- **线上抽查通过**：`index.json` 17 条全为六字段、5 条产品条目锚点为 `/mapleFlow/products.html#<id>`（子路径正确）；`search.html` preload 同目录 `index.json`、引用 `search.*.js`；无 `localhost:1313` 残留（索引内的 "localhost" 是 Grafana SOP 正文的 docker 示例，非残留）。
- **工作区干净**：仅 `.workbuddy-ai/` 未跟踪；本地 markdown 追踪器无 open 工单。

## 下一步

1. **内容填充待办**（卡用户材料，自候选 7 继承，不随图）：`data/products.yaml` 的 buy_url 填空 + `listed` 翻 true、`content/about.md` 真实简历、`hugo.toml` socialIcons 真实邮箱、删 `content/posts/my-first-post1.md` 脚手架。
2. **小 Nit**：`.github/workflows/deploy.yml` 的「Assert site contracts」步注释还枚举五类职责（套件已七类；AGENTS.md §3 与套件头注释已改）——下批顺手改，不单独烧 CI。
3. **重写 fastsearch 时的既有输入**（地图 Out of scope）：结果呈现层深化 / 引擎形态（ESM 模块化）/ 索引加载失败容错 UX——以 ADR-0010 的快照契约为输入，测试与新契约一起 TDD 出生。
4. **可选新需求**：菜单 4 个 `parent = "categories"` 子项配置了但 `header.html` 不渲染——要渲染是功能决定，另开图。

## 建议 skill

- **realeng-wayfinder** — 下一张图先排地图（目的地先行、工单是待决策问题、一会话一工单）。
- **realeng-grilling** — 一次一问、先给推荐答案；事实自己查（本会话两处「我以为的事实」——项目级 fastsearch 覆盖层、fixture 字面量空格——都是查出来的）。
- **realeng-tdd** — 红绿一次一行为；本图新断言累计 11 次变异/先红全收；行为保持型重构用「全套 + 构建 + 产物 grep」三重验收。
- **realeng-code-review** — 双轴并行，固定点取该批首个提交前；三轮评审共抓 6 处（文档失实 ×3、潜在缺陷 ×1、措辞 ×2）。
- 环境注意：① 查 CI 用 `curl` + GitHub API（未认证可读 runs/jobs；**logs API 需 admin 权限，403 拿不到**）；② **按 SHA 匹配 run 要用 `startswith` 或全量 SHA**——API 返回 40 位 head_sha，短 SHA `==` 永远匹配不上（本次轮询器空转 6 分钟即此，勿再犯）；③ 本 shell 的 grep 对 `\|` 交替失效（用 Grep 工具）；④ 沙箱升级时命令行输出会错乱——提交是否落库以 `git log` 为准，勿被回显骗到重复提交。

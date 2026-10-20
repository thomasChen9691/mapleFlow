# 交接：候选 5「reveal 协议」全程闭环 + 34 提交已 push 验 CI（2026-10-20）

## 当前状态

- **候选 5 全程闭环**：地图 `docs/wayfinder/map-reveal-protocol.md` 已 closed，六工单 0021~0026 全 closed；决策耐久化在 `docs/adr/0007-reveal-protocol.md`，术语条在 `CONTEXT.md`「reveal 协议」，导航在 `AGENTS.md`（§3 `npm test`、坑点 12、§7 目录级速查行），ADR-0002/0006 各加指针行（正文未改）。内部细节以这些文件为准，本文不复述。
- **代码/测试位置**：引擎 `assets/js/mf-reveal/`（app 入口 / filter 筛选 / scroll-in 进场 / reduced-motion 降级判定）；行为断言 `tests/assert_reveal.mjs`（`npm test`，16 项）；产物断言并入 `tests/assert_product_states.py`（39 项）；依赖声明 `package.json` + lock（jsdom 30.1.3，type:module，engines node>=22.22.2，唯一 devDependency）；CI 在 Build 前跑 node 步（`npm ci` → `npm test`，失败阻断部署）。本地终态：16/16 + 39/39 + SOP 100/100 + 生产构建 exit=0。
- **已 push 验 CI（本次）**：`3bf78be..0f7687a main -> main`（34 个提交）。Deploy run（id 39350204954）10 步全 success——Setup Node → npm ci → Assert reveal behavior → Build Hugo site → product states → SOP pipeline → Deploy，新 CI 路径首次生产验证通过；pages 部署 run 同步 success。
- **未决遗留**（评审记录在案，非阻塞）：① 改 `package.json` 必须同步 lock（CI `cache: 'npm'` 依赖 lockfile）；② 契约「定义处」三处入口（docstring / ADR 决策级摘要 / AGENTS 坑点）分层维护，改契约需三处同步，目前靠两套件兜底；③ 搜索 JS（fastsearch）与 `index.json` 的 kind 门禁归候选 8，未动（候选 4 的 0019 已留边界注释）。

## 下一步

1. **选下一张图**：候选 6「主题 fork」或候选 8「搜索契约」（含 index.json kind 门禁归属与投影字段定案）。另：用户 2026-10-19 计划重启后端开发——届时产品数据源替换只动 `product-items.html` 一处（ADR-0006 决策 2 / Consequences 继续有效）。
2. **内容类待办**（卡用户材料，不随图）：`data/products.yaml` 的 `buy_url` 填空 + `listed` 翻 true、`content/about.md` 真实简历、`hugo.toml` socialIcons 真实邮箱、删 `content/posts/my-first-post1.md` 脚手架。
3. **线上抽查**（刚部署）：产品页筛选交互观感、首页 hero 进场、无 localhost 残留——契约面已被 CI 守门，人工只验观感。

## 建议 skill

- **realeng-wayfinder** — 开下一张图先排地图：目的地先行、工单是待决策问题、一会话一工单。0026 的节奏（质询四问 → 红绿施工 → 双轴评审 → 单独 commit）可直接复用。
- **realeng-grilling** — 一次一问、先给推荐答案；事实自己查（文件/子代理），决策问用户；本场累计 12 问用户全选推荐，节奏已验证。
- **realeng-tdd** — 新行为先红后绿、每轮单独 commit；两条固化纪律：每条断言用变异检验证实有牙；测试期望值必须是独立字面量。
- **realeng-code-review** — 每批完工跑双轴（固定点取该批首个 commit，spec 源在工单 Resolution）；本场它抓出 3 处文档硬伤（术语条载路径 / 0006 指针越权 / ADR 复述字面契约）。

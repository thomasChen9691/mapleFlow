# 交接：推送上线与 CI 排障（2026-10-19）

> 本场只做两件事：把积压的 60 个 commit 推上线，并让 CI 转绿。
> 术语、模块设计、ADR 不在此重复——按 AGENTS.md §8.1 读 `CONTEXT.md` + `docs/adr/`。
> SOP 管线本身的形态与决策见 `docs/handoffs/2026-10-15-sop-pipeline-implementation.md`（本文是它的续篇）。

## 当前状态

- **远端与部署同步**：`main` = `origin/main` = `3bf78be`；`gh-pages` = `b31f79e`；最新 CI run **#16 success**。
- **历史已重写为纯 ASCII**：`filter-branch --msg-filter` 按 SHA 映射改写 60 个 commit message（14 个含非 ASCII：8 个 em-dash + 6 个中文）。备份分支 `backup/pre-msg-rewrite` 保留原状态；树哈希 `526676c6…` 前后一致，可证明纯消息改写、内容零变更。`backup/pre-msg-rewrite` **尚未删除**——确认线上无恙后可 `git branch -D`。
- **本场 3 个新 commit**（均已推）：
  - `0eb2ca8` 渲染确定性修复（新增 `layouts/partials/post_meta.html` 覆盖 + 删除被误作用域的 `[pagination] timeZone` 键）
  - `10dd50b` golden 比对容忍时区标记（`tests/sop_golden.py`）
  - `3bf78be` 交接文档补写
- **线上抽查全绿**：首页 / `about.html` / `products.html` / `categories/` / 6 篇派生 SOP / 手写索引页 / `index.xml` 全 200；sitemap 中 sop 类 URL 恰 7 条（6 派生 + 1 手写索引）；首页 `localhost:1313` 零命中；悬浮时间戳为 `2026-01-28 20:00:00 +0800`。
- **测试**：`tests/assert_sop_pipeline.py` 100/100、`tests/assert_product_states.py` 14/14。
- **主题覆盖增至 3 个**：`layouts/_default/baseof.html`、`layouts/partials/extend_head.html`、`layouts/partials/post_meta.html`。升级 PaperMod 子模块必须逐个同步（前两个管 `.no-js` 基线与 OG，第三个管时间戳确定性）。
- **工作区既有噪音，勿动**：`themes/PaperMod` 子模块标记（纯行尾规范化，gitlink 未变）。

## 下一步

1. **清理备份分支**：线上确认无恙后删除 `backup/pre-msg-rewrite`（本地分支，未推远端）。
2. **F10「小手抄集群」**（建议下一个开工）：`docs/sop/MAPLEFLOW_BLOG_SOP.md` 仍教人启动已退役的 backend（0011 遗留地雷），且与 `AGENTS.md` 存在陈旧重复；0009 决议当时明确未越权碰它。
3. **候选 4~6、8 各自成图**：product-index 接口收窄、reveal 协议、主题 fork、搜索契约。
4. **候选 7 精选机制**：文章 `featured` 字段驱动首页「精选文章」，方向已裁、待开工。
5. **内容类待办（等用户提供材料）**：`data/products.yaml` 的 `buy_url`（现全空 → 显示「即将上架」）、`content/about.md` 真实简历、`hugo.toml` socialIcons 真实邮箱、删除 `content/posts/my-first-post1.md` 脚手架残留。

## 本场踩到的新坑（值得记住的两条）

- **`tests/tmp` 里的构建产物会触发 safe-delete 护栏**：断言脚本清理临时目录时若单轮删除文件数超阈值，命令会被拦下、整条链式命令静默短路（后续 commit 不执行）。跑测试与提交**分开**执行。
- **链式命令的显示层仍会出幽灵**（本场复现：「no changes added」而 commit 实际已生成、`git rev-parse A B` 报 `Needed a single revision`）。铁律不变：提交后用 `git show --stat HEAD` / 分别 `git rev-parse` 独立验证。

## 建议 skill

- **realeng-grilling** — 开新地图时一次一问、先给推荐答案；事实自己查，决策问用户。
- **realeng-tdd** — 任何新行为先红后绿，每轮单独 commit。
- **realeng-code-review** — 每批完工跑双轴评审（固定点取该批首个 commit；spec 源在 `docs/wayfinder/` 与 ADR）。
- **realeng-domain-modeling** — 新术语当场进 `CONTEXT.md`，不攒批。
- **realeng-improve-codebase-architecture** — 选下一个候选前重跑（旧评审报告在 `internal/`，已 gitignore）。
- **realeng-handoff** — 会话收尾压缩交接，存 `docs/handoffs/`。

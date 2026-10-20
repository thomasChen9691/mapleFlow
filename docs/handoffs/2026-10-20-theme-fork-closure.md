# 交接：候选 6「主题 fork」全程闭环（2026-10-20）

> 本场做完候选 6 全程（排图 → 两张研究 → 四轮质询 → 三轮施工 → 双轴评审 → 收口）。
> 决策已耐久化在 ADR-0008 / CONTEXT.md / AGENTS.md / 主题 README，
> 本文不复述其内容——按 AGENTS.md §8.1 读 `CONTEXT.md` + `docs/adr/` 即可发现本模块。

## 当前状态

- **候选 6 地图已关闭**：`docs/wayfinder/map-theme-fork.md`（status: closed），八工单 0027~0034 全 closed；决策集落 `docs/adr/0008-theme-fork.md`，ADR-0002 加指针行（正文不改）；CONTEXT.md 有「主题层」术语条；AGENTS 有主题目录速查行 + 参数纪律坑点；主题导航在 `themes/maplemod/README.md`。
- **代码与测试**：`themes/maplemod` 48 文件（vendored 第一方主题，无子模块、无 `.gitmodules`、`.git/modules` 缓存已删）；站点层 `layouts/` 恰 7 文件；主题契约断言 B7-B13 并入 `tests/assert_product_states.py`（48/48，每条经变异检验）；npm 16/16；SOP 100/100；生产构建 exit=0；localhost 零残留。
- **未推送**：`origin/main..main` = 24 个提交（0029~0034 施工 + 记录）。**CI 未验**——0031 的 CI 改动（删 `submodules`/`fetch-depth`）只能由 push 后的 Deploy run 实证；若红，回滚那两行即可。
- **已知事实（勿重新推导）**：① 菜单配置 13 条、实际渲染 9 个顶层项（4 个 `parent = "categories"` 子项不渲染，既有行为）；② 五个合并文件（baseof/extend_head/extend_footer/post_meta/opengraph）的合并前历史在**旧站点路径**，`git log --follow` 穿不过合并点；③ 测试构建不带 `--minify` 而 `public/` 是 minified，断言正则须兼容引号两形态；④ 子代理曾持续 429，评审改主代理串行并在 commit 记录。

## 下一步

1. **push 验 CI**（唯一未验证面）：Deploy run 全绿 = 0031 验收关闭；顺带线上抽查首页/产品页/主题观感。
2. **选下一张图**：候选 8「搜索契约」（`index.json` 投影字段 + fastsearch + kind 门禁归属）；候选 7「精选机制」（方向已裁决、未开工）。
3. **内容类待办**（卡用户材料，不随图）：`data/products.yaml` 的 `buy_url` 填空 + `listed` 翻 true、`content/about.md` 真实简历、`hugo.toml` socialIcons 真实邮箱、删 `content/posts/my-first-post1.md` 脚手架。
4. **可选新需求**：菜单子项（ops/k8s/docker/aiops）渲染——当前 4 条配置项从未出现在页面上，属功能决策不是架构。

## 建议 skill

- **realeng-wayfinder** — 开下一张图先排地图（候选 8/7）。
- **realeng-grilling** — 一次一问、先给推荐答案；本场用户全程弹选项选择，节奏已验证。
- **realeng-tdd** — 红绿一次一行为；本场固化：断言逐条变异检验、期望值独立字面量、tracer bullet 发现（跳转页/菜单渲染面）当场入 Resolution 订正。
- **realeng-code-review** — 固定点取该批首个提交；子代理 429 时可主代理串行双轴，但须在 commit 记录。
- **realeng-handoff** — 会话收尾压缩交接，存 `docs/handoffs/`。

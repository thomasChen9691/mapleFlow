# 交接：候选 7「精选机制」全程闭环（决策 + 同场施工，2026-10-22 终态）

## 当前状态

- **候选 7 全程闭环**：地图 `docs/wayfinder/map-featured-mechanism.md` 已 closed，七工单 0035~0041 全 closed（0035 研究、0036-0041 质询，用户为决策者）。决策集耐久化在 **ADR-0009**（字段契约 / 首页行为 / seam 形状 / 测试缝 / 派生文归属）；**ADR-0006 加指针行**（featured 语义被跨类统一扩展），**ADR-0005 施工期补记**（契约四类→五类）。术语/导航：`CONTEXT.md`「精选」「注册表」条、`AGENTS.md` §3 命令与旧名指针 / §7 `post-items.html` 行 / 坑点 8·9·**11·12**、`archetypes/default.md` 注释。
- **代码与测试**：新 seam `layouts/partials/post-items.html`（只收 `limit`，返回 `{featured, rest, all}`，补集用 `complement` 对**实际显示的精选**求）；首页精选块真精选、网格分页建在补集、两块空集即整块不渲染；产品侧补 featured 布尔校验；`_content.gotmpl` 可选 `featured` **条件传键**；3 篇手写文章标 featured。测试：`assert_site_contracts.py` **61/61**、`assert_sop_pipeline.py` **104/104**、`npm test` **16/16**、生产构建 exit=0、无 localhost 残留。线上首页精选 = 索引 / AIOps / K8s，网格从 Prometheus 起。
- **提交**：`eec689f`（施工）+ 本提交（收口：ADR-0009 / ADR-0006 指针 / 坑点 11·12 / handoff）。**两个提交均未 push**——push 后 CI 首次验证本链路。
- **无在途工单**：本图无剩余；工作区仅 `.workbuddy-ai/` 未跟踪。
- 评审/施工细节（含 code-review 双轴 8 条处置、两处假绿陷阱）在各工单 Resolution 与 ADR-0009 Consequences，勿在此重述。

## 下一步

1. **push 并验 CI**：`git push origin main` → Deploy run 全绿 = 候选 7 全链路收尾；若红，先看 `Assert site contracts` 步（本链路新增的断言都在该步）。
2. **选下一张图**：候选 8「搜索契约」（`index.json` 投影字段 + fastsearch + kind 门禁归属）；或本图雾区三条（「精选」徽标是否在内容层可见 / 首页数据条是否区分精选 / 分类页是否消费精选）。二者互相独立。
3. **内容类待办**（卡用户材料，不随图）：`data/products.yaml` 的 `buy_url` 填空 + `listed` 翻 true、`content/about.md` 真实简历、`hugo.toml` socialIcons 真实邮箱、删 `content/posts/my-first-post1.md` 脚手架。
4. **可选新需求**：菜单 4 个 `parent = "categories"` 子项配置了但 `header.html` 不渲染——要渲染是功能决定，另开。

## 建议 skill

- **realeng-wayfinder** — 开下一张图先排地图（目的地先行、工单是待决策问题、一会话一工单）。
- **realeng-grilling** — 一次一问、先给推荐答案；事实自己查（本场两处「我以为的事实」都是查/file 才翻的盘：fixture 的 sop.yaml 镜像、`dict` nil 键的 `isset` 行为）。
- **realeng-tdd** — 红绿一次一行为；本场固化两条：① 每条断言变异检验（本次 5 次变异全红才收）；② fixture 日期不能用未来日（Hugo 不发布 → 假绿）。
- **realeng-code-review** — 双轴并行，固定点取该批首个提交；本场它抓出「测试与真实内容耦合」这条最重的（SOP 透传原实现能否过取决于真实文章日期）。
- 环境注意：本 shell 的 grep 对 `\|` 交替失效（用 `-e` 多模式）；`sed -i ''` 在 macOS 需带空串参数；`gh` 未安装（查 CI 用 API + curl）。

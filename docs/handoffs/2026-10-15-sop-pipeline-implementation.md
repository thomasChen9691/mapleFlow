# 交接：SOP 发布管线（候选 2）——地图已关闭，目的地到达

> 本图（`docs/wayfinder/map-sop-source-sync`）8 张工单全 closed，2026-10-16 收口。
> 本文是候选 2 全历程的最终状态；后续新工作另起地图。

## 最终状态

- **管线**：seam = `content/posts/_content.gotmpl`（注册表驱动 + errorf 契约五类：缺必填字段 slug/note/date/categories、死条目、首行无 H1、H1 后无章节标题行）；数据 = `data/sop.yaml` 注册表 + `docs/sop/` 源笔记；正文变换三规则（剥 H1 / 剥单行定位段 / 前置导语）。6 篇线上页面与迁移前一致（golden·规范化比对；见下「CI 排障」）。
- **决策耐久化**：ADR-0005（docs/adr/0005）+ CONTEXT.md 术语（发布管线节：SOP 发布管线 / 注册表）+ AGENTS.md 坑点 10 与速查表。新会话按 §8.1 读 CONTEXT.md + docs/adr/ 即可发现本模块。
- **测试**：`tests/assert_sop_pipeline.py` 100/100 绿（契约 fixture 六类各钉归因 / 产物断言 / 结构三断言 / golden 保真 / README 漂移 / ref / 搜索投影 / draft / CI 守门 / 页面集合孤儿守门）；golden 生命周期 = `tests/capture_sop_golden.py`（--check / 重捕获 / 按 slug 新建）；CI 双断言步阻断部署。产品状态套件 14/14 绿。
- **backend 已退役**（工单 0011）：全套删除 + ADR-0003 状态标注；架构评审「候选 3」随之消解。
- **已推送并上线（2026-10-19）**：60 个 commit 推到 `origin/main`（`5000dbc..806dea3`），随后两轮 CI 修复（`0eb2ca8`、`10dd50b`）后 **run #15 成功、gh-pages 更新为 `b31f79e`**，线上 6 篇 SOP 页 + 手写索引页共 7 条 sitemap URL 全 200，`localhost:1313` 零残留。CJK commit message 已用 `filter-branch --msg-filter` 全量重写为 ASCII（备份分支 `backup/pre-msg-rewrite`，树哈希前后一致）。

## CI 排障（2026-10-16 → 10-19，三轮首红）

1. **第 1 红（run #11）**：golden 逐字节比对在 CI 必红——golden 由本机 0.167 捕获、CI 钉 0.164。改为**规范化比对**（`tests/sop_golden.py: canonical`：标签名 + 排序属性 + 折叠文本），另给断言加 **GitHub 注解输出**（`::error`），使 CI 失败项无需日志权限即可从 run 页读出。
2. **第 2 红（run #12/13）**：注解直指分歧点 = post-meta 的 `title` 属性：本机 `+0800 CST`、CI `+0800 +0800`。
3. **第 3 红（run #14）**：误判为缺 `timeZone`——**实测证伪**（Hugo 的 timeZone 只影响语言级日期格式化，不改变已带偏移量的 `time.Time` 的 Location；`TZ=UTC` 本地可精确复现 CI 输出）。真因是 Go：只有偏移量与构建机器本地时区一致才用命名时区，否则造无名固定区；PaperMod 用 `printf "%s" .Date`（即 `time.Time.String()`）打印缩写。
   **根治**：新增主题覆盖 `layouts/partials/post_meta.html`（逐字复制主题，仅把 title 改为显式格式 `2006-01-02 15:04:05 -0700`）→ 跨时区构建**字节一致**（已实测）。比对侧另加「时间戳属性值的时区标记归一」容错，使旧 golden 无需重捕获、且未来任何 `.Date` 字符串化不再同类假红（时间值本身变了仍必红）。


## 后续事项（按优先级）

1. **后续提交**：main 已与 origin 同步，后续改动按常规 push（推 `main` 即触发 build + 双断言 + 部署）。
2. **候选 4~6、8**（各自独立成图）：product-index 接口收窄、reveal 协议、主题 fork、搜索契约。
3. **F10「小手抄集群」**：MAPLEFLOW_BLOG_SOP.md 与 AGENTS.md 的陈旧重复（该文件还教人启动已删除的 backend——0011 遗留地雷，按 0009 决议未越权碰它）。
4. **候选 7 精选机制**：文章 featured 字段，方向已裁决待开工。
5. **日常新增 SOP**：写笔记（守结构约定：H1 → 章节标题 → 单行定位段）→ 加注册条目 →（可选）跑 capture 建 golden；改定位段时同步 review 导语。
6. **主题覆盖已增至 3 个**：`layouts/_default/baseof.html`、`layouts/partials/extend_head.html`、`layouts/partials/post_meta.html`——升级 PaperMod 子模块时必须逐个同步，否则静默丢行为。

## 经验（本图历程）

- **工具输出显示层会出幽灵**：假「no changes added」、heredoc 里 `§` 字符损坏、`2>/dev/null` 吞掉 staging 失败（`e2de031` 只说没做靠 `e4a739e` 补）。铁律：提交后 `git show --stat` 独立验证。
- **golden 是迁移保真的锚，但别让它阻塞新增**：新条目无 golden 走结构断言（code-review 逼出的修正）。
- **Hugo 0.164 适配器三坑**：dates 必须嵌套、description 必须顶层（PaperMod 读 .Description）、`os.ReadFile` 对缺失文件静默返回空串（死条目要显式 `os.FileExists`）。
- **「本机绿、CI 红」先查环境依赖，不是先改测试**：三轮 CI 红全部源于「构建机器决定输出字节」（渲染器版本、机器本地时区）。定位手段按成本排序：① 断言直出 GitHub 注解（免日志权限）② 注解里带首个分歧 token ③ 本机 `TZ=UTC` 复现。根治点选在**渲染侧**（显式格式），比对侧只做环境元数据归一，不做内容级容错。

## 建议 skill（后续工作）

- **realeng-tdd** — 任何新行为先红后绿。
- **realeng-code-review** — 每批结束跑双轴（固定点取上一批首个 commit）。
- **realeng-grilling** — 新地图的决策点一次一问，先给推荐答案。
- **realeng-domain-modeling** — 新术语当场进 CONTEXT.md，不攒批。

# 交接：SOP 发布管线（候选 2）——地图已关闭，目的地到达

> 本图（`docs/wayfinder/map-sop-source-sync`）8 张工单全 closed，2026-10-16 收口。
> 本文是候选 2 全历程的最终状态；后续新工作另起地图。

## 最终状态

- **管线**：seam = `content/posts/_content.gotmpl`（注册表驱动 + errorf 契约五类：缺必填字段 slug/note/date/categories、死条目、首行无 H1、H1 后无章节标题行）；数据 = `data/sop.yaml` 注册表 + `docs/sop/` 源笔记；正文变换三规则（剥 H1 / 剥单行定位段 / 前置导语）。6 篇线上页面与迁移前逐字节一致（golden）。
- **决策耐久化**：ADR-0005（docs/adr/0005）+ CONTEXT.md 术语（发布管线节：SOP 发布管线 / 注册表）+ AGENTS.md 坑点 10 与速查表。新会话按 §8.1 读 CONTEXT.md + docs/adr/ 即可发现本模块。
- **测试**：`tests/assert_sop_pipeline.py` 100/100 绿（契约 fixture 六类各钉归因 / 产物断言 / 结构三断言 / golden 保真 / README 漂移 / ref / 搜索投影 / draft / CI 守门 / 页面集合孤儿守门）；golden 生命周期 = `tests/capture_sop_golden.py`（--check / 重捕获 / 按 slug 新建）；CI 双断言步阻断部署。产品状态套件 14/14 绿。
- **backend 已退役**（工单 0011）：全套删除 + ADR-0003 状态标注；架构评审「候选 3」随之消解。
- 本地 `main` 共 18 个 commit（`2597727` → `334ea3a`），**全部未 push**（ahead of origin 58；push 卡 CJK commit message 重写待用户批准）。

## 后续事项（按优先级）

1. **push 与历史重写**：CJK commit message 重写方案待批准（backup + cherry-pick replay + 树哈希双验）；批准后 58 个 commit 一次推，触发 CI（含新增断言步）。
2. **候选 4~6、8**（各自独立成图）：product-index 接口收窄、reveal 协议、主题 fork、搜索契约。
3. **F10「小手抄集群」**：MAPLEFLOW_BLOG_SOP.md 与 AGENTS.md 的陈旧重复（该文件还教人启动已删除的 backend——0011 遗留地雷，按 0009 决议未越权碰它）。
4. **候选 7 精选机制**：文章 featured 字段，方向已裁决待开工。
5. **日常新增 SOP**：写笔记（守结构约定：H1 → 章节标题 → 单行定位段）→ 加注册条目 →（可选）跑 capture 建 golden；改定位段时同步 review 导语。

## 经验（本图历程）

- **工具输出显示层会出幽灵**：假「no changes added」、heredoc 里 `§` 字符损坏、`2>/dev/null` 吞掉 staging 失败（`e2de031` 只说没做靠 `e4a739e` 补）。铁律：提交后 `git show --stat` 独立验证。
- **golden 是迁移保真的锚，但别让它阻塞新增**：新条目无 golden 走结构断言（code-review 逼出的修正）。
- **Hugo 0.164 适配器三坑**：dates 必须嵌套、description 必须顶层（PaperMod 读 .Description）、`os.ReadFile` 对缺失文件静默返回空串（死条目要显式 `os.FileExists`）。

## 建议 skill（后续工作）

- **realeng-tdd** — 任何新行为先红后绿。
- **realeng-code-review** — 每批结束跑双轴（固定点取上一批首个 commit）。
- **realeng-grilling** — 新地图的决策点一次一问，先给推荐答案。
- **realeng-domain-modeling** — 新术语当场进 CONTEXT.md，不攒批。

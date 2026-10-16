# 0005 - SOP 发布管线：源笔记单一真源 + 构建期派生

**状态**：已批准（2026-10-16）。决策过程见 wayfinder 地图「SOP 真源与发布管线图（候选 2）」与工单 0007~0014 决议；本 ADR 是决策的耐久化记录——AGENTS.md §8.1 的阅读路由（CONTEXT.md + docs/adr/）不含 wayfinder 目录，决策必须活在 docs/adr/（ADR-0004 立过的规矩）。

## 决策

1. **真源**：`docs/sop/` 源笔记是 6 篇工具 SOP 文的唯一真源；`content/posts/` 下不再有手写 `sop-*.md`（已删），磁盘上没有第二份 .md。
2. **机制**：content adapters——seam = `content/posts/_content.gotmpl`，构建期读 `data/sop.yaml` 注册表 + `docs/sop/` 笔记，`AddPage` 派生文章。`path` = 注册表 slug ⇒ **6 个线上 URL `/posts/sop-*.html` 冻结**（改 URL = 外链 404）。
3. **元数据**：web 包装（slug/note/date/categories/description/导语）住注册表；标题由 seam 从笔记首行 H1 提取（标题唯一源）；slug/note/date/categories 必填无缺省，tags 可缺节，`draft: true` 表已注册的草稿。
4. **契约**：模块内 `errorf` 执法、构建即门禁——缺必填字段 / 死条目（条目在而笔记缺失）/ 笔记首行无 H1 / H1 之后无章节标题行，四类坏输入必须构建失败。
5. **目录契约**：注册表驱动——无条目的笔记 = 尚未发布的稿件（`CONTEXT.md` 源笔记定义因此机械真实）；条目 ↔ 笔记配对由构建期执法，不给缺省值。
6. **正文变换**：剥 H1 → 保留首个章节标题行 → 剥紧随其后的单行定位段（其内容由注册表导语承载）→ 前置导语。定位段为多行则不剥（页面可见重复，不静默丢失内容）。
7. **测试**：build-then-assert（Hugo 生态无模板单测机制）。迁移保真 = golden 逐字节比对（捕获自迁移前线上页面，出处见 `tests/fixtures/sop-golden/README.md`）；存活断言 = 契约 fixture（每类钉到各自契约子串）+ 产物断言（URL 冻结 / 标题==H1 / 日期==注册表 / 结构三断言 / 无残留 / 页面集合孤儿守门）+ README↔注册表漂移 + ref 解析 + 搜索投影 + draft 行为 + CI 守门；golden 生命周期用独立捕获脚本（`tests/capture_sop_golden.py`）——期望值更新必须是 PR 里可审的 diff，验证与再生不共入口。
8. **连带后果**：backend（FastAPI 内容 API）随之退役——适配器化后其 `glob("*.md")` 对派生文章失效（静默 10→4 篇）且零消费者；ADR-0003 加状态标注（语义裁决仍有效，适用对象已不在）。

## Considered Options

- **module mounts**：虚拟视图，不能注入 front matter（docs/sop 八个文件全无），slug 按文件名小写化与现有 URL 冲突——排除。
- **构建外预生成脚本**：「漏跑一步 = 陈旧派生数据静默渲染」正是 ADR-0004 枪毙过的失效模式；且需另配守门测试才安全，机制总数不减反增——排除。
- **git symlink**：Hugo v0.163.1 安全修复（GHSA-c3wq-j5vh-68rc）起统一文件系统丢弃 symlink——排除。
- **backend 改道**（读 `public/` 产物 / Hugo custom output JSON / 接受 4/10 静默覆盖）：为零消费者维护新机制，或接受本项目一直在消灭的静默失效类别——排除，直接退役。

## Consequences

- 新增一篇 SOP = 写笔记 + 加注册条目；无条目即不发布，`draft: true` 即注册但未发布。
- 笔记结构成为契约依赖：首行 H1 → 章节标题 → 单行定位段（约定载于 `docs/sop/README.md`）。
- 适配器按 Hugo 0.164 语义编写（CI 钉版，本机 0.167 skew 已坐实）：`dates` 必须嵌套 dict（顶层 date 静默失效）、categories/tags 走 params、description 必须顶层（PaperMod 读 `.Description`）。
- 主题零改动：无 PaperMod 覆盖文件新增，子模块升级无同步负担（对照 ADR-0002 的两个覆盖文件）。
- 搜索索引、分类/标签 taxonomy、RSS 对派生页自动生效——生成页是真页面。

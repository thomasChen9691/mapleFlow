# SOP golden fixtures — 出处与复验方式

这些文件是 6 个迁移条目**迁移前线上页面的直捕**，是「迁移保真」断言的期望值。
期望值必须独立于实现——golden 捕获自实现之前的既有产物，不是对适配器
逻辑的重算（防同义反复测试）。

## 捕获方式（2026-10-15）

1. 源码状态：commit `2597727`（Cycle 1 迁移）的**父提交**——即 6 篇
   `content/posts/sop-*.md` 手写文章仍在、适配器尚未引入的状态。
   可从 git 取回原件核对：
   `git show 2597727^:content/posts/sop-ansible-automation-guide.md`
2. 构建命令（与 CI 逐字一致）：
   `hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml -d tests/tmp/baseline`
3. 抽取字段（每篇一个 JSON）：
   - `title`：`<title>` 全文
   - `meta_description`：`<meta name=description content="...">` 的值
   - `article_html`：`<article ...>` 开标签到 `</article>` 之间的原文
     （minify 后字节级比对，故构建必须带 `--minify`）

## 复验

改动适配器后跑 `python3 tests/assert_sop_pipeline.py`：任一迁移条目的
`<article>` 全文 / meta / title 与 golden 不符即 RED——线上页面正在
发生非预期变化。

## 新增条目

新 SOP（写笔记 + 加注册条目）**没有也不需要有 golden**：迁移保真断言
只覆盖有 golden 的条目；新条目由结构断言守护（导语在场、章节标题
序列 == 源笔记、笔记末行在场、标题 == H1、日期 == 注册表 date、
meta description == 注册表）。页面正确性由 PR 期人工审阅把关——与
任何内容变更同等流程。

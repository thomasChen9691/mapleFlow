# SOP golden fixtures — 出处与复验方式

这些文件是 6 个迁移条目**迁移前线上页面的直捕**，是「迁移保真」断言的期望值。
期望值必须独立于实现——golden 捕获自实现之前的既有产物，不是对适配器
逻辑的重算（防同义反复测试）。

## 捕获方式（2026-10-15，首次）

1. 源码状态：commit `2597727`（Cycle 1 迁移）的**父提交**——即 6 篇
   `content/posts/sop-*.md` 手写文章仍在、适配器尚未引入的状态。
   可从 git 取回原件核对：
   `git show 2597727^:content/posts/sop-ansible-automation-guide.md`
2. 构建命令（与 CI 逐字一致）：
   `hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml -d tests/tmp/baseline`
3. 抽取字段（每篇一个 JSON）：`title`（`<title>` 全文）、`meta_description`
   （`<meta name=description>` 的值）、`article_html`（`<article ...>` 开标签到
   `</article>` 之间的原文）。
   比对是**规范化**的（`tests/sop_golden.py: canonical`：标签名 + 排序属性 +
   折叠文本的 token 序列），不是逐字节——项目政策是「CI 钉 0.164、本机 0.167」，
   渲染器版本差异会改变属性引号/空白/代码高亮写法，逐字节比对在 CI 必红
   （2026-10-16 CI 首红实测）。规范化仍抓一切真实变化：标签、属性值、文本。

## 生命周期（2026-10-16，工单 0013 裁决 A：独立捕获脚本）

此后一律用脚本，不再手工抽取——抽取逻辑在 `tests/sop_golden.py`，由捕获脚本
与断言脚本共用（两边规则漂移是 golden 机制的隐形死法）：

```bash
python3 tests/capture_sop_golden.py --check   # 只读：任一 golden 陈旧即非零退出
python3 tests/capture_sop_golden.py           # 重捕获全部已有 golden
python3 tests/capture_sop_golden.py <slug>    # 为指定 slug 新建/更新 golden
```

- **笔记合理修订**：断言红（迁移保真）→ 确认变更有意 → 跑捕获脚本 → golden
  diff 进 PR review。期望值的更新永远是一个可审的文件变更。
- **新增 SOP 条目**：无 golden 是合法状态（结构断言守）；要字节级守门就顺手
  捕获一个，PR 里一并 review。
- **未改动树上跑捕获或 --check 必须零 diff**（幂等自检；同版本渲染下）。
- 为什么不放在断言脚本里加 `--recapture`：验证与再生混一个入口，误跑一下
  就把「页面回归」洗成「期望更新」。

## 复验

改动适配器后跑 `python3 tests/assert_sop_pipeline.py`：任一迁移条目的
`<article>` 全文 / meta / title 与 golden 不符即 RED——线上页面正在
发生非预期变化。

## 新增条目

新 SOP（写笔记 + 加注册条目）**没有也不需要有 golden**：迁移保真断言
只覆盖有 golden 的条目；新条目由结构断言守护（导语在场、章节标题
序列 == 源笔记、笔记末行在场、标题 == H1、日期 == 注册表 date、
meta description == 注册表）。页面正确性由 PR 期人工审阅把关——与
任何内容变更同等流程。想更强就跑捕获脚本建一个 golden。

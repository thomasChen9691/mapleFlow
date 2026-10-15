---
id: 0007
title: Hugo 构建期内容生成机制事实清单
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-sop-source-sync
claimed: 2026-10-15
closed: 2026-10-15
---

## Question

若把 docs/sop/ 定为唯一真源、让 Hugo 在构建期生成 content/posts 的 SOP 文，Hugo 0.164（CI 钉版）有哪些可用机制？各自的磁盘落盘行为、front matter 控制力、对仓库第二个磁盘消费者（backend glob `*.md`）的影响是什么？

## Resolution

2026-10-15 · research（子代理；实证于本机 0.167 临时站点 + 0.164 源码/文档/release notes 逐条核对）。全文：[research/0007-hugo-build-time-content-generation.md](../research/0007-hugo-build-time-content-generation.md)。

六条关键结论：

1. **只有 content adapters**（`content/**/_content.gotmpl` + `AddPage`，v0.126.0 引入，0.164 完全适用）同时满足三硬约束：磁盘单份 .md（真源可放 docs/sop，adapter 内 `os.ReadFile` 实测可读 content/ 外目录）、front matter 全可控（title/slug/draft/description 顶层，categories/tags 须入 params）、真页面（独立 URL/taxonomy/RSS/搜索索引）。
2. **module mounts 是虚拟视图**：不注入 front matter；docs/sop 8 个文件均无 front matter ⇒ 挂载后 title 空、date 零值、tags 全丢（Hugo 不从文件名/H1 回退 title，源码级确认）；slug 按文件名且默认小写（`ANSIBLE_SOP.md` → `/posts/ansible_sop.html`，与现有 URL 冲突）。
3. **git symlink 出局**：v0.163.1 安全修复（GHSA-c3wq-j5vh-68rc）起统一文件系统丢弃 symlink，0.164 确定生效，不必再评估。
4. **adapter 生成页仅内存存在，Hugo 无落盘选项**（`io.Discard` + 内存 page map，源码级确认）⇒ `backend/blog_parser.py` 的 `glob("*.md")` 返回空、`/api/posts` 断供；grep/AI 导航也看不到生成文章，唯一可 grep 真源变成 docs/sop + adapter 模板。
5. **日期写法是隐藏 seam**：adapter page map 顶层 `"date"` 静默失效（官方文档示例本身有错，以 v0.164 官方集成测试为准），必须 `"dates" (dict "date" (time "..."))`；照抄文档示例会让全部文章日期变零值。
6. **CI flags 组合无坑**（`--gc --minify --cleanDestinationDir` 与 adapters 实证共存）；值得新增的守门是 `--printPathWarnings`（撞路径检测）+ adapter 内 `errorf` 契约（构建期失败即断部署）。

**下游**：工单「SOP 文的派生机制」解除事实阻塞；「backend 取数路由」随机制结论激活（若选出内存态机制即进入 frontier）。

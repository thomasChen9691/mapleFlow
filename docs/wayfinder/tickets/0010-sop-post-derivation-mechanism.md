---
id: 0010
title: SOP 文的派生机制
type: grilling
mode: HITL
status: closed
blocked_by: [0008]
assignee: agent
claimed: 2026-10-16
closed: 2026-10-16
map: map-sop-source-sync
---

## Question

承接「真源归属」的裁决：SOP 文（或反向的源笔记）以什么机制派生？

候选（若 0008 裁 docs/sop 赢）：

- (a) **content adapters**——`_content.gotmpl` 读 docs/sop + `AddPage`：磁盘单份、front matter 全可控、真页面；代价 = 内存态（backend 断供、grep/AI 导航看不到文章）、`dates` 嵌套写法陷阱、`--printPathWarnings` 守门；
- (b) **module mounts**——虚拟视图：docs/sop 需补 front matter（8 个文件现在全无），slug 按文件名小写化、与现有 `/posts/sop-*.html` 冲突，需逐篇加 `slug`；
- (c) **构建外脚本**——CI/Makefile 从 docs/sop 生成 content/posts/*.md：磁盘两份但自动同步，backend/grep/AI 导航全部不受影响；代价 = 生成物入库后的 review 面与「漏跑即腐化」风险（ADR-0004 已拒过同款风险，需评估本次是否同构——脚本写 content/ 是 git 可见的，与派生数据静默渲染不同）。

若 0008 裁 content/posts 赢：本题反向——docs/sop 是退役、归档还是反向生成。

本工单同时确认两个硬约束：

1. 既有 6 篇线上 URL `/posts/sop-*.html` 是否**冻结**（改 URL = 外链 404 + gh-pages 残留，除非 `--cleanDestinationDir` 清掉）；
2. 导语 / description / tags 等已分叉差异的**承载位置**（细则归工单「已分叉差异的消长裁定」，本题只定承载位置的候选空间）。

决策依据：工单 0007 的机制事实与代价结构；ADR-0001（构建命令只做加法）；ADR-0004 的「接口即测试面」原则。

## 预裁记录（工单 0008 质询，2026-10-15）

本题核心已在 0008 质询中裁定（见 [0008 Resolution](0008-sop-source-of-truth.md) 第 1/2/3 条）：机制 = content adapters；URL 冻结为硬约束；元数据 = `data/sop.yaml` 注册表 + 标题从 H1 提取。进入 frontier 后只剩正式落档与实现细节确认：slug 唯一由注册表给（禁文件名推导）；正文变换 = 剥首行 H1 + 前置导语；categories/tags 缺省值；`{{< ref >}}` 对生成页解析的验证尖峰（实施期第一关）。

## Resolution

2026-10-16 · grilling（用户为决策者）。本题为 0008 预裁范围的正式落档 + 两项补订。

**机制落档（正式）**：content adapters，seam = `content/posts/_content.gotmpl`。预裁三项确认无误并已实现：

1. 注册表驱动：适配器只遍历 `hugo.Data.sop`；`path = entry.slug`（相对适配器所在目录，官方文档语义），slug 唯一由注册表给、禁文件名推导——URL 冻结由此保证。
2. page map 契约（0.164 语义，实施期实证）：title 由笔记 H1 提取；description 必须放**顶层**（PaperMod 的 head/opengraph 读 `.Description`，放 params 只落 `.Params.description`、meta 标签全空——实测踩坑）；`dates` 必须嵌套 dict（顶层 date 静默失效）；categories/tags 走 params；`draft` 透传。
3. 排除项复核（依据工单 0007 事实）：mounts（无 front matter 注入 + docs/sop 八个文件全无 front matter + slug 按文件名小写化撞现有 URL）；构建外脚本（ADR-0004 枪毙的「漏跑即陈旧」失效模式——本次复核结论：即便生成物 git 可见，仍需另配守门测试才安全，机制总数不减反增，仍排除）；git symlink（v0.163.1 安全修复确定丢弃）。

**本题两项补订（质询裁定的新决策）**：

4. **categories 必填**——与 slug/note/date 同级，缺即构建失败；tags 维持可缺省。理由：站点五个分类在用（运维/aiops/docker/k8s/随笔），缺省值即隐性假设；「必填无缺省」是 ADR-0004 既定哲学。已红绿落地（commit `6960f15`：fixture 先红、适配器后绿、draft fixture 同步满足新契约）。100/100 green。
5. **第五条契约入正册**——实施期添加的防御性守卫「笔记 H1 之后无章节标题行 → 构建失败」正式列为契约 ④。理由：注册即承诺可发布，空壳笔记是坏承诺；「先占位后补内容」的需求由 `draft: true` 正规通道满足，不需要空壳页面上线。

**实施期对预裁记录的订正（记录在案）**：

- 正文变换实为**三规则**（剥 H1 / 剥紧随首个章节标题后的单行定位段 / 前置导语），非预裁的两条——golden 比对发现的历史事实，已在工单 0012 预裁记录中订正；
- 死条目检查必须显式 `os.FileExists`——`os.ReadFile` 对缺失文件静默返回空串不报错，直接读会让错误归因漂到 H1 检查（code-review 抓出，`38f205e` 修复）。

**验证尖峰结论**：`{{< ref >}}` 对 adapter 生成页解析正常（真实构建默认 refLinksErrorLevel=ERROR 下 6 个 ref 全部命中，`assert_ref_links` 守门）；`--printPathWarnings` 不纳入固定构建命令（ADR-0001 只做加法），撞路径风险由「无残留」断言直接覆盖。

**新增实现缝（记录在案）**：`params.sopNotesDir`（默认 `docs/sop`）——fixture 覆盖笔记目录的测试缝，与 0013 预裁的 dataDir 覆盖同款加法，真实构建零行为变化。

**下游影响**：0011 前提完全坐实（adapters ⇒ backend `glob("*.md")` 返回空）；0012 解除阻塞进入 frontier（其「承载位置」题本题已裁为注册表 + H1 提取，余下逐篇数据填充）；0013 的契约断言集增加 categories 一类（已随 `6960f15` 落地）。雾区无增生。

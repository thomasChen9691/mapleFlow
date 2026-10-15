# Research 0007 — Hugo 0.164 构建期内容生成机制事实清单

对象仓库：mapleFlow（Hugo 0.164.0 extended + PaperMod，uglyURLs=true，CI 命令 `hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml`，本机 dev hugo 0.167.0）。实证部分在本机 hugo v0.167.0+extended 的 /tmp 临时站点完成，未改动 mapleFlow 仓库任何文件；0.164 适用性以官方文档/源码/release notes 为准并逐条标注。查不到出处的点标「未验证」。

## Q1 Content adapters（`content/**/_content.gotmpl`）

1. **机制**：`_content.gotmpl` 是放在 content 目录里的**模板**（非内容文件），每目录每语言最多一个；构建期执行，通过 `.AddPage` / `.AddResource` 向站点添加页面；生成页的逻辑路径相对 adapter 所在目录。v0.126.0 引入（release notes 原话 "Create pages from _content.gotmpl"）。0.164 完全适用。
2. **API 签名（0.164 源码）**：`AddPage(any) (string, error)`——入参为单个 map，`path` 是唯一必填键；空 path 仅保留给 home page（`Init()` 源码："empty path is reserved for the home page"）。
3. **可用字段（对照提问逐项）**：

| front matter 字段 | adapter page map 写法 | 0.164 可用性 |
|---|---|---|
| title | 顶层 `"title"` | ✅ |
| date | **必须** `"dates" (dict "date" (time "..."))` | ✅（见下方日期陷阱） |
| slug | 顶层 `"slug"` | ✅ |
| categories / tags | **只能**放 `"params"` 里 | ✅（官方文档明示 + 源码 PageConfigLate 无 Tags/Categories 字段） |
| draft | 顶层 `"draft"` | ✅ |
| description | 顶层 `"description"` | ✅ |

其余顶层可用键（源码 PageConfigEarly/PageConfigLate @ v0.164.0）：`kind`、`url`、`linkTitle`、`summary`、`weight`、`layout`、`type`、`outputs`、`aliases`、`keywords`、`translationKey`、`headless`、`build`、`menus`、`sitemap`、`sites`、`content`（`mediaType`+`value`）、`params`。**`markup` 禁止设置**（须用 `content.mediaType`，否则报错 "markup must not be set, use mediaType"）。

4. **执行期限制**：Site 未完全初始化——依赖已构建页面的方法（`.Site.Pages`、`.Site.RegularPages`）**报错**（文档原话："Methods that depend on built pages, such as Site.Pages, are unavailable at this stage and return an error"）。`.Site.Title`、`.Store` 可用。**实证**：`.Site.Pages` 与 `.Site.RegularPages` 在 0.167 执行期均 ERRORED，但 home/list 模板里 `site.RegularPages` 正常（生成页正常进集合）。
5. **内存 vs 落盘**：**仅内存**。0.164 源码 `Execute()`：打开 gotmpl → `TextParse` → `ExecuteWithContext(ctx, tmpl, io.Discard, data)`——模板输出直接丢弃；`AddPage` → `HandlePage` 只写入内存 page map。**不存在任何写 .md 的代码路径**。渲染出的 HTML 照常落 `public/`（实证：`/posts/note-one.html` 等正常生成）。
6. **读取 content/ 外目录**：**可以**。`os.ReadFile`/`readFile` 官方文档："attempts to resolve the path relative to the root of your project directory, then relative to the root of each module… then relative to the content directory"。**实证**（0.167）：adapter 内 `os.ReadFile "sop/NOTE.md"` 成功读取 content/ 之外的文件并生成完整页面（正文 Markdown 正常渲染）。也可用 `os.ReadDir` 枚举目录。限制：symlink 自 v0.163.1 起被丢弃（见 Q3）。
7. **日期陷阱（重要，实证+官方测试双重确认）**：page map 里**顶层 `"date"`（无论字符串还是 time 对象）静默无效**（实测 date 为零值）；唯一可靠写法是 `"dates" (dict "date" (time "..."))`——这正是 v0.164.0 官方集成测试的写法。注意官方文档 transform.PortableText 示例用了顶层 `"date"`，**与实现矛盾，以集成测试为准**。设 `dates.date` 后，lastmod/publishDate 按 frontmatter 回退链自动补齐。
8. **页面冲突**：adapter 生成页与同目录 .md 同路径时结果不确定（并发构建），用 `--printPathWarnings` 检测（0.126.x 起支持，commit 6b006616）。adapter 与同目录 `_index.md` 共存曾有一个 bug，修复于 2025-12-25（commit d4c0e445）→ **0.164 已修复**（0.167 实证共存正常）。
9. **0.126.0 的两个已知 bug 均已在 0.126.1 修复**（path 含点被截断 #12493；mixed-case params 39cf906b）→ 0.164 无此问题。
10. **多语言**：默认只为 gotmpl 文件定义的语言执行；`.EnableAllLanguages` / `.EnableAllDimensions` 可扩展（`EnableAllDimensions` 及 page map 的 `sites` 键 0.164 适用，对应 v0.153.0 的 sites matrix 维度扩展）。

### 引用

- 官方文档 Content adapters：https://gohugo.io/content-management/content-adapters/ （AddPage/AddResource/Site/Store/EnableAllLanguages/EnableAllDimensions 方法表、page map 字段表、taxonomy keys 须入 params、"Site not fully initialized"）
- v0.164.0 源码 `hugolib/pagesfromdata/pagesfromgotmpl.go`：https://github.com/gohugoio/hugo/blob/v0.164.0/hugolib/pagesfromdata/pagesfromgotmpl.go （AddPage 签名、`io.Discard`、EnableAllDimensions）
- v0.164.0 源码 `resources/page/pagemeta/page_frontmatter.go`：https://github.com/gohugoio/hugo/blob/v0.164.0/resources/page/pagemeta/page_frontmatter.go （PageConfigEarly/PageConfigLate 字段全集、`Init()` 的 home/empty-path 与 markup 限制、contentAdapterDatesHandler）
- v0.164.0 官方集成测试：https://github.com/gohugoio/hugo/blob/v0.164.0/hugolib/pagesfromdata/pagesfromgotmpl_integration_test.go （`"dates" (dict "date" $date)` 规范写法与期望值）
- v0.126.0 release notes：https://github.com/gohugoio/hugo/releases/tag/v0.126.0
- Issue #12493（path 含点截断，0.126.1 修复）：https://github.com/gohugoio/hugo/issues/12493
- jmooring 2026-07 回复（kind/draft/description 必须顶层、不能放 params）：https://discourse.gohugo.io/t/one-of-two-content-adapters-from-the-same-data-isnt-building-pages-although-the-list-page-is-correct/57379
- os.ReadFile 文档：https://gohugo.io/functions/os/readfile/

## Q2 Module mounts

1. **可以挂载**：`[[module.mounts]] source = 'docs/sop'` + `target = 'content/posts'`。官方定义："A mount is a configuration object that maps a file path (source) to a component path (target) within Hugo's unified file system"，target 必须以 component 目录开头。**0.164 完全适用**。
2. **默认 mount 陷阱**：在项目配置里给某 component 定义 mount 会**移除该 component 的全部默认 mount**——必须显式写回 `source='content', target='content'`，否则 content/ 其余内容（about.md、products.md、search.md）全部消失。
3. **粒度陷阱**：docs/sop 下所有文件（含 README.md、MAPLEFLOW_BLOG_SOP.md）都会变成文章 → 需 `files` glob 过滤（`files` 键 **v0.153.0 新增，0.164 适用**；旧的 excludeFiles/includeFiles 在 0.153.0 已弃用）。
4. **URL/slug 决定**：挂载文件**保持文件名**；文件名（去扩展名）即 slug；**URL 默认小写化**（`disablePathToLower` 默认 false）；源文件 front matter 里的 `slug`/`url` **优先于文件名**。**实证**（0.167）：`docs/ANSIBLE_SOP.md`（无 front matter）→ `/posts/ansible_sop.html`；`docs/GITLAB_SOP.md`（front matter `slug='sop-gitlab-cicd-guide'`）→ `/posts/sop-gitlab-cicd-guide.html`。
5. **front matter 注入/改写：不能**。mounts 的键只有 `source`/`target`/`files`/`sites`/`disableWatch`，无任何 front matter 注入能力。间接手段只有 `content/posts/_index.md` 的 `cascade`（后代已定义该字段则不注入；可用 `target.path` glob 限定范围）——只能设**共性值**，无法按文章差异化设置 title/date/tags。
6. **磁盘行为：纯内存虚拟**。**实证**：挂载后 content/posts/ 与 docs/ 磁盘均零变化，页面正常生成、taxonomy 页面正常产出。
7. **与 uglyURLs=true 交互**：正常，`.html` 后缀（实证 `/posts/ansible_sop.html`）。
8. **本方案对 mapleFlow 的硬伤**：docs/sop 源笔记**完全没有 front matter**（已核实：ANSIBLE_SOP.md 等 8 个文件均以 `# 标题` 开头）。**实证**：无 front matter 的挂载文件 → `title` 为空、`date` 为零值（0001-01-01）、无 categories/tags（且 Hugo 不会从文件名或 H1 回退 title——源码 `applyDefaultValues` 对 regular page 无回退分支）。即 mounts 方案要保住现有文章元数据，必须往源笔记补写 front matter。

### 引用

- 官方文档 Configure modules（mounts 节）：https://gohugo.io/configuration/module/ （mount 定义、默认 mount 移除规则、source/target/files/sites/disableWatch 键、v0.153.0 弃用说明）
- 官方配置参考（disablePathToLower 默认 false）：https://gohugo.io/configuration/all/
- 官方 Front matter 文档（cascade 语义与 target）：https://gohugo.io/content-management/front-matter/
- v0.164.0 源码 `hugolib/page__meta.go`（`applyDefaultValues`：regular page 无 title 回退）：https://github.com/gohugoio/hugo/blob/v0.164.0/hugolib/page__meta.go

## Q3 其他单真源机制枚举

| 机制 | 一句话机制 | 0.164 适用 | 磁盘单份 .md？ | front matter 可控？ |
|---|---|---|---|---|
| page bundles | leaf/branch bundle 组织内容与资源，仍是磁盘 .md | ✅ | ❌（每篇一个文件） | ✅ 但是第二份 |
| headless pages | `build.list/render=never` 不发布 HTML，仅作数据容器被 `.Site.GetPage` 取出嵌入他页 | ✅ | ❌（源 .md 仍在 content/） | ✅ 但是第二份；且不产生独立 URL |
| render hooks | Markdown→HTML 渲染期转换，**不创建页面** | ✅ | —（与单真源无关） | — |
| `resources.Get` + `transform.Unmarshal` | 从 assets/（或挂载到 assets 的目录）读数据文件，模板里 range 输出；**不创建真实页面**（无独立 URL/taxonomy/RSS 条目）——这正是 0.126 引入 adapters 的动机（issue #5074） | ✅（`format` 选项 v0.149.0 新增） | ✅（数据文件可放 assets/） | ✅（元数据随数据携带）但产出非真页面 |
| git symlink | content/posts 里放指向 docs/sop 的 symlink | ❌ **0.164 不可行** | — | — |
| Hugo Modules | 把 docs/sop 做成 module 再 mounts——mounts 的远程版，机制完全相同（虚拟、无 front matter 注入、需源文件自带 front matter） | ✅ | ✅（虚拟） | ✅（须写入源文件）；单仓库场景只增 go.mod 复杂度 |
| cascade（补充） | 在 `_index.md` 向后代注入共性 front matter；adapter 页也受 cascade（commit c745a3e1，0.148.x） | ✅ | — | 仅共性值，不能差异化 |
| 构建外脚本生成（补充，非 Hugo 机制） | CI/Makefile 从 docs/sop 生成 content/posts/*.md | ✅ | ❌（磁盘两份，但自动同步） | ✅；是唯一让 backend/grep 继续工作的方案 |

**关键排雷**：git symlink 路线**出局**。Hugo 安全公告 GHSA-c3wq-j5vh-68rc（影响 v0.123.0–v0.163.0，修复于 **v0.163.1**，2026-06-11）：修复 PR #15020 标题即 "Drop symlinks in os.ReadDir, os.ReadFile, os.Stat and os.FileExists"——unified filesystem 自此把 symlink 当不存在。0.164 > 0.163.1 → CI 环境下 content/posts/ 里的 symlink 确定被丢弃。

**综合判断**：只有 **content adapters** 能同时满足「磁盘单份 .md（真源在 docs/sop）」+「front matter 全可控」+「真页面（独立 URL/taxonomy/RSS/搜索索引）」。

### 引用

- Build options（headless）：https://gohugo.io/content-management/build-options/
- Render hooks 引言：https://gohugo.io/render-hooks/introduction
- transform.Unmarshal：https://gohugo.io/functions/transform/unmarshal/
- Issue #5074（"Build pages from data source"，adapters 的起源）：https://github.com/gohugoio/hugo/issues/5074
- 安全公告 GHSA-c3wq-j5vh-68rc：https://github.com/gohugoio/hugo/security/advisories/GHSA-c3wq-j5vh-68rc ；修复 PR #15020：https://github.com/gohugoio/hugo/pull/15020 ；v0.163.1：https://github.com/gohugoio/hugo/releases/tag/v0.163.1
- Hugo Modules 配置（与 mounts 同一机制）：https://gohugo.io/configuration/module/

## Q4 磁盘消费者影响

**(a) backend 的 Python 文件解析会看到什么**：`backend/blog_parser.py` 通过 `settings.blog_content_path`（默认 `"content/posts"`）的 `glob("*.md")` 取文（blog_parser.py:110-116；config.py:24）。adapter 化后 content/posts/ 下没有任何 `.md`（`_content.gotmpl` 不匹配 `*.md`）→ `get_all_blog_posts()` 返回 `[]` → `/api/posts` 空列表；`get_blog_post_by_slug()` 返回 `None`。注意改指 `docs/sop` 也救不了它：源笔记无 front matter（`parse_front_matter` 取不到 title/date/categories/tags，会回退 'Untitled'/now），且文件名 slug 语义断裂（`ANSIBLE_SOP.md` vs `sop-ansible-automation-guide.html`，`slug = file_path.stem`）。

**(b) 有没有选项把生成页落盘**：**没有**。证据链：① 0.164.0 源码中 AddPage→HandlePage 只写内存 page map，`Execute` 输出 `io.Discard`，无写 .md 路径；② 官方文档与全部配置项无相关选项；③ 未找到任何 issue/feature request 声称可以（**未验证**：不能穷尽社区讨论，但官方渠道 0.164 确定无此能力）。反向选项只有 `--renderToMemory`（连 public/ 都不落盘）。

**(c) 对 grep / CI 断言 / AI 代理导航的后果**：
- 文章正文与 front matter 只存在于构建期内存；`grep -r content/posts` 找不到任何文章，唯一可 grep 真源变成 `docs/sop/` + `content/posts/_content.gotmpl`。
- 现有 CI 断言 `tests/assert_product_states.py` **不受影响**——它只消费构建产物（products.html / index.html / index.json），不碰 content/posts 磁盘文件。但任何未来针对 `content/posts/*.md` 的断言都会挂。
- AI 代理/编辑器文件树导航看不到生成文章（它们不在磁盘上）；PaperMod 站内搜索走 Hugo 生成的 `index.json`，不受影响。
- 需要新增的守门：`--printPathWarnings`（防 adapter 页与残留 .md 撞路径）。

### 引用

- `backend/blog_parser.py` / `backend/config.py`（mapleFlow 仓库，已核实）
- `tests/assert_product_states.py`（mapleFlow 仓库，只消费 public/ 产物）
- v0.164.0 源码（内存态证据）：https://github.com/gohugoio/hugo/blob/v0.164.0/hugolib/pagesfromdata/pagesfromgotmpl.go
- `--renderToMemory` flag：https://gohugo.io/commands/hugo/

## Q5 CI 复现性

1. **flags 官方语义**：`--gc` = "enable to run some cleanup tasks (remove unused cache files) after the build"；`--minify` = "minify any supported output format (HTML, XML etc.)"；`--cleanDestinationDir` = "remove stale files from destination"。
2. **与 content adapters 组合：无已知坑**。**实证**（0.167）：`hugo --gc --minify --cleanDestinationDir` 构建 adapter 站点成功，minify 生效，磁盘零写入。机制上三者互不相交：`--gc` 清缓存文件、`--cleanDestinationDir` 清 public/ 陈旧产物、`--minify` 只作用于输出格式；adapter 只影响内存页面集合。
3. **0.126 → 0.164 content adapters 破坏性变更排查**（release notes + pagesfromdata 目录提交历史）：
   - v0.126.0（2024-05-14）引入；v0.126.1 修 path 含点截断（#12493）与 mixed-case params。
   - v0.128.x：AddPage 支持 menus（245928a1）。
   - v0.146.0（2025-04-10）：模板系统重写（83cfdd78）——adapter 模板改由新 TemplateStore 执行；与是否采用 adapter 正交。
   - v0.148.0（2025-06）：**破坏性变更（与本站 uglyURLs=true 直接相关）**——修复 home/section/taxonomy 的 uglyURLs 错误（#4428、#7497）+ OutputFormat.Path 分支路径（#13829）。**0.126–0.147 与 0.148+ 的 URL 行为不同；CI 0.164 = 修复后行为。**
   - v0.149.0（2025-08-27）：删除 adapter 文件后 rebuild 修复（87e100e）。
   - v0.153.0（2025-12-19）：mounts `files`/`sites` 键；sites matrix 维度扩展。
   - v0.163.1（2026-06-11）：symlink 丢弃（安全修复）。
   - v0.164.0（2026-07-06）：无 adapter 相关破坏性变更；修复 v0.128.0 引入的性能回归。
4. **结论**：AddPage 的 map 语义 0.126→0.164 **保持兼容**。区间内的破坏性变更（v0.146.0 模板系统、v0.148.0 uglyURLs/OutputFormat.Path）与「是否采用 adapter」正交，但因本站 `uglyURLs=true`，**一切 URL 断言必须以 0.148+ 修复后行为为准**。CI 0.164 vs 本机 0.167：本次全部实证（adapter 内存生成、mounts 虚拟、`dates` 嵌套写法、Site.Pages 执行期报错、uglyURLs 落 .html）在 0.167 上复现了 0.164 源码/文档语义。

### 引用

- hugo 命令 flags 文档：https://gohugo.io/commands/hugo/
- v0.148.0 release notes（uglyURLs 破坏性变更 + home pages from content adapters）：https://github.com/gohugoio/hugo/releases/tag/v0.148.0
- Issue #4428：https://github.com/gohugoio/hugo/issues/4428 ；Issue #7497：https://github.com/gohugoio/hugo/issues/7497 ；Issue #13829：https://github.com/gohugoio/hugo/issues/13829
- v0.127.0 / v0.146.0 / v0.149.0 / v0.153.0 / v0.163.1 / v0.164.0 release notes（GitHub releases/tag 页，发布日期已核实）
- pagesfromdata 目录提交历史（GitHub commits API，2024-05～2026-09 全量）

## 对 seam 决策的含义

1. **只有 content adapters 同时满足三个硬约束**（磁盘单份 .md、front matter 全可控、真页面）；mounts 只是虚拟视图——docs/sop 是唯一磁盘真源，但 backend/grep/AI 导航看到的 content/posts 是空目录。若「backend 不断供」也是硬约束，则只剩「构建外脚本生成」（磁盘两份、自动同步）这条路。
2. **adapter 方案的直接代价是 `/api/posts` 断供**（`glob("*.md")` 落空，实证+源码级确定）。seam 决策必须同时裁决 backend 取数改道：读 `public/` 产物、用 Hugo custom output 产出 JSON API、或接受该接口退役——不能只改 Hugo 侧。
3. **mounts 方案的两个隐性成本**：① docs/sop 必须补 front matter（现在 8 个文件全无），否则 title 空/date 零值/tags 全丢（实证，且 Hugo 不从文件名或 H1 回退 title）；② slug 由文件名决定且默认小写——`ANSIBLE_SOP.md` → `/posts/ansible_sop.html`，与现有 `/posts/sop-ansible-automation-guide.html` 不一致，要么逐篇加 `slug`，要么接受线上 URL 变更（SEO/外链风险）。
4. **日期写法是隐藏 seam**：普通 .md 里 `date = '...'` 字符串的写法搬到 adapter page map 会**静默失效**（必须 `"dates" (dict "date" (time "..."))`，实证 0.167 + v0.164 官方集成测试；官方文档 PortableText 示例本身是错的）。迁移时若照抄文档示例，全部文章日期变零值，排序/归档/RSS 静默错乱。
5. **CI 钉 0.164 使 0.148.0 的 uglyURLs 修复行为成为唯一行为**；本机 0.167 与 CI 0.164 在本次涉及的所有机制上行为一致。git symlink 路线因 v0.163.1 安全修复（0.164 确定丢弃 symlink）出局，不必再评估；Hugo Modules 与 mounts 同机制，单仓库场景无增益。
6. **CI flags 组合无坑**。真正值得新增的守门是 `--printPathWarnings`（撞路径检测）与 adapter 模板内 `errorf` 契约（构建期失败即断部署，对应现有 assert_product_states.py 的「契约坏用例必须构建失败」模式）。

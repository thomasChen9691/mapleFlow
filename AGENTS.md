# AGENTS.md — MapleFlow 博客项目（AI 编码代理须知）

本文件为 AI 编码代理（Claude Code / Codex / CodeBuddy 等）提供项目上下文与操作约束。
若同时读取到 `CLAUDE.md`，其内容与本文件一致。

## 1. 项目概览

- **性质**：使用 **Hugo** + **maplemod** 主题构建的个人技术博客，部署在 **GitHub Pages**。
- **主题**：`themes/maplemod` 是**仓内第一方主题**（2026-10 自 PaperMod v8.0-55 fork 并修剪；无子模块、无上游同步义务）。
- **内容方向**：运维开发 / SRE / DevOps 实战 SOP，覆盖 Kubernetes、Docker、CI/CD、AIOps、Prometheus、Grafana、Jenkins、GitLab、Ansible、SonarQube，见 `docs/sop/`。

## 2. 分支模型（重要）

| 分支 | 用途 | 操作权限 |
|------|------|----------|
| `main` | 源码与配置；所有开发工作在此分支 | 你应在此分支工作 |
| `gh-pages` | 由 GitHub Actions 自动构建的静态站点产物 | **不要手动修改/提交** |
| `origin/main` | 远端源码；推送到它会触发部署 | 仅通过 push 更新 |

- 部署流水线见 `.github/workflows/deploy.yml`：push `main` → 检出 → `hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml` → 推 `gh-pages`。
- 切勿直接编辑 `gh-pages` 或本地 `public/`（构建产物会覆盖）。

## 3. 核心命令

```bash
# 安装 Hugo（extended 版，必需）
# Windows:  winget install Hugo.Hugo.Extended
# macOS:    brew install hugo
# 验证:     hugo version   （CI 钉 0.164.0；本机版本不同不会让断言变红，
#                            但证明不了 CI 会绿——测试启动会打 WARN，见 ADR-0004）

# 本地开发预览（含草稿）—— 只用 hugo.toml，不要带生产配置！
hugo server -D        # 访问 http://localhost:1313/
# ⚠️ 禁止：hugo server -D --config hugo.toml,config.production.toml
#   生产配置 baseURL 带 /mapleFlow/ 子路径，但 hugo server 在根 / 提供文件，
#   会让 HTML 里 /mapleFlow/assets/... 的 CSS 链接 404 → 整页没样式（已实测踩坑）。
#   若观感"颜色/字体全没了"，先确认预览服务是 dev 配置、且用 http://localhost:1313/ 根路径打开。

# 生产构建（必须与 CI 命令完全一致！不能只跑 hugo）
hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml

# 【本地验证推荐】多一个 --cleanDestinationDir，可清掉草稿孤儿文件（见坑点 5b）
hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml

# 提交（见 §6 规范）
python3 auto_push.py                       # 自动 add/commit/push 到 main

# reveal 协议行为断言（jsdom；依赖声明见 package.json，首次先 npm ci）
npm test

# 站点契约断言（产品状态 / 产品索引 / 主题契约 B7-B14 / reveal 产物 / 文章精选 /
#               搜索索引投影 / 搜索交付面与 fastsearch 守门 / 搜索入口构件与加载面，共八类）
# 原名 tests/assert_product_states.py——2026-10 职责扩张后改名；ADR 与历史 handoff
# 里的旧名指的就是本脚本。
python3 tests/assert_site_contracts.py
```

## 4. 必知坑点（改动前先读）

1. **构建必须合并两个配置**：`hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml`。
   `config.production.toml` 提供 `baseURL` 与 `uglyURLs = true`。单独跑 `hugo` 会用 `localhost` 且路径不同。

2. **`uglyURLs = true` → 页面是 `.html` 文件**：
   - 顶层页面 `content/about.md` → `/about.html`（**不是** `/about/`）。
   - 菜单 `url` 必须写成 `/about.html`，否则 404。
   - **不要**把独立页面放在 `content/page/` 下（会变成 `/page/about.html` 分区，破坏干净 URL）。

3. **hugo.toml 参数纪律**：每个参数必须在 `themes/maplemod` 里有读取点（`grep -rn "<param>" themes/maplemod/layouts`）。**无读取点即死配置——删掉，不要留「文档价值」**（0029 已清 14 个）。新增参数前先证明读取点存在；导航顺序的唯一来源是 `[[menu.main]]` 的 `weight`（header.html 只渲染顶层项，而 Hugo 的 `site.Menus.main` **本就不含 `parent` 子项**——子项配置零读取点，2026-10-23 已删 4 条）。

4. **自定义样式放哪**：写入 `assets/css/extended/*.css`，Hugo Pipes 会自动并入主题样式表（已验证 `2D7FF9` 变量并入 `public/assets/css/...`）。不要放 `static/css/` 并用 `customCSS` 引用。

5. **Windows 上删除大量文件很慢**：`Remove-Item public -Recurse` 会触发 Defender 全量扫描而超时。
   重建时**直接再跑一次 hugo 构建**即可（Hugo 会覆盖变更文件），无需先删 `public`。
   **例外见 5b：存在孤儿文件时此建议不成立。**

5b. **草稿孤儿文件会让线上残留 `localhost:1313`（已实测踩坑）**：
   流程：本地跑过 `hugo server -D`（含草稿）→ 生成了草稿专属的分类/标签页（如 `categories/随笔/`）
   → 之后跑生产构建（不含草稿）→ Hugo **不会删除**这些已生成的页面，成为孤儿文件。
   后果：`grep -r "localhost:1313" public/` 命中，这些页面带着 localhost 绝对链接被推上线。
   排查：`ls -la public/<可疑路径>`，若修改时间早于本次构建时间即为孤儿。
   修复：生产构建加 `--cleanDestinationDir`（Hugo 内部清理，比 `rm -rf public` 快得多）：
   ```bash
   hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml
   ```
   验证：`grep -r "localhost:1313" public/` 必须无输出。
   注：CI（GitHub Actions）每次全新 checkout，`public/` 本就为空，不受此问题影响。

6. **图片/资源在 GitHub Pages 子路径下**：站点部署在 `.../mapleFlow/`（非根域）。页面内联 SVG 头像比引用 `static/img/*` 更稳；若引用静态资源，路径需相对正确。

7. **`public/` 为构建产物，当前未被 git 跟踪**（`git ls-files | grep '^public/'` → 0 文件）：`git add .` 不会包含它，真正对外的是 `gh-pages`，不必纠结 `main` 上的 `public`。

8. **SOP 文是构建期派生的，不要手写**（wayfinder 工单 0008/0009）：`content/posts/` 下 6 个 `sop-*.md` 已删除，文章由 `content/posts/_content.gotmpl`（seam）从 `data/sop.yaml` 注册表 + `docs/sop/` 源笔记在构建期生成，磁盘上没有第二份 .md。手写同名 .md 会与派生页撞路径（产物不确定），由「无残留」断言守。改 SOP 内容 = 改 `docs/sop/` 笔记；改 web 包装（标题由笔记 H1 承载，日期/分类/标签/描述/导语在注册表）= 改 `data/sop.yaml`。无注册条目的笔记 = 尚未发布的稿件；已注册的草稿 = 条目 `draft: true`（不进生产构建）。契约五类以 errorf 让构建失败：缺必填字段（slug/note/date/categories，tags 可缺省）、死条目（有条目无笔记）、笔记首行无 H1、H1 之后无章节标题行、`featured` 存在但非布尔（2026-10 精选机制；缺省即非精选）。测试 `python3 tests/assert_sop_pipeline.py`（CI 权威、本地 advisory，改动前先跑）。

9. **产品索引接口纪律：双 seam，不要绕（ADR-0006；候选 4 全决议）**：`layouts/partials/product-items.html`（数据准备）是指渲染链**唯一读 `hugo.Data.products` 的宿主**——featured 过滤、limit 截断（缺省/0=全量，负数 errorf）、交付形态词汇契约（`workflow`/`document`/`question-bank` 封闭集，词表外 kind 即 errorf，消息前缀「产品索引数据：」）、**featured 必须是布尔（非 bool 即 errorf，2026-10 跨类统一）**都只此一处；`layouts/partials/product-index.html`（纯渲染）零全局读，`items`/`uid` 必填（缺失即构建失败），空态文案归它。调用方（短代码、首页 `layouts/index.html` 精选区）不得自行 `where`/`first`/直读 `site.Data.products` 渲染列表。同页多实例 uid 必须不同：短代码由 `.Ordinal` 保唯一，模板调用方传字面量（重名不执法，partial 无页级视野）。搜索索引（`layouts/_default/index.json`）与首页计数条不随本链（前者有独立契约，见坑点 13 与 ADR-0010；后者见 ADR-0004）。改本链先跑 `python3 tests/assert_site_contracts.py`。

10. **reveal 协议契约纪律（ADR-0007）**：DOM 契约（class / data-* / aria / CSS 变量）的**定义处是 `assets/js/mf-reveal/` 各引擎文件头 docstring**，不在 CONTEXT.md 术语表（术语只放概念）。改契约 = 改 docstring + 同步断言，先跑 `npm test`（行为）与 `python3 tests/assert_site_contracts.py`（产物）。引擎经 `extend_footer` 的 js.Build 加载，不要改回内联 script；`extend_head` 的 class swap 是 ADR-0002 基线的一部分，保持内联。

11. **文章精选纪律：单 seam 三片，不要绕（ADR-0009；候选 7 全决议）**：`layouts/partials/post-items.html`（数据准备）是首页精选链**唯一**读 `site.RegularPages` 并做 featured 判定 / 截断 / 补集处；入参只收 `limit`（负数 errorf），一次返回 `{featured, rest, all}`，**渲染不抽**（精选编号行 / 网格卡片两套形态，强行统一会引入模式参数）。三条硬约束：① **补集必须对「实际显示的精选」求**（`complement $featured $pages`）——用 `where "Params.featured" "!=" true` 会把被 limit 截断的文章从首页彻底抹掉（静默丢内容）；② featured **只认布尔 `true`**，非布尔即 errorf（`if .Params.featured` 禁止：字符串 `"false"` 是真值）；③ 精选区与网格在各自集合为空时**整块不渲染**。改本链先跑 `python3 tests/assert_site_contracts.py`。
12. **测试 fixture 的时间陷阱**：Hugo 默认**不发布未来日期的内容**——fixture 文章写成未来日期会整篇消失，表现为「区块不渲染」的假绿（2026-10-22 踩过）。fixture 日期一律用过去的确定日；判定区块是否渲染要锚 DOM class（如 `class=mf-posts` / `entry-link`），不要用文案子串（首页数据条有「最近更新」等同名标签）。

13. **搜索契约纪律：两个定义处，三处同步（ADR-0010；候选 8 全决议）**：投影契约的定义处是 `layouts/_default/index.json` 文件头 docstring（**六字段冻结**——featured / kind 不投影，0044 负向决策；产品 name/summary 缺失即 errorf，前缀「搜索索引数据：」）；检索契约的定义处是 `themes/maplemod/assets/js/fastsearch.js` 文件头 docstring（**现状快照**：fuseOpts 参数位已删，默认值 threshold 0.4 / distance 100 / ignoreLocation true / keys 四字段就是契约）。三条硬约束：① **改投影字段 = 三处同步**（投影 docstring / fastsearch keys / 差集断言）——差集恰为 tags/categories，多一个字段就红；② **fastsearch.js 禁项目级 assets 覆盖复活**——单副本守门断言会红（2026-10 翻车实录：项目级 `assets/js/fastsearch.js` 曾是活文件、主题层副本是死的，`resources.Get` 项目级优先）；③ fixture 造搜索相关页面时日期用过去日（坑点 12）。kind 门禁归产品索引链（索引零暴露，见坑点 9 与 0045 定案）。测试 `python3 tests/assert_site_contracts.py`（投影 / 交付面 / 守门）。

## 5. 内容规范

- 文章：`content/posts/<slug>.md`。新增：`hugo new posts/xxx.md`（套用 `archetypes/default.md`）。
- front matter 至少包含：`title`、`date`、`draft = false`（否则线上不显示）、`categories`、`tags`。
- 简历/关于页：`content/about.md`（已含技能胶囊、时间线、项目卡片，使用内联 SVG）。当前为 **TEST 测试占位内容**（姓名「测试用户」/ 邮箱 `test@example.com` / GitHub `test-user` / 公司「测试公司 A·B」等），文件内以 `TEST` 与 HTML 注释标注；上线前替换为真实信息（**没有** `TODO:` 标注）。
- `docs/sop/*.md` 是源笔记，**不在** Hugo `content` 内，不会被渲染成页面。
- 中文日期由 Hugo/goldmark 原生支持，无需额外 JS 配置。

## 6. 提交规范

- 使用 **纯 ASCII** commit message（避免 Windows 控制台编码导致乱码）。例：`update: 2026-07-17 refine about page`。
- 推荐：`python3 auto_push.py`（自动 `add .` + ASCII 提交 + `push origin main`）。
- **不要** `git push` 到 `gh-pages`；也不要 `git commit` 前不确认改动范围。
- 改动完成后不要自动假设已提交；按规范交给用户审阅。

## 7. 关键文件速查

| 文件 | 作用 |
|------|------|
| `hugo.toml` | 主配置：站点信息、菜单 `[[menu.main]]`、`homeInfoParams`、`socialIcons`、品牌色 |
| `config.production.toml` | 生产 `baseURL` + `uglyURLs = true`（部署必需） |
| `themes/maplemod/` | 主题层（呈现与行为基线）：骨架/导航/文章与列表渲染/交互钩子/社交元数据；导航见其 README；无上游同步义务（0033 cut cord）；主题契约测试 B7-B13 见 `tests/assert_site_contracts.py` |
| `content/about.md` | 简历/关于页 |
| `assets/css/extended/custom.css` | 品牌样式（明暗双主题 CSS 变量） |
| `static/img/avatar.svg` | 占位头像 |
| `themes/maplemod/layouts/partials/post_meta.html` | 文章元信息（日期悬浮提示显式时区格式，消除「构建机器时区决定输出字节」）；主题层文件，无同步义务（0030 合并后站点层无覆盖） |
| `.github/workflows/deploy.yml` | 自动部署流水线 |
| `docs/sop/` | 运维 SOP 源笔记 |
| `layouts/partials/product-state.html` | 产品状态模块：上架/免费判定 + 控件语义（ADR-0004；测试 `tests/assert_site_contracts.py`，改动前先跑） |
| `layouts/partials/product-items.html` | 产品索引·数据准备 seam：索引渲染链唯一读 `hugo.Data.products` 处，featured 过滤（只认布尔 true，非 bool 即 errorf）+ limit 截断（缺省/0=全量，负数 errorf）+ 交付形态词汇契约（词表外 kind 即 errorf）。ADR-0006；测试 `tests/assert_site_contracts.py`，改动前先跑 |
| `layouts/partials/post-items.html` | 文章精选·数据准备 seam：首页精选链**唯一**读 `site.RegularPages` 并做 featured 判定/截断/补集处。入参 `limit`（精选条数，负数 errorf）；一次返回 `{featured, rest, all}` 三片，`rest` 对**实际显示的精选**求补集（被截断的 featured 必须回落到网格）；featured 只认布尔 true、非 bool 即 errorf。候选 7 决议；测试 `tests/assert_site_contracts.py`，改动前先跑 |
| `layouts/partials/product-index.html` | 产品索引·纯渲染 seam：零全局读，只渲染传入 items；`items`/`uid` 必填（缺失即构建失败），筛选 UI（交互行为归 reveal 协议引擎 `assets/js/mf-reveal/`）。ADR-0006；测试 `tests/assert_site_contracts.py`，改动前先跑 |
| `assets/js/mf-reveal/` | reveal 协议引擎（**契约定义处**）：app.js 入口 / filter.js 筛选 / scroll-in.js 滚动进场 / reduced-motion.js 降级判定。ADR-0007；测试 `npm test`（行为）+ `tests/assert_site_contracts.py`（产物），改动前先跑 |
| `layouts/_default/index.json` | 搜索索引·投影契约（**唯一定义处**）：六字段冻结 + 三类排除 + 产品投影；产品 name/summary 缺失即 errorf；与 fastsearch 的 keys 对齐由断言执法。ADR-0010；测试 `tests/assert_site_contracts.py`，改动前先跑 |
| `themes/maplemod/assets/js/fastsearch.js` | 搜索协议·检索契约（**唯一定义处**，现状快照）：挂点 / `.focus` / li 结构 / 键盘语义 / XHR 容错；fuseOpts 参数位已删、默认值是契约；禁项目级 assets 覆盖复活（单副本守门断言）。ADR-0010；测试 `tests/assert_site_contracts.py`，改动前先跑 |
| `content/posts/_content.gotmpl` | SOP 发布管线 seam：`data/sop.yaml` 注册表 + `docs/sop/` 源笔记 → 构建期派生文章（ADR-0005；契约 errorf 执法；测试 `tests/assert_sop_pipeline.py`，改动前先跑） |
| `data/sop.yaml` | SOP 发布注册表：slug/note/date/categories 必填，tags 可缺省，`draft: true` = 已注册的草稿，`featured` 可选（缺省即非精选、非布尔即构建失败） |
| `docs/sop/README.md` | 源笔记索引（与注册表双向漂移断言守护；`MAPLEFLOW_BLOG_SOP.md` 不发布） |

## 8. 工程纪律（realeng）

1. 任何会话（含更换模型后的新会话）第一步：读 `CONTEXT.md` 与 `docs/adr/`。术语以 `CONTEXT.md` 为准，禁止另造同义词。
2. 已被 ADR 记录的决策，禁止重新推导；认为 ADR 错了，先提出重审，不许默认推翻。
3. 难逆决策才写 ADR（难逆转 + 无上下文会惊讶 + 源于真实权衡，三条件齐备）。
4. 讨论中敲定的术语，当场更新 `CONTEXT.md`，不攒批。
5. 每批次单独 commit，commit message 说明改动意图。
6. 会话收尾用 realeng-handoff 压缩交接，长期接力文档存 `docs/handoffs/`。

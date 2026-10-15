# AGENTS.md — MapleFlow 博客项目（AI 编码代理须知）

本文件为 AI 编码代理（Claude Code / Codex / CodeBuddy 等）提供项目上下文与操作约束。
若同时读取到 `CLAUDE.md`，其内容与本文件一致。

## 1. 项目概览

- **性质**：使用 **Hugo** + **PaperMod** 主题构建的个人技术博客，部署在 **GitHub Pages**。
- **主题**：`themes/PaperMod` 是 Git **子模块**（`.gitmodules` 指向 `adityatelange/hugo-PaperMod`）。
- **内容方向**：运维开发 / SRE / DevOps 实战 SOP，覆盖 Kubernetes、Docker、CI/CD、AIOps、Prometheus、Grafana、Jenkins、GitLab、Ansible、SonarQube，见 `docs/sop/`。
- **后端**：`backend/`（FastAPI）解析 `content/posts` 的 Markdown 并暴露内容 API（与静态站点解耦，不影响部署）。

## 2. 分支模型（重要）

| 分支 | 用途 | 操作权限 |
|------|------|----------|
| `main` | 源码与配置；所有开发工作在此分支 | 你应在此分支工作 |
| `gh-pages` | 由 GitHub Actions 自动构建的静态站点产物 | **不要手动修改/提交** |
| `origin/main` | 远端源码；推送到它会触发部署 | 仅通过 push 更新 |

- 部署流水线见 `.github/workflows/deploy.yml`：push `main` → 检出（含子模块）→ `hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml` → 推 `gh-pages`。
- 切勿直接编辑 `gh-pages` 或本地 `public/`（构建产物会覆盖）。

## 3. 核心命令

```bash
# 安装 Hugo（extended 版，必需）
# Windows:  winget install Hugo.Hugo.Extended
# macOS:    brew install hugo
# 验证:     hugo version   （需 0.154.5+）

# 首次初始化主题子模块（关键！否则 hugo 报 "found no layout file"）
git submodule update --init themes/PaperMod
# 若因代理/SSL 失败，先 git config --global --unset http(s).proxy 再试

# 本地开发预览（含草稿）—— 只用 hugo.toml，不要带生产配置！
hugo server -D        # 访问 http://localhost:1313/
# ⚠️ 禁止：hugo server -D --config hugo.toml,config.production.toml
#   生产配置 baseURL 带 /mapleFlow/ 子路径，但 hugo server 在根 / 提供文件，
#   会让 HTML 里 /mapleFlow/assets/... 的 CSS 链接 404 → 整页没样式（已实测踩坑）。
#   若观感"颜色/字体全没了"，先确认预览服务是 dev 配置、且用 http://localhost:1313/ 根路径打开。

# 生产构建（必须与 CI 命令完全一致！不能只跑 hugo）
hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml

# 【本地验证推荐】多一个 --cleanDestinationDir，可清掉草稿孤儿文件（见坑点 7b）
hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml

# 启动后端 API（可选）
pip install -r backend/requirements.txt   # 或：uv sync
python3 run_backend.py                     # http://0.0.0.0:8000

# 提交（见 §6 规范）
python3 auto_push.py                       # 自动 add/commit/push 到 main
```

## 4. 必知坑点（改动前先读）

1. **构建必须合并两个配置**：`hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml`。
   `config.production.toml` 提供 `baseURL` 与 `uglyURLs = true`。单独跑 `hugo` 会用 `localhost` 且路径不同。

2. **`uglyURLs = true` → 页面是 `.html` 文件**：
   - 顶层页面 `content/about.md` → `/about.html`（**不是** `/about/`）。
   - 菜单 `url` 必须写成 `/about.html`，否则 404。
   - **不要**把独立页面放在 `content/page/` 下（会变成 `/page/about.html` 分区，破坏干净 URL）。

3. **PaperMod 不识别以下配置**（加了完全无效，是「改了没效果」的常见原因，禁止新增）：
   - `[params.navItems]`（导航栏应由标准 `[[menu.main]]` 控制。注：`[params.reorderNavItems]` 在当前 PaperMod 版本中**同样不被读取**（已 grep 主题全目录 0 命中），保留仅为文档价值，改导航请直接改 `[[menu.main]]` 的 `weight`）
   - `lightTheme` / `darkTheme`（daisyUI 概念，PaperMod 用 `defaultTheme`）
   - `headerTitle`
   - `[params.advanced].customCSS` / `customJS`
   - `[params.experimental].jsDate`

4. **自定义样式放哪**：写入 `assets/css/extended/*.css`，Hugo Pipes 会自动并入主题样式表（已验证 `2D7FF9` 变量并入 `public/assets/css/...`）。不要放 `static/css/` 并用 `customCSS` 引用。

5. **`[params.homeInfoParams]` 只使用 `Title` 与 `Content` 字段**：PaperMod 的 `home_info.html` 不渲染 `ImageUrl`。首页头像请用文章页 `avatar` 参数或直接在 `Content`（HTML）里引图。

6. **切换/检出分支会卡死（网络）**：`git checkout main` 触发 PaperMod 子模块递归联网拉取而超时。
   **正确做法**：先关闭子模块递归：
   ```bash
   git -c submodule.recurse=false checkout -f main
   ```
   （本项目已踩过此坑；不要反复裸 `git checkout main` 或 `git worktree add` 而不加此开关。）

7. **Windows 上删除大量文件很慢**：`Remove-Item public -Recurse` 会触发 Defender 全量扫描而超时。
   重建时**直接再跑一次 hugo 构建**即可（Hugo 会覆盖变更文件），无需先删 `public`。
   **例外见 7b：存在孤儿文件时此建议不成立。**

7b. **草稿孤儿文件会让线上残留 `localhost:1313`（已实测踩坑）**：
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

8. **图片/资源在 GitHub Pages 子路径下**：站点部署在 `.../mapleFlow/`（非根域）。页面内联 SVG 头像比引用 `static/img/*` 更稳；若引用静态资源，路径需相对正确。

9. **`public/` 为构建产物，当前未被 git 跟踪**（`git ls-files | grep '^public/'` → 0 文件）：`git add .` 不会包含它，真正对外的是 `gh-pages`，不必纠结 `main` 上的 `public`。

10. **SOP 文是构建期派生的，不要手写**（wayfinder 工单 0008/0009）：`content/posts/` 下 6 个 `sop-*.md` 已删除，文章由 `content/posts/_content.gotmpl`（seam）从 `data/sop.yaml` 注册表 + `docs/sop/` 源笔记在构建期生成，磁盘上没有第二份 .md。手写同名 .md 会与派生页撞路径（产物不确定），由「无残留」断言守。改 SOP 内容 = 改 `docs/sop/` 笔记；改 web 包装（标题由笔记 H1 承载，日期/分类/标签/描述/导语在注册表）= 改 `data/sop.yaml`。无注册条目的笔记 = 尚未发布的稿件；已注册的草稿 = 条目 `draft: true`（不进生产构建）。契约四类以 errorf 让构建失败：缺 slug/note/date、死条目（有条目无笔记）、笔记首行无 H1、H1 之后无章节标题行。测试 `python3 tests/assert_sop_pipeline.py`（CI 权威、本地 advisory，改动前先跑）。

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

## 7. 后端（FastAPI，`backend/`）

- `main.py`：FastAPI app，端点 `/api/posts`（列表）、`/api/posts/{slug}`（单篇）、`/api/posts/search`（搜索）、`/health`。
- `blog_parser.py`：用 `tomli` 解析 `content/posts` 的 front matter 与正文。
- `models.py` / `config.py` / `requirements.txt`：数据模型、配置、依赖。
- 运行：`python3 run_backend.py`（端口 8000，热重载）。响应统一 UTF-8（`ensure_ascii=False`）以正确返回中文。
- 依赖：`pip install -r backend/requirements.txt` 或 `uv sync`（见 `pyproject.toml`）。
- 测试：`test_api.py`（运行 `python3 test_api.py`）。

## 8. 关键文件速查

| 文件 | 作用 |
|------|------|
| `hugo.toml` | 主配置：站点信息、菜单 `[[menu.main]]`、`reorderNavItems`、`homeInfoParams`、`socialIcons`、品牌色 |
| `config.production.toml` | 生产 `baseURL` + `uglyURLs = true`（部署必需） |
| `content/about.md` | 简历/关于页 |
| `assets/css/extended/custom.css` | 品牌样式（明暗双主题 CSS 变量） |
| `static/img/avatar.svg` | 占位头像 |
| `.github/workflows/deploy.yml` | 自动部署流水线 |
| `backend/` | 内容 API（FastAPI） |
| `docs/sop/` | 运维 SOP 源笔记 |
| `layouts/partials/product-state.html` | 产品状态模块：上架/免费判定 + 控件语义（ADR-0004；测试 `tests/assert_product_states.py`，改动前先跑） |
| `content/posts/_content.gotmpl` | SOP 发布管线 seam：`data/sop.yaml` 注册表 + `docs/sop/` 源笔记 → 构建期派生文章（契约 errorf 执法；测试 `tests/assert_sop_pipeline.py`，改动前先跑） |
| `data/sop.yaml` | SOP 发布注册表：slug/note/date 必填，tags 可缺省，`draft: true` = 已注册的草稿 |
| `docs/sop/README.md` | 源笔记索引（与注册表双向漂移断言守护；`MAPLEFLOW_BLOG_SOP.md` 不发布） |

## 9. 工程纪律（realeng）

1. 任何会话（含更换模型后的新会话）第一步：读 `CONTEXT.md` 与 `docs/adr/`。术语以 `CONTEXT.md` 为准，禁止另造同义词。
2. 已被 ADR 记录的决策，禁止重新推导；认为 ADR 错了，先提出重审，不许默认推翻。
3. 难逆决策才写 ADR（难逆转 + 无上下文会惊讶 + 源于真实权衡，三条件齐备）。
4. 讨论中敲定的术语，当场更新 `CONTEXT.md`，不攒批。
5. 每批次单独 commit，commit message 说明改动意图。
6. 会话收尾用 realeng-handoff 压缩交接，长期接力文档存 `docs/handoffs/`。

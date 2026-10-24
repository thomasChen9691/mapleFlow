# MapleFlow 博客维护标准操作规范（SOP）

> **文档状态**（2026-10-19 更新）：
> - 本文件**不在 SOP 注册表**（`data/sop.yaml`）中，不发布上线；仓库运维的权威指令以根目录 `AGENTS.md` 为准，本文件是其对外 SOP 化副本，**两者冲突时以 AGENTS.md 为准**。
> - 下文「启动后端内容 API」为历史指令：backend 已于 2026-10-16 退役（wayfinder 工单 0011、ADR-0003；`backend/` 目录已删除）。项目负责人计划未来重启后端开发，故该段**保留作参考**，但当前不可直接执行。若重启后端，ADR-0003 的语义裁决继续有效：后端只镜像、分歧时后端对齐 Hugo。

## 1. 简介

MapleFlow 是基于 **Hugo** 静态站点生成器 + **PaperMod** 主题构建的个人技术博客，部署在 **GitHub Pages**。
本 SOP 用于规范本仓库的日常维护操作：克隆初始化、新增文章、本地预览、生产构建、自动部署与常见故障排查。

- **典型场景**：写技术文章、调整站点品牌与导航、修复部署问题、本地预览草稿。
- **仓库分支**：`main`（源码，所有开发在此） / `gh-pages`（GitHub Actions 自动构建的静态产物，**禁止手改**）。
- **关键技术点**：主题以 Git 子模块 `themes/PaperMod` 引入；生产构建强制 `uglyURLs = true`；构建必须合并两份配置文件。

---

## 2. 安装与初始化

### 2.1 安装 Hugo（Extended 版，必需）

```bash
# Windows
winget install Hugo.Hugo.Extended
# macOS
brew install hugo
# Linux
sudo apt-get install hugo       # 部分发行版版本较旧，建议用官方二进制
# 验证
hugo version                    # 需 >= 0.154.5（extended）
```

> 注意：必须使用 **extended** 版本（支持 SASS/SCSS），否则 `assets/css/extended/custom.css` 经由 Hugo Pipes 处理时会报错。

### 2.2 克隆仓库并初始化子模块

```bash
git clone --recurse-submodules git@github.com:thomasChen9691/mapleFlow.git
cd mapleFlow
```

若已克隆但未带子模块（PaperMod 主题目录为空），补执行：

```bash
git submodule update --init --recursive
```

> **子模块拉取失败（代理/SSL）**：若报 `SSL_ERROR_SYSCALL` 或连接超时，先临时取消代理再拉取：
> ```bash
> git config --global --unset http.proxy
> git config --global --unset https.proxy
> git submodule update --init --recursive
> ```
> 仍失败可手动克隆主题：
> ```bash
> rmdir /s /q themes\PaperMod
> git clone https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
> ```

### 2.3 切换分支（关键坑点）

直接 `git checkout main` 会触发 PaperMod 子模块递归联网拉取而**超时卡死**。必须先关闭子模块递归：

```bash
git -c submodule.recurse=false checkout -f main
```

---

## 3. 常用命令

```bash
# 本地预览（含草稿 draft=true）
hugo server -D                 # http://localhost:1313/

# 生产构建（必须与 CI 完全一致：合并两份配置）
hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml

# 新增文章（套用 archetypes/default.md）
hugo new posts/my-new-post.md

# 启动后端内容 API（可选，FastAPI :8000）
# ⚠️ backend 已于 2026-10-16 退役（工单 0011 / ADR-0003，backend/ 目录已删除）。
#    以下指令保留仅为未来重启后端时参考，当前仓库中不可执行。
pip install -r backend/requirements.txt
python3 run_backend.py

# 一键提交并推送到 main（ASCII 提交信息，触发部署）
python3 auto_push.py
```

---

## 4. 日常操作流程

### 4.1 新增并发布一篇文章

1. 在 `main` 分支上创建文章：
   ```bash
   git -c submodule.recurse=false checkout -f main
   hugo new posts/<slug>.md
   ```
2. 编辑 `content/posts/<slug>.md` 的 front matter 与正文：
   ```toml
   title = "文章标题"
   date  = 2026-07-17T10:00:00+08:00
   draft = false            # 必须 false，否则线上不显示
   categories = ["运维"]
   tags   = ["Hugo", "示例"]
   ```
3. 本地预览确认：
   ```bash
   hugo server -D
   ```
4. 生产构建验证（不带 `--minify` 也行，但建议与 CI 一致）：
   ```bash
   hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml
   ```
5. 提交推送，触发自动部署：
   ```bash
   python3 auto_push.py     # 或手动：git add . && git commit -m "post: <slug>" && git push origin main
   ```
6. 在 GitHub 仓库 **Actions** 页确认 workflow 成功，`gh-pages` 被更新。

### 4.2 调整站点品牌与导航

- **站点信息/菜单/首页介绍**：编辑 `hugo.toml`
  - 导航栏：`[[menu.main]]`（含 `identifier`/`name`/`url`/`weight`），顺序由 `weight` 控制（`[params.reorderNavItems]` 在当前 PaperMod 版本不被读取，无效）。
  - 首页个人介绍：`[params.homeInfoParams]`（`Title` 与 `Content` 字段；**不使用 ImageUrl**，PaperMod 不渲染它）。
  - 页脚社交图标：`[[params.socialIcons]]`（`name` 须为 PaperMod 内置图标名，如 `github`/`mail`）。
- **品牌配色**：编辑 `assets/css/extended/custom.css`，覆盖 `--primary` 等 CSS 变量（Hugo Pipes 自动并入，无需 `customCSS` 引用）。
- **关于/简历页**：编辑 `content/about.md`（已含技能胶囊、时间线、项目卡片，使用内联 SVG 头像）。替换其中的 `Your Name` / `name@example.com` / GitHub 用户名等占位（文件内以 `TODO:` 标注）。

### 4.3 自定义样式的正确位置

- ✅ 写入 `assets/css/extended/*.css` —— Hugo Pipes 会在构建时自动并入主题样式表（已验证主色变量 `2D7FF9` 被正确并入 `public/assets/css/...`）。
- ❌ 不要放 `static/css/` 并试图用 `[params.advanced].customCSS` 引用 —— PaperMod 不识别该参数。

---

## 5. 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| `found no layout file for "html"` / 分类页为空 | `themes/PaperMod` 子模块未初始化 | `git submodule update --init themes/PaperMod` |
| `git checkout main` 卡死/超时 | 切分支时递归联网拉子模块 | 加 `git -c submodule.recurse=false checkout -f main` |
| 线上链接指向 `localhost` 或路径错误 | 未用生产配置构建 | 必须用 `hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml` |
| 「关于」页面 404 | `uglyURLs=true` 下页面是 `.html`；菜单写成 `/about/` | 菜单 `url` 改为 `/about.html`；独立页放 `content/about.md`（勿放 `content/page/`） |
| 改了主题色/导航「没效果」 | 用了 PaperMod 不识别的参数（`navItems`、`lightTheme/darkTheme`、`headerTitle`、`advanced.customCSS`、`experimental.jsDate`） | 删除这些字段，改用 `[[menu.main]]`/`homeInfoParams`/`socialIcons`/`assets/css/extended/` |
| 首页预览不显示文章 | 文章 `draft = true` 或未设 `categories`/`tags` | 发布设 `draft = false`；本地预览加 `-D` |
| Windows 上 `Remove-Item public -Recurse` 超时 | Defender 实时扫描大量文件 | 不要先删 `public`，直接重跑 hugo 构建覆盖即可 |
| 子模块拉取报 SSL/代理错误 | 本地代理拦截 | 临时 `git config --global --unset http(s).proxy` 后重试 |

---

## 6. 参考链接

- Hugo 官方文档：<https://gohugo.io/documentation/>
- PaperMod 主题：<https://github.com/adityatelange/hugo-PaperMod>
- PaperMod 配置示例：`themes/PaperMod/exampleSite/config.yml`
- CI/CD 流水线：`.github/workflows/ci-cd.yml`（PR 门禁 + 合并后自动部署；2026-10-24 前名 `deploy.yml`）。`main` 受规则集 `main-protection` 保护：特性分支 → PR → 验证绿 → squash 合并 → 自动部署，直推 main 会被拒
- 项目上下文（AI 代理）：根目录 `AGENTS.md` / `CLAUDE.md`
- 同类 SOP 索引：`docs/sop/README.md`

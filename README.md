## MapleFlow（Hugo + maplemod）

本项目是使用 Hugo 静态站点生成器和第一方主题 maplemod（fork 自 PaperMod）搭建的个人博客，托管在 GitHub Pages 上。

---

### 本地开发启动

- **环境要求**
  - 已安装 Hugo Extended（建议版本 ≥ `0.154.5`）
  - 已安装 Git

- **首次克隆项目**

```bash
git clone git@github.com:thomasChen9691/mapleFlow.git
cd mapleFlow
```

- **本地开发模式（推荐）**

开发环境使用 `hugo.toml` 中的配置（`baseURL` 为 `http://localhost:1313/`）：

```bash
hugo server -D
```

- 访问：`http://localhost:1313/`
- `-D` 表示同时渲染 `draft = true` 和 `draft = false` 的文章（调试写作时很好用）。

---

### 线上部署（GitHub Pages）

仓库已配置 GitHub Actions 自动化 CI/CD，工作流文件：`.github/workflows/ci-cd.yml`（2026-10-24 由 `deploy.yml` 重建）。

- **验证（verify）**：PR 与 push 到 `main` 都会触发——
  1. `npm test`：reveal 协议 + 搜索前端行为断言（jsdom）；
  2. 生产构建（与 CI 权威命令逐字一致）并守门**零 WARN**：
     ```bash
     hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml
     ```
  3. `python3 tests/assert_site_contracts.py`：站点契约产物断言（十五类）；
  4. `python3 tests/assert_sop_pipeline.py`：SOP 发布管线保真 + CI wiring 自守门；
  5. localhost 泄漏守门：`public/` 不得残留 `localhost:1313` 绝对链接。

- **部署（deploy）**：仅 `main` 的 push / 手动触发，且 **verify 全绿后才跑**——重建并推送到 `gh-pages`，GitHub Pages 从该分支读取静态文件对外提供访问。

- **日常使用（受规则集保护的 PR 流程）**：`main` 已由规则集 `main-protection` 保护——**直接 push 到 `main` 会被拒绝**。标准流程：
  ```bash
  git checkout -b feat/your-topic   # 1. 开特性分支
  git push origin feat/your-topic   # 2. 推送（PR 上自动跑完整验证）
  # 3. 开 Pull Request → 「验证」检查全绿后才能合并
  # 4. Squash and merge → 合并即触发构建并部署到 GitHub Pages
  ```
  规则集要点：唯一必需检查 `验证（测试 + 构建 + 守门）`、Required approvals = 0（solo 仓库可合并自己的 PR）、仅允许 squash 合并、线性历史、禁强推与删除。无需任何手工构建/拷贝；规则集可在 Settings → Rules → Rulesets 调整。

- **GitHub Pages 设置（只需配置一次）**
  - 打开 GitHub 仓库 → `Settings` → `Pages`
  - `Source` 选择：**Deploy from a branch**
  - `Branch` 选择：`gh-pages` 分支（通常是 `/ (root)` 路径）

---

### 自动提交脚本（可选）

项目根目录下有一个简单的自动提交脚本 `auto_push.py`（请在项目根目录运行）。**推荐使用 `python3` 执行**（若本机只有 Python 3，也可用 `python` 或 `.\auto_push.py`）：

```bash
python3 auto_push.py
```

脚本会执行：

1. `git add .`
2. `git commit -m "update: 当前时间"`（使用英文时间格式，避免 Windows 控制台编码导致乱码）
3. `git push origin main`

若运行后无输出且未推送，请确认：在终端中执行（保证 `git` 在 PATH 中）、且当前目录为仓库根目录。推送完成后，GitHub Actions 会自动重新构建并部署最新版本到 Pages。

---

### 常见问题排查

- **首页没有文章 / 分类页为空**
  - 检查文章 front matter：
    - `draft = false`（否则不会出现在正式环境）
    - 如需在分类/标签页显示，需要设置例如：
      ```toml
      categories = ['随笔']
      tags = ['Hugo', '测试']
      ```

- **线上链接指向 localhost 或路径不对**
  - 确认 `config.production.toml` 中的 `baseURL` 为：
    ```toml
    baseURL = "https://thomasChen9691.github.io/mapleFlow/"
    ```
  - 确认 GitHub Actions 中的构建命令为：
    ```bash
    hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml
    ```

---

如需新增文章，可以在 `content/posts/` 下使用 Hugo 命令：

```bash
hugo new posts/my-new-post.md
```

然后编辑生成的 Markdown 文件，设置 `title`、`date`、`draft`、`categories`、`tags` 等字段即可。

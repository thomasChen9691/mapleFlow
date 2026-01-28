## 我的 Dream 博客（Hugo + PaperMod）

本项目是使用 Hugo 静态站点生成器和 PaperMod 主题搭建的个人博客，托管在 GitHub Pages 上。

---

### 本地开发启动

- **环境要求**
  - 已安装 Hugo Extended（建议版本 ≥ `0.154.5`）
  - 已安装 Git

- **首次克隆项目**

```bash
git clone --recurse-submodules git@github.com:YOUR_GITHUB_USERNAME/mapleFlow.git
cd mapleFlow
```

> 如果已经克隆但没有带上子模块（PaperMod 主题），可以补执行：
>
> ```bash
> git submodule update --init --recursive
> ```

- **本地开发模式（推荐）**

开发环境使用 `hugo.toml` 中的配置（`baseURL` 为 `http://localhost:1313/`）：

```bash
hugo server -D
```

- 访问：`http://localhost:1313/`
- `-D` 表示同时渲染 `draft = true` 和 `draft = false` 的文章（调试写作时很好用）。

---

### 线上部署（GitHub Pages）

仓库已配置 GitHub Actions 自动部署，工作流文件：`.github/workflows/deploy.yml`。

- **部署流程概览**
  1. 推送到 `main` 分支；
  2. GitHub Actions 触发 workflow，执行：
     - 检出代码（包含 PaperMod 子模块）
     - 使用命令：
       ```bash
       hugo --minify --config hugo.toml,config.production.toml
       ```
     - 将 `public/` 中生成的内容推送到 `gh-pages` 分支；
  3. GitHub Pages 从 `gh-pages` 分支读取静态文件，对外提供访问。

- **GitHub Pages 设置（只需配置一次）**
  - 打开 GitHub 仓库 → `Settings` → `Pages`
  - `Source` 选择：**Deploy from a branch**
  - `Branch` 选择：`gh-pages` 分支（通常是 `/ (root)` 路径）

---

### 自动提交脚本（可选）

项目根目录下有一个简单的自动提交脚本 `auto_push.py`：

```bash
python auto_push.py
```

脚本会执行：

1. `git add .`
2. `git commit -m "update: 当前时间"`
3. `git push origin main`

推送完成后，GitHub Actions 会自动重新构建并部署最新版本到 Pages。

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
    hugo --minify --config hugo.toml,config.production.toml
    ```

---

如需新增文章，可以在 `content/posts/` 下使用 Hugo 命令：

```bash
hugo new posts/my-new-post.md
```

然后编辑生成的 Markdown 文件，设置 `title`、`date`、`draft`、`categories`、`tags` 等字段即可。

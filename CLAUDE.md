# CLAUDE.md — MapleFlow 博客项目（Claude Code 须知）

本文件为 Claude Code 提供项目上下文与操作约束，内容与根目录 `AGENTS.md` 一致。
  
改动前请先阅读 `AGENTS.md` 的「必知坑点」一节。

## 1. 项目概览

- 使用 **Hugo** + **PaperMod** 主题构建的个人技术博客，部署在 **GitHub Pages**。
- `themes/PaperMod` 是 Git **子模块**（见 `.gitmodules`）。

## 2. 分支模型（重要）

- **`main`**：源码与配置，所有开发在此分支。
- **`gh-pages`**：GitHub Actions 自动构建的静态产物，**不要手动修改**。
- 推送 `main` 即触发 `.github/workflows/deploy.yml` 自动部署。
- 切勿直接操作 `gh-pages` 或本地 `public/`。

## 3. 核心命令

```bash
# 首次初始化主题子模块（否则 hugo 报 "found no layout file"）
git submodule update --init themes/PaperMod

# 本地预览（含草稿）
hugo server -D

# 生产构建（必须与 CI 完全一致，必须合并两个配置）
hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml

# 提交（ASCII 信息，推 main）
python3 auto_push.py
```

## 4. 必知坑点（改动前先读 `AGENTS.md` 第 4 节）

1. 构建必须：`hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml`（`config.production.toml` 含 `baseURL` 与 `uglyURLs = true`）。
2. `uglyURLs = true`：顶层页 `content/about.md` → `/about.html`；菜单 `url` 必须写 `/about.html`，不要把独立页放 `content/page/`。
3. PaperMod **不识别** `[params.navItems]`、`lightTheme/darkTheme`、`headerTitle`、`[params.advanced].customCSS/customJS`、`[params.experimental].jsDate` —— 禁止新增。
4. 自定义样式放 `assets/css/extended/*.css`（Hugo Pipes 自动并入），不要放 `static/css/` + `customCSS`。
5. `[params.homeInfoParams]` 只用 `Title`/`Content`，不渲染 `ImageUrl`。
6. 切换分支先关子模块递归，否则联网拉取超时：
   ```bash
   git -c submodule.recurse=false checkout -f main
   ```
7. Windows 上 `Remove-Item public -Recurse` 会触发 Defender 扫描超时 —— 直接重跑 hugo 构建覆盖即可，不必先删。
8. GitHub Pages 子路径部署（`.../mapleFlow/`）；页面内联 SVG 比引用 `static/img/*` 更稳。

## 5. 内容与提交

- 文章：`content/posts/<slug>.md`；新增 `hugo new posts/xxx.md`。front matter 含 `title/date/draft=false/categories/tags`。
- 关于页：`content/about.md`（当前为 TEST 测试占位内容，以 `TEST`/HTML 注释标注，**无** `TODO:` 标记；上线前替换为真实信息）。
- commit 用纯 ASCII 信息，推荐 `python3 auto_push.py`；不自动假设已提交，改动后交用户审阅。

## 6. 工程纪律（realeng）

1. 任何会话（含更换模型后的新会话）第一步：读 `CONTEXT.md` 与 `docs/adr/`。术语以 `CONTEXT.md` 为准，禁止另造同义词。
2. 已被 ADR 记录的决策，禁止重新推导；认为 ADR 错了，先提出重审，不许默认推翻。
3. 难逆决策才写 ADR（难逆转 + 无上下文会惊讶 + 源于真实权衡，三条件齐备）。
4. 讨论中敲定的术语，当场更新 `CONTEXT.md`，不攒批。
5. 每批次单独 commit，commit message 说明改动意图。
6. 会话收尾用 realeng-handoff 压缩交接，长期接力文档存 `docs/handoffs/`。

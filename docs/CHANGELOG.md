# 更新日志

> **已冻结（2026-10-23 决议）**：本文件停止维护，最后条目为 2026-10-16。
> 此后的变更记录只存在于两处——`docs/handoffs/`（每次会话 / 每张图的交接：状态、决策、去向）与 `docs/adr/`（耐久决策）。
> 理由：变更记录已由 handoff + ADR 承担，第三份账本必然漂移（与 ADR-0004 否掉「第二实现」同一逻辑）。
> 历史条目原样保留、不作改写；其中 2026-10-16 条「逐字节一致」措辞失准——golden 实际比对的是标签 / 属性 / 文本的 **token 序列**（ADR-0005 决策 7），以容忍 CI 0.164 与本机渲染器版本差异。

记录 MapleFlow 博客的变更；与 OpenSpec 变更可互为参考。

## 2026-10-16

### SOP 发布管线 + 后端退役
- 🚀 `content/posts/_content.gotmpl`（seam）+ `data/sop.yaml` 注册表 + `docs/sop/` 源笔记：6 篇 SOP 文改为构建期派生，磁盘上不再有第二份 .md；契约（缺必填字段 / 死条目 / 无 H1 / 无章节标题行）以 errorf 构建期执法；`tests/assert_sop_pipeline.py` 100/100 绿并接入 CI 阻断部署。线上 6 个 URL 冻结，页面与迁移前逐字节一致（golden 断言）。
- 🗑️ 退役 `backend/`（FastAPI 内容 API）及 `run_backend.py` / `test_api.py` / `verify_encoding.py` / `docs/BACKEND_DOCS.md` / `pyproject.toml`：零消费者（两份历史审计早已结论），且适配器化后其 glob 输入对派生文章失效。代码留 git 历史；ADR-0003 加状态标注（语义裁决仍有效，适用对象已不存在）。

## 2026-10-10

### 视觉改造（蓝橙双色 + 柔和渐变底）
- 🎨 `assets/css/extended/custom.css`：页面底改为蓝→橙的极淡双色渐变（保留原 SVG 噪点层，不改结构/动效令牌/排版）；
  强调色扩展为「靛蓝（主）+ 橙（次）」双色令牌（新增 `--accent` / `--accent-hover` / `--accent-soft`）；
  橙色用于眉标 `.mf-eyebrow`、数据条数字 `.mf-spec-num`、序号 `.mf-form-idx`、时间线圆点 `.timeline-dot`、
  题库标记 `.mf-kind[data-kind="question-bank"]` 等点睛处；蓝仍为主色。明暗两套主题对比度均过 WCAG AA。
- 🧹 修正 `custom.css` 中「深青绿 / 5.35:1」的陈旧注释为与新配色一致的准确描述。

### P1 修复
- ✅ P1-1 首页数据条「份可下载资源」改为按 `buy_url` 非空计数（不再把占位条目算成可下载）。
- ✅ P1-2 分类导航补「运维」入口（`[[menu.main]]` identifier=ops，覆盖 7/10 篇文章）。
- ✅ P1-3 测试数据：`content/about.md` 换为 TEST 占位内容；`hugo.toml` 三处邮箱统一为 `test@example.com`；
  `data/products.yaml` 5 条 `buy_url` 填测试地址（用于验证按钮由「即将上架」变为可点击的「购买 / 免费获取」）。
- ✅ P1-4 删除调试探针 `static/probe.js`（及已上线的构建产物 `public/probe.js`）。
- ✅ P1-5 `git rm --cached .hugo_build.lock` 与 `.idea/`（保留磁盘文件，仅取消跟踪）。
- ✅ P1-6 分页阈值 `paginate = 10 → 6`（10 篇 → TotalPages=2，分页器可见）。

### P2 修复
- ✅ P2-1 注释掉死配置 `[params.homeInfoParams]`；`[params.cover]` 空字典**保留**（防主题 cover.html 对 nil 的解引用）。
- ✅ P2-4 删除空目录 `content/page/`。
- ✅ P2-5 标签合并：`k8s` + `kubernetes` → `Kubernetes`（仅合并确属同义的标签，未改 categories）。
- ✅ P2-6/7 覆盖 `layouts/_default/index.json`：`content` 改为截断摘要（索引瘦身）+ 并入 `products.yaml` 条目
  （permalink 指向产品页锚点 `/products.html#<id>`）。
- ✅ P2-8 覆盖 `layouts/_default/rss.xml`：首页订阅源只输出 posts 区文章。
- ✅ P2-9 `languageCode` → `locale`（Hugo v0.158.0 起弃用 languageCode）。
- ✅ P2-10 `static/img/og-cover.png` 由约 1.02MB 压到约 295KB（980×490，合法 PNG）。
- ⏸️ P2-2 backend **保留不动**（用户决定，作为未来小程序 / APP 数据源）。
- ⏸️ P2-11 `static/img/avatar.svg` 保留（当前模板未渲染，无害）。

### 文档对齐
- ✅ README / AGENTS / CLAUDE 的 CI 命令统一为 `hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml`。
- ✅ 修正「`content/about.md` 用 `TODO:` 标注」的不实描述；更新 `public/` 跟踪状态说明（现 0 文件被跟踪）。
- ✅ `docs/README.md` 删除不存在的 `backend_docs.zip` 引用；SOP 索引路径改为 `/posts/sop-ops-tools-index.html`。
- ✅ 本文件修正对不存在文件（`docs/README_BACKEND.md` / `docs/API_TEST_SUMMARY.md`）的引用。

## 2026-01-29

### 新增功能
- ✅ 创建 FastAPI 后端服务，支持获取博客内容
- ✅ 实现博客文章解析器，支持 Hugo front matter 格式
- ✅ 添加搜索功能，支持按标题、内容、标签、分类搜索
- ✅ 创建跨平台 Python 测试脚本 (`test_api.py`)

### 修复问题
- ✅ **修复中文编码问题**
  - 添加自定义 `UTF8JSONResponse` 类
  - JSON 序列化时设置 `ensure_ascii=False`
  - 确保所有响应使用 UTF-8 编码
  - 文件读取使用 UTF-8 编码
  
- ✅ **跨平台支持**
  - 移除 PowerShell 脚本，改用 Python 脚本
  - 测试脚本支持 Linux/macOS/Windows
  - 自动处理不同平台的编码问题

### 文档更新
- ✅ 创建 `docs/` 文件夹统一管理文档
- ✅ 整理后端使用文档（实际文件为 `docs/BACKEND_DOCS.md`）
- ✅ 添加更新日志 (`docs/CHANGELOG.md`)

### 技术改进
- ✅ 使用 uv 进行包管理
- ✅ Python 3.13 支持
- ✅ 虚拟环境配置
- ✅ 环境变量管理 (`.env` 文件)

## 已知问题

### 终端编码问题（Windows）
在 Windows PowerShell 中直接使用 `curl` 或 Python 单行命令时，可能遇到中文乱码。这是 Windows 终端编码设置的问题，不是 API 的问题。

**解决方案：**
1. 使用 `python3 test_api.py` 脚本（推荐）
2. 使用浏览器访问 http://localhost:8000/docs
3. 设置 PowerShell 编码：`[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`

### API 响应编码
API 本身已正确配置 UTF-8 编码，所有 JSON 响应都使用 `ensure_ascii=False`，确保中文内容正确传输。

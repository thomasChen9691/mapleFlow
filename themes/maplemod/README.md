# maplemod — mapleFlow 的第一方主题

本目录是 mapleFlow 站点的**主题层**：呈现与行为基线（骨架、导航、文章与列表渲染、
交互钩子、社交元数据）。仓内 vendored，无 git 子模块、无上游同步义务。

## 来源与许可

- fork 自 [adityatelange/hugo-PaperMod](https://github.com/adityatelange/hugo-PaperMod)
  @ `6c5a8f6`（`v8.0-55`，2026-01-09），2026-10-20 入库并修剪。
- 许可：MIT，见同目录 `LICENSE`（两行上游版权声明原样保留）。MIT 无强制署名要求，
  站点页脚不加鸣谢。
- **已 cut cord**：不建 upstream remote、不跟踪上游。fork 点即上文的 commit 与日期；
  需要上游历史时自行 clone，仓库内不保存。

## 目录导览

| 路径 | 内容 |
|---|---|
| `layouts/_default/baseof.html` | 页面骨架；`<html class="no-js">` 渐进增强基线（ADR-0002） |
| `layouts/_default/{single,list,terms,search}.html` | 文章 / 列表 / 分类词表 / 搜索 |
| `layouts/404.html` | 404 页 |
| `layouts/_default/_markup/render-image.html` | 图片渲染钩子 |
| `layouts/partials/head.html` · `header.html` · `footer.html` | 文档头、导航、页脚 |
| `layouts/partials/extend_head.html` | no-js→js 的**内联** class swap（保持内联，勿外置） |
| `layouts/partials/extend_footer.html` | reveal 协议引擎的 js.Build 加载点（源码在站点 `assets/js/mf-reveal/`） |
| `layouts/partials/post_meta.html` | 文章元信息；title 属性用显式时区格式（构建机时区不决定字节） |
| `layouts/partials/{author,anchored_headings,cover}.html` | 作者、标题锚点、封面 |
| `layouts/partials/templates/{opengraph,twitter_cards,schema_json,_funcs/get-page-images}.html` | 社交与结构化数据（含 ogImage 兜底） |
| `assets/css/**` · `assets/js/**` | 主题样式与 fastsearch/fuse |
| `i18n/zh.yaml` | 单语言站点的 6 个在用键（prev/next/read_time/words/code_copy/code_copied） |

## 分层契约

- **主题层（本目录）**＝呈现与行为基线；**站点层**（仓库根 `layouts/`，仅 7 个文件：
  `index.html`、`_default/rss.xml`、`_default/index.json`、`product-state/items/index`、
  `shortcodes/product-index.html`）＝内容与数据。
- 判据：**因视觉 / 骨架 / 交互而变 → 改这里；因内容策略 / 数据结构而变 → 改站点层。**
- 两层**不得存在同相对路径文件**——`tests/assert_product_states.py` 的 B13 断言守着
  这条线（覆盖层复活即红）。领域定义见根目录 `CONTEXT.md` 的「主题层」。

## 修剪与合并记录

- **修剪（0029）**：删 12 个不可达 partial（breadcrumbs/comments/edit_post/post_canonical/
  post_nav_links/share_icons/toc/translation_list/home_info/index_profile/social_icons/svg）、
  6 个零引用短代码、`archives.html`、`robots.txt` 模板、上游 `.github/`、45 个非中文 i18n；
  保留 assets 全量、`LICENSE`、`theme.toml`、`go.mod`、`images/`。`head.html` 里对
  `google_analytics.html` 的调用是上游遗留钩子（渲染为空；CI 0.164 实证不报错），保留。
- **合并（0030）**：5 个原站点覆盖文件已并入本主题——`baseof.html`（no-js 类）、
  `extend_head.html`（class swap）、`extend_footer.html`（js.Build）、`post_meta.html`
  （时区格式）、`templates/opengraph.html`（ogImage 兜底）。
- **历史提示**：这 5 个文件的**合并前历史在旧站点路径**（如
  `git log -- layouts/partials/post_meta.html`）；`git log --follow` 不穿过合并点
  （`git mv -f` 在目标已存在时不产生 rename）。要查「为什么这样写」，去旧路径看。

## 测试

`python3 tests/assert_product_states.py` 的 B7-B13 守主题契约：全站 no-js 基线、
post_meta 时区格式、菜单渲染序、RSS 只收 posts、search 页挂点、ogImage 兜底、
站点/主题单副本不变量。改本目录前先跑它。

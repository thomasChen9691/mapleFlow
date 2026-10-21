# 精选机制事实底座（工单 0035 · 2026-10-21）

盘点范围：文章侧 featured 的实现面、首页「精选文章」区真实规则、产品侧已锁契约清单、测试 fixture 机制、SOP 派生文生成点、内容与断言缺口。
只记事实，不含决策。后续工单引用本文件，不重新推导。

## 1. 文章侧 featured：零实现

| 检查点 | 结论 |
|---|---|
| `hugo.toml` | 无任何 featured 相关参数（`grep -n featured hugo.toml` 无命中） |
| `archetypes/default.md` | 无 featured 字段 |
| 站点层 `layouts/`（7 文件） | 无 featured 读取（唯一相关是 `index.html:81` 的选文逻辑，见 §2） |
| 主题层 `themes/maplemod/layouts/` | **无** featured 读取；唯一命中 `partials/templates/_funcs/get-page-images.html` 的 `$resources.GetMatch "*feature*"` 是 **og 图资源匹配**（找页面 bundle 里名为 feature* 的图片），与精选机制无关 |
| `content/posts/*.md`（5 个） | 无 featured 声明 |

结论：文章侧「精选」**完全不存在**，首页区块的「精选」二字目前只是标题文案。

## 2. 首页「精选文章」区：实为「最新 3 篇」

- 集合来源：`layouts/index.html:9-10`
  ```
  $pages := where site.RegularPages "Type" "posts"
  if not $pages → $pages = site.RegularPages   （fallback）
  ```
- 选文：`layouts/index.html:81`
  ```
  range $i, $p := first 3 ($pages.ByDate.Reverse)
  ```
  即按日期倒序取前 3，**与 featured 无任何关系**。
- 只在第 1 页渲染：`:16` 的 `if eq $paginator.PageNumber 1` 包裹（`:114` 结束）。
- 渲染形态：`<ol class="mf-rows">` + `<li class="mf-row reveal">`（`:80-99`），序号 `%02d`，标题/摘要（`truncate 96`）/日期/前 3 个分类 + 「阅读」幽灵按钮。
- **同页重复**：`:11` 的 `$paginator := .Paginate $pages`，`:122` 的「最近更新」网格 `range $paginator.Pages` 消费**同一个 `$pages`**。故当前精选 3 篇 == 网格前 3 篇，同页重复展示。这是 0037 去重问题的事实依据（不是假想缺陷）。

## 3. 产品侧已锁契约（ADR-0006，引用不重开）

- **数据准备 seam** `layouts/partials/product-items.html`：入参 `featured`（bool，缺省 false → 不过滤）、`limit`（int，缺省或 0 = 全量，**负数 errorf**）；内部 `where $items "featured" true`；kind 封闭词表门禁（errorf 前缀「产品索引数据：」）。
- **纯渲染 seam** `layouts/partials/product-index.html`：零全局读，`items`/`uid` 必填；空态文案「暂无资源」。
- **短代码** `layouts/shortcodes/product-index.html`：对外 `featured/limit/filters` 属性，uid 由 `.Ordinal` 保唯一。
- **首页调用点** `layouts/index.html:110-111`：`partial "product-items.html" (dict "featured" true "limit" 3)` → `partial "product-index.html" (dict "items" ... "filters" false "uid" "mf-idx-home")`。
- **数据** `data/products.yaml`：5 条，`featured: true` 3 条（n8n-dify-workflows / sre-learning-docs / sre-interview-bank），false 2 条。
- **断言**（`tests/assert_product_states.py`）：
  - `FIXTURE_HOME_FEATURED_IDS`（4 条 featured，limit=3 截断后取前 3）
  - `FIXTURE_HOME_TRUNCATED_ID = fx-unlisted-free`（第 4 条 featured 被截断，不上首页）
  - `FIXTURE_NON_FEATURED_ID = fx-unlisted-plain`（featured false 不上首页）
  - `REAL_HOME_FEATURED_IDS`（真实数据 3 条 featured，yaml 序）
  - 文章侧对应位置**零断言**。

## 4. 测试 fixture 机制：只覆盖 dataDir

- `tests/assert_product_states.py:45-46`：
  ```
  FIXTURE_CONFIG = "hugo.toml,tests/hugo.test.toml"
  REAL_CONFIG = "hugo.toml,config.production.toml"
  ```
- `tests/hugo.test.toml` 全文只有一个有效键：
  ```toml
  dataDir = "tests/fixtures/data"
  ```
  注释明示「只覆盖 dataDir 指向 fixture；uglyURLs / timeZone / menu 等继承 hugo.toml」。
- **连带事实（关键）**：fixture 构建的 `content/` 是**真实目录**（含 `_content.gotmpl`），但 `dataDir` 被替换为 `tests/fixtures/data`（其中只有 `products.yaml`）→ `hugo.Data.sop` 为空 → **SOP 派生文在 fixture 构建中为 0 篇**；5 篇手写 `.md` 仍在。
- 因此文章 featured 的 fixture 若走 `contentDir` 覆盖，会**同时切断 SOP 注册表**（这是既有行为，不是新增破坏），并需在 fixture 内容目录里自行准备文章；若不覆盖 contentDir，则只能拿真实文章做断言（与真实内容耦合）。
- 坏用例机制：`tests/fixtures/bad/<case>/` 每个用例独立 dataDir，构建必须失败 + 钉错误子串（`BAD_CASE_EXPECT`）。

## 5. SOP 派生文 front matter 生成点

`content/posts/_content.gotmpl:61-69`：
```go
$.AddPage (dict
  "path" $entry.slug
  "title" $title
  "description" $entry.description
  "draft" $entry.draft
  "dates" (dict "date" ($entry.date | time.AsTime))
  "content" (dict "mediaType" "text/markdown" "value" $content)
  "params" (dict "categories" $entry.categories "tags" $entry.tags)
)
```
- `params` 里目前只有 `categories/tags`；**featured 若要进派生文，必须落在 `params` 内**（顶层只放官方 page map 契约字段：path/title/description/draft/dates/content/params）。
- 契约四类 errorf 在 `:34-55`（缺必填字段 / 死条目 / 首行无 H1 / H1 后无章节标题行）。
- 注册表 `data/sop.yaml` 6 条：`sop-ansible-automation-guide`、`sop-gitlab-cicd-guide`、`sop-jenkins-cicd-guide`、`sop-prometheus-metrics-alerting-guide`、`sop-sonarqube-code-quality-guide`、`sop-grafana-dashboard-alerting-guide`。

## 6. 内容盘点与缺口

- 手写文章 5 个 `.md`：`docker-common-commands`、`aiops-state-and-tools`、`k8s-common-commands`、`sop-ops-tools-index`、`my-first-post1`（脚手架，待删）。
- 派生文 6 篇（见 §5）。
- 首页当前「精选」3 篇（生产构建实测 `public/index.html`）：`sop-ops-tools-index`（手写，2026-01-28 20:30）、`sop-prometheus-metrics-alerting-guide`（派生，20:25）、`sop-grafana-dashboard-alerting-guide`（派生，20:20）——**按日期取最新，手写与派生混排，非人工挑选**。即派生文今天就占着「精选」位，这是 0040 的事实起点（不是「若参与」的假设）。
- 断言缺口：文章侧精选（选文、条数、去重、空态、缺省、坏值）**全无断言**；`assert_sop_pipeline.py` 与 featured 无关（grep 无命中）。
- `layouts/_default/index.json` 投影字段 = `title/permalink/summary/content/tags/categories`，**不含 featured**（候选 8 边界确认，本图不决策）。

## 附：易混淆项（防止后续工单误引）

- 主题 `get-page-images.html` 的 `*feature*` 是页面资源（图片）匹配，用于 og:image 兜底，**不是**精选标记。
- `hugo.toml` 的 `homeInfoParams` / `reorderNavItems` 与精选无关（后者已确认为死配置并清理过）。

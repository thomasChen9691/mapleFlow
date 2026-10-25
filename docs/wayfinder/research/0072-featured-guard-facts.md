# 0072 featured 类型守卫现状事实底座（盘点）

> 工单 0072 研究产物 · 2026-10-25 · 只查事实、不做决策、不给推荐 · 证据以 `文件:行号` 为准
> 范围：三处守卫拷贝逐行比对 · 三种谓词形态 · 坏值测试覆盖 · 键访问行为 · 消息前缀对应 · 调用链位置 · Hugo partial 机制。
> 版本环境：CI 钉 Hugo `0.164.0`（`.github/workflows/ci-cd.yml` 两处 `hugo-version: '0.164.0'`，见 grep 命中行 32/133）；本机可能 0.167 skew（`tests/assert_site_contracts.py:56-59` 版本纪律）。

## 1. 三处守卫拷贝逐行比对

三处拷贝的守卫本体（`isset` + 非 bool → `errorf`）逐字摘录：

**A. 文章侧** `layouts/partials/post-items.html:38-44`（独立段落，位于 limit 检查 :46-48 之前）：

```
{{- range $pages -}}
  {{- if isset .Params "featured" -}}
    {{- if ne (printf "%T" .Params.featured) "bool" -}}
      {{- errorf "文章精选数据：%s 的 featured 必须是布尔值（got %T=%v）" .RelPermalink .Params.featured .Params.featured -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
```

**B. 产品侧** `layouts/partials/product-items.html:36-42`（位于 `range $i, $p := $items` 循环 :30 内，与 kind 门禁 :33-35 同循环，守卫在前、`where` 过滤 :45 在后）：

```
{{- /* featured 只认布尔（工单 0036 决议：与文章侧同名同义；坏值构建失败，
       where 严格匹配对字符串/整数会静默排除，属静默失效类）。 */ -}}
{{- if isset $p "featured" -}}
  {{- if ne (printf "%T" $p.featured) "bool" -}}
    {{- errorf "产品索引数据：%q 的 featured 必须是布尔值（got %T=%v）" $id $p.featured $p.featured -}}
  {{- end -}}
{{- end -}}
```

**C. SOP 侧** `content/posts/_content.gotmpl:62-71`（位于 `range $entry := hugo.Data.sop` 循环 :33 内，与四个必填字段检查 :35-39、死条目/H1 检查 :40-56 同循环；守卫通过后有传键副作用 :70）：

```
{{- /* featured 可选（工单 0040 决议）：只认布尔；字段存在但非 bool 即 errorf。
       必须**条件传键**——dict 里塞 nil 会让 isset 为真，下游的「非 bool 即失败」
       会对每条未标条目误报（实测）。 */ -}}
{{- $params := dict "categories" $entry.categories "tags" $entry.tags -}}
{{- if isset $entry "featured" -}}
  {{- if ne (printf "%T" $entry.featured) "bool" -}}
    {{- errorf "SOP 发布管线：条目 %s 的 featured 必须是布尔值（got %T=%v）" $entry.slug $entry.featured $entry.featured -}}
  {{- end -}}
  {{- $params = merge $params (dict "featured" $entry.featured) -}}
{{- end -}}
```

### 1.1 逐字重复的部分（三处同构）

| 构件 | 文章侧 | 产品侧 | SOP 侧 |
|---|---|---|---|
| 存在性判据 | `isset .Params "featured"`（:39） | `isset $p "featured"`（:38） | `isset $entry "featured"`（:66） |
| 类型检查 | `ne (printf "%T" .Params.featured) "bool"`（:40） | `ne (printf "%T" $p.featured) "bool"`（:39） | `ne (printf "%T" $entry.featured) "bool"`（:67） |
| errorf 消息骨架 | `…：%s 的 featured 必须是布尔值（got %T=%v）`（:41） | `…：%q 的 featured 必须是布尔值（got %T=%v）`（:40） | `…：条目 %s 的 featured 必须是布尔值（got %T=%v）`（:68） |
| errorf 参数序 | `<定位> <值> <值>`（%T/%v 同传两遍） | 同左 | 同左 |

即「`isset` 外层 + `printf "%T"` + `ne "bool"` 内层 + errorf」四件套在三处逐字同构，差异仅在数据访问路径（`.Params.featured` / `$p.featured` / `$entry.featured`）与消息前缀/定位参数。

### 1.2 真实差异（逐类标出）

- **遍历模式**：文章侧是**独立循环**（:38-44 专为守卫遍历全部文章一次，$pages 在 :34-36 备好：`where site.RegularPages "Type" "posts"`，空则回落全量，`ByDate.Reverse`）；产品侧守卫与 kind 门禁**共用同一 range**（:30-43）；SOP 侧守卫与必填字段/死条目/H1/章节标题检查**共用同一 range**（:33-81）。
- **消息前缀与定位参数**：文章侧前缀「文章精选数据：」、定位用 `.RelPermalink`（%s）；产品侧前缀「产品索引数据：」、定位用 `$id`（%q 带引号，`$id := $p.id | default "<缺失>"` 在 :31）；SOP 侧前缀「SOP 发布管线：」、定位用 `$entry.slug` 且措辞多「条目」二字。
- **条件传键（仅 SOP 侧有）**：_content.gotmpl:65-71 的 `$params := dict …` + `merge` 只在 `isset` 为真时执行；docstring :62-64 与 ADR-0009 决策 5（`docs/adr/0009-featured-mechanism.md:15`）记录实测原因：`dict "featured" .featured` 在字段缺失时产出 `isset=true` + 类型 `nil`，盲传会让第 1 条的非布尔 errorf 对每条未标条目误报。文章侧（Page 集合）与产品侧（YAML 解析出的 map 条目）无 dict 传键场景，故无此注释与实现。
- **守卫的副作用（仅 SOP 侧有）**：守卫通过后把值 `merge` 进 `$params`（:70）供 `$.AddPage`（:72-80）使用——守卫与传键耦合在同一 `if` 块内；文章侧/产品侧的守卫是纯检查，无后续副作用。
- **与谓词的相对位置**：文章侧守卫（:38-44）在谓词 `where`（:50）之前独立成段；产品侧守卫（:36-42）在谓词 `where`（:45，条件过滤）之前同循环内；SOP 侧无 `where` 谓词（精选透传后由首页 post-items 的谓词消费，见第 2 项）。
- **docstring 中的理由注释**：产品侧 :36-37 有「where 严格匹配对字符串/整数会静默排除，属静默失效类」的理由注；文章侧 docstring :19-21 有等价实测记录（「实测：where "Params.featured" true 对字符串 "true"/"false"、yes、1 全不匹配——静默排除属静默失效类，故显式执法；而 if .Params.featured 会把字符串 "false" 当真值，禁止使用」）；SOP 侧理由在 :62-64（条件传键）与文件头 :22（契约⑤）。

## 2. 三种谓词形态

| # | 谓词 | 位置 | 消费方 | 语义 |
|---|---|---|---|---|
| 1 | `where $pages "Params.featured" true` | `layouts/partials/post-items.html:50` | 首页精选链唯一入口 `layouts/index.html:9`（`partial "post-items.html" (dict "limit" 3)`） | Page 集合按嵌套键 `Params.featured` 过滤，省略 operator 即判等；随后 `first $limit` 截断（:51-53）、`complement` 求补集（:56） |
| 2 | `where $items "featured" true`（**条件过滤**） | `layouts/partials/product-items.html:45`（`{{- if $featured }}{{ $items = where $items "featured" true }}{{ end -}}`，`$featured := .featured \| default false` 在 :27） | `layouts/shortcodes/product-index.html:8-11`（短代码经 `eq (.Get "featured" \| default "false") "true"` 转 bool）与 `layouts/index.html:114`（首页精选资源区，`dict "featured" true "limit" 3`） | 数据 map 集合按键 `featured` 过滤；入参缺省 false = 不过滤（与文章侧无条件过滤的行为差异点） |
| 3 | `eq .Params.featured true` | `themes/maplemod/layouts/partials/featured-badge.html:25` | 主题层 `_default/single.html:24`（文章页标题旁）、主题层 `_default/list.html:71`（列表卡片标题旁）、站点层 `layouts/index.html:130`（首页网格卡片标题内） | 单页布尔判定，渲染 `<span class="mf-featured" title="精选">精选</span>` |

`featured-badge.html` docstring 自称谓词与守卫「同源」的原文（`themes/maplemod/layouts/partials/featured-badge.html:8-11`）：

> 谓词：eq .Params.featured true——只认布尔 true（未声明/字符串/整数均不渲染）。坏值执法不归本文件：post-items.html 的 errorf 循环遍历全部文章，非布尔 featured 在首页构建时即失败（ADR-0009 决策 1），本谓词与该守卫同源。

同文件 :13 的拷贝禁令原文：「调用方（传页面上下文，不得内联拷贝本标记——三处拷贝即第二实现）」；:2 自称「精选标识（徽标）的唯一实现与契约定义处」。

## 3. 坏值测试覆盖全清单

### 3.1 文章侧两例（`tests/assert_site_contracts.py`）

- 期望子串字面量：`POSTS_BAD_FEATURED_EXPECT = "文章精选数据："`（`tests/assert_site_contracts.py:168`）；fixture 路径常量 `POSTS_BAD_CONTENT`（:166）/ `POSTS_BAD_INT_CONTENT`（:167）。
- `assert_post_featured_bad`（:755-759）：锚定构建 = `build(POSTS_FIXTURE_CONFIG, harness.dest("posts-fixture-bad"), ["--contentDir", POSTS_BAD_CONTENT])`，即 `hugo.toml,tests/hugo.test.posts.toml` + contentDir 覆盖 `tests/fixtures/content-posts-bad`；判定走 `report_build_failure`（:1337-1341：`returncode != 0` 且 expect 在 `stderr+stdout`）。
- `assert_post_featured_bad_int`（:762-766）：同构，contentDir 覆盖 `tests/fixtures/content-posts-bad-int`。
- fixture 实际内容（已打开核实）：
  - `tests/fixtures/content-posts-bad/posts/bad-featured.md:5` → `featured = 'true'`（字符串）；
  - `tests/fixtures/content-posts-bad-int/posts/bad-featured-int.md:5` → `featured = 1`（整数）。
- 两函数均在 `checks()` 中被调用（:1605-1606），`--quick` 不跳过（quick 只跳 `assert_real` 等真实构建组，:1620-1625）。

### 3.2 产品侧一例（`tests/assert_site_contracts.py`）

- 期望子串字面量：`BAD_CASE_EXPECT["featured-not-bool"] = '产品索引数据："fx-featured-not-bool" 的 featured 必须是布尔值'`（:188）。
- `assert_bad_cases`（:1309-1334）：遍历 `tests/fixtures/bad/products/` 每个目录，`harness.write_config(f"bad-{case}", dataDir=…)` + `build`；期望取 `BAD_CASE_EXPECT.get(case, "产品状态")`（:1333，缺省落产品状态模块前缀）。
- fixture 实际内容（已打开核实）：`tests/fixtures/bad/products/featured-not-bool/products.yaml` → `featured: "true"`（字符串 "true"，YAML 加引号），其余字段合法（`kind: document` 等），文件头注释声明「期望：构建失败，错误信息含『产品索引数据：』与条目 id」。

### 3.3 SOP 侧（`tests/assert_sop_pipeline.py`）

- featured 相关断言只有正路透传：`assert_featured_passthrough`（:361-395）。fixture = `tests/fixtures/featured/`：`data/sop.yaml` 两条（`sop-featured-entry` 带 `featured: true`；`sop-plain-entry` 未标）；`contentDir` 覆盖含适配器副本（`tests/fixtures/featured/content/posts/_content.gotmpl`，已 diff 核实与真实 seam **逐字节一致**，断言 :374-376 守此防漂移）；`sopNotesDir` 指向 `tests/fixtures/featured/notes`（FEAT.md / PLAIN.md）。断言两条：「注册表 featured: true → 派生文进首页精选区」「未标 featured 的派生文不进精选区（缺省即非精选）」（:392-395），观察点是首页 `index.html` 的 `ol.mf-rows` 精选区（消费方行为，非内部 params）。**只覆盖 true + 缺省两态，无坏值**。
- 坏用例断言 `assert_bad_cases`（:295-324）+ `BAD_CASE_EXPECT`（:70-77）：**已核实 `tests/fixtures/bad/sop/` 下只有六个用例目录，逐个打开 sop.yaml 确认无一带 featured 字段**：
  - `sop-dead-entry`（死条目，note: MISSING.md）
  - `sop-h1-only`（H1 之后无章节标题行）
  - `sop-missing-categories`（缺 categories）
  - `sop-missing-date`（缺 date）
  - `sop-missing-slug`（缺 slug）
  - `sop-no-h1`（首行无 H1）
- 判定方式：`PIPELINE_MARKER = "SOP 发布管线"`（:55）必须在输出 + 各用例 expect 子串（:322-324）。**SOP 侧 featured 坏值 fixture = 零**（`_content.gotmpl:68` 的 errorf 无任何坏用例钉子串）。

## 4. 三种数据形态的键访问行为

三种数据形态：`.Params`（Page 对象的 front matter map）· `hugo.Data.products`（数据文件 map，条目为 YAML 解析出的 map）· `hugo.Data.sop`（同）。

- **`.Params` 键小写化——官方文档显式声明**：Hugo 文档 `isset` 页（https://gohugo.io/functions/collections/isset/ ）原文：「When using the `isset` function you must reference the key using lower case. See the previous example.」其示例即配置写 `showHeroImage`、模板必须写 `isset site.Params "showheroimage"`。即 Page.Params / site.Params 类 map 的键被小写化，front matter 写 `Featured: true` 时 `.Params.featured` 与 `isset .Params "featured"` 可达。仓内佐证：工单 0036 Resolution（`docs/wayfinder/tickets/0036-post-featured-field-contract.md:33`）「Hugo 中顶层未知键自动进 `.Params`」。
- **数据文件 map 键保持原样——官方文档无小写化声明，与 Params 形成对照**：Hugo 文档 `hugo.Data` 页（https://gohugo.io/functions/hugo/data/ ）展示数据文件内层键按 YAML 书写形态链接访问（示例均为小写键，未给大小写混写示例），全文无「键小写化」措辞。`SITE.Data` 页（https://gohugo.io/methods/site/data/ ，v0.156 起 deprecated 指向 `hugo.Data`）同样只有「Returns a data structure composed from the files in the data directory」。仓内记录：`docs/wayfinder/map-featured-type-guard.md:36` 雾区条将该差异列为「待实测」——**本仓现状三种源的键全部书写为小写（front matter `featured`、`data/products.yaml:37,49,61,73,85`、`data/sop.yaml`），差异当前不可观测，只在统一接口跨源传键名时才成为问题面**。
- **`where "Params.featured" true` 匹配语义——仓内实测声明 + 官方文档双向佐证**：
  - 仓内实测（工单 0036 Resolution，`docs/wayfinder/tickets/0036-post-featured-field-contract.md:35`，Hugo 0.167 临时探针）：bool true 入选；字符串 `"true"`、字符串 `"false"`、`yes`（YAML 解析为字符串）、整数 `1` **全部不匹配**。ADR-0009 决策 1 同载（`docs/adr/0009-featured-mechanism.md:11`）。
  - 官方 `where` 文档（https://gohugo.io/functions/collections/where/ ）：「The values to compare must have comparable data types.」，对照表示例 `"123" "eq" 123` → `false`、`false "eq" "false"` → `false`——**无类型强制转换**；省略 operator 时默认判等（"Hugo will test for equality if you do not provide an OPERATOR argument."）。
  - 附带事实：`if .Params.featured` 写法会把字符串 `"false"` 当真值（ADR-0009:11、post-items.html:19-21、0036:35 三处记录）——故谓词禁用 `if` 形态。
- **`isset` 对 map/slice 的行为**：官方 `isset` 页（https://gohugo.io/functions/collections/isset/ ）：「Reports whether a specific key or index exists in the given map or slice.」返回 bool；对「键在、值为 nil」返回 true（该行为是 SOP 侧条件传键缺陷的根因，实测记录见 ADR-0009:15 与 _content.gotmpl:62-64）。

## 5. errorf 消息前缀与测试期望的对应关系

| 前缀 | 产出位置（全部 errorf 调用） | 钉住它的测试（函数名 + 期望字面量） |
|---|---|---|
| 「文章精选数据：」 | `layouts/partials/post-items.html:41`（featured 坏值）、:47（limit 负数） | `POSTS_BAD_FEATURED_EXPECT = "文章精选数据："`（`tests/assert_site_contracts.py:168`）→ `assert_post_featured_bad`（:755-759）/ `assert_post_featured_bad_int`（:762-766），判定经 `report_build_failure`（:1337-1341，`expect in (proc.stderr + proc.stdout)`） |
| 「产品索引数据：」 | `layouts/partials/product-items.html:34`（kind 门禁）、:40（featured 坏值）、:47（limit 负数） | `BAD_CASE_EXPECT["featured-not-bool"]`（:188，钉子串到条目 id 与「featured 必须是布尔值」）→ `assert_bad_cases`（:1309-1334，:1334 逐用例 `report_build_failure`）；同前缀另钉 `unknown-kind`（:186）/ `missing-kind`（:187）；`CALLER_LIMIT_NEGATIVE_EXPECT = "产品索引数据：limit 不能为负数"`（:199）→ `assert_bad_caller_limit`（:1344-1361，经短代码真实调用链触发） |
| 「SOP 发布管线：」 | `content/posts/_content.gotmpl:39`（缺必填字段）、:43（死条目）、:47（读失败）、:52（无 H1）、:56（无章节标题）、**:68（featured 坏值）** | `PIPELINE_MARKER = "SOP 发布管线"`（`tests/assert_sop_pipeline.py:55`）+ `BAD_CASE_EXPECT`（:70-77）→ `assert_bad_cases`（:295-324）。**注意：现役六用例的期望子串（死条目/缺必填字段/首行无 H1/无章节标题行）无一对应 featured 消息——:68 的消息目前零测试钉住** |

消息改动影响面：改「文章精选数据：」字面量 → `assert_post_featured_bad` / `assert_post_featured_bad_int` 两条红；改「产品索引数据：」→ featured-not-bool、unknown-kind、missing-kind、caller-limit-negative 四类断言红；改「SOP 发布管线：」→ SOP 套件全部坏用例判定红（PIPELINE_MARKER 是统一前置条件，:322），但其中 featured 专属消息（:68）的改动**当前不会红任何断言**（无对应用例）。

## 6. 三处拷贝的调用方与渲染链位置

- **post-items.html（首页精选链唯一数据准备）**：调用方 `layouts/index.html:9`（`{{- $postSets := partial "post-items.html" (dict "limit" 3) -}}`；产出 featured/rest/all 三片，:10-13 消费）。docstring 契约原文：
  - 「工单 0038 决议：文章侧的数据准备只此一处。本 partial 是首页精选渲染链中**唯一**读 site.RegularPages 并做 featured 判定/截断/补集的地方」（:4-6）；
  - 「契约（工单 0036 决议；构建期 errorf，不给缺省兜底）：· featured 只认布尔 true。字段存在但类型非 bool → errorf」（:17-21，含实测记录）；
  - 「边界：本 partial **只服务首页精选链**（ADR-0012 决策 4 负向锁边）——其他页面 / 模板不得调用本 partial 做 featured 判定或取数；内容层的精选呈现（文章页 / 列表卡片 / 首页网格徽标）归 themes/maplemod/layouts/partials/featured-badge.html（谓词同源、契约各自独立，ADR-0012 决策 2）」（:24-28）。
- **product-items.html（索引链唯一读 hugo.Data.products）**：调用方 `layouts/shortcodes/product-index.html:8-11`（产品页短代码）与 `layouts/index.html:114`（首页精选资源区）。docstring 契约原文：
  - 「工单 0015 决议：本 partial 是索引渲染链中**唯一读 hugo.Data.products 的宿主**；渲染 seam（product-index.html）零全局依赖，行为完全由入参决定」（:4-5）；
  - 「featured 只认布尔（工单 0036 决议：与文章侧同名同义；坏值构建失败，where 严格匹配对字符串/整数会静默排除，属静默失效类）」（:36-37）。
- **_content.gotmpl（SOP 发布管线 seam）**：无模板调用方——站点层 content 适配器（`content/posts/_content.gotmpl`），Hugo 对 content 目录自动执行，产出派生文章。docstring 契约原文：
  - 文件头 :22：「⑤ featured 存在但非布尔 → 构建失败（工单 0040 决议；缺省即非精选）」；
  - :62-64：「featured 可选（工单 0040 决议）：只认布尔；字段存在但非 bool 即 errorf。必须**条件传键**——dict 里塞 nil 会让 isset 为真，下游的『非 bool 即失败』会对每条未标条目误报（实测）」。
  - ADR-0009 决策 5 同载（`docs/adr/0009-featured-mechanism.md:15`）。
- **featured-badge.html（谓词侧，主题层，第 2 项已引）**：契约定义处 docstring 自称「唯一实现」；调用方三处（single.html:24 / list.html:71 / index.html:130）。CONTEXT.md「精选 (Featured)」条（`CONTEXT.md:110`）指向其为「标识的唯一实现与契约定义处」。

## 7. Hugo partial 的可用机制事实（含来源标注）

- **partial 能 return 值——官方文档**：https://gohugo.io/functions/partials/include/ 原文：「If the partial template contains a return statement, returns the given value, else returns the rendered output.」；return 语句页 https://gohugo.io/functions/go-template/return/ 原文：「Within a *partial* template, the `return` statement may return a value of any data type」「When returning a value, any output rendered before the `return` statement is discarded.」。仓内现成先例：`layouts/partials/post-items.html:57`（`return (dict "featured" … "rest" … "all" …)`）、`layouts/partials/product-items.html:52`（`return $items`）、product-state.html（return 型 partial，ADR-0004）。**版本限定**：return 页标注「New in v0.166.0」的是「任意位置、多条 return」的流控制语义；0.164 语义为「partial 内、根级单条 return」——仓内纪律见 `tests/assert_site_contracts.py:56-59`（「模块必须保持 0.164 语义（单变量 + 根级单条 return）」）与 ADR-0004；CI 钉 0.164.0。
- **partial 能 errorf——官方文档用法先例 + 仓内先例**：errorf 是 Hugo 模板函数（Go text/template 预定义函数集中无 errorf，Go 包文档 https://pkg.go.dev/text/template 的预定义函数列表不含它；Hugo 为扩展提供）。官方文档在 return 页的短代码示例中直接使用 `{{ errorf "The %q shortcode requires a src argument. …" }}`（https://gohugo.io/functions/go-template/return/ 「Return early」节）。仓内先例：三处守卫（post-items.html:41,47 / product-items.html:34,40,47 / _content.gotmpl:39,43,47,52,56,68）+ `layouts/partials/product-index.html:24,27`；且「errorf → 构建失败」被测试以 `report_build_failure` 坐实（assert_site_contracts.py:1337-1341、assert_sop_pipeline.py:322-324）。
- **查找序：站点层优先、主题层兜底——官方文档**：https://gohugo.io/hugo-modules/theme-components/ 原文：「For any given file, data entry, etc., Hugo will look first in the project and then in `my-shortcodes`, `base-theme`, and lastly `hyde`.」+「For `static`, `layouts` (templates), and `archetypes` files, these are merged on file level. So the left-most file will be chosen.」本仓为单 theme 配置（themes/maplemod），故 project（站点层 `layouts/`）优先于主题层 `themes/maplemod/layouts/`。
- **站点层调主题层 partial 的仓内先例（有，三处）**：站点层 `layouts/partials/` 现仅有 4 个文件（post-items / product-index / product-items / product-state），而 `layouts/index.html` 调用的 `featured-badge.html`（:130）、`post_meta.html`（:138）、`pagination.html`（:148）在站点层均无同名文件，实际解析到主题层 `themes/maplemod/layouts/partials/` 下同名文件——即站点层模板调用主题层 partial 是现役行为。
- **主题层调站点层 partial 的先例（无——已核实）**：`themes/maplemod/layouts/` 下全部 partial 调用点（single.html:24,33,38,40,45,50 / list.html:31,59,71,81,89 / baseof.html:27,35,39,41 / head.html:24,197,201-204 / footer.html:33 / post_meta.html:53 / templates/opengraph.html:45 / twitter_cards.html:9 / schema_json.html:88）的目标文件全部落在主题层自身；grep `post-items|product-items|product-index|product-state` 在 `themes/` 下仅命中 README 文字与 featured-badge.html docstring 的提及，**零调用**。ADR-0012 侧记录「theme→site 调用曾被否决」（`docs/wayfinder/map-featured-type-guard.md:20` 闭卷 ADR 条）。
- **相关永久断言**：`assert_single_copy`（`tests/assert_site_contracts.py:1587-1597`）断言站点层与主题层不得有同相对路径文件——站点层新建守卫 partial（主题层无同名）不触发该断言；但若守卫落站点层而徽标谓词（主题层）要消费它，即引入 ADR-0012 否决过的 theme→site 调用方向。

## 缺口清单（现有断言未覆盖、且本图需要决策的问题面）

1. **SOP 侧 featured 坏值零 fixture**：`_content.gotmpl:68` 的 errorf 无坏用例（`tests/fixtures/bad/sop/` 六例逐个核实无 featured 字段）、`assert_sop_pipeline.py` 的 `BAD_CASE_EXPECT`（:70-77）无登记子串——SOP 注册表写坏值当前只有真实构建能暴露。守卫单模块化后 SOP 侧的测试缝挂哪个套件、是否补坏例，是未决问题面（归工单 0077）。
2. **SOP featured 消息零钉子串**：「SOP 发布管线：」前缀整体被 `PIPELINE_MARKER` 钉住（:55），但 :68 的 featured 专属消息无任何期望子串——模块化后若统一消息形态，SOP 侧坏值的定位信息无测试保护（归工单 0076）。
3. **徽标谓词的坏值行为无直接断言**：`featured-badge.html:25` 的 `eq .Params.featured true` 依赖 post-items 全局循环在首页构建时执法（docstring:8-11），但坏值 fixture 构建（`assert_post_featured_bad`/`_bad_int`）只判「构建失败 + 前缀」，徽标三面断言（`assert_featured_badge`，:786-835）跑在正路 fixture 上——「坏值下徽标面在哪一环失败」无专门断言。
4. **两处 `where` 谓词的行为差异无对称断言**：文章侧无条件过滤（post-items.html:50）vs 产品侧条件过滤（product-items.html:45，`featured` 入参开关）——产品侧「不过滤」路径仅被 `assert_fixture` 首页计数等间接覆盖，文章侧无对应开关态；谓词形态统一后该差异的守门测试不存在。
5. **键大小写差异无实测无 fixture**：`.Params` 键小写化（官方 isset 页显式声明）vs `hugo.Data` map 键原样（官方无声明）——本仓三种源全部小写书写故不可观测；统一接口若跨源传键名，行为差异待实测（地图雾区 `map-featured-type-guard.md:36` 已列，归工单 0074）。
6. **守卫独立循环的遍历开销无断言保护**：post-items 的守卫循环（:38-44）与谓词（:50）对 $pages 遍历两次；产品侧守卫与 kind 门禁合循环；SOP 侧守卫与五类检查合循环——现有断言只锚构建产物不锚遍历次数/合并形态，模块化后单次遍历的语义等价无守门。
7. **dict nil 陷阱（条件传键）无回归 fixture**：`_content.gotmpl:65-71` 的条件传键与 ADR-0009:15 的实测记录存在，但「盲传 nil 会误报」无 fixture 复现——守卫模块若统一接收 dict 输入，该陷阱的守门测试不存在。
8. **徽标谓词的跨层归属是未决问题面**：谓词在主题层、守卫拷贝全在站点层；徽标 docstring 自称「同源」但「契约各自独立」（post-items.html:27-28）——「同源」是否必须「同实现」、theme→site 调用方向曾被 ADR-0012 否决，现有断言（BADGE_SPAN_RE 三面，:176/804-825）只锚 DOM 不锚谓词来源（归工单 0073/0075）。

---

证据基线：本文所有行号读取于 2026-10-25 工作区；未运行 hugo 构建、未做任何 git 写操作；除本文件外未修改仓库文件。

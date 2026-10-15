# Research 0001 — Hugo 模板逻辑可测试性与派生数据共享机制

对象仓库：mapleFlow（Hugo 0.164.0 extended + PaperMod，uglyURLs=true，生产 baseURL 带 `/mapleFlow/` 子路径，CI 见 `.github/workflows/deploy.yml`）。所有结论对照 Hugo 0.164 校验；仅更高版本具备的行为已显式标注。未找到可引用来源的点标「未验证」。

## Q1 模板逻辑的单元测试机制

Hugo 没有官方的模板单元测试机制：`hugo` 命令参考中不存在 test 子命令，官方文档亦无 template testing 章节（gohugo.io/commands/hugo）。社区标准替代是「build 后对产物断言」：Hugo 维护者 jmooring 在 gohugoio/hugo#12330 中写道 "It's fairly trivial to create a Hugo site to test partial and shortcode output against gold files, and then compare the content to report pass/fail"——即 gold 文件法（`content/tests/` 下放置例页面、期望输出存 `assets/gold`，构建后比对；`strings.Diff` 自 v0.125.0 起可输出 diff，0.164 可用）。社区框架 jest-hugo（Mastercard/jest-hugo）以 Jest + Hugo 构建 + snapshot 测试 shortcode/主题，要求 Hugo ≥0.100。官方可用于验证的 build flags：`--panicOnWarning`、`--printPathWarnings`、`--printUnusedTemplates`、`--templateMetrics`（配 `--templateMetricsHints`）、`--logLevel`、`--renderToMemory`、`--cleanDestinationDir`。render-segment 选项为 `--renderSegments`（配 `[segments]` 配置，v0.124.0 新增，按 kind/path/output 过滤页面，官方用例之一即「只渲染 JSON 输出格式以推送搜索索引」），0.164 可用。

## Q2 跨模板共享派生数据的惯用法

主流做法是 return 型 partial：partial 内 `{{ return dict "k" .v }}`，调用方 `{{ $x := partial "p.html" . }}`；`return` 关键字 v0.55.0 引入，官方称「可以写成像函数一样的 partial，返回任意类型」（dict/slice 均可）；无 return 时 partial 返回 `template.HTML` 字符串。Scratch vs Store：`PAGE.Scratch` 为 page 作用域，v0.138.0 起软弃用并别名到 `PAGE.Store`；Site 级只有 Store、没有 `.Site.Scratch`。`.Store` 家族 v0.139.0 引入（v0.139.0 release notes："Add site.Store and hugo.Store and Shortcode.Store"），作用域分 page/site/global/local/shortcode 五档，方法一致（Set/Get/Add/SetInMap/DeleteInMap/GetSortedMapValues/Delete）。官方描述为 "persistent data structure ... scoped to the current site/page"：站点级 Store 在同一 build 内按站点持续存在、可跨模板共享（官方未逐字写「跨模板」，系 scope 语义推论）。注意 "Determinate values" 陷阱：在 shortcode、render hook 或被 shortcode 调用的 partial 里 set 的值，在页面内容渲染前不确定，父模板需 `{{ $noop := .Content }}` 触发内容渲染后再读。output-format 模板可以调用 partial（官方 output formats 文档明示其模板 "can use a base template, include partial templates"；本仓库 `public/index.json` 即由主题 `_default/index.json` 生成，实证可行），因此同一派生结果可同时供 products 页、首页精选与 `layouts/index.json` 搜索索引复用（项目级 `layouts/index.json` 按查找顺序优先于主题同名模板）；跨输出格式共享时注意 Hugo 按 weight 顺序渲染（json weight=0 先于 html weight=10），勿依赖「HTML 模板先写 Store、JSON 模板后读」的顺序。

## Q3 data/ 目录是否支持构建期计算

严格静态，不支持构建期计算：官方文档 "Hugo reads the combined data structure into memory and keeps it there for the entire build"——构建启动时一次性读入内存（JSON/TOML/YAML/XML；CSV 不得放入 data/；主题与 module 的 data 会合并且项目优先），不存在在 build 过程中生成或改写 data/ 文件的机制。构建期计算的官方替代：(a) Hugo 之外的预构建脚本（本机有 Python 3.13 / Node 22）先写 data/ 再跑 hugo；(b) module mounts 把外部目录（含生成物）挂到 data/——`hugo.Data` 可访问 "the data directory, or within any directory mounted to the data directory"；(c) content adapters（v0.126.0 新增）：`content/**/_content.gotmpl` 在构建期动态 `AddPage`/`AddResource`，可从远程或本地数据源生成页面，但执行期间 Site 未完全初始化（`Site.Pages` 等方法报错）；(d) `resources.GetRemote` + `transform.Unmarshal` 构建期远程取数（带缓存）。

## Q4 「build then assert on artifacts」的可行性与坑

可行且成本低。CI 命令为 `hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml`（Hugo 0.164.0 extended），产物落 `public/`；已实测 `public/products.html`、`public/index.html`、`public/index.json` 均存在，uglyURLs=true 使产品页路径为 `/products.html`（非 `/products/index.html`）。可断言内容：产品按钮状态（`data/products.yaml` 中 buy_url 非空 → `<a class="mf-cta" href="…">购买/免费获取</a>`；为空 → `<span class="mf-cta mf-cta-ghost" aria-disabled="true">即将上架</span>`，已在 public/products.html 实测 5 条）与首页数据条 `.mf-spec-num` 四个值（可由 data/products.yaml + content 在 Python 侧重算后比对）。Gotchas：(1) CI 带 `--minify`，HTML 被压缩（tdewolff 默认 keepWhitespace=false），正则易碎，应使用 html.parser/BeautifulSoup（Python）或 cheerio/jsdom（Node）；(2) baseURL/子路径差异：hugo.toml（dev）为 localhost:1313 + relativeURLs=true，本地产物无 `/mapleFlow/` 前缀；config.production.toml 为 `https://thomasChen9691.github.io/mapleFlow/` + relativeURLs=false，产物为带前缀绝对 URL——断言 href 时须用与 CI 相同的合并配置构建，或先归一化剥离 baseURL；(3) 断言应跑 `hugo` 而非 `hugo server`：官方说明 server 默认写盘并服务，但据社区报告 server 会忽略配置 baseURL 改用 localhost（`--baseURL`/`--appendPort` 可覆盖，社区来源）；另社区报告 server 的 fast render 对 data/ 变更可能不触发重建（未验证），断言脚本应全量构建；(4) 版本 skew：本机 hugo 为 0.167.0 而 CI 锁定 0.164.0，两者 `return` 语义不同（见 Q5），本地通过不代表 CI 通过；(5) 可用 `--renderToMemory` 或 `-d <dir>` 避免污染 public/，`--cleanDestinationDir` 防陈旧产物混入断言。

## Q5 return 精确语法与 partialCached 副作用陷阱

0.164 适用的精确写法：partial 内先算好变量、根级单条返回，如 `{{- $free := or (not .price) (eq (int .price) 0) -}}{{- return dict "free" $free -}}`，调用方 `{{ $s := partial "product-state.html" . }}`。`return` 必须是 pipeline 的最后一条命令（`{{ return "even" | strings.ToUpper }}` 会报错）；return 语句之前渲染的输出会被丢弃。0.164 的硬约束来自官方 return 文档的版本说明（"New in v0.166.0"）：0.166 之前 return 仅支持于 partial 模板、每个模板只允许一条 return、且「无视其在逻辑块中的位置都会执行」——即写在 if/with/range 内也会无条件触发（2019 年社区指南同样警告不得在子句中 return、不得写多条 return；0.166 起才遵循正常流程控制、可任意位置任意次数）。partialCached 语义：变体参数不传给 partial、仅用于生成 cache key；cache 按 site（或 language）隔离；Hugo 并行渲染页面，缓存未热身前 partial 可能被并发执行多次。由此得出的正确性推论（基于上述文档行为的组合，非逐字官方条文）：带副作用的 partial（mutate hugo.Store/site.Store/.Scratch）一旦被 partialCached 包裹，缓存命中会整体跳过执行导致副作用丢失，缓存未命中又可能并发重复执行导致 Add 类副作用双跑——因此派生数据的 partial 必须保持「纯计算 + return」，需要缓存时对纯函数缓存并精心选择 variant。

## Sources

- https://gohugo.io/commands/hugo/ （build flags；无 test 命令）
- https://gohugo.io/commands/hugo_server/ （server flags：--baseURL/--appendPort/--renderToMemory；默认写盘）
- https://gohugo.io/functions/partials/include/ 与 https://gohugo.io/functions/partials/includecached/ （partial/partialCached 语义）
- https://gohugo.io/functions/go-template/return/ （return 语义与 v0.166.0 变更说明）
- https://github.com/gohugoio/hugo/releases/tag/v0.55.0 （return 关键字，v0.55.0；正文经 hugoDocs 预览镜像核对）
- https://github.com/gohugoio/hugo/releases/tag/v0.139.0 （"Add site.Store and hugo.Store and Shortcode.Store"）
- https://gohugo.io/methods/site/store/ 、https://gohugo.io/methods/page/store/ 、https://gohugo.io/methods/page/scratch/ 、https://gohugo.io/functions/hugo/store/ （Store 方法/作用域/弃用说明）
- https://gohugo.io/templates/data-templates/ 与 https://gohugo.io/functions/hugo/data/ （data/ 静态读入；挂载目录可访问）
- https://gohugo.io/getting-started/directory-structure/ （mounts 可挂 data 等目录；项目模板优先于主题）
- https://gohugo.io/content-management/content-adapters/ （content adapters；v0.126.0，另见 newreleases.io 的 release notes 镜像）
- https://gohugo.io/configuration/outputs 与 https://gohugo.io/configuration/output-formats/ （输出格式配置、weight 渲染顺序、noUgly/ugly）
- https://v0-109-0--gohugoio.netlify.app/templates/output-formats （官方旧版文档快照：输出格式模板可用 base 模板、可 include partial）
- https://gohugo.io/configuration/segments （segments 与 --renderSegments；v0.124.0）
- https://gohugo.io/configuration/minify/ （minify 默认配置）
- https://discourse.gohugo.io/t/functional-testing-harness-for-templates-partials/49094/1 （无官方 harness；gold 文件法；jest-hugo；strings.Diff v0.125.0）
- https://github.com/gohugoio/hugo/issues/12330 （gold 文件法原话；strings.Diff）
- https://github.com/Mastercard/jest-hugo （社区 Jest 测试框架）
- https://www.regisphilibert.com/blog/2019/12/hugo-partial-series-part-2-functions-with-returning-partials （社区：0.55 时代 return 约束）
- https://engineered.at/articles/override-baseurl-in-hugo-server （社区：hugo server 忽略配置 baseURL）
- 仓库实证：.github/workflows/deploy.yml、hugo.toml、config.production.toml、layouts/partials/product-index.html、layouts/index.html、data/products.yaml、public/products.html、public/index.html、public/index.json

## Implications for the seam decision

- 派生逻辑（free/paid、按钮态、CTA 文案）应收敛为单个 return 型 partial（如 `layouts/partials/product-state.html`），由 product-index.html、index.html 数据条与未来的 index.json 共同调用；0.164 下必须「单变量 + 根级单条 return」，禁用 0.166+ 的条件多 return 写法，否则 CI（0.164）与本机（0.167）行为分叉。
- 渲染与派生分离：product-index.html 只消费派生结果做 HTML，使「产品状态」成为可被 build-then-assert 单点覆盖的 seam（解析 public/products.html 的 .mf-cta/.mf-cta-ghost 与 data-price，对照 data/products.yaml 重算）。
- 新代码用 hugo.Store/site.Store（v0.139+，0.164 可用）而非 .Scratch（v0.138 起软弃用）；若借 Store 跨模板共享，需防 shortcode/render hook 内 set 值的 "Determinate values" 顺序陷阱。
- 搜索索引（layouts/index.json）可直接调用同一派生 partial（output-format 模板可 include partial），但勿依赖跨输出格式的 Store 写入顺序（json 先于 html 渲染）。
- 测试基建用 Python/Node 产物断言，构建命令与 CI 对齐（合并 config + 固定 Hugo 0.164.0），并显式处理 minified HTML 与 `/mapleFlow/` 子路径前缀两个坑。

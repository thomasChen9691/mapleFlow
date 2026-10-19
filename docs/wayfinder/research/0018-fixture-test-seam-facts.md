# Research 0018 — fixture 与测试缝事实底座（0019 决策前置）

对象仓库：mapleFlow（Hugo；本机 hugo v0.167.0+extended，CI 钉 0.164.0 extended，uglyURLs=true，见 hugo.toml:17 与 .github/workflows/deploy.yml:31-35）。本报告只做事实陈述，全部结论以仓库文件为准并附 文件:行号；未查实之处显式标注「未查实」。相关背景：docs/adr/0004-product-state-module.md、docs/wayfinder/map-product-index-narrowing.md、工单 0019（docs/wayfinder/tickets/0019-narrowed-interface-test-seam.md）。

## 摘要

- assert_product_states.py 做三种构建：fixture 构建（hugo.toml+tests/hugo.test.toml，仅覆盖 dataDir 到 tests/fixtures/data）、逐坏用例运行时动态生成 TOML 的构建（dataDir 指向 tests/fixtures/bad/<case>，判定=非零退出且输出含「产品状态」）、真实数据构建（hugo.toml+config.production.toml）；--quick 只跳过真实数据构建。
- fixture 数据是 listed × price 的 2×2 四行，四条 featured 全为 false；契约用例 4 个的断言语义上只匹配模块 errorf 的统一前缀「产品状态」，弱于 SOP 脚本的逐用例子串登记（BAD_CASE_EXPECT）。
- 对照 product-index 入参组合：只有「无 featured × limit=0 × filters 开 × uid 由短代码派生 × 非空」一格被逐行断言；featured+limit 截断、filters 开/关差异、uid 多实例/唯一性、空态文案均无断言。
- Hugo 版本差异不做脚本级适配：时区由 hugo.toml:10 钉 Asia/Shanghai，脚本与工作流均无 TZ 处理；CI 顺序为 Checkout 后 Setup Hugo 0.164.0 后 Build(--gc --minify) 后 assert_product_states 后 assert_sop_pipeline 后 Deploy，断言步即守门点。
- SOP 脚本有 10 项可复用手法（动态双覆盖 fixture 配置、逐用例契约子串、同配置双构建、零依赖 YAML 解析、规范化 golden 比对、CI 注解、守门自守门等），其中「逐用例子串登记」正是产品脚本的强度缺口。

## Q1 tests/assert_product_states.py 的整体结构

### 三条测试缝（预先商定）

docstring 明示：渲染产物 seam（fixture 构建的 products.html 控件态/文案/data-price 与 index.html「可下载产品」计数）、契约 seam（tests/fixtures/bad/ 每个用例构建必须失败，非零退出+错误含「产品状态」）、真实数据 seam（生产配置构建的 products.html / index.html，线上回归守门）（tests/assert_product_states.py:5-10）。

### 构建原语与双构建机制

- run()：subprocess.run、cwd=REPO、捕获输出（tests/assert_product_states.py:141-142）。
- build(config, dest)：执行 `hugo --cleanDestinationDir --config <config> -d <dest>`（tests/assert_product_states.py:145-146）。注意：**不带 --gc --minify**——与 SOP 脚本（tests/assert_sop_pipeline.py:120-127，注释明言为与 CI 生产命令逐字一致）及 CI 部署构建步（.github/workflows/deploy.yml:41）不同。产品脚本不带这两个 flag 的原因未查实（无注释；SOP 脚本 :121-123 有其自身理由：golden 逐字节比对需要）。
- fixture 构建：FIXTURE_CONFIG = "hugo.toml,tests/hugo.test.toml"（tests/assert_product_states.py:35）；tests/hugo.test.toml 全文仅一行 `dataDir = "tests/fixtures/data"`（tests/hugo.test.toml:5），头注释明言「只覆盖 dataDir 指向 fixture；uglyURLs / timeZone / menu 等继承 hugo.toml」（tests/hugo.test.toml:3-4）。即 dataDir 覆盖机制 = 在 hugo.toml 之后追加一个只写 dataDir 的 TOML，Hugo 的 --config 多文件中后者覆盖前者。
- 真实数据构建：REAL_CONFIG = "hugo.toml,config.production.toml"（tests/assert_product_states.py:36）；config.production.toml 覆盖 baseURL=https://thomasChen9691.github.io/mapleFlow/、relativeURLs=false、uglyURLs=true（config.production.toml:1-5）。
- dest：fixture 到 tests/tmp/fixture（tests/assert_product_states.py:174）、bad 到 tests/tmp/bad-<case>（:212）、real 到 tests/tmp/real（:219）；TMP=tests/tmp（:33），每次启动整目录清空重建（:243-244），tmp/ 被 .gitignore:62 忽略。

### 产物断言如何读

- fixture 全分支断言（assert_fixture, tests/assert_product_states.py:173-193）：构建失败即记一项并返回（:176-178）；成功后用自研 ProductRowParser（html.parser 子类，:68-128）解析 products.html 每条 li.mf-row，抽取 id / data-price / 价格文案 / 控件形态（a.mf-cta=link；span.mf-cta-ghost=disabled，取 aria-disabled）/ href（:79-99）；对 FIXTURE_ROWS 四条独立字面量期望逐条比对 control/label/data-price/price_text/href/aria_disabled 六字段（:180-190；期望表 :41-62）；再用正则 parse_spec_count（:131-138）从 index.html 抽「可下载产品」计数，期望==2（:191-192；FIXTURE_LISTED_COUNT=2 见 :63）。注意首页计数条文案实为「份可下载产品」（layouts/index.html:62），匹配用的是子串「可下载产品」；该数字由 layouts/index.html:53-62 现场计算——range site.Data.products，逐条 `partial "product-state.html" .` 取 .listed 求和，模板不自行推导（ADR-0004）。
- assert_search_index（tests/assert_product_states.py:161-170）：index.json 中 permalink 含 "products.html#" 的产品条目 tags 必须 == ["产品"]（注入见 layouts/_default/index.json 的产品段 "tags" (slice "产品")）。
- 真实数据 seam（assert_real, tests/assert_product_states.py:218-231）：解析 products.html，期望 5 条全部 disabled「即将上架」（REAL_ROW_COUNT=5 见 :64、REAL_LISTED_COUNT=0 见 :65，注释说明迁移后全部未上架、计数显示 0 是工单既定行为）；并期望 index.html 计数==0（:230-231）。

### 契约用例（构建必须失败）如何构造与判定

assert_bad_cases（tests/assert_product_states.py:196-215）：
- 发现：扫描 tests/fixtures/bad/ 下「目录内含 products.yaml」的子目录（:203-204）。bad/ 是产品与 SOP 共享的坏用例空间，按文件形态归属过滤，防止 sop-* 用例被扫入（docstring :197-201）；一个都没有则记失败（:205-207）。
- 构造：每个用例在 tests/tmp/ 下动态写一个仅含 `dataDir = "tests/fixtures/bad/<case>"` 的 TOML（:209-211），再 `--config hugo.toml,<该 TOML>` 构建到 tests/tmp/bad-<case>（:212）。**无文件拷贝、无临时站点目录**——dataDir 直接指向 fixture 目录，layouts/content/其余配置全部用真实站点。
- 判定：`proc.returncode != 0 and "产品状态" in (proc.stderr + proc.stdout)`（:213）。「产品状态」是模块内 errorf 的统一消息前缀（layouts/partials/product-state.html:37/39/41/43 四条 errorf 均以「产品状态：%q …」开头）。**不匹配各用例特有错误子串、不校验条目名**（对照 Q3/Q5）。

### --quick 与运行形态

--quick 定义在 tests/assert_product_states.py:236，main 中仅条件跳过 assert_real（:249-250）——fixture 构建与全部契约坏用例仍跑。hugo 不在 PATH 直接返回 2（:239-241）。产物：Report 逐项 PASS/FAIL + RED/GREEN + 退出码 1/0（:252-262）；**无 GitHub Actions ::error 注解**（SOP 脚本有，tests/assert_sop_pipeline.py:445-449）。

## Q2 fixtures 的组织方式（data / draft / bad）

### tests/fixtures/data/（产品状态 fixture 数据）

tests/fixtures/data/products.yaml 共 4 条，为 listed(上架/未上架) × price(付费/免费) 的 2×2，文件头注释明言覆盖控件语义四种组合（tests/fixtures/data/products.yaml:9-10；对应断言期望表 tests/assert_product_states.py:41-62）：

| 条目 | kind | price | listed | buy_url | featured | 行号 |
|---|---|---|---|---|---|---|
| fx-listed-paid | workflow | 39 | true | 非空 | false | tests/fixtures/data/products.yaml:14-24 |
| fx-listed-free | document | 0 | true | 非空 | false | :26-36 |
| fx-unlisted-paid | question-bank | 49 | false | "" | false | :38-48 |
| fx-unlisted-free | document | 0 | false | "" | false | :50-60 |

关键事实：4 条 featured **全部为 false**；kind 覆盖三种取值（workflow / document / question-bank，恰好等于筛选控件的三个 data-group=kind 按钮值，layouts/partials/product-index.html:33-35）；version 有空串与非空两种；updated 均为 2026-10-15。

装配机制：**不拷贝、不搭临时站点目录**。tests/hugo.test.toml 仅把 dataDir 改指 tests/fixtures/data（tests/hugo.test.toml:5），layouts、content、hugo.toml 全部配置都是真实站点。即「临时站点 = 真实站点 + dataDir 覆盖」。附带事实：同目录有 sop.yaml 镜像（tests/fixtures/data/sop.yaml），头注释说明存在理由——fixture 构建覆盖 dataDir 后若无 sop.yaml，SOP 适配器生成 0 页、索引文章 ref 短码落空会导致整个 fixture 构建报错（2026-10-15 迁移时的回归）；无任何断言消费它（tests/fixtures/data/sop.yaml:1-9）。

### tests/fixtures/draft/（SOP 管线专用，产品状态脚本不接触）

data/sop.yaml 两条注册条目：draft-live-entry（对照组）与 draft-hidden-entry（draft: true），外加 categories [运维]（tests/fixtures/draft/data/sop.yaml:6-15）；notes/ 下有 LIVE.md、DRAFT.md 两个源笔记。由 SOP 脚本的 fixture_config 以 dataDir 与 params.sopNotesDir 双覆盖装配（tests/assert_sop_pipeline.py:217-235），消费方是 assert_draft（tests/assert_sop_pipeline.py:346-362）。

### tests/fixtures/bad/（共享坏用例空间，共 10 例）

产品用例 4 个，每个目录仅一个 products.yaml（用例目录即 dataDir）：listed-no-url / missing-listed / missing-price / unlisted-with-url。SOP 用例 6 个，每个目录为 data/sop.yaml + notes/*.md：sop-dead-entry / sop-h1-only / sop-missing-categories / sop-missing-date / sop-missing-slug / sop-no-h1。归属过滤：产品脚本认 products.yaml（tests/assert_product_states.py:204），SOP 脚本认 data/sop.yaml（tests/assert_sop_pipeline.py:329）。目录形态差异有原因：SOP 用例的 dataDir 指向 <case>/data、notes/ 平级隔离——Hugo 数据加载器会递归解析 dataDir 下所有文件，.md 混入 dataDir 会以「unmarshal of format」崩溃（tests/assert_sop_pipeline.py:221-223 注释）。坏用例的构建配置（tests/tmp/bad-<case>.toml）运行时动态生成，不是仓库内静态文件（tests/assert_product_states.py:209-212；SOP 侧 tests/assert_sop_pipeline.py:229-235）。

## Q3 tests/fixtures/bad 产品用例的错误信息契约

产品侧判定公式统一为「构建失败（returncode != 0）且 stderr+stdout 含『产品状态』」（tests/assert_product_states.py:213）。四条 errorf 均在 layouts/partials/product-state.html：缺 listed :37、缺 price :39、已上架+buy_url 空 :41、未上架+buy_url 非空 :43，消息格式统一为 `产品状态：%q <说明>`。逐条：

| 用例目录 | 违约点（fixture 行号） | 对应 errorf | 模块真实错误子串 | 脚本实际校验 |
|---|---|---|---|---|
| bad/listed-no-url | listed=true 且 buy_url=""（tests/fixtures/bad/listed-no-url/products.yaml:1-14） | product-state.html:41 | 「产品状态」+「已上架但 buy_url 为空」+ 条目名 | 仅「产品状态」（:213） |
| bad/missing-listed | 缺 listed 字段（tests/fixtures/bad/missing-listed/products.yaml:1-12） | :37 | 「产品状态」+「缺少 listed 字段」+ 条目名 | 仅「产品状态」 |
| bad/missing-price | 缺 price 字段（tests/fixtures/bad/missing-price/products.yaml:1-13） | :39 | 「产品状态」+「缺少 price 字段」+ 条目名 | 仅「产品状态」 |
| bad/unlisted-with-url | listed=false 且 buy_url 非空（tests/fixtures/bad/unlisted-with-url/products.yaml:1-15） | :43 | 「产品状态」+「未上架但 buy_url 非空」+ 条目名 | 仅「产品状态」 |

即：脚本级契约比 fixture 注释声明的契约（「含『产品状态』与条目名」）弱——任一产品状态 errorf 都能让全部 4 个用例通过，「因别的原因失败也绿灯」未被防住。对照 SOP 侧：BAD_CASE_EXPECT 逐用例登记特有子串（tests/assert_sop_pipeline.py:76-83：sop-dead-entry 到「死条目」，sop-missing-date/sop-missing-slug/sop-missing-categories 到「缺必填字段」，sop-no-h1 到「首行无 H1」，sop-h1-only 到「无章节标题行」）+ PIPELINE_MARKER「SOP 发布管线」双校验（:61、:341），未登记即红（:335-336）。

## Q4 对照 product-index 输入组合的覆盖与缺口

### partial 入参契约与实现

layouts/partials/product-index.html:8-12 声明入参：featured bool 只显示精选（实现 :19，`where $items "featured" true`）；limit int，0 或空 = 全部，仅 >0 时取前 N（实现 :20）；filters bool，缺省 true，控制筛选控件与交互脚本是否输出（实现 :22，输出块 :30-41 与 :81-154）；uid string DOM id，缺省 "mf-idx"（实现 :21）。空态分支输出 `<p class="mf-empty">暂无资源。请在 <code>data/products.yaml</code> 中添加条目。</p>`（:24-25）；另有 default slice 防护 dataDir 覆盖后 site.Data.products 为 nil 的崩溃（:15-18，注释明言空态分支「为此而写却永不可达」的修复动因）。

### 真实调用点（共两处，第三处是短代码包装）

- layouts/index.html:110：`dict "featured" true "limit" 3 "filters" false "uid" "mf-idx-home"`（首页「精选资源」区，:102-110）。
- layouts/shortcodes/product-index.html:6-11：短代码参数转 dict；featured 经 `eq (.Get "featured" | default "false") "true"`、limit 经 `int`、filters 经 `ne ... "true"`、uid 为 `printf "mf-idx-%d" .Ordinal`。content/products.md:50 以 `{{< product-index >}}` 无参调用 → featured 假、limit 0、filters 真、uid=mf-idx-0（渲染实证见下）。

### 数据侧事实

- fixture 数据 4 条 featured 全 false（Q2 表）→ 首页 featured=true 区在 fixture 构建中恒为空态。
- 真实数据 5 条：featured: true × 3（data/products.yaml:37 n8n-dify-workflows、:49 sre-learning-docs、:61 sre-interview-bank），featured: false × 2（:73、:85）；全部 listed: false（:35、:47、:59、:71、:83）。**恰好 3 条 featured = limit 3**——首页精选区候选数恰好等于限额，limit 截断逻辑（first N）在真实构建中不暴露。

### 构建产物实证（tests/tmp/ 上次运行残留，gitignore:62 忽略；未重跑）

- fixture/products.html：id="mf-idx-0"，含 mf-filters 容器与 8 个 mf-filter 按钮及 <script>（filters 默认开生效）。
- fixture/index.html「精选资源」区渲染 `<p class="mf-empty">暂无资源…`（空态分支被真实执行）。
- real/index.html：id="mf-idx-home"，无 mf-filter（filters=false 生效）。
- real/products.html：id="mf-idx-0"。
- partial 的 uid 缺省值 "mf-idx"（layouts/partials/product-index.html:21）**在任何构建中都不被渲染**——短代码总是显式传 uid，layouts/index.html:110 也显式传；缺省分支当前是死路。

### 覆盖矩阵（✓=有断言；△=被执行/被渲染但无断言；✗=未执行）

| 输入组合 | fixture 构建 | 真实数据构建 | 断言情况 |
|---|---|---|---|
| featured 无 × limit=0(全部) × filters 开 × uid=mf-idx-0(短代码派生) × 非空(4 行) | △（products.html，content/products.md:50） | △ | ✓ 唯一被逐行断言的一格：4 行控件态六字段比对（tests/assert_product_states.py:180-190）+ 首页计数 ==2（:191-192） |
| featured=true × limit=3 × filters 关 × uid=字面量 × 非空 | ✗（fixture featured 全 false，直接空态） | △（mf-idx-home 实证） | ✗ 无任何断言读首页精选区产物；assert_real 只解析 products.html 与 index.html 计数条（tests/assert_product_states.py:218-231） |
| featured=true × 空态（无 featured 条目） | △（mf-empty 实证） | ✗（真实有 3 条 featured） | ✗ 空态文案无断言 |
| featured 过滤本身选中哪些条目 | ✗ | △ | ✗ 无「精选区恰好是 featured: true 子集」类断言 |
| limit 真正截断（候选数 > limit） | ✗ | ✗（真实恰好 3=3） | ✗ 截断逻辑未暴露 |
| limit=0/空 = 全部（显式语义） | ✓ 同上第一格（4 行全渲染） | △ | ✓ 间接覆盖 |
| filters=true 输出控件+脚本 / filters=false 不输出 | △ / △ | △ / △ | ✗ 无 .mf-filters / script 存在与缺失断言 |
| uid：缺省值 "mf-idx" | ✗（死路，见上） | ✗ | ✗ |
| uid：短代码派生命名（mf-idx-0） | △ | △ | ✗ 无断言检查 uid 值 |
| uid：同页多实例 / 重名检测 | ✗（products 页与首页是两个页面；短代码全仓仅调用一次） | ✗ | ✗ 多实例契约完全无覆盖 |
| nil 数据（default slice 路径，:15-18） | ✗（fixture dataDir 含 products.yaml） | ✗ | ✗；附带事实：SOP 坏用例的 dataDir（<case>/data）只有 sop.yaml，届时 hugo.Data.products 为 nil 会走到该分支，但那些构建因 SOP 契约失败而中止，空态渲染不被断言也不可依赖 |

**小结**：fixture 的 4 条数据只服务产品状态六字段断言；product-index 的四个入参中，只有「无 featured + 无 limit + filters 默认开」这一默认路径被间接执行并部分断言；其余组合或不被执行、或执行了无断言。

## Q5 tests/assert_sop_pipeline.py 可复用手法（0019 借鉴候选）

1. **运行时时序生成 fixture 配置**（fixture_config, tests/assert_sop_pipeline.py:217-235）：动态写 TOML 到 tests/tmp，同时覆盖 dataDir 与 [params].sopNotesDir 两个注入点；路径用 `relative_to(REPO).as_posix()`——注释说明 Windows 上反斜杠嵌进 TOML 会被当转义序列、导致坏用例因路径失败而非契约失败（假红）（:223-225）；并写 `refLinksErrorLevel = "WARNING"` 把「环境差异导致的 ref 落空」降级，避免掩蔽本模块契约错误（:226-228 注释 + :232 写入）。
2. **构建命令与 CI 逐字一致 + drafts 开关**（tests/assert_sop_pipeline.py:120-127）：`--gc --minify --cleanDestinationDir`，可选 `-D`；注释明言这是 golden 逐字节比对的前提（:121-123）。
3. **逐用例契约子串登记表**（BAD_CASE_EXPECT, tests/assert_sop_pipeline.py:76-83）：每个坏用例钉一个期望错误子串，防「因别的原因失败也绿灯」；判定为 returncode≠0 且管线标记与期望子串都在输出（:341）；未登记的用例直接红（:335-336）。这正是 Q3 指出的产品脚本所缺的强度。
4. **用例发现按内容归属过滤**（tests/assert_sop_pipeline.py:328-329）：与产品脚本同构（tests/assert_product_states.py:203-204），共享坏用例目录不互相扫入。
5. **同配置双构建验证行为语义**（assert_draft, tests/assert_sop_pipeline.py:346-362）：生产构建断言条目缺席、-D 构建断言条目出现——「行为随构建立即可见」的示范，比单构建断言更强。
6. **零依赖 YAML 子集解析器**（parse_registry, tests/assert_sop_pipeline.py:86-113）：只用 stdlib（CI python3 不保证有 PyYAML，:89-91 注释），schema 约束写进 docstring（标量或行内列表、无多行块值、含冒号仅限时间串）。
7. **独立期望值来源 + 归一化比对工具集**：html_to_text / squash / md_inline / md_to_text / strip_code_blocks / note_headings / page_headings（tests/assert_sop_pipeline.py:142-192）；hugo_date_text 独立格式化注册表日期（:195-202，注释记录 Hugo 按 +0800 渲染的实测）；ZERO_DATE_TEXT 零值日期字面量（:62，断言处 :289-291）。
8. **golden 共享模块防规则漂移**（tests/assert_sop_pipeline.py:51-52 引用 tests/sop_golden.py）：捕获脚本与断言脚本共用抽取逻辑（tests/sop_golden.py:3-7 docstring）；比对用 canonical token 序列而非逐字节——属性引号/空白/时区缩写等渲染器版本差异归一，内容与结构变化仍全捕获（tests/sop_golden.py:46-88，docstring :79-84 明言 CI 钉 0.164、本机 0.167 的逐字节必红教训）；first_divergence 输出首个分歧点作诊断（:91-107）；golden 缺失 = 新条目走结构断言、不红（tests/assert_sop_pipeline.py:310-323）。
9. **CI 注解输出**（tests/assert_sop_pipeline.py:445-449）：GITHUB_ACTIONS=true 时把失败项以 `::error` 打印——CI 日志需认证才能取，注解在 run 页直接可见（:446-447 注释记录 2026-10-16 首红时读不到日志的教训）。
10. **守门自守门 + 目录独占纪律**（assert_ci_wiring, tests/assert_sop_pipeline.py:407-415）：断言 deploy.yml 里必须出现本脚本路径；tests/tmp 独占与两脚本须顺序运行（CI 即顺序）写在 docstring（:36-38）。

## Q6 Hugo 版本相关事实

### 脚本层适配：无适配，只有纪律声明

两个脚本都**不做任何 Hugo 版本探测或分支适配**，只在 docstring 声明纪律：
- tests/assert_product_states.py:16-18：「模块必须保持 0.164 语义（单变量 + 根级单条 return）。本机 hugo 可能为 0.167 而 CI 钉 0.164——0.164 风格代码两端一致，但 0.166+ 的条件多 return 写法本地过、CI 红。本脚本只消费构建产物，与 Hugo 版本无关。」
- tests/assert_sop_pipeline.py:28-30：同构声明（适配器按 0.164 语义编写：dates 嵌套 dict、params 承载 categories/tags、description 顶层；本脚本只消费构建产物）。
- 被执法对象 layouts/partials/product-state.html:25-26 同样写明该硬约束（单变量 + 根级单条 return，改动前先跑 tests/assert_product_states.py）。
- 本地实测 hugo version = v0.167.0+extended+withdeploy darwin/arm64（本机运行输出）。

### 时区处理

- hugo.toml:10 显式 `timeZone = "Asia/Shanghai"`，注释（hugo.toml:6-9）说明动因：缺省时 Hugo 用运行机器本地时区渲染时间，本地（Asia/Shanghai）与 CI runner（UTC）产出不同字节——2026-10-16 CI golden 比对首红即此处（post-meta 的 title 属性）。
- 两个断言脚本与 CI 工作流中**均无 TZ 环境变量设置、无脚本级时区处理**（对 tests/*.py 与 .github/workflows/deploy.yml 检索 TZ / timeZone / Asia/Shanghai 无命中）。
- 唯一与时区相关的脚本逻辑在 tests/sop_golden.py:22-43（_DT_ATTR / _normalize_attr_value）：把时间戳属性值的时区缩写归一（本机渲染 `+0800 CST`，CI runner 渲染 `+0800 +0800`），注释明言这是构建环境元数据而非内容差异，且 hugo.toml 的 timeZone 管不到已带偏移量的 time.Time 的 Location（tests/sop_golden.py:36-37）。

### CI 工作流（.github/workflows/deploy.yml，唯一工作流）

步骤顺序与守门点：
1. Checkout code（:25-29，submodules: true、fetch-depth: 0——PaperMod 为子模块）。
2. Setup Hugo（:31-35）：peaceiris/actions-hugo@v2，`hugo-version: '0.164.0'`（:34），`extended: true`（:35）。
3. Build Hugo site（:36-41）：`hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml`——**先构建再断言**，产物落 public/。
4. Assert product states（:43-47）：`python3 tests/assert_product_states.py`（全套，非 --quick）。失败即阻断部署（注释 :44-46：不让失实的「可下载产品」数字上线）。
5. Assert SOP pipeline（:49-54）：`python3 tests/assert_sop_pipeline.py`（全套）。失败即阻断部署。
6. Deploy to GitHub Pages（:56-61）：peaceiris/actions-gh-pages@v4 推 public/ 到 gh-pages。

即：CI 权威体现在「测试步位于 Build 之后、Deploy 之前，非零退出即流程红」；两个断言步本身是守门点，且 SOP 脚本还有 assert_ci_wiring 自守门（tests/assert_sop_pipeline.py:407-415）——产品脚本无对应自守门（deploy.yml 里出现产品脚本路径这件事无断言保护，未查实是否有意省略）。

## 缺口清单（对照 0019 要决策的「输入组合全分支」）

G1. **契约断言强度**：产品坏用例只匹配「产品状态」前缀，不钉逐用例特有错误子串与条目名（tests/assert_product_states.py:213 vs SOP 的 tests/assert_sop_pipeline.py:76-83/341）；任一条产品状态 errorf 均可让 4 个用例全绿。
G2. **featured 过滤行为**：fixture 4 条 featured 全 false、真实恰好 3 条 = limit 3，导致「精选区选中的是 featured: true 子集」这一语义在两种构建中都没有有效暴露与断言。
G3. **limit 截断**：候选数 > limit 的组合在任何构建中都不存在（真实 3=3、fixture 0 featured），first N 逻辑零执行零断言。
G4. **filters 开/关**：两种形态都被渲染（fixture products.html 有控件+脚本、index.html 无）但无任何存在性/缺失性断言。
G5. **uid 契约**：缺省值 "mf-idx" 是死路（从不渲染）；短代码派生命名无断言；同页多实例/重名在任何构建中均不存在（短代码全仓仅一次调用，products 页与首页分离）。
G6. **空态文案**：fixture 首页精选区实际走空态分支（mf-empty 实证），但「暂无资源」「没有符合筛选条件的资源」两处文案无断言（后者 layouts/partials/product-index.html:78 还是 hidden 属性 + JS 驱动，静态产物中断言价值有限）。
G7. **nil 数据路径**：default slice（layouts/partials/product-index.html:15-18）无专属 fixture；SOP 坏用例构建虽会途经 nil 分支但因契约失败中止，不可依赖。
G8. **partial 无直接驱动 seam**：product-index 只能经 content/products.md 的短代码间接驱动（featured/limit/filters 由短代码参数固定转换）；若 0019 后的收窄接口改变入参形状，现有「dataDir 单点覆盖」机制能否注入全部组合，取决于 0015 的方向（未决）。
G9. **CI 注解缺失**：产品脚本无 GitHub Actions ::error 输出（SOP 有，tests/assert_sop_pipeline.py:445-449），CI 失败诊断弱于 SOP 侧。
G10. **产品脚本构建命令与 CI 不一致**：产品脚本不带 --gc --minify（tests/assert_product_states.py:146），真实数据 seam 跑在非 minify 产物上（当前断言为解析型不受影响；若未来要做字节级/golden 型断言即成为障碍）。
G11. **fixture 与真实数据同步无机制**：tests/fixtures/data/sop.yaml 靠注释「建议同步」无人强制执行；产品 fixture 4 条与真实 data/products.yaml 的演进关系同样只靠人工（地图 Not yet specified 第 3 条已列此议题）。

## 给 0019 的注意（决策前须知、本报告未查实的事项）

1. **0015 未决导致缝形状无法预判**：product-index 收窄后的入参形状（显式数据入参 or 保留自读 hugo.Data.products）由工单 0015 决定；本报告只覆盖现状。「哪些 fixture 构建 × 哪些产物断言」若依赖新入参形状，事实底座需在 0015 定稿后补查。
2. **同页多实例的测试载体不存在**：0017 的 uid 多实例契约若要求同页两实例，当前内容结构（products 页与首页分离、短代码仅调用一次）中没有现成载体；需要新建测试页/短代码调用点到什么程度，未查实也无现成先例。
3. **tests/tmp 产物证据为上次运行残留**：Q4 的构建产物实证来自 tests/tmp 的上次运行快照（gitignore:62 忽略、每次启动清空），本报告未重跑脚本验证；若代码此后有变动，残留产物可能不代表当前行为。
4. **产品脚本不带 --gc --minify 的原因未查实**：仓库内无注释说明（SOP 脚本 :121-123 有其自身理由）；是「解析型断言不需要」的显式决策还是历史遗漏，未查实。
5. **Hugo 0.164 模板语义的行为细节未实测**：如 `default slice`、`where` 对 nil、`first (int .)` 对 limit 类型转换等在 0.164 / 0.167 两端是否完全一致，本报告只读代码与注释，未做双版本实测。
6. **合流 vs 独立脚本的成本事实**：0019 问「缝与 assert_product_states.py 合流还是独立脚本」；已知约束是两脚本共享 tests/tmp 且须顺序运行（tests/assert_sop_pipeline.py:36-38 docstring、CI 顺序即 deploy.yml:43-54），但合并后的维护成本/CI 时长影响等未查实。
7. **assert_ci_wiring 是否该有产品侧对应未查实**：SOP 脚本断言 deploy.yml 含自身路径；产品脚本无此自守门，deploy.yml 中产品脚本路径被误删时无任何测试会发现——这是设计取舍还是遗漏，未查实。

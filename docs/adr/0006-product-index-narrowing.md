# 0006 - product-index 接口收窄：数据准备与纯渲染双 seam

**状态**：已批准（2026-10-19）。决策过程见 wayfinder 地图「product-index 接口收窄图（候选 4）」（docs/wayfinder/map-product-index-narrowing.md，六工单全 closed）与工单 0015~0020 决议；本 ADR 是决策的耐久化记录——AGENTS.md §8.1 的阅读路由（CONTEXT.md + docs/adr/）不含 wayfinder 目录，决策必须活在 docs/adr/。产品状态模块本身见 ADR-0004（本 ADR 只收窄其下游的索引接口）。

**2026-10-22 指针**：本 ADR 的 `featured` 语义已被 ADR-0009（精选机制）扩展为**跨类统一**——`featured` 只认布尔 `true`、非布尔即 errorf（产品侧原未定义坏值行为，ADR-0009 决策 1 补齐）；文章侧的字段契约、首页行为、seam 形状与测试缝均见 ADR-0009。本 ADR 正文不改（ADR 是历史记录）。

**2026-10-22 指针（二）**：本 ADR 决策 5 与工单 0019 悬置的「index.json 直读 products 不过 kind 门禁」已由 **ADR-0010**（候选 8 收口）定案——索引不消费 kind（不投影），门禁归产品索引链；坏 kind 由「产品页恒渲染全量 → product-items 恒被调用」触发 errorf，隐式兜底的牙是 `assert_real` 产品页全量断言。

## 决策

1. **双 seam 拆分**：
   - `layouts/partials/product-items.html`（数据准备 seam）：索引渲染链中**唯一读 `hugo.Data.products` 的宿主**，负责 featured 过滤与 limit 截断，返回 slice，不渲染。入参：`featured`（bool，缺省 false）、`limit`（int，缺省或 0 = 全量；**负数即 errorf**——旧行为负数走 `gt 0` 分支外静默全量，属静默失效类）。
   - `layouts/partials/product-index.html`（纯渲染 seam）：**零全局依赖**，只渲染传入 items + 筛选 UI；`items` 与 `uid` **必填，缺失即构建失败**（「无缺省」宗教：nil 路径不得静默走空态）。空态文案留渲染 seam。
2. **无 source 注入位**：数据准备 seam 不留「传入 items 优先、缺省回落全局」的参数——缺省回落正是 ADR-0004 枪毙的 draft 分歧模式；后端重启时的数据源替换届时再开新 seam，不现在预留死参数。
3. **kind 契约化写死**：三枚 kind 筛选按钮 = CONTEXT.md「交付形态」封闭词表（workflow / document / question-bank）的执行区；词表由数据准备 seam 在构建期逐条执法——**未知或缺失 kind 即 errorf**，消息前缀「产品索引数据：」，含产品 id 与坏值（测试按此钉子串）。产品状态模块不碰：工单 0005 裁决（kind 是事实而非状态派生项）不变，升级的只是「不检查」→「数据门禁处检查」。
4. **uid 显式必填，重名不执法**：删掉 `default "mf-idx"` 死缺省；短代码由 `.Ordinal` 保证页内唯一，模板调用方传字面量（uid 兼深链锚）。同页重名不建检测机制——partial 无页级视野，重名检测要所有调用方多传 page 键 + `.Page.Store` 记账，成本与收益悬殊；契约写进 docstring。
5. **范围只收窄索引渲染链**：短代码、首页精选区（`index.html` 精选调用点）改走双 seam；首页计数条（ADR-0004 已定案、14/14 测试钉住）与搜索索引（`index.json`，属候选 8 搜索契约）保持各自迭代，`index.json` 留边界注释（kind 门禁靠「产品页恒渲染全量 → 数据门禁恒生效」兜底）。
6. **测试缝 = 合流 + 输入组合全覆盖**：测试留在 `tests/assert_product_states.py`（不新建脚本——fixture 基建单份，拆脚本即复制基建）；契约断言按用例钉子串（BAD_CASE_EXPECT，修掉旧判定只匹配统一前缀的弱点）；调用方级坏用例经真实调用链触发（limit 负数走短代码、items/uid 缺失走 layoutsDir 直调 partial）；fixture 含**非 featured 对照行 + 4 条 featured**——过滤与截断两个分支可分辨（旧全 featured 布局下「取前 3」与「过滤后取前 3」结果重合，过滤分支实际无回归保护，变异检验实测）；filters 开关差异有产物断言（产品页出筛选控件、首页精选区不出）。每条断言以变异检验证实有牙。
7. **命名与导航**：seam 文件名（product-items / product-index）即定名；CONTEXT.md 新增「产品索引」术语条（领域概念），seam 分工进 AGENTS.md 速查表（术语表不载文件布局）。

## Considered Options

- **数据准备外移到调用方**（拒绝：`where featured` / `first` 三处拷贝，改一次漏两处）；**保持内驻只正语义**（拒绝：接口泄漏原样保留，后续决策压在隐式全局依赖上）。
- **按 filters 分支 uid**（filters=false 不要求 uid）：拒绝——seam 加分支、首页深链锚消失、行为面变大。
- **uid 重名检测**（传 page 上下文 + .Page.Store）：拒绝——partial 无页级视野，全调用方改造成本与收益悬殊。
- **kind 词汇按数据派生**（按钮按出现 kind 去重生成）：拒绝——CONTEXT.md 词表失去执行锚点，加形态 = 改数据即改导航 UI，无审批点。
- **测试拆独立脚本**（assert_product_index.py）：拒绝——fixture 基建复制即第二实现，必然漂移（ADR-0004 枪毙过的模式）。

## Consequences

- 新增/下架产品只改 `data/products.yaml`，两个消费点（产品页全量、首页精选分栏）自动跟随；页面无手写产品列表。
- 新增第四种交付形态 = 改 `data/products.yaml` 的数据 + 同改两处执法点（数据门禁校验、模板按钮）——已知判断调用，留待词表真要扩展时再评估词汇 seam。
- 后端重启（项目负责人 2026-10-19 计划）时，产品数据源替换只动数据准备 seam 一处；ADR-0003「后端只镜像、分歧对齐 Hugo」的语义裁决对产品域继续有效。
- 搜索索引的 kind 门禁归属候选 8（搜索契约）；本 ADR 只在 `index.json` 留边界注释。
- **指针**：产品索引筛选的**交互行为层**（脚本、is-in 终态、计数、空态、减弱动效降级）归 ADR-0007 的 reveal 协议。
- 测试期望值均为独立字面量（非同义反复）；变异检验纪律：每条断言以「破坏实现→断言红→还原」证实有牙。

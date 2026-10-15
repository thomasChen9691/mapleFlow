---
id: 0005
title: 测试缝的形状
type: grilling
mode: HITL
status: closed
blocked_by: []
assignee: agent
map: map-product-state-convergence
claimed: 2026-10-15
closed: 2026-10-15
---

## Question

深化后的产品状态模块，测试断言什么？候选（可组合）：

- (a) 派生规则单测 —— fixture yaml → 期望状态表；
- (b) 构建产物断言 —— `hugo` 构建后解析 `public/products.html`，核对按钮态与首页数字；
- (c) 数据契约检查 —— `products.yaml` 每条状态字段合法、无未知交付形态、占位标记不冲突。

决策依据：工单 0002 的 seam 形状决定测试能穿过哪条缝；「接口即测试面」—— 测试必须与调用方走同一道缝，不得为可测性另造入口。

## Resolution

2026-10-15 · grilling（用户为决策者），三问落定：

1. **契约执法权在模块内**：输入契约（0003 定案）由 partial 内 `errorf` 执行，构建即门禁——本地 dev 与 CI 通吃，单一住所。排除独立契约检查器：它是契约规则的第二实现，必然漂移（F2 模式），且漏跑即无门。契约是模块接口的一部分，执法权在接口内侧（「接口即测试面」）。
2. **覆盖策略 = 双构建**：fixture 构建（4 状态组合 + 5 类坏数据用例）断言规则全覆盖，含 Q1 执法的行为验证（坏 fixture → 构建失败）；真实数据构建断言保留作线上回归——5-vs-0 失实本身就是真实数据 bug，纯 fixture 会漏。实现：测试配置叠加 hugo.toml 覆盖 `dataDir` 指向 fixture、构建到临时目录；**对 ADR-0001 是加法，生产构建命令一字不动**。
3. **运行阶段 = CI 权威 + 本地 advisory**：`deploy.yml` 在 build 与 deploy 之间插断言步，失败阻断部署（fail closed）；本地同一脚本 advisory 跑。脚本落 `tests/assert_product_states.py`，fixture 与测试配置同目录。版本 skew 不对称（0.164 风格代码在 0.167 同样合法），漏报风险仅限「有人写出 0.166 风格代码」——脚本头注释钉住「模块必须保持 0.164 兼容」纪律。

**断言清单**（执行期素材）：fixture 构建断言每条目的控件态（可点链接+文案 / 禁用占位+aria-disabled）、`data-price`、首页数据条计数；坏数据用例断言构建失败（非零退出）。真实构建断言同款控件态 + 计数（迁移后预期 5×即将上架、计数 0）。

**下游影响**：雾区「测试运行阶段」随本题溶解，地图雾区清空；0006 无新阻塞。

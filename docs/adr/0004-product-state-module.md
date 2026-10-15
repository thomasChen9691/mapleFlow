# 0004 - 产品状态模块：单一 return 型 partial，产物断言测试

产品的上架/免费判定与控件语义收敛在 `layouts/partials/product-state.html` 一个 return 型 partial，`product-index.html`、首页数据条与测试共用同一 seam；输入契约（字段必填、已上架⇒buy_url 真实、未上架⇒buy_url 空）由模块内 `errorf` 执法——不给缺省值，draft 分歧（ADR-0003 的教训）不重演；测试只以构建产物断言（fixture 双构建覆盖全部分支 + 真实数据守线上回归）。曾评估并拒绝预构建脚本方案：漏跑一步即静默渲染陈旧派生数据，等于用新的静默腐化源换可单测性。决策过程见 wayfinder 地图「产品状态模块深化图（候选 1）」（docs/wayfinder/map-product-state-convergence.md）。

**Considered Options**：预构建派生脚本（拒绝：漏跑即腐化）；独立契约检查器（拒绝：契约规则的第二实现，必然漂移）；规则级单测（Hugo 生态不存在模板单测机制，非主动放弃）。

**Consequences**：模板与首页不得自行推导产品状态，发现第二处推导即违本 ADR；模块必须保持 0.164 语义（单变量 + 根级单条 return）——本机 hugo 0.167 与 CI 钉版 0.164 之间存在不对称 skew，0.166+ 的条件多 return 写法本地过、CI 红；测试运行策略（CI 权威 + 本地 advisory，tests/assert_product_states.py）随模块落地一并建设。

id: "0063"
title: 构建入口的旗标分歧归谁
type: grilling
mode: HITL
status: closed
assignee: agent
blocked_by: ["0062"]
map: map-test-harness-convergence.md
created: 2026-10-25
claimed: 2026-10-25
closed: 2026-10-25
---

## Question

两个 Python 套件的构建入口是同名不同实现的复制：站点套件 `build()` 不带 `--minify`，SOP 套件带——分歧有文档化理由（SOP 套件注释解释了为何必须不同），但理由住在一份拷贝里，改一处漏一处。harness 统一构建入口后，这个分歧由谁表达。

要决策的面：

1. **分歧的表达形态**：harness 提供命名档位（如 site-contracts / sop 两档，档位自带旗标与理由注释），还是入口只收显式旗标、分歧留在各套件调用点？判据：档位是集中了知识还是把「为什么不同」埋进了档名；调用方显式传是否是另一种逐字复制（两个套件各写一遍旗标串）。
2. **共有旗标的归属**：`--cleanDestinationDir`、`--config`、`-d` 等两套件一致的旗标进 harness 默认；`--minify` 这类分歧项如何脱离默认集。
3. **分歧理由的文档化**：SOP 套件现有的「为何必须不同」注释随档位走（harness 档位 docstring）还是留调用点；将来第三套构建出现时，新增档位的门槛是什么（对照参数纪律：无读取点即死配置——档位没有消费方是否允许存在）。
4. **与真实构建命令的关系**：harness 的构建入口与 CI / 开发用的生产构建命令（`hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml`）是两套命令——测试构建故意不同（不 minify 便于断言）这一点是否需要显式声明，防将来有人「统一」成生产旗标。

边界（不开票）：tmp 目标目录的所有权归 tmp 工单（本票只决旗标）；Hugo 版本 skew 预检归预检工单。

事实前提：`assert_site_contracts.py:367-373`（run/build，无 --minify）与 `assert_sop_pipeline.py:117-128`（build，带 --minify 及理由注释）；`tests/assert_sop_pipeline.py:36-37` 的串行约束文档（该约束的存废归 tmp 工单）。

## Resolution

2026-10-25 · grilling（HITL，项目负责人两问定案；六票同场例外见地图 Notes）：

**分歧表达（Q1）**：**命名档位 + 显式 extras**。harness.build(config, dest, profile, flags=None)——档位封装基底旗标集与理由，逐调用差异走 flags：
- `site-contracts` 档 = `--cleanDestinationDir`（无 `--gc --minify`：断言要解析带引号属性与未压缩 HTML）
- `sop-pipeline` 档 = `--gc --minify --cleanDestinationDir`（与 CI 生产命令逐字一致：golden 按 minify 后的线上产物捕获，构建条件不一致则逐字节比对无意义——理由随档位走）
- `drafts` 语义糖拆除：唯一调用点改传 `flags=["-D"]`；site 的 `--contentDir` / `--layoutsDir` 同走 flags

**档位门槛与关系声明（Q2）**：档位 docstring 必须载「为什么是这组旗标」的理由（照 SOP 现有注释的规格）；新档位须过 0062 双门槛（≥2 消费者 + deletion test），档位表不得膨胀成无纪律配置（坑点 3 同款病）。站点 `real` 构建的承重不对称——**生产配置、故意不 minify、minify 形态归 CI 零 WARN 守门**——在 site 档 docstring 显式声明，防将来有人「统一」成生产旗标。

**对下游的输入**：build 落 harness 时按本票形态施工（属 0069 迁移批的确定工作项）；`prod` 档位不造（当前无消费方）。

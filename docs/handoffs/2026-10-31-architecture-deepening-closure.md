# 交接：架构深化收口（2026-10-31）

> 决策与契约见 **ADR-0016**（`docs/adr/0016-architecture-deepening.md`，四章 20 条）与地图 `docs/wayfinder/map-architecture-deepening.md`（已 closed，10/10 票）。本文只记当前状态、下一步、环境坑与建议 skill。

## 当前状态

- **地图已收口**：`map-architecture-deepening` 10/10 票 closed（0079–0088），frontier 空 = 目的地到达。决策集耐久化于 ADR-0016；ADR-0007 / 0008 各加一行指针（正文不改）。
- **四件落地**：① 文章卡片单模块（主题层 `post-card.html`，三面同卡、零参数、父容器契约载明）；② 注册缝下沉（引擎去 `autoInit`，`app.js` 的 `ENGINES` 表是唯一挂载点，逐个 try/catch，`scroll-in` fail-open）；③ 死面删除（2 个整文件 + 23 个选择器块，−196 行，零断言改动）；④ CSS 影子契约 parity 门（`tests/tokens.mjs` + `assert_reveal.mjs` 的 RGR-14）。
- **验证基线**：site **185/185** · npm **13+31+41** · sop **105/105** · 生产构建 **0 WARN** · 无 localhost 泄漏。
- **分支与提交**：`refactor/card-registration`（自 `refactor/featured-guard-module` 尖 `13c8f4a` 起，共 5 笔）——`31117d5` 文档（地图 + 10 票）、`34e068b` PR①（卡片 + 注册缝）、`8e7b785` PR② 第一笔（死面）、`08f1280` PR② 第二笔（parity 门）、末笔收口（ADR-0016 + 术语 + AGENTS + 地图 + 本文件）。**分支未推**（GitHub auth-required）。
- **已知偏差（诚实入档）**：`hugo.toml` 的注释遗留键**未删**（0085 决策 13 的一半未执行——复核后判定它们已带「已删除」标注、删掉会掩盖历史）；ADR-0016 Consequences 已记。

## 下一步

1. **推送与 PR**：`git push -u origin refactor/card-registration` → 开 PR → 门禁绿 → squash 合并。注意基数：本分支叠在未合并的 `refactor/featured-guard-module` 与 `refactor/harness-convergence` 之上，建议按 harness → featured-guard → card-registration 的顺序合，或先 `rebase --onto origin/main` 逐段落地。
2. **0079 事实票仍 open**（唯一 frontier）：四区事实已在施工中逐条查实并写进各票，但系统性的「四区事实底座 + token 矩阵」从未单独成文。若认为已无价值，可**关票并在地图 Out of scope 记一行**；若要留档，按票内五项盘一次。
3. **PR② 可选延伸**：`hugo.toml` 注释键清理（0085 决策 13 的另一半）可另开一笔；死面无长期门，若日后回流明显，再评估守门。

## 环境坑（本图新增）

- **shell 的 `grep` 对 `\|` 交替静默失效**（本图踩三次：`is-morphing` 误判、卡片类名误判、残留扫描漏检）——内容搜索一律用 Grep 工具，且**双向复核**（先查「有没有」，再查「是不是假阴性」）。
- **反向断言在解析为空时假绿**：`assert_featured_badge` 的「不带徽标」在 `grid={}` 时通过。凡「没有 X 就是对的」类断言，必须先有一条「解析到了东西」的前置。
- **模板条件类写在动作外面**（`class="mf-price{{ if x }} is-free{{ end }}"`）：抽取 class 属性前必须剥 `{{ … }}`，否则 token 粘成 `is-free{{`。
- **safe-delete 每轮预算 5000**、**单命令约第 6 个 node 进程会被 kill**（历图传承，仍适用）。

## 建议 skill

- **realeng-code-review**：每批收尾双轴评审——本图两批各抓到真问题（PR①：引用未落档 ADR、`zmedia.css` reduce 守卫漏改、RGR-13 源码扫描假绿；PR②：无——门自己抓到了抽取 bug）。
- **realeng-tdd**：红绿循环 + 变异检验照旧；纯删除批的变体 = 「删完套件原样全绿」即证据。
- **realeng-grilling**：下张地图开图用（一次一问、推荐先行、事实自查后问决策）。
- 无需 wayfinder 操作：本地图已 closed；开新工作先开新地图，勿往已闭图里加票。

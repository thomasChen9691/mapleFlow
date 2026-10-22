# 交接：候选 8「搜索契约」全程闭环（决策 + 同场施工，2026-10-22 终态）

## 当前状态

- **候选 8 全程闭环**：地图 `docs/wayfinder/map-search-contract.md` 已 closed，七工单 0042~0048 全 closed（0042 研究、0043-0048 质询，用户为决策者）。决策集耐久化在 **ADR-0010**（模块边界 / 字段契约 / kind 门禁 / 协议归属 / 测试缝五组）；**ADR-0006/0007/0009 各加指针行**（0019 边界定案 / 搜索 JS 归属闭环 / featured 不投影）。术语/导航：`CONTEXT.md`「搜索索引」条一词两指针、`AGENTS.md` §3 命令不变 / §7 新增 `index.json` 与 `fastsearch.js` 两行 / 坑点 13「搜索契约纪律」/ 坑点 9 的「归候选 8」指向已更新。
- **代码与测试**：两个契约定义处落位——`layouts/_default/index.json` 文件头 docstring（投影契约五块：字段表[含 featured/kind 负向决策与同源确认] / 三类排除 / 产品投影 / fastsearch 接口条款[fetch 同目录 index.json] / errorf 清单）+ `themes/maplemod/assets/js/fastsearch.js` 文件头 docstring（检索协议现状快照：挂点 / .focus 双落点 / li 结构 / 键盘语义含 Escape 在结果门之前 / XHR 容错三条已知限制）。投影侧：产品 name/summary 缺失即 errorf（前缀「搜索索引数据：」，两个 bad 用例）；字段集冻结六项。检索侧：**fuseOpts 参数位删除**（head.html 传参 + import + 两分支，默认值升格契约）。测试：`assert_site_contracts.py` **76/76**（候选 7 闭环 61 → 0043 批 +10 → 0044/0046 批 +2 → 本批 +3 交付面断言；头注释七类）、`assert_sop_pipeline.py` **104/104**、`npm test` **16/16**、生产构建 exit=0、无 localhost 残留；新断言全部变异检验（投影字段 / keys / 排除 / plainify / permalink / content / fetch 路径 / 脚本接线各红过）。
- **施工期翻出并处置的盘外事实**（已入工单 0046 施工期补记）：项目级 `assets/js/fastsearch.js` 覆盖（子模块时代遗产）因 `resources.Get` 项目级优先而**一直是活文件**，主题层副本是死的——0043 的 B3 断言与 docstring ④ 一度读的是死文件。已把 XHR 同目录修正合并入主题层、`git rm` 站点副本、加单副本守门断言、修 head.html preload 的 `../index.json` → `index.json`（同一子路径 bug 的另一半）、改正 docstring ④ 的 fetch 路径条款。
- **提交与 CI**：`943e41b`（0043 决议 + 投影契约施工）→ `49ec9ac`（0044/0046 决议 + 同场施工）→ 本收口批（0045/0047/0048 决议 + ADR-0010 + 导航收口）随本交接文档同批落库——**三笔均已 commit、未 push**（push 与 CI 验证由项目负责人决定节奏，候选 7 先例）。
- **无在途工单**：本地 markdown 追踪器无 open 工单；工作区仅 `.workbuddy-ai/` 未跟踪。

## 下一步

1. **push 并验 CI**（若项目负责人指示）：三笔提交一次推送，deploy.yml 的 Assert site contracts 步将首次覆盖搜索契约断言。
2. **内容类待办**（卡用户材料，不随图，自候选 7 继承）：`data/products.yaml` 的 `buy_url` 填空 + `listed` 翻 true、`content/about.md` 真实简历、`hugo.toml` socialIcons 真实邮箱、删 `content/posts/my-first-post1.md` 脚手架。
3. **重写 fastsearch 时的既有输入**（地图 Out of scope，非本图）：结果呈现层深化（摘要/标签/高亮）、引擎形态（ESM 模块化 + fuse/license 依存）、索引加载失败容错 UX——届时以本图的快照契约为输入，测试与新契约一起 TDD。
4. **可选新需求**：菜单 4 个 `parent = "categories"` 子项配置了但 `header.html` 不渲染——要渲染是功能决定，另开。

## 建议 skill

- **realeng-wayfinder** — 下一张图（若有）先排地图（目的地先行、工单是待决策问题、一会话一工单）。
- **realeng-grilling** — 一次一问、先给推荐答案；事实自己查（本图两处「我以为的事实」都是查/file 才翻的盘：项目级覆盖层、Hugo truncate 省略号外的 fixture 字面量空格）。
- **realeng-tdd** — 红绿一次一行为；本图固化三条：① 每条断言变异检验（本图累计 11 次变异全红才收）；② 表征测试（现状即契约时）以变异证明有牙；③ 行为保持型重构（fuseOpts 删除）的全套 + 构建 + 产物 grep 三重验收。
- **realeng-code-review** — 双轴并行，固定点取该批首个提交前；本图它抓出两处最重的：文档记着已删机制（落地说明）、docstring 快照与代码行为不符（Escape 门条件）。
- 环境注意：本 shell 的 grep 对 `\|` 交替失效（用 `-e` 多模式或 Grep 工具）；`sed -i ''` 在 macOS 需带空串参数；`gh` 未安装（查 CI 用 API + curl）；**沙箱升级时命令行输出会错乱**——`git add && git commit && git push` 链可能显示 "nothing added to commit" 而提交实际已成功，判断提交是否落库以 `git log` 为准，勿被回显骗到重复提交。

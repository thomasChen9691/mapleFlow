# 交接：候选 4 收口与积压提交待推送（2026-10-19）

> 本场做完候选 4「product-index 接口收窄」全程（排图→研究→质询→施工→收口→文档），
> 并处理了两笔积压。决策已全部耐久化在 ADR-0006 / CONTEXT.md / AGENTS.md，
> 本文不重复其内容——按 AGENTS.md §8.1 读 `CONTEXT.md` + `docs/adr/` 即可发现本模块。

## 当前状态

- **候选 4 地图已关闭**：`docs/wayfinder/map-product-index-narrowing.md`（status: closed），六工单 0015~0020 全 closed；决策集落 ADR-0006，CONTEXT.md 有「产品索引」术语条，AGENTS.md 坑点 11 + 速查两行。
- **代码与测试**：双 seam 已落地（product-items 数据准备 / product-index 纯渲染），产品测试 29/29、SOP 100/100、生产构建 exit=0、`localhost:1313` 零残留。
- **本地领先 origin/main 9 个提交，均未 push**：
  - `197d2ae` 交接文档补写（上一场的欠账）→ `7cf08f8` MAPLEFLOW_BLOG_SOP.md 退役标注（backend 内容按用户指示保留，只为未来重启后端留参考）→ `d58af84` 排图 + 0018 研究解决 → `94e00c4` 0015/0016 决议 → `14b6dc8` 0015/0016 施工 → `cd0ee23` 0017/0019 决议 → `569339b` 0017/0019 施工 → `515726a` 0020 决议 + 地图收口 → `908e150` ADR-0006 与导航痕迹。
- **两个遗留项**（评审记录在案，未决）：
  1. kind 封闭词表两处执法点（product-items 校验 + 模板按钮），加第四种 kind 须同改两处——词表真要扩展时再评估词汇 seam；
  2. 搜索索引（`layouts/_default/index.json`）的 kind 门禁归属**候选 8**（0019 决议），index.json 已留边界注释；首页计数条门禁无需求（ADR-0004）。
  3. `assert_bad_caller_direct` 四参数 Data Clumps——再加第五格坏用例时收拢为 dict。
- **工作区噪音勿动**：`themes/PaperMod` 子模块 dirty（纯行尾，gitlink 未变）；`.workbuddy-ai/` 未跟踪。注意 `auto_push.py` 的 `add .` 会误带子模块状态，提交按文件精确暂存。

## 下一步

1. **push**（`git push origin main`）触发 CI：Build → assert_product_states → assert_sop_pipeline → Deploy，两断言步即守门点；推完线上抽查（products.html 5 条全「即将上架」、首页精选 3 条、无 localhost 残留）。
2. **下一张图三选一**（候选 4 的雾区已随 0019 部分溶解，剩余归各图）：候选 5「reveal 协议」（客户端筛选脚本与 `.reveal`/`is-in` 交互的契约化，0019 明确其边界留给本图）、候选 6「主题 fork」、候选 8「搜索契约」（含 index.json 的 kind 门禁归属与投影字段定案）。
3. **内容类待办**（卡用户材料，不随图）：`data/products.yaml` 的 `buy_url` 填空 + `listed` 翻 true、`content/about.md` 真实简历、`hugo.toml` socialIcons 真实邮箱、删 `content/posts/my-first-post1.md` 脚手架。
4. 用户 2026-10-19 计划**重启后端开发**：届时产品数据源替换只动 product-items 一处（ADR-0006 决策 2/Consequences）；ADR-0003「后端只镜像、分歧对齐 Hugo」语义裁决继续有效；`docs/sop/MAPLEFLOW_BLOG_SOP.md` 的 backend 历史指令已作退役标注、保留参考。

## 建议 skill

- **realeng-wayfinder** — 开下一张图（候选 5/6/8）时先排地图：目的地先行、工单是待决策问题、一会话一工单。
- **realeng-grilling** — 每张工单一次一问、先给推荐答案；事实自己查（文件/子代理），决策问用户。本场五轮质询用户全选推荐，节奏已验证。
- **realeng-tdd** — 新行为先红后绿、每轮单独 commit；本场固化两条纪律：① 每条断言用变异检验（破坏实现→断言红→还原）证实有牙——正是它抓出 fixture 全 featured 布局下 where 分支无回归保护的洞；② 测试期望值必须是独立字面量。
- **realeng-code-review** — 每批完工跑双轴（固定点取该批首个 commit；spec 源在工单 Resolution）。本场它抓出 CONTEXT.md 术语条混入文件级细节的硬伤。
- **realeng-domain-modeling** — 新术语当场进 CONTEXT.md（本场「产品索引」即此路径）。
- **realeng-improve-codebase-architecture** — 选下一个候选前重跑（旧评审报告在 `internal/`，已 gitignore）。
- **realeng-handoff** — 会话收尾压缩交接，存 `docs/handoffs/`。

## 本场踩到的坑（值得记住）

- **本 shell 的 grep 对 `\|` alternation 失效**（多次误报 0 命中）——验证用 `sed -n` / `grep -e a -e b` 或直接读文件；`&&` 链中 grep 无命中会静默短路后续命令，验证类命令用 `;` 分隔。
- **Hugo 配置合并语义**：`layoutsDir` 写在追加 `--config` 文件里不生效，必须走 CLI flag；`--dataDir` 无 CLI flag，走配置文件——调用方级坏用例用二者组合。dataDir 覆盖到空目录会连带抹掉 `sop.yaml` → SOP 派生页消失 → 索引页 ref 失败，空态测试须放 fixture 的 sop.yaml 镜像。
- **Hugo `errorf %q` 对 nil 输出 `%!q(<nil>)`**——契约消息的可变字段先 `| default "<缺失>"`。
- **minify 后 HTML 属性无引号**（`id=mf-idx-home`）——grep 断言别写带引号的属性。
- **fixture summary 含未加引号的 `: `（冒号空格）会 YAML 解析失败**。

# 交接：2026-10-23 待办清理批（17 项清单 → 12 项落地，产物中性，已推已验）

> 本文只记本批终态、决策落点与去向，不重述 `CONTEXT.md` / `docs/adr/` / 工单已有内容。
> 待办清单本体在 **`docs/backlog.md`**（17 项，含每项证据、验收与来源），后续工作以它为准。

## 当前状态

- **本批范围**：`docs/backlog.md` 的 17 项中完成 **1-10、14、15**，另对 **11** 做出「不重写」的决策；**12、13** 挂起，**16、17** 为风险登记（无需动作）。9 笔提交 `c19c17f`…`0aeb1e8` 已推，`origin/main == HEAD == 0aeb1e8`，工作区干净。
- **CI 全绿**：run **39881178618**（head=`0aeb1e8`）十步全 success；三套测试 76/76、104/104、16/16；构建零 WARN（原 3 条弃用警告已清）。
- **产物中性已证明，不是假设**：`git worktree` 检出 `504d63e`（批前）与 `0aeb1e8` 各做一次生产构建，`diff -r` 两个 `public/` **0 行不同**。因此 gh-pages 分支头**仍停在 `5d9c240` 是正确的**——部署步 success 的含义是「无差异、无需发布」，不是故障。昨日 `504d63e`（docs-only）同理。
- **本地 vs CI 的唯一字节级差异 = generator meta**（线上 `Hugo 0.164.0` vs 本机 `0.167.0`）；线上 `index.json` 与本地 0 差异、首页归一化版本号后完全一致。这是第 15 项版本防呆的实证。
- **线上终态核对通过**：导航 9 项且顺序不变、`dir=auto`、`index.json` 17 条恰六字段、产品锚点 `/mapleFlow/products.html#<id>`、`search.html` 与分类页均 200、无 `localhost:1313` 残留（索引内唯一 `localhost` 是 Grafana SOP 正文的 docker 示例）。
- **本批决策的耐久落点**（细节不在此重述，只给指针）：
  - 后端不重启 → `docs/adr/0006` 末尾指针行（含将来重启的可证伪触发条件）
  - 不重写 fastsearch → `docs/adr/0010` 末尾指针行（仅渲染层按需改）
  - CHANGELOG 冻结 → `docs/CHANGELOG.md` 文件头
  - OpenSpec 退役 → `docs/README.md` 与 `docs/wayfinder/README.md` 的历史指针
  - Hugo 版本 skew → `tests/assert_site_contracts.py` 的 `preflight_hugo_version()`（WARN，不进断言计数）
- **踩到并已修的盘外事实**（若复现先读这里）：Hugo 的 `site.Menus.main` **不含 `parent` 子项**（实测），故那 4 条 `parent="categories"` 是零读取点死配置；`AGENTS.md` §7 表曾挂着早已删除的 `reorderNavItems`；`grep -c "\[\[menu.main\]\]"` 会把注释里的同名字符串也数进去（`hugo.toml:94`）。

## 下一步

1. **第 12 项（搜索入口形态）与第 13 项（精选三条雾区）**：都是「目的地未定」的决策项，各自需先排地图再动工——不要直接施工。第 12 项依赖第 11 项的结论（ADR-0010 已定「不重写引擎」），因此它只剩「渲染层要不要加摘要/标签」与「入口形态」两个子问题。
2. **内容填充仍卡外部输入**（不随批、不随图，见各地图 Out of scope）：`data/products.yaml` 的 `buy_url` + `listed`、`content/about.md` 真实简历、`hugo.toml` socialIcons 真实邮箱。`docs/backlog.md` 末尾有指针，别丢。
3. **可选**：本批没走地图（纯清理批），若项目负责人要求补流程记录，可把本交接当作该批的记录，无需另立工单。
4. 若下次要动模板/构建：**先跑一次 `python3 tests/assert_site_contracts.py`**，开头的版本 WARN 是 Hugo 版本 skew 提醒，别当噪音忽略。

## 建议 skill

- **realeng-wayfinder** — 第 12/13 项开图前先排地图（目的地先行、工单是待决策问题、一会话一工单）。
- **realeng-grilling** — 决策项访谈（一次一问、先给推荐答案；事实自己查）。
- **realeng-tdd** — 若第 12 项真的动渲染层，新契约与新测试一起出生。
- **realeng-code-review** — 收口前双轴评审；本批的经验是它最擅长抓「文档记着已删机制」。
- **环境注意**：① 本 shell 的 grep 对 `\|` 交替失效，用 Grep 工具；② `gh` 未安装，查 CI 用 `curl` + GitHub API（未认证可读 runs/jobs，logs 需 admin）；③ 按 SHA 匹配 run 用 `startswith` 或全量 SHA；④ 判断「改动是否影响线上」用 `git worktree` 双构建 `diff -r`，比 spot-check 强得多。

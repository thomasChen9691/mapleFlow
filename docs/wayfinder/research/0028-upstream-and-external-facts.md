# research/0028 —— 上游与外部事实（PaperMod / Hugo / 许可）

> 工单：[tickets/0028-upstream-external-facts.md](../tickets/0028-upstream-external-facts.md)（地图：map-theme-fork.md，候选 6 主题 fork 图）
> 产出：2026-10-20，research 子代理核实（WebSearch/WebFetch + 本地只读），未执行任何 git 命令。外部访问日期均为 2026-10-20。
> 用途：候选 6 各决策工单的外部事实底坐。本文只产事实，不产决策；未核实处以「未验证」标注。

## 1. 上游现状：hugo-PaperMod 相对钉住 commit 的差距

| 事实 | 值 | 来源 |
|---|---|---|
| 钉住 commit 6c5a8f6 的日期 | committer date `2026-01-09T16:11:22Z`，消息 "Update LICENSE (Add current year 2026)" | api.github.com/repos/adityatelange/hugo-PaperMod/commits/6c5a8f6 |
| **6c5a8f6 → master 落后提交数** | **ahead_by = 92，behind_by = 0**（compare `6c5a8f6...master`，三次独立请求一致） | api.github.com/repos/adityatelange/hugo-PaperMod/compare/6c5a8f6...master |
| 交叉佐证 1 | `v8.0...6c5a8f6`，ahead_by = 55——与本地 `git describe` 的 `v8.0-55-g6c5a8f6` 完全吻合，证明 compare 计数可信 | api.github.com/.../compare/v8.0...6c5a8f6 |
| 交叉佐证 2 | `v8.0...master`，ahead_by = 147（v8.0 之后全部在 master 滚动） | api.github.com/.../compare/v8.0...master |
| master HEAD | `969bebdc5600a1639158b5ef4eff9cf6cbb511ac`，`2026-10-18T15:16:39Z`，"fix(post_meta): format date tooltip as ISO 8601, closes #1865" | api.github.com/.../commits/master |
| 仓库活跃度 | `pushed_at 2026-10-18T15:16:54Z`（距访问日 2 天）；`updated_at 2026-10-19`；`archived: false`；open issues 10；stars 14,004；forks 3,441 | api.github.com/repos/adityatelange/hugo-PaperMod |
| 分支 | 仅 `master`（protected）与 `exampleSite` | api.github.com/.../branches |
| 最新 tag / release | **最新 tag 即 v8.0，无 v9**；v8.0 release 发布于 `2024-11-03T07:58:18Z`（prerelease=false，latest） | api.github.com/.../tags、.../releases |

事实小结（非决策）：钉住点距上次正式发布（v8.0，2024-11-03）约 55 个提交；距 HEAD 落后 92 个提交、时间跨度约 9.3 个月（2026-01-09 → 2026-10-18）。上游活跃（距访问 2 天仍有 PGP 签名提交），但 release 策略为 v8.0（2024-11）之后只滚动 master、不打新 tag。compare 响应中摘录到的钉住后主要变更（未经逐条 API 复核）：llms.txt 支持（3bb0ca2，2026-01-25）、`hiddenInRss` 排除 RSS（#1833）、`.post-content`→`.md-content` CSS 重构、audio/video shortcodes、多项 Hugo 上游 tpl 补丁移植（RSS/opengraph/twitter_cards）。逐条日期来自 compare 提交列表的模型读数，**未验证**，需要逐字引用前应再逐条核对。

## 2. Hugo 0.164 主题解析机制（官方文档）

- `themesDir` 默认值即 `themes`：`(string) The designated directory for themes. Default is themes.`（https://gohugo.io/configuration/all/ ，访问 2026-10-20）
- `theme` 键定义：`(string or []string) The theme to use. Multiple themes can be listed, with precedence given from left to right.`（同上）
- **主题名与目录名绑定**（改名是否必须同步 hugo.toml）：官方 theme-components 页原文—— "The name used in the `theme` definition above must match a directory in `/your-site/themes`, e.g. `/your-site/themes/my-shortcodes`."（https://gohugo.io/hugo-modules/theme-components/ ，访问 2026-10-20）。即：把 `themes/PaperMod` 改名为 `themes/maplemod` 后，`hugo.toml` 的 `theme` 字段**必须同步改为 `maplemod`**，否则 Hugo 按名字找不到主题目录。本站 `hugo.toml:23` 当前为 `theme = "PaperMod"`（本地只读确认）。
- **项目 layouts/ 对主题的优先顺序**（0.146.0 模板系统重写后的官方表述，适用于 0.164）：lookup-order 页原文—— "Templates can live in either the project's or the themes' `layout` directories, and the most specific templates will be chosen. Hugo will interleave the lookups listed below, finding the most specific one either in the project or themes."（https://gohugo.io/templates/lookup-order/ ，访问 2026-10-20，页面标注 "We did a complete overhaul of Hugo's template system in v0.146.0"，最后更新 2026-06-18）。theme-components 页给出更直接的优先级表述—— "For any given file, data entry, etc., Hugo will look first in the project and then in `my-shortcodes`, `base-theme`, and lastly `hyde`."；且 "For `static`, `layouts` (templates), and `archetypes` files, these are merged on file level. So the left-most file will be chosen."（layouts 合并粒度是**文件级**，最左优先；项目在最左）。
- **themes/ 下的非子模块普通目录 = vendored 主题，构建行为不变**：机制事实链——(a) Hugo 只按 `theme` 键 + `themesDir` 挂载目录，"Imported modules automatically mount their component directories to Hugo's unified file system"（use-modules 页，https://gohugo.io/hugo-modules/use-modules/ ，访问 2026-10-20）；Hugo 不感知 git/子模块。(b) 官方 vendoring 定义："To vendor (verb) is to include the source code of third-party dependencies directly within your project's repository, instead of downloading them from an external package manager when needed."（同上）。(c) submodule 只是 PaperMod wiki 列出的四种等位安装方式之一：Method 1 `git clone`、Method 2 submodule、Method 3 下载 zip、Method 4 Hugo module，四种方式产出的目录对 Hugo 完全等价（https://github.com/adityatelange/hugo-PaperMod/wiki/Installation ，访问 2026-10-20）。结论：去掉子模块、文件原样留在 `themes/PaperMod`，Hugo 侧挂载与查找完全一致。**未验证项**：本次未在本地实跑构建对比，以上为文档机制结论。
- CI 钉的版本存在且为正式版：**Hugo v0.164.0 发布于 2026-07-06T17:48:54Z**（api.github.com/repos/gohugoio/hugo/releases/tags/v0.164.0，访问 2026-10-20）。官方文档页最后更新 2026-10-10，已含 v0.168.0 内容——0.164 与文档描述同代，无版本代差风险。

## 3. 子模块退役的机制事实（未执行任何 git 命令）

- 官方整体删除语义（gitsubmodules(7)，https://git-scm.com/docs/gitsubmodules ，访问 2026-10-20）："A submodule can be deleted by running git rm <submodule-path> && git commit. … The deletion removes the superproject's tracking data, which are both the `gitlink` entry and the section in the `.gitmodules` file." 另有 deinit 仅改 `$GIT_DIR/config`、不动历史（git-submodule 文档，https://git-scm.com/docs/git-submodule ）。
- `git rm --cached` 的语义（git-rm 文档，https://git-scm.com/docs/git-rm ，访问 2026-10-20）：`--cached` — "Use this option to unstage and remove paths only from the index. Working tree files, whether modified or not, will be left alone."；且 SUBMODULES 节明确："If it exists the `submodule.<name>` section in the gitmodules[5] file **will also be removed** and that file will be staged (**unless `--cached` or `-n`** are taken)." 即：`git rm --cached themes/PaperMod` 只摘除 index 中的 gitlink、**不会**动 `.gitmodules`（需另行删除 `.gitmodules` 并 commit），工作区文件原样保留——这正是「保留文件、改普通目录入库（vendor 化）」的机械路径：`git rm --cached themes/PaperMod` → 删 `.gitmodules` → `git add themes/PaperMod` → commit。注：官方文档分别给出 `--cached` 与整体移除的语义，但**没有**以一页形式给出「保留工作区文件的编号 vendor 流程」；该组合为社区通行做法（此点如实标注）。
- `actions/checkout` 的 `submodules` 行为（https://github.com/actions/checkout ，访问 2026-10-20）：文档原文 "Whether to checkout submodules: `true` to checkout submodules or `recursive` to recursively checkout submodules. … **Default: false**"。事实推论：默认 `false` 时子模块**不会**被检出；本站 `deploy.yml:26-29` 现为 `actions/checkout@v4` + `submodules: true` + `fetch-depth: 0`（本地只读确认），即当前 CI 依赖显式 `true` 才能拿到主题。子模块退役后，主题文件作为普通目录随主检出必然入库，`submodules` 取 `false`（默认）或保留 `true`（无子模块可拉）两种情况构建均可成功——**移除后不要求为构建正确性改动 deploy.yml**；是否顺手改回默认属清理性决策，本报告不代做。
- 本地 `.gitmodules` 当前只有一条记录：`[submodule "themes/PaperMod"] url = https://github.com/adityatelange/hugo-PaperMod.git`（只读确认）。

## 4. MIT 许可义务

- 本地 `themes/PaperMod/LICENSE`（只读确认）：标准 MIT，两行版权声明——`Copyright (c) 2020 nanxiaobei and adityatelange` 与 `Copyright (c) 2021-2026 adityatelange`；与上游 6c5a8f6（该 commit 正是把 2025 改为 2026）逐字一致。
- 最低义务（choosealicense.com MIT 页，https://choosealicense.com/licenses/mit/ ，访问 2026-10-20）：MIT 的 Conditions 只有一条 "License and copyright notice"；正文要求 "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."。Permissions：commercial use / distribution / modification / private use；Limitations：liability / warranty。事实推论：fork + 修改后，凡**分发**副本或实质部分时须随附版权声明与许可声明；仓库内继续保留 `LICENSE` 文件（含原版权行）即为该义务的常规满足方式；私有部署不构成分发，义务不触发。
- PaperMod 源码自带版权头：`assets/css/core/license.css` 与 `assets/js/license.js` 头部注释（6c5a8f6 的 patch 可见，"PaperMod v8+ / License: MIT … / Copyright (c) …"），保留这些文件头是内附带声明的最常见落点。
- 署名/鸣谢要求：**无强制要求**。README "Support" 段原文为 "Star 🌟 this repository." "Help spread the word about PaperMod by sharing it on social media and recommending it to your friends." "You can also sponsor 🏅 on Github Sponsors / Ko-Fi."；wiki Installation "Support" 段同样仅 star / 传播 / sponsor 三项，均为自愿请求而非许可条件；README/wiki 均无「保留页脚署名」类条款（本地 README.md 全文 + wiki Installation 页只读核实，2026-10-20）。

## 5. Hugo 官方/社区对 fork 主题后跟随上游的指导

- 官方 quick start 至今仍以子模块为教学路线：`git submodule add https://github.com/gohugo-ananke/ananke themes/ananke` + `echo "theme = 'ananke'" >> hugo.toml`（https://gohugo.io/getting-started/quick-start/ ，访问 2026-10-20，页面最后更新 2026-10-10）。
- 旧版 theme-management 页 `gohugo.io/hugo-modules/theme-management/` 返回 **404**（访问 2026-10-20）——官方独立的「主题管理」页已不在；现行入口是 quick-start（子模块）、theme-components、use-modules 三页。
- Hugo Modules 与子模块在 0.164 时代的取舍事实（均为官方页原文或机制）：
  - Modules 需要本机 Git + Go ≥1.18；`hugo mod get -u` 按版本查询更新，`go.mod`/`go.sum` 记录版本与校验和，"Clearing the module cache and rebuilding will re-download the originally imported module version … ensuring consistent builds"（use-modules 页）。
  - `hugo mod vendor` 生成 `_vendor` 目录提交入库；且 "Modules within the `themes` directory are not vendored."（同上）——即 themes/ 下的主题目录不参与该 vendor 路径。
  - `hugo mod init` 后主题经 `module.imports` 声明；theme-components 页支持多主题组件 `theme = ['my-shortcodes', 'base-theme', 'hyde']`，优先级从左到右（官方文档：fork 出的层可与其它组件叠加，项目同名文件始终最左/最优先）。
  - **官方是否明确「modules 取代 submodule」**：本次核实的全部官方页中**未见**逐字的取代性推荐；官方 quick start 仍教 submodule，modules 提供的是版本化、可复现的更新路径。更强的立场表述（如论坛/官方公告级别）**未验证**。
- 社区通行（标记为社区实践，非官方条文的）：fork 后保留一个 upstream remote、按需 `git fetch upstream && git merge upstream/master`；除 upstream git 外，也可用 `git remote add` + PaperMod wiki 的 Method 1/2/3/4 各更新路径（`git pull` / `git submodule update --remote --merge` / `hugo mod get -u`）。官方文档无专门「fork 主题如何跟随上游」指南——**未检索到官方专门指南**。

## 未能核实 / 需注意的项

- compare API 提交数组的逐条日期读数在两次请求间不一致（大 JSON 经 WebFetch 中转被截断），故第 1 节中钉住后的逐条变更列表标注「未逐条复核」；`ahead_by` 顶层计数三次一致（92），且有 v8.0→钉住点 =55 与本地 `git describe` 吻合佐证，可信。
- 第 3 节「`git rm --cached` 保留工作区文件的完整编号流程」为官方两种语义（`--cached` 只动 index；`git rm` 全量移除并清理 `.gitmodules`）组合出的机制结论，官方未以单页给出该组合流程。
- 未在本地执行构建/测试验证任何改动——本报告不含任何执行性操作。

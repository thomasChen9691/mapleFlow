# 交接：CI/CD 重建 + 规则集 + 视觉批 E/F（2026-10-24 终态）

> 决策与契约不在此重述，按需取：**ADR-0013**（搜索浮层与 ADR-0010 重评）· **AGENTS.md** §2/§3/§4坑点14/§7（分支模型、命令、搜索前端纪律）· `docs/adr/0010-search-contract.md` 末段指针（重评结论）· 主题 fork 分层判据见 **ADR-0008**。本文只记当前状态、下一步、建议 skill。

## 当前状态

- **分支与 PR**：`style/css-modern-batch`（origin 已同步）= **3 笔提交待合并**——`980c57d`（E 批 CSS 现代化：dvh / 浮层退出过场 / 滚动稳定性 / text-wrap / 触屏 polish）、`38ef931`（P1 CLS：render-image 注入真实宽高 + `img{height:auto}` 配对 + fixture/断言）、`db12d86`（F 批：iOS 双机制滚锁 / inert 背景钉住 / @starting-style 统一进出场 / 打印样式）。**PR 未创建**——GitHub 连接器对本仓库只读（写 403），创建与合并须用户在 UI 点：https://github.com/thomasChen9691/mapleFlow/pull/new/style/css-modern-batch
- **合并后预期**：这次 gh-pages **会推进**（E/F 批改了 CSS 与 render-image，产物有 diff；对照：上一次 docs-only 的 PR #1 产物逐字节一致、gh-pages 不动——两种行为都已实证）。
- **规则集 `main-protection` 已生效并验证**：直推 main 被拒（GH013，检查名 `验证（测试 + 构建 + 守门）` 零偏差 + PR-required 双命中）；PR #1 走完「门禁绿 → squash 合并 → 自动部署」全链。配置在 GitHub Settings → Rules → Rulesets（仓库侧，仓库内无副本）。
- **CI/CD**：`.github/workflows/ci-cd.yml`（verify + deploy 双 job、PR 门禁、零 WARN 守门、localhost 泄漏守门）——push 与 PR 事件均实测绿。`assert_sop_pipeline.assert_ci_wiring` 已改 glob（不再钉工作流文件名）。
- **验证基线**：三套 **155/155 · 104/104 · 23+41**；生产构建零 WARN、无 localhost 泄漏。浏览器实测全过（含打印媒体模拟、inert、iOS 滚锁、@starting-style 进入过场的逐帧采样）。
- **P2 jank 结案**：body 固定渐变层三方案滚动帧率无差异（0% 掉帧）→ **不改**，`background-attachment: fixed` 是刻意设计。
- **本地环境**：main = origin/main = `89c3d50`；工作树干净；Hugo 本机 0.167 / CI 钉 0.164（skew WARN 是提醒不是失败）。

## 下一步

1. **唯一待办（用户侧）**：开 PR 合并 `style/css-modern-batch` → 门禁绿 → squash → 自动部署。合并后删远端分支、本地 `git pull`。
2. **可选后续（非紧急，按触发条件再排）**：
   - `content-visibility: auto`（页脚 / 长列表渲染省电）——**必须配 `contain-intrinsic-size`**，否则滚动条会跳；改动前先量 CLS/滚动位置稳定性。
   - 负向测试「PR 必需检查失败时合并被阻塞」未做（正向链路已全验；约束已由直推拒绝信息间接证明）。
   - 观察器脚本的哨兵重置缺陷（`/tmp/cicd-watcher.sh`，一次性脚本不入仓）——若复用须先修「基线置位后合入事件未重置 DEPLOY_SEEN」。
3. **内容侧**：products.yaml 的 buy_url/listed、about.md 真实简历、socialIcons 邮箱——仍卡用户材料，不排期。

## 建议 skill

- **realeng-code-review**：本项目每批的「双轴评审（Standards/Spec）+ 修完再提交」惯例——下批照例。
- **realeng-diagnosing-bugs**：布局/样式怪症的排查循环（本会话两次靠「先实测再下结论」救场：误判死声明、误判泄漏，一次真 bug 也是靠产物+computed 双重验证抓回）。
- **frontend-design**：继续视觉批次（P3 余项已清；新视觉需求出现时用）。
- 排查 CI 红或线上异常时：公开 API 可匿名查 runs/jobs（本会话已验证），但 **Actions 日志下载与规则集读写需要管理员 token**（连接器对本仓库只读）。

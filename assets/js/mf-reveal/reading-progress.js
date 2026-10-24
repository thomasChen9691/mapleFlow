/**
 * reading-progress.js —— 阅读进度条（reveal 协议·行为层）
 * ============================================================
 * 【阅读进度契约的定义处——2026-10-24 D1】
 * 条本身是纯视觉（顶部固定 2px，宽度由 CSS 变量驱动）；本引擎是**唯一写入方**，
 * 与 scroll-in.js 同族：都只读滚动位置、只写一个状态位，不做布局计算。
 *
 * DOM 契约：
 *   读  `.mf-progress`（仅文章页渲染；缺失即 no-op → 非文章页静默降级）
 *       `.post-content`（量测对象：只量正文，不含标题 / 目录 / 上下篇）
 *   写  `.mf-progress` 上的 `--mf-progress`（0..1，三位小数字符串）——
 *       样式侧 `.mf-progress span { transform: scaleX(var(--mf-progress, 0)) }`
 *   降级  缺任一挂点 → no-op；无 requestAnimationFrame → setTimeout 兜底
 *   节流  scroll 用 rAF 合并；监听 passive（不阻塞滚动）
 *
 * 计算（纯函数 computeProgress，导出供测试直接喂字面量）：
 *   p = clamp((scrollY - contentTop) / (contentH - viewportH), 0, 1)
 *   内容不足一屏（contentH <= viewportH）→ 0：条保持空，不谎报「快读完了」。
 *
 * 与 no-js 基线（ADR-0002）的关系：`.no-js .mf-progress { display:none }`——
 * 无 JS 时整条不出现，内容零影响。
 * 与减弱动效偏好的关系：进度条是**功能性指示**（同滚动条），不做动画、不加
 * transition，故不豁免——它只随滚动变化，不产生自主运动。
 *
 * 测试：tests/assert_reveal.mjs（RGR-9 纯函数字面量 / RGR-10 写入 seam /
 * RGR-11 缺挂点 no-op）；产物面由 assert_reveal_artifacts 守（文章页有、列表页无）。
 */

/** 进度纯计算：所有输入显式传入，不读全局（测试可直接喂字面量） */
export function computeProgress({ scrollY, viewportH, contentTop, contentH }) {
  const scrollable = contentH - viewportH;
  if (scrollable <= 0) { return 0; }
  const p = (scrollY - contentTop) / scrollable;
  return Math.min(1, Math.max(0, p));
}

/** 绑定当前 document 的进度条；导出供测试调用 */
export function initReadingProgress(doc) {
  const bar = doc.querySelector('.mf-progress');
  const content = doc.querySelector('.post-content');
  if (!bar || !content) { return; }
  const win = doc.defaultView;

  const update = () => {
    const rect = content.getBoundingClientRect();
    const scrollY = win.scrollY || win.pageYOffset || 0;
    const p = computeProgress({
      scrollY,
      viewportH: win.innerHeight,
      contentTop: rect.top + scrollY,
      contentH: rect.height,
    });
    bar.style.setProperty('--mf-progress', p.toFixed(3));
  };

  const raf = typeof win.requestAnimationFrame === 'function'
    ? (fn) => win.requestAnimationFrame(fn)
    : (fn) => win.setTimeout(fn, 16);
  let ticking = false;
  win.addEventListener('scroll', () => {
    if (ticking) { return; }
    ticking = true;
    raf(() => { update(); ticking = false; });
  }, { passive: true });
  win.addEventListener('resize', update, { passive: true });

  update();
}

/** import 时自动注册（浏览器与 jsdom 均以全局 document 为宿主） */
export function autoInit() {
  if (typeof document === 'undefined') { return; }
  initReadingProgress(document);
}

autoInit();

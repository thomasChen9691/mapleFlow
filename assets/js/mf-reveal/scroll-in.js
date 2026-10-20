/**
 * scroll-in.js —— 滚动进场引擎（reveal 协议·行为层）
 * ============================================================
 * 【`.reveal → is-in` 契约的定义处——工单 0022 决议②】
 * `.reveal` 的初始隐藏由 CSS 承担（.js .reveal { opacity:0 }），本引擎是
 * 唯一的「点亮」写入方；筛选引擎在用户交互后直写 is-in 属于同协议的
 * 终态捷径（见 filter.js 的 apply）。
 *
 * DOM 契约：
 *   读  `.reveal`（document 全量扫描；首页 hero 下方、精选区、产品行共用）
 *   写  is-in     进入视口后加，一次性（加完即 unobserve，不重播）
 *   降级  ① prefers-reduced-motion: reduce → 全量直写 is-in，不做动画
 *        ② 浏览器无 IntersectionObserver → 同上（内容不得因引擎缺席而消失）
 *   阈值  rootMargin `0px 0px -6% 0px`、threshold 0.06（观感参数，不属契约）
 *
 * 与 no-js 基线（ADR-0002）的关系：<html> 默认 .no-js，head 内联脚本换成 .js
 * 后 CSS 才隐藏初始态；本引擎只负责「点亮」。JS 加载失败时基线兜底，内容可见。
 *
 * 测试：tests/assert_reveal.mjs（RGR-7 三态）；生产经 app.js 入口由 extend_footer
 * 以 js.Build 引用。
 */

const REDUCED_QUERY = '(prefers-reduced-motion: reduce)';

/** 扫描并绑定当前 document 的全部 .reveal 元素；导出供测试调用 */
export function initScrollIn(doc) {
  const win = doc.defaultView;
  const els = doc.querySelectorAll('.reveal');
  if (!els.length) { return; }

  const reduce = !!(win.matchMedia && win.matchMedia(REDUCED_QUERY).matches);
  if (reduce || !('IntersectionObserver' in win)) {
    els.forEach((el) => el.classList.add('is-in'));
    return;
  }

  const io = new win.IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });

  els.forEach((el) => io.observe(el));
}

/** import 时自动注册（浏览器与 jsdom 均以全局 document 为宿主） */
export function autoInit() {
  if (typeof document === 'undefined') { return; }
  initScrollIn(document);
}

autoInit();

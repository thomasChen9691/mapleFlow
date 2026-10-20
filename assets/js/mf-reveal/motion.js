/**
 * motion.js —— 动效降级判定的单一来源（工单 0025 决议③）
 * ============================================================
 * 两个引擎共用同一判定：
 *   · scroll-in.js —— reduce 时不做 IO，全部直落 is-in 终态
 *   · filter.js    —— reduce 时照常过滤，但不播放 morph / bump
 *
 * 层次分工（不是重复实现）：
 *   · JS 层（本文件）：决定「是否播放动画」
 *   · CSS 层（assets/css/extended/custom.css 的
 *     @media (prefers-reduced-motion: reduce)）：兜底「定格最终画面」——
 *     JS 加载失败时仍然生效（ADR-0002 基线不破）。
 *   两层各自独立，语义一致；改判定语义只改本文件 + CSS 媒体查询两处。
 *
 * 契约：matchMedia 不可用时按「不减弱」处理（守卫路径，非悲观禁用）。
 */
const REDUCED_QUERY = '(prefers-reduced-motion: reduce)';

export function prefersReducedMotion(win) {
  return !!(win.matchMedia && win.matchMedia(REDUCED_QUERY).matches);
}

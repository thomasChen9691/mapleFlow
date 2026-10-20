/**
 * filter.js —— 产品索引筛选引擎（reveal 协议·行为层）
 * ============================================================
 * 【筛选交互契约的定义处——工单 0022 决议②：协议层拥有 DOM 契约命名权】
 * （`.reveal → is-in` 的契约定义处在 scroll-in.js；两文件合起来是 reveal 协议。
 *   product-index 渲染 seam 是消费者，只负责产出符合本契约的 DOM。）
 *
 * 注册方式（工单 0022 决议③）：import 时自动扫描 `.mf-index` roots 并各自绑定，
 *   不依赖 uid —— uid 仍是渲染 seam 的 DOM id 契约（必填、兼深链锚），
 *   但不再是本引擎的注册键。同页多实例各管各的按钮与计数。
 *
 * DOM 契约（读 → 写）：
 *   读  root                    `.mf-index`（筛选区根，每实例一个）
 *       buttons                 `.mf-filter[data-group][data-value]`（kind 组：all/workflow/document/question-bank；price 组：all/free/paid）
 *                               词汇表归产品索引渲染链（ADR-0006），引擎不持有词表
 *       rows                    `.mf-rows > .mf-row[data-kind][data-price]`
 *       count                   `.mf-count[aria-live="polite"]`
 *       empty                   `.mf-empty`（无匹配条目时显隐）
 *   写  aria-pressed            组内互斥：当前值 pressed=true，同组其余 false；再点当前值回到 all
 *       is-hidden              不匹配行加、匹配行去（配合 CSS display:none）
 *       is-in                   用户交互后可见行直写终态（不依赖滚动进场点亮）
 *       --mf-i                  可见序 stagger 变量，第 9 条起截断为 8（长列表防迟钝）
 *       is-morphing / is-bump   一次性重播动画类（remove → reflow → add；morph 520ms 后由 timer 移除，bump 不设 timer）
 *       count.textContent       「显示 X / Y」；empty.hidden = (X > 0)
 * 降级  prefers-reduced-motion: reduce 时仍完整过滤，但不播放 morph / bump
 *        （判定来源：reduced-motion.js，两引擎共用；matchMedia 不可用时按「不减弱」处理）
 *
 * 测试：tests/assert_reveal.mjs（seam S1，工单 0022 决议④的 A 类行为项）。
 * 生产加载：经 assets/js/mf-reveal/app.js 入口由 extend_footer 以 js.Build 引用；
 *   视觉参数（22ms stagger、520ms  timer、rootMargin 等）属 CSS/调值层，不在契约内。
 */

import { prefersReducedMotion } from './reduced-motion.js';

/** 把单个 root 绑定为独立筛选实例；导出供测试逐 root 调用 */
export function initFilter(root) {
  const win = root.ownerDocument.defaultView;
  const rows = root.querySelectorAll('.mf-row');
  const count = root.querySelector('.mf-count');
  const state = { kind: 'all', price: 'all' };

  let morphTimer;

  /* 重播一次性动画：移除 class → 强制回流 → 重新加上。
     少了中间的 reflow，浏览器会合并成一次样式变更，动画不会重播。 */
  function replay(el, cls, ms) {
    if (!el) { return; }
    el.classList.remove(cls);
    void el.offsetWidth;
    el.classList.add(cls);
    if (ms) {
      win.clearTimeout(morphTimer);
      morphTimer = win.setTimeout(() => { el.classList.remove(cls); }, ms);
    }
  }

  function apply(animate) {
    let shown = 0;
    rows.forEach((el) => {
      const okKind = state.kind === 'all' || el.dataset.kind === state.kind;
      const okPrice = state.price === 'all' || el.dataset.price === state.price;
      const visible = okKind && okPrice;
      el.classList.toggle('is-hidden', !visible);
      if (visible) {
        /* 小分组 stagger：第 9 条起不再累加延迟，长列表会显得迟钝 */
        el.style.setProperty('--mf-i', Math.min(shown, 8));
        /* 用户已交互过 —— 直接把条目落到终态（否则未进入过视口的条目仍带
           .reveal(opacity:0)，动画结束会重新变回透明，像"筛完又消失了"） */
        if (animate) { el.classList.add('is-in'); }
        shown++;
      }
    });
    if (count) { count.textContent = `显示 ${shown} / ${rows.length}`; }
    const empty = root.querySelector('.mf-empty');
    if (empty) { empty.hidden = shown > 0; }

    /* 只在用户点筛选时播放；首屏那次（animate=false）保持静止，
       否则会和 .reveal 的滚动进场撞在一起 */
    if (!animate || prefersReducedMotion(win)) { return; }
    replay(root.querySelector('.mf-rows'), 'is-morphing', 520);
    replay(count, 'is-bump', 0);
  }

  root.querySelectorAll('.mf-filter').forEach((btn) => {
    btn.addEventListener('click', () => {
      const group = btn.dataset.group;
      const value = btn.dataset.value;
      state[group] = state[group] === value ? 'all' : value;
      root.querySelectorAll(`.mf-filter[data-group="${group}"]`).forEach((other) => {
        other.setAttribute('aria-pressed', other.dataset.value === state[group] ? 'true' : 'false');
      });
      apply(true);
    });
  });

  apply(false);
}

/** import 时自动注册（浏览器与 jsdom 均以全局 document 为宿主） */
export function autoInit() {
  if (typeof document === 'undefined') { return; }
  document.querySelectorAll('.mf-index').forEach(initFilter);
}

autoInit();

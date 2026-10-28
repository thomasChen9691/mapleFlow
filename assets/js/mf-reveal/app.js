/**
 * app.js —— reveal 协议引擎入口（js.Build 打包点）
 * ============================================================
 * 【注册缝的唯一位置——工单 0083 决议（ADR 待 0088 收口落档）】
 * 三个引擎都**不再 import 自注册**（历史实现是各引擎尾部 `autoInit()`），
 * 挂载全部由本文件显式发起。这样「谁挂了谁」只有一处可读，引擎本身
 * 变成可单独 import 的纯模块（Node / jsdom 直接测，不需要副作用）。
 *
 *   · scroll-in.js        —— .reveal → is-in 滚动进场（IO 写入方）
 *   · filter.js           —— 产品索引筛选（.mf-index roots 自动注册）
 *   · reading-progress.js —— 阅读进度条（--mf-progress 写入方）
 *
 * 顺序与隔离（0083 决议）：
 *   · **顺序无关**——三个引擎互不依赖，下面数组的顺序不是契约；
 *   · **逐个隔离**——每个挂载各自 try/catch，单个失败只 console.error，
 *     不连带其余。理由 ADR-0002：scroll-in 不跑时 .reveal 停在 opacity:0
 *     （内容消失），不能让一个筛选 bug 把阅读进度条一起带走。
 *   · scroll-in 自身的 fail-open 归它自己（引擎内兜底），本文件不兜内容。
 *
 * 挂点发现权归引擎（0083 决议）：选择器（.reveal / .mf-index / .mf-progress）
 * 与契约 docstring 同文件，本文件只调用，不持有选择器。
 *
 * 生产由 layouts/partials/extend_footer.html 以 js.Build 引用本入口；
 * DOM 契约定义处 = 各引擎文件头 docstring。
 */
import { initScrollIn } from './scroll-in.js';
import { mountFilter } from './filter.js';
import { initReadingProgress } from './reading-progress.js';

const ENGINES = [
  ['scroll-in', initScrollIn],
  ['filter', mountFilter],
  ['reading-progress', initReadingProgress],
];

for (const [name, mount] of ENGINES) {
  try {
    mount(document);
  } catch (err) {
    console.error(`[mf-reveal] ${name} 挂载失败`, err);
  }
}

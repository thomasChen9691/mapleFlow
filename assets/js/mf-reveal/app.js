/**
 * app.js —— reveal 协议引擎入口（js.Build 打包点，工单 0022 决议①）
 * ============================================================
 * 两个引擎互不依赖，import 顺序无关；各自 import 时自动注册：
 *   · scroll-in.js —— .reveal → is-in 滚动进场（IO 写入方）
 *   · filter.js    —— 产品索引筛选（.mf-index roots 自动注册）
 * 生产由 layouts/partials/extend_footer.html 以 js.Build 引用本入口；
 * DOM 契约定义处 = 各引擎文件头 docstring。
 */
import './scroll-in.js';
import './filter.js';

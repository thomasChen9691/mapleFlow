/**
 * mf-search-overlay.js —— 搜索前端的 js.Build 入口（ADR-0013 决策 3）
 * ============================================================
 * 只做装配，不承载行为：
 *   · import '@params'（Hugo 构建期注入：searchUrl = search 页 RelPermalink、
 *     indexUrl = index.json 的 relLangURL，两者都自动带 /mapleFlow/ 生产子路径）
 *   · 装配浮层引擎（initSearchOverlay）——成功则把它的 open 作为入口引擎的
 *     env.openSearch 钩子（`/` 开浮层）；失败（挂点缺失 / indexUrl 缺失）则
 *     不传钩子，入口回落 searchUrl 跳转（ADR-0013 决策 4 的兜底）。
 *
 * 行为与契约定义处：mf-search-overlay-engine.js（浮层）/ mf-search-entry-engine.js
 * （快捷键）两个文件头 docstring——本文件不被测试导入（@params 仅 Hugo 可解析，
 * 这正是「入口/引擎裂为两文件」的原因：引擎零 Hugo 依赖、可被 Node 直接导入）。
 *
 * 加载（extend_footer 的第二个 js.Build）：与 fuse.basic.min.js + license.js
 * concat 后 fingerprint——fuse 在 bundle 前段，浮层代码运行时 Fuse 已定义
 * （与 head.html 给 search 页的 search.js 同款管线；区别是那件只 concat 经典
 * 脚本，本件先 js.Build 再 concat）。
 */
import * as params from '@params';
import { registerSearchEntry } from './mf-search-entry-engine.js';
import { initSearchOverlay } from './mf-search-overlay-engine.js';

const overlay = initSearchOverlay(document, window, {
    indexUrl: params.indexUrl,
});

registerSearchEntry(params, {
    document,
    location: window.location,
    openSearch: overlay ? overlay.open : undefined,
});

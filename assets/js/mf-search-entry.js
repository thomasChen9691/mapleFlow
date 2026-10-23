/**
 * mf-search-entry.js —— 搜索入口引擎的 js.Build 入口（候选 12 工单 0050 决议⑤⑥）
 * ============================================================
 * 只做装配，不承载行为：导入 Hugo 构建期注入的 params（@params 虚拟模块，
 * 值 = search 页 RelPermalink，自动带 /mapleFlow/ 生产子路径）与纯引擎，
 * 以真实全局 { document, location } 注册。
 * 行为与 DOM/键盘契约的定义处 = mf-search-entry-engine.js 文件头 docstring；
 * 本文件不被测试导入（@params 仅 Hugo 可解析——这正是入口/引擎裂为两文件的
 * 原因：引擎保持零 Hugo 依赖、可被 Node 直接导入，工单 0050 决议⑤「单文件」
 * 的 seam 意图由「入口名不变 + 引擎拆出」承接）。
 */
import * as params from '@params';
import { registerSearchEntry } from './mf-search-entry-engine.js';

registerSearchEntry(params, { document, location });

/**
 * mf-search-entry-engine.js —— 搜索入口引擎（候选 12 工单 0050 决议 + ADR-0013
 * 决策 4 升级；纯函数 seam）
 * ============================================================
 * 职责：全站 `/` 快捷键——把「从任意页面发起搜索」压缩为 1 步。
 *
 * **2026-10-24 ADR-0013 决策 4（supersede 工单 0050 决议③的「轻形态只跳转」）**：
 * 按键的动作为「开浮层」而非「跳转 search 页」——浮层装配成功时 env.openSearch
 * 有值（由 bundle 入口注入 mf-search-overlay-engine 的 open）；无钩子（浮层
 * 没装配 / params 缺失）才回落 searchUrl 跳转，原轻形态降级为兜底。
 * 重评全文：docs/adr/0013-search-overlay.md。
 *
 * DOM / 键盘契约（本 docstring 是唯一定义处；与 themes/maplemod/assets/js/
 *   fastsearch.js 文件头「搜索协议」快照契约、mf-search-overlay-engine.js
 *   浮层契约三者并列互指、不合并——本引擎只决定「何时打开」，打开什么由
 *   调用方给；检索（search 页）归快照协议、就地检索归浮层协议）：
 *   · 键位 `/`：无修饰键。按着 Ctrl / Meta / Alt 时不拦截（让位浏览器快捷键）。
 *   · 焦点门控：焦点在 input / textarea / select / contenteditable 时不拦截
 *     （`/` 是合法输入字符；search 页搜索框内输入即靠此放行）。
 *   · 非 search 页：preventDefault 后调 env.openSearch()（有钩子）或跳转
 *     params.searchUrl（无钩子兜底）。
 *   · 当前即 search 页：不跳转不刷新，聚焦 #searchInput（search 页打开时
 *     已有原生 autofocus，此处覆盖「已在页内但焦点丢失」的情形；与另一分支
 *     同样 preventDefault——避免 / 触发浏览器页内查找）。
 *   · 降级：searchUrl 缺失或非字符串 → 静默不注册监听——菜单「搜索」链接
 *     即入口（ADR-0002 no-js 基线：无内容被隐藏，只是增强；脚本不加载 /
 *     参数缺失时菜单照常工作）。
 *
 * 加载（工单 0050 决议⑤ + ADR-0013 决策 3）：站点层本文件 + bundle 入口
 * mf-search-overlay.js，经主题 extend_footer 的 js.Build（iife + minify +
 * fingerprint + defer）全站恒加载——与 mf-reveal 同款管线；两层不得有同
 * 相对路径文件（ADR-0008）。
 *
 * 测试（工单 0050 决议⑧ + ADR-0013 决策 9）：tests/assert_search.mjs 导入本
 * 文件直接测（纯函数 + env 注入，零 Hugo 依赖）；产物面（构件引用 / 加载面 /
 * URL 子路径 / 菜单文案 / 浮层 DOM 与 parity）由 tests/assert_site_contracts.py 守。
 */
export function registerSearchEntry(config, env) {
    const searchUrl = config && typeof config.searchUrl === 'string' ? config.searchUrl : '';
    if (!searchUrl) return;
    const searchPath = new URL(searchUrl, env.location.href).pathname;
    const openSearch = env.openSearch;
    env.document.addEventListener('keydown', (e) => {
        if (e.key !== '/') return;
        if (e.ctrlKey || e.metaKey || e.altKey) return;
        const t = e.target;
        if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA'
            || t.tagName === 'SELECT' || t.isContentEditable)) return;
        e.preventDefault();
        if (env.location.pathname === searchPath) {
            const input = env.document.getElementById('searchInput');
            if (input) input.focus();
            return;
        }
        if (typeof openSearch === 'function') { openSearch(); return; }
        env.location.href = searchUrl;
    });
}

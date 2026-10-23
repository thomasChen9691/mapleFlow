/**
 * mf-search-entry-engine.js —— 搜索入口引擎（候选 12 工单 0050 决议，纯函数 seam）
 * ============================================================
 * 职责：全站 `/` 快捷键——把「从任意页面发起搜索」从 2 步（菜单 → search 页）
 * 压缩为 1 步。轻形态（工单 0050 决议③）：按键只负责跳转 / 聚焦，检索仍在
 * search 页（fastsearch 的领地）——本引擎与 fastsearch、index.json 零耦合，
 * 故不构成 ADR-0010 的「第二个消费方」，不触发重评（决议⑦）。
 *
 * DOM / 键盘契约（本 docstring 是唯一定义处，与 fastsearch.js 快照契约并列互指）：
 *   · 键位 `/`：无修饰键。按着 Ctrl / Meta / Alt 时不拦截（让位浏览器快捷键）。
 *   · 焦点门控：焦点在 input / textarea / select / contenteditable 时不拦截
 *     （`/` 是合法输入字符；search 页搜索框内输入即靠此放行）。
 *   · 非 search 页：preventDefault 后跳转 params.searchUrl（Hugo 构建期经
 *     js.Build params 注入，入口文件 mf-search-entry.js 负责 import '@params'）。
 *   · 当前即 search 页：不跳转不刷新，聚焦 #searchInput（search 页打开时
 *     已有原生 autofocus，此处覆盖「已在页内但焦点丢失」的情形；与跳转分支
 *     同样 preventDefault——避免 / 触发浏览器页内查找）。
 *   · 降级：searchUrl 缺失或非字符串 → 静默不注册监听——菜单「搜索」链接
 *     即入口（ADR-0002 no-js 基线：无内容被隐藏，只是增强；脚本不加载 /
 *     参数缺失时菜单照常工作）。
 *
 * 加载（工单 0050 决议⑤）：站点层本文件 + 入口 mf-search-entry.js，经主题
 * extend_footer 的第二个 js.Build（iife + minify + fingerprint + defer）
 * 全站恒加载——与 mf-reveal 同款管线；两层不得有同相对路径文件（ADR-0008）。
 *
 * 测试（工单 0050 决议⑧）：tests/assert_search.mjs 导入本文件直接测
 * （纯函数 + env 注入，零 Hugo 依赖）；产物面（构件引用 / 加载面 / URL 子
 * 路径 / 菜单文案）由 tests/assert_site_contracts.py 守。
 */
export function registerSearchEntry(config, env) {
    const searchUrl = config && typeof config.searchUrl === 'string' ? config.searchUrl : '';
    if (!searchUrl) return;
    const searchPath = new URL(searchUrl, env.location.href).pathname;
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
        env.location.href = searchUrl;
    });
}

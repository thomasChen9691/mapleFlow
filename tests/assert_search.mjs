/**
 * 搜索入口·行为断言（候选 12 工单 0050 决议⑧：新引擎与新契约一起出生）
 * ============================================================
 * 被测对象：assets/js/mf-search-entry-engine.js 的导出函数
 *   registerSearchEntry(params, env) —— 纯函数 seam：
 *     · params.searchUrl 由 Hugo 构建期经 js.Build params（@params）注入，
 *       在入口文件 mf-search-entry.js 里导入后传入；本引擎零 Hugo 依赖，
 *       故可被 Node 直接导入测试（reveal 同款纪律：只测源码，不经构建）。
 *     · env = { document, location } —— 测试传 jsdom 样本与 location 桩，
 *       生产由入口文件传真实全局。
 * 断言方式：每个行为一个用例——装样本 DOM → 调 register → 派发键盘事件 →
 *   断言可观测效果（location.href 跳转 / 焦点落点 / 事件是否被 prevent）。
 *
 * 契约定义处 = mf-search-entry-engine.js 文件头 docstring（工单 0050 决议⑤：
 * 新文件自有 docstring，与 fastsearch.js 快照契约并列互指、不合并）。
 * 与 ADR-0010 决策 5 的关系：该决议否决的是「为 fastsearch 遗留快照立 jsdom
 * 套件」；本套件测的是按 ADR-0007 纪律「与新契约一起出生」的新引擎。
 *
 * 跑法：npm test（package.json 串联 assert_reveal.mjs + 本文件）
 */
import { JSDOM } from 'jsdom';
import { pathToFileURL, fileURLToPath } from 'node:url';
import path from 'node:path';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ENGINE = path.join(REPO, 'assets/js/mf-search-entry-engine.js');
const SEARCH_URL = '/mapleFlow/search.html'; // 独立字面量：生产子路径形态（config.production.toml 的 baseURL）
const ARTICLE_HREF = 'http://localhost/posts/foo.html';

let passed = 0;
let failed = 0;

function check(name, cond, detail) {
    if (cond) {
        passed++;
        console.log(`  ok  ${name}`);
    } else {
        failed++;
        console.log(`FAIL  ${name}${detail ? `\n      ${detail}` : ''}`);
    }
}

/** 装一个样本页面：非 search 页（文章页），无表单焦点 */
function installArticlePage() {
    const dom = new JSDOM('<!DOCTYPE html><html><body><article><p>正文</p></article></body></html>',
        { url: 'http://localhost/posts/foo.html' });
    return {
        document: dom.window.document,
        location: { href: ARTICLE_HREF, pathname: '/posts/foo.html' },
    };
}

/** 派发一次 `/` keydown；返回事件对象（供 defaultPrevented 断言） */
function pressSlash(env, opts = {}) {
    const { KeyboardEvent } = env.document.defaultView;
    const ev = new KeyboardEvent('keydown', Object.assign({ key: '/', bubbles: true, cancelable: true }, opts));
    (opts.on || env.document).dispatchEvent(ev);
    return ev;
}

const { registerSearchEntry } = await import(pathToFileURL(ENGINE).href);

// ---- 行为 1：非 search 页按 `/` → 跳转注入的 searchUrl（工单 0050 决议③轻形态）
{
    const env = installArticlePage();
    registerSearchEntry({ searchUrl: SEARCH_URL }, env);
    pressSlash(env);
    check('非 search 页按 / 跳转注入的 searchUrl',
        env.location.href === SEARCH_URL, `got href=${env.location.href}`);
}

// ---- 行为 2：焦点在表单元素时按 `/` 不拦截（`/` 是合法输入字符；决议④门控）
{
    const dom = new JSDOM('<!DOCTYPE html><html><body><input id="q" type="text"></body></html>',
        { url: 'http://localhost/posts/foo.html' });
    const env = {
        document: dom.window.document,
        location: { href: ARTICLE_HREF, pathname: '/posts/foo.html' },
    };
    registerSearchEntry({ searchUrl: SEARCH_URL }, env);
    const ev = pressSlash(env, { on: env.document.getElementById('q') });
    check('焦点在 input 按 / 不跳转',
        env.location.href === ARTICLE_HREF, `got href=${env.location.href}`);
    check('焦点在 input 按 / 不 preventDefault（放行输入）',
        ev.defaultPrevented === false, 'event was prevented');
}

// ---- 行为 3：按着 Ctrl/Meta/Alt 时按 `/` 不拦截（让位浏览器与系统快捷键；决议④门控）
{
    const env = installArticlePage();
    registerSearchEntry({ searchUrl: SEARCH_URL }, env);
    const cases = [
        ['Ctrl', { ctrlKey: true }],
        ['Meta', { metaKey: true }],
        ['Alt', { altKey: true }],
    ];
    let allPass = true;
    for (const [label, opts] of cases) {
        const ev = pressSlash(env, opts);
        const ok = env.location.href === ARTICLE_HREF && !ev.defaultPrevented;
        if (!ok) allPass = false;
        check(`${label} + / 不跳转不拦截`, ok, `href=${env.location.href}, prevented=${ev.defaultPrevented}`);
    }
    check('三种修饰键组合全部放行', allPass);
}

// ---- 行为 4：当前即 search 页时按 `/` 只聚焦 #searchInput，不跳转不刷新（决议③附带细节）
{
    const dom = new JSDOM('<!DOCTYPE html><html><body><div id="searchbox">'
        + '<input id="searchInput" type="search"></div><ul id="searchResults"></ul></body></html>',
        { url: 'http://localhost/mapleFlow/search.html' });
    const env = {
        document: dom.window.document,
        location: { href: 'http://localhost/mapleFlow/search.html', pathname: '/mapleFlow/search.html' },
    };
    registerSearchEntry({ searchUrl: SEARCH_URL }, env);
    const ev = pressSlash(env);
    const input = env.document.getElementById('searchInput');
    check('search 页按 / 不跳转（href 不变）',
        env.location.href === 'http://localhost/mapleFlow/search.html', `got href=${env.location.href}`);
    check('search 页按 / 聚焦 #searchInput', env.document.activeElement === input,
        `activeElement=${env.document.activeElement && env.document.activeElement.id}`);
    check('search 页按 / 仍 preventDefault（不让 / 触发页内查找）', ev.defaultPrevented === true,
        'event not prevented');
}

// ---- 行为 5：searchUrl 缺失 / 为空 / 非字符串 → 静默不注册（决议⑥降级：
//      菜单「搜索」链接兜底，绝不猜 URL；fixture 无 search 页时同走此路径）
{
    const cases = [
        ['缺失', {}],
        ['空串', { searchUrl: '' }],
        ['非字符串', { searchUrl: 42 }],
    ];
    for (const [label, config] of cases) {
        const env = installArticlePage();
        registerSearchEntry(config, env);
        const ev = pressSlash(env);
        check(`searchUrl ${label} → 按 / 无动作（静默降级）`,
            env.location.href === ARTICLE_HREF && !ev.defaultPrevented,
            `href=${env.location.href}, prevented=${ev.defaultPrevented}`);
    }
}

console.log(`\n${passed}/${passed + failed} passed`);
if (failed) {
    console.log('RED — %d 个行为未满足', failed);
    process.exit(1);
}

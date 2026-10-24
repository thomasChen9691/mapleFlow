/**
 * 搜索入口·行为断言（候选 12 工单 0050 决议⑧：新引擎与新契约一起出生）
 * ============================================================
 * 被测对象（两个站点层引擎；2026-10-24 ADR-0013 起合称「搜索前端」）：
 *   assets/js/mf-search-entry-engine.js
 *     registerSearchEntry(params, env) —— 快捷键入口纯函数 seam：
 *     · params.searchUrl 由 Hugo 构建期经 js.Build params（@params）注入，
 *       在装配入口 mf-search-overlay.js 里导入后传入；本引擎零 Hugo 依赖，
 *       故可被 Node 直接导入测试（reveal 同款纪律：只测源码，不经构建）。
 *     · env = { document, location, openSearch? } —— 测试传 jsdom 样本与
 *       location 桩；openSearch 是浮层装配成功时的钩子（ADR-0013 决策 4：
 *       有钩子开浮层、无钩子回落 searchUrl 跳转）。
 *   assets/js/mf-search-overlay-engine.js
 *     initSearchOverlay(doc, win, config) —— 浮层引擎纯函数 seam（ADR-0013
 *     决策 3）：config 注入 indexUrl / fetchImpl / fuseFactory / navigate，
 *     返回 { open, close, isOpen } 或 null（挂点缺失即降级）。
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

// ---- 行为 1：非 search 页按 `/` → 有 openSearch 钩子时开浮层、不跳转
//      （ADR-0013 决策 4：浮层装配成功时快捷键的就地形态）
{
    const env = installArticlePage();
    let opened = 0;
    env.openSearch = () => { opened += 1; };
    registerSearchEntry({ searchUrl: SEARCH_URL }, env);
    const ev = pressSlash(env);
    check('非 search 页按 / 调 openSearch 钩子（不跳转）',
        opened === 1 && env.location.href === ARTICLE_HREF && ev.defaultPrevented,
        `got opened=${opened} href=${env.location.href} prevented=${ev.defaultPrevented}`);
}

// ---- 行为 1b：无 openSearch 钩子 → 回落跳转 searchUrl（原轻形态降级为兜底）
{
    const env = installArticlePage();
    registerSearchEntry({ searchUrl: SEARCH_URL }, env);
    pressSlash(env);
    check('无浮层钩子时按 / 仍跳转 searchUrl（兜底不破）',
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

// ============================================================
// 浮层引擎（ADR-0013）：initSearchOverlay(doc, win, config)
// 样本 DOM 镜像 themes/maplemod/layouts/partials/search-overlay.html 的契约
// ============================================================
const OVERLAY_ENGINE = path.join(REPO, 'assets/js/mf-search-overlay-engine.js');
const INDEX_URL = '/mapleFlow/index.json';

/** 镜像主题 partial 的 DOM 契约（引擎 docstring 是唯一定义处，此处是样本） */
function overlaySample() {
    return `<!DOCTYPE html><html><body>
<a class="mf-search-link" href="${SEARCH_URL}" aria-label="搜索">icon</a>
<div class="mf-search-overlay" id="mfSearchOverlay" role="dialog" aria-modal="true" aria-label="搜索" hidden>
  <div class="mf-search-backdrop"></div>
  <div class="mf-search-panel">
    <div class="mf-search-box">
      <input id="mfSearchInput" type="search" maxlength="64" aria-label="搜索" autocomplete="off">
      <button type="button" class="mf-search-close" aria-label="关闭搜索">×</button>
    </div>
    <ul class="mf-search-results" id="mfSearchResults" aria-label="搜索结果"></ul>
    <p class="mf-search-empty" hidden>没有匹配的结果</p>
    <p class="mf-search-error" hidden>索引加载失败</p>
  </div>
</div></body></html>`;
}

/** 装浮层样本；fetchImpl / fuseFactory / navigate 全部可注入 */
function installOverlay({ records, fetchFails = false, fuseImpl } = {}) {
    const dom = new JSDOM(overlaySample(), { url: 'http://localhost/posts/foo.html' });
    const doc = dom.window.document;
    let fetchCalls = 0;
    const fetchImpl = async () => {
        fetchCalls += 1;
        if (fetchFails) { throw new Error('network down'); }
        return { ok: true, json: async () => records };
    };
    const fuseCalls = [];
    const fuseFactory = (items, options) => {
        fuseCalls.push({ items, options });
        return fuseImpl || { search: () => [] };
    };
    const navigated = [];
    return { dom, doc, fetchImpl, fuseFactory, fuseCalls, navigated, fetchCount: () => fetchCalls };
}

/** 触发一次输入（设值 + input 事件；异步检索让出微任务） */
async function typeQuery(doc, value) {
    const input = doc.getElementById('mfSearchInput');
    input.value = value;
    input.dispatchEvent(new doc.defaultView.Event('input', { bubbles: true }));
    await new Promise((r) => setTimeout(r, 0));
}

{
    const { initSearchOverlay } = await import(pathToFileURL(OVERLAY_ENGINE).href);

    // 挂点缺失 → null 降级
    const bare = new JSDOM('<!DOCTYPE html><html><body><p>no overlay here</p></body></html>',
        { url: 'http://localhost/' });
    check('MFO-1 缺挂点时 init 返回 null（静默降级）',
        initSearchOverlay(bare.window.document, bare.window, { indexUrl: INDEX_URL }) === null);

    // indexUrl 缺失 → null（params 降级：图标回落链接）
    const noUrl = installOverlay({ records: [] });
    check('MFO-2 indexUrl 缺失时 init 返回 null',
        initSearchOverlay(noUrl.doc, noUrl.dom.window, {}) === null);

    // 开 / 关：hidden、焦点、body 锁
    const o = installOverlay({ records: [] });
    const overlay = initSearchOverlay(o.doc, o.dom.window, {
        indexUrl: INDEX_URL, fetchImpl: o.fetchImpl, fuseFactory: o.fuseFactory,
        navigate: (u) => o.navigated.push(u),
    });
    const overlayEl = o.doc.getElementById('mfSearchOverlay');
    check('MFO-3 初始 hidden（无 JS 不可见，no-js 基线）', overlayEl.hasAttribute('hidden'));
    const link = o.doc.querySelector('.mf-search-link');
    link.focus();
    overlay.open();
    check('MFO-4 open：去 hidden + 输入框获焦 + body 滚动锁',
        !overlayEl.hasAttribute('hidden')
        && o.doc.activeElement === o.doc.getElementById('mfSearchInput')
        && o.doc.body.style.overflow === 'hidden');
    overlay.close();
    check('MFO-5 close：回 hidden + 焦点还焦触发器 + body 解锁',
        overlayEl.hasAttribute('hidden')
        && o.doc.activeElement === link
        && o.doc.body.style.overflow !== 'hidden');

    // 图标点击：preventDefault + 打开（no-js 时它是普通链接）
    const c = installOverlay({ records: [] });
    initSearchOverlay(c.doc, c.dom.window, {
        indexUrl: INDEX_URL, fetchImpl: c.fetchImpl, fuseFactory: c.fuseFactory, navigate: () => {},
    });
    const ev = new c.dom.window.MouseEvent('click', { bubbles: true, cancelable: true });
    c.doc.querySelector('.mf-search-link').dispatchEvent(ev);
    check('MFO-6 点击图标 preventDefault 并打开浮层',
        ev.defaultPrevented && !c.doc.getElementById('mfSearchOverlay').hasAttribute('hidden'));

    // 三路关闭：Esc / backdrop / 关闭按钮
    for (const [name, act] of [
        ['Esc', (doc, win) => doc.dispatchEvent(new win.KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }))],
        ['backdrop', (doc) => doc.querySelector('.mf-search-backdrop').dispatchEvent(new doc.defaultView.MouseEvent('click', { bubbles: true, cancelable: true }))],
        ['关闭按钮', (doc) => doc.querySelector('.mf-search-close').dispatchEvent(new doc.defaultView.MouseEvent('click', { bubbles: true, cancelable: true }))],
        ['选中结果', (doc) => {
            const ul = doc.getElementById('mfSearchResults');
            ul.innerHTML = '<li class="mf-search-item"><a href="/x/">t</a></li>';
            ul.querySelector('a').dispatchEvent(new doc.defaultView.MouseEvent('click', { bubbles: true, cancelable: true }));
        }],
    ]) {
        const x = installOverlay({ records: [] });
        initSearchOverlay(x.doc, x.dom.window, {
            indexUrl: INDEX_URL, fetchImpl: x.fetchImpl, fuseFactory: x.fuseFactory, navigate: () => {},
        }).open();
        act(x.doc, x.dom.window);
        check(`MFO-7 ${name} 关闭浮层`, x.doc.getElementById('mfSearchOverlay').hasAttribute('hidden'));
    }

    // 检索：懒 fetch（仅一次）→ fuse 配置 parity 字面量 → 渲染结果
    const r = installOverlay({
        records: [{ title: 'T1', permalink: '/p1/', summary: 'S1', content: 'C1' }],
        fuseImpl: { search: () => [{ item: { title: '命中标题', permalink: '/hit/', summary: '命中摘要' } }] },
    });
    initSearchOverlay(r.doc, r.dom.window, {
        indexUrl: INDEX_URL, fetchImpl: r.fetchImpl, fuseFactory: r.fuseFactory,
        navigate: (u) => r.navigated.push(u),
    }).open();
    check('MFO-8 打开时不预拉索引（懒加载）', r.fetchCount() === 0);
    await typeQuery(r.doc, 'docker');
    check('MFO-9 首次输入才 fetch 索引，且只 fetch 一次',
        r.fetchCount() === 1, `got ${r.fetchCount()}`);
    const opts = r.fuseCalls[0] && r.fuseCalls[0].options;
    check('MFO-10 fuse 配置与快照逐字一致（keys/distance/threshold/ignoreLocation）',
        !!opts && JSON.stringify(opts.keys) === JSON.stringify(['title', 'permalink', 'summary', 'content'])
        && opts.distance === 100 && opts.threshold === 0.4 && opts.ignoreLocation === true,
        `got ${JSON.stringify(opts)}`);
    await typeQuery(r.doc, 'docker2');
    check('MFO-11 索引缓存：第二次输入不再 fetch', r.fetchCount() === 1);
    const items = r.doc.querySelectorAll('#mfSearchResults li');
    const first = items[0];
    check('MFO-12 结果渲染：li + 标题 + 摘要 + 链接（契约结构）',
        items.length === 1 && first.querySelector('a').getAttribute('href') === '/hit/'
        && first.textContent.includes('命中标题') && first.textContent.includes('命中摘要'),
        `got ${r.doc.getElementById('mfSearchResults').innerHTML.slice(0, 120)}`);

    // 空态 / 错误态
    const e = installOverlay({ records: [], fuseImpl: { search: () => [] } });
    initSearchOverlay(e.doc, e.dom.window, {
        indexUrl: INDEX_URL, fetchImpl: e.fetchImpl, fuseFactory: e.fuseFactory, navigate: () => {},
    }).open();
    await typeQuery(e.doc, 'nothing');
    check('MFO-13 空结果显示空态文案',
        !e.doc.querySelector('.mf-search-empty').hasAttribute('hidden')
        && e.doc.querySelectorAll('#mfSearchResults li').length === 0);

    // 拉取失败：错误态可见、**空态保持隐藏**（两句同时出现会误导——换词修不了网络）
    const f = installOverlay({ fetchFails: true });
    initSearchOverlay(f.doc, f.dom.window, {
        indexUrl: INDEX_URL, fetchImpl: f.fetchImpl, fuseFactory: f.fuseFactory, navigate: () => {},
    }).open();
    await typeQuery(f.doc, 'docker');
    check('MFO-14 索引拉取失败：错误态可见且空态隐藏（互斥）',
        !f.doc.querySelector('.mf-search-error').hasAttribute('hidden')
        && f.doc.querySelector('.mf-search-empty').hasAttribute('hidden')
        && f.doc.querySelectorAll('#mfSearchResults li').length === 0);

    // 非 ok 响应同样走错误态
    const nok = installOverlay({});
    initSearchOverlay(nok.doc, nok.dom.window, {
        indexUrl: INDEX_URL,
        fetchImpl: async () => ({ ok: false, json: async () => [] }),
        fuseFactory: nok.fuseFactory, navigate: () => {},
    }).open();
    await typeQuery(nok.doc, 'docker');
    check('MFO-14b 索引响应非 ok 也显示错误态',
        !nok.doc.querySelector('.mf-search-error').hasAttribute('hidden'));

    // 非数组 JSON（索引损坏）同样走错误态
    const bad = installOverlay({});
    initSearchOverlay(bad.doc, bad.dom.window, {
        indexUrl: INDEX_URL,
        fetchImpl: async () => ({ ok: true, json: async () => ({ not: 'an array' }) }),
        fuseFactory: bad.fuseFactory, navigate: () => {},
    }).open();
    await typeQuery(bad.doc, 'docker');
    check('MFO-14c 索引损坏（非数组 JSON）也显示错误态',
        !bad.doc.querySelector('.mf-search-error').hasAttribute('hidden'));

    // Enter → 首条结果导航
    const n = installOverlay({
        records: [],
        fuseImpl: { search: () => [{ item: { title: 'A', permalink: '/first/', summary: 's' } }] },
    });
    initSearchOverlay(n.doc, n.dom.window, {
        indexUrl: INDEX_URL, fetchImpl: n.fetchImpl, fuseFactory: n.fuseFactory,
        navigate: (u) => n.navigated.push(u),
    }).open();
    await typeQuery(n.doc, 'a');
    n.doc.getElementById('mfSearchInput').dispatchEvent(
        new n.dom.window.KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true }));
    check('MFO-15 Enter 导航到首条结果', n.navigated.length === 1 && n.navigated[0] === '/first/',
        `got ${JSON.stringify(n.navigated)}`);

    // Tab 困排（aria-modal 的承诺）
    const tp = installOverlay({ records: [] });
    initSearchOverlay(tp.doc, tp.dom.window, {
        indexUrl: INDEX_URL, fetchImpl: tp.fetchImpl, fuseFactory: tp.fuseFactory, navigate: () => {},
    }).open();
    const focusables = () => [...tp.doc.querySelectorAll('.mf-search-panel button, .mf-search-panel input')];
    focusables().pop().focus();
    tp.doc.dispatchEvent(new tp.dom.window.KeyboardEvent('keydown', { key: 'Tab', bubbles: true, cancelable: true }));
    check('MFO-16 Tab 在面板内困排（末元素再 Tab 回首元素）',
        tp.doc.activeElement === focusables()[0],
        `got ${tp.doc.activeElement && (tp.doc.activeElement.id || tp.doc.activeElement.className)}`);
    // shift+Tab 反向：首元素再 shift+Tab 末元素
    focusables()[0].focus();
    tp.doc.dispatchEvent(new tp.dom.window.KeyboardEvent('keydown',
        { key: 'Tab', shiftKey: true, bubbles: true, cancelable: true }));
    check('MFO-16b shift+Tab 反向困排（首元素再 shift+Tab 末元素）',
        tp.doc.activeElement === focusables().pop(),
        `got ${tp.doc.activeElement && (tp.doc.activeElement.id || tp.doc.activeElement.className)}`);
}

console.log(`\n${passed}/${passed + failed} passed`);
if (failed) {
    console.log('RED — %d 个行为未满足', failed);
    process.exit(1);
}

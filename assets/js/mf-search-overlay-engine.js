/**
 * mf-search-overlay-engine.js —— 搜索浮层引擎（ADR-0013；纯函数 seam）
 * ============================================================
 * 【浮层交互契约的定义处。2026-10-24 ADR-0013 重评的落地：fastsearch 快照契约
 *   （ADR-0010 决策 4）保持不动、仍只在 search 页加载；本引擎是全站第二个
 *   搜索 JS 加载面、index.json 投影的第二个消费方——重评结论与设计见
 *   docs/adr/0013-search-overlay.md。】
 *
 * 与并列模块的关系（三协议并列互指、不合并命名，ADR-0010 决策 4 同款纪律）：
 *   · layouts/_default/index.json —— 投影契约（六字段冻结；本引擎消费同一投影，
 *     不新增字段；summary 200 即结果第二行）
 *   · themes/maplemod/assets/js/fastsearch.js —— search 页检索快照契约
 *     （本引擎的 fuse 配置与其逐字一致，由 assert_site_contracts.py 的
 *     parity 断言执法：两处配置同改，防静默分叉）
 *   · assets/js/mf-search-entry-engine.js —— `/` 快捷键入口（env.openSearch
 *     钩子由本引擎的 open 提供；无钩子时入口回落 searchUrl 跳转）
 *
 * DOM 契约（本 docstring 是唯一定义处；样本见 themes/maplemod/layouts/
 *   partials/search-overlay.html，行为测试 tests/assert_search.mjs 镜像）：
 *   读  .mf-search-link                触发器（header 的图标 <a href=search 页>；
 *                                       no-js 时它是普通链接——点击被 intercept
 *                                       只是增强，ADR-0002 基线不破）
 *       #mfSearchOverlay              浮层根（role=dialog aria-modal=true，
 *                                       默认 hidden——无 JS 不可见）
 *       #mfSearchInput                输入框（maxlength=64 / aria-label=搜索）
 *       #mfSearchResults              结果列表（ul；**init 必需挂点之一**）
 *       .mf-search-empty / .mf-search-error  空态 / 错误态（默认 hidden；
 *                                       两者互斥——错误态出现时空态必隐藏）
 *       .mf-search-backdrop / .mf-search-close  背景点击关闭 / 关闭按钮
 *   写  #mfSearchOverlay.hidden       false=开 / true=关（唯一显隐开关）
 *       #mfSearchResults.innerHTML    <li class="mf-search-item"><a href="{permalink}">
 *                                       <span class="mf-search-title">{title}</span>
 *                                       <span class="mf-search-summary">{summary}</span>
 *                                       </a></li>——整行可点（不像 fastsearch 的
 *                                       绝对定位热区；标题+摘要+链接三件套与
 *                                       search 页结果视觉语言一致）
 *       document.body.style.overflow  打开时 'hidden'（滚锁），关闭时还原
 *   键盘 Escape 关（浮层开时）；Enter 导航首条结果（有结果时）；
 *       Tab 在 .mf-search-panel 内困排（aria-modal 的承诺）。
 *
 * 检索契约（与快照逐字一致，parity 断言执法）：
 *   Fuse options：distance 100 / threshold 0.4 / ignoreLocation true；
 *   keys = [title, permalink, summary, content]（与投影六字段差集 {tags,
 *   categories} 不变）。调参 = 改两处代码 + 改契约 + 评审（ADR-0010 决策 4）。
 *   索引来源：fetch config.indexUrl（Hugo 构建期经 js.Build params 注入的
 *   index.json RelPermalink，自动带 /mapleFlow/ 子路径——不是 fastsearch 的
 *   同目录相对，本引擎全站加载、不能假设页面旁边有索引）。
 *
 * 容错 UX（ADR-0013 决策 6——快照的「XHR 失败仅 console.log」静默失效在新引擎
 *   不继承）：fetch 抛错 / 返回非 ok / JSON.parse 失败 → .mf-search-error 显示
 *   （可见错误态 + 引导去 search 页）；无结果 → .mf-search-empty 显示。
 *   懒加载：打开时不预拉，首次输入才 fetch，之后缓存（索引 17 条，一次拉取）。
 *
 * 降级：缺 #mfSearchOverlay / #mfSearchInput / .mf-search-link / indexUrl
 *   任一 → init 返回 null（调用方据此不装 openSearch 钩子，入口回落跳转）。
 *
 * 测试：tests/assert_search.mjs（MFO-1..16：降级 / 开关与焦点 / 三路关闭 /
 *   懒加载与 parity / 渲染结构 / 空态 / 错误态 / Enter / Tab 困排）。
 */

/**
 * 装配浮层。返回 { open, close, isOpen } 或 null（挂点缺失即降级）。
 *
 * @param doc  Document
 * @param win  Window（事件宿主；滚动位置与 location 的来源）
 * @param config { indexUrl, fetchImpl?, fuseFactory?, navigate? }
 *   fetchImpl  默认 win.fetch（测试注入桩）
 *   fuseFactory 默认 win.Fuse（测试注入桩；生产由 bundle concat 的 fuse 提供）
 *   navigate   默认 (url) => { win.location.href = url }（测试注入桩）
 */
export function initSearchOverlay(doc, win, config) {
    const indexUrl = config && typeof config.indexUrl === 'string' ? config.indexUrl : '';
    const overlay = doc.getElementById('mfSearchOverlay');
    const input = doc.getElementById('mfSearchInput');
    const results = doc.getElementById('mfSearchResults');
    const emptyHint = doc.querySelector('.mf-search-empty');
    const errorHint = doc.querySelector('.mf-search-error');
    const closeBtn = doc.querySelector('.mf-search-close');
    const backdrop = doc.querySelector('.mf-search-backdrop');
    const triggers = [...doc.querySelectorAll('.mf-search-link')];
    if (!indexUrl || !overlay || !input || !results || !triggers.length) { return null; }

    const fetchImpl = config.fetchImpl || ((...a) => win.fetch(...a));
    const fuseFactory = config.fuseFactory || ((...a) => new win.Fuse(...a));
    const navigate = config.navigate || ((url) => { win.location.href = url; });

    let opened = false;
    let index = null;        // 缓存：拉到的索引记录
    let loading = null;      // 进行中的拉取Promise（防并发重复拉）
    let lastFocus = null;    // 打开时的焦点（关闭时还焦）
    let prevOverflow = '';   // 打开前的 body overflow（关闭时还原）

    const setOpen = (next) => {
        opened = next;
        overlay.hidden = !next;
    };

    const lockScroll = () => {
        prevOverflow = doc.body.style.overflow;
        doc.body.style.overflow = 'hidden';
    };
    const unlockScroll = () => {
        doc.body.style.overflow = prevOverflow;
    };

    function open() {
        if (opened) { return; }
        lastFocus = doc.activeElement;
        setOpen(true);
        lockScroll();
        input.focus();
    }

    function close() {
        if (!opened) { return; }
        setOpen(false);
        unlockScroll();
        if (lastFocus && typeof lastFocus.focus === 'function') { lastFocus.focus(); }
    }

    // 索引：懒加载 + 缓存；失败/损坏走错误态（返回 null 表示本次不可用）
    async function loadIndex() {
        if (index) { return index; }
        if (loading) { return loading; }
        loading = (async () => {
            let records = null;
            try {
                const res = await fetchImpl(indexUrl);
                if (!res || res.ok !== true) { throw new Error('index not ok'); }
                records = await res.json();
                if (!Array.isArray(records)) { throw new Error('index not an array'); }
            } catch (err) {
                loading = null;
                throw err;
            }
            index = records;
            loading = null;
            return records;
        })();
        return loading;
    }

    function render(items) {
        results.innerHTML = '';
        if (!items.length) {
            if (emptyHint) { emptyHint.hidden = false; }
            return;
        }
        if (emptyHint) { emptyHint.hidden = true; }        const frag = doc.createDocumentFragment();
        for (const hit of items) {
            const it = hit && hit.item ? hit.item : hit;
            const li = doc.createElement('li');
            li.className = 'mf-search-item';
            const a = doc.createElement('a');
            a.href = it.permalink || '#';
            const title = doc.createElement('span');
            title.className = 'mf-search-title';
            title.textContent = it.title || '';
            const sum = doc.createElement('span');
            sum.className = 'mf-search-summary';
            sum.textContent = it.summary || '';
            a.append(title, sum);
            li.append(a);
            frag.append(li);
        }
        results.append(frag);
    }

    async function runSearch() {
        const q = input.value.trim();
        if (!q) {
            render([]);
            if (emptyHint) { emptyHint.hidden = true; }
            if (errorHint) { errorHint.hidden = true; }
            return;
        }
        let records;
        try {
            records = await loadIndex();
        } catch (err) {
            // 错误态与空态**互斥**：拉取失败时清结果但不显示「没有匹配」——
            // 换关键词修不了网络失败，两句同时出现会误导（2026-10-24 评审抓出）
            results.innerHTML = '';
            if (emptyHint) { emptyHint.hidden = true; }
            if (errorHint) { errorHint.hidden = false; }
            return;
        }
        if (errorHint) { errorHint.hidden = true; }
        const fuse = fuseFactory(records, {
            keys: ['title', 'permalink', 'summary', 'content'],
            distance: 100,
            threshold: 0.4,
            ignoreLocation: true,
        });
        render(fuse.search(q));
    }

    // ---- 事件绑定 ----
    for (const t of triggers) {
        t.addEventListener('click', (e) => { e.preventDefault(); open(); });
    }
    if (closeBtn) { closeBtn.addEventListener('click', close); }
    if (backdrop) { backdrop.addEventListener('click', close); }

    input.addEventListener('input', () => { runSearch(); });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const first = results.querySelector('li a');
            if (first) { e.preventDefault(); navigate(first.getAttribute('href')); close(); }
        }
    });

    doc.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && opened) { e.preventDefault(); close(); return; }
        // Tab 困排：aria-modal 承诺焦点不出面板
        if (e.key === 'Tab' && opened) {
            const panel = overlay.querySelector('.mf-search-panel');
            const items = [...panel.querySelectorAll('button, input, [href], [tabindex="0"]')]
                .filter((el) => !el.disabled);
            if (!items.length) { return; }
            const firstEl = items[0];
            const lastEl = items[items.length - 1];
            if (e.shiftKey && doc.activeElement === firstEl) {
                e.preventDefault(); lastEl.focus();
            } else if (!e.shiftKey && doc.activeElement === lastEl) {
                e.preventDefault(); firstEl.focus();
            }
        }
    });

    // 点击结果链接即关（导航由浏览器执行）
    results.addEventListener('click', (e) => {
        if (e.target.closest('a')) { close(); }
    });

    return {
        open,
        close,
    };
}

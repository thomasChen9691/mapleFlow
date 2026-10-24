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
 *       document.body.style           打开时 overflow:hidden + position:fixed +
 *                                       top:-<scrollY>px + left/right:0 +
 *                                       width:100%（**双机制滚锁**：overflow 挡
 *                                       桌面程序化滚动，position:fixed 挡 iOS
 *                                       Safari 的触摸滚动——单 overflow 在 iOS
 *                                       上拦不住背后页面，经典坑）；关闭时还原
 *                                       样式并 scrollTo 回原位置（先还原后滚动，
 *                                       顺序反了会看到页面跳顶再回来）
 *       背景节点 inert                支持 inert 的浏览器：打开时给 body 内
 *                                       除浮层外的所有子节点 setAttribute
 *                                       ('inert','')，关闭时移除（焦点与指针
 *                                       一起被浏览器挡住，比手写困排彻底）
 *   键盘 Escape 关（浮层开时）；Enter 导航首条结果（有结果时）；
 *       Tab 困排**仅兜底路径**：不支持 inert 的浏览器才在 doc keydown 里手写
 *       循环（支持 inert 时背景已钉住，两个机制不同时开——会抢两轮焦点）。
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
 * 测试：tests/assert_search.mjs（MFO-1..16+：降级 / 开关与焦点 / 三路关闭 /
 *   懒加载与 parity / 渲染结构 / 空态 / 错误态 / Enter / Tab 困排兜底 /
 *   iOS 双机制滚锁 / inert 分支——后者经 config.supportsInert 注入 true 走
 *   inert 路径，jsdom 无原生 inert、特性检测恒 false，不注入就测不到）。
 */

/**
 * 装配浮层。返回 { open, close, isOpen } 或 null（挂点缺失即降级）。
 *
 * @param doc  Document
 * @param win  Window（事件宿主；滚动位置与 location 的来源）
 * @param config { indexUrl, fetchImpl?, fuseFactory?, navigate?, supportsInert? }
 *   fetchImpl  默认 win.fetch（测试注入桩）
 *   fuseFactory 默认 win.Fuse（测试注入桩；生产由 bundle concat 的 fuse 提供）
 *   navigate   默认 (url) => { win.location.href = url }（测试注入桩）
 *   supportsInert 默认按 'inert' in HTMLElement.prototype 特性检测；测试可注入
 *     true 走 inert 分支（jsdom 无原生 inert，特性检测必为 false——不注入就
 *     测不到那条路径，故开此 seam）
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
    // inert 分支 vs 手写 Tab 困排兜底（见 docstring「背景钉住」条）
    const supportsInert = config && typeof config.supportsInert === 'boolean'
        ? config.supportsInert
        : (typeof HTMLElement !== 'undefined' && 'inert' in HTMLElement.prototype);

    let opened = false;
    let index = null;        // 缓存：拉到的索引记录
    let loading = null;      // 进行中的拉取Promise（防并发重复拉）
    let lastFocus = null;    // 打开时的焦点（关闭时还焦）
    let prevOverflow = '';   // 打开前的 body overflow（关闭时还原）
    let savedScrollY = 0;    // 打开时的滚动位置（关闭时还原）
    let inerted = [];        // 打开时被钉 inert 的背景节点（关闭时还原）

    const setOpen = (next) => {
        opened = next;
        overlay.hidden = !next;
    };

    /* 滚锁：两套机制叠加，各有各的战场——
       ① overflow:hidden：桌面端阻止程序化滚动（scrollTo 之类）；
       ② position:fixed + 负 top + width:100%：**iOS Safari 专用**。iOS 上
          overflow:hidden 拦不住背后页面的触摸滚动（经典坑），必须把 body 整体
          钉住并用负 top 抵消当前滚动位移，视觉上页面停在原处；关闭时先还原
          样式再 scrollTo 回原位置（顺序反了会看到页面跳到顶部再回来）。
       负 top 的取整用 Math.round——iOS 对亚像素 top 会发火。 */
    const lockScroll = () => {
        savedScrollY = Math.round(win.scrollY || win.pageYOffset || 0);
        prevOverflow = doc.body.style.overflow;
        doc.body.style.overflow = 'hidden';
        doc.body.style.position = 'fixed';
        doc.body.style.top = `-${savedScrollY}px`;
        doc.body.style.left = '0';
        doc.body.style.right = '0';
        doc.body.style.width = '100%';
    };
    const unlockScroll = () => {
        doc.body.style.overflow = prevOverflow;
        doc.body.style.position = '';
        doc.body.style.top = '';
        doc.body.style.left = '';
        doc.body.style.right = '';
        doc.body.style.width = '';
        if (typeof win.scrollTo === 'function') { win.scrollTo(0, savedScrollY); }
    };

    /* 背景钉住：inert 一步到位（焦点与指针全部被浏览器挡住，比手写困排更彻底，
       且顺带解决「Tab 到地址栏再回来」这类手写管不了的路径）。不支持的浏览器
       （Safari < 15.5 等）退回 doc keydown 里的手写 Tab 困排。 */
    const setBackgroundInert = (next) => {
        if (next) {
            inerted = [...doc.body.children].filter(
                (el) => el !== overlay && !overlay.contains(el));
            for (const el of inerted) { el.setAttribute('inert', ''); }
        } else {
            for (const el of inerted) { el.removeAttribute('inert'); }
            inerted = [];
        }
    };

    function open() {
        if (opened) { return; }
        lastFocus = doc.activeElement;
        setOpen(true);
        lockScroll();
        if (supportsInert) { setBackgroundInert(true); }
        input.focus();
    }

    function close() {
        if (!opened) { return; }
        setOpen(false);
        unlockScroll();
        if (supportsInert) { setBackgroundInert(false); }
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
        // Tab 困排**兜底路径**：仅在不支持 inert 的浏览器启用手写循环。
        // 支持 inert 时背景节点被钉住，Tab 根本出不去（且 inert 连指针一起挡，
        // 手写循环管不了那条路径）——两个机制不要同时开，否则焦点会被抢两轮。
        if (e.key === 'Tab' && opened && !supportsInert) {
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

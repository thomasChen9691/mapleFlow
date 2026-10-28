/**
 * reveal 协议·行为断言（seam S1：引擎模块的公有心智）
 * ============================================================
 * 被测对象：assets/js/mf-reveal/ 下的引擎 ESM 模块——
 *   · filter.js     产品索引筛选引擎（自动注册 .mf-index roots）
 *   · scroll-in.js  滚动进场引擎（.reveal → is-in 的 IO 写入方）
 * 断言方式：jsdom 加载镜像渲染 seam DOM 契约的样本 HTML，
 *   import 引擎模块（cache-bust 强制重新求值），交互后断言可观测 DOM 状态。
 *
 * seam 约定（工单 0022 决议④ + 0023 决议，正式 seam）：
 *   A 类 9 项行为全部落本文件；样本 HTML 手写、镜像引擎 docstring 的 DOM 契约；
 *   渲染 seam 是否偏离契约由 B 类产物断言（tests/assert_site_contracts.py）守。
 *   依赖由 package.json 声明（jsdom devDependency），CI 以 npm ci + 本文件为
 *   权威守门（0023 决议①），本地跑同一命令即可复现。
 *
 * 与 Hugo 版本 skew 的关系：断言只消费引擎源码，不经 Hugo 构建，
 *   与 CI 钉版 0.164 / 本机 0.167 无关。
 *
 * 跑法：
 *   npm ci && node tests/assert_reveal.mjs
 */
import { check, finish, installDom, loadFresh, loadMounted } from './dom.mjs';
/** 筛选控件条：镜像 product-index.html 渲染 seam 的 DOM 契约（词汇归 ADR-0006） */
function filtersBar() {
  return `<div class="mf-filters">
    <button type="button" class="mf-filter" data-group="kind" data-value="all" aria-pressed="true">全部</button>
    <button type="button" class="mf-filter" data-group="kind" data-value="workflow" aria-pressed="false">工作流</button>
    <button type="button" class="mf-filter" data-group="kind" data-value="document" aria-pressed="false">文档</button>
    <button type="button" class="mf-filter" data-group="kind" data-value="question-bank" aria-pressed="false">题库</button>
    <span class="mf-sep" aria-hidden="true"></span>
    <button type="button" class="mf-filter" data-group="price" data-value="free" aria-pressed="false">免费</button>
    <button type="button" class="mf-filter" data-group="price" data-value="paid" aria-pressed="false">付费</button>
    <span class="mf-count" aria-live="polite"></span>
  </div>`;
}

/** 产品行：kind 三元循环、price 交替（第 1 行 workflow/paid，第 2 行 document/free…） */
function rowsHtml(n) {
  const kinds = ['workflow', 'document', 'question-bank'];
  return Array.from({ length: n }, (_, i) =>
    `<li class="mf-row reveal" id="fx-${i + 1}" data-kind="${kinds[i % 3]}" data-price="${i % 2 ? 'free' : 'paid'}"><div class="mf-row-num">${String(i + 1).padStart(2, '0')}</div></li>`).join('\n');
}

function sampleIndex(n = 3, id = 'mf-idx-0') {
  return `<div class="mf-index" id="${id}">
  ${filtersBar()}
  <ol class="mf-rows">
    ${rowsHtml(n)}
  </ol>
  <p class="mf-empty" hidden>没有符合筛选条件的资源。</p>
</div>`;
}

/** 点击某组某值按钮 */
function clickFilter(dom, group, value) {
  dom.window.document
    .querySelector(`.mf-filter[data-group="${group}"][data-value="${value}"]`)
    .dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
}

console.log('reveal 行为断言（S1 seam，正式；CI 权威守门）');

// ---- RGR-0：引擎 import 无副作用；注册缝在 app.js（0083 决议）----
// 「注册点唯一」的可观测形态：加载引擎模块本身不改变 DOM；必须显式调用
// 导出函数才生效。历史实现是 import 期 autoInit() 自注册——那让「谁挂了谁」
// 散落在各引擎尾部，app.js 只剩三行 import。
{
  const dom = installDom('<div class="reveal" id="r0"></div>');
  const mod = await loadFresh('assets/js/mf-reveal/scroll-in.js');
  const el = dom.window.document.getElementById('r0');
  check(
    'RGR-0a 引擎 import 不产生副作用（.reveal 未被自动点亮）',
    !el.classList.contains('is-in'),
    'import 期自注册仍在写 is-in',
  );
  mod.initScrollIn(dom.window.document);
  check(
    'RGR-0b 显式调用 initScrollIn 后才点亮（无 IO 降级直落终态）',
    el.classList.contains('is-in'),
    'explicit initScrollIn did not light up .reveal',
  );
}

// ---- RGR-1：引擎存在且 import 时自动注册 roots，初始 apply(false) 写计数 ----
{
  const dom = installDom(sampleIndex());
  await loadMounted('assets/js/mf-reveal/filter.js', (m) => m.mountFilter(document));
  const count = dom.window.document.querySelector('.mf-count');
  check(
    'RGR-1 挂载即注册 .mf-index roots，初始计数为「显示 3 / 3」',
    count.textContent === '显示 3 / 3',
    `got count=${JSON.stringify(count.textContent)}`,
  );
}

// ---- RGR-2：点击切换 state，同值再点回 all，组内 aria-pressed 互斥 ----
{
  const dom = installDom(sampleIndex());
  await loadMounted('assets/js/mf-reveal/filter.js', (m) => m.mountFilter(document));
  const doc = dom.window.document;
  const allBtn = doc.querySelector('.mf-filter[data-group="kind"][data-value="all"]');
  const wfBtn = doc.querySelector('.mf-filter[data-group="kind"][data-value="workflow"]');

  clickFilter(dom, 'kind', 'workflow');
  check(
    'RGR-2a 点击 workflow：workflow aria-pressed=true、all 归 false',
    wfBtn.getAttribute('aria-pressed') === 'true' && allBtn.getAttribute('aria-pressed') === 'false',
    `got wf=${wfBtn.getAttribute('aria-pressed')} all=${allBtn.getAttribute('aria-pressed')}`,
  );
  clickFilter(dom, 'kind', 'workflow');
  check(
    'RGR-2b 同值再点回 all：all=true、workflow 归 false',
    allBtn.getAttribute('aria-pressed') === 'true' && wfBtn.getAttribute('aria-pressed') === 'false',
    `got wf=${wfBtn.getAttribute('aria-pressed')} all=${allBtn.getAttribute('aria-pressed')}`,
  );
}

// ---- RGR-3：is-hidden 切换、计数随过滤更新、空态显隐 ----
{
  const dom = installDom(sampleIndex());
  await loadMounted('assets/js/mf-reveal/filter.js', (m) => m.mountFilter(document));
  const doc = dom.window.document;
  const row = (id) => doc.getElementById(id);
  const count = doc.querySelector('.mf-count');
  const empty = doc.querySelector('.mf-empty');

  clickFilter(dom, 'kind', 'workflow');
  check(
    'RGR-3a 筛 workflow：仅匹配行可见，其余加 is-hidden；计数「显示 1 / 3」；空态隐藏',
    !row('fx-1').classList.contains('is-hidden')
      && row('fx-2').classList.contains('is-hidden')
      && row('fx-3').classList.contains('is-hidden')
      && count.textContent === '显示 1 / 3'
      && empty.hidden === true,
    `got fx1=${row('fx-1').className} fx2=${row('fx-2').className} fx3=${row('fx-3').className} count=${count.textContent} empty.hidden=${empty.hidden}`,
  );

  clickFilter(dom, 'price', 'paid');
  check(
    'RGR-3b 追加 price=paid：计数不变「显示 1 / 3」',
    count.textContent === '显示 1 / 3',
    `got count=${count.textContent}`,
  );

  clickFilter(dom, 'kind', 'document');
  check(
    'RGR-3c 组合筛到 0 匹配：空态显示、计数「显示 0 / 3」',
    empty.hidden === false && count.textContent === '显示 0 / 3',
    `got empty.hidden=${empty.hidden} count=${count.textContent}`,
  );
}

// ---- RGR-4：animate 路径直写 is-in，--mf-i 第 9 条起截断为 8 ----
{
  const dom = installDom(sampleIndex(12));
  await loadMounted('assets/js/mf-reveal/filter.js', (m) => m.mountFilter(document));
  const doc = dom.window.document;
  const rows = [...doc.querySelectorAll('.mf-row')];
  clickFilter(dom, 'kind', 'all');

  const allIn = rows.every((el) => el.classList.contains('is-in'));
  const mfI = rows.map((el) => el.style.getPropertyValue('--mf-i'));
  const expectI = [...Array.from({ length: 9 }, (_, i) => String(i)), '8', '8', '8'];
  check(
    'RGR-4a 交互后 12 个可见行全部直写 is-in 终态',
    allIn,
    `got rows without is-in: ${rows.filter((el) => !el.classList.contains('is-in')).map((el) => el.id).join(',')}`,
  );
  check(
    'RGR-4b --mf-i 前 9 条为 0..8，第 10-12 条截断为 8',
    JSON.stringify(mfI) === JSON.stringify(expectI),
    `got ${JSON.stringify(mfI)}`,
  );
}

// ---- RGR-5：morph/bump 一次性重播，morph 由 timer 移除，bump 无 timer ----
{
  const dom = installDom(sampleIndex());
  // 捕获 timer：不睡真时间，手动 flush；不断言具体毫秒值（C 类：调值属视觉层）
  const timers = [];
  dom.window.setTimeout = (fn, ms) => { timers.push({ fn, ms }); return timers.length; };
  dom.window.clearTimeout = () => {};
  await loadMounted('assets/js/mf-reveal/filter.js', (m) => m.mountFilter(document));

  const doc = dom.window.document;
  const list = doc.querySelector('.mf-rows');
  const count = doc.querySelector('.mf-count');
  clickFilter(dom, 'kind', 'workflow');

  check(
    'RGR-5a 交互后 list 加 is-morphing、count 加 is-bump；仅 morph 挂一个 timer',
    list.classList.contains('is-morphing') && count.classList.contains('is-bump')
      && timers.length === 1,
    `got list=${list.className} count=${count.className} timers=${timers.length}`,
  );

  timers.forEach((t) => t.fn());
  check(
    'RGR-5b flush timer 后 morph 移除、bump 保留（一次性）',
    !list.classList.contains('is-morphing') && count.classList.contains('is-bump'),
    `got list=${list.className} count=${count.className}`,
  );
}

// ---- RGR-6：prefers-reduced-motion 下仍完整过滤，但不播放 morph/bump ----
{
  const dom = installDom(sampleIndex());
  dom.window.matchMedia = () => ({ matches: true, addEventListener() {}, removeEventListener() {} });
  await loadMounted('assets/js/mf-reveal/filter.js', (m) => m.mountFilter(document));
  const doc = dom.window.document;
  const list = doc.querySelector('.mf-rows');
  const count = doc.querySelector('.mf-count');
  clickFilter(dom, 'kind', 'workflow');

  check(
    'RGR-6 减弱动效：过滤与 is-in 照常，morph/bump 不播放',
    !doc.getElementById('fx-1').classList.contains('is-hidden')
      && doc.getElementById('fx-2').classList.contains('is-hidden')
      && count.textContent === '显示 1 / 3'
      && doc.getElementById('fx-1').classList.contains('is-in')
      && !list.classList.contains('is-morphing')
      && !count.classList.contains('is-bump'),
    `got list=${list.className} count=${count.className} count.text=${count.textContent}`,
  );
}

// ---- RGR-7：滚动进场引擎三态（无 IO 全量 / IO 视口点亮 / 减弱动效直落）----
{
  /* 7a：无 IntersectionObserver（jsdom 默认缺席）→ 全量直写 is-in */
  const dom = installDom(`<div><p class="reveal" id="r1">a</p><p class="reveal" id="r2">b</p></div>`);
  await loadMounted('assets/js/mf-reveal/scroll-in.js', (m) => m.initScrollIn(document));
  check(
    'RGR-7a 无 IntersectionObserver：全部 .reveal 直写 is-in 终态',
    dom.window.document.getElementById('r1').classList.contains('is-in')
      && dom.window.document.getElementById('r2').classList.contains('is-in'),
    `got r1=${dom.window.document.getElementById('r1').className} r2=${dom.window.document.getElementById('r2').className}`,
  );
}
{
  /* 7b：IO stub → 仅视口内点亮，点亮即 unobserve，视口外保持 */
  const dom = installDom(`<div><p class="reveal" id="r1">a</p><p class="reveal" id="r2">b</p></div>`);
  let fire; const observed = []; const unobserved = [];
  dom.window.IntersectionObserver = class {
    constructor(cb) { fire = cb; }
    observe(el) { observed.push(el); }
    unobserve(el) { unobserved.push(el); }
    disconnect() {}
  };
  await loadMounted('assets/js/mf-reveal/scroll-in.js', (m) => m.initScrollIn(document));
  const doc = dom.window.document;
  check(
    'RGR-7b1 有 IO：两个 .reveal 都被 observe，初始不亮',
    observed.length === 2 && !doc.getElementById('r1').classList.contains('is-in'),
    `got observed=${observed.length}`,
  );
  fire([{ isIntersecting: true, target: doc.getElementById('r1') }, { isIntersecting: false, target: doc.getElementById('r2') }], null);
  check(
    'RGR-7b2 视口内条目点亮并 unobserve，视口外保持未亮',
    doc.getElementById('r1').classList.contains('is-in')
      && unobserved.length === 1 && unobserved[0] === doc.getElementById('r1')
      && !doc.getElementById('r2').classList.contains('is-in'),
    `got r1=${doc.getElementById('r1').className} unobserved=${unobserved.length} r2=${doc.getElementById('r2').className}`,
  );
}
{
  /* 7c：减弱动效 → 不走 IO，全量直落终态（A7 的 reduce 分支） */
  const dom = installDom(`<div><p class="reveal" id="r1">a</p><p class="reveal" id="r2">b</p></div>`);
  dom.window.matchMedia = () => ({ matches: true, addEventListener() {}, removeEventListener() {} });
  const observed = [];
  dom.window.IntersectionObserver = class {
    constructor() {}
    observe(el) { observed.push(el); }
    unobserve() {}
    disconnect() {}
  };
  await loadMounted('assets/js/mf-reveal/scroll-in.js', (m) => m.initScrollIn(document));
  const doc = dom.window.document;
  check(
    'RGR-7c 减弱动效：不构造 IO、全部直落 is-in',
    observed.length === 0
      && doc.getElementById('r1').classList.contains('is-in')
      && doc.getElementById('r2').classList.contains('is-in'),
    `got observed=${observed.length} r1=${doc.getElementById('r1').className}`,
  );
}

// ---- RGR-8：同页多实例 roots 各自独立（state/计数/aria 不外溢）----
{
  const dom = installDom(`<div>${sampleIndex(3, 'mf-idx-a')}${sampleIndex(3, 'mf-idx-b')}</div>`);
  await loadMounted('assets/js/mf-reveal/filter.js', (m) => m.mountFilter(document));
  const doc = dom.window.document;
  const rootA = doc.getElementById('mf-idx-a');
  const rootB = doc.getElementById('mf-idx-b');
  rootA.querySelector('.mf-filter[data-group="kind"][data-value="workflow"]')
    .dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));

  const countA = rootA.querySelector('.mf-count').textContent;
  const countB = rootB.querySelector('.mf-count').textContent;
  const bAll = rootB.querySelector('.mf-filter[data-group="kind"][data-value="all"]').getAttribute('aria-pressed');
  const bHidden = [...rootB.querySelectorAll('.mf-row')].some((el) => el.classList.contains('is-hidden'));
  check(
    'RGR-8 点 A 的 workflow：A 计数「显示 1 / 3」，B 计数/aria/可见性均不受影响',
    countA === '显示 1 / 3' && countB === '显示 3 / 3' && bAll === 'true' && !bHidden,
    `got countA=${countA} countB=${countB} bAll=${bAll} bHidden=${bHidden}`,
  );
}

// ---- RGR-9：阅读进度条·纯计算（computeProgress 的字面量期望）----
{
  const dom = installDom('<div></div>');
  const mod = await loadFresh('assets/js/mf-reveal/reading-progress.js');
  const p0 = mod.computeProgress({ scrollY: 300, viewportH: 800, contentTop: 300, contentH: 2000 });
  const pMid = mod.computeProgress({ scrollY: 800, viewportH: 800, contentTop: 300, contentH: 2000 });
  const pEnd = mod.computeProgress({ scrollY: 1500, viewportH: 800, contentTop: 300, contentH: 2000 });
  const pOver = mod.computeProgress({ scrollY: 9999, viewportH: 800, contentTop: 300, contentH: 2000 });
  const pBefore = mod.computeProgress({ scrollY: 0, viewportH: 800, contentTop: 300, contentH: 2000 });
  const pShort = mod.computeProgress({ scrollY: 500, viewportH: 800, contentTop: 300, contentH: 600 });
  check('RGR-9a 顶部（scrollY = contentTop）→ 0', p0 === 0, `got ${p0}`);
  check('RGR-9b 中点（可滚动 1200，已滚 500）→ 0.4166666666666667（字面量，非公式反推）',
    Math.abs(pMid - 0.4166666666666667) < 1e-12, `got ${pMid}`);
  check('RGR-9c 到底（scrollY = contentTop + 可滚动高度）→ 1', pEnd === 1, `got ${pEnd}`);
  check('RGR-9d 越界钳制（超底 → 1、未到顶 → 0）', pOver === 1 && pBefore === 0,
    `got over=${pOver} before=${pBefore}`);
  check('RGR-9e 内容不足一屏（total <= 0）→ 0（条为空，不误导）', pShort === 0, `got ${pShort}`);
}

// ---- RGR-10：阅读进度条·写入 seam（--mf-progress）----
{
  const dom = installDom(`<div class="mf-progress" aria-hidden="true"><span></span></div>
    <div class="post-content">x</div>`);
  const win = dom.window;
  const bar = win.document.querySelector('.mf-progress');
  const content = win.document.querySelector('.post-content');
  // getBoundingClientRect 是**视口相对**坐标：绝对 top=300、已滚 900 时
  // rect.top = 300 - 900 = -600（引擎会 +scrollY 还原绝对位置）
  content.getBoundingClientRect = () => ({ top: -600, height: 2000, bottom: 1400, left: 0, right: 0, width: 0 });
  Object.defineProperty(win, 'innerHeight', { value: 800, configurable: true });
  Object.defineProperty(win, 'scrollY', { value: 900, configurable: true, writable: true });
  await loadMounted('assets/js/mf-reveal/reading-progress.js', (m) => m.initReadingProgress(document));
  const v = bar.style.getPropertyValue('--mf-progress');
  check('RGR-10a 挂载即按当前位置写入 --mf-progress（900 滚 / 可滚 1200 → 0.500）',
    Math.abs(parseFloat(v) - 0.5) < 1e-3, `got "${v}"`);
}

// ---- RGR-11：非文章页（缺 .mf-progress / .post-content）静默 no-op ----
{
  const dom = installDom('<div class="list-page">no article here</div>');
  const mod = await loadFresh('assets/js/mf-reveal/reading-progress.js');
  let threw = false;
  try { mod.initReadingProgress(dom.window.document); } catch { threw = true; }
  check('RGR-11 缺挂点时不抛错（非文章页静默降级）', !threw);
}

// ---- RGR-12：scroll-in 自身失败时 fail-open（0084 决议；ADR-0002）----
// 隔离（app.js 的 try/catch）只保其余引擎，保不住「scroll-in 自己炸了，
// 内容停在 opacity:0」。降级路径与「无 IntersectionObserver」同一条：
// 全量直写 is-in。这里用 matchMedia 抛错来逼出异常分支。
{
  const dom = installDom('<div class="reveal" id="r12"></div>');
  const mod = await loadFresh('assets/js/mf-reveal/scroll-in.js');
  dom.window.matchMedia = () => { throw new Error('boom'); };
  let threw = false;
  try { mod.initScrollIn(dom.window.document); } catch { threw = true; }
  const el = dom.window.document.getElementById('r12');
  check('RGR-12a scroll-in 内部失败不外抛（不打断挂载点）', !threw, '异常逃逸到调用方');
  check('RGR-12b 失败时内容仍可见（fail-open 直写 is-in）',
    el.classList.contains('is-in'), '停在 opacity:0 = 内容消失');
}

// ---- RGR-13：app.js 装配完整性（0084 决议；防「漏挂一个引擎」的假绿）----
// 行为面而非源码面：装一个含三类挂点的 DOM，加载生产入口 app.js，
// 三个副作用必须都出现。只 import 不挂载（漏进 ENGINES 表）会红——
// 源码扫描式的检查在这里不够：`import './x.js'` 也会命中。
{
  const dom = installDom(`
    <div class="reveal" id="r13"></div>
    <div class="mf-progress" aria-hidden="true"><span></span></div>
    <div class="post-content">x</div>
    ${sampleIndex(2, 'mf-idx-r13')}
  `);
  const content = dom.window.document.querySelector('.post-content');
  content.getBoundingClientRect = () => ({ top: 0, height: 2000, bottom: 2000, left: 0, right: 0, width: 0 });
  Object.defineProperty(dom.window, 'innerHeight', { value: 800, configurable: true });
  Object.defineProperty(dom.window, 'scrollY', { value: 0, configurable: true, writable: true });
  await loadFresh('assets/js/mf-reveal/app.js');
  const doc = dom.window.document;
  const lit = doc.getElementById('r13').classList.contains('is-in');
  const counted = doc.querySelector('.mf-count').textContent === '显示 2 / 2';
  const progress = doc.querySelector('.mf-progress').style.getPropertyValue('--mf-progress') !== '';
  check(
    'RGR-13 app.js 装配三个引擎（点亮 / 筛选计数 / 进度变量都出现）',
    lit && counted && progress,
    `lit=${lit} counted=${counted} progress=${progress}`,
  );
}

finish();

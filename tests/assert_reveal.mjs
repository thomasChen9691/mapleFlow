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
 *   渲染 seam 是否偏离契约由 B 类产物断言（tests/assert_product_states.py）守。
 *   依赖由 package.json 声明（jsdom devDependency），CI 以 npm ci + 本文件为
 *   权威守门（0023 决议①），本地跑同一命令即可复现。
 *
 * 与 Hugo 版本 skew 的关系：断言只消费引擎源码，不经 Hugo 构建，
 *   与 CI 钉版 0.164 / 本机 0.167 无关。
 *
 * 跑法：
 *   npm ci && node tests/assert_reveal.mjs
 */
import { JSDOM } from 'jsdom';
import { pathToFileURL, fileURLToPath } from 'node:url';
import path from 'node:path';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let passed = 0;
let failed = 0;
let bust = 0;

function check(name, cond, detail) {
  if (cond) {
    passed++;
    console.log(`  ok  ${name}`);
  } else {
    failed++;
    console.log(`FAIL  ${name}${detail ? `\n      ${detail}` : ''}`);
  }
}

/** 重新求值引擎模块（ESM 缓存会让 import 副作用只跑一次，测试间必须 cache-bust） */
async function loadFresh(rel) {
  const url = pathToFileURL(path.join(REPO, rel)).href + `?t=${++bust}`;
  return import(url);
}

/** 绑定 jsdom 全局（引擎以 document/window 全局为宿主） */
function installDom(html) {
  const dom = new JSDOM(html, { url: 'http://localhost/' });
  globalThis.window = dom.window;
  globalThis.document = dom.window.document;
  return dom;
}

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

console.log('reveal 行为断言（S1 seam，provisional pending 0023）');

// ---- RGR-1：引擎存在且 import 时自动注册 roots，初始 apply(false) 写计数 ----
{
  const dom = installDom(sampleIndex());
  await loadFresh('assets/js/mf-reveal/filter.js');
  const count = dom.window.document.querySelector('.mf-count');
  check(
    'RGR-1 import 即自动注册 .mf-index roots，初始计数为「显示 3 / 3」',
    count.textContent === '显示 3 / 3',
    `got count=${JSON.stringify(count.textContent)}`,
  );
}

// ---- RGR-2：点击切换 state，同值再点回 all，组内 aria-pressed 互斥 ----
{
  const dom = installDom(sampleIndex());
  await loadFresh('assets/js/mf-reveal/filter.js');
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
  await loadFresh('assets/js/mf-reveal/filter.js');
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
  await loadFresh('assets/js/mf-reveal/filter.js');
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
  await loadFresh('assets/js/mf-reveal/filter.js');

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
  await loadFresh('assets/js/mf-reveal/filter.js');
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
  await loadFresh('assets/js/mf-reveal/scroll-in.js');
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
  await loadFresh('assets/js/mf-reveal/scroll-in.js');
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
  await loadFresh('assets/js/mf-reveal/scroll-in.js');
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
  await loadFresh('assets/js/mf-reveal/filter.js');
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

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);

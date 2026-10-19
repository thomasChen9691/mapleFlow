/**
 * reveal 协议·行为断言（seam S1：引擎模块的公有心智）
 * ============================================================
 * 被测对象：assets/js/mf-reveal/ 下的引擎 ESM 模块——
 *   · filter.js     产品索引筛选引擎（自动注册 .mf-index roots）
 *   · scroll-in.js  滚动进场引擎（.reveal → is-in 的 IO 写入方）
 * 断言方式：jsdom 加载镜像渲染 seam DOM 契约的样本 HTML，
 *   import 引擎模块（cache-bust 强制重新求值），交互后断言可观测 DOM 状态。
 *
 * seam 约定（工单 0022 决议④，本文件为施工期 provisional）：
 *   A 行为 harness 9 项全部落本文件；样本 HTML 为手写（镜像 DOM 契约），
 *   样本来源 / 套件归并 / CI 守门待工单 0023 质询追认。
 *
 * 与 Hugo 版本 skew 的关系：断言只消费引擎源码，不经 Hugo 构建，
 *   与 CI 钉版 0.164 / 本机 0.167 无关。
 *
 * 跑法（jsdom 经 node_modules symlink 从 managed workspace 解析，不入仓）：
 *   node tests/assert_reveal.mjs
 */
import { JSDOM } from 'jsdom';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

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

/** 样本：镜像 product-index.html 渲染 seam 的 DOM 契约（3 条产品，filters=true） */
function sampleIndex() {
  return `<div class="mf-index" id="mf-idx-0">
  <div class="mf-filters">
    <button type="button" class="mf-filter" data-group="kind" data-value="all" aria-pressed="true">全部</button>
    <button type="button" class="mf-filter" data-group="kind" data-value="workflow" aria-pressed="false">工作流</button>
    <button type="button" class="mf-filter" data-group="kind" data-value="document" aria-pressed="false">文档</button>
    <button type="button" class="mf-filter" data-group="kind" data-value="question-bank" aria-pressed="false">题库</button>
    <span class="mf-sep" aria-hidden="true"></span>
    <button type="button" class="mf-filter" data-group="price" data-value="free" aria-pressed="false">免费</button>
    <button type="button" class="mf-filter" data-group="price" data-value="paid" aria-pressed="false">付费</button>
    <span class="mf-count" aria-live="polite"></span>
  </div>
  <ol class="mf-rows">
    <li class="mf-row reveal" id="fx-1" data-kind="workflow" data-price="paid"><div class="mf-row-num">01</div></li>
    <li class="mf-row reveal" id="fx-2" data-kind="document" data-price="free"><div class="mf-row-num">02</div></li>
    <li class="mf-row reveal" id="fx-3" data-kind="question-bank" data-price="paid"><div class="mf-row-num">03</div></li>
  </ol>
  <p class="mf-empty" hidden>没有符合筛选条件的资源。</p>
</div>`;
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

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);

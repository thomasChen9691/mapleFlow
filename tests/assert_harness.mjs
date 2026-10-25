/**
 * assert_harness.mjs —— harness Node 侧（dom.mjs）自测（工单 0066）
 * ============================================================
 * 测什么：牙临界行为——check 的 verdict 记录、finish 的汇总与退出码、
 *   installDom 的全局绑定、installPage 的 env 装配、loadFresh 的重求值。
 *   间接覆盖判据（0066 Q1）：破坏这些行为时契约套件是否可定位地红——
 *   check 不达标（已实证：if(true) 变异下静默假绿、套件无法自知），故立自测。
 *
 * 纪律：**独立记账**——刻意不复用被测的 check/finish 做本文件的记账（复用
 *   即同义反复：被测物坏掉时自测的记账一起坏）；期望值独立字面量；每条
 *   以变异检验证牙（施工期执行：破坏 dom.mjs → 本文件红 → 还原）；本文件
 *   禁存任何被测模块的契约字面量（0061 禁项在自测侧同样生效）。
 *
 * 观测法（进程内，零子进程）：
 *   · finish 会 process.exit——截换 process.exit 与 console.log 两个全局
 *     副作用边界观测之，用后恢复；
 *   · dom.mjs 的计数器是模块级的——每个观测经 loadFresh 自加载拿全新实例
 *     （计数器归零），汇总字面量才是确定值。
 *
 * 跑法：npm test（package.json 串联，本文件先于契约断言——harness 红在
 *   契约断言之前先红，失败定位前移）。
 */
import * as bootstrap from './dom.mjs';

// 独立记账（被测物正是 dom.mjs 的 check/finish，故自建）
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

/** 每个观测拿一份全新 dom.mjs 实例（模块级计数器归零，汇总字面量才确定）。 */
async function freshDom() {
    return bootstrap.loadFresh('tests/dom.mjs');
}

/** 观测 finish：截换 process.exit（抛 ExitSignal 模拟其不返回语义）与
 *  console.log（收汇总结论），用后恢复。 */
class ExitSignal extends Error {
    constructor(code) { super('exit:' + code); this.code = code; }
}

function observeFinish(fn) {
    const realExit = process.exit;
    const realLog = console.log;
    let exitCode = null;
    const out = [];
    process.exit = (c) => { throw new ExitSignal(c === undefined ? 0 : c); };
    console.log = (...a) => out.push(a.join(' '));
    try {
        fn();
    } catch (e) {
        if (!(e instanceof ExitSignal)) { throw e; }
        exitCode = e.code;
    } finally {
        process.exit = realExit;
        console.log = realLog;
    }
    return { exitCode, out: out.join('\n') };
}

// ---- check 的 verdict 记录：失败必须进汇总与退出码（防 if(true) 静默假绿类）
{
    const dom = await freshDom();
    const r = observeFinish(() => { dom.check('probe', false); dom.finish(); });
    check('check 记录失败：finish 退出码 1', r.exitCode === 1, `got ${r.exitCode}`);
    check('check 记录失败：汇总 0/1 + RED',
        r.out.includes('0/1 passed') && r.out.includes('RED'), r.out.slice(-120));
}
{
    const dom = await freshDom();
    const r = observeFinish(() => { dom.check('probe', true); dom.finish(); });
    check('check 记录通过：finish 退出码 0', r.exitCode === 0, `got ${r.exitCode}`);
    check('check 记录通过：汇总 1/1 + GREEN',
        r.out.includes('1/1 passed') && r.out.includes('GREEN'), r.out.slice(-120));
}
{
    const dom = await freshDom();
    const r = observeFinish(() => { dom.check('a', true); dom.check('b', false); dom.finish(); });
    check('混合 verdict：退出码 1 且汇总 1/2',
        r.exitCode === 1 && r.out.includes('1/2 passed'), r.out.slice(-120));
}

// ---- installDom：window / document 绑全局（引擎以全局为宿主的模式）
{
    const dom = await freshDom();
    const d = dom.installDom('<html><body><article><p>x</p></article></body></html>');
    check('installDom 绑全局且样本可查',
        typeof document !== 'undefined' && typeof window !== 'undefined'
        && document.querySelector('article') !== null
        && document.defaultView === window);
    d.window.close();
}

// ---- installPage：真 document + 注入 location 桩（入口引擎 env 模式）
{
    const dom = await freshDom();
    const env = dom.installPage({
        html: '<input id="q">',
        href: 'http://localhost/posts/foo.html',
        pathname: '/posts/foo.html',
    });
    check('installPage 装配 env（document + location 桩）',
        env.document.getElementById('q') !== null
        && env.location.href === 'http://localhost/posts/foo.html'
        && env.location.pathname === '/posts/foo.html');
}

// ---- loadFresh：cache-bust 重求值（ESM 缓存会让 import 副作用只跑一次）
{
    const dom = await freshDom();
    const a = await dom.loadFresh('assets/js/mf-reveal/reduced-motion.js');
    const b = await dom.loadFresh('assets/js/mf-reveal/reduced-motion.js');
    check('loadFresh 重求值（函数身份不同）',
        typeof a.prefersReducedMotion === 'function'
        && a.prefersReducedMotion !== b.prefersReducedMotion);
}

console.log(`\n${passed}/${passed + failed} passed`);
if (failed) {
    console.log('RED — %d 个行为未满足', failed);
    process.exit(1);
}
console.log('GREEN');
process.exit(0);

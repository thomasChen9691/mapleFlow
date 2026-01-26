// 1. 动态注入 Halo 动画 HTML
(function() {
    const loaderHTML = `
    <div id="halo-racer-loader">
      <div class="racer-container">
        <div class="bar p1"></div>
        <div class="bar p2"></div>
        <div class="bar red"></div>
      </div>
    </div>
  `;
    document.write(loaderHTML);

    // 动画消失逻辑
    const loader = document.getElementById('halo-racer-loader');
    window.addEventListener('load', function() {
        setTimeout(() => {
            loader.classList.add('hidden');
            setTimeout(() => { loader.style.display = 'none'; }, 300);
        }, 1000);
    });
})();

// 2. 代码块按钮逻辑 (智能默认折叠 + 复制)
function attachCodeBlockTools() {
    const svgCopy = '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>';
    const svgCheck = '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';

    // 箭头向上（折叠图标）
    const svgFold = '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/></svg>';
    // 箭头向下（展开图标）
    const svgUnfold = '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6z"/></svg>';

    const codeBlocks = document.querySelectorAll('.highlight');
    if (codeBlocks.length === 0) return;

    codeBlocks.forEach(block => {
        if (block.querySelector('.code-tools')) return;

        const tools = document.createElement('div');
        tools.className = 'code-tools';

        // --- 折叠按钮逻辑 ---
        const btnFold = document.createElement('button');
        btnFold.className = 'c-btn';

        // 【核心修改】智能判断：如果代码高度超过 150px，则默认折叠
        // 您可以修改这个数字：150 代表约 6-7 行代码的高度
        const threshold = 150;
        let isFolded = block.offsetHeight > threshold;

        if (isFolded) {
            block.classList.add('folded');   // 添加CSS折叠类
            btnFold.innerHTML = svgUnfold;   // 显示"向下展开"图标
            btnFold.title = "展开代码";
        } else {
            btnFold.innerHTML = svgFold;     // 显示"向上折叠"图标
            btnFold.title = "折叠代码";
        }

        btnFold.onclick = () => {
            isFolded = !isFolded;
            block.classList.toggle('folded');
            // 切换图标：折叠时显示"展开(下箭头)"，展开时显示"折叠(上箭头)"
            btnFold.innerHTML = isFolded ? svgUnfold : svgFold;
            btnFold.title = isFolded ? "展开代码" : "折叠代码";
        };

        // --- 复制按钮逻辑 ---
        const btnCopy = document.createElement('button');
        btnCopy.className = 'c-btn';
        btnCopy.innerHTML = svgCopy;
        btnCopy.title = "复制";
        btnCopy.onclick = () => {
            const codeElement = block.querySelector('td:last-child pre code') || block.querySelector('code');
            const codeText = codeElement ? codeElement.innerText : block.innerText;
            navigator.clipboard.writeText(codeText).then(() => {
                btnCopy.innerHTML = svgCheck;
                btnCopy.style.color = '#4caf50';
                setTimeout(() => {
                    btnCopy.innerHTML = svgCopy;
                    btnCopy.style.color = '';
                }, 2000);
            });
        };

        tools.appendChild(btnFold);
        tools.appendChild(btnCopy);

        // 插入到代码块最前面
        block.insertBefore(tools, block.firstChild);
    });
}

// 监听 DOM 加载
document.addEventListener('DOMContentLoaded', attachCodeBlockTools);

// 兜底超时
setTimeout(function() {
    const loader = document.getElementById('halo-racer-loader');
    if (loader && !loader.classList.contains('hidden')) loader.classList.add('hidden');
}, 5000);

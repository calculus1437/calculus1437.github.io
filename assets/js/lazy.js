(function() {
  // 等待 DOM 加载完成
  function initLazyRender() {
    // 找到所有可能包含公式的父容器（可以根据实际结构调整）
    // 建议观察每个独立的块级元素，例如 <p>, <div>, <li>, <blockquote> 等
    const containers = document.querySelectorAll('p, div, li, blockquote, section, article .content');
    // 如果上面选择太广，也可以只观察包裹公式的特定元素
    // 更简单：观察所有含有能触发表述的文本的容器？但不好判断。
    // 最稳妥：观察每个段落和 div，这样粒度小，渲染及时。
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          // 避免重复渲染
          if (el.hasAttribute('data-katex-rendered')) return;
          // 渲染该元素内的公式
          try {
            renderMathInElement(el, {
              delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true}
              ]
            });
          } catch (err) {
            console.warn('KaTeX render error', err);
          }
          el.setAttribute('data-katex-rendered', 'true');
          // 渲染后可以选择不再观察该元素
          observer.unobserve(el);
        }
      });
    }, { rootMargin: '200px' }); // 提前200px开始渲染，避免滚动时看到未渲染的公式

    containers.forEach(el => observer.observe(el));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLazyRender);
  } else {
    initLazyRender();
  }
})();
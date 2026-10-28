(() => {
  'use strict';
  const dataElement = document.getElementById('study-data');
  if (!dataElement) return;
  const studies = JSON.parse(dataElement.textContent);
  const select = document.getElementById('study-select');
  const image = document.getElementById('viewer-image');
  const stage = document.getElementById('viewer-open');
  const aspectButtons = [...document.querySelectorAll('.orientation-controls button')];
  const prompt = document.getElementById('creation-prompt');
  const copyStatus = document.getElementById('copy-status');
  const dialog = document.getElementById('image-dialog');
  const motionToggle = document.getElementById('motion-toggle');
  const systemMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let reduced = systemMotion.matches;
  let orientation = 'landscape';
  let displayedOrientation = 'landscape';
  let current = studies[0];
  let request = 0;
  let lastDialogFocus = null;
  let promptEdited = false;
  const observationText = {
    '01-glass-cup': '透射、厚边与主体对应',
    '02-spoon-paper': '完整轮廓、纸层与覆盖密度',
    '03-porcelain-cup': '色场、白瓷曲面与主体占比',
    '04-spoon-drawing': '手、工具与纸稿的实际接触',
    '05-spoon-finish-detail': '凹面反射、薄边与加工方向',
    '06-spoon-finish-comparison': '不同表面的反射与可用比较',
    '07-held-spoon-study': '手持支撑、薄纸弯曲与覆盖',
    '08-cotton-paper-embossing': '浅压纹、纸边与厚度',
    '09-softbox-paper-study': '连续光场、叠层与线条接续'
  };
  function applyMotion(value) {
    reduced = value;
    document.documentElement.dataset.motion = value ? 'reduced' : 'standard';
    motionToggle.setAttribute('aria-pressed', String(value));
    motionToggle.textContent = value ? '减少动画：已开启' : '减少动画';
    if (value) for (const animation of document.getAnimations?.() || []) {
      if (animation.effect?.getTiming().iterations === Infinity) animation.cancel();
      else animation.finish();
    }
  }
  applyMotion(reduced);
  motionToggle.addEventListener('click', () => applyMotion(!reduced));
  systemMotion.addEventListener('change', event => applyMotion(event.matches));
  prompt.addEventListener('input', () => { promptEdited = true; });
  function updatePrompt() {
    if (promptEdited) {
      copyStatus.textContent = '已保留你编辑的请求。';
      return;
    }
    const aspect = orientation === 'portrait' ? '9:16' : '16:9';
    prompt.value = `使用 $siuyu-lightbox-still-life，根据我的主体与参考，生成一张 ${aspect} 的光台材料研究图。\n参考“${current.title}”中的${observationText[current.id] || '材料与光的关系'}，按我提供的主体确定材料、结构和颜色。\n安排能让这些关系可见的机位、光线和空间，实际生成图片并检查完整构图与原生细节。`;
    copyStatus.textContent = `当前请求：${current.title}，${aspect}。可直接编辑。`;
  }
  async function updateStudy() {
    const token = ++request;
    const next = studies.find(item => item.id === select.value) || studies[0];
    const asset = next[orientation];
    stage.setAttribute('aria-busy', 'true');
    const preload = new Image();
    preload.src = asset.image;
    try { await preload.decode(); } catch (_) {
      if (token !== request) return;
      select.value = current.id;
      orientation = displayedOrientation;
      stage.removeAttribute('aria-busy');
      document.getElementById('viewer-status').textContent = '图片暂时未能载入，请重新选择。';
      return;
    }
    if (token !== request) return;
    current = next;
    displayedOrientation = orientation;
    image.src = asset.image;
    image.width = asset.width;
    image.height = asset.height;
    const label = orientation === 'portrait' ? '竖幅' : '横幅';
    image.alt = `${current.title}，${label}构图`;
    stage.dataset.orientation = orientation;
    stage.setAttribute('aria-label', `放大${current.title}，${label}`);
    document.getElementById('study-title').textContent = current.title;
    document.getElementById('study-description').textContent = current.observe.replace(/^观察/, '');
    document.getElementById('viewer-dimension').textContent = `${label} · ${asset.width} × ${asset.height}`;
    document.getElementById('original-link').href = asset.image;
    document.getElementById('review-link').href = asset.visual_review;
    document.getElementById('parameters-link').href = asset.image_job;
    document.getElementById('viewer-status').textContent = `已显示${current.title}的${label}原生图片。`;
    for (const button of aspectButtons) button.setAttribute('aria-pressed', String(button.dataset.orientation === orientation));
    stage.removeAttribute('aria-busy');
    if (!reduced) image.animate([{opacity:.35,transform:'translateY(8px)'},{opacity:1,transform:'translateY(0)'}],{duration:380,easing:'cubic-bezier(.22,1,.36,1)'});
    updatePrompt();
  }
  select.addEventListener('change', updateStudy);
  for (const button of aspectButtons) button.addEventListener('click', () => {
    if (orientation === button.dataset.orientation) return;
    orientation = button.dataset.orientation;
    updateStudy();
  });
  stage.addEventListener('click', () => {
    const asset = current[displayedOrientation];
    document.getElementById('dialog-image').src = asset.image;
    document.getElementById('dialog-image').alt = image.alt;
    document.getElementById('dialog-title').textContent = image.alt;
    document.getElementById('dialog-original').href = asset.image;
    if (typeof dialog.showModal !== 'function') { location.href = asset.image; return; }
    lastDialogFocus = document.activeElement;
    dialog.showModal();
    document.body.classList.add('has-dialog');
    document.getElementById('dialog-close').focus();
  });
  document.getElementById('dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('keydown', event => {
    if (event.key !== 'Tab') return;
    const first = document.getElementById('dialog-close');
    const last = document.getElementById('dialog-original');
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault(); first.focus();
    }
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('has-dialog');
    if (lastDialogFocus) lastDialogFocus.focus();
  });
  document.getElementById('copy-request').addEventListener('click', async () => {
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Selection fallback');
      await navigator.clipboard.writeText(prompt.value);
      copyStatus.textContent = '创作请求已复制。附上你的主体与参考即可使用。';
    } catch (_) {
      prompt.focus(); prompt.select();
      copyStatus.textContent = '请求已选中，请按 ⌘C 或 Ctrl+C 复制。';
    }
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const el = entry.target;
        if (!reduced) {
          const type = el.dataset.enter;
          const frames = type === 'image' ? [{opacity:.7,transform:'scale(.98)'},{opacity:1,transform:'scale(1)'}] : type === 'fade' ? [{opacity:.3},{opacity:1}] : [{opacity:.4,transform:'translateY(20px)'},{opacity:1,transform:'translateY(0)'}];
          el.animate(frames,{duration:type === 'image' ? 950 : 650,easing:'cubic-bezier(.22,1,.36,1)',delay:type === 'row' ? 60 : 0});
        }
        observer.unobserve(el);
      }
    },{threshold:.16});
    for (const el of document.querySelectorAll('[data-enter]')) observer.observe(el);
    const hero = document.querySelector('.hero-figure');
    let heroVisible = false;
    const syncHero = () => hero.classList.toggle('is-in-view', heroVisible && !document.hidden);
    const heroObserver = new IntersectionObserver(entries => {
      for (const entry of entries) heroVisible = entry.isIntersecting;
      syncHero();
    },{threshold:.05});
    heroObserver.observe(hero);
    document.addEventListener('visibilitychange', syncHero);
  }
  updatePrompt();
})();

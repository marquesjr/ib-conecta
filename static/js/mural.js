// Mural da igreja em slide: setas avançam uma página de cartazes; sem JavaScript a faixa segue deslizável.
(() => {
  const mural = document.querySelector('.mural');
  const track = mural && mural.querySelector('.mural-track');
  const controls = mural && mural.querySelector('.mural-controls');
  if (!track || !controls) return;
  const items = Array.from(track.children);
  const [prev, next] = controls.querySelectorAll('.mural-button');
  const status = controls.querySelector('.mural-status');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  // Cartazes inteiramente à vista (com folga de 2px para arredondamento de subpixel).
  const visibleRange = () => {
    const left = track.scrollLeft - 2;
    const right = track.scrollLeft + track.clientWidth + 2;
    const shown = items
      .map((item, index) => ({ index, start: item.offsetLeft, end: item.offsetLeft + item.offsetWidth }))
      .filter(({ start, end }) => start >= left && end <= right);
    if (!shown.length) return [0, 0];
    return [shown[0].index, shown[shown.length - 1].index];
  };

  let frame = 0;
  const update = () => {
    frame = 0;
    const overflowing = track.scrollWidth > track.clientWidth + 2;
    controls.hidden = !overflowing;
    mural.classList.toggle('is-slider', overflowing);
    if (!overflowing) return;
    const [first, last] = visibleRange();
    status.textContent = first === last
      ? `${first + 1} de ${items.length}`
      : `${first + 1}–${last + 1} de ${items.length}`;
    prev.disabled = track.scrollLeft <= 2;
    next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
  };
  const schedule = () => { if (!frame) frame = requestAnimationFrame(update); };

  controls.addEventListener('click', (event) => {
    const button = event.target.closest('.mural-button');
    if (!button || button.disabled) return;
    const [first, last] = visibleRange();
    const perPage = Math.max(1, last - first + 1);
    const direction = Number(button.dataset.direction);
    const target = Math.min(items.length - 1, Math.max(0, first + direction * perPage));
    track.scrollTo({
      left: items[target].offsetLeft,
      behavior: reduceMotion.matches ? 'auto' : 'smooth',
    });
  });

  track.addEventListener('scroll', schedule, { passive: true });
  if ('ResizeObserver' in window) new ResizeObserver(schedule).observe(track);
  else window.addEventListener('resize', schedule);
  update();
})();

(() => {
  // Remover louvor pede confirmação, porque o tom e as observações se perdem.
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
})();

(() => {
  // Arrastar pelo ⠿ para ordenar (mouse e toque). Sem JS, as setas continuam funcionando.
  const list = document.querySelector('.playlist-items[data-reorder-url]');
  if (!list || !list.dataset.reorderUrl) return;
  const items = () => Array.from(list.querySelectorAll('.playlist-item'));
  if (items().length < 2) return;

  const csrf = list.querySelector('input[name="csrfmiddlewaretoken"]');
  list.classList.add('is-sortable');
  list.querySelectorAll('.playlist-handle').forEach((handle) => { handle.hidden = false; });
  const hint = document.querySelector('.playlist-hint');
  if (hint) hint.hidden = false;

  const refreshArrows = () => {
    const all = items();
    all.forEach((item, index) => {
      const up = item.querySelector('button[value="up"]');
      const down = item.querySelector('button[value="down"]');
      if (up) up.disabled = index === 0;
      if (down) down.disabled = index === all.length - 1;
    });
  };

  const save = (before) => {
    const order = items().map((item) => item.dataset.item);
    if (order.join() === before.join()) return;
    const body = new URLSearchParams();
    order.forEach((pk) => body.append('item', pk));
    fetch(list.dataset.reorderUrl, {
      method: 'POST',
      headers: { Accept: 'application/json', 'X-CSRFToken': csrf ? csrf.value : '' },
      body,
      credentials: 'same-origin',
    }).then((response) => {
      if (!response.ok) throw new Error(String(response.status));
      refreshArrows();
    }).catch(() => { window.location.reload(); });
  };

  let dragging = null;
  let before = [];

  list.addEventListener('pointerdown', (event) => {
    const handle = event.target.closest('.playlist-handle');
    if (!handle || event.button > 0) return;
    event.preventDefault();
    dragging = handle.closest('.playlist-item');
    before = items().map((item) => item.dataset.item);
    dragging.classList.add('is-dragging');
    handle.setPointerCapture(event.pointerId);
  });

  list.addEventListener('pointermove', (event) => {
    if (!dragging) return;
    const target = items().find((item) => {
      if (item === dragging) return false;
      const box = item.getBoundingClientRect();
      return event.clientY >= box.top && event.clientY <= box.bottom;
    });
    if (!target) return;
    const box = target.getBoundingClientRect();
    const after = event.clientY > box.top + box.height / 2;
    list.insertBefore(dragging, after ? target.nextSibling : target);
  });

  const drop = () => {
    if (!dragging) return;
    dragging.classList.remove('is-dragging');
    dragging = null;
    save(before);
  };
  list.addEventListener('pointerup', drop);
  list.addEventListener('pointercancel', drop);
})();

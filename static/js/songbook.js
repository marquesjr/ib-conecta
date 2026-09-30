(() => {
  // Busca enquanto digita: filtra a lista já carregada pelo título, sem recarregar a página.
  const input = document.querySelector('[data-song-search]');
  const list = document.querySelector('[data-song-list]');
  if (!input || !list) return;
  const empty = document.querySelector('[data-song-empty]');
  const items = Array.from(list.querySelectorAll('li[data-title]'));
  const printLinks = Array.from(document.querySelectorAll('[data-print-link]'));
  const normalize = (text) => text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();

  const apply = () => {
    const query = normalize(input.value);
    let visible = 0;
    items.forEach((item) => {
      const match = !query || normalize(item.dataset.title).includes(query);
      item.hidden = !match;
      if (match) visible += 1;
    });
    if (empty) empty.hidden = visible > 0;
    // A impressão acompanha a busca digitada.
    printLinks.forEach((link) => {
      const url = new URL(link.href, window.location.href);
      url.searchParams.set('q', input.value.trim());
      link.href = url.pathname + url.search;
    });
  };

  input.addEventListener('input', apply);
})();

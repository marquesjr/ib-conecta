// Cifra do louvor: botões A−/A+ mudam o tamanho da letra das cifras da página; sem JavaScript o bloco só rola para o lado.
(() => {
  const controls = document.querySelector('.chord-size');
  if (!controls) return;
  const sizes = ['.7rem', '.8rem', '.9rem', '1rem', '1.1rem'];
  const storageKey = 'ib-conecta:chord-size';
  const fallback = 2;
  let index = fallback;
  try {
    const stored = window.localStorage.getItem(storageKey);
    const saved = stored === null ? NaN : Number(stored);
    if (Number.isInteger(saved) && saved >= 0 && saved < sizes.length) index = saved;
  } catch (error) { /* armazenamento indisponível: usa o tamanho padrão */ }

  const buttons = controls.querySelectorAll('[data-chord-step]');
  const apply = () => {
    document.querySelectorAll('.chord-sheet').forEach((sheet) => sheet.style.setProperty('--chord-size', sizes[index]));
    buttons.forEach((button) => {
      const step = Number(button.dataset.chordStep);
      button.disabled = index + step < 0 || index + step >= sizes.length;
    });
  };

  buttons.forEach((button) => button.addEventListener('click', () => {
    index = Math.min(sizes.length - 1, Math.max(0, index + Number(button.dataset.chordStep)));
    try { window.localStorage.setItem(storageKey, String(index)); } catch (error) { /* ignora */ }
    apply();
  }));

  controls.hidden = false;
  apply();
})();

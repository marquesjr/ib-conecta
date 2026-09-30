(() => {
  // Caixas de texto do cadastro de louvor crescem com o conteúdo.
  // Navegadores com `field-sizing: content` já fazem isso só com CSS.
  if (window.CSS && CSS.supports('field-sizing', 'content')) return;
  const fit = (area) => {
    area.style.height = 'auto';
    area.style.height = `${area.scrollHeight + 2}px`;
  };
  document.querySelectorAll('.sectioned-form textarea').forEach((area) => {
    fit(area);
    area.addEventListener('input', () => fit(area));
  });
})();

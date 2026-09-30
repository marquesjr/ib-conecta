// Botões "Copiar" da página de contribuições: copia a chave PIX ou o código
// copia e cola e avisa "Copiada" numa região aria-live.
(() => {
  const selectText = (element) => {
    const range = document.createRange();
    range.selectNodeContents(element);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
  };

  document.querySelectorAll('[data-copy-target]').forEach((button) => {
    const source = document.getElementById(button.dataset.copyTarget);
    const status = document.getElementById(button.dataset.copyStatus);
    if (!source) return;
    button.hidden = false;
    let timer;
    button.addEventListener('click', async () => {
      let message = button.dataset.copyDone || 'Copiado!';
      try {
        await navigator.clipboard.writeText(source.textContent.trim());
      } catch (error) {
        selectText(source);
        message = 'Texto selecionado. Use Copiar do seu aparelho.';
      }
      if (!status) return;
      status.textContent = message;
      clearTimeout(timer);
      timer = setTimeout(() => { status.textContent = ''; }, 4000);
    });
  });
})();

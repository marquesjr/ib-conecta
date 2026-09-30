(() => {
  // Formulários com data-auto-submit salvam ao trocar a seleção; o botão fica só para quem está sem JS.
  document.querySelectorAll('form[data-auto-submit]').forEach((form) => {
    const button = form.querySelector('button[type="submit"]');
    if (button) button.hidden = true;
    form.querySelectorAll('select').forEach((select) => {
      select.addEventListener('change', () => form.requestSubmit());
    });
  });
})();

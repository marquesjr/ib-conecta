(() => {
  // Botão "Mostrar/Ocultar" do campo de senha na tela de login.
  document.querySelectorAll('.password-toggle').forEach((toggle) => {
    const input = document.getElementById(toggle.getAttribute('aria-controls'));
    if (!input) return;
    toggle.hidden = false;
    toggle.addEventListener('click', () => {
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      toggle.textContent = show ? 'Ocultar senha' : 'Mostrar senha';
      input.focus();
    });
  });
})();

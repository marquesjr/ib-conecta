(() => {
  // Após um envio com erros, leva o foco ao primeiro campo inválido (WCAG 3.3.1).
  const invalid = document.querySelector('form [aria-invalid="true"], form .form-errors');
  if (invalid) {
    if (!invalid.matches('input, select, textarea')) invalid.setAttribute('tabindex', '-1');
    invalid.focus();
  }
})();

(() => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('#primary-nav');
  if (!toggle || !nav) return;
  toggle.hidden = false;
  const close = () => {
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
  };
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    const group = document.querySelector('.nav-group[open]');
    if (group) { group.open = false; group.querySelector('summary').focus(); }
    else if (toggle.getAttribute('aria-expanded') === 'true') { close(); toggle.focus(); }
  });
  document.addEventListener('click', (event) => {
    const group = document.querySelector('.nav-group[open]');
    if (group && !group.contains(event.target)) group.open = false;
    if (!event.target.closest('.site-header')) close();
  });
  nav.querySelectorAll('a').forEach((link) => {
    if (link.origin === location.origin && link.pathname === location.pathname) link.setAttribute('aria-current', 'page');
  });
})();

// Inscrição do retiro: esconde os blocos de familiar vazios e mostra um por vez
// com o botão "Adicionar familiar". Sem JavaScript, os blocos continuam visíveis.
(() => {
  const group = document.querySelector('[data-family-members]');
  if (!group) return;
  const button = group.querySelector('[data-add-family]');
  const template = group.querySelector('[data-family-template]');
  const total = group.querySelector('input[name$="-TOTAL_FORMS"]');
  const max = group.querySelector('input[name$="-MAX_NUM_FORMS"]');
  if (!button || !template || !total) return;

  const prefix = total.name.replace(/-TOTAL_FORMS$/, '');
  const limit = max ? Number(max.value) : Infinity;

  group.querySelectorAll('.family-member[data-empty]').forEach((member) => { member.hidden = true; });

  const refresh = () => {
    const canAdd = group.querySelector('.family-member[hidden]') || Number(total.value) < limit;
    button.hidden = !canAdd;
  };

  button.addEventListener('click', () => {
    let member = group.querySelector('.family-member[hidden]');
    if (member) {
      member.hidden = false;
    } else {
      const index = Number(total.value);
      if (index >= limit) return;
      const html = template.innerHTML
        .replace(new RegExp(`${prefix}-__prefix__`, 'g'), `${prefix}-${index}`)
        .replace(/__number__/g, String(index + 1));
      button.insertAdjacentHTML('beforebegin', html);
      total.value = String(index + 1);
      member = button.previousElementSibling;
    }
    const first = member.querySelector('input, textarea, select');
    if (first) first.focus();
    refresh();
  });

  refresh();
})();

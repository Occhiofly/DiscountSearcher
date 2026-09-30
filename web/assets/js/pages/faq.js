/**
 * Pagina delle domande frequenti: filtro per testo e per gruppo, apertura
 * automatica della domanda indicata nell'ancora dell'URL (faq.html#faq-...).
 */

import { boot } from '../app.js';
import { FAQ_GROUPS } from '../services/content.js';
import { accordionMarkup, initAccordions, openAccordionItem } from '../components/accordion.js';
import { stateBlock } from '../components/ticket-ui.js';
import { debounce, escapeHtml, normalize } from '../services/utils.js';
import { t, url } from '../services/i18n.js';

const host = document.querySelector('[data-faq]');
const chipsHost = document.querySelector('[data-faq-groups]');
const input = document.getElementById('faq-search');
const status = document.getElementById('faq-status');

let activeGroup = 'all';

function matches(item, words) {
  if (!words.length) return true;
  const hay = normalize(`${item.q} ${item.tags.join(' ')} ${item.a.replace(/<[^>]+>/g, ' ')}`);
  return words.every((w) => hay.includes(w));
}

function render() {
  const words = normalize(input?.value || '').split(/\s+/).filter((w) => w.length > 1);

  const groups = FAQ_GROUPS
    .filter((g) => activeGroup === 'all' || g.id === activeGroup)
    .map((g) => ({ ...g, items: g.items.filter((i) => matches(i, words)) }))
    .filter((g) => g.items.length);

  const total = groups.reduce((n, g) => n + g.items.length, 0);

  if (!total) {
    host.innerHTML = stateBlock({
      iconName: 'search',
      title: t('faq.noMatchTitle'),
      text: t('faq.noMatchText'),
      actions: `
        <button class="ds-btn ds-btn--secondary" type="button" data-faq-reset>${t('faq.showAll')}</button>
        <a class="ds-btn ds-btn--primary" href="${url('ticketNew')}">${t('faq.openTicket')}</a>`,
    });
    status.textContent = t('faq.none');
    return;
  }

  host.innerHTML = groups.map((g) => `
    <section class="ds-stack ds-stack--4" aria-labelledby="grp-${g.id}" style="margin-bottom:var(--ds-7)">
      <h2 id="grp-${g.id}" style="font-size:var(--ds-fs-h3)">${escapeHtml(g.title)}</h2>
      ${accordionMarkup(g.items)}
    </section>`).join('');

  initAccordions(host);

  //Con una ricerca attiva apriamo subito la prima risposta: chi cerca
  //vuole leggere, non fare un clic in più.
  if (words.length) openFirst();

  status.textContent = t(total === 1 ? 'faq.countOne' : 'faq.countMany', { n: total });
}

function openFirst() {
  const first = host.querySelector('.ds-accordion__trigger');
  if (!first) return;
  first.setAttribute('aria-expanded', 'true');
  document.getElementById(first.getAttribute('aria-controls'))?.classList.add('is-open');
}

function renderChips() {
  const all = [{ id: 'all', title: t('faq.all') }, ...FAQ_GROUPS];
  chipsHost.innerHTML = all.map((g) => `
    <button class="ds-chip" type="button" data-group="${g.id}" aria-pressed="${g.id === activeGroup}">
      ${escapeHtml(g.title)}
    </button>`).join('');
}

chipsHost?.addEventListener('click', (e) => {
  const chip = e.target.closest('[data-group]');
  if (!chip) return;
  activeGroup = chip.dataset.group;
  renderChips();
  render();
});

host?.addEventListener('click', (e) => {
  if (!e.target.closest('[data-faq-reset]')) return;
  input.value = '';
  activeGroup = 'all';
  renderChips();
  render();
  input.focus();
});

input?.addEventListener('input', debounce(render, 160));
input?.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { input.value = ''; render(); }
});

/** Apre la domanda indicata nell'ancora, se esiste. */
function openFromHash() {
  const hash = decodeURIComponent(window.location.hash.slice(1));
  if (hash) openAccordionItem(hash);
}

if (host) {
  renderChips();
  render();
  boot();
  openFromHash();
  window.addEventListener('hashchange', openFromHash);
}

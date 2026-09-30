/**
 * Pagina iniziale.
 * Il testo della pagina è nell'HTML; qui si montano solo le parti generate da
 * dati (finestre dell'app, negozi, team) e l'interazione della vetrina.
 */

import { boot } from '../app.js';
import { appPreviewMarkup, setPreviewState } from '../components/app-preview.js';
import { STORES } from '../services/content.js';
import { mountTeam } from '../components/team.js';
import { escapeHtml } from '../services/utils.js';
import { t } from '../services/i18n.js';

function mountPreviews() {
  document.querySelectorAll('[data-app-preview]').forEach((host) => {
    host.innerHTML = appPreviewMarkup(host.dataset.appPreview);
  });
}

/**
 * Vetrina a passi: i pulsanti a sinistra si comportano come schede (tab)
 * e cambiano lo stato della finestra a destra.
 * Frecce sinistra/destra/su/giù spostano il focus fra i passi, come previsto
 * dal pattern "tabs" delle linee guida WAI-ARIA.
 */
function initShowcase() {
  const list = document.querySelector('[data-showcase-steps]');
  const frame = document.querySelector('[data-showcase-frame]');
  const panel = document.getElementById('showcase-panel');
  const caption = document.querySelector('[data-step-caption]');
  if (!list || !frame) return;

  const tabs = [...list.querySelectorAll('[role="tab"]')];

  const select = (tab, focus = false) => {
    tabs.forEach((t) => {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
    });
    if (panel) panel.setAttribute('aria-labelledby', tab.id);
    //Su schermi stretti il testo del passo è nascosto dentro la scheda e
    //compare qui sotto. aria-hidden: gli screen reader lo leggono già dal tab.
    if (caption) caption.textContent = tab.querySelector('.ds-step__text')?.textContent || '';
    setPreviewState(frame, tab.dataset.state);
    if (focus) tab.focus();
  };

  tabs.forEach((tab) => tab.addEventListener('click', () => select(tab)));

  list.addEventListener('keydown', (e) => {
    const i = tabs.indexOf(document.activeElement);
    if (i < 0) return;
    const keys = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
    if (e.key in keys) {
      e.preventDefault();
      select(tabs[(i + keys[e.key] + tabs.length) % tabs.length], true);
    } else if (e.key === 'Home') {
      e.preventDefault(); select(tabs[0], true);
    } else if (e.key === 'End') {
      e.preventDefault(); select(tabs[tabs.length - 1], true);
    }
  });
}

function mountStores() {
  const host = document.querySelector('[data-stores]');
  if (!host) return;
  host.innerHTML = STORES.map((s) => `
    <li class="ds-store" data-reveal data-reveal-step="60">
      <span class="ds-store__logo">
        <img src="${escapeHtml(s.logo)}" alt="" width="24" height="24" loading="lazy" decoding="async">
      </span>
      <span class="ds-stack">
        <span class="ds-store__name">${escapeHtml(s.name)}</span>
        <span class="ds-store__meta">${t('home.storeMeta')}</span>
      </span>
    </li>`).join('');
}

//Prima si genera il contenuto, poi boot(): così le animazioni di comparsa
//trovano anche le card appena create.
mountPreviews();
mountStores();
mountTeam();
initShowcase();
boot();

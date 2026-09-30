/**
 * Barra di navigazione locale, montata in [data-ds-subnav]. Tiene insieme le
 * pagine di un'area del sito e, a destra, mostra lo stato dell'account:
 * "Accedi", oppure nome utente ed "Esci".
 *
 * Quale barra mostrare lo decide l'HTML: [data-ds-subnav] da solo (o vuoto) è
 * il Centro assistenza, [data-ds-subnav="lavoro"] è "Lavora con noi".
 */

import { SUPPORT_NAV, WORK_NAV } from '../services/content.js';
import { t } from '../services/i18n.js';
import { currentPage, escapeHtml } from '../services/utils.js';
import { getSession, loginUrl, logout, SESSION_EVENT } from '../services/session.js';
import { LANG, PAGES } from '../services/i18n.js';
import { icon } from './icons.js';

/** Le barre disponibili: voci da mostrare e nome della navigazione. */
const NAV_SETS = {
  assistenza: { label: t('subnav.support'), items: SUPPORT_NAV },
  lavoro:     { label: t('subnav.jobs'),    items: WORK_NAV },
};

function accountMarkup(page) {
  //Sulla pagina di accesso il pulsante "Accedi" sarebbe un link a sé stessa
  if (page === PAGES.login[LANG]) return '';

  const session = getSession();
  if (!session) {
    return `
      <a class="ds-btn ds-btn--secondary ds-btn--sm" href="${loginUrl()}">
        ${icon('key', { size: 15, className: 'ds-btn__icon' })}<span>${t('subnav.signIn')}</span>
      </a>`;
  }
  return `
    <span class="ds-subnav__user" title="${escapeHtml(t('subnav.signedInAs', { username: session.username }))}">
      ${icon('user', { size: 16 })}<span>${escapeHtml(session.username)}</span>
    </span>
    <button class="ds-btn ds-btn--ghost ds-btn--sm" type="button" data-logout>${t('subnav.signOut')}</button>`;
}

export function mountSubnav() {
  const host = document.querySelector('[data-ds-subnav]');
  if (!host) return;

  const page = currentPage();
  const nav = NAV_SETS[host.dataset.dsSubnav] || NAV_SETS.assistenza;

  host.className = 'ds-subnav';
  host.innerHTML = `
    <div class="ds-container ds-container--wide ds-subnav__bar">
      <nav aria-label="${nav.label}">
        <div class="ds-subnav__inner">
          ${nav.items.map((item) => {
            const active = item.match.includes(page) ? ' aria-current="page"' : '';
            return `<a class="ds-subnav__link" href="${item.href}"${active}>${item.label}</a>`;
          }).join('')}
        </div>
      </nav>
      <div class="ds-subnav__account" data-account></div>
    </div>`;

  const account = host.querySelector('[data-account]');
  const renderAccount = () => { account.innerHTML = accountMarkup(page); };
  renderAccount();

  //La sessione può cambiare a pagina aperta: scadenza rilevata da una chiamata,
  //oppure accesso/uscita in un'altra scheda (evento "storage" del browser).
  window.addEventListener(SESSION_EVENT, renderAccount);
  window.addEventListener('storage', (e) => { if (e.key === 'ds_session') renderAccount(); });

  //Delegato sul contenitore: il pulsante viene ricreato a ogni aggiornamento
  account.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-logout]');
    if (!btn) return;
    btn.classList.add('is-loading');
    await logout();
    //Ricarica: ogni pagina ridisegna i propri contenuti per un utente non collegato
    window.location.reload();
  });

  //Su schermi stretti la barra scorre in orizzontale: portiamo in vista la
  //voce attiva. scrollLeft invece di scrollIntoView, che sposterebbe anche
  //la pagina in verticale.
  const inner = host.querySelector('.ds-subnav__inner');
  const active = host.querySelector('[aria-current="page"]');
  if (inner && active && inner.scrollWidth > inner.clientWidth) {
    inner.scrollLeft = active.offsetLeft - inner.offsetLeft - 16;
  }
}

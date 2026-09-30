/**
 * Pezzi di interfaccia condivisi dalle pagine dei ticket e dell'assistenza:
 * badge di stato, stati vuoto/errore/caricamento, invito ad accedere.
 */

import { TICKET_STATUS } from '../services/tickets.js';
import { loginUrl } from '../services/session.js';
import { findCategory, JOB_CATEGORY, JOB_CATEGORY_LABEL } from '../services/content.js';
import { t, url } from '../services/i18n.js';
import { icon } from './icons.js';
import { escapeHtml } from '../services/utils.js';

/**
 * Badge colorato per uno stato del ticket (colore + testo, mai solo colore).
 * `label` sostituisce il testo predefinito (l'area staff dice "In attesa dell'utente").
 */
export function statusBadge(status, label) {
  const s = TICKET_STATUS[status] || { label: status, badge: '' };
  return `<span class="ds-badge ${s.badge}"><span class="ds-badge__dot" aria-hidden="true"></span>${escapeHtml(label || s.label)}</span>`;
}

/**
 * Nome leggibile di una categoria a partire dal suo identificativo.
 * Le candidature non sono una categoria dell'assistenza (non hanno articoli),
 * quindi hanno la loro etichetta: senza, comparirebbero come "Altro".
 */
export function categoryLabel(id) {
  if (id === JOB_CATEGORY) return JOB_CATEGORY_LABEL;
  return findCategory(id)?.title || t('state.otherCategory');
}

/** Stato generico: vuoto, errore o successo. */
export function stateBlock({ kind = 'empty', iconName = 'inbox', title, text, actions = '' }) {
  const role = kind === 'error' ? ' role="alert"' : '';
  return `
    <div class="ds-state ds-state--${kind}"${role}>
      <span class="ds-icon-box ds-icon-box--lg">${icon(iconName)}</span>
      <h2 class="ds-state__title">${title}</h2>
      ${text ? `<p class="ds-state__text">${text}</p>` : ''}
      ${actions ? `<div class="ds-row" style="justify-content:center">${actions}</div>` : ''}
    </div>`;
}

/**
 * Invito ad accedere, al posto del contenuto che richiede il login.
 * @param {string} [message] spiegazione (es. "La sessione è scaduta...")
 * @param {string} [next] pagina a cui tornare dopo l'accesso
 */
export function loginRequiredBlock(message, next) {
  return stateBlock({
    iconName: 'lock',
    title: t('state.loginRequiredTitle'),
    text: escapeHtml(message || t('state.loginRequiredText')),
    actions: `
      <a class="ds-btn ds-btn--primary" href="${loginUrl(next)}">
        ${icon('key', { size: 17, className: 'ds-btn__icon' })}<span>${t('state.signIn')}</span>
      </a>
      <a class="ds-btn ds-btn--ghost" href="${url('register')}">${t('state.noAccount')}</a>`,
  });
}

/** Blocco di errore per un TicketsError (o qualsiasi errore), con "Riprova" facoltativo. */
export function ticketErrorBlock(err, { title = t('state.errorTitle'), retry = true } = {}) {
  if (err?.kind === 'auth') return loginRequiredBlock(err.message);
  return stateBlock({
    kind: 'error',
    iconName: err?.kind === 'network' ? 'refresh' : 'alert',
    title,
    text: escapeHtml(err?.message || t('state.unexpected')),
    actions: retry
      ? `<button class="ds-btn ds-btn--secondary" type="button" data-retry>${icon('refresh', { size: 17, className: 'ds-btn__icon' })}<span>${t('state.retry')}</span></button>`
      : '',
  });
}

/** Righe scheletro durante il caricamento di un elenco. */
export function skeletonRows(n = 3) {
  return `
    <div class="ds-stack ds-stack--3" aria-hidden="true">
      ${Array.from({ length: n }, () => '<div class="ds-skeleton ds-skeleton--row"></div>').join('')}
    </div>`;
}

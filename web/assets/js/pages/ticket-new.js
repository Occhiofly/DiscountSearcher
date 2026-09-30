/**
 * Apertura di un nuovo ticket di assistenza.
 *
 * Validazione e invio sono in components/ticket-form.js e gli allegati in
 * components/file-picker.js, condivisi con il modulo delle candidature: qui
 * restano solo le cose di questa pagina, cioè le categorie dell'assistenza e
 * gli articoli suggeriti.
 */

import { boot } from '../app.js';
import { CATEGORIES, findCategory } from '../services/content.js';
import { createTicket, isLoggedIn } from '../services/tickets.js';
import { getSession } from '../services/session.js';
import { loginRequiredBlock } from '../components/ticket-ui.js';
import { initCounters, setupCancelConfirm, setupTicketForm } from '../components/ticket-form.js';
import { createFilePicker } from '../components/file-picker.js';
import { icon } from '../components/icons.js';
import { escapeHtml, queryParam } from '../services/utils.js';
import { t, url } from '../services/i18n.js';

const form = document.getElementById('ticket-form');
const view = document.querySelector('[data-ticket-view]');

/** Selettore degli allegati, creato in init() solo se l'utente ha fatto l'accesso. */
let picker = null;

/** Regole per campo. Ogni regola restituisce un messaggio d'errore o null. */
const RULES = {
  subject: (v) => {
    if (!v.trim()) return t('new.subjectRequired');
    if (v.trim().length < 8) return t('new.subjectShort');
    if (v.length > 120) return t('new.subjectLong');
    return null;
  },
  category: (v) => (v ? null : t('new.categoryRequired')),
  description: (v) => {
    if (!v.trim()) return t('new.descriptionRequired');
    if (v.trim().length < 30) return t('new.descriptionShort');
    if (v.length > 3000) return t('new.descriptionLong');
    return null;
  },
  extra: (v) => (v.length > 1000 ? t('new.extraLong') : null),
  //Il valore dell'input dei file non conta: l'elenco vero lo tiene il selettore
  files: () => picker?.validate() ?? null,
};

const LABELS = {
  subject: t('new.labelSubject'), category: t('new.labelCategory'),
  description: t('new.labelDescription'), extra: t('new.labelExtra'), files: t('new.labelFiles'),
};

function populateCategories(select) {
  select.innerHTML = `<option value="">${t('new.chooseCategory')}</option>` +
    CATEGORIES.map((c) => `<option value="${c.id}">${escapeHtml(c.title)}</option>`).join('');

  //Arrivando da una categoria (?c=bug) il modulo è già impostato su quella
  const preset = queryParam('c');
  if (preset && findCategory(preset)) select.value = preset;
}

/**
 * Suggerimenti in base alla categoria scelta: prima di scrivere un ticket,
 * vale la pena vedere se la risposta è già in un articolo.
 */
function renderSuggestions(categoryId) {
  const host = document.querySelector('[data-suggestions]');
  if (!host) return;
  const category = findCategory(categoryId);

  if (!category) {
    host.innerHTML = `<p class="ds-hint">${t('new.suggestionsHint')}</p>`;
    return;
  }
  host.innerHTML = `
    <ul class="ds-stack ds-stack--2">
      ${category.articles.map((a) => `
        <li>
          <a class="ds-toc__link" style="display:block" href="${url('category', `?c=${category.id}#${a.id}`)}" target="_blank" rel="noopener">
            ${escapeHtml(a.title)}<span class="ds-sr-only">${t('new.newTab')}</span>
          </a>
        </li>`).join('')}
    </ul>`;
}

function renderSuccess(ticket, fileCount) {
  const files = fileCount
    ? `<div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('new.labelFiles')}</dt><dd class="ds-ticket-meta__val" style="margin:0">${t(fileCount === 1 ? 'new.attachmentsSent' : 'new.attachmentsSentMany', { n: fileCount })}</dd></div>`
    : '';
  view.innerHTML = `
    <div class="ds-panel ds-stack ds-stack--5" style="align-items:center;text-align:center" tabindex="-1" data-success>
      <span class="ds-icon-box ds-icon-box--lg" style="color:var(--ds-ok);background:var(--ds-ok-soft)">${icon('checkCircle')}</span>
      <div class="ds-stack ds-stack--2" style="align-items:center">
        <span class="ds-badge ds-badge--accent">${escapeHtml(ticket.id)}</span>
        <h1 style="font-size:var(--ds-fs-h2)">${t('new.successTitle')}</h1>
      </div>
      <p class="ds-lead" style="text-align:center">${t('new.successText')}</p>
      <dl class="ds-ticket-meta" style="width:min(420px,100%);text-align:left">
        <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('new.labelSubject')}</dt><dd class="ds-ticket-meta__val" style="margin:0">${escapeHtml(ticket.subject)}</dd></div>
        <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('new.labelCategory')}</dt><dd class="ds-ticket-meta__val" style="margin:0">${escapeHtml(findCategory(ticket.category)?.title || '—')}</dd></div>
        ${files}
      </dl>
      <div class="ds-row" style="justify-content:center">
        <a class="ds-btn ds-btn--primary" href="${url('ticketDetail', `?id=${encodeURIComponent(ticket.id)}`)}">${t('new.openTicket')}</a>
        <a class="ds-btn ds-btn--ghost" href="${url('ticketList')}">${t('detail.backToList')}</a>
      </div>
    </div>`;
  view.querySelector('[data-success]').focus();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function init() {
  if (!form) return;

  //Senza accesso il modulo non potrebbe essere inviato: mostriamo subito
  //l'invito ad accedere invece di farlo scoprire dopo aver scritto tutto.
  if (!isLoggedIn()) {
    form.outerHTML = `<div>${loginRequiredBlock(t('new.loginRequired'))}</div>`;
    const suggestions = document.querySelector('[data-suggestions]');
    if (suggestions) {
      suggestions.innerHTML = `<p class="ds-hint">${t('new.meanwhile', { support: url('support'), faq: url('faq') })}</p>`;
    }
    return;
  }

  const session = getSession();
  document.querySelector('[data-account-notice]').innerHTML = `
    <div class="ds-notice">
      <span class="ds-notice__icon">${icon('user', { size: 17 })}</span>
      <p>${t('form.accountNotice', { username: escapeHtml(session.username) })}</p>
    </div>`;

  const { field, wrapper, validateField } = setupTicketForm({
    form,
    rules: RULES,
    labels: LABELS,
    onSubmit: async (values) => {
      const sending = form.querySelector('[data-sending]');
      sending.hidden = !picker.files.length;
      try {
        const ticket = await createTicket({
          subject: values.subject,
          category: values.category,
          description: values.description,
          extra: values.extra || null,
          attachments: await picker.toPayload(),
        });
        renderSuccess(ticket, picker.files.length);
      } finally {
        sending.hidden = true;
      }
    },
  });

  //Ogni aggiunta o rimozione di file si controlla subito, senza aspettare l'invio
  picker = createFilePicker(wrapper('files'), () => {
    wrapper('files').dataset.touched = 'true';
    validateField('files');
  });

  populateCategories(field('category'));
  initCounters(form);
  renderSuggestions(field('category').value);

  field('category').addEventListener('change', () => {
    renderSuggestions(field('category').value);
    if (wrapper('category').dataset.touched) validateField('category');
  });

  setupCancelConfirm(form, ['subject', 'description', 'extra'], 'subject', () => picker.files.length > 0);
}

init();
boot();

/**
 * Candidatura per entrare nel team.
 *
 * Non c'è un sistema separato: la candidatura apre un ticket, con la stessa
 * meccanica dell'assistenza (stesso account, stessa conversazione, stesse
 * email). Cambia solo come viene compilato:
 *
 *   oggetto     "Candidatura — <ruolo>", composto qui
 *   categoria   sempre JOB_CATEGORY, così il team la riconosce subito
 *   descrizione la presentazione scritta dalla persona
 *   extra       ruolo, disponibilità e link, uno per riga
 *   allegati    file facoltativi: il server li manda al team via email e non li
 *               salva (nel ticket resta l'elenco dei nomi)
 *
 * Validazione e invio arrivano da components/ticket-form.js, gli stessi del
 * modulo dell'assistenza.
 */

import { boot } from '../app.js';
import { JOB_CATEGORY, ROLES, findRole } from '../services/content.js';
import { createTicket, isLoggedIn } from '../services/tickets.js';
import { getSession } from '../services/session.js';
import { loginRequiredBlock } from '../components/ticket-ui.js';
import { initCounters, setupCancelConfirm, setupTicketForm } from '../components/ticket-form.js';
import { createFilePicker } from '../components/file-picker.js';
import { icon } from '../components/icons.js';
import { escapeHtml, queryParam } from '../services/utils.js';
import { t, url } from '../services/i18n.js';

const form = document.getElementById('apply-form');
const view = document.querySelector('[data-ticket-view]');

/** Selettore degli allegati, creato in init() solo se l'utente ha fatto l'accesso. */
let picker = null;

/** Regole per campo. Ogni regola restituisce un messaggio d'errore o null. */
const RULES = {
  role: (v) => (findRole(v) ? null : t('apply.roleRequired')),
  presentation: (v) => {
    if (!v.trim()) return t('apply.presentationRequired');
    if (v.trim().length < 30) return t('apply.presentationShort');
    if (v.length > 3000) return t('apply.presentationLong');
    return null;
  },
  //I limiti di questi due campi sommati stanno dentro i 1000 caratteri che il
  //server accetta per le informazioni aggiuntive del ticket.
  links: (v) => (v.length > 600 ? t('apply.linksLong') : null),
  availability: (v) => (v.length > 200 ? t('apply.availabilityLong') : null),
  //Il valore dell'input dei file non conta: l'elenco vero lo tiene il selettore
  files: () => picker?.validate() ?? null,
};

const LABELS = {
  role: t('apply.labelRole'), presentation: t('apply.labelPresentation'),
  links: t('apply.labelLinks'), availability: t('apply.labelAvailability'),
  files: t('new.labelFiles'),
};

function populateRoles(select) {
  select.innerHTML = `<option value="">${t('apply.chooseRole')}</option>` +
    ROLES.map((r) => `<option value="${r.id}">${escapeHtml(r.title)}</option>`).join('');

  //Arrivando dalla scheda di un ruolo (?r=grafica) il modulo è già impostato
  const preset = queryParam('r');
  if (preset && findRole(preset)) select.value = preset;
}

/** Scheda del ruolo scelto, accanto al modulo: cosa farai e com'è la prova. */
function renderRoleCard(roleId) {
  const host = document.querySelector('[data-role-card]');
  if (!host) return;
  const role = findRole(roleId);

  if (!role) {
    host.innerHTML = `<p class="ds-hint">${t('apply.roleHint')}</p>`;
    return;
  }
  host.innerHTML = `
    <div class="ds-stack ds-stack--3">
      <p class="ds-card__text">${escapeHtml(role.summary)}</p>
      <ul class="ds-stack ds-stack--2">
        ${role.does.map((d) => `<li class="ds-feature__li">${icon('check', { size: 14 })}${escapeHtml(d)}</li>`).join('')}
      </ul>
      <p class="ds-hint"><strong>${t('apply.trial')}</strong> ${escapeHtml(role.trial)}</p>
    </div>`;
}

/** Ruolo, disponibilità e link finiscono nelle informazioni aggiuntive del ticket. */
function buildExtra(values) {
  const role = findRole(values.role);
  const lines = [t('apply.extraRole', { role: role.title })];
  if (values.availability) lines.push(t('apply.extraAvailability', { value: values.availability }));
  if (values.links) lines.push(t('apply.extraLinks', { value: values.links }));
  return lines.join('\n');
}

function renderSuccess(ticket, roleTitle, fileCount) {
  const files = fileCount
    ? `<div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('apply.attachments')}</dt><dd class="ds-ticket-meta__val" style="margin:0">${t(fileCount === 1 ? 'new.attachmentsSent' : 'new.attachmentsSentMany', { n: fileCount })}</dd></div>`
    : '';
  view.innerHTML = `
    <div class="ds-panel ds-stack ds-stack--5" style="align-items:center;text-align:center" tabindex="-1" data-success>
      <span class="ds-icon-box ds-icon-box--lg" style="color:var(--ds-ok);background:var(--ds-ok-soft)">${icon('checkCircle')}</span>
      <div class="ds-stack ds-stack--2" style="align-items:center">
        <span class="ds-badge ds-badge--accent">${escapeHtml(ticket.id)}</span>
        <h1 style="font-size:var(--ds-fs-h2)">${t('apply.successTitle')}</h1>
      </div>
      <p class="ds-lead" style="text-align:center">${t('apply.successText')}</p>
      <dl class="ds-ticket-meta" style="width:min(420px,100%);text-align:left">
        <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('apply.role')}</dt><dd class="ds-ticket-meta__val" style="margin:0">${escapeHtml(roleTitle)}</dd></div>
        <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('apply.number')}</dt><dd class="ds-ticket-meta__val" style="margin:0">${escapeHtml(ticket.id)}</dd></div>
        ${files}
      </dl>
      <div class="ds-row" style="justify-content:center">
        <a class="ds-btn ds-btn--primary" href="${url('ticketDetail', `?id=${encodeURIComponent(ticket.id)}`)}">${t('apply.openApplication')}</a>
        <a class="ds-btn ds-btn--ghost" href="${url('ticketList')}">${t('detail.backToList')}</a>
      </div>
    </div>`;
  view.querySelector('[data-success]').focus();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function init() {
  if (!form) return;

  //Senza accesso il modulo non potrebbe essere inviato: lo diciamo subito,
  //non dopo che la presentazione è già stata scritta.
  if (!isLoggedIn()) {
    form.outerHTML = `<div>${loginRequiredBlock(t('apply.loginRequired'))}</div>`;
    const card = document.querySelector('[data-role-card]');
    if (card) card.innerHTML = `<p class="ds-hint">${t('apply.meanwhile', { jobs: url('jobs') })}</p>`;
    return;
  }

  const session = getSession();
  document.querySelector('[data-account-notice]').innerHTML = `
    <div class="ds-notice">
      <span class="ds-notice__icon">${icon('user', { size: 17 })}</span>
      <p>${t('form.accountNoticeApply', { username: escapeHtml(session.username) })}</p>
    </div>`;

  const { field, wrapper, validateField } = setupTicketForm({
    form,
    rules: RULES,
    labels: LABELS,
    onSubmit: async (values) => {
      const role = findRole(values.role);
      const sending = form.querySelector('[data-sending]');
      sending.hidden = !picker.files.length;
      try {
        const ticket = await createTicket({
          subject: t('apply.subject', { role: role.title }),
          category: JOB_CATEGORY,
          description: values.presentation,
          extra: buildExtra(values),
          attachments: await picker.toPayload(),
        });
        renderSuccess(ticket, role.title, picker.files.length);
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

  populateRoles(field('role'));
  initCounters(form);
  renderRoleCard(field('role').value);

  field('role').addEventListener('change', () => {
    renderRoleCard(field('role').value);
    if (wrapper('role').dataset.touched) validateField('role');
  });

  setupCancelConfirm(form, ['presentation', 'links', 'availability'], 'presentation',
    () => picker.files.length > 0);
}

init();
boot();

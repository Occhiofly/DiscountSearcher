/**
 * Dettaglio di un ticket: ticket-dettaglio.html?id=<ID>
 * Conversazione, riquadro di risposta e scheda riassuntiva dello stato.
 */

import { boot } from '../app.js';
import { getTicket, isLoggedIn, replyToTicket, TICKET_STATUS } from '../services/tickets.js';
import {
  categoryLabel, loginRequiredBlock, stateBlock, statusBadge, ticketErrorBlock,
} from '../components/ticket-ui.js';
import { icon } from '../components/icons.js';
import { escapeHtml, formatDateTime, queryParam, timeAgo } from '../services/utils.js';
import { t, url } from '../services/i18n.js';

const MAX_REPLY = 3000;

const host = document.querySelector('[data-ticket]');
const crumb = document.querySelector('[data-crumb-current]');
const id = queryParam('id');

function message(m) {
  const staff = m.role === 'staff';
  return `
    <li class="ds-msg${staff ? ' ds-msg--staff' : ''}">
      <span class="ds-msg__avatar" aria-hidden="true">${escapeHtml(m.author.charAt(0))}</span>
      <article class="ds-msg__bubble" aria-label="${t('detail.messageFrom', { author: escapeHtml(m.author) })}">
        <header class="ds-msg__head">
          <span class="ds-msg__author">${escapeHtml(m.author)}</span>
          ${staff ? `<span class="ds-msg__role">${t('detail.teamRole')}</span>` : ''}
          <time class="ds-msg__when" datetime="${escapeHtml(m.at)}" title="${formatDateTime(m.at)}">${timeAgo(m.at)}</time>
        </header>
        <p class="ds-msg__body">${escapeHtml(m.body)}</p>
      </article>
    </li>`;
}

function replyBox(ticket) {
  const s = TICKET_STATUS[ticket.status];
  if (!s?.canReply) {
    return `
      <div class="ds-notice">
        <span class="ds-notice__icon">${icon('lock', { size: 17 })}</span>
        <p><strong>${t('detail.closedTitle')}</strong> ${t('detail.closedText')}
          <a href="${url('ticketNew', `?c=${encodeURIComponent(ticket.category)}`)}">${t('detail.openAnother')}</a>${t('detail.ifAnother')}</p>
      </div>`;
  }
  return `
    <form class="ds-panel ds-reply" id="reply-form" novalidate>
      <div class="ds-field" id="reply-field">
        <div class="ds-field-row">
          <label class="ds-label" for="reply">${t('detail.replyLabel')}</label>
          <span class="ds-counter" id="reply-counter" aria-hidden="true">0 / ${MAX_REPLY}</span>
        </div>
        <textarea class="ds-textarea" id="reply" name="reply" rows="4" required
                  placeholder="${t('detail.replyPlaceholder')}"
                  aria-describedby="reply-err"></textarea>
        <p class="ds-error" id="reply-err">${icon('alert', { size: 14 })}<span></span></p>
      </div>
      <div class="ds-notice ds-notice--warn" id="reply-fail" role="alert" hidden>
        <span class="ds-notice__icon">${icon('alert', { size: 17 })}</span>
        <p><strong>${t('detail.replyFailed')}</strong> <span data-msg></span></p>
      </div>
      <div class="ds-reply__actions">
        <button class="ds-btn ds-btn--primary" type="submit">
          ${icon('send', { size: 17, className: 'ds-btn__icon' })}<span>${t('detail.sendReply')}</span>
        </button>
        <span class="ds-hint">${t('detail.noPassword')}</span>
      </div>
    </form>`;
}

function render(ticket) {
  const s = TICKET_STATUS[ticket.status];
  document.title = t('detail.docTitle', { id: ticket.id, subject: ticket.subject });
  if (crumb) crumb.textContent = ticket.id;

  host.innerHTML = `
    <header class="ds-stack ds-stack--3" style="margin-bottom:var(--ds-6)">
      <div class="ds-row">
        <span class="ds-badge ds-badge--accent">${escapeHtml(ticket.id)}</span>
        ${statusBadge(ticket.status)}
      </div>
      <h1 style="font-size:var(--ds-fs-h2)">${escapeHtml(ticket.subject)}</h1>
    </header>

    <div class="ds-ticket-layout">
      <section class="ds-stack ds-stack--5" aria-labelledby="conv-title">
        <h2 class="ds-sr-only" id="conv-title">${t('detail.thread')}</h2>
        <ol class="ds-thread" data-thread aria-live="polite">
          ${ticket.messages.map(message).join('')}
        </ol>
        ${replyBox(ticket)}
      </section>

      <aside class="ds-ticket-layout__side ds-stack ds-stack--4" aria-label="${t('detail.detailsTitle')}">
        <div class="ds-panel">
          <h2 style="font-size:1rem;margin-bottom:var(--ds-3)">${t('detail.detailsTitle')}</h2>
          <dl class="ds-ticket-meta">
            <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('detail.id')}</dt><dd class="ds-ticket-meta__val ds-mono" style="margin:0">${escapeHtml(ticket.id)}</dd></div>
            <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('detail.status')}</dt><dd class="ds-ticket-meta__val" style="margin:0" data-status-cell>${statusBadge(ticket.status)}</dd></div>
            <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('detail.category')}</dt><dd class="ds-ticket-meta__val" style="margin:0">${escapeHtml(categoryLabel(ticket.category))}</dd></div>
            <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('detail.created')}</dt><dd class="ds-ticket-meta__val ds-mono" style="margin:0;font-size:var(--ds-fs-xs)">${formatDateTime(ticket.createdAt)}</dd></div>
            <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('detail.updated')}</dt><dd class="ds-ticket-meta__val ds-mono" style="margin:0;font-size:var(--ds-fs-xs)" data-updated-cell>${formatDateTime(ticket.updatedAt)}</dd></div>
          </dl>
        </div>
        <div class="ds-panel ds-stack ds-stack--2">
          <h2 style="font-size:1rem">${t('detail.statusMeaning')}</h2>
          <p class="ds-card__text" data-status-text>${escapeHtml(s?.text || '')}</p>
        </div>
        <div class="ds-notice">
          <span class="ds-notice__icon">${icon('mail', { size: 17 })}</span>
          <p>${t('detail.emailNote')}</p>
        </div>
        <a class="ds-btn ds-btn--ghost" href="${url('ticketList')}">
          ${icon('arrowLeft', { size: 17, className: 'ds-btn__icon' })}<span>${t('detail.backToList')}</span>
        </a>
      </aside>
    </div>`;

  initReply(ticket);
}

function initReply(ticket) {
  const form = document.getElementById('reply-form');
  if (!form) return;
  const textarea = form.elements.reply;
  const wrap = document.getElementById('reply-field');
  const counter = document.getElementById('reply-counter');
  const errText = wrap.querySelector('.ds-error > span:last-child');
  const btn = form.querySelector('[type="submit"]');
  const fail = document.getElementById('reply-fail');

  const validate = () => {
    const v = textarea.value.trim();
    const msg = !v ? t('detail.replyEmpty')
      : textarea.value.length > MAX_REPLY ? t('detail.replyTooLong', { max: MAX_REPLY }) : null;
    wrap.classList.toggle('is-invalid', Boolean(msg));
    textarea.setAttribute('aria-invalid', String(Boolean(msg)));
    errText.textContent = msg || '';
    return !msg;
  };

  textarea.addEventListener('input', () => {
    counter.textContent = `${textarea.value.length} / ${MAX_REPLY}`;
    counter.classList.toggle('is-over', textarea.value.length > MAX_REPLY);
    if (wrap.classList.contains('is-invalid')) validate();
  });

  //Ctrl+Invio invia, come nella maggior parte delle chat
  textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) form.requestSubmit();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    fail.hidden = true;
    if (!validate()) { textarea.focus(); return; }

    btn.classList.add('is-loading');
    btn.setAttribute('aria-busy', 'true');
    textarea.disabled = true;
    let sent = false;
    try {
      const msg = await replyToTicket(ticket.id, textarea.value.trim());
      document.querySelector('[data-thread]').insertAdjacentHTML('beforeend', message(msg));
      textarea.value = '';
      counter.textContent = `0 / ${MAX_REPLY}`;
      sent = true;
    } catch (err) {
      if (err.kind === 'auth') {
        //Sessione scaduta: il testo scritto andrebbe perso con un reindirizzamento
        //automatico, quindi lo lasciamo nel campo e mostriamo l'invito ad accedere.
        fail.hidden = false;
        const back = url('ticketDetail', `?id=${ticket.id}`);
        fail.querySelector('[data-msg]').innerHTML = `${escapeHtml(err.message)} `
          + t('detail.copyBeforeLogin', { url: `${url('login')}?next=${encodeURIComponent(back)}` });
      } else if (err.kind === 'closed') {
        //Chiuso nel frattempo dal team: ricarichiamo per mostrare lo stato vero
        load();
        return;
      } else {
        fail.hidden = false;
        fail.querySelector('[data-msg]').textContent = err.message || t('detail.retryLater');
      }
    } finally {
      btn.classList.remove('is-loading');
      btn.removeAttribute('aria-busy');
      textarea.disabled = false;
      textarea.focus();
    }

    if (!sent) return;
    //La risposta riapre il ticket lato server: aggiorniamo stato e data. Se questa
    //lettura fallisce non è un problema: il messaggio è già stato inviato.
    try {
      const updated = await getTicket(ticket.id);
      document.querySelector('[data-status-cell]').innerHTML = statusBadge(updated.status);
      document.querySelector('[data-updated-cell]').textContent = formatDateTime(updated.updatedAt);
      document.querySelector('[data-status-text]').textContent = TICKET_STATUS[updated.status]?.text || '';
    } catch { /* stato mostrato aggiornato al prossimo caricamento */ }
  });
}

/**
 * Titolo della pagina per gli stati senza ticket (accesso, non trovato, errore).
 * Visivamente il titolo è quello del riquadro; questo h1 nascosto serve agli
 * screen reader, che navigano la pagina a partire dal titolo principale.
 */
const pageHeading = (text) => `<h1 class="ds-sr-only">${escapeHtml(text)}</h1>`;

function renderNotFound() {
  if (crumb) crumb.textContent = t('detail.notFoundTitle');
  host.innerHTML = pageHeading(t('detail.notFoundTitle')) + stateBlock({
    kind: 'error',
    iconName: 'ticket',
    title: t('detail.notFoundTitle'),
    text: id
      ? t('detail.notFoundWithId', { id: escapeHtml(id) })
      : t('detail.notFoundNoId'),
    actions: `<a class="ds-btn ds-btn--primary" href="${url('ticketList')}">${t('detail.backToList')}</a>`,
  });
}

async function load() {
  if (!id) { renderNotFound(); return; }
  if (!isLoggedIn()) {
    if (crumb) crumb.textContent = id;
    host.innerHTML = pageHeading(t('detail.ticketWord', { id })) + loginRequiredBlock();
    return;
  }
  try {
    render(await getTicket(id));
  } catch (err) {
    if (err.kind === 'notfound') { renderNotFound(); return; }
    host.innerHTML = pageHeading(t('detail.ticketWord', { id })) + ticketErrorBlock(err, { title: t('detail.loadError') });
    host.querySelector('[data-retry]')?.addEventListener('click', load);
  }
}

boot();
load();
